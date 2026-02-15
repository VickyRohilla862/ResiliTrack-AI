"""
Utilities for fetching baseline indicators from public data sources.
"""
import json
import os
import time
import statistics
from bisect import bisect_left
from concurrent.futures import ThreadPoolExecutor
import requests

WORLD_BANK_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json"
WORLD_BANK_ALL_URL = "https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=20000"

DEFAULT_CACHE_TTL_SECONDS = 24 * 60 * 60
DEFAULT_REQUEST_TIMEOUT = 6
DEFAULT_MAX_WORKERS = 12


def _ensure_cache_dir(cache_path):
    cache_dir = os.path.dirname(cache_path)
    if cache_dir and not os.path.isdir(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)


def _read_cache(cache_path, ttl_seconds):
    if not os.path.isfile(cache_path):
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        timestamp = payload.get("timestamp", 0)
        if (time.time() - timestamp) > ttl_seconds:
            return None
        return payload.get("data")
    except (OSError, json.JSONDecodeError):
        return None


def _write_cache(cache_path, data):
    _ensure_cache_dir(cache_path)
    payload = {
        "timestamp": time.time(),
        "data": data
    }
    with open(cache_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def fetch_world_bank_latest(country_code, indicator_code, timeout=DEFAULT_REQUEST_TIMEOUT):
    url = WORLD_BANK_URL.format(country=country_code, indicator=indicator_code)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if not payload or len(payload) < 2 or not payload[1]:
        return None
    for entry in payload[1]:
        value = entry.get("value")
        if value is not None:
            return float(value)
    return None


def fetch_world_bank_latest_with_year(country_code, indicator_code, timeout=DEFAULT_REQUEST_TIMEOUT):
    url = WORLD_BANK_URL.format(country=country_code, indicator=indicator_code)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if not payload or len(payload) < 2 or not payload[1]:
        return {"value": None, "year": None}
    for entry in payload[1]:
        value = entry.get("value")
        if value is not None:
            year = entry.get("date")
            return {"value": float(value), "year": year}
    return {"value": None, "year": None}


def fetch_world_bank_all_latest(indicator_code, timeout=DEFAULT_REQUEST_TIMEOUT):
    url = WORLD_BANK_ALL_URL.format(indicator=indicator_code)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if not payload or len(payload) < 2 or not payload[1]:
        return {}

    latest_by_country = {}
    for entry in payload[1]:
        value = entry.get("value")
        if value is None:
            continue
        country = entry.get("country", {}).get("id")
        if not country or country in latest_by_country:
            continue
        latest_by_country[country] = float(value)

    return latest_by_country


def load_world_bank_indicators(
    country_codes,
    indicator_codes,
    cache_path,
    ttl_seconds=DEFAULT_CACHE_TTL_SECONDS,
    max_workers=DEFAULT_MAX_WORKERS
):
    cached = _read_cache(cache_path, ttl_seconds)
    if cached:
        return cached

    data = {indicator: {} for indicator in indicator_codes}
    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for indicator in indicator_codes:
            for country_name, country_code in country_codes.items():
                tasks.append(
                    executor.submit(fetch_world_bank_latest, country_code, indicator)
                )

        index = 0
        for indicator in indicator_codes:
            for country_name in country_codes.keys():
                future = tasks[index]
                index += 1
                try:
                    value = future.result()
                except requests.RequestException:
                    value = None
                except Exception:
                    value = None
                data[indicator][country_name] = value

    _write_cache(cache_path, data)
    return data


def load_world_bank_indicator_snapshot(
    country_codes,
    indicator_codes,
    max_workers=DEFAULT_MAX_WORKERS
):
    data = {indicator: {} for indicator in indicator_codes}
    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for indicator in indicator_codes:
            for country_name, country_code in country_codes.items():
                tasks.append(
                    executor.submit(fetch_world_bank_latest_with_year, country_code, indicator)
                )

        index = 0
        for indicator in indicator_codes:
            for country_name in country_codes.keys():
                future = tasks[index]
                index += 1
                try:
                    payload = future.result()
                except requests.RequestException:
                    payload = {"value": None, "year": None}
                except Exception:
                    payload = {"value": None, "year": None}
                data[indicator][country_name] = payload

    return data


def load_world_bank_global_indicators(
    indicator_codes,
    cache_path,
    ttl_seconds=DEFAULT_CACHE_TTL_SECONDS,
    max_workers=DEFAULT_MAX_WORKERS
):
    cached = _read_cache(cache_path, ttl_seconds)
    if cached:
        return cached

    data = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_world_bank_all_latest, indicator): indicator
            for indicator in indicator_codes
        }
        for future, indicator in futures.items():
            try:
                data[indicator] = future.result()
            except requests.RequestException:
                data[indicator] = {}
            except Exception:
                data[indicator] = {}

    _write_cache(cache_path, data)
    return data


def normalize_indicator(values_by_country, higher_is_better=True):
    values = [value for value in values_by_country.values() if value is not None]
    if not values:
        return {country: 50 for country in values_by_country}

    min_value = min(values)
    max_value = max(values)
    if abs(max_value - min_value) < 1e-9:
        return {country: 50 for country in values_by_country}

    median_value = statistics.median(values)
    normalized = {}
    for country, value in values_by_country.items():
        value = median_value if value is None else value
        ratio = (value - min_value) / (max_value - min_value)
        ratio = 1 - ratio if not higher_is_better else ratio
        normalized[country] = round(ratio * 100)

    return normalized


def normalize_indicator_global(values_by_country, global_values, higher_is_better=True):
    values = [value for value in global_values if value is not None]
    if not values:
        return {country: 50 for country in values_by_country}

    sorted_values = sorted(values)
    median_value = statistics.median(sorted_values)
    max_index = max(len(sorted_values) - 1, 1)

    normalized = {}
    for country, value in values_by_country.items():
        value = median_value if value is None else value
        rank = bisect_left(sorted_values, value)
        percentile = rank / max_index
        percentile = 1 - percentile if not higher_is_better else percentile
        normalized[country] = round(percentile * 100)

    return normalized

"""
Baseline resilience model for 10 countries.
Fetches indicators from public data sources and computes aspect scores.
"""
import os
from .scoring import ResilienceScorer
from .data_sources import (
    load_world_bank_indicators,
    load_world_bank_indicator_snapshot,
    load_world_bank_global_indicators,
    normalize_indicator,
    normalize_indicator_global
)

INDICATOR_SPECS = {
    'gdp_per_capita': {
        'code': 'NY.GDP.PCAP.CD',
        'higher_is_better': True
    },
    'gdp_growth': {
        'code': 'NY.GDP.MKTP.KD.ZG',
        'higher_is_better': True
    },
    'inflation': {
        'code': 'FP.CPI.TOTL.ZG',
        'higher_is_better': False
    },
    'debt_gdp': {
        'code': 'GC.DOD.TOTL.GD.ZS',
        'higher_is_better': False
    },
    'military_spend_gdp': {
        'code': 'MS.MIL.XPND.GD.ZS',
        'higher_is_better': True
    },
    'health_spend_per_capita': {
        'code': 'SH.XPD.CHEX.PC.CD',
        'higher_is_better': True
    },
    'internet_users': {
        'code': 'IT.NET.USER.ZS',
        'higher_is_better': True
    },
    'gini': {
        'code': 'SI.POV.GINI',
        'higher_is_better': False
    },
    'energy_imports': {
        'code': 'EG.IMP.CONS.ZS',
        'higher_is_better': False
    },
    'life_expectancy': {
        'code': 'SP.DYN.LE00.IN',
        'higher_is_better': True
    }
}

INDICATORS = list(INDICATOR_SPECS.keys())

ASPECT_WEIGHTS = {
    'Economic Stability': {
        'gdp_per_capita': 0.4,
        'gdp_growth': 0.3,
        'inflation': 0.3
    },
    'Defense & Strategic Security': {
        'military_spend_gdp': 0.6,
        'gdp_per_capita': 0.4
    },
    'Healthcare & Biological Readiness': {
        'health_spend_per_capita': 0.7,
        'life_expectancy': 0.3
    },
    'Cyber Resilience & Digital Infrastructure': {
        'internet_users': 0.7,
        'gdp_per_capita': 0.3
    },
    'Demographic & Social Stability': {
        'gini': 0.5,
        'life_expectancy': 0.3,
        'gdp_per_capita': 0.2
    },
    'Energy Security': {
        'energy_imports': 0.7,
        'gdp_per_capita': 0.3
    },
    'Debt & Fiscal Sustainability': {
        'debt_gdp': 0.7,
        'inflation': 0.3
    }
}

COUNTRY_CODES = {
    'India': 'IND',
    'China': 'CHN',
    'Pakistan': 'PAK',
    'Nepal': 'NPL',
    'Bangladesh': 'BGD',
    'Sri Lanka': 'LKA',
    'USA': 'USA',
    'Russia': 'RUS',
    'Japan': 'JPN',
    'UK': 'GBR'
}

COUNTRIES = list(COUNTRY_CODES.keys())

MODEL_METHODOLOGY = (
    'Baseline scores are computed from public World Bank indicators covering economic '
    'performance, fiscal pressure, defense effort, health capacity, digital access, social '
    'inequality, energy dependence, and longevity. Each resilience aspect is a weighted '
    'blend of normalized indicators. Indicators are normalized to a 0-100 scale across the '
    'tracked countries and aggregated as a simple average across the 7 aspects.'
)


def compute_baseline_scores():
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    cache_path = os.path.join(base_dir, 'world_bank_cache.json')
    global_cache_path = os.path.join(base_dir, 'world_bank_global_cache.json')
    indicator_codes = [spec['code'] for spec in INDICATOR_SPECS.values()]
    raw_data = load_world_bank_indicators(COUNTRY_CODES, indicator_codes, cache_path)
    global_data = load_world_bank_global_indicators(indicator_codes, global_cache_path)

    normalized_indicators = {country: {} for country in COUNTRY_CODES}
    for indicator_name, spec in INDICATOR_SPECS.items():
        code = spec['code']
        values_by_country = raw_data.get(code, {})
        global_values = list(global_data.get(code, {}).values())
        if global_values:
            normalized = normalize_indicator_global(
                values_by_country,
                global_values,
                higher_is_better=spec['higher_is_better']
            )
        else:
            normalized = normalize_indicator(
                values_by_country,
                higher_is_better=spec['higher_is_better']
            )
        for country in COUNTRY_CODES:
            normalized_indicators[country][indicator_name] = normalized.get(country, 50)

    aspect_scores = {}
    for country, indicators in normalized_indicators.items():
        country_aspects = {}
        for aspect, weights in ASPECT_WEIGHTS.items():
            score = 0.0
            for indicator, weight in weights.items():
                score += indicators[indicator] * weight
            country_aspects[aspect] = round(score)
        aspect_scores[country] = country_aspects

    country_scores = {
        country: ResilienceScorer.calculate_total_score(scores)
        for country, scores in aspect_scores.items()
    }

    return {
        'baseline_aspect_scores': aspect_scores,
        'baseline_country_scores': country_scores,
        'normalized_indicators': normalized_indicators,
        'indicator_specs': INDICATOR_SPECS,
        'indicators': INDICATORS,
        'aspect_weights': ASPECT_WEIGHTS,
        'methodology': MODEL_METHODOLOGY
    }


def compute_baseline_audit():
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    global_cache_path = os.path.join(base_dir, 'world_bank_global_cache.json')
    indicator_codes = [spec['code'] for spec in INDICATOR_SPECS.values()]

    snapshot = load_world_bank_indicator_snapshot(COUNTRY_CODES, indicator_codes)
    global_data = load_world_bank_global_indicators(indicator_codes, global_cache_path)

    raw_indicators = {country: {} for country in COUNTRY_CODES}
    indicator_years = {country: {} for country in COUNTRY_CODES}
    normalized_indicators = {country: {} for country in COUNTRY_CODES}

    for indicator_name, spec in INDICATOR_SPECS.items():
        code = spec['code']
        values_by_country = {}
        for country in COUNTRY_CODES:
            payload = snapshot.get(code, {}).get(country, {})
            value = payload.get('value')
            year = payload.get('year')
            values_by_country[country] = value
            raw_indicators[country][indicator_name] = value
            indicator_years[country][indicator_name] = year

        global_values = list(global_data.get(code, {}).values())
        if global_values:
            normalized = normalize_indicator_global(
                values_by_country,
                global_values,
                higher_is_better=spec['higher_is_better']
            )
        else:
            normalized = normalize_indicator(
                values_by_country,
                higher_is_better=spec['higher_is_better']
            )

        for country in COUNTRY_CODES:
            normalized_indicators[country][indicator_name] = normalized.get(country, 50)

    aspect_scores = {}
    for country, indicators in normalized_indicators.items():
        country_aspects = {}
        for aspect, weights in ASPECT_WEIGHTS.items():
            score = 0.0
            for indicator, weight in weights.items():
                score += indicators[indicator] * weight
            country_aspects[aspect] = round(score)
        aspect_scores[country] = country_aspects

    country_scores = {
        country: ResilienceScorer.calculate_total_score(scores)
        for country, scores in aspect_scores.items()
    }

    return {
        'indicator_codes': {name: spec['code'] for name, spec in INDICATOR_SPECS.items()},
        'raw_indicators': raw_indicators,
        'indicator_years': indicator_years,
        'normalized_indicators': normalized_indicators,
        'baseline_aspect_scores': aspect_scores,
        'baseline_country_scores': country_scores,
        'indicators': INDICATORS,
        'aspect_weights': ASPECT_WEIGHTS,
        'methodology': MODEL_METHODOLOGY
    }

"""
Scenario interpretation and impact application logic.
Requires Gemini for reasoning-based scenario profiling and explanations.
"""
import hashlib
from .gemini_api import get_gemini_client
from .scoring import ResilienceScorer
from .baseline_model import COUNTRIES, compute_baseline_scores

ASPECTS = ResilienceScorer.ASPECTS

INTERVENTION_MAP = {
    'Economic Stability': 'stabilize trade flows and secure fiscal buffers',
    'Defense & Strategic Security': 'strengthen emergency readiness and regional coordination',
    'Healthcare & Biological Readiness': 'expand surge capacity and public health logistics',
    'Cyber Resilience & Digital Infrastructure': 'harden critical infrastructure and response playbooks',
    'Demographic & Social Stability': 'increase social support and risk communication',
    'Energy Security': 'diversify energy supply and protect energy infrastructure',
    'Debt & Fiscal Sustainability': 'restructure liabilities and preserve fiscal headroom'
}

DEFAULT_ASPECT_REASONS = {
    'Economic Stability': 'no significant change',
    'Defense & Strategic Security': 'no significant change',
    'Healthcare & Biological Readiness': 'no significant change',
    'Cyber Resilience & Digital Infrastructure': 'no significant change',
    'Demographic & Social Stability': 'no significant change',
    'Energy Security': 'no significant change',
    'Debt & Fiscal Sustainability': 'no significant change'
}

SECTOR_ASPECT_WEIGHTS = {
    'health': {
        'Healthcare & Biological Readiness': 0.7,
        'Demographic & Social Stability': 0.2,
        'Economic Stability': 0.1
    },
    'cyber': {
        'Cyber Resilience & Digital Infrastructure': 0.7,
        'Defense & Strategic Security': 0.2,
        'Economic Stability': 0.1
    },
    'energy': {
        'Energy Security': 0.7,
        'Economic Stability': 0.2,
        'Debt & Fiscal Sustainability': 0.1
    },
    'financial': {
        'Economic Stability': 0.5,
        'Debt & Fiscal Sustainability': 0.3,
        'Demographic & Social Stability': 0.2
    },
    'conflict': {
        'Defense & Strategic Security': 0.5,
        'Economic Stability': 0.2,
        'Demographic & Social Stability': 0.2,
        'Energy Security': 0.1
    },
    'climate': {
        'Economic Stability': 0.3,
        'Healthcare & Biological Readiness': 0.3,
        'Demographic & Social Stability': 0.2,
        'Energy Security': 0.2
    },
    'social': {
        'Demographic & Social Stability': 0.5,
        'Healthcare & Biological Readiness': 0.2,
        'Economic Stability': 0.2,
        'Defense & Strategic Security': 0.1
    },
    'supply_chain': {
        'Economic Stability': 0.5,
        'Energy Security': 0.2,
        'Cyber Resilience & Digital Infrastructure': 0.2,
        'Debt & Fiscal Sustainability': 0.1
    },
    'governance': {
        'Demographic & Social Stability': 0.4,
        'Economic Stability': 0.3,
        'Defense & Strategic Security': 0.2,
        'Debt & Fiscal Sustainability': 0.1
    }
}


def interpret_scenario(text, baseline_aspects=None, api_key=None):
    client = get_gemini_client(api_key=api_key)

    if not client:
        raise RuntimeError('Gemini API is required for scenario interpretation.')

    summary = 'Scenario analyzed.'
    impacts = None

    profile = client.extract_scenario_profile(text)
    if isinstance(profile, dict):
        summary = profile.get('summary', summary)
        impacts = _compute_impacts_from_profile(profile, baseline_aspects)

        if impacts:
            reasons = client.explain_impacts(profile, impacts)
            if reasons and len(reasons) == len(impacts):
                for impact, reason in zip(impacts, reasons):
                    impact['reason'] = reason
            else:
                for impact in impacts:
                    impact['reason'] = _fallback_reason(profile, impact)

    if not impacts:
        result = client.extract_impacts(text)
        if not result or 'impacts' not in result:
            raise RuntimeError('Gemini failed to generate valid impact analysis.')
        summary = result.get('summary', summary)
        impacts = result['impacts']

    sanitized_impacts = _sanitize_impacts(impacts)
    sanitized_impacts = _ensure_country_coverage(sanitized_impacts)
    interventions = _suggest_interventions(sanitized_impacts)

    return {
        'summary': summary,
        'impacts': sanitized_impacts,
        'interventions': interventions
    }


def _compute_impacts_from_profile(profile, baseline_aspects):
    if not isinstance(profile, dict):
        return None

    sectors = profile.get('sectors') or []
    if not sectors:
        sectors = ['supply_chain']

    severity = profile.get('severity', 0.5)
    try:
        severity = float(severity)
    except (TypeError, ValueError):
        severity = 0.5
    severity = max(0.05, min(1.0, severity))

    direction = profile.get('direction', -1)
    direction = 1 if int(direction) > 0 else -1

    affected_countries = profile.get('affected_countries') or []
    summary = str(profile.get('summary', '')).lower()
    scope = str(profile.get('scope', '')).lower()
    is_global = scope == 'global' or 'global' in summary or len(affected_countries) >= 8

    if not affected_countries and is_global:
        affected_countries = COUNTRIES

    if baseline_aspects is None:
        baseline_aspects = compute_baseline_scores().get('baseline_aspect_scores', {})

    base_magnitude = 6 + int(round(14 * severity))
    impacts = []

    for country in COUNTRIES:
        if country in affected_countries:
            multiplier = 1.0
        elif is_global:
            multiplier = 0.35
        else:
            multiplier = 0.2

        aspect_scores = baseline_aspects.get(country, {})
        aspect_deltas = {}
        for sector in sectors:
            weights = SECTOR_ASPECT_WEIGHTS.get(sector, {})
            for aspect, weight in weights.items():
                baseline_score = aspect_scores.get(aspect, 50)
                vulnerability = 0.6 + (1 - baseline_score / 100.0) * 0.8
                delta = direction * base_magnitude * weight * vulnerability * multiplier
                aspect_deltas[aspect] = aspect_deltas.get(aspect, 0.0) + delta

        if not aspect_deltas:
            continue

        sorted_aspects = sorted(aspect_deltas.items(), key=lambda x: abs(x[1]), reverse=True)
        selected = [item for item in sorted_aspects if abs(item[1]) >= 1.5]
        if not selected:
            selected = sorted_aspects[:1]
        else:
            selected = selected[:3]

        for aspect, delta in selected:
            rounded = int(round(delta))
            if rounded == 0:
                rounded = 1 if direction > 0 else -1
            impacts.append({
                'country': country,
                'aspect': aspect,
                'delta': rounded,
                'reason': ''
            })

    return impacts


def _fallback_reason(profile, impact):
    channels = profile.get('channels', []) if isinstance(profile, dict) else []
    sectors = profile.get('sectors', []) if isinstance(profile, dict) else []
    channel_text = channels[0] if channels else 'secondary spillovers'
    sector_text = sectors[0] if sectors else 'cross-sector disruption'
    aspect = impact.get('aspect', 'resilience capacity')
    return f"{sector_text} shock via {channel_text} strains {aspect.lower()}."


def _sanitize_impacts(impacts):
    sanitized_impacts = []
    for impact in impacts or []:
        if not all(k in impact for k in ['country', 'aspect', 'delta']):
            continue

        try:
            delta = int(impact['delta'])
        except (ValueError, TypeError):
            continue

        if delta == 0:
            delta = -1

        delta = max(-20, min(20, delta))
        impact['delta'] = delta

        if 'reason' not in impact or not impact['reason']:
            impact['reason'] = 'AI assessment of scenario impact.'

        sanitized_impacts.append(impact)

    return sanitized_impacts


def _ensure_country_coverage(impacts):
    if not impacts:
        impacts = []

    covered = {impact['country'] for impact in impacts if impact.get('country')}
    missing = [country for country in COUNTRIES if country not in covered]
    if not missing:
        return impacts

    avg_abs = 5
    if impacts:
        avg_abs = sum(abs(impact['delta']) for impact in impacts) / len(impacts)
    magnitude = max(2, int(round(avg_abs * 0.3)))
    if not impacts:
        direction = -1
    else:
        direction = -1 if sum(impact['delta'] for impact in impacts) < 0 else 1
    delta = direction * magnitude

    for country in missing:
        impacts.append({
            'country': country,
            'aspect': 'Economic Stability',
            'delta': delta,
            'reason': 'Global spillovers from the scenario affect trade, investment, and confidence.'
        })

    return impacts


def apply_impacts(baseline_aspects, impacts):
    updated = {}
    deltas = {}

    for country, aspects in baseline_aspects.items():
        updated[country] = aspects.copy()
        deltas[country] = {aspect: 0 for aspect in ASPECTS}

    for impact in impacts:
        country = impact['country']
        aspect = impact['aspect']
        delta = int(round(impact['delta']))
        if country not in updated or aspect not in updated[country]:
            continue
        new_value = max(0, min(100, updated[country][aspect] + delta))
        deltas[country][aspect] += new_value - updated[country][aspect]
        updated[country][aspect] = new_value

    return updated, deltas


def build_rank_changes(baseline_scores, new_scores):
    baseline_ranked = sorted(baseline_scores.items(), key=lambda x: x[1], reverse=True)
    new_ranked = sorted(new_scores.items(), key=lambda x: x[1], reverse=True)

    baseline_pos = {country: idx + 1 for idx, (country, _) in enumerate(baseline_ranked)}
    new_pos = {country: idx + 1 for idx, (country, _) in enumerate(new_ranked)}

    changes = []
    for country, score in new_scores.items():
        change = baseline_pos[country] - new_pos[country]
        changes.append({
            'country': country,
            'rank': new_pos[country],
            'previous_rank': baseline_pos[country],
            'rank_change': change,
            'score': score,
            'score_change': score - baseline_scores[country]
        })

    return sorted(changes, key=lambda x: x['rank'])


def summarize_impacts(rank_changes, deltas):
    ranked = sorted(rank_changes, key=lambda x: x['rank_change'], reverse=True)
    top_risers = [entry for entry in ranked if entry['rank_change'] > 0][:3]
    top_fallers = [entry for entry in reversed(ranked) if entry['rank_change'] < 0][:3]

    aspect_totals = {aspect: 0 for aspect in ASPECTS}
    for aspects in deltas.values():
        for aspect, delta in aspects.items():
            aspect_totals[aspect] += delta

    top_aspects = sorted(
        [{'aspect': aspect, 'delta': value} for aspect, value in aspect_totals.items()],
        key=lambda x: abs(x['delta']),
        reverse=True
    )[:3]

    return {
        'top_risers': top_risers,
        'top_fallers': top_fallers,
        'top_aspects': top_aspects
    }


def build_explanations(impacts):
    explanations = {country: [] for country in COUNTRIES}
    for impact in impacts:
        country = impact['country']
        aspect = impact['aspect']
        delta = impact['delta']
        reason = impact.get('reason', 'Impact applied')
        explanations[country].append(f"{aspect}: {delta:+d} points because {reason}.")

    return {country: ' '.join(lines) if lines else 'No significant changes.' for country, lines in explanations.items()}


def build_aspect_reasons(impacts):
    reasons = {country: {aspect: DEFAULT_ASPECT_REASONS[aspect] for aspect in ASPECTS} for country in COUNTRIES}
    for impact in impacts:
        country = impact['country']
        aspect = impact['aspect']
        if country in reasons and aspect in reasons[country] and impact.get('reason'):
            reasons[country][aspect] = impact['reason']
    return reasons


def build_delta_summary(summary, impact_summary):
    lines = []

    if summary:
        lines.append(f"Scenario: {summary}")

    top_risers = impact_summary.get('top_risers', []) if impact_summary else []
    top_fallers = impact_summary.get('top_fallers', []) if impact_summary else []
    top_aspects = impact_summary.get('top_aspects', []) if impact_summary else []

    if top_risers:
        risers_text = ', '.join(entry['country'] for entry in top_risers)
        lines.append(f"Top risers: {risers_text}")

    if top_fallers:
        fallers_text = ', '.join(entry['country'] for entry in top_fallers)
        lines.append(f"Top fallers: {fallers_text}")

    if top_aspects:
        aspects_text = ', '.join(entry['aspect'] for entry in top_aspects)
        lines.append(f"Most affected aspects: {aspects_text}")

    if not lines:
        return 'Scenario analyzed. No significant changes detected.'

    return '\n'.join(lines)


def _suggest_interventions(impacts):
    suggestions = {country: [] for country in COUNTRIES}
    seen = {country: set() for country in COUNTRIES}

    for impact in impacts:
        country = impact['country']
        aspect = impact['aspect']
        suggestion = INTERVENTION_MAP.get(aspect)
        if suggestion and suggestion not in seen[country]:
            suggestions[country].append(suggestion)
            seen[country].add(suggestion)

    for country, items in suggestions.items():
        if not items:
            suggestions[country] = ['maintain monitoring and contingency planning']
        else:
            suggestions[country] = items[:3]

    return suggestions

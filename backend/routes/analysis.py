"""
Analysis routes for pandemic resilience assessment
"""
from flask import Blueprint, request, jsonify
from utils.baseline_model import compute_baseline_scores, compute_baseline_audit
from utils.impact_engine import (
    interpret_scenario,
    apply_impacts,
    build_rank_changes,
    summarize_impacts,
    build_explanations,
    build_aspect_reasons,
    build_delta_summary
)
from utils.scoring import ResilienceScorer
from utils.auth import require_auth, get_current_user_with_key

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api')

# Store analysis results in memory (per user for demo purposes)
analysis_results = {
    'by_user': {}
}

@analysis_bp.route('/analyze', methods=['POST'])
@require_auth
def analyze():
    """
    Analyze a pandemic scenario and calculate country resilience scores
    
    Request body:
    {
        "headline": "A new virus outbreak in Asia"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'headline' not in data:
            return jsonify({'error': 'Missing headline in request'}), 400
        
        headline = data['headline'].strip()
        
        if not headline:
            return jsonify({'error': 'Headline cannot be empty'}), 400

        user = get_current_user_with_key()
        if not user or not user.get('gemini_api_key'):
            return jsonify({'error': 'Gemini API key required'}), 403

        user_bucket = analysis_results['by_user'].setdefault(user['id'], {'by_headline': {}})

        cache_key = headline.lower()
        cached = user_bucket.get('by_headline', {}).get(cache_key)
        if cached:
            return jsonify(cached), 200
        
        baseline = compute_baseline_scores()
        baseline_aspects = baseline['baseline_aspect_scores']
        baseline_scores = baseline['baseline_country_scores']

        interpretation = interpret_scenario(headline, baseline_aspects, api_key=user['gemini_api_key'])
        updated_aspects, aspect_deltas = apply_impacts(baseline_aspects, interpretation['impacts'])

        updated_scores = {
            country: ResilienceScorer.calculate_total_score(scores)
            for country, scores in updated_aspects.items()
        }

        rank_changes = build_rank_changes(baseline_scores, updated_scores)
        impact_summary = summarize_impacts(rank_changes, aspect_deltas)
        explanations = build_explanations(interpretation['impacts'])
        aspect_reasons = build_aspect_reasons(interpretation['impacts'])
        analysis_summary = build_delta_summary(interpretation.get('summary', ''), impact_summary)

        analysis_result = {
            'analysis': analysis_summary,
            'scenario_summary': interpretation.get('summary', ''),
            'impacts': interpretation.get('impacts', []),
            'country_scores': updated_scores,
            'aspect_scores': updated_aspects,
            'baseline_country_scores': baseline_scores,
            'baseline_aspect_scores': baseline_aspects,
            'aspect_deltas': aspect_deltas,
            'rank_changes': rank_changes,
            'impact_summary': impact_summary,
            'explanations': explanations,
            'aspect_reasons': aspect_reasons,
            'interventions': interpretation.get('interventions', {}),
            'model_metadata': {
                'indicators': baseline['indicators'],
                'aspect_weights': baseline['aspect_weights'],
                'methodology': baseline['methodology']
            }
        }

        user_bucket['last_analysis'] = analysis_result
        user_bucket['by_headline'][cache_key] = analysis_result
        return jsonify(analysis_result), 200
    
    except RuntimeError as e:
        print(f"Error in /analyze: {str(e)}")
        return jsonify({'error': 'Scenario analysis unavailable', 'details': str(e)}), 503
    except Exception as e:
        print(f"Error in /analyze: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@analysis_bp.route('/results', methods=['GET'])
@require_auth
def get_results():
    """
    Get the last analysis results
    """
    try:
        user = get_current_user_with_key()
        user_bucket = analysis_results['by_user'].get(user['id'], {}) if user else {}
        if not user_bucket.get('last_analysis'):
            return jsonify({
                'analysis': 'No analysis yet. Send a pandemic scenario to the chatbot to get started.',
                'country_scores': {},
                'aspect_scores': {},
                'explanations': {}
            }), 200
        
        return jsonify(user_bucket['last_analysis']), 200
    
    except Exception as e:
        print(f"Error in /results: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@analysis_bp.route('/countries', methods=['GET'])
def get_countries():
    """
    Get list of all tracked countries
    """
    countries = [
        'India',
        'China',
        'Pakistan',
        'Nepal',
        'Bangladesh',
        'Sri Lanka',
        'USA',
        'Russia',
        'Japan',
        'UK'
    ]
    
    return jsonify({'countries': countries}), 200

@analysis_bp.route('/aspects', methods=['GET'])
def get_aspects():
    """
    Get list of all resilience aspects
    """
    aspects = ResilienceScorer.ASPECTS
    
    return jsonify({'aspects': aspects}), 200


@analysis_bp.route('/baseline-audit', methods=['GET'])
def get_baseline_audit():
    """
    Return raw indicator values, years, and normalized scores for verification.
    """
    try:
        audit = compute_baseline_audit()
        return jsonify(audit), 200
    except Exception as e:
        print(f"Error in /baseline-audit: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

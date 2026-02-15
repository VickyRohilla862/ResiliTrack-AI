"""
Scoring system for pandemic resilience assessment
"""

class ResilienceScorer:
    """
    Scores countries based on 7 aspects of pandemic resilience
    """
    
    ASPECTS = [
        'Economic Stability',
        'Defense & Strategic Security',
        'Healthcare & Biological Readiness',
        'Cyber Resilience & Digital Infrastructure',
        'Demographic & Social Stability',
        'Energy Security',
        'Debt & Fiscal Sustainability'
    ]
    
    @staticmethod
    def calculate_total_score(aspect_scores):
        """
        Calculate total score as average of all aspects
        
        Args:
            aspect_scores (dict): Dictionary with aspect names as keys and scores as values
        
        Returns:
            int: Total score (0-100)
        """
        if not aspect_scores:
            return 0
        
        total = sum(aspect_scores.values())
        return round(total / len(aspect_scores))
    
    @staticmethod
    def validate_scores(aspect_scores):
        """
        Validate that all scores are within 0-100 range
        
        Args:
            aspect_scores (dict): Dictionary with aspect names and scores
        
        Returns:
            dict: Validated scores (clamped to 0-100)
        """
        validated = {}
        for aspect, score in aspect_scores.items():
            # Clamp score between 0 and 100
            validated[aspect] = max(0, min(100, int(score)))
        
        return validated
    
    @staticmethod
    def get_aspect_insights(country, aspect_scores_before, aspect_scores_after):
        """
        Generate insights about score changes for different aspects
        
        Args:
            country (str): Country name
            aspect_scores_before (dict): Scores before scenario
            aspect_scores_after (dict): Scores after scenario
        
        Returns:
            dict: Dictionary with aspect names and score change explanations
        """
        insights = {}
        
        for aspect in ResilienceScorer.ASPECTS:
            before = aspect_scores_before.get(aspect, 0)
            after = aspect_scores_after.get(aspect, 0)
            change = after - before
            
            if change > 0:
                insights[aspect] = f"+{change} points (Improved)"
            elif change < 0:
                insights[aspect] = f"{change} points (Reduced)"
            else:
                insights[aspect] = f"No change"
        
        return insights

"""
Gemini API utility for fetching pandemic-related data about countries
"""
import os
import google.generativeai as genai
from flask import current_app
import json

class GeminiAPIClient:
    
    def __init__(self, api_key=None):
        api_key = api_key or current_app.config.get('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
        preferred = os.getenv('GEMINI_MODEL') or 'gemini-1.5-flash'
        self.model_names = [preferred]
        self.model = genai.GenerativeModel(self.model_names[0])
        
        # Fallback list of models to try if the preferred one fails
        self.fallback_models = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-2.0-flash',
            'gemini-1.0-pro'
        ]

    def _generate_content(self, prompt):
        # Try preferred model first
        try:
            return self.model.generate_content(prompt)
        except Exception:
            # Try fallback models
            last_error = None
            for model_name in self.fallback_models:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    return self.model.generate_content(prompt)
                except Exception as exc:
                    last_error = exc
            
            # If all fail, try to list models and pick one that works
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                for model_name in available_models:
                    if 'gemini' in model_name:
                        try:
                            self.model = genai.GenerativeModel(model_name)
                            return self.model.generate_content(prompt)
                        except Exception:
                            continue
            except Exception:
                pass
                
            if last_error:
                raise last_error
            raise Exception("No suitable Gemini model found")
    
    def analyze_scenario(self, headline):
        """
        Analyze a pandemic scenario and fetch data about 10 countries
        for 7 different aspects
        """
        
        prompt = f"""
You are a pandemic resilience expert. Given the pandemic scenario: "{headline}"

Analyze the resilience of these 10 countries:
1. India
2. China
3. Pakistan
4. Nepal
5. Bangladesh
6. Sri Lanka
7. USA
8. Russia
9. Japan
10. UK

For each country, evaluate these 7 aspects of pandemic resilience (rate 0-100):
1. Economic Stability (Economic strength and fiscal health)
2. Defense & Strategic Security (Military and emergency response capability)
3. Healthcare & Biological Readiness (Healthcare system quality and pandemic preparedness)
4. Cyber Resilience & Digital Infrastructure (Digital infrastructure and cybersecurity)
5. Demographic & Social Stability (Social cohesion and demographic factors)
6. Energy Security (Energy independence and reliability)
7. Debt & Fiscal Sustainability (Government debt levels and fiscal management)

IMPORTANT: Return ONLY a valid JSON object with no additional text. Use this exact structure:
{{
  "analysis": "Detailed explanation of score changes for each affected country and aspect. Format: 'Country - Aspect: +/-X points because reason. Country - Aspect: +/-X points because reason.' Be specific about which aspects are affected and by how much for EACH country.",
  "country_scores": {{
    "India": <total_score>,
    "China": <total_score>,
    ...
  }},
  "aspect_scores": {{
    "India": {{
      "Economic Stability": <score>,
      "Defense & Strategic Security": <score>,
      "Healthcare & Biological Readiness": <score>,
      "Cyber Resilience & Digital Infrastructure": <score>,
      "Demographic & Social Stability": <score>,
      "Energy Security": <score>,
      "Debt & Fiscal Sustainability": <score>
    }},
    ...
  }},
  "explanations": {{
    "India": "Detailed explanation with specific score changes for each aspect affected by this scenario",
    ...
  }}
}}

Make sure each country's total score is the average of all 7 aspects.
In the analysis field, list ALL score changes in format: 'CountryName - AspectName: +/-points because reason.'
"""
        
        try:
            response = self._generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to parse JSON
            try:
                # Find the JSON object in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    return result
                else:
                    return self._create_default_response(headline)
            except json.JSONDecodeError:
                return self._create_default_response(headline)
        
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return self._create_default_response(headline)

    def extract_impacts(self, headline):
        """
        Extract structured impacts without directly generating final scores.
        Returns JSON with scenario summary and list of impact objects.
        """
        prompt = f"""
You are a resilience analyst. Interpret this scenario and return only valid JSON:
"{headline}"

Return JSON in this exact structure:
{{
    "summary": "1-2 sentence causal summary of the shock",
    "impacts": [
        {{
            "country": "India",
            "aspect": "Economic Stability",
            "delta": -12,
            "confidence": 0.0,
            "reason": "short causal chain explaining the change",
            "channels": ["trade disruption", "cost inflation"]
        }}
    ]
}}

Rules:
- Use only these countries: India, China, Pakistan, Nepal, Bangladesh, Sri Lanka, USA, Russia, Japan, UK.
- Use only these aspects: Economic Stability, Defense & Strategic Security, Healthcare & Biological Readiness,
    Cyber Resilience & Digital Infrastructure, Demographic & Social Stability, Energy Security,
    Debt & Fiscal Sustainability.
- Deltas are integers from -20 to +20 based on severity and relevance. Do not use 0.
- Include at least one impact for each of the 10 countries.
- Provide multiple impacts if the scenario is multi-sector or multi-country.
- Reasons must be 8-18 words, causal, and mention at least one channel.
- The reasoning must be causal, not keyword-based.
"""

        try:
            response = self._generate_content(prompt)
            response_text = response.text.strip()

            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx == -1 or end_idx <= start_idx:
                return None

            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        except Exception as e:
            print(f"Error extracting impacts: {e}")
            return None

    def extract_scenario_profile(self, headline):
        """
        Extract a scenario profile for reasoning-based impact simulation.
        Returns JSON with severity, sectors, scope, and channels.
        """
        prompt = f"""
You are a resilience analyst. Interpret this scenario and return only valid JSON:
"{headline}"

Return JSON in this exact structure:
{{
  "summary": "1-2 sentence causal summary of the shock",
  "severity": 0.0,
  "direction": -1,
    "scope": "regional",
  "affected_countries": ["India"],
  "sectors": ["health"],
  "channels": ["trade disruption", "capacity strain"],
  "secondary_effects": ["spillover to regional supply chains"]
}}

Rules:
- severity is a float from 0.0 to 1.0.
- direction is -1 for adverse shocks, 1 for positive shocks.
- scope is one of: local, regional, global.
- affected_countries is a subset of: India, China, Pakistan, Nepal, Bangladesh, Sri Lanka, USA, Russia, Japan, UK.
- sectors must be chosen from: health, cyber, energy, financial, conflict, climate, social, supply_chain, governance.
- channels are short causal mechanisms (2-4 words each).
- If scope is global, include all countries.
- Do not include any additional text outside the JSON.
"""

        try:
            response = self._generate_content(prompt)
            response_text = response.text.strip()

            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx == -1 or end_idx <= start_idx:
                return None

            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        except Exception as e:
            print(f"Error extracting scenario profile: {e}")
            return None

    def explain_impacts(self, profile, impacts):
        """
        Generate causal reasons for each impact entry.
        Returns a list of strings aligned to the impacts list.
        """
        summary = profile.get('summary', '') if isinstance(profile, dict) else ''
        channels = profile.get('channels', []) if isinstance(profile, dict) else []
        sectors = profile.get('sectors', []) if isinstance(profile, dict) else []

        prompt = f"""
You are a resilience analyst. Provide a short causal reason for each impact.

Scenario summary:
{summary}

Sectors: {sectors}
Channels: {channels}

Impacts (JSON array):
{json.dumps(impacts, ensure_ascii=True)}

Return ONLY a JSON array of strings, same length and order as the impacts list.
Each reason must be 8-20 words, causal, and mention a channel or sector.
Do not include any extra text outside the JSON array.
"""

        try:
            response = self._generate_content(prompt)
            response_text = response.text.strip()

            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx == -1 or end_idx <= start_idx:
                return None

            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            if isinstance(result, list):
                return [str(item) for item in result]
            return None
        except Exception as e:
            print(f"Error generating impact explanations: {e}")
            return None

    def _create_default_response(self, headline):
        """
        Create a default response when API fails
        Used for development/testing - generates dynamic scores based on headline
        """
        import random
        
        # Base scores for each country
        base_scores = {
            "India": {"Economic Stability": 55, "Defense & Strategic Security": 70, "Healthcare & Biological Readiness": 55, "Cyber Resilience & Digital Infrastructure": 50, "Demographic & Social Stability": 50, "Energy Security": 60, "Debt & Fiscal Sustainability": 50},
            "China": {"Economic Stability": 78, "Defense & Strategic Security": 85, "Healthcare & Biological Readiness": 70, "Cyber Resilience & Digital Infrastructure": 80, "Demographic & Social Stability": 60, "Energy Security": 75, "Debt & Fiscal Sustainability": 60},
            "Pakistan": {"Economic Stability": 40, "Defense & Strategic Security": 65, "Healthcare & Biological Readiness": 45, "Cyber Resilience & Digital Infrastructure": 40, "Demographic & Social Stability": 45, "Energy Security": 45, "Debt & Fiscal Sustainability": 35},
            "Nepal": {"Economic Stability": 45, "Defense & Strategic Security": 50, "Healthcare & Biological Readiness": 50, "Cyber Resilience & Digital Infrastructure": 35, "Demographic & Social Stability": 55, "Energy Security": 40, "Debt & Fiscal Sustainability": 40},
            "Bangladesh": {"Economic Stability": 50, "Defense & Strategic Security": 55, "Healthcare & Biological Readiness": 50, "Cyber Resilience & Digital Infrastructure": 40, "Demographic & Social Stability": 50, "Energy Security": 45, "Debt & Fiscal Sustainability": 45},
            "Sri Lanka": {"Economic Stability": 35, "Defense & Strategic Security": 55, "Healthcare & Biological Readiness": 60, "Cyber Resilience & Digital Infrastructure": 45, "Demographic & Social Stability": 50, "Energy Security": 40, "Debt & Fiscal Sustainability": 30},
            "USA": {"Economic Stability": 75, "Defense & Strategic Security": 90, "Healthcare & Biological Readiness": 75, "Cyber Resilience & Digital Infrastructure": 85, "Demographic & Social Stability": 65, "Energy Security": 80, "Debt & Fiscal Sustainability": 60},
            "Russia": {"Economic Stability": 60, "Defense & Strategic Security": 85, "Healthcare & Biological Readiness": 65, "Cyber Resilience & Digital Infrastructure": 70, "Demographic & Social Stability": 55, "Energy Security": 85, "Debt & Fiscal Sustainability": 70},
            "Japan": {"Economic Stability": 80, "Defense & Strategic Security": 75, "Healthcare & Biological Readiness": 85, "Cyber Resilience & Digital Infrastructure": 85, "Demographic & Social Stability": 70, "Energy Security": 65, "Debt & Fiscal Sustainability": 50},
            "UK": {"Economic Stability": 75, "Defense & Strategic Security": 80, "Healthcare & Biological Readiness": 80, "Cyber Resilience & Digital Infrastructure": 80, "Demographic & Social Stability": 70, "Energy Security": 65, "Debt & Fiscal Sustainability": 70}
        }
        
        # Detect scenario type and affected regions/aspects
        headline_lower = headline.lower()
        
        # Determine which countries are most affected
        affected_countries = []
        if any(word in headline_lower for word in ['south asia', 'india', 'pakistan', 'bangladesh', 'nepal', 'sri lanka']):
            affected_countries = ['India', 'Pakistan', 'Bangladesh', 'Nepal', 'Sri Lanka']
        elif any(word in headline_lower for word in ['china', 'chinese']):
            affected_countries = ['China', 'Japan', 'Russia']
        elif any(word in headline_lower for word in ['europe', 'european', 'uk', 'britain']):
            affected_countries = ['UK', 'Russia']
        elif any(word in headline_lower for word in ['america', 'us', 'usa', 'united states']):
            affected_countries = ['USA', 'UK']
        elif any(word in headline_lower for word in ['russia', 'russian']):
            affected_countries = ['Russia', 'China']
        elif any(word in headline_lower for word in ['global', 'world', 'worldwide', 'international']):
            affected_countries = list(base_scores.keys())
        else:
            # Random affected countries
            affected_countries = random.sample(list(base_scores.keys()), random.randint(3, 6))
        
        # Determine which aspects are affected
        affected_aspects = []
        impact_range = (5, 15)  # Points to deduct/add
        
        if any(word in headline_lower for word in ['earthquake', 'tsunami', 'flood', 'hurricane', 'storm', 'disaster', 'cyclone']):
            affected_aspects = [('Cyber Resilience & Digital Infrastructure', -1), ('Healthcare & Biological Readiness', -1), ('Defense & Strategic Security', -1)]
            impact_range = (8, 15)
        elif any(word in headline_lower for word in ['virus', 'pandemic', 'disease', 'outbreak', 'epidemic', 'covid', 'flu']):
            affected_aspects = [('Healthcare & Biological Readiness', -1), ('Economic Stability', -1), ('Demographic & Social Stability', -1)]
            impact_range = (10, 18)
        elif any(word in headline_lower for word in ['war', 'conflict', 'attack', 'military', 'invasion']):
            affected_aspects = [('Defense & Strategic Security', -1), ('Economic Stability', -1), ('Energy Security', -1)]
            impact_range = (12, 20)
        elif any(word in headline_lower for word in ['recession', 'crisis', 'crash', 'economic', 'financial', 'shortage']):
            affected_aspects = [('Economic Stability', -1), ('Debt & Fiscal Sustainability', -1), ('Demographic & Social Stability', -1)]
            impact_range = (10, 18)
        elif any(word in headline_lower for word in ['cyber', 'hack', 'technology', 'digital']):
            affected_aspects = [('Cyber Resilience & Digital Infrastructure', -1), ('Defense & Strategic Security', -1)]
            impact_range = (8, 14)
        elif any(word in headline_lower for word in ['energy', 'oil', 'gas', 'power', 'electricity']):
            affected_aspects = [('Energy Security', -1), ('Economic Stability', -1)]
            impact_range = (10, 16)
        elif any(word in headline_lower for word in ['debt', 'default', 'bankruptcy', 'fiscal']):
            affected_aspects = [('Debt & Fiscal Sustainability', -1), ('Economic Stability', -1)]
            impact_range = (12, 20)
        else:
            # Default mixed impact
            all_aspects = list(base_scores[list(base_scores.keys())[0]].keys())
            affected_aspects = [(asp, -1) for asp in random.sample(all_aspects, random.randint(2, 4))]
            impact_range = (5, 12)
        
        # Apply changes to scores
        modified_scores = {}
        explanations = {}
        analysis_parts = []
        
        for country, aspects in base_scores.items():
            modified_scores[country] = aspects.copy()
            country_changes = []
            
            if country in affected_countries:
                for aspect, direction in affected_aspects:
                    change = random.randint(impact_range[0], impact_range[1]) * direction
                    modified_scores[country][aspect] = max(0, min(100, aspects[aspect] + change))
                    
                    if change < 0:
                        reason = f"due to {headline_lower[:40]}..."
                        analysis_parts.append(f"{country} - {aspect}: {change} points {reason}")
                        country_changes.append(f"{aspect}: {change} points")
                    elif change > 0:
                        reason = f"from improved response to {headline_lower[:40]}..."
                        analysis_parts.append(f"{country} - {aspect}: +{change} points {reason}")
                        country_changes.append(f"{aspect}: +{change} points")
            else:
                # Small random variations for non-affected countries
                if random.random() < 0.5:
                    aspect = random.choice(list(aspects.keys()))
                    change = random.randint(-3, 3)
                    modified_scores[country][aspect] = max(0, min(100, aspects[aspect] + change))
                    if change != 0:
                        country_changes.append(f"{aspect}: {change:+d} points (minor)")
            
            # Create explanation
            if country_changes:
                explanations[country] = f"Score changes: {'. '.join(country_changes)}. Overall resilience {'decreased' if country in affected_countries else 'stable'} for this scenario."
            else:
                explanations[country] = f"No significant changes. Resilience remains stable at baseline levels for this scenario."
        
        # Calculate total scores
        country_scores = {}
        for country, aspects in modified_scores.items():
            total = sum(aspects.values()) / len(aspects)
            country_scores[country] = round(total, 1)
        
        analysis_text = f"Analyzing pandemic scenario: {headline}. " + " ".join(analysis_parts[:6])
        if len(analysis_parts) > 6:
            analysis_text += f" ({len(analysis_parts) - 6} more changes...)"
        
        return {
            "analysis": analysis_text,
            "country_scores": country_scores,
            "aspect_scores": modified_scores,
            "explanations": explanations
        }

def get_gemini_client(api_key=None):
    """Factory function to get Gemini client"""
    api_key = api_key or current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return None
    return GeminiAPIClient(api_key=api_key)

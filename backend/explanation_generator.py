# backend/explanation_generator.py
from transformers import pipeline
from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

class NewsExplanationGenerator:
    """Generate balanced explanations for news analysis results"""
    
    def __init__(self):
        try:
            # Load a text generation model for creating explanations
            self.text_generator = pipeline(
                "text2text-generation",
                model="google/flan-t5-small",  # Lightweight model for explanations
                max_length=200
            )
        except Exception as e:
            logger.warning(f"Could not load text generation model: {e}")
            self.text_generator = None
    
    def _extract_key_entities(self, text: str) -> Dict:
        """Extract key entities and topics from the news text"""
        text_lower = text.lower()
        
        # Political entities
        political_keywords = ['president', 'senator', 'congress', 'government', 'minister', 
                            'parliament', 'election', 'vote', 'policy', 'law']
        
        # Economic entities  
        economic_keywords = ['economy', 'market', 'stock', 'price', 'inflation', 'gdp',
                           'company', 'business', 'financial', 'bank']
        
        # Social entities
        social_keywords = ['health', 'education', 'crime', 'community', 'social',
                         'public', 'people', 'citizen']
        
        # Technology entities
        tech_keywords = ['technology', 'digital', 'internet', 'ai', 'computer',
                        'software', 'data', 'cyber']
        
        categories = {
            'political': sum(1 for kw in political_keywords if kw in text_lower),
            'economic': sum(1 for kw in economic_keywords if kw in text_lower),
            'social': sum(1 for kw in social_keywords if kw in text_lower),
            'technology': sum(1 for kw in tech_keywords if kw in text_lower)
        }
        
        # Determine primary category
        primary_category = max(categories, key=categories.get) if any(categories.values()) else 'general'
        
        # Extract mentioned entities (simple approach)
        entities = []
        
        # Find proper nouns (capitalized words)
        words = text.split()
        for i, word in enumerate(words):
            if word.istitle() and len(word) > 2:
                # Check if it's part of a multi-word entity
                entity = word
                j = i + 1
                while j < len(words) and words[j].istitle():
                    entity += " " + words[j]
                    j += 1
                entities.append(entity)
        
        return {
            'categories': categories,
            'primary_category': primary_category,
            'entities': entities[:5]  # Limit to top 5 entities
        }
    
    def _generate_positive_aspects(self, text: str, entities: Dict, classification: str) -> str:
        """Generate positive aspects of the news"""
        if classification == "FAKE":
            return "N/A for fake news"
        
        primary_category = entities['primary_category']
        
        # Template-based positive aspect generation
        positive_templates = {
            'political': [
                "This news may indicate progress in democratic processes and governance.",
                "Political developments can lead to improved policies and public representation.",
                "Such political events often reflect active civic engagement."
            ],
            'economic': [
                "Economic news often signals market opportunities and growth potential.",
                "Such developments may benefit businesses and employment prospects.",
                "Economic changes can lead to improved financial conditions for many."
            ],
            'social': [
                "This news highlights important social issues requiring public attention.",
                "Social developments often lead to positive community changes.",
                "Such events may drive awareness and social progress."
            ],
            'technology': [
                "Technological developments typically drive innovation and progress.",
                "Such tech news often represents advancement in human capabilities.",
                "Technology stories frequently highlight problem-solving potential."
            ],
            'general': [
                "This news provides important information for public awareness.",
                "Such reporting contributes to an informed society.",
                "News coverage helps people stay connected to current events."
            ]
        }
        
        # Use AI generation if available
        if self.text_generator and len(text) > 20:
            try:
                prompt = f"Identify positive aspects of this news: {text[:200]}"
                result = self.text_generator(prompt, max_length=100, do_sample=False)
                ai_generated = result[0]['generated_text'].strip()
                if ai_generated and len(ai_generated) > 10:
                    return ai_generated
            except Exception as e:
                logger.debug(f"AI generation failed for positive aspects: {e}")
        
        # Fallback to templates
        import random
        return random.choice(positive_templates.get(primary_category, positive_templates['general']))
    
    def _generate_negative_aspects(self, text: str, entities: Dict, classification: str, 
                                 forensic_results: Dict) -> str:
        """Generate negative aspects or concerns"""
        if classification == "FAKE":
            red_flags = forensic_results.get('credibility_assessment', {}).get('red_flags', [])
            if red_flags:
                return f"This appears to be fake news with concerning patterns: {', '.join(red_flags)}"
            else:
                return "This content appears to be fake news and may spread misinformation."
        
        # For real news, identify potential concerns
        concerns = []
        text_lower = text.lower()
        
        # Check for concerning topics
        if any(word in text_lower for word in ['crisis', 'emergency', 'disaster', 'threat']):
            concerns.append("may involve serious public safety concerns")
        
        if any(word in text_lower for word in ['conflict', 'war', 'violence', 'attack']):
            concerns.append("involves conflict or violence that affects communities")
        
        if any(word in text_lower for word in ['corruption', 'scandal', 'fraud', 'illegal']):
            concerns.append("involves legal or ethical issues requiring investigation")
        
        # Economic concerns
        if any(word in text_lower for word in ['recession', 'unemployment', 'inflation', 'debt']):
            concerns.append("may have negative economic implications")
        
        if concerns:
            return f"Potential concerns: This news {', and '.join(concerns)}."
        
        # Use AI generation if available
        if self.text_generator and len(text) > 20:
            try:
                prompt = f"Identify potential risks or concerns from this news: {text[:200]}"
                result = self.text_generator(prompt, max_length=100, do_sample=False)
                ai_generated = result[0]['generated_text'].strip()
                if ai_generated and len(ai_generated) > 10:
                    return ai_generated
            except Exception as e:
                logger.debug(f"AI generation failed for negative aspects: {e}")
        
        # Default neutral response
        return "As with all news, it's important to consider multiple perspectives and verify information through additional sources."
    
    def _generate_neutral_context(self, text: str, entities: Dict, fact_check_result: Dict) -> str:
        """Generate neutral, contextual information"""
        context_points = []
        
        # Add fact-check context
        fact_status = fact_check_result.get('status', 'UNKNOWN')
        if fact_status == 'SUPPORTED':
            context_points.append("This information has been corroborated by trusted news sources")
        elif fact_status == 'UNVERIFIED_RECENT':
            context_points.append("This appears to be recent news that is still being verified")
        elif fact_status == 'NOT_FOUND':
            context_points.append("This claim has not been independently verified by major news outlets")
        
        # Add entity context
        if entities['entities']:
            main_entities = entities['entities'][:2]
            context_points.append(f"Key entities mentioned: {', '.join(main_entities)}")
        
        # Add category context
        primary_cat = entities['primary_category']
        if primary_cat != 'general':
            context_points.append(f"This falls under {primary_cat} news category")
        
        # Use AI for additional context if available
        if self.text_generator and len(text) > 20:
            try:
                prompt = f"Provide neutral background context for this news: {text[:200]}"
                result = self.text_generator(prompt, max_length=100, do_sample=False)
                ai_context = result[0]['generated_text'].strip()
                if ai_context and len(ai_context) > 10:
                    context_points.append(ai_context)
            except Exception as e:
                logger.debug(f"AI generation failed for neutral context: {e}")
        
        return ". ".join(context_points) if context_points else "Additional context is recommended for full understanding."
    
    def _generate_fake_news_explanation(self, text: str, ml_result: Dict, 
                                      forensic_results: Dict, fact_check_result: Dict) -> str:
        """Generate explanation for why content is classified as fake news"""
        reasons = []
        
        # ML model reasoning
        ml_confidence = ml_result.get('confidence', 0)
        if ml_confidence > 0.8:
            reasons.append(f"Machine learning model classified this as fake with {ml_confidence:.1%} confidence")
        
        # Forensic red flags
        red_flags = forensic_results.get('credibility_assessment', {}).get('red_flags', [])
        if red_flags:
            flag_descriptions = {
                'excessive_exclamations': 'excessive use of exclamation marks',
                'excessive_capitals': 'overuse of capital letters',
                'clickbait_language': 'clickbait-style language patterns',
                'overly_long_sentences': 'unusually long and complex sentences',
                'no_source_attribution': 'lack of credible source citations'
            }
            
            flag_explanations = [flag_descriptions.get(flag, flag) for flag in red_flags]
            reasons.append(f"Forensic analysis detected: {', '.join(flag_explanations)}")
        
        # Fact-check reasoning
        fact_status = fact_check_result.get('status', 'UNKNOWN')
        if fact_status == 'NOT_FOUND':
            reasons.append("No supporting evidence found in trusted news sources")
        elif fact_status == 'CONFLICTING':
            reasons.append("Conflicting information found in reliable sources")
        
        # Sensational keywords
        sensational = forensic_results.get('content_analysis', {}).get('sensational_keywords', {})
        found_sensational = [category for category, words in sensational.items() if words]
        if found_sensational:
            reasons.append(f"Contains sensational language patterns: {', '.join(found_sensational)}")
        
        if reasons:
            return f"This content is likely fake because: {'; '.join(reasons)}."
        else:
            return "This content shows patterns typical of fake news, though specific indicators may vary."
    
    def generate_comprehensive_explanation(self, 
                                         text: str, 
                                         classification: str,
                                         ml_result: Dict,
                                         fact_check_result: Dict,
                                         forensic_results: Dict) -> Dict:
        """Generate comprehensive explanation for the analysis results"""
        
        # Extract entities and context
        entities = self._extract_key_entities(text)
        
        # Generate input summary
        input_summary = text[:200] + "..." if len(text) > 200 else text
        
        if classification == "FAKE":
            return {
                'positive': "N/A - Content classified as fake news",
                'negative': self._generate_fake_news_explanation(text, ml_result, forensic_results, fact_check_result),
                'neutral': self._generate_neutral_context(text, entities, fact_check_result),
                'context': f"Analysis based on ML classification, forensic checks, and fact verification. "
                          f"Primary category: {entities['primary_category']}. "
                          f"Key entities: {', '.join(entities['entities'][:3]) if entities['entities'] else 'None identified'}."
            }
        else:  # REAL news
            return {
                'positive': self._generate_positive_aspects(text, entities, classification),
                'negative': self._generate_negative_aspects(text, entities, classification, forensic_results),
                'neutral': self._generate_neutral_context(text, entities, fact_check_result),
                'context': f"This appears to be legitimate news content. "
                          f"Primary category: {entities['primary_category']}. "
                          f"Verification status: {fact_check_result.get('status', 'Unknown')}. "
                          f"Key entities: {', '.join(entities['entities'][:3]) if entities['entities'] else 'None identified'}."
            }

# Global instance
explanation_generator = NewsExplanationGenerator()

def generate_news_explanation(text: str, classification: str, ml_result: Dict,
                            fact_check_result: Dict, forensic_results: Dict) -> Dict:
    """Utility function to generate news explanation"""
    return explanation_generator.generate_comprehensive_explanation(
        text, classification, ml_result, fact_check_result, forensic_results
    )

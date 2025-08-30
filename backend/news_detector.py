# backend/news_detector.py
import re
from typing import Dict, List, Tuple
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class NewsDetector:
    """Advanced news detection system to identify if text is news content"""
    
    def __init__(self):
        # Load a classification model for text analysis
        try:
            # Use a general text classification model to help with news detection
            self.text_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
        except Exception as e:
            logger.warning(f"Could not load zero-shot classifier: {e}")
            self.text_classifier = None
    
    def _extract_linguistic_features(self, text: str) -> Dict:
        """Extract linguistic features that indicate news content"""
        words = text.split()
        sentences = text.split('.')
        
        # News-specific vocabulary
        news_keywords = {
            'temporal': ['today', 'yesterday', 'breaking', 'latest', 'recent', 'now', 'just'],
            'authority': ['president', 'minister', 'official', 'spokesperson', 'government', 
                         'police', 'court', 'judge', 'senator', 'congress'],
            'reporting': ['said', 'reported', 'according', 'sources', 'confirmed', 
                         'announced', 'revealed', 'disclosed', 'stated'],
            'locations': ['city', 'state', 'country', 'national', 'local', 'international'],
            'organizations': ['company', 'corporation', 'department', 'agency', 'committee']
        }
        
        # Count occurrences of each category
        category_counts = {}
        text_lower = text.lower()
        
        for category, keywords in news_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            category_counts[category] = count
        
        # Calculate features
        features = {
            'word_count': len(words),
            'sentence_count': max(1, len([s for s in sentences if s.strip()])),
            'avg_words_per_sentence': len(words) / max(1, len(sentences)),
            'news_keyword_categories': category_counts,
            'total_news_keywords': sum(category_counts.values()),
            'has_quotes': '"' in text or "'" in text,
            'has_timestamps': bool(re.search(r'\b(20\d{2}|19\d{2})\b', text)),
            'has_locations': bool(re.search(r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b', text)),
            'title_case_ratio': sum(1 for w in words if w.istitle()) / max(len(words), 1)
        }
        
        return features
    
    def _calculate_news_probability(self, text: str, features: Dict) -> float:
        """Calculate probability that text is news content based on features"""
        score = 0.0
        
        # Length-based scoring
        word_count = features['word_count']
        if 5 <= word_count <= 50:  # Typical headline length
            score += 0.3
        elif 50 <= word_count <= 500:  # Short article
            score += 0.4
        elif word_count > 500:  # Full article
            score += 0.5
        
        # News keyword scoring
        total_keywords = features['total_news_keywords']
        if total_keywords >= 3:
            score += 0.3
        elif total_keywords >= 1:
            score += 0.15
        
        # Authority/reporting keywords (strong indicators)
        authority_count = features['news_keyword_categories'].get('authority', 0)
        reporting_count = features['news_keyword_categories'].get('reporting', 0)
        
        if authority_count > 0 and reporting_count > 0:
            score += 0.25
        elif authority_count > 0 or reporting_count > 0:
            score += 0.15
        
        # Structure-based scoring
        if features['has_quotes']:
            score += 0.1
        if features['has_timestamps']:
            score += 0.1
        if features['has_locations']:
            score += 0.1
        
        # Title case ratio (proper nouns common in news)
        if features['title_case_ratio'] > 0.3:
            score += 0.1
        
        # Sentence structure
        avg_words = features['avg_words_per_sentence']
        if 8 <= avg_words <= 25:  # Typical news sentence length
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _use_ai_classification(self, text: str) -> float:
        """Use AI model to classify if text is news-related"""
        if not self.text_classifier:
            return 0.5  # Neutral if no model available
            
        try:
            candidate_labels = ["news article", "headline", "breaking news", 
                              "casual conversation", "random text", "advertisement"]
            
            result = self.text_classifier(text[:512], candidate_labels)
            
            # Calculate news probability from classification scores
            news_labels = ["news article", "headline", "breaking news"]
            news_score = sum(score for label, score in zip(result['labels'], result['scores']) 
                           if label in news_labels)
            
            return min(news_score, 1.0)
            
        except Exception as e:
            logger.warning(f"AI classification failed: {e}")
            return 0.5
    
    def detect_news(self, text: str, threshold: float = 0.6) -> Dict:
        """
        Main function to detect if text is news content
        
        Args:
            text: Input text to analyze
            threshold: Minimum score to classify as news (default: 0.6)
            
        Returns:
            Dict with detection results
        """
        if not text or len(text.strip()) < 3:
            return {
                'is_news': False,
                'confidence': 0.0,
                'reason': 'Text too short or empty',
                'features': {}
            }
        
        # Extract features
        features = self._extract_linguistic_features(text)
        
        # Calculate rule-based probability
        rule_based_score = self._calculate_news_probability(text, features)
        
        # Get AI-based probability
        ai_score = self._use_ai_classification(text)
        
        # Combine scores (weighted average)
        combined_score = 0.7 * rule_based_score + 0.3 * ai_score
        
        is_news = combined_score >= threshold
        
        # Determine reason
        if not is_news:
            if features['word_count'] < 5:
                reason = "Text too short to be news"
            elif features['total_news_keywords'] == 0:
                reason = "No news-related keywords found"
            else:
                reason = f"Low news probability (score: {combined_score:.2f})"
        else:
            key_indicators = []
            if features['news_keyword_categories']['authority'] > 0:
                key_indicators.append("authority figures mentioned")
            if features['news_keyword_categories']['reporting'] > 0:
                key_indicators.append("reporting language")
            if features['has_quotes']:
                key_indicators.append("quoted statements")
            if features['has_timestamps']:
                key_indicators.append("temporal references")
                
            reason = f"News detected. Key indicators: {', '.join(key_indicators) if key_indicators else 'general news structure'}"
        
        return {
            'is_news': is_news,
            'confidence': round(combined_score, 3),
            'reason': reason,
            'features': {
                'word_count': features['word_count'],
                'news_keywords': features['total_news_keywords'],
                'has_authority_figures': features['news_keyword_categories']['authority'] > 0,
                'has_reporting_language': features['news_keyword_categories']['reporting'] > 0,
                'has_quotes': features['has_quotes'],
                'rule_based_score': round(rule_based_score, 3),
                'ai_score': round(ai_score, 3) if ai_score != 0.5 else None
            }
        }
    
    def is_news_headline(self, text: str) -> bool:
        """Quick check if text appears to be a news headline"""
        words = text.split()
        return (
            4 <= len(words) <= 25 and  # Reasonable headline length
            any(w.istitle() for w in words) and  # Contains proper nouns
            not text.lower().startswith(('hi', 'hello', 'i', 'you', 'what', 'how'))  # Not conversational
        )
    
    def is_news_article(self, text: str) -> bool:
        """Check if text appears to be a full news article"""
        return (
            len(text.split()) > 30 and  # Long enough to be an article
            text.count('.') >= 2 and  # Multiple sentences
            self.detect_news(text, threshold=0.5)['is_news']  # Lower threshold for full articles
        )

# Global instance for use across modules
news_detector = NewsDetector()

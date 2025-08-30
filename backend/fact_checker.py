# backend/fact_checker.py
import asyncio
import httpx
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from typing import Dict, List, Optional, Tuple
import logging
import re
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedFactChecker:
    """Enhanced fact-checking system with better handling of new/unverified news"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Trusted news sources with reliability scores
        self.trusted_sources = {
            "https://www.bbc.com/news": {"reliability": 0.95, "region": "global"},
            "https://www.reuters.com": {"reliability": 0.98, "region": "global"},
            "https://www.apnews.com": {"reliability": 0.96, "region": "global"},
            "https://www.cnn.com": {"reliability": 0.85, "region": "us"},
            "https://www.nytimes.com": {"reliability": 0.90, "region": "us"},
            "https://www.theguardian.com": {"reliability": 0.88, "region": "uk"},
            "https://www.washingtonpost.com": {"reliability": 0.89, "region": "us"},
            "https://www.aljazeera.com": {"reliability": 0.82, "region": "global"},
            "https://www.npr.org": {"reliability": 0.91, "region": "us"},
            "https://www.hindustantimes.com": {"reliability": 0.78, "region": "india"},
        }
        
        # Fact-checking specific sources
        self.factcheck_sources = [
            "https://www.snopes.com",
            "https://www.factcheck.org",
            "https://www.politifact.com"
        ]
    
    def _get_cache_filename(self, cache_type: str) -> Path:
        """Get cache filename with timestamp"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.cache_dir / f"{cache_type}_{today}.json"
    
    def _load_from_cache(self, cache_type: str, max_age_hours: int = 2) -> Optional[List]:
        """Load data from cache if recent enough"""
        cache_file = self._get_cache_filename(cache_type)
        
        if not cache_file.exists():
            return None
            
        try:
            # Check if cache is recent enough
            file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_age > timedelta(hours=max_age_hours):
                return None
                
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} items from cache: {cache_type}")
                return data
                
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_type}: {e}")
            return None
    
    def _save_to_cache(self, cache_type: str, data: List):
        """Save data to cache"""
        cache_file = self._get_cache_filename(cache_type)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Cached {len(data)} items: {cache_type}")
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_type}: {e}")
    
    async def fetch_trusted_headlines(self, max_per_source: int = 50) -> List[Dict]:
        """Fetch recent headlines from trusted sources with metadata"""
        # Try cache first
        cached_headlines = self._load_from_cache("trusted_headlines")
        if cached_headlines:
            return cached_headlines
        
        headlines = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for source_url, metadata in self.trusted_sources.items():
                try:
                    logger.info(f"Fetching from {source_url}")
                    response = await client.get(source_url)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Extract headlines with better selectors
                    headline_selectors = [
                        'h1', 'h2', 'h3',  # Standard headers
                        '.headline', '.title',  # Common CSS classes
                        '[data-testid*="headline"]',  # Modern web elements
                        'article h1', 'article h2'  # Article-specific headers
                    ]
                    
                    source_headlines = []
                    for selector in headline_selectors:
                        elements = soup.select(selector)[:max_per_source]
                        for element in elements:
                            headline_text = element.get_text(strip=True)
                            if len(headline_text.split()) >= 4:  # Reasonable headline length
                                source_headlines.append({
                                    'text': headline_text,
                                    'source_url': source_url,
                                    'reliability': metadata['reliability'],
                                    'region': metadata['region'],
                                    'fetched_at': datetime.now().isoformat()
                                })
                    
                    headlines.extend(source_headlines[:max_per_source])
                    logger.info(f"Fetched {len(source_headlines)} headlines from {source_url}")
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source_url}: {e}")
                    continue
        
        # Cache the results
        self._save_to_cache("trusted_headlines", headlines)
        logger.info(f"Total headlines fetched: {len(headlines)}")
        return headlines
    
    def find_similar_headlines(self, claim: str, headlines: List[Dict], 
                             min_similarity: float = 0.7) -> List[Dict]:
        """Find headlines similar to the claim using semantic similarity"""
        if not headlines:
            return []
        
        try:
            # Encode claim
            claim_embedding = self.embedding_model.encode(claim, convert_to_tensor=True)
            
            # Encode all headlines
            headline_texts = [h['text'] for h in headlines]
            headline_embeddings = self.embedding_model.encode(headline_texts, convert_to_tensor=True)
            
            # Calculate similarities
            similarities = util.pytorch_cos_sim(claim_embedding, headline_embeddings)[0]
            
            # Find matches above threshold
            similar_headlines = []
            for i, similarity in enumerate(similarities):
                if similarity >= min_similarity:
                    headline = headlines[i].copy()
                    headline['similarity'] = float(similarity)
                    similar_headlines.append(headline)
            
            # Sort by similarity (highest first) and reliability
            similar_headlines.sort(key=lambda x: (x['similarity'], x['reliability']), reverse=True)
            
            return similar_headlines[:5]  # Return top 5 matches
            
        except Exception as e:
            logger.error(f"Failed to find similar headlines: {e}")
            return []
    
    def analyze_claim_novelty(self, claim: str) -> Dict:
        """Analyze if a claim is about recent/breaking news"""
        text_lower = claim.lower()
        
        # Temporal indicators
        recent_indicators = ['breaking', 'just', 'today', 'yesterday', 'this morning', 
                           'minutes ago', 'hours ago', 'latest', 'developing']
        
        breaking_score = sum(1 for indicator in recent_indicators if indicator in text_lower)
        
        # Date patterns
        date_patterns = [
            r'\b(today|yesterday)\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b',
            r'\b202[0-9]\b',  # Recent years
            r'\b\d{1,2}/\d{1,2}/202[0-9]\b'  # Date formats
        ]
        
        has_recent_date = any(re.search(pattern, text_lower) for pattern in date_patterns)
        
        return {
            'is_breaking_news': breaking_score > 0,
            'breaking_score': breaking_score,
            'has_recent_date': has_recent_date,
            'novelty_assessment': 'recent' if (breaking_score > 0 or has_recent_date) else 'standard'
        }
    
    async def comprehensive_fact_check(self, claim: str) -> Dict:
        """
        Comprehensive fact-checking with improved handling of new/unverified news
        """
        # Get trusted headlines
        headlines = await self.fetch_trusted_headlines()
        
        # Analyze claim novelty
        novelty = self.analyze_claim_novelty(claim)
        
        # Find similar headlines
        similar_headlines = self.find_similar_headlines(claim, headlines)
        
        if not similar_headlines:
            # No direct matches found
            if novelty['is_breaking_news']:
                return {
                    'status': 'UNVERIFIED_RECENT',
                    'confidence': 0.3,
                    'evidence': None,
                    'explanation': 'This appears to be recent/breaking news that may not yet be verified by trusted sources',
                    'recommendation': 'Monitor trusted news sources for verification',
                    'novelty': novelty
                }
            else:
                return {
                    'status': 'NOT_FOUND',
                    'confidence': 0.8,
                    'evidence': None,
                    'explanation': 'No similar reports found in trusted news sources',
                    'recommendation': 'Be cautious as this claim lacks mainstream news coverage',
                    'novelty': novelty
                }
        
        # Analyze the best match
        best_match = similar_headlines[0]
        
        # High similarity with reliable source
        if best_match['similarity'] > 0.85 and best_match['reliability'] > 0.85:
            return {
                'status': 'SUPPORTED',
                'confidence': min(best_match['similarity'] * best_match['reliability'], 0.95),
                'evidence': {
                    'matched_headline': best_match['text'],
                    'source_url': best_match['source_url'],
                    'similarity': best_match['similarity'],
                    'source_reliability': best_match['reliability']
                },
                'explanation': f'Similar report found in trusted source ({best_match["reliability"]:.1%} reliable)',
                'recommendation': 'This claim appears to be supported by trusted news reporting',
                'similar_headlines': similar_headlines[:3],
                'novelty': novelty
            }
        
        # Moderate similarity
        elif best_match['similarity'] > 0.7:
            return {
                'status': 'PARTIALLY_SUPPORTED',
                'confidence': 0.6,
                'evidence': {
                    'matched_headline': best_match['text'],
                    'source_url': best_match['source_url'],
                    'similarity': best_match['similarity'],
                    'source_reliability': best_match['reliability']
                },
                'explanation': 'Similar but not identical reports found in trusted sources',
                'recommendation': 'This claim has some support but may contain inaccuracies',
                'similar_headlines': similar_headlines[:3],
                'novelty': novelty
            }
        
        # Low similarity
        else:
            return {
                'status': 'CONFLICTING',
                'confidence': 0.4,
                'evidence': {
                    'matched_headline': best_match['text'],
                    'source_url': best_match['source_url'],
                    'similarity': best_match['similarity']
                },
                'explanation': 'Found related but different reports in trusted sources',
                'recommendation': 'This claim may be misleading or misrepresented',
                'similar_headlines': similar_headlines[:3],
                'novelty': novelty
            }
    
    def get_fact_check_assessment(self, fact_check_result: Dict) -> str:
        """Convert detailed fact-check result to simple assessment"""
        status = fact_check_result['status']
        
        if status == 'SUPPORTED':
            return 'Valid news'
        elif status in ['PARTIALLY_SUPPORTED', 'UNVERIFIED_RECENT']:
            return 'Potentially valid but unverified'
        elif status == 'CONFLICTING':
            return 'Conflicting information found'
        else:  # NOT_FOUND
            return 'No verification found'

# Forensic analysis functions (enhanced from your existing code)
def run_enhanced_forensic_checks(text: str) -> Dict:
    """Enhanced forensic analysis with more sophisticated checks"""
    words = text.split()
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    # Basic metrics
    num_words = len(words)
    num_chars = len(text)
    num_sentences = len(sentences)
    
    # Enhanced sensational keyword detection
    sensational_keywords = {
        'clickbait': ['shocking', 'unbelievable', 'amazing', 'incredible', 'mind-blowing', 
                     'you won\'t believe', 'what happened next', 'secret revealed'],
        'emotional': ['outrage', 'fury', 'scandal', 'bombshell', 'explosive', 'devastating'],
        'urgency': ['breaking', 'urgent', 'alert', 'emergency', 'crisis', 'immediate'],
        'superlatives': ['best', 'worst', 'never', 'always', 'everyone', 'nobody', 'all']
    }
    
    detected_keywords = {}
    text_lower = text.lower()
    
    for category, keywords in sensational_keywords.items():
        found = [kw for kw in keywords if kw in text_lower]
        detected_keywords[category] = found
    
    # Linguistic analysis
    uppercase_words = [w for w in words if len(w) > 3 and w.isupper()]
    exclamation_count = text.count('!')
    question_count = text.count('?')
    caps_ratio = sum(1 for c in text if c.isupper()) / max(num_chars, 1)
    
    # Structural analysis
    avg_sentence_length = num_words / max(num_sentences, 1)
    has_quotes = '"' in text or "'" in text
    
    # URL analysis
    urls = re.findall(r'https?://\S+', text)
    
    # Credibility indicators
    source_citations = len(re.findall(r'according to|sources say|reported by|as per', text_lower))
    specific_details = len(re.findall(r'\b\d{1,2}:\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b|\$\d+|\d+%', text))
    
    # Red flags calculation
    red_flags = []
    if exclamation_count > 3:
        red_flags.append("excessive_exclamations")
    if caps_ratio > 0.15:
        red_flags.append("excessive_capitals")
    if len(detected_keywords['clickbait']) > 0:
        red_flags.append("clickbait_language")
    if avg_sentence_length > 30:
        red_flags.append("overly_long_sentences")
    if source_citations == 0 and num_words > 50:
        red_flags.append("no_source_attribution")
    
    # Calculate credibility score
    credibility_score = 0.8  # Start with neutral
    
    # Deduct for red flags
    credibility_score -= len(red_flags) * 0.1
    
    # Add for positive indicators
    if source_citations > 0:
        credibility_score += 0.1
    if specific_details > 0:
        credibility_score += 0.1
    if has_quotes:
        credibility_score += 0.05
    
    credibility_score = max(0.0, min(1.0, credibility_score))
    
    return {
        'basic_metrics': {
            'character_count': num_chars,
            'word_count': num_words,
            'sentence_count': num_sentences,
            'avg_sentence_length': round(avg_sentence_length, 1)
        },
        'linguistic_analysis': {
            'uppercase_ratio': round(caps_ratio, 3),
            'exclamation_count': exclamation_count,
            'question_count': question_count,
            'uppercase_words': uppercase_words[:5],  # Limit for readability
            'has_quotes': has_quotes
        },
        'content_analysis': {
            'sensational_keywords': detected_keywords,
            'source_citations': source_citations,
            'specific_details': specific_details,
            'urls_found': len(urls)
        },
        'credibility_assessment': {
            'red_flags': red_flags,
            'credibility_score': round(credibility_score, 3),
            'assessment': 'high' if credibility_score > 0.7 else 'medium' if credibility_score > 0.4 else 'low'
        }
    }

# Global instance
fact_checker = EnhancedFactChecker()

# Utility functions
async def quick_fact_check(claim: str) -> Dict:
    """Quick fact-check function for external use"""
    return await fact_checker.comprehensive_fact_check(claim)

def forensic_analysis(text: str) -> Dict:
    """Quick forensic analysis function"""
    return run_enhanced_forensic_checks(text)

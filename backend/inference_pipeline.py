# backend/inference_pipeline.py
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path
from typing import Dict, Optional
import logging
from datetime import datetime

# Import our custom modules
from news_detector import news_detector
from fact_checker import fact_checker, run_enhanced_forensic_checks
from explanation_generator import explanation_generator

logger = logging.getLogger(__name__)

class FakeNewsInferencePipeline:
    """Complete inference pipeline for fake news detection with multi-layer analysis"""
    
    def __init__(self, model_dir: str = "model_out"):
        self.model_dir = Path(model_dir)
        self.ml_pipeline = None
        self.load_ml_model()
    
    def load_ml_model(self):
        """Load the trained ML model for fake news classification"""
        try:
            if self.model_dir.exists() and (self.model_dir / "pytorch_model.bin").exists():
                logger.info(f"Loading custom trained model from {self.model_dir}")
                self.ml_pipeline = pipeline(
                    "text-classification", 
                    model=str(self.model_dir),
                    return_all_scores=True
                )
            else:
                logger.info("No custom model found, using pre-trained model")
                self.ml_pipeline = pipeline(
                    "text-classification",
                    model="mrm8488/bert-tiny-finetuned-fake-news-detection",
                    return_all_scores=True
                )
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            # Fallback to a simple model
            try:
                self.ml_pipeline = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert"  # As a very basic fallback
                )
            except:
                self.ml_pipeline = None
    
    def run_ml_classification(self, text: str) -> Dict:
        """Run ML-based fake news classification"""
        if not self.ml_pipeline:
            return {
                'label': 'UNKNOWN',
                'confidence': 0.5,
                'reason': 'ML model not available'
            }
        
        try:
            # Limit text length for model input
            input_text = text[:512]
            
            # Get prediction
            results = self.ml_pipeline(input_text)
            
            # Handle different model output formats
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], list):
                    # Multiple scores returned
                    predictions = results[0]
                    # Find REAL/FAKE or similar labels
                    real_score = 0.5
                    fake_score = 0.5
                    
                    for pred in predictions:
                        label = pred['label'].upper()
                        score = pred['score']
                        
                        if label in ['REAL', 'LABEL_1', 'TRUE', 'LEGITIMATE']:
                            real_score = score
                        elif label in ['FAKE', 'LABEL_0', 'FALSE', 'TOXIC']:
                            fake_score = score
                    
                    if real_score > fake_score:
                        final_label = 'REAL'
                        confidence = real_score
                    else:
                        final_label = 'FAKE'
                        confidence = fake_score
                else:
                    # Single prediction
                    pred = results[0]
                    label = pred['label'].upper()
                    confidence = pred['score']
                    
                    # Map various label formats to REAL/FAKE
                    if label in ['REAL', 'LABEL_1', 'TRUE', 'LEGITIMATE']:
                        final_label = 'REAL'
                    elif label in ['FAKE', 'LABEL_0', 'FALSE', 'TOXIC']:
                        final_label = 'FAKE'
                    else:
                        # Unknown label format, use score to decide
                        final_label = 'REAL' if confidence > 0.5 else 'FAKE'
            else:
                final_label = 'UNKNOWN'
                confidence = 0.5
            
            return {
                'label': final_label,
                'confidence': round(float(confidence), 3),
                'reason': f'ML model prediction with {confidence:.1%} confidence'
            }
            
        except Exception as e:
            logger.error(f"ML classification failed: {e}")
            return {
                'label': 'UNKNOWN',
                'confidence': 0.5,
                'reason': f'ML classification error: {str(e)}'
            }
    
    def apply_hybrid_correction(self, 
                               ml_result: Dict, 
                               forensic_results: Dict, 
                               fact_check_result: Dict) -> Dict:
        """Apply hybrid correction logic to ML predictions"""
        
        original_label = ml_result['label']
        original_confidence = ml_result['confidence']
        
        # Count red flags from different sources
        red_flags = 0
        red_flag_details = []
        
        # Forensic red flags
        forensic_flags = forensic_results.get('credibility_assessment', {}).get('red_flags', [])
        red_flags += len(forensic_flags)
        if forensic_flags:
            red_flag_details.extend([f"forensic: {flag}" for flag in forensic_flags])
        
        # Fact-check red flags
        fact_status = fact_check_result.get('status', 'UNKNOWN')
        if fact_status in ['NOT_FOUND', 'CONFLICTING']:
            red_flags += 1
            red_flag_details.append(f"fact-check: {fact_status}")
        
        # Low credibility score
        credibility_score = forensic_results.get('credibility_assessment', {}).get('credibility_score', 0.8)
        if credibility_score < 0.5:
            red_flags += 1
            red_flag_details.append(f"low credibility score: {credibility_score:.2f}")
        
        # Apply correction logic
        if original_label == 'REAL' and red_flags >= 2:
            # Override REAL prediction if too many red flags
            return {
                'label': 'FAKE',
                'confidence': min(0.8, 0.5 + (red_flags * 0.1)),
                'reason': f'Originally classified as REAL, but overridden due to {red_flags} red flags: {", ".join(red_flag_details)}'
            }
        
        elif original_label == 'FAKE' and fact_status in ['SUPPORTED', 'PARTIALLY_SUPPORTED']:
            # Reduce confidence if fact-check supports the claim
            new_confidence = max(0.3, original_confidence - 0.3)
            return {
                'label': 'FAKE',
                'confidence': new_confidence,
                'reason': f'Classified as FAKE but fact-check shows some support. Confidence reduced.'
            }
        
        elif original_label == 'FAKE' and fact_status == 'UNVERIFIED_RECENT':
            # Special handling for recent/breaking news
            return {
                'label': 'UNVERIFIED',
                'confidence': 0.4,
                'reason': 'Classified as FAKE but may be recent news not yet verified by trusted sources'
            }
        
        else:
            # No correction needed
            return ml_result
    
    async def analyze_text(self, text: str, include_explanations: bool = True) -> Dict:
        """
        Complete multi-layer analysis pipeline
        
        Flow: News Detection -> Validity Check -> Real/Fake Classification -> Explanation
        """
        
        # Step 1: News Detection Layer
        news_detection = news_detector.detect_news(text)
        
        if not news_detection['is_news']:
            return {
                'input_summary': text[:300] + "..." if len(text) > 300 else text,
                'is_news': False,
                'validity_check': 'Not news',
                'message': news_detection['reason'],
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        # Step 2: Validity & Fact-Check Layer
        fact_check_result = await fact_checker.comprehensive_fact_check(text)
        
        # Step 3: Forensic Analysis
        forensic_results = run_enhanced_forensic_checks(text)
        
        # Step 4: ML Classification
        ml_result = self.run_ml_classification(text)
        
        # Step 5: Apply Hybrid Correction
        final_ml_result = self.apply_hybrid_correction(ml_result, forensic_results, fact_check_result)
        
        # Step 6: Determine Validity Assessment
        validity_assessment = self._determine_validity(final_ml_result, fact_check_result)
        
        # Step 7: Generate Explanations (if requested)
        explanations = {}
        if include_explanations:
            explanations = explanation_generator.generate_comprehensive_explanation(
                text, final_ml_result['label'], final_ml_result, fact_check_result, forensic_results
            )
        
        # Compile final result
        result = {
            'input_summary': text[:300] + "..." if len(text) > 300 else text,
            'is_news': True,
            'validity_check': validity_assessment,
            'fact_check': {
                'status': fact_check_result.get('status', 'UNKNOWN'),
                'confidence': fact_check_result.get('confidence', 0),
                'evidence': fact_check_result.get('evidence'),
                'explanation': fact_check_result.get('explanation', ''),
                'recommendation': fact_check_result.get('recommendation', '')
            },
            'ml_fake_news_check': {
                'label': final_ml_result['label'],
                'confidence': final_ml_result['confidence'],
                'reason': final_ml_result['reason']
            },
            'forensic_analysis': forensic_results,
            'news_detection': news_detection,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        if include_explanations:
            result['explanation'] = explanations
        
        return result
    
    def _determine_validity(self, ml_result: Dict, fact_check_result: Dict) -> str:
        """Determine overall validity assessment"""
        ml_label = ml_result['label']
        fact_status = fact_check_result.get('status', 'UNKNOWN')
        
        if ml_label == 'FAKE':
            if fact_status in ['SUPPORTED', 'PARTIALLY_SUPPORTED']:
                return 'Conflicting evidence - requires further verification'
            else:
                return 'Fake news'
        
        elif ml_label == 'REAL':
            if fact_status == 'SUPPORTED':
                return 'Valid news'
            elif fact_status in ['PARTIALLY_SUPPORTED', 'UNVERIFIED_RECENT']:
                return 'Likely valid but unverified'
            else:
                return 'Questionable validity'
        
        elif ml_label == 'UNVERIFIED':
            return 'Unverified - may be recent news'
        
        else:
            return 'Unknown validity'
    
    def quick_classify(self, text: str) -> str:
        """Quick classification without full analysis"""
        news_detection = news_detector.detect_news(text)
        if not news_detection['is_news']:
            return 'Not news'
        
        ml_result = self.run_ml_classification(text)
        return ml_result['label']

# Global inference pipeline instance
inference_pipeline = FakeNewsInferencePipeline()

# Utility functions for external use
async def analyze_news_text(text: str, include_explanations: bool = True) -> Dict:
    """Main function for analyzing news text"""
    return await inference_pipeline.analyze_text(text, include_explanations)

def quick_news_check(text: str) -> str:
    """Quick news validity check"""
    return inference_pipeline.quick_classify(text)

# Data collection function for continuous learning
def save_analysis_result(text: str, result: Dict, user_feedback: Optional[str] = None):
    """Save analysis results for continuous model improvement"""
    # Use backend/data directory to be consistent with existing data
    backend_dir = Path(__file__).parent  # Current directory is backend/
    data_file = backend_dir / "data" / "training_data.jsonl"
    data_file.parent.mkdir(exist_ok=True)
    
    record = {
        'timestamp': datetime.now().isoformat(),
        'text': text,
        'analysis_result': result,
        'user_feedback': user_feedback,
        'ml_prediction': result.get('ml_fake_news_check', {}).get('label'),
        'fact_check_status': result.get('fact_check', {}).get('status')
    }
    
    try:
        with open(data_file, 'a', encoding='utf-8') as f:
            import json
            f.write(json.dumps(record) + '\n')
    except Exception as e:
        logger.error(f"Failed to save analysis result: {e}")

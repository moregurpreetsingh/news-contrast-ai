#!/usr/bin/env python3
"""
Simple but working trainer for fake news detection
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, f1_score

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleNewsTrainer:
    """Simple trainer that actually creates working model files"""
    
    def __init__(self, data_dir="data", model_dir="model_out"):
        self.data_dir = Path(data_dir)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
        self.classifier = LogisticRegression(
            random_state=42,
            max_iter=1000,
            C=1.0
        )
        
    def load_training_data(self):
        """Load training data from JSONL file"""
        # Check backend/data first, then fall back to data_dir
        backend_training_file = Path(__file__).parent / "data" / "training_data.jsonl"
        if backend_training_file.exists():
            training_file = backend_training_file
        else:
            training_file = self.data_dir / "training_data.jsonl"
        
        if not training_file.exists():
            # Create sample training data
            sample_data = [
                {"text": "Scientists announce breakthrough discovery in medical research", "label": "REAL"},
                {"text": "Government announces new policy changes affecting citizens", "label": "REAL"},
                {"text": "Local news reports on community events and activities", "label": "REAL"},
                {"text": "Breaking news: Major economic developments reported by experts", "label": "REAL"},
                {"text": "Educational institution publishes research findings in peer-reviewed journal", "label": "REAL"},
                {"text": "SHOCKING: You won't believe what celebrities are doing now!", "label": "FAKE"},
                {"text": "Miracle cure discovered by doctors hate this simple trick", "label": "FAKE"},
                {"text": "Government hiding alien contact from secret moon base", "label": "FAKE"},
                {"text": "Click here to see what happens next in this unbelievable story", "label": "FAKE"},
                {"text": "Scientists shocked by this one weird discovery that changes everything", "label": "FAKE"},
                # Add more realistic examples
                {"text": "Climate change research shows concerning trends in global temperature data", "label": "REAL"},
                {"text": "Local hospital reports increased patient recovery rates with new treatment", "label": "REAL"},
                {"text": "City council approves budget for infrastructure improvements", "label": "REAL"},
                {"text": "University study reveals important findings about sleep patterns", "label": "REAL"},
                {"text": "Weather service issues warning for severe storm conditions", "label": "REAL"},
                {"text": "Ancient aliens built pyramids using advanced technology says expert", "label": "FAKE"},
                {"text": "Eating this fruit everyday will make you live to 200 years old", "label": "FAKE"},
                {"text": "Government secretly controlling weather using hidden satellites", "label": "FAKE"},
                {"text": "Doctors discover 5000-year-old secret to perfect health", "label": "FAKE"},
                {"text": "Magic pill melts away fat while you sleep - doctors amazed", "label": "FAKE"}
            ]
            
            logger.info("Creating sample training data...")
            with open(training_file, 'w', encoding='utf-8') as f:
                for item in sample_data:
                    f.write(json.dumps(item) + '\n')
        
        # Load data
        data = []
        try:
            with open(training_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line.strip())
                        data.append(item)
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return [], []
        
        # Extract texts and labels, handling different record formats
        texts = []
        labels = []
        
        for item in data:
            text = item.get('text', '')
            if not text:
                continue
                
            # Handle different label formats
            label = None
            if 'label' in item:
                # Simple format: {"text": "...", "label": "REAL"}
                label = str(item['label']).upper()
            elif 'analysis_result' in item:
                # Complex format from analysis results
                ml_result = item.get('analysis_result', {}).get('ml_fake_news_check', {})
                if ml_result:
                    label = str(ml_result.get('label', '')).upper()
            elif 'ml_prediction' in item:
                # Alternative format with direct ml_prediction
                label = str(item['ml_prediction']).upper()
            
            # Clean up label variations
            if label in ['FAKE (OVERRIDDEN)', 'FAKE (OVERRIDE)']:
                label = 'FAKE'
            
            # Only include valid entries
            if label in ['REAL', 'FAKE'] and text.strip():
                texts.append(text)
                labels.append(1 if label == 'REAL' else 0)
        
        logger.info(f"Loaded {len(data)} training samples")
        logger.info(f"Real news: {sum(labels)}, Fake news: {len(labels) - sum(labels)}")
        
        return texts, labels
    
    def train_model(self):
        """Train the model and save it"""
        logger.info("Starting model training...")
        
        # Load data
        texts, labels = self.load_training_data()
        
        if len(texts) == 0:
            raise ValueError("No training data available")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        
        # Vectorize text
        logger.info("Vectorizing text data...")
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train classifier
        logger.info("Training classifier...")
        self.classifier.fit(X_train_vec, y_train)
        
        # Evaluate
        train_pred = self.classifier.predict(X_train_vec)
        test_pred = self.classifier.predict(X_test_vec)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        test_f1 = f1_score(y_test, test_pred)
        
        logger.info(f"Training accuracy: {train_acc:.3f}")
        logger.info(f"Test accuracy: {test_acc:.3f}")
        logger.info(f"Test F1 score: {test_f1:.3f}")
        
        # Save model
        self.save_model(test_acc, test_f1, len(texts))
        
        return {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'test_f1': test_f1,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
    
    def save_model(self, accuracy, f1_score, total_samples):
        """Save the trained model and metadata"""
        logger.info(f"Saving model to {self.model_dir}")
        
        # Save vectorizer
        with open(self.model_dir / "vectorizer.pkl", 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # Save classifier
        with open(self.model_dir / "classifier.pkl", 'wb') as f:
            pickle.dump(self.classifier, f)
        
        # Save metadata
        metadata = {
            'model_name': 'simple_fake_news_detector',
            'model_type': 'sklearn_logistic_regression',
            'vectorizer_type': 'tfidf',
            'train_samples': total_samples,
            'final_metrics': {
                'eval_accuracy': accuracy,
                'eval_f1': f1_score
            },
            'trained_at': datetime.now().isoformat(),
            'features': {
                'max_features': 10000,
                'ngram_range': [1, 2],
                'stop_words': 'english'
            }
        }
        
        with open(self.model_dir / "training_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Model saved successfully!")
    
    def load_model(self):
        """Load the trained model"""
        try:
            with open(self.model_dir / "vectorizer.pkl", 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open(self.model_dir / "classifier.pkl", 'rb') as f:
                self.classifier = pickle.load(f)
            
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def predict(self, texts):
        """Make predictions on new texts"""
        if isinstance(texts, str):
            texts = [texts]
        
        # Vectorize
        X_vec = self.vectorizer.transform(texts)
        
        # Get predictions and probabilities
        predictions = self.classifier.predict(X_vec)
        probabilities = self.classifier.predict_proba(X_vec)
        
        results = []
        for i, text in enumerate(texts):
            pred_label = "REAL" if predictions[i] == 1 else "FAKE"
            confidence = max(probabilities[i])
            
            results.append({
                'text': text,
                'predicted_label': pred_label,
                'confidence': float(confidence),
                'fake_probability': float(probabilities[i][0]),
                'real_probability': float(probabilities[i][1])
            })
        
        return results[0] if len(texts) == 1 else results

def train_simple_model():
    """Main training function"""
    try:
        trainer = SimpleNewsTrainer()
        metrics = trainer.train_model()
        
        return {
            'status': 'success',
            'message': 'Model trained successfully',
            'training_metrics': metrics,
            'model_path': str(trainer.model_dir)
        }
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Training failed'
        }

def test_model():
    """Test the trained model"""
    trainer = SimpleNewsTrainer()
    
    if not trainer.load_model():
        print("No trained model found. Training new model...")
        train_simple_model()
        trainer.load_model()
    
    # Test cases
    test_cases = [
        "Scientists announce breakthrough in renewable energy research",
        "SHOCKING: This one weird trick will change your life forever!",
        "Local government approves new funding for public transportation",
        "Ancient aliens visited Earth according to this amazing discovery"
    ]
    
    print("\nTesting model predictions:")
    print("=" * 50)
    
    for text in test_cases:
        result = trainer.predict(text)
        print(f"Text: {text[:60]}...")
        print(f"Prediction: {result['predicted_label']} (confidence: {result['confidence']:.3f})")
        print("-" * 50)

if __name__ == "__main__":
    # Train model
    result = train_simple_model()
    print(json.dumps(result, indent=2))
    
    # Test model
    test_model()

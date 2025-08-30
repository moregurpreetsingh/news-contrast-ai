# backend/data_processor.py
import pandas as pd
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datasets import Dataset
import logging

logger = logging.getLogger(__name__)

class NewsDataProcessor:
    """Enhanced data processor for multiple fake news datasets"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.processed_data = []
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text data"""
        if not text or pd.isna(text):
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove URLs but keep the context
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                     '[URL]', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{3,}', '!!!', text)
        text = re.sub(r'[?]{3,}', '???', text)
        
        return text.strip()
    
    def is_valid_news_text(self, text: str) -> bool:
        """Check if text appears to be valid news content"""
        if not text or len(text.strip()) < 10:
            return False
            
        # Must have some structure
        words = text.split()
        if len(words) < 3:
            return False
            
        # Should contain some news-like indicators
        news_indicators = [
            'said', 'reported', 'according', 'news', 'breaking',
            'president', 'government', 'police', 'court', 'official'
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for indicator in news_indicators if indicator in text_lower)
        
        # At least one news indicator or proper sentence structure
        return indicator_count > 0 or (text.count('.') > 0 and len(words) > 5)
    
    def load_fakenewsnet_data(self) -> List[Dict]:
        """Load FakeNewsNet dataset (Politifact + GossipCop)"""
        datasets = []
        
        # Define dataset files
        dataset_files = [
            ("fakenewsnet/politifact_fake.csv", "FAKE"),
            ("fakenewsnet/politifact_real.csv", "REAL"),
            ("fakenewsnet/gossipcop_fake.csv", "FAKE"),
            ("fakenewsnet/gossipcop_real.csv", "REAL")
        ]
        
        for file_path, label in dataset_files:
            full_path = self.data_dir / file_path
            if full_path.exists():
                try:
                    df = pd.read_csv(full_path)
                    logger.info(f"Loading {len(df)} samples from {file_path}")
                    
                    for _, row in df.iterrows():
                        title = self.clean_text(str(row.get('title', '')))
                        if self.is_valid_news_text(title):
                            datasets.append({
                                'text': title,
                                'label': label,
                                'source': 'fakenewsnet',
                                'dataset': file_path.split('/')[1].replace('.csv', '')
                            })
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {e}")
                    
        return datasets
    
    def load_custom_jsonl_data(self, file_path: str = "training_data.jsonl") -> List[Dict]:
        """Load custom JSONL training data"""
        datasets = []
        # Check backend/data first, then fall back to data_dir
        backend_data_path = Path(__file__).parent / "data" / file_path
        if backend_data_path.exists():
            full_path = backend_data_path
        else:
            full_path = self.data_dir / file_path
        
        if not full_path.exists():
            logger.info(f"No custom training data found at {full_path}")
            return datasets
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        record = json.loads(line.strip())
                        text = self.clean_text(str(record.get('text', '')))
                        
                        # Handle different record formats
                        label = None
                        if 'label' in record:
                            # Simple format: {"text": "...", "label": "REAL"}
                            label = str(record.get('label', '')).upper()
                        elif 'analysis_result' in record:
                            # Complex format from analysis results
                            ml_result = record.get('analysis_result', {}).get('ml_fake_news_check', {})
                            if ml_result:
                                label = str(ml_result.get('label', '')).upper()
                        elif 'ml_prediction' in record:
                            # Alternative format with direct ml_prediction
                            label = str(record.get('ml_prediction', '')).upper()
                        
                        # Clean up label variations
                        if label in ['FAKE (OVERRIDDEN)', 'FAKE (OVERRIDE)']:
                            label = 'FAKE'
                        
                        if text and label in ['FAKE', 'REAL'] and self.is_valid_news_text(text):
                            datasets.append({
                                'text': text,
                                'label': label,
                                'source': 'custom',
                                'dataset': 'training_data'
                            })
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON at line {line_num} in {file_path}")
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to load custom data: {e}")
            
        return datasets
    
    def load_pheme_data(self) -> List[Dict]:
        """Load PHEME dataset if available"""
        datasets = []
        pheme_dir = self.data_dir / "pheme"
        
        if not pheme_dir.exists():
            return datasets
            
        # Look for converted annotations or raw data
        annotation_files = list(pheme_dir.glob("*annotations*.json"))
        
        for file_path in annotation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for item in data:
                    text = self.clean_text(str(item.get('text', '')))
                    # Map PHEME veracity labels to FAKE/REAL
                    veracity = item.get('veracity', '').lower()
                    if veracity in ['false', 'fake']:
                        label = 'FAKE'
                    elif veracity in ['true', 'real', 'verified']:
                        label = 'REAL'
                    else:
                        continue  # Skip unverified/unclear items
                        
                    if text and self.is_valid_news_text(text):
                        datasets.append({
                            'text': text,
                            'label': label,
                            'source': 'pheme',
                            'dataset': file_path.stem
                        })
                        
            except Exception as e:
                logger.warning(f"Failed to load PHEME data from {file_path}: {e}")
                
        return datasets
    
    def balance_dataset(self, datasets: List[Dict], max_per_class: Optional[int] = None) -> List[Dict]:
        """Balance the dataset to have equal FAKE/REAL samples"""
        fake_samples = [d for d in datasets if d['label'] == 'FAKE']
        real_samples = [d for d in datasets if d['label'] == 'REAL']
        
        logger.info(f"Before balancing: {len(fake_samples)} FAKE, {len(real_samples)} REAL")
        
        # Determine target size
        if max_per_class:
            target_size = min(max_per_class, len(fake_samples), len(real_samples))
        else:
            target_size = min(len(fake_samples), len(real_samples))
            
        if target_size < 10:
            logger.warning(f"Very small dataset size: {target_size} samples per class")
            
        # Sample equally from each class
        balanced_data = fake_samples[:target_size] + real_samples[:target_size]
        
        logger.info(f"After balancing: {target_size} samples per class, {len(balanced_data)} total")
        return balanced_data
    
    def create_training_dataset(self, min_samples: int = 20, max_per_class: Optional[int] = None) -> Dataset:
        """Create a unified training dataset from all available sources"""
        all_data = []
        
        # Load all available datasets
        all_data.extend(self.load_fakenewsnet_data())
        all_data.extend(self.load_custom_jsonl_data())
        all_data.extend(self.load_pheme_data())
        
        if len(all_data) < min_samples:
            raise ValueError(f"Insufficient training data: {len(all_data)} samples found, need at least {min_samples}")
        
        # Remove duplicates based on text similarity
        seen_texts = set()
        unique_data = []
        for item in all_data:
            text_key = item['text'][:100].lower().strip()  # Use first 100 chars as key
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_data.append(item)
                
        logger.info(f"Removed {len(all_data) - len(unique_data)} duplicate samples")
        
        # Balance the dataset
        balanced_data = self.balance_dataset(unique_data, max_per_class)
        
        # Convert to HuggingFace Dataset format
        texts = [item['text'] for item in balanced_data]
        labels = [1 if item['label'] == 'REAL' else 0 for item in balanced_data]  # 1=REAL, 0=FAKE
        
        return Dataset.from_dict({
            'text': texts,
            'label': labels,
            'source': [item['source'] for item in balanced_data]
        })
    
    def save_processed_dataset(self, dataset: Dataset, output_path: str = "processed_training_data.jsonl"):
        """Save processed dataset to JSONL format"""
        output_file = self.data_dir / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in dataset:
                record = {
                    'text': item['text'],
                    'label': 'REAL' if item['label'] == 1 else 'FAKE',
                    'source': item['source']
                }
                f.write(json.dumps(record) + '\n')
                
        logger.info(f"Saved processed dataset to {output_file}")
        return output_file

# Utility functions for external use
def get_training_data(data_dir: str = "data", min_samples: int = 20) -> Dataset:
    """Quick function to get training dataset"""
    processor = NewsDataProcessor(data_dir)
    return processor.create_training_dataset(min_samples)

def preprocess_datasets(data_dir: str = "data") -> str:
    """Preprocess all available datasets and save unified training data"""
    processor = NewsDataProcessor(data_dir)
    dataset = processor.create_training_dataset()
    output_file = processor.save_processed_dataset(dataset)
    return str(output_file)

# backend/enhanced_main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import httpx
from bs4 import BeautifulSoup
import logging
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

# Import our enhanced modules
from inference_pipeline import analyze_news_text, save_analysis_result, inference_pipeline
from simple_trainer import train_simple_model
from data_processor import preprocess_datasets

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced News Contrast AI", 
    version="1.0.0",
    description="Advanced fake news detection with multi-layer analysis pipeline"
) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", 
                   "https://news-contrast-ai.vercel.app/"
                  ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: HttpUrl | None = None
    text: str | None = None
    include_explanations: bool = True

class FeedbackRequest(BaseModel):
    text: str
    analysis_id: str
    user_feedback: str  # "correct", "incorrect", "partially_correct"
    comments: Optional[str] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Enhanced News Contrast AI API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Multi-layer news detection",
            "Advanced fact-checking",
            "ML-based classification",
            "Forensic analysis",
            "Explanation generation"
        ]
    }

@app.post("/analyze")
async def analyze_news(request: AnalyzeRequest):
    """
    Enhanced news analysis endpoint with complete pipeline
    
    Returns structured analysis following the specified JSON format
    """
    if not request.url and not request.text:
        raise HTTPException(status_code=400, detail="Provide either a URL or raw text")

    try:
        text_to_analyze = ""
        
        # Handle URL input
        if request.url:
            logger.info(f"Analyzing URL: {request.url}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.get(str(request.url))
                    response.raise_for_status()
                    
                    # Extract text content from HTML
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Try to extract main content
                    main_content = ""
                    
                    # Look for article content
                    article = soup.find('article')
                    if article:
                        main_content = article.get_text(strip=True)
                    else:
                        # Look for common content selectors
                        content_selectors = [
                            '.article-content', '.post-content', '.entry-content',
                            'main', '[role="main"]', '.content'
                        ]
                        
                        for selector in content_selectors:
                            element = soup.select_one(selector)
                            if element:
                                main_content = element.get_text(strip=True)
                                break
                    
                    # Fallback to title + first few paragraphs
                    if not main_content:
                        title = soup.find('title')
                        paragraphs = soup.find_all('p')[:5]  # First 5 paragraphs
                        
                        title_text = title.get_text(strip=True) if title else ""
                        paragraph_text = " ".join(p.get_text(strip=True) for p in paragraphs)
                        
                        main_content = f"{title_text}. {paragraph_text}".strip()
                    
                    text_to_analyze = main_content[:2000]  # Limit content length
                    
                except httpx.HTTPError as e:
                    raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")
        
        # Handle direct text input
        if request.text:
            text_to_analyze = request.text
        
        if not text_to_analyze.strip():
            raise HTTPException(status_code=400, detail="No valid text content found")
        
        # Run the enhanced analysis pipeline
        analysis_result = await analyze_news_text(
            text_to_analyze, 
            include_explanations=request.include_explanations
        )
        
        # Format response according to specified structure
        formatted_response = {
            "text_analysis": analysis_result
        }
        
        # If URL was provided, also add URL-specific analysis
        if request.url:
            formatted_response["url_analysis"] = {
                "source_url": str(request.url),
                "extracted_text_preview": text_to_analyze[:200] + "..." if len(text_to_analyze) > 200 else text_to_analyze,
                "content_length": len(text_to_analyze)
            }
        
        # Save for continuous learning
        try:
            save_analysis_result(text_to_analyze, analysis_result)
        except Exception as e:
            logger.warning(f"Failed to save analysis result: {e}")
        
        return formatted_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback for continuous model improvement"""
    try:
        # Save feedback for model improvement
        feedback_record = {
            'timestamp': datetime.now().isoformat(),
            'text': feedback.text,
            'analysis_id': feedback.analysis_id,
            'user_feedback': feedback.user_feedback,
            'comments': feedback.comments
        }
        
        feedback_file = Path("data/user_feedback.jsonl")
        feedback_file.parent.mkdir(exist_ok=True)
        
        with open(feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_record) + '\n')
        
        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": feedback.analysis_id
        }
        
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback")

@app.post("/retrain")
async def retrain_model():
    """Enhanced model retraining with better dataset handling"""
    try:
        logger.info("Starting enhanced model retraining...")
        
        # First, preprocess all available datasets
        processed_file = preprocess_datasets("data")
        logger.info(f"Preprocessed datasets saved to: {processed_file}")
        
        # Train the simple but working model
        training_result = train_simple_model()
        
        if training_result['status'] == 'success':
            return {
                "status": "success",
                "message": "Model trained successfully",
                "training_metrics": {
                    "eval_accuracy": training_result['training_metrics']['test_accuracy'],
                    "eval_f1": training_result['training_metrics']['test_f1']
                },
                "model_path": training_result.get('model_path', 'model_out')
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Training failed: {training_result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retraining failed: {e}")
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

@app.get("/model/status")
async def get_model_status():
    """Get current model status and training information"""
    try:
        model_dir = Path("model_out")
        metadata_file = model_dir / "training_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            return {
                "model_available": True,
                "model_info": metadata,
                "model_path": str(model_dir)
            }
        else:
            return {
                "model_available": model_dir.exists(),
                "model_info": None,
                "message": "Using default pre-trained model" if not model_dir.exists() else "Model available but no metadata"
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "model_available": False
        }

@app.get("/datasets/info")
async def get_dataset_info():
    """Get information about available datasets"""
    try:
        from data_processor import NewsDataProcessor
        
        processor = NewsDataProcessor("data")
        
        # Get counts from different sources
        fakenewsnet_data = processor.load_fakenewsnet_data()
        custom_data = processor.load_custom_jsonl_data()
        pheme_data = processor.load_pheme_data()
        
        return {
            "dataset_sources": {
                "fakenewsnet": {
                    "total_samples": len(fakenewsnet_data),
                    "fake_samples": len([d for d in fakenewsnet_data if d['label'] == 'FAKE']),
                    "real_samples": len([d for d in fakenewsnet_data if d['label'] == 'REAL'])
                },
                "custom_jsonl": {
                    "total_samples": len(custom_data),
                    "fake_samples": len([d for d in custom_data if d['label'] == 'FAKE']),
                    "real_samples": len([d for d in custom_data if d['label'] == 'REAL'])
                },
                "pheme": {
                    "total_samples": len(pheme_data),
                    "fake_samples": len([d for d in pheme_data if d['label'] == 'FAKE']),
                    "real_samples": len([d for d in pheme_data if d['label'] == 'REAL'])
                }
            },
            "total_available": len(fakenewsnet_data) + len(custom_data) + len(pheme_data)
        }
        
    except Exception as e:
        logger.error(f"Failed to get dataset info: {e}")
        return {"error": str(e)}

@app.get("/training-data/stats")
async def get_training_data_stats():
    """Get statistics from the training_data.jsonl file"""
    try:
        # Look for training data in backend/data first
        backend_data_path = Path(__file__).parent / "data" / "training_data.jsonl"
        data_path = backend_data_path if backend_data_path.exists() else Path("data/training_data.jsonl")
        
        if not data_path.exists():
            return {
                "status": "no_data",
                "message": "No training data found",
                "file_path": str(data_path),
                "total_entries": 0,
                "label_distribution": {"REAL": 0, "FAKE": 0},
                "recent_entries": []
            }
        
        # Read and analyze the data
        entries = []
        label_counts = {"REAL": 0, "FAKE": 0, "OTHER": 0}
        
        with open(data_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line.strip())
                    entries.append(record)
                    
                    # Extract label from different possible formats
                    label = None
                    if 'label' in record:
                        label = str(record['label']).upper()
                    elif 'analysis_result' in record:
                        # From analysis results
                        ml_result = record.get('analysis_result', {}).get('ml_fake_news_check', {})
                        if ml_result:
                            label = str(ml_result.get('label', '')).upper()
                    elif 'ml_prediction' in record:
                        label = str(record['ml_prediction']).upper()
                    
                    # Count labels
                    if label in ['REAL', 'TRUE', 'LEGITIMATE']:
                        label_counts["REAL"] += 1
                    elif label in ['FAKE', 'FALSE', 'FAKE (OVERRIDDEN)']:
                        label_counts["FAKE"] += 1
                    else:
                        label_counts["OTHER"] += 1
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON at line {line_num} in training data")
                    continue
                except Exception as e:
                    logger.warning(f"Error processing line {line_num}: {e}")
                    continue
        
        # Get recent entries (last 10)
        recent_entries = []
        for entry in entries[-10:]:
            recent_entry = {
                "timestamp": entry.get('timestamp', 'Unknown'),
                "text_preview": str(entry.get('text', ''))[:100] + "..." if len(str(entry.get('text', ''))) > 100 else str(entry.get('text', '')),
                "label": entry.get('label') or entry.get('ml_prediction', 'Unknown')
            }
            recent_entries.append(recent_entry)
        
        # Calculate file size
        file_size = data_path.stat().st_size
        
        return {
            "status": "success",
            "file_path": str(data_path),
            "file_size_bytes": file_size,
            "total_entries": len(entries),
            "label_distribution": {
                "REAL": label_counts["REAL"],
                "FAKE": label_counts["FAKE"],
                "OTHER": label_counts["OTHER"]
            },
            "recent_entries": recent_entries,
            "last_modified": datetime.fromtimestamp(data_path.stat().st_mtime).isoformat() if data_path.exists() else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get training data stats: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to analyze training data"
        }

@app.post("/test-pipeline")
async def test_pipeline():
    """Test the complete pipeline with sample data"""
    test_cases = [
        {
            "text": "Breaking: President announces new policy changes",
            "expected_type": "news"
        },
        {
            "text": "You won't believe what happened next in this shocking revelation!",
            "expected_type": "suspicious"
        },
        {
            "text": "Hello how are you doing today?",
            "expected_type": "not_news"
        },
        {
            "text": "Scientists report breakthrough in climate change research according to Nature journal",
            "expected_type": "news"
        }
    ]
    
    results = []
    
    for case in test_cases:
        try:
            result = await analyze_news_text(case["text"], include_explanations=False)
            results.append({
                "test_text": case["text"],
                "expected": case["expected_type"],
                "result": {
                    "is_news": result.get("is_news"),
                    "validity": result.get("validity_check"),
                    "ml_label": result.get("ml_fake_news_check", {}).get("label"),
                    "fact_status": result.get("fact_check", {}).get("status")
                }
            })
        except Exception as e:
            results.append({
                "test_text": case["text"],
                "expected": case["expected_type"],
                "error": str(e)
            })
    
    return {
        "test_results": results,
        "pipeline_status": "operational" if all("error" not in r for r in results) else "issues_detected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

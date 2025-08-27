# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx, re, json
from collections import Counter
from datetime import datetime
from pathlib import Path
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from bs4 import BeautifulSoup
from train import train_model
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="News Contrast AI", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path("data/training_data.jsonl")
MODEL_OUT = Path(__file__).parent / "model_out"
TRUSTED_SOURCES = [
    "https://www.bbc.com/news",
    "https://www.reuters.com",
    "https://www.apnews.com",
    "https://www.hindustantimes.com",
    "https://timesofindia.indiatimes.com",
    "https://www.cnn.com",
    "https://www.nytimes.com",
    "https://www.theguardian.com",
    "https://www.washingtonpost.com",
    "https://www.aljazeera.com",
    "https://www.economist.com",
    "https://www.npr.org",
    "https://www.ft.com",
    "https://www.wsj.com",
    "https://www.cbsnews.com",
    "https://www.nbcnews.com",
    "https://www.foxnews.com",
    "https://www.latimes.com",
    "https://www.chicagotribune.com",
]


class AnalyzeRequest(BaseModel):
    url: HttpUrl | None = None
    text: str | None = None


# ---------------- ML & Forensic ----------------
def run_forensic_checks(text: str) -> dict:
    words = text.split()
    num_words = len(words)
    num_chars = len(text)
    common_words = Counter(w.lower().strip(".,!?") for w in words).most_common(5)
    sensational_keywords = ["shocking", "breaking", "must see", "exclusive", "unbelievable", "scandal", "urgent"]
    sensational_found = [word for word in sensational_keywords if word in text.lower()]
    uppercase_ratio = sum(1 for c in text if c.isupper()) / max(num_chars, 1)
    punctuation_ratio = sum(1 for c in text if c in "!?.") / max(num_chars, 1)
    urls = re.findall(r"https?://\S+", text)
    questionable_patterns = {
        "clickbait": bool(re.search(r"(won't believe|what happened next|secret revealed)", text.lower())),
        "too_many_exclamations": text.count("!") > 3,
        "all_caps_words": [w for w in words if len(w) > 3 and w.isupper()]
    }
    return {
        "length_characters": num_chars,
        "length_words": num_words,
        "uppercase_ratio": round(uppercase_ratio, 3),
        "punctuation_ratio": round(punctuation_ratio, 3),
        "common_words": common_words,
        "sensational_keywords_found": sensational_found,
        "num_urls": len(urls),
        "urls_found": urls,
        "questionable_patterns": questionable_patterns,
    }


# ---------------- Model Loader ----------------
def load_model():
    """Load the local retrained model if exists, else fallback to pretrained public model"""
    if MODEL_OUT.exists() and (MODEL_OUT / "pytorch_model.bin").exists():
        return pipeline("text-classification", model=str(MODEL_OUT))
    else:
        print("[INFO] model_out missing, loading default public model")
        return pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-fake-news-detection")


fake_news_pipeline = load_model()


def ml_fake_news_check(text: str, forensic: dict, fact_check: dict) -> dict:
    try:
        result = fake_news_pipeline(text[:512])[0]
        label_map = {"LABEL_0": "FAKE", "LABEL_1": "REAL"}
        ml_label = label_map.get(result["label"], result["label"])
        ml_score = round(result["score"], 3)

        # --- Hybrid correction layer ---
        red_flags = 0
        if forensic["sensational_keywords_found"]:
            red_flags += 1
        if forensic["questionable_patterns"]["clickbait"]:
            red_flags += 1
        if forensic["questionable_patterns"]["too_many_exclamations"]:
            red_flags += 1
        if fact_check["status"] == "NOT FOUND":
            red_flags += 1

        if ml_label == "REAL" and red_flags >= 2:
            return {
                "label": "FAKE (overridden)",
                "score": ml_score,
                "reason": f"ML predicted REAL, but forensic + fact-check raised {red_flags} red flags"
            }

        return {"label": ml_label, "score": ml_score}

    except Exception as e:
        return {"error": str(e)}


# ---------------- Fact Check ----------------
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


async def fetch_trusted_headlines():
    headlines = []
    async with httpx.AsyncClient() as client:
        for url in TRUSTED_SOURCES:
            try:
                resp = await client.get(url)
                soup = BeautifulSoup(resp.text, "lxml")
                for h in soup.find_all(['h1','h2','h3']):
                    text = h.get_text(strip=True)
                    if text: headlines.append(text)
            except:
                continue
    return headlines


def compute_fact_check(claim: str, headlines: list):
    """
    Compare claim to headlines using sentence embeddings.
    Returns NOT FOUND if no headline is similar enough.
    """
    if not headlines:
        return {"status": "NOT FOUND", "evidence": None}

    claim_emb = embedding_model.encode(claim, convert_to_tensor=True)
    headlines_emb = embedding_model.encode(headlines, convert_to_tensor=True)
    cos_scores = util.pytorch_cos_sim(claim_emb, headlines_emb)[0]
    top_idx = cos_scores.argmax().item()

    if cos_scores[top_idx] < 0.7:  # threshold for relevance
        return {"status": "NOT FOUND", "evidence": None}

    return {
        "status": "SUPPORTED",
        "evidence": {
            "headline": headlines[top_idx],
            "similarity": float(cos_scores[top_idx])
        }
    }


# ---------------- API ----------------
@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    if not request.url and not request.text:
        raise HTTPException(status_code=400, detail="Provide either a URL or raw text")

    response = {}

    # ---------------- News detector ----------------
    def is_news(text: str) -> bool:
        """
        Heuristic to detect news:
        - Accepts either:
        1. Full news article (>= 8 words)
        2. Short headline (>= 4 words, max 20, usually contains ':' or '-')
        """
        words = text.split()
        num_words = len(words)

        # Full article heuristic
        if num_words >= 8:
            return True

        # Headline heuristic
        if 4 <= num_words <= 20 and (":" in text or "-" in text or any(w.istitle() for w in words)):
            return True

        return False
    # ---------------- URL analysis ----------------
    if request.url:
        async with httpx.AsyncClient() as client:
            resp = await client.get(str(request.url))
            resp.raise_for_status()
            url_content = resp.text[:5000]

        if not is_news(url_content):
            response["url_analysis"] = {
                "input_summary": url_content[:300] + "...",
                "is_news": False,
                "message": "Input does not appear to be news."
            }
        else:
            forensic_url = run_forensic_checks(url_content)
            headlines_url = await fetch_trusted_headlines()
            fact_check_url = compute_fact_check(url_content[:200], headlines_url)
            ml_results_url = ml_fake_news_check(url_content, forensic_url, fact_check_url)
            save_to_dataset(url_content, ml_results_url["label"])

            response["url_analysis"] = {
                "input_summary": url_content[:300] + "...",
                "is_news": True,
                "forensic_checks": forensic_url,
                "ml_fake_news_check": ml_results_url,
                "fact_check": fact_check_url
            }

    # ---------------- Text analysis ----------------
    if request.text:
        text_content = request.text

        if not is_news(text_content):
            response["text_analysis"] = {
                "input_summary": text_content[:300] + "...",
                "is_news": False,
                "message": "Input does not appear to be news."
            }
        else:
            forensic_text = run_forensic_checks(text_content)
            headlines_text = await fetch_trusted_headlines()
            fact_check_text = compute_fact_check(text_content[:200], headlines_text)
            ml_results_text = ml_fake_news_check(text_content, forensic_text, fact_check_text)
            save_to_dataset(text_content, ml_results_text["label"])

            response["text_analysis"] = {
                "input_summary": text_content[:300] + "...",
                "is_news": True,
                "forensic_checks": forensic_text,
                "ml_fake_news_check": ml_results_text,
                "fact_check": fact_check_text
            }

    return response

#----------- save data ------------------
def save_to_dataset(text: str, label: str):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "text": text,
        "label": label
    }
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

# ---------------- Retrain ----------------
@app.post("/retrain")
def retrain():
    try:
        result = train_model()  # retrain the model
        global fake_news_pipeline
        fake_news_pipeline = load_model()  # reload the updated model
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Retrain failed: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrain failed: {e}")

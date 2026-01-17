from celery import Celery
from transformers import pipeline
from database import SessionLocal, AnalysisResult
import os

# Connect Celery to Redis
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("worker", broker=redis_url, backend=redis_url)

# --- LOAD AI MODEL (Global Scope) ---
# We load this OUTSIDE the function so it loads only once when the worker starts.
print("Loading AI Model... (This might take a moment)")
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
print("AI Model Loaded!")

@celery_app.task(bind=True)
def analyze_sentiment_task(self, text_list, task_id_db):
    """
    This function runs in the background worker.
    """
    db = SessionLocal()
    # 1. Find the entry in Postgres and mark as PROCESSING
    record = db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id_db).first()
    if record:
        record.status = "PROCESSING"
        db.commit()

    try:
        # 2. Run the heavy AI computation
        results = sentiment_pipeline(text_list)
        
        # 3. Update DB with success
        if record:
            record.status = "COMPLETED"
            record.result = results
            db.commit()
            
    except Exception as e:
        # 4. Handle Failure
        if record:
            record.status = "FAILED"
            record.result = {"error": str(e)}
            db.commit()
    
    finally:
        db.close()
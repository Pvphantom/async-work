from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db, AnalysisResult
from tasks import analyze_sentiment_task
import uuid

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Input Schema
from pydantic import BaseModel
class SentimentRequest(BaseModel):
    texts: list[str]

@app.post("/analyze")
def start_analysis(request: SentimentRequest, db: Session = Depends(get_db)):
    # Generate a unique ID
    task_id = str(uuid.uuid4())
    
    # Create a "PENDING" record in Postgres
    new_record = AnalysisResult(task_id=task_id, status="PENDING")
    db.add(new_record)
    db.commit()
    
    # Send the job to Celery (Redis)
    analyze_sentiment_task.delay(request.texts, task_id)
    
    return {"task_id": task_id, "message": "Job submitted! Check status at /status/" + task_id}

@app.get("/status/{task_id}")
def get_status(task_id: str, db: Session = Depends(get_db)):
    record = db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        "status": record.status,
        "result": record.result
    }
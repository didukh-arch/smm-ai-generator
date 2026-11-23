from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import engine, Base, get_db
from models import ScenarioDB

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SMM AI Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScenarioCreate(BaseModel):
    topic: str
    tone: str

class ScenarioResponse(BaseModel):
    id: int
    topic: str
    tone: str
    content: str

    class Config:
        from_attributes = True

@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "ok", "database": "connected"}

@app.post("/api/v1/scenarios/generate", response_model=ScenarioResponse)
def generate_scenario(data: ScenarioCreate, db: Session = Depends(get_db)):
    if not data.topic.strip():
        raise HTTPException(status_code=400, detail="Тема не може бути порожньою!")
    
    generated_content = f"🎯 **Хук:** Увага! {data.topic}\n\n📝 **Текст:** Основна частина відео..."
    
    db_scenario = ScenarioDB(
        topic=data.topic,
        tone=data.tone,
        content=generated_content
    )
    
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    
    return db_scenario

@app.get("/api/v1/scenarios/history", response_model=List[ScenarioResponse])
def get_history(db: Session = Depends(get_db)):
    return db.query(ScenarioDB).order_by(ScenarioDB.created_at.desc()).all()
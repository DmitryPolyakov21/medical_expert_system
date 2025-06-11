from fastapi import FastAPI, Depends
from . import models, schemas, crud, geoip
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/v1/diagnosis", response_model=schemas.DiagnosisResponse)
async def receive_diagnosis(
    data: schemas.DiagnosisCreate, 
    db: Session = Depends(get_db)
):
    """Прием данных о диагнозе"""
    region = geoip.get_region_from_ip(data.patient_ip)
    return crud.create_diagnosis(db, data, region)

@app.get("/api/v1/stats/region/{region_name}")
async def get_region_stats(
    region_name: str,
    days: int = 30,
    limit: int = 7,
    db: Session = Depends(get_db)
):
    """Топ заболеваний по региону"""
    return crud.get_top_diseases(db, region_name, days, limit)

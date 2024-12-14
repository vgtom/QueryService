from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..database import get_db
from ..services.query_service import QueryService
from ..services.lineage_service import LineageService
from ..services.ai_service import AIService

router = APIRouter()
ai_service = AIService()  # Initialize without API key for now

@router.post("/queries/")
def store_query(user_id: str, query_text: str, db: Session = Depends(get_db)):
    query = QueryService.store_query(db, user_id, query_text)
    LineageService.store_lineage(db, query.id, query_text)
    return query

@router.get("/queries/")
def get_queries(
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    return QueryService.get_queries(db, user_id, start_date, end_date)

@router.get("/queries/{query_id}/lineage")
def get_query_lineage(query_id: int, db: Session = Depends(get_db)):
    query = db.query(Query).filter(Query.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return query.lineage_entries

@router.post("/queries/analyze")
def analyze_query(query_text: str):
    return ai_service.get_query_suggestions(query_text) 
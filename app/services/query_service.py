from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Query, QueryLineage
from ..cache import CacheService

class QueryService:
    def __init__(self):
        self.cache = CacheService()
    
    def store_query(self, db: Session, user_id: str, query_text: str) -> Query:
        query = Query(
            user_id=user_id,
            query_text=query_text
        )
        db.add(query)
        db.commit()
        db.refresh(query)
        
        # Invalidate user's queries cache
        self.cache.invalidate(f"user_queries:{user_id}")
        return query
    
    def get_queries(
        self,
        db: Session,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Query]:
        # Try to get from cache if only filtering by user_id
        if user_id and not (start_date or end_date):
            cache_key = f"user_queries:{user_id}"
            cached = self.cache.get(cache_key)
            if cached:
                return [Query(**q) for q in cached]
        
        query = db.query(Query)
        
        if user_id:
            query = query.filter(Query.user_id == user_id)
        if start_date:
            query = query.filter(Query.created_at >= start_date)
        if end_date:
            query = query.filter(Query.created_at <= end_date)
            
        results = query.all()
        
        # Cache results if only filtered by user_id
        if user_id and not (start_date or end_date):
            self.cache.set(f"user_queries:{user_id}", [q.__dict__ for q in results])
            
        return results 
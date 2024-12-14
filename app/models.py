from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Query(Base):
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    query_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lineage_entries = relationship("QueryLineage", back_populates="query")

class QueryLineage(Base):
    __tablename__ = "query_lineage"
    
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey("queries.id"))
    table_name = Column(String, nullable=False)
    column_name = Column(String, nullable=True)
    
    # Relationships
    query = relationship("Query", back_populates="lineage_entries") 
import sqlglot
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from ..models import Query, QueryLineage

class LineageService:
    @staticmethod
    def extract_lineage(query_text: str) -> List[Tuple[str, Optional[str]]]:
        """
        Enhanced lineage extraction using sqlglot parser.
        Returns list of (table_name, column_name) tuples.
        """
        try:
            # Parse the SQL query
            parsed = sqlglot.parse_one(query_text)
            tables = set()
            columns = set()
            
            # Extract tables
            for table in parsed.find_all(sqlglot.exp.Table):
                tables.add((table.name, None))
            
            # Extract columns with their tables
            for col in parsed.find_all(sqlglot.exp.Column):
                if col.table:
                    columns.add((col.table.name, col.name))
                else:
                    columns.add((None, col.name))
                    
            return list(tables.union(columns))
        except Exception as e:
            # Log the error and fall back to basic parsing
            logger.error(f"SQL parsing error: {str(e)}")
            return LineageService._basic_parse_fallback(query_text)
    
    @staticmethod
    def _basic_parse_fallback(query_text: str) -> List[Tuple[str, Optional[str]]]:
        """Fallback to basic parsing if sqlglot fails"""
        # Previous basic parsing implementation here
    
    @staticmethod
    def store_lineage(db: Session, query_id: int, query_text: str):
        lineage_entries = LineageService.extract_lineage(query_text)
        
        for table_name, column_name in lineage_entries:
            entry = QueryLineage(
                query_id=query_id,
                table_name=table_name or "unknown",
                column_name=column_name
            )
            db.add(entry)
        
        db.commit() 
from typing import Dict
import openai
from datetime import datetime

class AIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key
    
    def get_query_suggestions(self, query_text: str) -> Dict:
        if not self.api_key:
            # Mock response for development
            return {
                "suggestions": [
                    "Consider adding an index on frequently filtered columns",
                    "Use explicit column names instead of SELECT *",
                    "Add appropriate WHERE clauses to limit data retrieval"
                ],
                "optimized_query": query_text,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        # Real OpenAI integration would go here
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a SQL optimization expert."},
                {"role": "user", "content": f"Please suggest improvements for this SQL query: {query_text}"}
            ]
        )
        
        return {
            "suggestions": [response.choices[0].message.content],
            "optimized_query": query_text,  # We could parse the response to get an optimized version
            "generated_at": datetime.utcnow().isoformat()
        } 
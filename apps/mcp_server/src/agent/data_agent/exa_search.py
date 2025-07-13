"""
Exa search integration for quantified self analysis enhancement
"""

import os
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import weave

load_dotenv()


class ExaSearcher:
    """Handles web searches using Exa API for research and context enhancement"""

    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.exa.ai",
            api_key=os.getenv("EXA_API_KEY"),
        )

    @weave.op()
    def search_health_insights(self, query: str, context: Optional[str] = None) -> str:
        """
        Search for health and fitness insights related to quantified self data
        
        Args:
            query: Search query (e.g., "protein intake recommendations", "sleep quality factors")
            context: Optional context about user's data to make search more relevant
            
        Returns:
            Relevant insights and recommendations from web search
        """
        # Build enhanced query with context if provided
        enhanced_query = query
        if context:
            enhanced_query = f"Given this context: {context}, find insights about: {query}"
        
        try:
            completion = self.client.chat.completions.create(
                model="exa-pro",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a health and fitness research assistant. Provide evidence-based insights, recommendations, and scientific context for quantified self data analysis. Focus on actionable advice and cite sources when possible."
                    },
                    {
                        "role": "user", 
                        "content": enhanced_query
                    }
                ],
                stream=False
            )
            
            if completion.choices and completion.choices[0].message:
                return completion.choices[0].message.content
            else:
                return f"No search results found for: {query}"
                
        except Exception as e:
            return f"Search error: {str(e)}"

    def get_workout_insights(self, exercises: list, weights: list, user_context: str = "") -> str:
        """Get specific insights about workout performance and recommendations"""
        exercise_summary = ", ".join(exercises)
        weight_summary = ", ".join([f"{w} lbs" for w in weights])
        
        query = f"Analysis and recommendations for these exercises: {exercise_summary} with weights: {weight_summary}"
        if user_context:
            query += f". User context: {user_context}"
            
        return self.search_health_insights(query)

    def get_nutrition_insights(self, foods: list, nutrients: Dict[str, float], user_context: str = "") -> str:
        """Get specific insights about nutrition and dietary recommendations"""
        food_summary = ", ".join(foods)
        nutrient_summary = ", ".join([f"{k}: {v}g" for k, v in nutrients.items()])
        
        query = f"Nutritional analysis and recommendations for foods: {food_summary} with nutrients: {nutrient_summary}"
        if user_context:
            query += f". User context: {user_context}"
            
        return self.search_health_insights(query)

    def get_sleep_insights(self, duration: float, quality: int, user_context: str = "") -> str:
        """Get specific insights about sleep patterns and recommendations"""
        query = f"Sleep analysis for {duration} hours of sleep with quality rating {quality}/10"
        if user_context:
            query += f". User context: {user_context}"
            
        return self.search_health_insights(query)

    def get_general_health_insights(self, data_summary: str) -> str:
        """Get general health insights based on overall quantified self data"""
        query = f"Comprehensive health analysis and recommendations based on this quantified self data: {data_summary}"
        return self.search_health_insights(query)
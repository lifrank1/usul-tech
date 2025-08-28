#!/usr/bin/env python3
"""
SOF Week Speaker Recommendation Engine - Main Server

A FastAPI-based web service that provides speaker recommendations
using vector embeddings and similarity search.
"""

import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from speaker_recommendation_engine import SpeakerRecommendationEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SOF Week Speaker Recommendation API",
    description="AI-powered speaker recommendation engine for SOF Week 2025",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class RecommendationRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class SpeakerResponse(BaseModel):
    name: str
    title: str
    company: str
    relevance_score: float
    explanation: str
    contact_info: Dict[str, str]
    session_details: Dict[str, str]
    image_url: Optional[str] = None

class RecommendationResponse(BaseModel):
    query: str
    recommendations: List[SpeakerResponse]
    total_found: int
    processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    message: str
    total_speakers: int
    version: str

# Global recommendation engine instance
recommendation_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize the recommendation engine on startup."""
    global recommendation_engine
    
    try:
        # Get data file path (relative to backend folder)
        data_file = os.path.join(os.path.dirname(__file__), "..", "data", "sof_week_speakers_complete.json")
        
        logger.info(f"Initializing recommendation engine with data: {data_file}")
        recommendation_engine = SpeakerRecommendationEngine(data_file)
        logger.info("Recommendation engine initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize recommendation engine: {e}")
        raise

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    if recommendation_engine is None:
        raise HTTPException(status_code=503, detail="Recommendation engine not available")
    
    return HealthResponse(
        status="healthy",
        message="SOF Week Speaker Recommendation API is running",
        total_speakers=len(recommendation_engine.get_all_speakers()),
        version="1.0.0"
    )

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_speakers(request: RecommendationRequest):
    """
    Get speaker recommendations based on a natural language query.
    
    Example queries:
    - "I'm a drone contractor, find me contacts that have experience in that field"
    - "Looking for experts in cybersecurity and information systems"
    - "Need contacts in acquisition and procurement"
    """
    if recommendation_engine is None:
        raise HTTPException(status_code=503, detail="Recommendation engine not available")
    
    try:
        import time
        start_time = time.time()
        
        # Get recommendations
        recommendations = recommendation_engine.recommend_speakers(
            query=request.query,
            top_k=request.top_k
        )
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Convert to response format
        speaker_responses = []
        for rec in recommendations:
            speaker_data = rec['speaker']
            speaker_responses.append(SpeakerResponse(
                name=speaker_data.get('name', ''),
                title=speaker_data.get('title', ''),
                company=speaker_data.get('company', ''),
                relevance_score=rec['relevance_score'],
                explanation=rec['explanation'],
                contact_info=rec['contact_info'],
                session_details=rec['session_details'],
                image_url=speaker_data.get('image_url')
            ))
        
        return RecommendationResponse(
            query=request.query,
            recommendations=speaker_responses,
            total_found=len(speaker_responses),
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/speakers", response_model=List[Dict[str, Any]])
async def get_all_speakers():
    """Get all speakers in the database."""
    if recommendation_engine is None:
        raise HTTPException(status_code=503, detail="Recommendation engine not available")
    
    try:
        return recommendation_engine.get_all_speakers()
    except Exception as e:
        logger.error(f"Error retrieving speakers: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving speakers: {str(e)}")

@app.get("/speakers/search")
async def search_speakers_by_keyword(keyword: str):
    """Search speakers by keyword."""
    if recommendation_engine is None:
        raise HTTPException(status_code=503, detail="Recommendation engine not available")
    
    try:
        results = recommendation_engine.search_speakers_by_keyword(keyword)
        return {
            "keyword": keyword,
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching speakers: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching speakers: {str(e)}")

@app.get("/speakers/{speaker_name}")
async def get_speaker_by_name(speaker_name: str):
    """Get a specific speaker by name."""
    if recommendation_engine is None:
        raise HTTPException(status_code=503, detail="Recommendation engine not available")
    
    try:
        speaker = recommendation_engine.get_speaker_by_name(speaker_name)
        if speaker is None:
            raise HTTPException(status_code=404, detail=f"Speaker '{speaker_name}' not found")
        return speaker
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving speaker: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving speaker: {str(e)}")

@app.get("/stats")
async def get_database_stats():
    """Get database statistics."""
    if recommendation_engine is None:
        raise HTTPException(status_code=503, detail="Recommendation engine not available")
    
    try:
        speakers = recommendation_engine.get_all_speakers()
        
        # Calculate some basic stats
        total_speakers = len(speakers)
        speakers_with_bios = sum(1 for s in speakers if s.get('detailed_bio') and s['detailed_bio'].strip())
        companies = set(s.get('company', '') for s in speakers if s.get('company'))
        
        return {
            "total_speakers": total_speakers,
            "speakers_with_detailed_bios": speakers_with_bios,
            "unique_companies": len(companies),
            "companies": list(companies),
            "data_source": "SOF Week 2025",
            "last_updated": "2025-08-27",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "backend.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )

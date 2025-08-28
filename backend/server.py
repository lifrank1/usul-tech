from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from speaker_recommendation_engine import SpeakerRecommendationEngine
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    query: str
    top_k: int = 5

class SpeakerResponse(BaseModel):
    name: str
    title: str
    company: str
    relevance_score: float
    explanation: str
    contact_info: dict
    session_details: dict
    image_url: str = None

class RecommendationResponse(BaseModel):
    query: str
    recommendations: list[SpeakerResponse]
    total_found: int

engine = None

@app.on_event("startup")
async def startup():
    global engine
    data_file = os.path.join(os.path.dirname(__file__), "..", "data", "sof_week_speakers_complete.json")
    engine = SpeakerRecommendationEngine(data_file)

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    recommendations = engine.recommend_speakers(request.query, request.top_k)
    
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
        total_found=len(speaker_responses)
    )

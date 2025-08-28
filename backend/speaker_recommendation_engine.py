import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeakerRecommendationEngine:
    """
    A recommendation engine for SOF Week speakers using vector embeddings and similarity search.
    Built with free/open-source tools: Sentence Transformers + ChromaDB
    """
    
    def __init__(self, json_file_path: str):
        """
        Initialize the recommendation engine.
        
        Args:
            json_file_path: Path to the JSON file containing speaker data
        """
        self.json_file_path = json_file_path
        self.speakers_data = None
        self.embedding_model = None
        self.vector_db = None
        self.speaker_documents = []
        self.speaker_metadata = []
        
        # Initialize components
        self._load_data()
        self._initialize_embedding_model()
        self._initialize_vector_database()
        self._create_speaker_documents()
        self._index_speakers()
        
    def _load_data(self):
        """Load speaker data from JSON file."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.speakers_data = json.load(f)
            logger.info(f"Loaded {len(self.speakers_data['speakers'])} speakers from {self.json_file_path}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def _initialize_embedding_model(self):
        """Initialize the Sentence Transformers embedding model."""
        try:
            # Use a lightweight, fast model that's free and open source
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Initialized embedding model: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            raise
    
    def _initialize_vector_database(self):
        """Initialize ChromaDB for vector storage."""
        try:
            # Use in-memory ChromaDB for simplicity in prototype
            self.vector_db = chromadb.Client()
            
            # Create collection for speakers
            self.speaker_collection = self.vector_db.create_collection(
                name="sof_week_speakers",
                metadata={"description": "SOF Week 2025 Speaker Database"}
            )
            logger.info("Initialized ChromaDB vector database")
        except Exception as e:
            logger.error(f"Error initializing vector database: {e}")
            raise
    
    def _create_speaker_documents(self):
        """Create coherent text documents for each speaker suitable for embedding."""
        self.speaker_documents = []
        self.speaker_metadata = []
        
        for i, speaker in enumerate(self.speakers_data['speakers']):
            # Construct a comprehensive document for each speaker
            document_parts = []
            
            # Basic information
            if speaker.get('name'):
                document_parts.append(f"Name: {speaker['name']}")
            if speaker.get('title'):
                document_parts.append(f"Title: {speaker['title']}")
            if speaker.get('company'):
                document_parts.append(f"Company: {speaker['company']}")
            
            # Session information
            if speaker.get('session_title'):
                document_parts.append(f"Session: {speaker['session_title']}")
            if speaker.get('session_description'):
                document_parts.append(f"Session Description: {speaker['session_description']}")
            if speaker.get('location'):
                document_parts.append(f"Location: {speaker['location']}")
            if speaker.get('speaking_time'):
                document_parts.append(f"Speaking Time: {speaker['speaking_time']}")
            
            # Bio information
            if speaker.get('detailed_bio') and speaker['detailed_bio'].strip():
                document_parts.append(f"Bio: {speaker['detailed_bio']}")
            
            # Join all parts with semantic separators
            document_text = " | ".join(document_parts)
            
            # Store document and metadata
            self.speaker_documents.append(document_text)
            self.speaker_metadata.append({
                'speaker_index': str(i),
                'has_detailed_bio': str(bool(speaker.get('detailed_bio') and speaker['detailed_bio'].strip())),
                'speaker_name': speaker.get('name', ''),
                'speaker_title': speaker.get('title', ''),
                'speaker_company': speaker.get('company', '')
            })
        
        logger.info(f"Created {len(self.speaker_documents)} speaker documents")
    
    def _index_speakers(self):
        """Index all speaker documents in the vector database."""
        try:
            # Generate embeddings for all speaker documents
            embeddings = self.embedding_model.encode(self.speaker_documents)
            
            # Add documents to ChromaDB
            self.speaker_collection.add(
                embeddings=embeddings.tolist(),
                documents=self.speaker_documents,
                metadatas=self.speaker_metadata,
                ids=[f"speaker_{i}" for i in range(len(self.speaker_documents))]
            )
            
            logger.info(f"Indexed {len(self.speaker_documents)} speakers in vector database")
        except Exception as e:
            logger.error(f"Error indexing speakers: {e}")
            raise
    
    def recommend_speakers(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recommend speakers based on a natural language query.
        
        Args:
            query: Natural language query (e.g., "I'm a drone contractor, find me contacts that have experience in that field")
            top_k: Number of top recommendations to return
            
        Returns:
            List of recommended speakers with relevance scores and explanations
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode([query])
            
            # Search for similar speakers
            results = self.speaker_collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process and format results
            recommendations = []
            for i in range(len(results['ids'][0])):
                speaker_idx = int(results['metadatas'][0][i]['speaker_index'])
                speaker_data = self.speakers_data['speakers'][speaker_idx]
                distance = results['distances'][0][i]
                document = results['documents'][0][i]
                
                # Convert distance to similarity score (0-1, higher is better)
                # ChromaDB returns distances, so we need to handle them properly
                if distance < 0:
                    # If distance is negative, it's likely a similarity score already
                    similarity_score = abs(distance)
                else:
                    # Convert distance to similarity (assuming max distance is around 2.0)
                    similarity_score = max(0, 1 - (distance / 2.0))
                
                # Calculate relevance explanation
                explanation = self._generate_relevance_explanation(query, speaker_data, similarity_score)
                
                recommendation = {
                    'speaker': speaker_data,
                    'relevance_score': round(similarity_score, 3),
                    'explanation': explanation,
                    'contact_info': self._extract_contact_info(speaker_data),
                    'session_details': {
                        'title': speaker_data.get('session_title', ''),
                        'time': speaker_data.get('speaking_time', ''),
                        'location': speaker_data.get('location', ''),
                        'description': speaker_data.get('session_description', '')
                    }
                }
                
                recommendations.append(recommendation)
            
            # Sort by relevance score (highest first)
            recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"Generated {len(recommendations)} recommendations for query: '{query}'")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    def _generate_relevance_explanation(self, query: str, speaker_data: Dict, similarity_score: float) -> str:
        """Generate a human-readable explanation of why a speaker is relevant."""
        query_lower = query.lower()
        speaker_text = f"{speaker_data.get('name', '')} {speaker_data.get('title', '')} {speaker_data.get('company', '')} {speaker_data.get('session_title', '')} {speaker_data.get('detailed_bio', '')}".lower()
        
        # Identify key matching areas
        matches = []
        
        if speaker_data.get('name') and any(word in speaker_data['name'].lower() for word in query_lower.split()):
            matches.append("name")
        
        if speaker_data.get('title') and any(word in speaker_data['title'].lower() for word in query_lower.split()):
            matches.append("professional title")
        
        if speaker_data.get('company') and any(word in speaker_data['company'].lower() for word in query_lower.split()):
            matches.append("company")
        
        if speaker_data.get('session_title') and any(word in speaker_data['session_title'].lower() for word in query_lower.split()):
            matches.append("session topic")
        
        if speaker_data.get('detailed_bio') and any(word in speaker_data['detailed_bio'].lower() for word in query_lower.split()):
            matches.append("professional background")
        
        # Generate explanation
        if matches:
            match_text = ", ".join(matches)
            if similarity_score > 0.7:
                strength = "highly relevant"
            elif similarity_score > 0.5:
                strength = "relevant"
            else:
                strength = "somewhat relevant"
            
            return f"This speaker is {strength} based on matches in: {match_text}. The semantic similarity score is {similarity_score:.1%}."
        else:
            return f"This speaker shows semantic relevance (score: {similarity_score:.1%}) based on the overall context and professional background."
    
    def _extract_contact_info(self, speaker_data: Dict) -> Dict[str, str]:
        """Extract contact information from speaker data."""
        contact_info = {}
        
        # Extract email if present in bio
        bio = speaker_data.get('detailed_bio', '')
        if '@' in bio:
            # Simple email extraction (could be enhanced with regex)
            words = bio.split()
            for word in words:
                if '@' in word and '.' in word:
                    contact_info['email'] = word.strip('.,!?')
                    break
        
        # Company contact
        if speaker_data.get('company'):
            contact_info['company'] = speaker_data['company']
        
        # Session location/time for in-person contact
        if speaker_data.get('location') and speaker_data.get('speaking_time'):
            contact_info['session_contact'] = f"{speaker_data['speaking_time']} at {speaker_data['location']}"
        
        return contact_info
    
    def get_speaker_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific speaker by name."""
        for speaker in self.speakers_data['speakers']:
            if speaker['name'].lower() == name.lower():
                return speaker
        return None
    
    def get_all_speakers(self) -> List[Dict[str, Any]]:
        """Get all speakers in the database."""
        return self.speakers_data['speakers']
    
    def search_speakers_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Search speakers by keyword in their data."""
        keyword_lower = keyword.lower()
        matches = []
        
        for speaker in self.speakers_data['speakers']:
            speaker_text = f"{speaker.get('name', '')} {speaker.get('title', '')} {speaker.get('company', '')} {speaker.get('session_title', '')} {speaker.get('detailed_bio', '')}".lower()
            
            if keyword_lower in speaker_text:
                matches.append(speaker)
        
        return matches

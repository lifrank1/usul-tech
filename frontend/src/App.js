import React, { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const getRecommendations = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          top_k: 5
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get recommendations');
      }
      
      const data = await response.json();
      setRecommendations(data.recommendations);
    } catch (err) {
      setError('Failed to get recommendations. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    getRecommendations();
  };

  return (
    <div className="App">
      <div className="container">
        <h1>SOF Week Speaker Recommendations</h1>
        
        <form onSubmit={handleSubmit} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., I'm a drone contractor, find me contacts that have experience in that field"
            className="search-input"
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={loading || !query.trim()}
          >
            {loading ? 'Searching...' : 'Find Speakers'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {recommendations.length > 0 && (
          <div className="results">
            <h2>Found {recommendations.length} relevant speakers:</h2>
            {recommendations.map((speaker, index) => (
              <div key={index} className="speaker-card">
                <div className="speaker-header">
                  <h3>{speaker.name}</h3>
                  <span className="score">{Math.round(speaker.relevance_score * 100)}%</span>
                </div>
                <p className="title">{speaker.title}</p>
                <p className="company">{speaker.company}</p>
                <p className="explanation">{speaker.explanation}</p>
                <div className="session-info">
                  <p><strong>Session:</strong> {speaker.session_details.title}</p>
                  <p><strong>Time:</strong> {speaker.session_details.time}</p>
                  <p><strong>Location:</strong> {speaker.session_details.location}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

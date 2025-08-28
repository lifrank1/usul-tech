# SOF Week Speaker Recommendation Engine - Backend

This is the backend server for the SOF Week Speaker Recommendation Engine. It provides a REST API that uses vector embeddings and similarity search to recommend relevant speakers based on natural language queries.

## 🏗️ Architecture

```
backend/
├── __init__.py                    # Package initialization
├── server.py                      # Main FastAPI server
├── speaker_recommendation_engine.py # Core recommendation engine
├── run.py                         # Simple server runner
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# Option 1: Using the run script
python run.py

# Option 2: Using the server module directly
python -m server

# Option 3: Using uvicorn directly
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/
- **Base URL**: http://localhost:8000

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check and server status |
| `POST` | `/recommend` | Get speaker recommendations |
| `GET` | `/speakers` | List all speakers |
| `GET` | `/speakers/search` | Search speakers by keyword |
| `GET` | `/speakers/{name}` | Get specific speaker by name |
| `GET` | `/stats` | Database statistics |

### Example Usage

#### Get Recommendations

```bash
curl -X POST "http://localhost:8000/recommend" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "I need contacts in drone technology",
       "top_k": 5
     }'
```

#### Search by Keyword

```bash
curl "http://localhost:8000/speakers/search?keyword=cybersecurity"
```

#### Get All Speakers

```bash
curl "http://localhost:8000/speakers"
```

## 🔧 Configuration

### Environment Variables

The server can be configured using environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: info)
- `RELOAD`: Enable auto-reload (default: true)

### Data Source

The server expects the speaker data file at:
```
../data/sof_week_speakers_complete.json
```

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "healthy",
  "message": "SOF Week Speaker Recommendation API is running",
  "total_speakers": 44,
  "version": "1.0.0"
}
```

### Test Recommendation

```bash
curl -X POST "http://localhost:8000/recommend" \
     -H "Content-Type: application/json" \
     -d '{"query": "test query", "top_k": 1}'
```

## 📊 Performance

- **Startup Time**: ~2-5 seconds (includes model loading)
- **Query Response**: <100ms for typical queries
- **Memory Usage**: ~200-500MB
- **Concurrent Requests**: Designed for single-user prototype

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find and kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Import Errors**
   ```bash
   # Make sure you're in the backend directory
   cd backend
   python -m server
   ```

3. **Data File Not Found**
   - Ensure `../data/sof_week_speakers_complete.json` exists
   - Check file permissions

### Debug Mode

Enable detailed logging by setting the log level:

```bash
LOG_LEVEL=debug python run.py
```

## 🔄 Development

### Auto-reload

The server runs with auto-reload enabled by default. Any changes to Python files will automatically restart the server.

### Adding New Endpoints

1. Add the endpoint to `server.py`
2. Define Pydantic models if needed
3. Test with the interactive docs at `/docs`

### Modifying the Recommendation Engine

The core logic is in `speaker_recommendation_engine.py`. Changes here will be reflected in the API responses.

## 📝 Logs

The server provides structured logging with timestamps. Logs include:
- Server startup and initialization
- API request/response details
- Recommendation engine operations
- Error details for debugging

## 🚀 Production Deployment

For production use, consider:

1. **Process Manager**: Use systemd, supervisor, or similar
2. **Reverse Proxy**: Nginx or Apache in front of the API
3. **Environment Variables**: Configure production settings
4. **Logging**: Configure external log aggregation
5. **Monitoring**: Add health checks and metrics

## 📄 License

This backend uses open-source tools and is provided as-is for educational and prototyping purposes.

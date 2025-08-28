# SOF Week Speaker Recommendation Engine

An AI-powered recommendation engine that uses vector embeddings and similarity search to match natural language queries with the most relevant speakers from SOF Week 2025. Built entirely with free and open-source tools.

## 🚀 Features

- **Semantic Search**: Understands the meaning behind queries, not just keywords
- **Natural Language Queries**: Ask questions like "I'm a drone contractor, find me contacts that have experience in that field"
- **Fast Response**: Vector similarity search provides results in milliseconds
- **Comprehensive Results**: Includes relevance scores, explanations, and contact information
- **Multiple Interfaces**: Command-line, API, and demo modes

## 🛠️ Technology Stack

- **Embedding Model**: Sentence Transformers (`all-MiniLM-L6-v2`) - Free, lightweight, and fast
- **Vector Database**: ChromaDB - In-memory storage for simplicity
- **Web Framework**: FastAPI - Modern, fast Python web framework
- **All Tools**: 100% free and open source

## 📁 Project Structure

```
usul2/
├── data/
│   └── sof_week_speakers_complete.json    # Speaker data
├── backend/                                # Backend server
│   ├── __init__.py                        # Package initialization
│   ├── server.py                          # Main FastAPI server
│   ├── speaker_recommendation_engine.py   # Core recommendation engine
│   ├── run.py                             # Server runner
│   ├── requirements.txt                   # Backend dependencies
│   └── README.md                          # Backend documentation
├── frontend/                               # React UI
│   ├── package.json                       # Node.js dependencies
│   ├── src/                               # React source code
│   ├── public/                            # Static assets
│   ├── start.sh                           # Frontend startup script
│   └── README.md                          # Frontend documentation
├── cli.py                                  # Command-line interface
├── demo.py                                 # Demo script
├── start.sh                                # Interactive startup script
└── README.md                               # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
python demo.py
```

This will show you how the system works with several example queries.

### 3. Try Your Own Queries

```bash
python cli.py "I'm a drone contractor, find me contacts that have experience in that field"
```

### 4. Start the Web API

```bash
cd backend
python run.py
```

Then visit `http://localhost:8000` for the interactive API documentation.

### 5. Start the Frontend UI

```bash
cd frontend
./start.sh
```

Then visit `http://localhost:3001` for the clean, minimalist UI.

## 📖 Usage Examples

### Command Line Interface

```bash
# Basic recommendation
python cli.py "Looking for cybersecurity experts"

# Get more recommendations
python cli.py "Need acquisition specialists" --top-k 10

# Use different data file
python cli.py "Veteran transition experts" --data-file path/to/data.json
```

### Web API

```bash
# Start the server
cd backend
python run.py

# Then use these endpoints:
GET  /                    # Health check
POST /recommend           # Get speaker recommendations
GET  /speakers            # List all speakers
GET  /speakers/search     # Search by keyword
GET  /speakers/{name}     # Get specific speaker
GET  /stats               # Database statistics
```

### Example API Request

```bash
curl -X POST "http://localhost:8000/recommend" \
     -H "Content-Type: application/json" \
     -d '{"query": "I need contacts in drone technology", "top_k": 5}'
```

## 🔍 How It Works

### Phase 1: Indexing Pipeline

1. **Data Loading**: Loads speaker data from JSON file
2. **Document Construction**: Combines all speaker fields into coherent text documents
3. **Embedding Generation**: Uses Sentence Transformers to create vector embeddings
4. **Vector Storage**: Stores embeddings in ChromaDB for fast similarity search

### Phase 2: Retrieval Pipeline

1. **Query Processing**: Converts user query to vector embedding
2. **Similarity Search**: Finds most similar speaker documents using cosine similarity
3. **Result Ranking**: Ranks results by relevance score
4. **Explanation Generation**: Provides human-readable explanations for each recommendation

### Example Document Structure

```
Name: Mr. Jeff Pottinger | Title: Co-Founder | Company: ReLAUNCH Advisors | 
Session: The Honor Foundation Transition Seminar | Session Description: This one-day seminar... | 
Bio: Mr. Jeff Pottinger is a career transition expert...
```

## 📊 Sample Queries and Results

### Query: "I'm a drone contractor, find me contacts that have experience in that field"

**Expected Results:**
- Speakers with aviation/aircraft experience
- Technology and acquisition specialists
- SOF AT&L personnel
- Industry contractors in related fields

### Query: "Looking for experts in cybersecurity and information systems"

**Expected Results:**
- Enterprise Information Systems (EIS) directors
- Cybersecurity program managers
- Technology acquisition specialists
- Information security experts

### Query: "Need contacts in acquisition and procurement"

**Expected Results:**
- SOF AT&L acquisition executives
- Procurement directors
- Program managers
- Contracting officers

## ⚡ Performance Characteristics

- **Initialization**: ~2-5 seconds (includes model loading and indexing)
- **Query Response**: <100ms for typical queries
- **Memory Usage**: ~200-500MB (depending on model size)
- **Scalability**: Designed for small to medium datasets (44 speakers in this case)

## 🔧 Customization

### Adding New Data Sources

1. Update the `_create_speaker_documents()` method in `SpeakerRecommendationEngine`
2. Modify document construction logic for your data structure
3. Adjust embedding model if needed for your domain

### Changing the Embedding Model

```python
# In speaker_recommendation_engine.py
self.embedding_model = SentenceTransformer('your-model-name')
```

Popular alternatives:
- `all-mpnet-base-v2` - Higher quality, slower
- `paraphrase-MiniLM-L3-v2` - Faster, smaller
- `multi-qa-MiniLM-L6-cos-v1` - Optimized for Q&A

### Modifying Relevance Scoring

Update the `_generate_relevance_explanation()` method to customize how relevance is calculated and explained.

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **Memory Issues**: The embedding model requires ~200MB RAM
3. **Slow Initialization**: First run downloads the model (~90MB)
4. **No Results**: Try rephrasing your query or using different keywords

### Debug Mode

Enable detailed logging by modifying the logging level in the engine:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Future Enhancements

- **Hybrid Search**: Combine semantic search with keyword matching
- **User Feedback**: Learn from user interactions to improve recommendations
- **Multi-modal**: Include image analysis for speaker photos
- **Real-time Updates**: Support for live data updates
- **Advanced Filtering**: Filter by company, location, session type, etc.

## 🤝 Contributing

This is a prototype project. Feel free to:
- Report bugs
- Suggest improvements
- Add new features
- Optimize performance

## 📄 License

This project uses open-source tools and is provided as-is for educational and prototyping purposes.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Test with the demo script to verify functionality

---

**Built with ❤️ using free and open-source tools**
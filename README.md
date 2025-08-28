# SOF Week Speaker Recommendations

AI-powered speaker recommendation engine using vector embeddings.

## Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python run.py

# Frontend  
cd ../frontend
npm install
npm start
```

Visit `http://localhost:3000` to use the UI.

## How It Works

1. **Indexing**: Converts speaker data to vector embeddings using Sentence Transformers
2. **Search**: Finds similar speakers using ChromaDB vector similarity search
3. **Results**: Returns ranked recommendations with relevance scores

## Tech Stack

- **Backend**: FastAPI + Sentence Transformers + ChromaDB
- **Frontend**: React
- **Scrapers**: Python + BeautifulSoup/Selenium (run once to collect data)
- **All**: Free and open source

## Data Collection

The scrapers in the `scrapers/` folder collect speaker data from conference websites. They only need to be run **once** to populate the `data/` folder. After that, the recommendation engine uses the collected data.
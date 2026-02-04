# How to run Scrapbox RAG local

## 1. Prerequisites
- Docker (for Elasticsearch)
- Ollama (running Gemma 3)
- Python 3.12+ (uv recommended)
- Node.js 18+

## 2. Setup Elasticsearch
```bash
docker run -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.16.0
```

## 3. Setup Backend
```bash
cd backend
# Install dependencies
uv sync

# 1. Start SPLADE Encoder API (Port 8001)
uv run python encoder_app.py

# 2. Start Search API (Port 8000)
uv run python -m app.main
```

## 4. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

## 5. Usage
1. Open http://localhost:3000
2. Upload a Scrapbox JSON export using the "JSON Import" button.
3. Start searching!

# BharatAQI-X

A hackathon prototype that explores links between satellite formaldehyde (HCHO) observations and modeled surface air quality in India. The dashboard presents prediction, forecast, hotspot, and explanation views. The local demo generates sample data. Treat the resulting maps and forecasts as exploratory outputs.
**Bharatiya Antariksh Hackathon 2026 | Problem Statement: HCHO & Surface AQI**

---

## 📁 Project Structure

```
BharatAQI-X/
├── ml/                    # Machine Learning pipeline
│   ├── data_loader.py     # Data ingestion + synthetic fallback
│   ├── feature_engineering.py  # Lag, rolling, interaction features
│   ├── train_model.py     # RF + XGBoost + LightGBM + Ensemble
│   ├── hotspot_detection.py    # HCHO hotspots: DBSCAN + ISO Forest
│   └── explainability.py  # SHAP global + local explanations
├── agent/
│   └── agent.py           # LangChain + Qwen3 (Ollama) + Gemini fallback
├── backend/
│   ├── app.py             # FastAPI endpoints
│   └── requirements.txt   # Python dependencies
├── frontend/              # React + TypeScript + Vite
│   └── src/
│       ├── pages/         # Home, AQIMap, HCHOMap, Forecast, Explainability, AIAnalyst, About
│       ├── components/    # Layout (sidebar navigation)
│       └── lib/api.ts     # API client + AQI utilities
├── docker/
│   ├── Dockerfile.backend
│   └── docker-compose.yml
├── data/raw/              # Input CSVs (auto-generated if missing)
├── data/processed/        # master_dataset.csv
├── models/                # Serialized .pkl model files
├── outputs/               # Hotspot CSVs, summaries
└── figures/               # SHAP plots (PNG)
```

---

## 🚀 Quick Start

### 1. Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt

# Generate data + train models
cd ../ml
python data_loader.py          # Generates all 4 datasets
python feature_engineering.py  # Builds master_dataset.csv
python train_model.py          # Trains RF/XGBoost/LightGBM/Ensemble
python hotspot_detection.py    # Detects HCHO hotspots
python explainability.py       # Generates SHAP plots

# Start API server
cd ../backend
uvicorn app:app --reload --port 8000
# Docs → http://localhost:8000/docs
```

### 2. Frontend (React)
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 3. Docker (Full Stack)
```bash
cd docker
docker-compose up --build
# Backend  → http://localhost:8000
# Frontend → http://localhost:3000
# Ollama   → http://localhost:11434
```

---

## 🌐 API Endpoints

| Method | Endpoint    | Description |
|--------|-------------|-------------|
| GET    | `/predict`  | Predict surface AQI |
| GET    | `/forecast` | 7–30 day AQI forecast |
| GET    | `/hotspots` | HCHO hotspot clusters |
| GET    | `/explain`  | SHAP feature importance |
| POST   | `/analyze`  | AI agent analysis |
| GET    | `/map-data` | Geospatial dashboard data |

---

## 🤖 AI Agent

The agent uses LangChain with:
- **Primary**: Ollama + Qwen3 (local, no API key needed)
- **Fallback**: Google Gemini 1.5 Flash (`GOOGLE_API_KEY`)
- **Demo mode**: Built-in mock responses (no LLM required)

```bash
# Install Ollama + pull Qwen3
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3
```

---

## 📊 ML Models

| Model        | R² Target | Notes |
|-------------|-----------|-------|
| RandomForest | >0.82    | Baseline |
| XGBoost      | >0.87    | Best single model |
| LightGBM     | >0.88    | Fastest training |
| **Ensemble** | **>0.90**| XGB+LGB weighted 2:1 |

---

## 🗺️ Pages

| Page | Description |
|------|-------------|
| Home | National AQI dashboard, rankings |
| AQI Map | Interactive Leaflet map with city markers |
| HCHO Map | Sentinel-5P hotspot visualization |
| Forecast | 7–30 day predictions with Plotly charts |
| Explainability | SHAP global/local explanations |
| AI Analyst | LangChain agent with interactive sliders |
| About | Architecture, API docs, data sources |

---

## 🌍 Environment Variables

```env
GOOGLE_API_KEY=your_key      # For Gemini fallback
OLLAMA_HOST=http://localhost:11434
VITE_API_URL=http://localhost:8000
```

---

## 📦 Deployment

- **Backend**: Render.com (Docker or Python buildpack)
- **Frontend**: Vercel (`npm run build` → `/dist`)
- **Ollama**: Self-hosted or Replicate API

---

*Built for Bharatiya Antariksh Hackathon 2026 | ISRO*

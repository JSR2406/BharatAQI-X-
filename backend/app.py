"""
BharatAQI-X: FastAPI Backend
Endpoints: /predict, /forecast, /hotspots, /explain, /analyze, /health, /cities
"""
import logging, json, os, sys
from pathlib import Path
from typing import Optional, List
from datetime import date, datetime

import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ─── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
OUTPUTS    = BASE_DIR / "outputs"
sys.path.insert(0, str(BASE_DIR / "ml"))
sys.path.insert(0, str(BASE_DIR / "agent"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="BharatAQI-X API",
    description="Satellite-to-Surface Air Quality Digital Twin for India",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global State ──────────────────────────────────────────────────────────────
MODEL        = None
HOTSPOT_DATA = None
MASTER_DF    = None


def _load_resources():
    global MODEL, HOTSPOT_DATA, MASTER_DF
    try:
        model_path = MODELS_DIR / "lightgbm_model.pkl"
        if model_path.exists():
            MODEL = joblib.load(model_path)
            logger.info("Model loaded ✓")
        else:
            logger.warning("No trained model found – predictions will use heuristics")
    except Exception as e:
        logger.error(f"Model load error: {e}")

    hotspot_path = OUTPUTS / "hcho_hotspots_full.csv"
    if hotspot_path.exists():
        HOTSPOT_DATA = pd.read_csv(hotspot_path)
        logger.info(f"Hotspot data loaded: {len(HOTSPOT_DATA)} rows")

    master_path = BASE_DIR / "data" / "processed" / "master_dataset.csv"
    if master_path.exists():
        MASTER_DF = pd.read_csv(master_path, parse_dates=["date"])
        logger.info(f"Master dataset loaded: {len(MASTER_DF)} rows")


@app.on_event("startup")
async def startup():
    _load_resources()


# ─── Pydantic Models ───────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    city:        str         = Field(..., example="Delhi")
    date:        str         = Field(..., example="2024-06-15")
    pm25:        float       = Field(0,   ge=0, le=1000)
    pm10:        float       = Field(0,   ge=0, le=1000)
    no2:         float       = Field(0,   ge=0, le=500)
    so2:         float       = Field(0,   ge=0, le=500)
    co:          float       = Field(0,   ge=0, le=50)
    o3:          float       = Field(0,   ge=0, le=500)
    HCHO:        float       = Field(0,   ge=0)
    temperature: float       = Field(25)
    humidity:    float       = Field(60,  ge=0, le=100)
    pressure:    float       = Field(1013)
    wind_speed:  float       = Field(2,   ge=0)
    fire_count:  int         = Field(0,   ge=0)
    latitude:    float       = Field(28.6)
    longitude:   float       = Field(77.2)


class AnalyzeRequest(BaseModel):
    city:        str   = Field(..., example="Delhi")
    aqi:         float = Field(..., example=200)
    pm25:        float = Field(0)
    pm10:        float = Field(0)
    no2:         float = Field(0)
    so2:         float = Field(0)
    co:          float = Field(0)
    o3:          float = Field(0)
    hcho:        float = Field(0)
    temperature: float = Field(25)
    humidity:    float = Field(60)
    wind_speed:  float = Field(2)
    fire_count:  int   = Field(0)
    date:        str   = Field("2024-01-01")
    use_mock:    bool  = Field(True)


# ─── AQI Utilities ─────────────────────────────────────────────────────────────
CITY_COORDS = {
    "Delhi": (28.6139, 77.2090), "Mumbai": (19.0760, 72.8777),
    "Kolkata": (22.5726, 88.3639), "Chennai": (13.0827, 80.2707),
    "Bangalore": (12.9716, 77.5946), "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567), "Ahmedabad": (23.0225, 72.5714),
    "Lucknow": (26.8467, 80.9462), "Kanpur": (26.4499, 80.3319),
    "Jaipur": (26.9124, 75.7873), "Patna": (25.5941, 85.1376),
}

def _aqi_category(aqi: float) -> str:
    if aqi <= 50:   return "Good"
    if aqi <= 100:  return "Satisfactory"
    if aqi <= 200:  return "Moderate"
    if aqi <= 300:  return "Poor"
    if aqi <= 400:  return "Very Poor"
    return "Severe"

def _heuristic_aqi(req: PredictRequest) -> float:
    return min(500, max(0,
        req.pm25 * 1.5 + req.no2 * 0.5 + req.so2 * 0.3 +
        req.co * 20 + req.pm10 * 0.3 + req.fire_count * 2
    ))

def _build_feature_vector(req: PredictRequest) -> dict:
    dt = pd.to_datetime(req.date)
    return {
        "pm25": req.pm25, "pm10": req.pm10, "no2": req.no2,
        "so2": req.so2, "co": req.co, "o3": req.o3, "HCHO": req.HCHO,
        "temperature": req.temperature, "humidity": req.humidity,
        "pressure": req.pressure, "wind_speed": req.wind_speed,
        "latitude": req.latitude, "longitude": req.longitude,
        "month": dt.month, "fire_count": req.fire_count,
        "day_of_year": dt.day_of_year, "is_weekend": int(dt.weekday() >= 5),
        "month_sin": np.sin(2 * np.pi * dt.month / 12),
        "month_cos": np.cos(2 * np.pi * dt.month / 12),
    }


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    return {
        "project": "BharatAQI-X",
        "version": "1.0.0",
        "description": "Explainable Satellite-to-Surface AQI Digital Twin for India",
        "endpoints": ["/predict", "/forecast", "/hotspots", "/explain", "/analyze",
                      "/cities", "/health", "/docs"],
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "model_loaded": MODEL is not None,
        "hotspot_data": HOTSPOT_DATA is not None,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/cities", tags=["Reference"])
def get_cities():
    return {
        "cities": [
            {"name": name, "latitude": lat, "longitude": lon}
            for name, (lat, lon) in CITY_COORDS.items()
        ]
    }


@app.post("/predict", tags=["Prediction"])
def predict_aqi(req: PredictRequest):
    try:
        if MODEL is not None:
            feats = _build_feature_vector(req)
            X = pd.DataFrame([feats])
            cols = [c for c in X.columns if c in (MODEL.feature_name_() if hasattr(MODEL, "feature_name_") else X.columns)]
            X_inp = X.reindex(columns=cols if cols else X.columns, fill_value=0)
            predicted_aqi = float(MODEL.predict(X_inp)[0])
        else:
            predicted_aqi = _heuristic_aqi(req)

        return {
            "city":          req.city,
            "date":          req.date,
            "predicted_aqi": round(predicted_aqi, 1),
            "category":      _aqi_category(predicted_aqi),
            "model_used":    "LightGBM" if MODEL else "heuristic",
            "input_summary": {
                "pm25": req.pm25, "pm10": req.pm10,
                "no2": req.no2, "HCHO": req.HCHO,
            },
        }
    except Exception as e:
        logger.error(f"/predict error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/forecast", tags=["Prediction"])
def forecast_aqi(
    city: str = Query(..., example="Delhi"),
    days: int = Query(7, ge=1, le=30),
):
    try:
        if MASTER_DF is not None and city in MASTER_DF["city"].values:
            city_df = MASTER_DF[MASTER_DF["city"] == city].sort_values("date")
            last_known = city_df["aqi"].tail(30).values
            trend      = np.polyfit(range(len(last_known)), last_known, 1)[0]
            base_aqi   = last_known[-1]
        else:
            base_aqi = 150.0
            trend    = 0.0

        forecast = []
        for i in range(1, days + 1):
            noise     = np.random.normal(0, 8)
            pred_aqi  = max(0, min(500, base_aqi + trend * i + noise))
            forecast.append({
                "day":      i,
                "aqi":      round(pred_aqi, 1),
                "category": _aqi_category(pred_aqi),
            })

        return {"city": city, "forecast_days": days, "forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/hotspots", tags=["Hotspots"])
def get_hotspots(
    top_n:    int   = Query(50, ge=1, le=500),
    method:   str   = Query("any", enum=["pct", "dbscan", "iso", "any"]),
    min_hcho: float = Query(0.0, ge=0),
):
    try:
        if HOTSPOT_DATA is None:
            # Return mock hotspot data
            mock = [
                {"latitude": 28.6, "longitude": 77.2, "HCHO": 8.2e-5, "state": "Delhi", "cluster": 0},
                {"latitude": 30.2, "longitude": 75.8, "HCHO": 7.1e-5, "state": "Punjab", "cluster": 1},
                {"latitude": 25.3, "longitude": 83.0, "HCHO": 6.8e-5, "state": "Uttar Pradesh", "cluster": 2},
            ]
            return {"count": len(mock), "hotspots": mock, "method": method}

        df = HOTSPOT_DATA.copy()
        if method == "pct":
            mask = df.get("is_hotspot_pct", pd.Series(False, index=df.index))
        elif method == "dbscan":
            mask = df.get("cluster", pd.Series(-1, index=df.index)) >= 0
        elif method == "iso":
            mask = df.get("is_hotspot_iso", pd.Series(False, index=df.index))
        else:
            mask = df.get("hotspot_any", pd.Series(False, index=df.index))

        if "HCHO" in df.columns:
            df = df[df["HCHO"] >= min_hcho]

        hotspots = df[mask].nlargest(top_n, "HCHO") if "HCHO" in df.columns else df[mask].head(top_n)
        return {
            "count":    len(hotspots),
            "method":   method,
            "hotspots": hotspots[["latitude","longitude","HCHO","state","cluster"]].fillna("N/A").to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/explain", tags=["Explainability"])
def get_explanations(city: str = Query("Delhi"), top_n: int = Query(10)):
    fig_dir = BASE_DIR / "figures"
    local_exp_path = fig_dir / "local_explanations.json"
    global_fi_path = fig_dir / "global_shap_importance.csv"

    response = {"city": city, "status": "ok"}

    if local_exp_path.exists():
        with open(local_exp_path) as f:
            response["local_explanations"] = json.load(f)

    if global_fi_path.exists():
        fi_df = pd.read_csv(global_fi_path).head(top_n)
        response["global_feature_importance"] = fi_df.to_dict(orient="records")
    else:
        response["global_feature_importance"] = [
            {"feature": "pm25",       "mean_abs_shap": 45.2},
            {"feature": "aqi_lag1",   "mean_abs_shap": 38.7},
            {"feature": "no2",        "mean_abs_shap": 22.1},
            {"feature": "HCHO",       "mean_abs_shap": 18.5},
            {"feature": "fire_count", "mean_abs_shap": 12.3},
            {"feature": "humidity",   "mean_abs_shap": 9.8},
            {"feature": "wind_speed", "mean_abs_shap": 8.4},
            {"feature": "temperature","mean_abs_shap": 6.7},
        ][:top_n]

    return response


@app.post("/analyze", tags=["Agent"])
def ai_analyze(req: AnalyzeRequest):
    try:
        from agent import analyze_location
        analysis = analyze_location(
            city=req.city, aqi=req.aqi, pm25=req.pm25, pm10=req.pm10,
            no2=req.no2, so2=req.so2, co=req.co, o3=req.o3, hcho=req.hcho,
            temperature=req.temperature, humidity=req.humidity,
            wind_speed=req.wind_speed, fire_count=req.fire_count,
            date=req.date, use_mock=req.use_mock,
        )
        return {"city": req.city, "aqi": req.aqi, "analysis": analysis}
    except Exception as e:
        logger.error(f"/analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/map-data", tags=["Map"])
def get_map_data(pollutant: str = Query("aqi", enum=["aqi","pm25","HCHO","no2","fire"])):
    if MASTER_DF is not None:
        latest = MASTER_DF.sort_values("date").groupby("city").last().reset_index()
        col = pollutant if pollutant in latest.columns else "aqi"
        records = latest[["city","latitude","longitude", col]].dropna().to_dict(orient="records")
    else:
        records = [
            {"city": "Delhi",    "latitude": 28.61, "longitude": 77.21, pollutant: 285},
            {"city": "Mumbai",   "latitude": 19.08, "longitude": 72.88, pollutant: 120},
            {"city": "Kolkata",  "latitude": 22.57, "longitude": 88.36, pollutant: 198},
            {"city": "Chennai",  "latitude": 13.08, "longitude": 80.27, pollutant: 95},
            {"city": "Bangalore","latitude": 12.97, "longitude": 77.59, pollutant: 88},
        ]
    return {"pollutant": pollutant, "data": records}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

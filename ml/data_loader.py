"""
BharatAQI-X: Data Loader Module
Loads, validates, and cleans all datasets. Generates synthetic data if files are missing.
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"
PROC_DIR = BASE_DIR / "data" / "processed"

INDIA_CITIES = {
    "Delhi":          (28.6139, 77.2090),
    "Mumbai":         (19.0760, 72.8777),
    "Kolkata":        (22.5726, 88.3639),
    "Chennai":        (13.0827, 80.2707),
    "Bangalore":      (12.9716, 77.5946),
    "Hyderabad":      (17.3850, 78.4867),
    "Pune":           (18.5204, 73.8567),
    "Ahmedabad":      (23.0225, 72.5714),
    "Lucknow":        (26.8467, 80.9462),
    "Kanpur":         (26.4499, 80.3319),
    "Jaipur":         (26.9124, 75.7873),
    "Patna":          (25.5941, 85.1376),
    "Bhopal":         (23.2599, 77.4126),
    "Nagpur":         (21.1458, 79.0882),
    "Indore":         (22.7196, 75.8577),
    "Surat":          (21.1702, 72.8311),
    "Varanasi":       (25.3176, 82.9739),
    "Agra":           (27.1767, 78.0081),
    "Amritsar":       (31.6340, 74.8723),
    "Chandigarh":     (30.7333, 76.7794),
    "Visakhapatnam":  (17.6868, 83.2185),
    "Coimbatore":     (11.0168, 76.9558),
    "Kochi":          ( 9.9312, 76.2673),
    "Guwahati":       (26.1445, 91.7362),
    "Bhubaneswar":    (20.2961, 85.8245),
    "Raipur":         (21.2514, 81.6296),
    "Ranchi":         (23.3441, 85.3096),
    "Jodhpur":        (26.2389, 73.0243),
    "Srinagar":       (34.0837, 74.7973),
    "Thiruvananthapuram": (8.5241, 76.9366),
}

CITY_POLLUTION_FACTOR = {
    "Delhi": 2.5, "Kanpur": 2.2, "Kolkata": 2.0, "Patna": 1.8,
    "Agra": 1.7, "Lucknow": 1.6, "Varanasi": 1.5, "Mumbai": 1.4,
    "Ahmedabad": 1.3, "Jodhpur": 1.2, "Pune": 1.1, "Hyderabad": 1.0,
    "Chennai": 0.95, "Bangalore": 0.9, "Kochi": 0.7, "Thiruvananthapuram": 0.65,
    "Srinagar": 0.6,
}


def _ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROC_DIR.mkdir(parents=True, exist_ok=True)


def _validate_dataframe(df: pd.DataFrame, required_cols: list, name: str = "dataset") -> pd.DataFrame:
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"[{name}] Missing required columns: {missing}")

    before = len(df)
    df = df.drop_duplicates()
    dropped = before - len(df)
    if dropped:
        logger.info(f"[{name}] Dropped {dropped} duplicate rows")

    null_report = df[required_cols].isnull().sum()
    if null_report.any():
        logger.warning(f"[{name}] Nulls found: {null_report[null_report > 0].to_dict()}")
        df = df.dropna(subset=required_cols)

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    logger.info(f"[{name}] Validated: {len(df)} records remaining")
    return df


# ─── Synthetic Data Generators ────────────────────────────────────────────────

def _generate_aqi(n_days: int = 365) -> pd.DataFrame:
    logger.info("Generating synthetic AQI data …")
    records = []
    start = datetime(2023, 1, 1)
    for city, (lat, lon) in INDIA_CITIES.items():
        factor = CITY_POLLUTION_FACTOR.get(city, 1.0)
        for d in range(n_days):
            date  = start + timedelta(days=d)
            month = date.month
            sea   = 1 + 0.5 * np.sin((month - 11) * np.pi / 6) if lat > 20 else 1.0
            pm25  = max(5,   np.random.normal(40 * factor * sea, 15))
            pm10  = max(10,  pm25 * np.random.uniform(1.5, 2.0))
            no2   = max(2,   np.random.normal(25 * factor * sea, 10))
            so2   = max(1,   np.random.normal(10 * factor, 5))
            co    = max(0.1, np.random.normal(1.5 * factor, 0.5))
            o3    = max(5,   np.random.normal(60 - 10 * factor, 15))
            aqi   = min(500, max(0, pm25 * 1.5 + no2 * 0.5 + so2 * 0.3 + co * 20 + pm10 * 0.3))
            records.append(dict(
                date=date.strftime("%Y-%m-%d"), city=city,
                latitude=round(lat + np.random.uniform(-0.05, 0.05), 4),
                longitude=round(lon + np.random.uniform(-0.05, 0.05), 4),
                pm25=round(pm25, 2), pm10=round(pm10, 2),
                no2=round(no2, 2), so2=round(so2, 2),
                co=round(co, 3), o3=round(o3, 2), aqi=round(aqi, 1),
            ))
    return pd.DataFrame(records)


def _generate_satellite(n_days: int = 365) -> pd.DataFrame:
    logger.info("Generating synthetic Sentinel-5P data …")
    records = []
    start = datetime(2023, 1, 1)
    lats  = np.arange(8, 37, 2.5)
    lons  = np.arange(68, 98, 2.5)
    for d in range(0, n_days, 3):
        date  = start + timedelta(days=d)
        month = date.month
        hcho_season = 1 + 0.4 * np.sin((month - 3) * np.pi / 6)
        for lat in lats:
            for lon in lons:
                igp = 1.6 if (24 < lat < 32 and 75 < lon < 90) else 1.0
                records.append(dict(
                    date=date.strftime("%Y-%m-%d"),
                    latitude=round(lat, 2), longitude=round(lon, 2),
                    NO2=round(max(0, np.random.normal(3e-5 * igp, 1e-5)), 7),
                    SO2=round(max(0, np.random.normal(2e-5 * igp, 8e-6)), 7),
                    CO=round(max(0,  np.random.normal(0.025 * igp, 0.01)), 4),
                    O3=round(max(0,  np.random.normal(0.15, 0.03)), 4),
                    HCHO=round(max(0, np.random.normal(4e-5 * igp * hcho_season, 1.5e-5)), 7),
                ))
    return pd.DataFrame(records)


def _generate_fire(n_days: int = 365) -> pd.DataFrame:
    logger.info("Generating synthetic fire data …")
    records = []
    start = datetime(2023, 1, 1)
    regions = [
        (30.0, 75.5, "Punjab/Haryana", [10, 11]),
        (21.0, 82.0, "MP Forests",     [3, 4, 5]),
        (20.5, 85.0, "Odisha",         [3, 4, 5]),
        (25.0, 87.0, "Bihar",          [10, 11]),
        (24.0, 93.0, "NE Forests",     [3, 4]),
    ]
    for d in range(n_days):
        date  = start + timedelta(days=d)
        month = date.month
        for blat, blon, name, peak_months in regions:
            n_fires = np.random.poisson(12 if month in peak_months else 1)
            for _ in range(n_fires):
                records.append(dict(
                    acq_date=date.strftime("%Y-%m-%d"),
                    latitude=round(blat + np.random.uniform(-2, 2), 4),
                    longitude=round(blon + np.random.uniform(-2, 2), 4),
                    brightness=round(np.random.uniform(300, 450), 1),
                    confidence=random.choice(["low", "nominal", "high"]),
                    frp=round(np.random.exponential(20), 1),
                ))
    return pd.DataFrame(records)


def _generate_weather(n_days: int = 365) -> pd.DataFrame:
    logger.info("Generating synthetic weather data …")
    records = []
    start = datetime(2023, 1, 1)
    for city, (lat, lon) in INDIA_CITIES.items():
        for d in range(n_days):
            date  = start + timedelta(days=d)
            month = date.month
            base_t = 30 - (lat - 15) * 0.5
            temp   = base_t + 5 * np.sin((month - 4) * np.pi / 6) + np.random.normal(0, 3)
            hum    = np.clip(np.random.normal(80 if 6 <= month <= 9 else 50, 10), 20, 100)
            records.append(dict(
                date=date.strftime("%Y-%m-%d"),
                latitude=lat, longitude=lon,
                temperature=round(temp, 2),
                humidity=round(hum, 1),
                pressure=round(np.random.normal(1013, 5), 2),
                wind_speed=round(max(0, np.random.normal(3, 2)), 2),
            ))
    return pd.DataFrame(records)


# ─── Public Loaders ────────────────────────────────────────────────────────────

def load_aqi(filepath: Path = None) -> pd.DataFrame:
    _ensure_dirs()
    path = filepath or RAW_DIR / "openaq_india.csv"
    if not path.exists():
        df = _generate_aqi()
        df.to_csv(path, index=False)
    df = pd.read_csv(path)
    df = _validate_dataframe(df, ["date","city","latitude","longitude","pm25","aqi"], "AQI")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_satellite(filepath: Path = None) -> pd.DataFrame:
    _ensure_dirs()
    path = filepath or RAW_DIR / "sentinel5p_india.csv"
    if not path.exists():
        df = _generate_satellite()
        df.to_csv(path, index=False)
    df = pd.read_csv(path)
    df = _validate_dataframe(df, ["date","latitude","longitude","HCHO"], "Satellite")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_fire(filepath: Path = None) -> pd.DataFrame:
    _ensure_dirs()
    path = filepath or RAW_DIR / "fire_india.csv"
    if not path.exists():
        df = _generate_fire()
        df.to_csv(path, index=False)
    df = pd.read_csv(path)
    df = _validate_dataframe(df, ["acq_date","latitude","longitude"], "Fire")
    df["acq_date"] = pd.to_datetime(df["acq_date"])
    return df


def load_weather(filepath: Path = None) -> pd.DataFrame:
    _ensure_dirs()
    path = filepath or RAW_DIR / "weather_india.csv"
    if not path.exists():
        df = _generate_weather()
        df.to_csv(path, index=False)
    df = pd.read_csv(path)
    df = _validate_dataframe(df, ["date","latitude","longitude","temperature"], "Weather")
    df["date"] = pd.to_datetime(df["date"])
    return df


if __name__ == "__main__":
    aqi = load_aqi();    logger.info(f"AQI: {len(aqi)} rows, {aqi['city'].nunique()} cities")
    sat = load_satellite(); logger.info(f"Satellite: {len(sat)} rows")
    fir = load_fire();   logger.info(f"Fire: {len(fir)} rows")
    wea = load_weather(); logger.info(f"Weather: {len(wea)} rows")

"""
BharatAQI-X: Feature Engineering Module
Creates lag features, rolling averages, spatial, temporal, and interaction features.
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"


def merge_datasets(aqi_df, sat_df, fire_df, weather_df) -> pd.DataFrame:
    """Merge all four datasets into a master feature DataFrame."""
    logger.info("Merging datasets …")

    # --- Round satellite lat/lon for approximate join ---
    sat_df = sat_df.copy()
    sat_df["lat_r"] = (sat_df["latitude"] / 2.5).round() * 2.5
    sat_df["lon_r"] = (sat_df["longitude"] / 2.5).round() * 2.5
    sat_agg = sat_df.groupby(["date","lat_r","lon_r"])[["NO2","SO2","CO","O3","HCHO"]].mean().reset_index()
    sat_agg.rename(columns={"lat_r":"latitude","lon_r":"longitude"}, inplace=True)

    # --- Fire count per day (national) ---
    fire_daily = fire_df.groupby("acq_date").size().reset_index(name="fire_count")
    fire_daily.rename(columns={"acq_date":"date"}, inplace=True)

    # --- Start from AQI ---
    df = aqi_df.copy()

    # Round AQI lat/lon to nearest grid
    df["lat_r"] = (df["latitude"] / 2.5).round() * 2.5
    df["lon_r"] = (df["longitude"] / 2.5).round() * 2.5

    # Merge satellite on approximate grid
    df = df.merge(sat_agg, left_on=["date","lat_r","lon_r"],
                  right_on=["date","latitude","longitude"], how="left", suffixes=("","_sat"))
    df.drop(columns=["lat_r","lon_r","latitude_sat","longitude_sat"], errors="ignore", inplace=True)

    # Merge weather on city lat/lon
    weather_city = weather_df.groupby(["date","latitude","longitude"])[
        ["temperature","humidity","pressure","wind_speed"]
    ].mean().reset_index()
    df = df.merge(weather_city, on=["date","latitude","longitude"], how="left")

    # Merge fire counts
    df = df.merge(fire_daily, on="date", how="left")
    df["fire_count"] = df["fire_count"].fillna(0)

    # Fill remaining satellite nulls with medians
    for col in ["NO2","SO2","CO","O3","HCHO"]:
        df[col] = df[col].fillna(df[col].median())

    for col in ["temperature","humidity","pressure","wind_speed"]:
        df[col] = df[col].fillna(df[col].median())

    logger.info(f"Merged dataset shape: {df.shape}")
    return df


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Month, day-of-year, season, weekend flag."""
    logger.info("Adding temporal features …")
    df = df.copy()
    df["month"]       = df["date"].dt.month
    df["day_of_year"] = df["date"].dt.dayofyear
    df["day_of_week"] = df["date"].dt.dayofweek
    df["year"]        = df["date"].dt.year
    df["is_weekend"]  = (df["day_of_week"] >= 5).astype(int)

    def season(m):
        if m in [12, 1, 2]:  return "Winter"
        if m in [3, 4, 5]:   return "Spring"
        if m in [6, 7, 8, 9]: return "Monsoon"
        return "Autumn"

    df["season"] = df["month"].apply(season)
    le = LabelEncoder()
    df["season_enc"] = le.fit_transform(df["season"])

    # Cyclic encoding for month
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    return df


def add_lag_features(df: pd.DataFrame, target_cols: list, lags: list = [1, 3, 7]) -> pd.DataFrame:
    """Lag features per city."""
    logger.info(f"Adding lag features for {target_cols} at lags {lags} …")
    df = df.sort_values(["city", "date"]).copy()
    for col in target_cols:
        for lag in lags:
            df[f"{col}_lag{lag}"] = df.groupby("city")[col].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame, target_cols: list, windows: list = [3, 7, 14]) -> pd.DataFrame:
    """Rolling mean & std per city."""
    logger.info(f"Adding rolling features …")
    df = df.sort_values(["city", "date"]).copy()
    for col in target_cols:
        for win in windows:
            roll = df.groupby("city")[col].transform(lambda x: x.shift(1).rolling(win, min_periods=1).mean())
            df[f"{col}_roll{win}_mean"] = roll
            roll_std = df.groupby("city")[col].transform(lambda x: x.shift(1).rolling(win, min_periods=1).std())
            df[f"{col}_roll{win}_std"] = roll_std.fillna(0)
    return df


def add_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-pollutant and weather-pollution interaction features."""
    logger.info("Adding interaction features …")
    df = df.copy()
    # Pollution interactions
    df["pm25_no2"]   = df["pm25"] * df["no2"]
    df["hcho_temp"]  = df["HCHO"] * df["temperature"]
    df["no2_wind"]   = df["no2"]  / (df["wind_speed"] + 0.1)
    df["fire_pm25"]  = df["fire_count"] * df["pm25"]
    df["humidity_so2"] = df["humidity"] * df["so2"]

    # Pollution ratio features
    df["pm25_pm10_ratio"] = df["pm25"] / (df["pm10"] + 1e-6)
    df["no2_o3_ratio"]    = df["no2"]  / (df["o3"]   + 1e-6)

    # Atmospheric stability proxy
    df["atm_stability"] = df["wind_speed"] / (df["temperature"] + 273.15)
    return df


def encode_city(df: pd.DataFrame) -> pd.DataFrame:
    """Label-encode city column."""
    le = LabelEncoder()
    df["city_enc"] = le.fit_transform(df["city"])
    return df, le


def build_master_dataset(aqi_df, sat_df, fire_df, weather_df, save: bool = True) -> pd.DataFrame:
    """Full feature engineering pipeline."""
    df = merge_datasets(aqi_df, sat_df, fire_df, weather_df)
    df = add_temporal_features(df)

    poll_cols = ["pm25","pm10","no2","so2","co","o3","HCHO","aqi"]
    df = add_lag_features(df, target_cols=poll_cols, lags=[1, 3, 7])
    df = add_rolling_features(df, target_cols=["pm25","aqi","HCHO"], windows=[3, 7, 14])
    df = add_interaction_features(df)
    df, _ = encode_city(df)

    # Drop rows with null lags (first 7 rows per city)
    df.dropna(subset=[c for c in df.columns if "_lag7" in c], inplace=True)
    df.reset_index(drop=True, inplace=True)

    logger.info(f"Master dataset: {df.shape[0]} rows × {df.shape[1]} columns")

    if save:
        PROC_DIR.mkdir(parents=True, exist_ok=True)
        out = PROC_DIR / "master_dataset.csv"
        df.to_csv(out, index=False)
        logger.info(f"Saved → {out}")

    return df


FEATURE_COLS = [
    "pm25","pm10","no2","so2","co","o3","HCHO",
    "temperature","humidity","pressure","wind_speed",
    "latitude","longitude","month","season_enc","fire_count",
    "city_enc","day_of_year","is_weekend","month_sin","month_cos",
    "pm25_lag1","pm25_lag3","pm25_lag7",
    "aqi_lag1","aqi_lag3","aqi_lag7",
    "HCHO_lag1","HCHO_lag3","HCHO_lag7",
    "no2_lag1","no2_lag3",
    "pm25_roll3_mean","pm25_roll7_mean","pm25_roll14_mean",
    "pm25_roll7_std",
    "aqi_roll3_mean","aqi_roll7_mean",
    "HCHO_roll7_mean",
    "pm25_no2","hcho_temp","no2_wind","fire_pm25","humidity_so2",
    "pm25_pm10_ratio","no2_o3_ratio","atm_stability",
]

TARGET_COL = "aqi"


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(Path(__file__).parent))
    from data_loader import load_aqi, load_satellite, load_fire, load_weather
    aqi = load_aqi(); sat = load_satellite(); fir = load_fire(); wea = load_weather()
    master = build_master_dataset(aqi, sat, fir, wea)
    print(master[["date","city","aqi","HCHO","fire_count"]].head(10))

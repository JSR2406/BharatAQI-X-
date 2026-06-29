"""
BharatAQI-X: HCHO Hotspot Detection Module
Detects HCHO hotspots using percentile thresholding, DBSCAN, and Isolation Forest.
"""
import logging, json
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from shapely.geometry import Point

logger = logging.getLogger(__name__)
BASE_DIR  = Path(__file__).resolve().parent.parent
OUT_DIR   = BASE_DIR / "outputs"
FIG_DIR   = BASE_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# India state bounding boxes (approx)
INDIA_STATES = {
    "Uttar Pradesh":     (24.0, 83.0, 30.0, 78.0),
    "Bihar":             (24.0, 83.0, 27.5, 88.0),
    "Punjab":            (29.5, 73.8, 32.5, 76.9),
    "Haryana":           (27.6, 74.0, 30.9, 77.6),
    "Delhi":             (28.4, 76.8, 28.9, 77.4),
    "Rajasthan":         (23.0, 69.5, 30.2, 78.2),
    "Maharashtra":       (15.6, 72.6, 22.0, 80.9),
    "Odisha":            (17.8, 81.4, 22.6, 87.5),
    "Jharkhand":         (21.9, 83.3, 25.4, 87.5),
    "West Bengal":       (21.5, 85.8, 27.2, 89.9),
    "Assam":             (24.1, 89.7, 27.9, 96.0),
    "Madhya Pradesh":    (21.1, 74.0, 26.9, 82.8),
    "Chhattisgarh":      (17.8, 80.2, 24.1, 84.4),
    "Telangana":         (15.8, 77.2, 19.9, 81.3),
    "Andhra Pradesh":    (12.6, 77.0, 19.9, 84.8),
    "Karnataka":         ( 11.6, 74.0, 18.5, 78.6),
    "Tamil Nadu":        (  8.1, 77.0, 13.6, 80.3),
    "Kerala":            (  8.2, 74.8, 12.8, 77.4),
    "Gujarat":           (20.1, 68.2, 24.7, 74.4),
}


def percentile_threshold(sat_df: pd.DataFrame, column: str = "HCHO",
                          threshold_pct: float = 90.0) -> pd.DataFrame:
    """Flag cells above a given percentile as hotspots."""
    thresh = np.percentile(sat_df[column].dropna(), threshold_pct)
    result = sat_df.copy()
    result["is_hotspot_pct"] = result[column] >= thresh
    result["hotspot_score"]  = (result[column] - thresh).clip(lower=0)
    n = result["is_hotspot_pct"].sum()
    logger.info(f"Percentile({threshold_pct}%) threshold={thresh:.6f}: {n} hotspot cells")
    return result, thresh


def dbscan_clusters(sat_df: pd.DataFrame, column: str = "HCHO",
                    eps_deg: float = 2.5, min_samples: int = 5) -> pd.DataFrame:
    """Cluster hotspot cells using DBSCAN on lat/lon."""
    result = sat_df.copy()
    threshold = np.percentile(sat_df[column].dropna(), 85)
    hot = result[result[column] >= threshold].copy()

    coords = hot[["latitude","longitude"]].values
    # Convert degrees to km roughly: 1° ≈ 111 km
    eps_rad = eps_deg / 111.0
    db = DBSCAN(eps=eps_rad, min_samples=min_samples, algorithm="ball_tree", metric="haversine")
    hot["cluster"] = db.fit_predict(np.radians(coords))

    result["cluster"] = -1
    result.loc[hot.index, "cluster"] = hot["cluster"]

    n_clusters = len(set(hot["cluster"])) - (1 if -1 in hot["cluster"].values else 0)
    logger.info(f"DBSCAN found {n_clusters} clusters, {(hot['cluster']==-1).sum()} noise pts")
    return result


def isolation_forest_anomaly(sat_df: pd.DataFrame,
                              feature_cols: list = ["HCHO","NO2","SO2","CO"],
                              contamination: float = 0.1) -> pd.DataFrame:
    """Use Isolation Forest to detect anomalous pollution cells."""
    result = sat_df.copy()
    cols = [c for c in feature_cols if c in sat_df.columns]
    X = result[cols].fillna(result[cols].median())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    iso = IsolationForest(contamination=contamination, random_state=42, n_jobs=-1)
    preds = iso.fit_predict(X_scaled)
    scores = iso.score_samples(X_scaled)

    result["anomaly_label"]  = preds          # -1 = anomaly, 1 = normal
    result["anomaly_score"]  = -scores        # higher = more anomalous
    result["is_hotspot_iso"] = preds == -1

    n = (preds == -1).sum()
    logger.info(f"Isolation Forest: {n} anomalies detected ({contamination*100:.0f}% contamination)")
    return result


def assign_state(df: pd.DataFrame) -> pd.DataFrame:
    """Assign Indian state based on lat/lon bounding boxes (approximate)."""
    def _get_state(row):
        for state, (lat_min, lon_min, lat_max, lon_max) in INDIA_STATES.items():
            if lat_min <= row["latitude"] <= lat_max and lon_min <= row["longitude"] <= lon_max:
                return state
        return "Other"
    df = df.copy()
    df["state"] = df.apply(_get_state, axis=1)
    return df


def compute_statewise_hotspots(sat_df: pd.DataFrame, column: str = "HCHO") -> pd.DataFrame:
    """Aggregate hotspot statistics per state."""
    df = assign_state(sat_df)
    stats = df.groupby("state").agg(
        mean_hcho    =(column, "mean"),
        max_hcho     =(column, "max"),
        hotspot_count=("is_hotspot_pct", "sum") if "is_hotspot_pct" in df.columns else (column, "count"),
        cell_count   =(column, "count"),
    ).reset_index()
    stats["hotspot_density"] = stats["hotspot_count"] / stats["cell_count"]
    stats = stats.sort_values("mean_hcho", ascending=False).reset_index(drop=True)
    stats.to_csv(OUT_DIR / "statewise_hotspots.csv", index=False)
    logger.info(f"Top 5 states by HCHO: {stats['state'].head(5).tolist()}")
    return stats


def run_hotspot_pipeline(sat_df: pd.DataFrame) -> dict:
    """Run all three hotspot methods and save outputs."""
    logger.info("=== HCHO Hotspot Detection Pipeline ===")

    pct_df, thresh  = percentile_threshold(sat_df)
    dbscan_df       = dbscan_clusters(pct_df)
    iso_df          = isolation_forest_anomaly(dbscan_df)
    final_df        = assign_state(iso_df)

    # Combined hotspot flag
    final_df["hotspot_any"] = (
        final_df.get("is_hotspot_pct", False) |
        (final_df.get("cluster", -1) >= 0)   |
        final_df.get("is_hotspot_iso", False)
    )

    final_df.to_csv(OUT_DIR / "hcho_hotspots_full.csv", index=False)
    logger.info(f"Saved full hotspot data → {OUT_DIR / 'hcho_hotspots_full.csv'}")

    statewise = compute_statewise_hotspots(final_df)

    summary = {
        "threshold_pct90":      round(thresh, 7),
        "n_hotspot_pct":        int(final_df.get("is_hotspot_pct", pd.Series()).sum()),
        "n_dbscan_clusters":    int(final_df[final_df.get("cluster", pd.Series(dtype=int)) >= 0].shape[0]) if "cluster" in final_df else 0,
        "n_anomalies_iso":      int(final_df.get("is_hotspot_iso", pd.Series()).sum()),
        "top_state_hcho":       statewise["state"].iloc[0] if len(statewise) else "N/A",
        "top_state_hcho_value": round(float(statewise["mean_hcho"].iloc[0]), 7) if len(statewise) else 0,
    }

    with open(OUT_DIR / "hotspot_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return {"data": final_df, "statewise": statewise, "summary": summary}


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(Path(__file__).parent))
    from data_loader import load_satellite
    sat = load_satellite()
    results = run_hotspot_pipeline(sat)
    print(results["statewise"].head(10))

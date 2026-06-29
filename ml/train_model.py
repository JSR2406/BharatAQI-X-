"""
BharatAQI-X: Model Training Module
Trains RandomForest, XGBoost, LightGBM and an ensemble. Saves best model.
"""
import logging, json, joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb

logger = logging.getLogger(__name__)
BASE_DIR   = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def load_master(path: Path = None) -> pd.DataFrame:
    p = path or BASE_DIR / "data" / "processed" / "master_dataset.csv"
    if not p.exists():
        raise FileNotFoundError(f"Master dataset not found: {p}. Run feature_engineering.py first.")
    df = pd.read_csv(p, parse_dates=["date"])
    logger.info(f"Loaded master dataset: {df.shape}")
    return df


def split_data(df: pd.DataFrame, feature_cols: list, target: str = "aqi", test_size: float = 0.2):
    # Time-based split (no shuffle)
    df = df.sort_values("date")
    X = df[feature_cols].copy()
    y = df[target].copy()

    # Fill any remaining NaN
    X = X.fillna(X.median(numeric_only=True))

    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test


def compute_metrics(y_true, y_pred, name: str = "") -> dict:
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae  = mean_absolute_error(y_true, y_pred)
    r2   = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-6))) * 100
    metrics = dict(RMSE=round(rmse,4), MAE=round(mae,4), R2=round(r2,4), MAPE=round(mape,4))
    logger.info(f"[{name}] RMSE={rmse:.3f} MAE={mae:.3f} R²={r2:.4f} MAPE={mape:.2f}%")
    return metrics


def train_random_forest(X_train, y_train) -> RandomForestRegressor:
    logger.info("Training RandomForest …")
    model = RandomForestRegressor(
        n_estimators=200, max_depth=12, min_samples_leaf=3,
        n_jobs=-1, random_state=42
    )
    model.fit(X_train, y_train)
    return model


def train_xgboost(X_train, y_train) -> xgb.XGBRegressor:
    logger.info("Training XGBoost …")
    model = xgb.XGBRegressor(
        n_estimators=300, learning_rate=0.05, max_depth=6,
        subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1,
        random_state=42, n_jobs=-1, verbosity=0
    )
    model.fit(X_train, y_train,
              eval_set=[(X_train, y_train)],
              verbose=False)
    return model


def train_lightgbm(X_train, y_train) -> lgb.LGBMRegressor:
    logger.info("Training LightGBM …")
    model = lgb.LGBMRegressor(
        n_estimators=300, learning_rate=0.05, num_leaves=63,
        subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1,
        random_state=42, n_jobs=-1, verbosity=-1
    )
    model.fit(X_train, y_train)
    return model


def build_ensemble(rf, xgb_m, lgb_m):
    logger.info("Building ensemble …")
    ensemble = VotingRegressor(
        estimators=[("rf", rf), ("xgb", xgb_m), ("lgb", lgb_m)],
        weights=[1, 2, 2]
    )
    return ensemble


def cross_validate_model(model, X, y, name: str, cv: int = 5) -> dict:
    kf = KFold(n_splits=cv, shuffle=False)
    scores = cross_val_score(model, X, y, cv=kf, scoring="r2", n_jobs=-1)
    logger.info(f"[{name}] CV R² = {scores.mean():.4f} ± {scores.std():.4f}")
    return {"cv_r2_mean": round(scores.mean(), 4), "cv_r2_std": round(scores.std(), 4)}


def get_feature_importance(model, feature_cols: list) -> pd.DataFrame:
    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
    else:
        imp = np.zeros(len(feature_cols))
    fi = pd.DataFrame({"feature": feature_cols, "importance": imp})
    fi = fi.sort_values("importance", ascending=False).reset_index(drop=True)
    fi.to_csv(MODELS_DIR / "feature_importance.csv", index=False)
    return fi


def train_all(df: pd.DataFrame, feature_cols: list, target: str = "aqi") -> dict:
    X_train, X_test, y_train, y_test = split_data(df, feature_cols, target)

    rf  = train_random_forest(X_train, y_train)
    xgb_m = train_xgboost(X_train, y_train)
    lgb_m = train_lightgbm(X_train, y_train)

    # Evaluate each
    results = {}
    for name, model in [("RandomForest", rf), ("XGBoost", xgb_m), ("LightGBM", lgb_m)]:
        preds = model.predict(X_test)
        results[name] = compute_metrics(y_test, preds, name)
        cv = cross_validate_model(model, X_train, y_train, name)
        results[name].update(cv)
        joblib.dump(model, MODELS_DIR / f"{name.lower()}_model.pkl")

    # Ensemble
    ensemble = build_ensemble(rf, xgb_m, lgb_m)
    ensemble.fit(X_train, y_train)
    ens_preds = ensemble.predict(X_test)
    results["Ensemble"] = compute_metrics(y_test, ens_preds, "Ensemble")
    joblib.dump(ensemble, MODELS_DIR / "ensemble_model.pkl")

    # Feature importance from best single model (LightGBM)
    fi = get_feature_importance(lgb_m, feature_cols)
    logger.info(f"Top 5 features: {fi['feature'].head(5).tolist()}")

    # Save results
    with open(MODELS_DIR / "model_results.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info("\n=== Model Comparison ===")
    for m, r in results.items():
        logger.info(f"{m}: R²={r['R2']} RMSE={r['RMSE']} MAE={r['MAE']}")

    best = max(["RandomForest","XGBoost","LightGBM","Ensemble"], key=lambda m: results[m]["R2"])
    logger.info(f"Best model: {best} (R²={results[best]['R2']})")
    return results


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(Path(__file__).parent))
    from feature_engineering import FEATURE_COLS, TARGET_COL
    df = load_master()
    avail = [c for c in FEATURE_COLS if c in df.columns]
    results = train_all(df, avail, TARGET_COL)

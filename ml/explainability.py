"""
BharatAQI-X: Explainability Module
SHAP-based global and local explanations for the AQI prediction model.
"""
import logging, json
import numpy as np
import pandas as pd
import shap
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

logger = logging.getLogger(__name__)
BASE_DIR  = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
FIG_DIR    = BASE_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def load_model(name: str = "lightgbm_model"):
    path = MODELS_DIR / f"{name}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}. Run train_model.py first.")
    model = joblib.load(path)
    logger.info(f"Loaded model: {path}")
    return model


def compute_shap_values(model, X: pd.DataFrame) -> tuple:
    """Compute SHAP values using TreeExplainer."""
    logger.info(f"Computing SHAP values for {len(X)} samples …")
    try:
        explainer = shap.TreeExplainer(model)
    except Exception:
        explainer = shap.KernelExplainer(model.predict, X.sample(min(100, len(X))))
    shap_values = explainer(X)
    logger.info("SHAP computation complete")
    return explainer, shap_values


def shap_summary_plot(shap_values, X: pd.DataFrame, max_display: int = 20, save: bool = True):
    """SHAP summary beeswarm plot (global feature importance)."""
    fig, ax = plt.subplots(figsize=(10, 8))
    shap.summary_plot(shap_values, X, max_display=max_display, show=False)
    plt.title("SHAP Summary Plot – AQI Feature Importance", fontsize=14, fontweight="bold")
    plt.tight_layout()
    if save:
        out = FIG_DIR / "shap_summary.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        logger.info(f"Saved → {out}")
    plt.close()


def shap_bar_plot(shap_values, X: pd.DataFrame, max_display: int = 15, save: bool = True):
    """SHAP global bar plot (mean absolute SHAP)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    shap.plots.bar(shap_values, max_display=max_display, show=False)
    plt.title("SHAP Global Feature Importance (Mean |SHAP|)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save:
        out = FIG_DIR / "shap_bar.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        logger.info(f"Saved → {out}")
    plt.close()


def shap_waterfall_plot(shap_values, X: pd.DataFrame, idx: int = 0, save: bool = True):
    """SHAP waterfall plot for a single prediction (local explanation)."""
    fig, ax = plt.subplots(figsize=(10, 7))
    shap.plots.waterfall(shap_values[idx], show=False)
    plt.title(f"SHAP Waterfall – Sample #{idx} (Local Explanation)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save:
        out = FIG_DIR / f"shap_waterfall_{idx}.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        logger.info(f"Saved → {out}")
    plt.close()


def shap_dependence_plot(shap_values, X: pd.DataFrame, feature: str,
                          interaction: str = None, save: bool = True):
    """SHAP dependence plot for a given feature."""
    if feature not in X.columns:
        logger.warning(f"Feature '{feature}' not found in X.")
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    shap.dependence_plot(feature, shap_values.values, X,
                          interaction_index=interaction, show=False, ax=ax)
    ax.set_title(f"SHAP Dependence: {feature}", fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save:
        out = FIG_DIR / f"shap_dep_{feature}.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        logger.info(f"Saved → {out}")
    plt.close()


def get_global_importance(shap_values, feature_cols: list) -> pd.DataFrame:
    """Return DataFrame of mean |SHAP| per feature."""
    mean_abs = np.abs(shap_values.values).mean(axis=0)
    fi = pd.DataFrame({"feature": feature_cols, "mean_abs_shap": mean_abs})
    fi = fi.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
    fi.to_csv(FIG_DIR / "global_shap_importance.csv", index=False)
    return fi


def get_local_explanation(shap_values, X: pd.DataFrame, idx: int) -> dict:
    """Return local explanation for sample idx as a dict."""
    row_shap = shap_values.values[idx]
    base     = float(shap_values.base_values[idx])
    pred     = base + row_shap.sum()
    feature_contributions = {
        col: round(float(val), 4)
        for col, val in sorted(zip(X.columns, row_shap), key=lambda x: abs(x[1]), reverse=True)
    }
    return {
        "sample_index":    idx,
        "base_value":      round(base, 4),
        "predicted_aqi":   round(pred, 4),
        "top_drivers":     dict(list(feature_contributions.items())[:10]),
        "all_shap":        feature_contributions,
    }


def run_explainability(df: pd.DataFrame, feature_cols: list,
                        model_name: str = "lightgbm_model",
                        n_samples: int = 500) -> dict:
    """Full explainability pipeline."""
    logger.info("=== SHAP Explainability Pipeline ===")
    model = load_model(model_name)

    X = df[[c for c in feature_cols if c in df.columns]].fillna(0)
    # Use a sample for speed
    X_sample = X.sample(min(n_samples, len(X)), random_state=42).reset_index(drop=True)

    explainer, shap_values = compute_shap_values(model, X_sample)

    shap_summary_plot(shap_values, X_sample)
    shap_bar_plot(shap_values, X_sample)
    shap_waterfall_plot(shap_values, X_sample, idx=0)

    # Dependence plots for top features
    global_fi = get_global_importance(shap_values, list(X_sample.columns))
    for feat in global_fi["feature"].head(4).tolist():
        shap_dependence_plot(shap_values, X_sample, feat)

    # Local explanations for first 3 samples
    local_exps = [get_local_explanation(shap_values, X_sample, i) for i in range(3)]
    with open(FIG_DIR / "local_explanations.json", "w") as f:
        json.dump(local_exps, f, indent=2)

    return {
        "global_importance": global_fi,
        "local_explanations": local_exps,
        "shap_values": shap_values,
        "explainer": explainer,
        "X_sample": X_sample,
    }


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(Path(__file__).parent))
    from feature_engineering import FEATURE_COLS
    df = pd.read_csv(BASE_DIR / "data" / "processed" / "master_dataset.csv")
    result = run_explainability(df, FEATURE_COLS)
    print(result["global_importance"].head(10))

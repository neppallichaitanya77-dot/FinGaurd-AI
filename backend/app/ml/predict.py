"""Load the trained risk model and make predictions, with a rule-based
fallback when no trained model is available."""
import os
import pickle

import numpy as np

from app.ml.train import MODEL_PATH, train_model


def _default_model():
    """Deterministic rule-based fallback that does not require a pickled model."""
    return None


def ensure_model():
    if not os.path.exists(MODEL_PATH):
        try:
            train_model(save=True)
        except Exception:
            return None
    return MODEL_PATH


def _rule_based_probability(indicators: dict) -> float:
    """Deterministic fallback probability based on financial indicators."""
    utilization = float(indicators.get("credit_utilization", 0))
    dti = float(indicators.get("dti", 0))
    delay_freq = float(indicators.get("payment_delay_frequency", 0))
    consistency = float(indicators.get("repayment_consistency", 1.0))
    expense_trend = float(indicators.get("expense_trend", 0))

    p = (
        0.00
        + 0.30 * min(utilization / 100, 1.0)
        + 0.25 * min(dti / 100, 1.0)
        + 0.20 * delay_freq
        + 0.25 * max((1.0 - consistency), 0)
    )
    p += max(expense_trend, 0) / 500.0
    return float(np.clip(p, 0.0, 1.0))


def predict_distress_probability(indicators: dict) -> float:
    """Return distress probability in [0, 1]."""
    from app.ml.preprocess import build_feature_vector

    model_path = ensure_model()
    if model_path:
        try:
            with open(model_path, "rb") as f:
                bundle = pickle.load(f)
            model = bundle["model"]
            X = build_feature_vector(indicators)
            prob = float(model.predict_proba(X)[0][1])
            return min(max(prob, 0.0), 1.0)
        except Exception:
            pass
    return _rule_based_probability(indicators)

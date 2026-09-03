"""Train and persist an ML financial-distress risk model.

The model is trained on simulated/anonymized financial indicators. Both a
LogisticRegression and a RandomForest are trained so their performance can be
compared; the better model is persisted to the model directory.
"""
import os
import pickle
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from app.ml.preprocess import FEATURE_NAMES

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.pkl")


def _synthetic_dataset(n=6000, seed=42):
    """Generate a synthetic dataset with a known relationship to distress."""
    rng = np.random.default_rng(seed)
    dti = rng.uniform(5, 90, n)
    utilization = rng.uniform(5, 100, n)
    delay_freq = rng.uniform(0, 1, n)
    debt_growth = rng.uniform(-10, 40, n)
    expense_trend = rng.uniform(-20, 60, n)
    overdrafts = rng.integers(0, 8, n)
    consistency = rng.uniform(0, 1, n)

    X = np.column_stack(
        [dti, utilization, delay_freq, debt_growth, expense_trend, overdrafts, consistency]
    )

    # Distress probability grows with risk indicators
    score = (
        0.30 * (dti / 90)
        + 0.25 * (utilization / 100)
        + 0.20 * delay_freq
        + 0.10 * np.clip(debt_growth / 40, 0, 1)
        + 0.10 * np.clip(expense_trend / 60, 0, 1)
        + 0.05 * np.clip(overdrafts / 8, 0, 1)
        + 0.10 * (1 - consistency)
    )
    noise = rng.normal(0, 0.08, n)
    prob = np.clip(score + noise, 0, 1)
    y = (prob > 0.5).astype(int)
    return X, y


def train_model(save: bool = True):
    X, y = _synthetic_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=10, random_state=42, class_weight="balanced"
        ),
    }

    results = {}
    best_model = None
    best_auc = -1
    best_name = None

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_prob),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }
        results[name] = metrics
        if metrics["roc_auc"] > best_auc:
            best_auc = metrics["roc_auc"]
            best_model = model
            best_name = name

    if save:
        os.makedirs(MODEL_DIR, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(
                {"model": best_model, "feature_names": FEATURE_NAMES, "model_name": best_name},
                f,
            )

    return {"best_model": best_name, "results": results}

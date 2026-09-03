"""Model training / evaluation report generator."""
import json
import os

from app.ml.train import MODEL_DIR, train_model


def evaluate_and_report(output_dir: str = MODEL_DIR):
    """Train models and write a JSON evaluation report."""
    report = train_model(save=True)
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "evaluation_report.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return report

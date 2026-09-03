"""Feature engineering for the financial distress prediction pipeline."""
import numpy as np

FEATURE_NAMES = [
    "dti",
    "credit_utilization",
    "payment_delay_frequency",
    "debt_growth",
    "expense_trend",
    "overdraft_frequency",
    "repayment_consistency",
]


def build_feature_vector(indicators: dict) -> np.ndarray:
    """Convert indicator dict into a feature vector consistent with training."""
    return np.array(
        [
            float(indicators.get("dti", 0)),
            float(indicators.get("credit_utilization", 0)),
            float(indicators.get("payment_delay_frequency", 0)),
            float(indicators.get("debt_growth", 0)),
            float(indicators.get("expense_trend", 0)),
            float(indicators.get("overdraft_frequency", 0)),
            float(indicators.get("repayment_consistency", 1.0)),
        ],
        dtype=float,
    ).reshape(1, -1)

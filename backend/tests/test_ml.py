import os
import pytest
from app.ml.preprocess import build_feature_vector, FEATURE_NAMES
from app.ml.train import train_model, MODEL_PATH
from app.ml.predict import predict_distress_probability, _rule_based_probability


def test_feature_vector_shape_and_names():
    indicators = {
        "dti": 30.0,
        "credit_utilization": 45.0,
        "payment_delay_frequency": 0.05,
        "debt_growth": 5.0,
        "expense_trend": 10.0,
        "overdraft_frequency": 1,
        "repayment_consistency": 0.95,
    }
    vec = build_feature_vector(indicators)
    assert vec.shape == (1, len(FEATURE_NAMES))
    assert vec[0][0] == 30.0
    assert vec[0][1] == 45.0


def test_rule_based_fallback():
    low_risk = {
        "credit_utilization": 10.0,
        "dti": 15.0,
        "payment_delay_frequency": 0.0,
        "repayment_consistency": 1.0,
        "expense_trend": 0.0,
    }
    high_risk = {
        "credit_utilization": 95.0,
        "dti": 80.0,
        "payment_delay_frequency": 0.5,
        "repayment_consistency": 0.5,
        "expense_trend": 50.0,
    }
    p_low = _rule_based_probability(low_risk)
    p_high = _rule_based_probability(high_risk)
    assert 0.0 <= p_low <= 1.0
    assert 0.0 <= p_high <= 1.0
    assert p_high > p_low


def test_model_training_and_evaluation():
    output = train_model(save=True)
    assert "best_model" in output
    assert output["best_model"] in ["logistic_regression", "random_forest"]

    results = output["results"]
    for model_name in ["logistic_regression", "random_forest"]:
        metrics = results[model_name]
        assert metrics["accuracy"] >= 0.70, f"{model_name} accuracy too low: {metrics['accuracy']}"
        assert metrics["roc_auc"] >= 0.80, f"{model_name} ROC-AUC too low: {metrics['roc_auc']}"
        assert metrics["recall"] >= 0.70, f"{model_name} recall too low: {metrics['recall']}"
        assert "confusion_matrix" in metrics

    assert os.path.exists(MODEL_PATH)


def test_predict_distress_probability():
    indicators = {
        "dti": 50.0,
        "credit_utilization": 60.0,
        "payment_delay_frequency": 0.1,
        "debt_growth": 10.0,
        "expense_trend": 15.0,
        "overdraft_frequency": 1,
        "repayment_consistency": 0.9,
    }
    prob = predict_distress_probability(indicators)
    assert 0.0 <= prob <= 1.0

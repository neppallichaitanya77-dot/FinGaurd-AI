import pytest


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_dashboard_endpoint(client, auth_headers):
    res = client.get("/api/dashboard", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "health_score" in data
    assert "risk_score" in data
    assert "risk_level" in data
    assert "balance" in data
    assert "balance_chart" in data
    assert "alerts" in data
    assert "recommendations" in data


def test_financial_health_endpoint(client, auth_headers):
    res = client.get("/api/financial-health", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "health_score" in data or "financial_health_score" in data
    assert "health_status" in data or "financial_health_status" in data
    assert "positive_factors" in data or "key_positive_factors" in data
    assert "concerns" in data or "key_concerns" in data
    assert "balance" in data
    assert "balance_chart" in data


def test_risk_score_endpoint(client, auth_headers):
    res = client.get("/api/risk-score", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "risk_score" in data
    assert "risk_level" in data
    assert "probability" in data
    assert "risk_factors" in data


def test_alerts_lifecycle(client, auth_headers):
    # Get all alerts
    res = client.get("/api/alerts", headers=auth_headers)
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)
    if alerts:
        alert_id = alerts[0]["id"]
        # Mark as read
        mark_res = client.put(f"/api/alerts/{alert_id}/read", headers=auth_headers)
        assert mark_res.status_code == 200

        # Dismiss
        del_res = client.delete(f"/api/alerts/{alert_id}", headers=auth_headers)
        assert del_res.status_code == 200


def test_recommendations_lifecycle(client, auth_headers):
    res = client.get("/api/recommendations", headers=auth_headers)
    assert res.status_code == 200
    recs = res.json()
    assert isinstance(recs, list)
    if recs:
        rec_id = recs[0]["id"]
        accept_res = client.post(f"/api/recommendations/{rec_id}/accept", headers=auth_headers)
        assert accept_res.status_code == 200
        assert accept_res.json()["status"] == "accepted"


def test_transactions_endpoint(client, auth_headers):
    res = client.get("/api/transactions?page=1&page_size=5", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert "data" in body
    assert "total" in body
    assert len(body["data"]) <= 5

    # Filter by category or search
    search_res = client.get("/api/transactions?search=Salary", headers=auth_headers)
    assert search_res.status_code == 200


def test_loans_endpoint(client, auth_headers):
    res = client.get("/api/loans", headers=auth_headers)
    assert res.status_code == 200
    loans = res.json()
    assert isinstance(loans, list)
    assert len(loans) > 0
    first_loan = loans[0]
    assert "name" in first_loan
    assert "outstanding_amount" in first_loan or "outstanding" in first_loan
    assert "monthly_emi" in first_loan or "emi" in first_loan


def test_ai_assistant_chat_and_history(client, auth_headers):
    chat_payload = {"message": "Why is my credit utilization important?"}
    chat_res = client.post("/api/ai/chat", json=chat_payload, headers=auth_headers)
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert "response" in data
    assert "FinGuard AI provides supportive guidance" in data["response"]
    assert data["conversation_id"]
    assert data["status"] == "FALLBACK_RESPONSE"
    assert 2 <= len(data["suggested_questions"]) <= 4

    followup = client.post(
        "/api/ai/chat",
        json={
            "message": "How can I reduce it?",
            "conversation_id": data["conversation_id"],
            "previous_suggested_questions": data["suggested_questions"],
        },
        headers=auth_headers,
    )
    assert followup.status_code == 200
    followup_data = followup.json()
    assert 2 <= len(followup_data["suggested_questions"]) <= 4
    assert set(followup_data["suggested_questions"]).isdisjoint(data["suggested_questions"])

    # Check history
    hist_res = client.get("/api/ai/history", headers=auth_headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert isinstance(history, list)
    assert any(h["content"] == chat_payload["message"] for h in history)


def test_scenario_simulator_dynamic_response(client, auth_headers):
    healthy_scenario = {
        "monthly_income": 90000,
        "monthly_expenses": 35000,
        "outstanding_debt": 40000,
        "credit_utilization": 20,
        "upcoming_emi": 3500,
        "payment_delays": 0,
    }
    distressed_scenario = {
        "monthly_income": 35000,
        "monthly_expenses": 32000,
        "outstanding_debt": 350000,
        "credit_utilization": 88,
        "upcoming_emi": 15000,
        "payment_delays": 3,
    }

    res_healthy = client.post("/api/scenario/analyze", json=healthy_scenario, headers=auth_headers)
    assert res_healthy.status_code == 200
    healthy_data = res_healthy.json()

    res_distressed = client.post("/api/scenario/analyze", json=distressed_scenario, headers=auth_headers)
    assert res_distressed.status_code == 200
    distressed_data = res_distressed.json()

    # Verify that results change logically:
    assert distressed_data["risk_score"] > healthy_data["risk_score"]
    assert distressed_data["financial_health_score"] < healthy_data["financial_health_score"]
    assert len(distressed_data["risk_factors"]) > len(healthy_data["risk_factors"])

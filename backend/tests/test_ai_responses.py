from app.services.llm_service import fallback_explanation


CONTEXT = {
    "risk_score": 71,
    "risk_level": "HIGH",
    "health_score": 29,
    "credit_utilization": 65,
    "balance_trend": "DECLINING",
    "upcoming_emi": 8500,
    "monthly_income": 45000,
    "total_debt": 120000,
    "payment_delays": 1,
    "expense_trend": 12.5,
    "risk_factors": [{"name": "Credit Utilization", "value": "65%"}],
    "conversation": [],
}


def test_fallback_answers_exact_questions_differently():
    questions = [
        "Why is my risk score high?",
        "How can I reduce my debt?",
        "What is credit utilization?",
        "How can I manage my upcoming EMI?",
        "How can I reduce my monthly expenses?",
        "Why is my financial health score low?",
        "What happens if my expenses increase?",
    ]
    answers = [fallback_explanation(question, CONTEXT) for question in questions]

    assert len(set(answers)) == len(questions)
    assert "71/100" in answers[0]
    assert "120,000" in answers[1]
    assert "percentage" in answers[2]
    assert "8,500" in answers[3]
    assert "12.5%" in answers[4]
    assert "29/100" in answers[5]
    assert "expense" in answers[6].lower()


def test_fallback_uses_prior_conversation_for_pronouns():
    context = {**CONTEXT, "conversation": [{"role": "user", "content": "Why is my risk score high?"}]}
    answer = fallback_explanation("How can I improve it?", context)

    assert "71/100" in answer
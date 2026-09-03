from app.services.llm_service import generate_followup_questions


def test_followups_are_topic_aware_and_deduplicated():
    context = {
        "risk_level": "HIGH",
        "conversation": [],
    }
    questions = generate_followup_questions(
        "Why is my credit utilization high?",
        "Your credit utilization is an important risk indicator.",
        context,
    )

    assert 2 <= len(questions) <= 4
    assert any("credit" in question.lower() or "utilization" in question.lower() for question in questions)

    next_questions = generate_followup_questions(
        "How can I reduce it?",
        "Paying down balances can reduce credit utilization.",
        context,
        questions,
    )
    assert 2 <= len(next_questions) <= 4
    assert set(next_questions).isdisjoint(questions)


def test_followups_change_for_loan_and_budget_topics():
    context = {"risk_level": "LOW", "conversation": []}
    loan_questions = generate_followup_questions(
        "I am worried about my upcoming EMI.", "Review your upcoming EMI and cash flow.", context
    )
    budget_questions = generate_followup_questions(
        "How can I reduce my expenses?", "A monthly budget can help organize spending.", context
    )

    assert any("emi" in question.lower() or "loan" in question.lower() for question in loan_questions)
    assert any("expense" in question.lower() or "budget" in question.lower() for question in budget_questions)
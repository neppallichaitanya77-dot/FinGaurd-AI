"""LLM + NLP service for the AI financial assistant.

Uses an external LLM API when configured. When no API key is available it falls
back to a safe, deterministic explanation engine built from the customer's
actual financial context. This guarantees the application never crashes when
the LLM API is unavailable.
"""
import json
from typing import Dict

from app.core.config import get_settings

settings = get_settings()

SAFETY_DISCLAIMER = (
    "FinGuard AI provides supportive guidance, not financial advice. "
    "Please consult a licensed financial advisor for major financial decisions."
)


def _context_prompt(user_question: str, context: Dict) -> str:
    return f"""
You are FinGuard AI, a supportive financial wellness assistant. You help people
understand their financial situation, explain risk scores and indicators in
simple language, and suggest supportive, optional actions. You never make
unsupported financial claims, never claim to be a licensed advisor, and never
make irreversible financial decisions on behalf of the user.

Use ONLY the following customer context. Never invent financial figures.

Customer context (JSON):
{json.dumps(context, indent=2)}

The customer asks:
{user_question}

Provide a clear, empathetic, and concise answer (max 200 words). End with the
following disclaimer exactly:
{SAFETY_DISCLAIMER}
"""


def call_llm(user_question: str, context: Dict) -> str:
    """Call the configured LLM provider. Raises on failure."""
    if not settings.LLM_API_KEY or not settings.LLM_ENABLED:
        raise RuntimeError("LLM not configured")

    import urllib.request

    provider = _detect_provider(settings.LLM_API_BASE_URL)
    endpoint = f"{settings.LLM_API_BASE_URL}/chat/completions"
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": _context_prompt(user_question, context)},
            {"role": "user", "content": user_question},
        ],
        "temperature": 0.4,
        "max_tokens": 400,
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"]


def _detect_provider(base_url: str) -> str:
    if "openai" in base_url:
        return "openai"
    if "anthropic" in base_url:
        return "anthropic"
    return "openai-compatible"


def fallback_explanation(user_question: str, context: Dict) -> str:
    """Deterministic explanation engine used when no LLM is available."""
    q = user_question.lower()
    risk_score = context.get("risk_score", 0)
    risk_level = context.get("risk_level", "LOW")
    utilization = context.get("credit_utilization", 0)
    balance_trend = context.get("balance_trend", "STABLE")
    upcoming_emi = context.get("upcoming_emi", 0)
    health = context.get("health_score", 0)
    factors = context.get("risk_factors", [])

    factor_text = ", ".join(f["name"] for f in factors) if factors else "no major factors"

    if "risk" in q and ("high" in q or "why" in q or "score" in q):
        return (
            f"Your risk level is currently {risk_level} with a score of {risk_score}/100. "
            f"This is primarily influenced by your financial indicators: {factor_text}. "
            "These are early-warning signals, not a judgment. Small, consistent changes can "
            "meaningfully improve your position over time. " + SAFETY_DISCLAIMER
        )

    if "debt" in q and ("reduce" in q or "lower" in q):
        return (
            "To reduce debt, consider: 1) Prioritizing high-interest debt first, "
            "2) Avoiding new debt while repaying, 3) Consolidating multiple loans, "
            "4) Setting up automatic payments to avoid missed EMIs, and "
            "5) Reviewing your budget to free up repayment capacity. " + SAFETY_DISCLAIMER
        )

    if "warning" in q or "alert" in q or "why did i receive" in q:
        return (
            "You received an early-warning alert because one or more of your financial "
            "indicators moved in a concerning direction — for example, rising credit "
            "utilization, a declining balance, or an upcoming EMI. These alerts exist to "
            "help you act early, when there is still time to make adjustments. " + SAFETY_DISCLAIMER
        )

    if "emi" in q.lower():
        return (
            f"Your next EMI obligation is ₹{upcoming_emi:,.0f}. To manage it comfortably, "
            "review your available balance and upcoming cash flow. Consider setting aside "
            "the payment amount early and reviewing discretionary spending in the weeks "
            "around the due date. " + SAFETY_DISCLAIMER
        )

    if "health" in q or "score" in q:
        return (
            f"Your financial health score is {health}/100. This reflects your current "
            "balance, income, expenses, debt, and utilization patterns. Your key indicators "
            f"are: credit utilization {utilization:.0f}% and a balance trend of {balance_trend}. "
            "Improvements in these areas typically raise your score over time. " + SAFETY_DISCLAIMER
        )

    if "balance" in q or "income" in q or "expense" in q:
        return (
            f"Your balance trend is currently {balance_trend}, with credit utilization at "
            f"{utilization:.0f}%. Monitoring income versus expenses regularly helps keep "
            "your finances on track. " + SAFETY_DISCLAIMER
        )

    return (
        "I can help you understand your financial situation, risk indicators, and "
        "personalized suggestions. Some helpful questions: Why is my risk score what it is? "
        "How can I reduce my debt? How can I manage my upcoming EMI? " + SAFETY_DISCLAIMER
    )


def generate_response(user_question: str, context: Dict) -> str:
    """High-level entry point: try the LLM, fall back to the explanation engine."""
    try:
        if settings.LLM_ENABLED and settings.LLM_API_KEY:
            return call_llm(user_question, context)
    except Exception:
        pass
    return fallback_explanation(user_question, context)

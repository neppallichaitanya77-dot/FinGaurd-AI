"""LLM + NLP service for the AI financial assistant.

Uses an external LLM API when configured. When no API key is available it falls
back to a safe, deterministic explanation engine built from the customer's
actual financial context. This guarantees the application never crashes when
the LLM API is unavailable.
"""
import json
import logging
import re
from typing import Dict, List, Optional

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

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


def _normalise_question(question: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", question.lower()).strip()


def _topic_for_question(user_question: str, assistant_response: str, context: Dict) -> str:
    question = f"{user_question} {assistant_response}".lower()
    if any(word in question for word in ("emi", "loan", "repay", "installment")):
        return "loan"
    if any(word in question for word in ("budget", "expense", "spend", "saving")):
        return "budget"
    if any(word in question for word in ("credit", "utilization", "card")):
        return "credit"
    if any(word in question for word in ("risk", "score", "health", "factor")):
        return "risk"
    if context.get("risk_level") in {"HIGH", "CRITICAL"}:
        return "risk"
    return "general"


def _fallback_question_sets(topic: str, context: Dict) -> List[str]:
    sets = {
        "risk": [
            "What factor is increasing my risk the most?",
            "How can I improve my financial health?",
            "How is my risk score calculated?",
            "What would lower my risk level?",
            "Can you explain my biggest risk factor?",
            "What should I focus on first?",
        ],
        "credit": [
            "How can I reduce my credit utilization?",
            "How much should I pay toward my balance?",
            "What credit card spending should I review first?",
            "Will lowering utilization improve my risk score?",
            "How does credit utilization affect my health score?",
            "Can you help me make a credit repayment plan?",
        ],
        "loan": [
            "How can I plan my upcoming EMI payments?",
            "What should I consider before making an extra payment?",
            "Can you help me review my loan obligations?",
            "How can I prepare for my next EMI?",
            "What would make my EMI easier to manage?",
            "How do loan payments affect my financial health?",
        ],
        "budget": [
            "Which expenses should I review first?",
            "Can you help me create a monthly budget?",
            "How can I increase my monthly savings?",
            "How should I divide my income across expenses?",
            "What spending categories should I track?",
            "What happens if I reduce my expenses by 10%?",
        ],
        "general": [
            "What should I focus on first?",
            "Can you explain my main financial indicators?",
            "What happens if my expenses increase?",
            "How can I prepare for upcoming payments?",
            "Which financial trend should I monitor next?",
            "Can you help me explore a different scenario?",
        ],
    }
    return sets[topic]


def generate_followup_questions(
    user_question: str,
    assistant_response: str,
    context: Dict,
    previous_questions: Optional[List[str]] = None,
) -> List[str]:
    """Generate three relevant, deduplicated follow-ups without inventing facts."""
    previous = previous_questions or []
    blocked = {_normalise_question(user_question)}
    blocked.update(_normalise_question(item) for item in previous)
    blocked.update(
        _normalise_question(message.get("content", ""))
        for message in context.get("conversation", [])
    )
    questions = []
    candidates = _llm_followup_questions(user_question, assistant_response, context) or _fallback_question_sets(
        _topic_for_question(user_question, assistant_response, context), context
    )
    for question in candidates:
        normalised = _normalise_question(question)
        if normalised and normalised not in blocked:
            questions.append(question)
            blocked.add(normalised)
        if len(questions) == 3:
            break
    return questions


def _llm_followup_questions(
    user_question: str, assistant_response: str, context: Dict
) -> List[str]:
    """Request structured follow-ups when an LLM is configured; otherwise return none."""
    if not settings.LLM_ENABLED or not settings.LLM_API_KEY:
        return []
    try:
        import urllib.request

        prompt = {
            "user_question": user_question,
            "assistant_response": assistant_response,
            "financial_context": context,
        }
        request = urllib.request.Request(
            f"{settings.LLM_API_BASE_URL}/chat/completions",
            data=json.dumps({
                "model": settings.LLM_MODEL,
                "messages": [{
                    "role": "system",
                    "content": (
                        "You are a responsible financial-support assistant. Return JSON only "
                        "with a suggested_questions array containing 3 concise, practical "
                        "questions. Use only the supplied context, do not repeat the current "
                        "question, and do not make financial decisions."
                    ),
                }, {"role": "user", "content": json.dumps(prompt)}],
                "temperature": 0.3,
                "max_tokens": 180,
            }).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
            },
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            content = json.loads(response.read().decode("utf-8"))["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        questions = parsed.get("suggested_questions", [])
        if isinstance(questions, list):
            return [question.strip() for question in questions if isinstance(question, str) and question.strip()][:4]
    except Exception:
        return []
    return []


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
    total_debt = context.get("total_debt", 0)
    payment_delays = context.get("payment_delays", 0)
    expense_trend = context.get("expense_trend", 0)
    factors = context.get("risk_factors", [])
    conversation = context.get("conversation", [])

    factor_text = ", ".join(f["name"] for f in factors) if factors else "no major factors"

    if any(word in q for word in ("it", "that", "this")) and conversation:
        prior_text = " ".join(message.get("content", "") for message in conversation[-4:]).lower()
        if any(word in prior_text for word in ("risk", "score", "health")):
            q += " risk score"

    if "health" in q:
        return (
            f"Your financial health score is {health}/100. It reflects your balance, income, expenses, debt, "
            f"credit utilization, and payment behavior. The current risk level is {risk_level}, with utilization "
            f"at {utilization:.0f}% and a {balance_trend.lower()} balance trend. Reviewing the factors that are "
            "pulling the score down can help you choose practical next steps. " + SAFETY_DISCLAIMER
        )

    if "risk" in q and ("high" in q or "why" in q or "score" in q):
        return (
            f"Your risk level is currently {risk_level} with a score of {risk_score}/100. "
            f"This is primarily influenced by your financial indicators: {factor_text}. "
            "These are early-warning signals, not a judgment. Small, consistent changes can "
            "meaningfully improve your position over time. " + SAFETY_DISCLAIMER
        )

    if "credit utilization" in q or "what is credit utilization" in q:
        return (
            f"Credit utilization is the percentage of your available revolving credit that you are using. "
            f"Your current utilization is {utilization:.0f}%. Lowering balances or avoiding unnecessary new charges "
            "can reduce it; review the statement balances and payment dates that affect the calculation. "
            + SAFETY_DISCLAIMER
        )

    if "debt" in q:
        return (
            f"Your tracked outstanding debt is ₹{total_debt:,.0f}. To reduce it, list each obligation and its interest rate, "
            "prioritize the highest-cost balance while keeping required payments current, and direct any affordable extra "
            "amount toward that balance. Review your budget first so the plan remains sustainable. " + SAFETY_DISCLAIMER
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

    if "score" in q:
        return (
            f"Your financial health score is {health}/100. This reflects your current "
            "balance, income, expenses, debt, and utilization patterns. Your key indicators "
            f"are: credit utilization {utilization:.0f}% and a balance trend of {balance_trend}. "
            "Improvements in these areas typically raise your score over time. " + SAFETY_DISCLAIMER
        )

    if "what happens" in q and ("expense" in q or "spend" in q):
        return (
            f"If your expenses increase while monthly income stays at ₹{context.get('monthly_income', 0):,.0f}, "
            "the amount available for savings and required payments will shrink. Because your recent expense trend is "
            f"{expense_trend:+.1f}% and your balance trend is {balance_trend.lower()}, review the new spending first, "
            "protect essential payments, and test the change in the scenario simulator before committing to it. "
            + SAFETY_DISCLAIMER
        )

    if "budget" in q or "expense" in q or "spend" in q or "saving" in q:
        return (
            f"Your tracked monthly income is ₹{context.get('monthly_income', 0):,.0f}, and your recent expense trend is "
            f"{expense_trend:+.1f}%. Start by grouping recent spending into needs, debt payments, and discretionary items. "
            "Set a realistic limit for discretionary spending and review it weekly while protecting required payments. "
            + SAFETY_DISCLAIMER
        )

    return (
        f"I can help with that question. Your current risk level is {risk_level}, your balance trend is "
        f"{balance_trend.lower()}, and you have {payment_delays} recorded payment delay(s). "
        "Please ask about a specific score, balance, debt, payment, expense, or financial concept so I can relate the explanation "
        "to the information available. " + SAFETY_DISCLAIMER
    )


def generate_response(user_question: str, context: Dict) -> str:
    """High-level entry point: try the LLM, fall back to the explanation engine."""
    return generate_response_details(user_question, context)["response"]


def generate_response_details(user_question: str, context: Dict) -> Dict[str, str]:
    """Return the answer and an explicit provider status for development diagnostics."""
    try:
        if settings.LLM_ENABLED and settings.LLM_API_KEY:
            response = call_llm(user_question, context)
            logger.info("AI response status=LLM_SUCCESS")
            return {"response": response, "source": "llm", "status": "LLM_SUCCESS"}
        logger.info("AI response status=LLM_UNAVAILABLE reason=not_configured")
    except Exception:
        logger.exception("LLM request failed; using contextual fallback")
    return {
        "response": fallback_explanation(user_question, context),
        "source": "fallback",
        "status": "FALLBACK_RESPONSE",
    }

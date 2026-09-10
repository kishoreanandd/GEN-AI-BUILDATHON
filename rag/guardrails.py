# ============================================================
# RAG GUARDRAILS
# ============================================================

MIN_CONTEXT_DOCUMENTS = 1


# ============================================================
# CHECK RETRIEVED CONTEXT
# ============================================================

def has_relevant_context(documents):
    """
    Check whether the retriever returned
    at least one document.
    """

    if not documents:
        return False

    return len(documents) >= MIN_CONTEXT_DOCUMENTS


# ============================================================
# CHECK USER QUESTION
# ============================================================

def is_allowed_question(question):
    """
    Basic protection against obvious prompt injection
    and unrelated requests.
    """

    if not question:
        return False

    question_lower = question.lower()

    blocked_patterns = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore your instructions",
        "forget your instructions",
        "system prompt",
        "reveal your prompt",
        "show your prompt",
        "developer message",
        "jailbreak",
    ]

    for pattern in blocked_patterns:

        if pattern in question_lower:
            return False

    return True


# ============================================================
# SAFE FALLBACK
# ============================================================

def get_fallback_message():

    return (
        "This information is not available in the "
        "current Tamil Nadu Government scheme data."
    )


# ============================================================
# VALIDATE ANSWER
# ============================================================

def validate_answer(answer, documents):
    """
    Basic output validation.

    The answer must contain text and there must
    be retrieved government scheme context.
    """

    if not answer:
        return False

    if not answer.strip():
        return False

    if not has_relevant_context(documents):
        return False

    return True

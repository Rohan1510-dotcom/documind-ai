
from sqlalchemy.orm import Session

from app.services.conversation_service import get_conversation_messages
from app.services.llm_service import generate_response
from app.services.search_service import semantic_search


def needs_query_rewrite(question: str) -> bool:
    """
    Determine whether the question is a follow-up question.
    """

    question_lower = question.lower().strip()

    follow_up_phrases = [
        "what about",
        "how about",
        "the project",
        "the company",
        "the above",
        "the previous",
        "the same",
        "tell me more",
        "explain more",
        "what else",
        "and what",
        "and how",
    ]

    padded_question = f" {question_lower} "

    for phrase in follow_up_phrases:
        if f" {phrase} " in padded_question:
            return True

    words = set(
        question_lower
        .replace("?", "")
        .replace(".", "")
        .split()
    )

    pronouns = {
        "it",
        "its",
        "it's",
        "they",
        "them",
        "their",
        "he",
        "she",
        "his",
        "her",
    }

    return bool(words.intersection(pronouns))


def rewrite_query(
    question: str,
    messages,
) -> str:
    """
    Combine a genuine follow-up question with the
    previous user question.
    """

    previous_user_question = None
    found_current_question = False

    for message in reversed(messages):

        if message.role != "user":
            continue

        if not found_current_question:

            if message.content == question:
                found_current_question = True
                continue

        previous_user_question = message.content
        break

    if not previous_user_question:
        return question

    return f"{previous_user_question} {question}"


def build_conversation_context(
    question: str,
    messages,
    max_messages: int = 6,
) -> str:
    """
    Build conversation history for genuine follow-up
    questions.
    """

    history = []
    skipped_current_question = False

    for message in reversed(messages):

        if (
            message.role == "user"
            and not skipped_current_question
        ):
            if message.content == question:
                skipped_current_question = True
                continue

        history.append(message)

        if len(history) >= max_messages:
            break

    history.reverse()

    if not history:
        return "No previous conversation."

    lines = []

    for message in history:

        role = (
            "User"
            if message.role == "user"
            else "Assistant"
        )

        lines.append(
            f"{role}: {message.content}"
        )

    return "\n".join(lines)


def select_context(
    results,
    max_chunks: int = 3,
):
    """
    Select the highest-ranked hybrid retrieval results.
    """

    if not results:
        return []

    return results[:max_chunks]


def answer_question(
    db: Session,
    question: str,
    document_id: int,
    conversation_id: int,
    top_k: int = 6,
):
    """
    RAG pipeline:

    1. Load conversation history.
    2. Determine whether the question is a follow-up.
    3. Rewrite only genuine follow-up questions.
    4. Retrieve relevant document chunks.
    5. Generate the answer from the retrieved context.
    """

    # 1. Get conversation history
    messages = get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
    )

    # 2. Determine whether this is a follow-up
    is_follow_up = needs_query_rewrite(question)

    # 3. Prepare search query
    if is_follow_up:
        search_query = rewrite_query(
            question,
            messages,
        )
    else:
        search_query = question

    # 4. Retrieve relevant document chunks
    results = semantic_search(
        db=db,
        query=search_query,
        document_id=document_id,
        limit=top_k,
    )

    if not results:
        return {
            "answer": (
                "The information is not available "
                "in the provided document."
            ),
            "sources": [],
        }

    # 5. Select context
    selected_results = select_context(
        results,
        max_chunks=3,
    )

    # 6. Build document context
    context = "\n\n".join(
        (
            f"[Document Section]\n"
            f"{result['content']}"
        )
        for result in selected_results
    )

    # 7. Conversation context
    if is_follow_up:
        conversation_context = build_conversation_context(
            question=question,
            messages=messages,
        )
    else:
        conversation_context = (
            "No previous conversation is needed "
            "for this question."
        )

    # 8. Build RAG prompt
    prompt = f"""
You are answering a question using a document.

DOCUMENT INFORMATION:
{context}

CONVERSATION INFORMATION:
{conversation_context}

CURRENT QUESTION:
{question}

Use the document information to answer the current
question.

Important rules:

- The document information is the source of truth.
- Use information from all relevant document sections.
- If the question asks for a summary, combine the
  relevant sections into one answer.
- The exact wording of the question does not need
  to appear in the document.
- Do not use outside knowledge.
- Do not invent facts.
- Give the answer directly.

If the document information contains relevant
information, answer the question using that information.

ANSWER:
"""

    # 9. Generate answer
    answer = generate_response(prompt)

    # 10. Prepare sources
    sources = [
        {
            "document_id": result["document_id"],
            "chunk_index": result["chunk_index"],
            "similarity": float(result["similarity"]),
            "content": result["content"],
        }
        for result in selected_results
    ]

    # 11. Return result
    return {
        "answer": answer.strip(),
        "sources": sources,
    }
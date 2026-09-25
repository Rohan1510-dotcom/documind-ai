
from types import SimpleNamespace

from app.services.rag_service import (
    needs_query_rewrite,
    rewrite_query,
    select_context,
)


def test_independent_question_is_not_follow_up():
    question = "Summarize the projects in this document."

    assert needs_query_rewrite(question) is False


def test_follow_up_question_is_detected():
    question = "What about the other project?"

    assert needs_query_rewrite(question) is True


def test_pronoun_follow_up_is_detected():
    question = "What technologies were used in it?"

    assert needs_query_rewrite(question) is True


def test_rewrite_query_uses_previous_user_question():
    messages = [
        SimpleNamespace(
            role="user",
            content="Explain VisionMatch AI.",
        ),
        SimpleNamespace(
            role="assistant",
            content="It is a visual product search engine.",
        ),
    ]

    question = "What technologies were used in it?"

    result = rewrite_query(question, messages)

    assert result == (
        "Explain VisionMatch AI. "
        "What technologies were used in it?"
    )


def test_rewrite_query_without_history_returns_original():
    question = "What technologies were used in it?"

    assert rewrite_query(question, []) == question


def test_select_context_returns_top_three_chunks():
    results = [
        {"chunk_index": 5, "similarity": 0.9},
        {"chunk_index": 4, "similarity": 0.8},
        {"chunk_index": 2, "similarity": 0.7},
        {"chunk_index": 1, "similarity": 0.6},
    ]

    selected = select_context(results, max_chunks=3)

    assert len(selected) == 3
    assert [
        item["chunk_index"] for item in selected
    ] == [5, 4, 2]


def test_select_context_returns_empty_list_for_no_results():
    assert select_context([]) == []
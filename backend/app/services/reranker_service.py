from sentence_transformers import CrossEncoder


# Cross-encoder model used for document reranking.
# It evaluates the query and document together.
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker = None


def get_reranker():
    """
    Load the reranker model once and reuse it.
    """

    global _reranker

    if _reranker is None:
        print("Loading reranker model...")
        _reranker = CrossEncoder(MODEL_NAME)
        print("Reranker model loaded.")

    return _reranker


def rerank_results(
    query: str,
    results: list,
    top_k: int = 3,
) -> list:
    """
    Rerank retrieved document chunks using a cross-encoder.

    Args:
        query: The user's standalone search query.
        results: Results returned by semantic search.
        top_k: Number of results to return after reranking.

    Returns:
        Reranked document chunks.
    """

    if not results:
        return []

    reranker = get_reranker()

    # Create (query, document) pairs
    pairs = [
        (query, result["content"])
        for result in results
    ]

    # Generate relevance scores
    scores = reranker.predict(pairs)

    # Attach reranking score to each result
    reranked_results = []

    for result, score in zip(results, scores):
        result = dict(result)

        result["rerank_score"] = float(score)

        reranked_results.append(result)

    # Sort by reranking score
    reranked_results.sort(
        key=lambda x: x["rerank_score"],
        reverse=True,
    )

    return reranked_results[:top_k]
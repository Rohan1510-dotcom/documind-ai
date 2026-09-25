import re

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.embedding_service import generate_embedding


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "about",
    "be",
    "by",
    "can",
    "could",
    "do",
    "does",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "please",
    "show",
    "summarize",
    "tell",
    "the",
    "this",
    "to",
    "was",
    "what",
    "were",
    "which",
    "with",
    "would",
    "you",
}


def tokenize(text_value: str) -> set[str]:
    """
    Convert text into normalized terms and remove
    common stop words.
    """

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text_value.lower(),
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 1
    }


def lexical_similarity(
    query: str,
    content: str,
) -> float:
    """
    Calculate lexical overlap between the query
    and a document chunk.

    Score:
        number of query terms found in chunk
        -----------------------------------
        number of query terms
    """

    query_terms = tokenize(query)
    content_terms = tokenize(content)

    if not query_terms or not content_terms:
        return 0.0

    overlap = query_terms.intersection(
        content_terms
    )

    return len(overlap) / len(query_terms)


def semantic_search(
    db: Session,
    query: str,
    limit: int = 3,
    document_id: int | None = None,
):
    """
    Hybrid retrieval.

    Step 1:
        Retrieve a broad candidate pool using pgvector
        semantic similarity.

    Step 2:
        Calculate lexical overlap for every candidate.

    Step 3:
        Combine semantic and lexical scores.

    Step 4:
        Return the highest-ranked hybrid results.
    """

    # --------------------------------------------------
    # 1. Generate query embedding
    # --------------------------------------------------

    query_embedding = generate_embedding(query)

    embedding_string = "[" + ",".join(
        str(value)
        for value in query_embedding
    ) + "]"

    # --------------------------------------------------
    # 2. Retrieve a broad candidate pool
    # --------------------------------------------------

    # We intentionally retrieve more than the final
    # requested number so lexical matching has a chance
    # to promote relevant chunks.
    candidate_limit = max(
        limit * 3,
        10,
    )

    if document_id is not None:

        sql = text(
            """
            SELECT
                id,
                document_id,
                chunk_index,
                content,
                1 - (
                    embedding <=> CAST(
                        :query_embedding AS vector
                    )
                ) AS similarity
            FROM document_chunks
            WHERE
                embedding IS NOT NULL
                AND document_id = :document_id
            ORDER BY embedding <=> CAST(
                :query_embedding AS vector
            )
            LIMIT :limit
            """
        )

        result = db.execute(
            sql,
            {
                "query_embedding": embedding_string,
                "document_id": document_id,
                "limit": candidate_limit,
            },
        )

    else:

        sql = text(
            """
            SELECT
                id,
                document_id,
                chunk_index,
                content,
                1 - (
                    embedding <=> CAST(
                        :query_embedding AS vector
                    )
                ) AS similarity
            FROM document_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> CAST(
                :query_embedding AS vector
            )
            LIMIT :limit
            """
        )

        result = db.execute(
            sql,
            {
                "query_embedding": embedding_string,
                "limit": candidate_limit,
            },
        )

    candidates = list(
        result.mappings().all()
    )

    if not candidates:
        return []

    # --------------------------------------------------
    # 3. Calculate hybrid relevance
    # --------------------------------------------------

    scored_candidates = []

    for candidate in candidates:

        semantic_score = float(
            candidate["similarity"]
        )

        lexical_score = lexical_similarity(
            query,
            candidate["content"],
        )

        # Semantic similarity remains the primary signal.
        #
        # Lexical similarity provides an additional signal
        # when the actual words from the question occur
        # inside the document.
        hybrid_score = (
            semantic_score * 0.7
            + lexical_score * 0.3
        )

        scored_candidates.append(
            {
                "id": candidate["id"],
                "document_id": candidate["document_id"],
                "chunk_index": candidate["chunk_index"],
                "content": candidate["content"],
                "similarity": semantic_score,
                "lexical_similarity": lexical_score,
                "hybrid_score": hybrid_score,
            }
        )

    # --------------------------------------------------
    # 4. Sort by hybrid score
    # --------------------------------------------------

    scored_candidates.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True,
    )

    # --------------------------------------------------
    # 5. Return final results
    # --------------------------------------------------

    return scored_candidates[:limit]
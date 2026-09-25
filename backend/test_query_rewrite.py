from app.db.database import SessionLocal
from app.services.rag_service import rewrite_query
from app.services.search_service import semantic_search


def main():
    db = SessionLocal()

    queries = [
        "What projects demonstrate the candidate's machine learning experience?",
        "What technologies were used in VisionMatch AI?",
        "Where did the candidate complete their B.Tech?",
        "What experience does the candidate have with LLMs?",
    ]

    try:
        for question in queries:

            print("\n" + "=" * 80)
            print("ORIGINAL QUERY:")
            print(question)

            # For this experiment there is no conversation history.
            rewritten_query = rewrite_query(
                question=question,
                conversation_history="",
            )

            print("\nREWRITTEN QUERY:")
            print(rewritten_query)

            results = semantic_search(
                db=db,
                query=rewritten_query,
                limit=5,
                document_id=29,
            )

            print("\n" + "-" * 80)
            print("SEARCH RESULTS USING REWRITTEN QUERY")
            print("-" * 80)

            for rank, result in enumerate(results, start=1):

                print(
                    f"\nRank {rank}"
                    f" | Chunk {result['chunk_index']}"
                    f" | Similarity: {result['similarity']:.4f}"
                )

                print(result["content"][:500])

    finally:
        db.close()


if __name__ == "__main__":
    main()
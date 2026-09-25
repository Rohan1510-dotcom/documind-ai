from app.db.database import SessionLocal
from app.services.search_service import semantic_search
from app.services.reranker_service import rerank_results


def main():
    db = SessionLocal()

    queries = [
        "What projects demonstrate the candidate's machine learning experience?",
        "What technologies were used in VisionMatch AI?",
        "Where did the candidate complete their B.Tech?",
        "What experience does the candidate have with LLMs?",
    ]

    try:
        for query in queries:

            print("\n" + "=" * 80)
            print("QUERY:", query)

            results = semantic_search(
                db=db,
                query=query,
                limit=15,
                document_id=29,
            )

            print("\n" + "-" * 80)
            print("VECTOR SEARCH RESULTS")
            print("-" * 80)

            for rank, result in enumerate(results, start=1):

                print(
                    f"\nRank {rank}"
                    f" | Chunk {result['chunk_index']}"
                    f" | Similarity: {result['similarity']:.4f}"
                )

                print(result["content"][:500])

            reranked = rerank_results(
                query=query,
                results=results,
                top_k=5,
            )

            print("\n" + "-" * 80)
            print("RERANKED RESULTS")
            print("-" * 80)

            for rank, result in enumerate(
                reranked,
                start=1,
            ):

                print(
                    f"\nRank {rank}"
                    f" | Chunk {result['chunk_index']}"
                    f" | Similarity: {result['similarity']:.4f}"
                    f" | Rerank score: {result['rerank_score']:.4f}"
                )

                print(result["content"][:500])

    finally:
        db.close()


if __name__ == "__main__":
    main()
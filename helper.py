# helper.py

import argparse
from search import semantic_search
from db import get_claims_by_status
from synthesize import synthesize_answer


def main():
    parser = argparse.ArgumentParser(description="Main CLI for semantic search and synthesis.")
    parser.add_argument("query", help="Your search question.")
    parser.add_argument("--status", choices=["promoted", "demoted", "unreviewed", "all"], default="promoted",
                        help="Filter claims by status.")
    parser.add_argument("--top_k", type=int, default=5, help="Number of top search results to use.")
    args = parser.parse_args()

    # Step 1: Semantic search
    search_results = semantic_search(args.query, top_k=args.top_k)
    print("Search Results:", search_results)
    # Each result should have claim_id

    # Step 2: Filter claims by status
    filtered_claims = []
    claims = get_claims_by_status(args.status)
    for result in search_results:
        claim_id = int(result.get("claim_id"))
        for claim in claims:
            if int(claim.get("claim_id")) == claim_id:
                filtered_claims.append(claim)
    
    if not filtered_claims:
        print("No claims found for the selected filters.")
        return
    
    # Step 3: Snythsize answer
    answer = synthesize_answer(args.query, filtered_claims)
    print("\n--- Synthesized Answer ---\n")
    print(answer)
    print("\n--- Claims Used ---")
    for claim in filtered_claims:
        print(f"- {claim['claim_text']} (Source: {claim['source_ref']})")
    
if __name__ == "__main__":
    main()
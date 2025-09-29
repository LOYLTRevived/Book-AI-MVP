# synthesize.py

import argparse
from llm import get_llm_response
import sqlite3
from db import get_claims_by_status

def get_current_winner_claims(db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        SELECT claim_text, source_ref FROM claims WHERE current_winner = 1
    """)
    claims = [{"claim_text": row[0], "source_ref": row[1]} for row in c.fetchall()]
    conn.close()
    return claims

def synthesize_answer(query, claims, past_claims=None):
    # Format claims for LLM prompt
    claims_text = "\n".join(
        [f"- \"{claim['claim_text']}\" (Source: {claim['source_ref']})" for claim in claims]
    )

    prompt = (
        f"You are a synthesis engine. Given the following user question and a list of claims (with sources), "
        f"write a concise, well-reasoned answer that only uses these claims. Cite each claim's source in your answer.\n\n"
        f"Question: {query}\n\n"
        f"Claims:\n{claims_text}\n\n"
        f"Answer:"
    )
    response = get_llm_response(prompt)
    return response

def main():
    parser = argparse.ArgumentParser(description="Synthesize an answer from claims with flexible filtering.")
    parser.add_argument("query", help="The question to answer.")
    parser.add_argument("--status", choices=["all", "promoted", "demoted", "unsure"], default="promoted",
                        help="Which claims to use: all, promoted, demoted, or unsure.")
    args = parser.parse_args()

    claims = get_claims_by_status(status=args.status)
    if not claims:
        print("No claims found for the selected filter.")
        return

    answer = synthesize_answer(args.query, claims)
    print("\n--- Synthesized Answer ---\n")
    print(answer)


if __name__ == "__main__":
    main()
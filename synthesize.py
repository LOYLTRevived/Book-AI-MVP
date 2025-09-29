# synthesize.py

"""
Documentation:

Dependencies:
The script requires argparse, sqlite3, the LLM gateway function (llm.get_llm_response), and the database function (db.get_claims_by_status).

Key Functions:
    1. get_current_winner_claims(db_path)
    This function queries the SQLite database to fetch all claims currently marked as current_winner = 1 from the claims table. While present, the script's main() function uses the more flexible get_claims_by_status function instead, making this function potentially obsolete.

    2. synthesize_answer(query, claims, past_claims=None)
    This is the core function for generation.
    Prompt Construction: It formats the list of provided claims (along with their source_ref) into a clear, structured list within the LLM prompt.
    LLM Instruction: It instructs the LLM to act as a "synthesis engine," only use the provided claims to answer the query, and cite each claim's source in the final answer. This strict instruction is vital for maintaining factuality and traceability in the RAG system.
    LLM Call: It calls get_llm_response(prompt) to generate the final synthesized answer.

    3. Execution (main())
    The script takes a query (the question) and a required --status filter (all, promoted, demoted, unsure) as command-line arguments.
    It calls get_claims_by_status to retrieve the claims from the database based on the selected status.
    It passes the retrieved claims and the query to synthesize_answer to produce the final output, which is then printed to the console.
"""

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
# log_verdict.py

"""
Documentation:

Dependencies:
Requires argparse and the promote_claim and insert_verdict functions from db.py, along with standard sqlite3.

Key Functionality:
This script serves as the interface for a human reviewer to interact with the database and assert a belief state about a claim.

    1. log_verdict(cliam_id, verdict, db_path)
    Retrieve Group ID: It first queries the database to find the line_id associated with the given claim_id. This line_id is essential because the belief logic (promotion/demotion) operates on groups of claims related to the same topic or line of argument.
    Update Belief State: It calls promote_claim(cliam_id, line_id) (from db.py). This function performs two critical actions:
    It marks the current claim_id as the current_winner = 1 and increments its belief_score.
    It marks all other claims that share the same line_id as current_winner = 0 and decrements their belief_score. This creates a system of "believed" and "disbelieved" facts for a specific topic, where only one claim can be the current winner.
    Log History: It calls insert_verdict(cliam_id, verdict) (from db.py) to record the human-provided verdict ("true," "false," or "unsure") in the verdicts table.

    2. Execution (main())
    It uses argparse to accept two required command-line arguments:
    The claim_id (an integer) that the user is reviewing.
    The verdict (a string) which is restricted to the choices: "true", "false", or "unsure".
"""

import argparse
from db import promote_claim, insert_verdict
import sqlite3

def log_verdict(cliam_id, verdict, db_path="knowledge.db"):
    # Get line_id for the claim
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT line_id FROM claims WHERE claim_id = ?", (cliam_id,))
    row = c.fetchone()
    if not row:
        print(f"Claim {cliam_id} not found.")
        return
    line_id = row[0]
    conn.close()

    # Promote the claim and demote other in the same line_id
    promote_claim(cliam_id, line_id, db_path=db_path)

    # Log the verdict (history)
    insert_verdict(cliam_id, verdict, db_path=db_path)
    print(f"claim {cliam_id} promoted as winner for line_id '{line_id}'. Verdict '{verdict}' logged. ")

def main():
    parser = argparse.ArgumentParser(description="Log a verdict for a claim and update belief logic.")
    parser.add_argument("claim_id", type=int, help="The claim_id to mark as winner.")
    parser.add_argument("verdict", choices=["true", "false", "unsure"], help="Your verdict for the claim.")
    args = parser.parse_args()

    log_verdict(args.claim_id, args.verdict)


if __name__ == "__main__":
    main()

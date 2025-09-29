# log_verdict.py

"""
Documentation:

Dependencies:
Requires argparse, and the explicit belief control functions from db.py: promote_claim, demote_claim, and insert_verdict, along with standard sqlite3.

Key Functionality:
This script serves as the interface for a human reviewer to interact with the database and assert a belief state about a claim.

    1. Core Logic (Deprecated/Unused)
    The function log_verdict(claim_id, verdict, db_path) from the previous version remains in the script but is no longer called or used by the main() execution block.

    2. Execution (main()) — Shift to Explicit Control
    The command-line interface has been refactored to replace automatic promotion with explicit actions:
    Required Argument: claim_id (integer) to act on.
    Action Flags: The user must now specify the action using either --promote or --demote.
    If --promote is used, it calls the single-claim update function db.promote_claim(claim_id).
    If --demote is used, it calls the single-claim update function db.demote_claim(claim_id).

    Optional Logging: 
    An optional --verdict choice ("true", "false", or "unsure") can be supplied. If present, it calls db.insert_verdict(claim_id, verdict) to log the historical decision, but the verdict itself does not drive the belief state change.
"""

import argparse
from db import promote_claim, demote_claim, insert_verdict
import sqlite3

def log_verdict(claim_id, verdict, db_path="knowledge.db"):
    # Get line_id for the claim
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT line_id FROM claims WHERE claim_id = ?", (claim_id,))
    row = c.fetchone()
    if not row:
        print(f"Claim {claim_id} not found.")
        return
    line_id = row[0]
    conn.close()

    # Promote the claim and demote other in the same line_id
    promote_claim(claim_id, line_id, db_path=db_path)

    # Log the verdict (history)
    insert_verdict(claim_id, verdict, db_path=db_path)
    print(f"claim {claim_id} promoted as winner for line_id '{line_id}'. Verdict '{verdict}' logged. ")
def main():
    parser = argparse.ArgumentParser(description="Log a verdict for a claim and update belief logic.")
    parser.add_argument("claim_id", type=int, help="The claim_id to act on.")
    parser.add_argument("--promote", action="store_true", help="Promote this claim as winner.")
    parser.add_argument("--demote", action="store_true", help="Demote this claim manually.")
    parser.add_argument("--verdict", choices=["true", "false", "unsure"], help="Your verdict for the claim.")
    args = parser.parse_args()

    if args.promote:
        promote_claim(args.claim_id)
        if args.verdict:
            insert_verdict(args.claim_id, args.verdict)
        print(f"Claim {args.claim_id} promoted.")
    elif args.demote:
        demote_claim(args.claim_id)
        if args.verdict:
            insert_verdict(args.claim_id, args.verdict)
        print(f"Claim {args.claim_id} demoted.")
    else:
        print("Specify --promote or --demote.")


if __name__ == "__main__":
    main()

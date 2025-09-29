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

# db.py

"""
Documentation:

Dependencies: Requires the standard Python sqlite3 library.

Key Functionality:
The script defines several functions for database interaction, all using a default database path of "knowledge.db".

    1. create_tables()
    Initializes the database by creating two tables if they don't already exist:
    claims: Stores the raw assertions extracted from documents.
    Key columns include claim_id (Primary Key), line_id (a grouping identifier), claim_text, belief_score (for ranking), current_winner (a boolean flag for the best claim in a group), and source_ref (the source file).
    verdicts: Stores a historical log of decisions made about claims.
    Key columns include verdict_id (Primary Key), claim_id (Foreign Key referencing claims), and verdict (the actual judgment, e.g., "true," "false").

    2. insert_claim(line_id, claim_text, source_ref)
    Adds a new, extracted claim into the claims table.
    The claim is initially given a belief_score of 0 and is not marked as the current_winner.
    Returns the new claim_id.

    3. insert_verdict(claim_id, verdict)
    Logs a judgment (verdict) about a specific claim into the verdicts table, preserving the history of fact-checking/reviews.

    4. promote_claim(claim_id, line_id)
    Implements the core belief update logic:
    It demotes all other claims that share the same line_id by setting their current_winner flag to 0 and decreasing their belief_score by 1.
    It promotes the specified claim_id by setting its current_winner flag to 1 and increasing its belief_score by 1.

    5. get_verdict_history(line_id)
    Retrieves all recorded verdicts for every claim associated with a given line_id, allowing users to track the evolution of belief/judgment on a specific topic group.
"""

import sqlite3

def create_tables(db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    #Claims table
    c.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            line_id TEXT,
            claim_text TEXT,
            belief_score REAL DEFAULT 0,
            current_winner BOOLEAN DEFAULT 0,
            status TEXT DEFAULT 'unreviewed',  # <-- new column
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source_ref TEXT
        )
    """)

    #Verdicts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS verdicts (
            verdict_id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER,
            verdict TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
        )
    """)
    conn.commit()
    conn.close()

def insert_claim(line_id, claim_text, source_ref, db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        INSERT INTO claims (line_id, claim_text, source_ref, status) 
        VALUES (?, ?, ?, 'unreviewed')
    """, (line_id, claim_text, source_ref))
    conn.commit()
    claim_id = c.lastrowid
    conn.close()
    return claim_id

def insert_verdict(claim_id, verdict, db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        INSERT INTO verdicts (claim_id, verdict)
        VALUES (?, ?)
    """, (claim_id, verdict))
    conn.commit()
    conn.close()

def promote_claim(claim_id, db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        UPDATE claims SET current_winner = 1, status = 'promoted', belief_score = belief_score + 1
        WHERE claim_id = ?
    """, (claim_id,))
    conn.commit()
    conn.close()

def demote_claim(claim_id, db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        UPDATE claims SET current_winner = 0, status = 'demoted', belief_score = belief_score - 1
        WHERE claim_id = ?
    """, (claim_id,))
    conn.commit()
    conn.close()

def get_verdict_history(line_id, db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        SELECT v.verdict_id, v.claim_id, c.claim_text, v.verdict, v.timestamp
        FROM verdicts v
        JOIN claims c ON v.claim_id = c.claim_id
        WHERE c.line_id = ?
        ORDER BY v.timestamp ASC
    """, (line_id,))
    history = c.fetchall()
    conn.close()
    return history

def get_claims_by_status(status="all", db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if status == "promoted":
        c.execute("SELECT claim_text, source_ref FROM claims WHERE status = 'promoted'")
    elif status == "demoted":
        c.execute("SELECT claim_text, source_ref FROM claims WHERE status = 'demoted'")
    elif status == "unreviewed":
        c.execute("SELECT claim_text, source_ref FROM claims WHERE status = 'unreviewed'")
    else: # all
        c.execute("SELECT claim_text, source_ref FROM claims")
    claims = [{"claim_text": row[0], "source_ref": row[1]} for row in c.fetchall()]
    conn.close()
    return claims

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")
# db.py

"""
Documentation:

Dependencies: Requires the standard Python sqlite3 library.

Key Functionality Updates
    1. Schema Change (create_tables)
    NEW Column: status: The claims table now includes a status column, defaulting to 'unreviewed'. This formalizes the belief state, allowing claims to be filtered by their review status, which is crucial for RAG filtering in helper.py.
    NEW Column: timestamp: Added to both claims and verdicts tables for tracking creation and logging times.

    2. Claim Insertion and Retrieval
    insert_claim: Now explicitly sets the initial status of a new claim to 'unreviewed'.
    NEW Function: get_claims_by_status(status): This critical function allows retrieval of claims based on their status ('promoted', 'demoted', 'unreviewed', or 'all'). It's used by both the helper.py and synthesize.py scripts to curate the RAG context.

    3. Belief Logic Management (Refactored)
    The automatic, line-based logic has been removed and replaced with explicit, single-claim update functions:
    promote_claim(claim_id): Promotes a single claim by setting current_winner = 1, updating the status to 'promoted', and incrementing the belief_score by 1. It no longer demotes other claims within the same line_id.
    NEW Function: demote_claim(claim_id): Explicitly demotes a single claim by setting current_winner = 0, updating the status to 'demoted', and decrementing the belief_score by 1.

    4. Historical Logging
    insert_verdict(claim_id, verdict): Logs a human judgment (verdict) into the verdicts table, maintaining a history of review actions.
    get_verdict_history(line_id): Retrieves all historical verdicts for all claims associated with a given line_id.
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
        c.execute("SELECT claim_id, claim_text, source_ref FROM claims WHERE status = 'promoted'")
    elif status == "demoted":
        c.execute("SELECT claim_id, claim_text, source_ref FROM claims WHERE status = 'demoted'")
    elif status == "unreviewed":
        c.execute("SELECT claim_id, claim_text, source_ref FROM claims WHERE status = 'unreviewed'")
    else: # all
        c.execute("SELECT claim_id, claim_text, source_ref FROM claims")
    claims = [{"claim_id": row[0], "claim_text": row[1], "source_ref": row[2]} for row in c.fetchall()]
    conn.close()
    return claims

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")
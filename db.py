# db.py

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
        INSERT INTO claims (line_id, claim_text, source_ref) 
        VALUES (?, ?, ?)
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

def promote_claim(claim_id, line_id, db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Demote all other claims in the same line_id
    c.execute("""
        UPDATE claims SET current_winner = 0, belief_score = belief_score - 1
        WHERE line_id = ? AND claim_id != ?
    """, (line_id, claim_id))
    # Promote the selected claim
    c.execute("""
        UPDATE claims SET current_winner = 1, belief_score = belief_score + 1
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

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")
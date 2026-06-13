import sqlite3

conn = sqlite3.connect(
    "memory.db"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory(
    id INTEGER PRIMARY KEY,
    fact TEXT
)
""")

conn.commit()

def save_memory(fact):

    cursor.execute(
        "INSERT INTO memory (fact) VALUES (?)",
        (fact,)
    )

    conn.commit()

def get_memories():

    cursor.execute(
        "SELECT fact FROM memory"
    )

    return [
        row[0]
        for row in cursor.fetchall()
    ]
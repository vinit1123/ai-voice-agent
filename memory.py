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
        "SELECT fact FROM memory WHERE fact=?",
        (fact,)
    )

    exists = cursor.fetchone()

    if exists:
        return

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
def search_memory(query):

    cursor.execute(
        "SELECT fact FROM memory"
    )

    memories = [
        row[0]
        for row in cursor.fetchall()
    ]

    query = query.lower()

    matches = []

    for memory in memories:

        if any(
            word in memory.lower()
            for word in query.split()
        ):

            matches.append(
                memory
            )

    return matches[-5:]
#cursor.execute(
    #"DELETE FROM memory"
#)

#conn.commit()
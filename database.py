import os
import random
import string
import sqlite3

# The folder that contains this file (database.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full path of the database file, always next to database.py
DATABASE_NAME = os.path.join(BASE_DIR, "shortqr.db")

def get_connection():
    """Open a connection to the database file."""
    connection = sqlite3.connect(DATABASE_NAME)
    # This lets us read columns by name, like row["short_code"]
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the links table if it does not exist yet."""
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER NOT NULL DEFAULT 0
        )
    """)

    # commit() saves our changes permanently
    connection.commit()
    # Always close the connection when we're finished
    connection.close()

# The characters a short code may contain: a-z, A-Z and 0-9
CODE_CHARACTERS = string.ascii_letters + string.digits
CODE_LENGTH = 6


def code_exists(short_code):
    """Return True if this short code is already in the database."""
    connection = get_connection()

    # The ? is a placeholder. The value goes in the tuple after the query.
    row = connection.execute(
        "SELECT id FROM links WHERE short_code = ?",
        (short_code,),
    ).fetchone()

    connection.close()
    # If no row was found, row is None, so this returns False
    return row is not None


def generate_short_code():
    """Create a random code that is not used yet."""
    while True:
        # Pick CODE_LENGTH random characters and join them into one string
        new_code = "".join(
            random.choice(CODE_CHARACTERS) for _ in range(CODE_LENGTH)
        )

        # Only return the code if nobody else has it
        if not code_exists(new_code):
            return new_code


def save_link(original_url):
    """Save a URL in the database and return its new short code."""
    short_code = generate_short_code()

    connection = get_connection()
    connection.execute(
        "INSERT INTO links (original_url, short_code) VALUES (?, ?)",
        (original_url, short_code),
    )
    connection.commit()
    connection.close()

    return short_code

def get_original_url(short_code):
    """Look up a short code. Return the original URL, or None if not found."""
    connection = get_connection()

    row = connection.execute(
        "SELECT original_url FROM links WHERE short_code = ?",
        (short_code,),
    ).fetchone()

    connection.close()

    # If no row matched, there is no such link
    if row is None:
        return None

    return row["original_url"]

def increment_clicks(short_code):
    """Add 1 to the click counter of a link."""
    connection = get_connection()

    connection.execute(
        "UPDATE links SET clicks = clicks + 1 WHERE short_code = ?",
        (short_code,),
    )

    connection.commit()
    connection.close()


def get_recent_links(limit=10):
    """Return the newest links first, as a list of dictionaries."""
    connection = get_connection()

    rows = connection.execute(
        "SELECT short_code, original_url, created_at, clicks "
        "FROM links ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()

    connection.close()

    # Turn each database row into a normal dictionary so jsonify can use it
    return [dict(row) for row in rows]

# Runs only when we start this file directly: python database.py
if __name__ == "__main__":
    init_db()
    print("Database ready!")
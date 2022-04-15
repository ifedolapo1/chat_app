import sqlite3  # Import from python library

db_config_file = 'database.db'

# SQLite database connection
con = sqlite3.connect(db_config_file)
cur = con.cursor()

def runSqlDatabase():
    # Create users and chats table if it does not exists
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username, password)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY, from_username, to_username, text,  enc_text, time)")
    con.commit() # Save database execution changes
    # con.close() # Close database connection
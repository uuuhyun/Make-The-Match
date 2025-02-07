import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute(
'''
    CREATE TABLE IF NOT EXISTS soccer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team1 text, 
        team2 text, 
        time text, 
        location text, 
        details text, 
        people int,
        email text)
'''
)
cur.execute(
'''
    CREATE TABLE IF NOT EXISTS basketball (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team1 text, 
        team2 text, 
        time text, 
        location text, 
        details text, 
        people int,
        email text)
'''
)
cur.execute(
'''
    CREATE TABLE IF NOT EXISTS tennis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team1 text, 
        team2 text, 
        time text, 
        location text, 
        details text, 
        people int,
        email text)
'''
)

cur.execute(
'''
    CREATE TABLE IF NOT EXISTS vs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team text, 
        time text, 
        location text, 
        details text,
        applied_team text,
        email text,
        sports TEXT NOT NULL)
'''
)

cur.execute('''
    CREATE TABLE IF NOT EXISTS leftboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        context TEXT NOT NULL,
        username text,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
cur.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        comment_text TEXT NOT NULL,
        username text,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES leftboard (id)
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        username TEXT NOT NULL,
        major TEXT NOT NULL,
        team TEXT NOT NULL,
        manager text
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS applied (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matchnum int NOT NULL,
        email TEXT NOT NULL,
        sports TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

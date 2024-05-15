import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute(
'''
    CREATE TABLE IF NOT EXISTS soccer (team1 text, team2 text, time text, location text, details text)
'''
)

cur.execute(
'''
    CREATE TABLE IF NOT EXISTS basketball (team1 text, team2 text, time text, location text, details text)
'''
)

cur.execute(
'''
    CREATE TABLE IF NOT EXISTS tennis (team1 text, team2 text, time text, location text, details text)
'''
)

cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", ('유현', 'hello@inha.edu', 'world'))
conn.commit()
conn.close()

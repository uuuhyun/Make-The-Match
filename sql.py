import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

conn.execute(
'''
create table soccer (match text, time text, details text)
'''
)
conn.execute(
'''
create table basketball (match text, time text, details text)
'''
)
conn.execute(
'''
create table tennis (match text, time text, details text)
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

import sqlite3

conn = sqlite3.connect('database.db')

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

conn.close()
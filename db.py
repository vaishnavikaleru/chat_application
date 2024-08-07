import sqlite3
from flask import g

DATABASE = 'chatApp.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()

def init_db_command():
    with open('schema.sql', mode='r') as f:
        get_db().executescript(f.read())

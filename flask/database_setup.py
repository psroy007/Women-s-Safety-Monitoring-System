import sqlite3

def create_db():
    conn = sqlite3.connect('video_uploads.db')
    c = conn.cursor()
    
    # Create table for videos
    c.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        filepath TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

create_db()

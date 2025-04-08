import sqlite3


def init_db(dbfile):
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            pub_year INTEGER,
            pages INTEGER,
            genre TEXT
        )
    """)
    conn.commit()

    cursor.execute("""CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            date_read DATE,
            rating INTEGER,
            review TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)

    conn.close()

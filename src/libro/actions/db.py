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
    conn.commit()

    cursor.execute("""CREATE TABLE reading_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_date DATE DEFAULT CURRENT_DATE
        )
    """)
    conn.commit()

    cursor.execute("""CREATE TABLE reading_list_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            added_date DATE DEFAULT CURRENT_DATE,
            priority INTEGER DEFAULT 0,
            FOREIGN KEY (list_id) REFERENCES reading_lists(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
            UNIQUE(list_id, book_id)
        )
    """)
    conn.commit()

    conn.close()


def migrate_db(conn):
    """Add reading lists tables to existing databases if they don't exist."""
    cursor = conn.cursor()

    # Check if reading_lists table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='reading_lists'"
    )
    if not cursor.fetchone():
        cursor.execute("""CREATE TABLE reading_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_date DATE DEFAULT CURRENT_DATE
            )
        """)
        conn.commit()

    # Check if reading_list_books table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='reading_list_books'"
    )
    if not cursor.fetchone():
        cursor.execute("""CREATE TABLE reading_list_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                added_date DATE DEFAULT CURRENT_DATE,
                priority INTEGER DEFAULT 0,
                FOREIGN KEY (list_id) REFERENCES reading_lists(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                UNIQUE(list_id, book_id)
            )
        """)
        conn.commit()

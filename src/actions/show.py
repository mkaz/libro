import sqlite3


def show_books(db):
    books = get_books(db)
    for book in books:
        print(book)


def get_books(db):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM books LIMIT 5")
        books = cursor.fetchall()
        return books
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if db:
            db.close()

from dataclasses import dataclass
from typing import Optional
import sqlite3
from datetime import date


# Register date adapter to fix Python 3.12+ deprecation warning
def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()


def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return date.fromisoformat(val.decode())


sqlite3.register_adapter(date, adapt_date_iso)
sqlite3.register_converter("date", convert_date)


@dataclass
class Book:
    """Represents a book in the database."""

    title: str
    author: str
    pub_year: Optional[int] = None
    pages: Optional[int] = None
    genre: Optional[str] = None
    id: Optional[int] = None

    def insert(self, db: sqlite3.Connection) -> int:
        """Insert the book into the database and return its ID."""
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO books (
                title, author, pub_year, pages, genre
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                self.title,
                self.author,
                self.pub_year,
                self.pages,
                self.genre,
            ),
        )
        self.id = cursor.lastrowid
        db.commit()
        if self.id is None:
            raise RuntimeError("Failed to insert book: no ID returned")
        return self.id

    @classmethod
    def get_by_id(cls, db: sqlite3.Connection, book_id: int) -> Optional["Book"]:
        """Retrieve a book by its ID."""
        cursor = db.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return cls(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            pub_year=row["pub_year"],
            pages=row["pages"],
            genre=row["genre"],
        )

    @classmethod
    def find_by_title_author(
        cls, db: sqlite3.Connection, title: str, author: str
    ) -> Optional["Book"]:
        """Find a book by title and author (case-insensitive)."""
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM books WHERE LOWER(title) = LOWER(?) AND LOWER(author) = LOWER(?)",
            (title, author),
        )
        row = cursor.fetchone()

        if not row:
            return None

        return cls(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            pub_year=row["pub_year"],
            pages=row["pages"],
            genre=row["genre"],
        )


@dataclass
class Review:
    """Represents a review in the database."""

    book_id: int
    date_read: Optional[date] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    id: Optional[int] = None

    def insert(self, db: sqlite3.Connection) -> int:
        """Insert the review into the database and return its ID."""
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO reviews (
                book_id, date_read, rating, review
            ) VALUES (?, ?, ?, ?)
            """,
            (
                self.book_id,
                self.date_read,
                self.rating,
                self.review,
            ),
        )
        self.id = cursor.lastrowid
        db.commit()
        if self.id is None:
            raise RuntimeError("Failed to insert review: no ID returned")
        return self.id


@dataclass
class BookReview:
    """Represents a combined Book and Review object."""

    # Fields from Review (non-defaults first)
    book_id: int  # Review's book_id, also the book's ID
    book_title: str
    book_author: str

    # Optionals/defaults after required fields
    review_id: Optional[int] = None  # Review's ID
    date_read: Optional[date] = None
    rating: Optional[int] = None
    review_text: Optional[str] = None
    book_pub_year: Optional[int] = None
    book_pages: Optional[int] = None
    book_genre: Optional[str] = None

    @classmethod
    def get_by_id(
        cls, db: sqlite3.Connection, review_id: int
    ) -> Optional["BookReview"]:
        """
        Fetch a combined BookReview entry by the review ID.
        Returns a BookReview instance or None if not found.
        """
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT
                    r.id, r.date_read, r.rating, r.review, r.book_id,
                    b.title, b.author, b.pub_year, b.pages, b.genre
                FROM reviews r
                JOIN books b ON r.book_id = b.id
                WHERE r.id = ?
                """,
                (review_id,),
            )
            row = cursor.fetchone()
            if row:
                # Create a BookReview instance from the row data
                return cls(
                    book_id=row["book_id"],
                    book_title=row["title"],
                    book_author=row["author"],
                    review_id=row["id"],
                    date_read=row["date_read"],
                    rating=row["rating"],
                    review_text=row["review"],
                    book_pub_year=row["pub_year"],
                    book_pages=row["pages"],
                    book_genre=row["genre"],
                )
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None


@dataclass
class ReadingList:
    """Represents a reading list in the database."""

    name: str
    description: Optional[str] = None
    created_date: Optional[date] = None
    id: Optional[int] = None

    def insert(self, db: sqlite3.Connection) -> int:
        """Insert the reading list into the database and return its ID."""
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO reading_lists (
                name, description, created_date
            ) VALUES (?, ?, ?)
            """,
            (
                self.name,
                self.description,
                self.created_date or date.today(),
            ),
        )
        self.id = cursor.lastrowid
        db.commit()
        if self.id is None:
            raise RuntimeError("Failed to insert reading list: no ID returned")
        return self.id

    @classmethod
    def get_all(cls, db: sqlite3.Connection) -> list["ReadingList"]:
        """Get all reading lists from the database."""
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, name, description, created_date
            FROM reading_lists
            ORDER BY created_date DESC
            """
        )
        lists = []
        for row in cursor.fetchall():
            lists.append(
                cls(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    created_date=row["created_date"],
                )
            )
        return lists

    @classmethod
    def get_by_name(cls, db: sqlite3.Connection, name: str) -> Optional["ReadingList"]:
        """Get a reading list by name."""
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, name, description, created_date
            FROM reading_lists
            WHERE name = ?
            """,
            (name,),
        )
        row = cursor.fetchone()
        if row:
            return cls(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                created_date=row["created_date"],
            )
        return None

    @classmethod
    def get_by_id(cls, db: sqlite3.Connection, list_id: int) -> Optional["ReadingList"]:
        """Get a reading list by ID."""
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, name, description, created_date
            FROM reading_lists
            WHERE id = ?
            """,
            (list_id,),
        )
        row = cursor.fetchone()
        if row:
            return cls(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                created_date=row["created_date"],
            )
        return None

    def update(self, db: sqlite3.Connection) -> None:
        """Update the reading list in the database."""
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE reading_lists 
            SET name = ?, description = ?
            WHERE id = ?
            """,
            (self.name, self.description, self.id),
        )
        db.commit()

    def delete(self, db: sqlite3.Connection) -> None:
        """Delete the reading list from the database."""
        cursor = db.cursor()
        cursor.execute("DELETE FROM reading_lists WHERE id = ?", (self.id,))
        db.commit()


@dataclass
class ReadingListBook:
    """Represents a book in a reading list."""

    list_id: int
    book_id: int
    added_date: Optional[date] = None
    priority: int = 0
    id: Optional[int] = None

    def insert(self, db: sqlite3.Connection) -> int:
        """Insert the reading list book into the database and return its ID."""
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO reading_list_books (
                list_id, book_id, added_date, priority
            ) VALUES (?, ?, ?, ?)
            """,
            (
                self.list_id,
                self.book_id,
                self.added_date or date.today(),
                self.priority,
            ),
        )
        self.id = cursor.lastrowid
        db.commit()
        if self.id is None:
            raise RuntimeError("Failed to insert reading list book: no ID returned")
        return self.id

    @classmethod
    def get_books_in_list(cls, db: sqlite3.Connection, list_id: int) -> list[dict]:
        """Get all books in a reading list with their read status."""
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT
                b.id as book_id,
                b.title,
                b.author,
                b.genre,
                b.pub_year,
                b.pages,
                rlb.added_date,
                rlb.priority,
                CASE WHEN r.id IS NOT NULL THEN 1 ELSE 0 END as is_read,
                r.date_read,
                r.rating
            FROM reading_list_books rlb
            JOIN books b ON rlb.book_id = b.id
            LEFT JOIN reviews r ON b.id = r.book_id
            WHERE rlb.list_id = ?
            ORDER BY rlb.priority DESC, rlb.added_date ASC
            """,
            (list_id,),
        )
        return cursor.fetchall()

    @classmethod
    def remove_book_from_list(
        cls, db: sqlite3.Connection, list_id: int, book_id: int
    ) -> None:
        """Remove a book from a reading list."""
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM reading_list_books WHERE list_id = ? AND book_id = ?",
            (list_id, book_id),
        )
        db.commit()

    @classmethod
    def get_list_stats(cls, db: sqlite3.Connection, list_id: int) -> dict:
        """Get statistics for a reading list."""
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_books,
                COUNT(r.id) as books_read,
                COUNT(*) - COUNT(r.id) as books_unread
            FROM reading_list_books rlb
            JOIN books b ON rlb.book_id = b.id
            LEFT JOIN reviews r ON b.id = r.book_id
            WHERE rlb.list_id = ?
            """,
            (list_id,),
        )
        row = cursor.fetchone()
        if row:
            total = row["total_books"]
            read = row["books_read"]
            percentage = (read / total * 100) if total > 0 else 0
            return {
                "total_books": total,
                "books_read": read,
                "books_unread": row["books_unread"],
                "completion_percentage": percentage,
            }
        return {
            "total_books": 0,
            "books_read": 0,
            "books_unread": 0,
            "completion_percentage": 0,
        }

    @classmethod
    def get_lists_for_book(cls, db: sqlite3.Connection, book_id: int) -> list[str]:
        """Get all reading lists that contain a specific book."""
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT rl.name
            FROM reading_list_books rlb
            JOIN reading_lists rl ON rlb.list_id = rl.id
            WHERE rlb.book_id = ?
            ORDER BY rl.name
            """,
            (book_id,),
        )
        return [row["name"] for row in cursor.fetchall()]

    @classmethod
    def get_lists_with_ids_for_book(
        cls, db: sqlite3.Connection, book_id: int
    ) -> list[tuple[int, str]]:
        """Get all reading lists (ID and name) that contain a specific book."""
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT rl.id, rl.name
            FROM reading_list_books rlb
            JOIN reading_lists rl ON rlb.list_id = rl.id
            WHERE rlb.book_id = ?
            ORDER BY rl.name
            """,
            (book_id,),
        )
        return [(row["id"], row["name"]) for row in cursor.fetchall()]

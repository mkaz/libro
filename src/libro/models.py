from dataclasses import dataclass
from typing import Optional
import sqlite3
from datetime import date


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
        return self.id


@dataclass
class Review:
    """Represents a book in the database."""

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
        return self.id


@dataclass
class BookReview:
    """Represents a combined Book and Review entry."""

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
                    book_id=row[4],
                    book_title=row[5],
                    book_author=row[6],
                    review_id=row[0],
                    date_read=row[1],
                    rating=row[2],
                    review_text=row[3],
                    book_pub_year=row[7],
                    book_pages=row[8],
                    book_genre=row[9],
                )
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

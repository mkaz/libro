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
    """Represents a book review in the database."""

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

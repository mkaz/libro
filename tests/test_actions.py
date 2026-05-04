"""Tests for libro actions/commands."""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from libro.actions.db import init_db
from libro.actions.show import (
    get_books_only,
    get_reviews,
    show_book_detail,
    show_book_only_detail,
    show_recent_reviews,
)
from libro.models import Book, Review


class TestShowActions:
    """Test show action functions."""

    def test_get_books_only_empty_db(self, temp_db):
        """Test getting books from empty database."""
        books = get_books_only(temp_db)
        assert books == []

    def test_get_books_only_with_books(self, temp_db, sample_book_data):
        """Test getting books from database with books."""
        # Add some test books
        book1 = Book(title="First Book", author="Author A", genre="fiction")
        book1.insert(temp_db)

        book2 = Book(title="Second Book", author="Author B", genre="nonfiction")
        book2.insert(temp_db)

        books = get_books_only(temp_db)
        assert len(books) == 2

        # Should be sorted by ID DESC (newest first)
        assert books[0]["title"] == "Second Book"
        assert books[1]["title"] == "First Book"

    def test_get_books_by_author(self, temp_db):
        """Test getting books filtered by author."""
        book1 = Book(title="Book 1", author="Jane Smith", genre="fiction")
        book1.insert(temp_db)

        book2 = Book(title="Book 2", author="John Doe", genre="fiction")
        book2.insert(temp_db)

        # Test partial match
        books = get_books_only(temp_db, author_name="Jane")
        assert len(books) == 1
        assert books[0]["author"] == "Jane Smith"

        # Test case insensitive
        books = get_books_only(temp_db, author_name="jane")
        assert len(books) == 1
        assert books[0]["author"] == "Jane Smith"

    def test_get_books_by_year(self, temp_db):
        """Test getting books filtered by publication year."""
        book1 = Book(title="Old Book", author="Author", pub_year=2020, genre="fiction")
        book1.insert(temp_db)

        book2 = Book(title="New Book", author="Author", pub_year=2023, genre="fiction")
        book2.insert(temp_db)

        books = get_books_only(temp_db, year=2023)
        assert len(books) == 1
        assert books[0]["title"] == "New Book"

    def test_get_books_by_title(self, temp_db):
        """Test getting books filtered by title."""
        book1 = Book(title="Python Programming", author="Author", genre="tech")
        book1.insert(temp_db)

        book2 = Book(title="Java Programming", author="Author", genre="tech")
        book2.insert(temp_db)

        books = get_books_only(temp_db, title="Python")
        assert len(books) == 1
        assert books[0]["title"] == "Python Programming"

    def test_get_reviews_empty_db(self, temp_db):
        """Test getting reviews from empty database."""
        reviews = get_reviews(temp_db, year=2023)
        assert reviews == []

    def test_get_reviews_by_year(self, temp_db, sample_book_data):
        """Test getting reviews filtered by year."""
        # Create book and reviews
        book = Book(**sample_book_data)
        book_id = book.insert(temp_db)

        review1 = Review(
            book_id=book_id, rating=4, date_read="2023-06-01", review="Good"
        )
        review1.insert(temp_db)

        review2 = Review(
            book_id=book_id, rating=5, date_read="2022-06-01", review="Great"
        )
        review2.insert(temp_db)

        # Test filtering by year
        reviews_2023 = get_reviews(temp_db, year=2023)
        assert len(reviews_2023) == 1
        assert reviews_2023[0]["rating"] == 4

        reviews_2022 = get_reviews(temp_db, year=2022)
        assert len(reviews_2022) == 1
        assert reviews_2022[0]["rating"] == 5

    def test_get_reviews_by_author(self, temp_db):
        """Test getting reviews filtered by author."""
        # Create books and reviews
        book1 = Book(title="Book 1", author="Jane Smith", genre="fiction")
        book1_id = book1.insert(temp_db)

        book2 = Book(title="Book 2", author="John Doe", genre="fiction")
        book2_id = book2.insert(temp_db)

        review1 = Review(book_id=book1_id, rating=4, date_read="2023-01-01")
        review1.insert(temp_db)

        review2 = Review(book_id=book2_id, rating=5, date_read="2023-02-01")
        review2.insert(temp_db)

        # Test filtering by author
        reviews = get_reviews(temp_db, author_name="Jane")
        assert len(reviews) == 1
        assert reviews[0]["author"] == "Jane Smith"

    def test_get_reviews_by_rating(self, temp_db):
        """Test getting reviews filtered by rating."""
        book1 = Book(title="Book 1", author="Jane Smith", genre="fiction")
        book1_id = book1.insert(temp_db)

        book2 = Book(title="Book 2", author="John Doe", genre="fiction")
        book2_id = book2.insert(temp_db)

        Review(book_id=book1_id, rating=4, date_read="2023-01-01").insert(temp_db)
        Review(book_id=book2_id, rating=5, date_read="2023-02-01").insert(temp_db)

        reviews = get_reviews(temp_db, rating=4)
        assert len(reviews) == 1
        assert reviews[0]["rating"] == 4
        assert reviews[0]["author"] == "Jane Smith"

    def test_get_reviews_with_combined_filters(self, temp_db):
        """Test getting reviews filtered by more than one field."""
        jane_book = Book(title="Python Notes", author="Jane Smith", genre="fiction")
        jane_book_id = jane_book.insert(temp_db)

        john_book = Book(title="Python Notes", author="John Doe", genre="fiction")
        john_book_id = john_book.insert(temp_db)

        Review(book_id=jane_book_id, rating=4, date_read="2023-01-01").insert(temp_db)
        Review(book_id=jane_book_id, rating=5, date_read="2023-02-01").insert(temp_db)
        Review(book_id=john_book_id, rating=4, date_read="2023-03-01").insert(temp_db)

        reviews = get_reviews(temp_db, author_name="Jane", title="Python", rating=4)
        assert len(reviews) == 1
        assert reviews[0]["author"] == "Jane Smith"
        assert reviews[0]["title"] == "Python Notes"
        assert reviews[0]["rating"] == 4

    def test_show_recent_reviews_ignores_default_year(self, temp_db):
        """Test default review listing shows recent reviews, not the current year."""
        old_book = Book(title="Old Review", author="Author A", genre="fiction")
        old_book_id = old_book.insert(temp_db)

        new_book = Book(title="New Review", author="Author B", genre="fiction")
        new_book_id = new_book.insert(temp_db)

        Review(book_id=old_book_id, rating=3, date_read="2023-01-01").insert(temp_db)
        Review(book_id=new_book_id, rating=5, date_read="2024-01-01").insert(temp_db)

        with patch("libro.actions.show.Console") as mock_console:
            show_recent_reviews(temp_db, {"year": 2024, "year_explicit": False})

        rendered_table = mock_console.return_value.print.call_args[0][0]
        assert rendered_table.title == "Recent Reviews (Latest 20)"
        assert len(rendered_table.rows) == 2

    def test_show_book_detail_plain_output(self, temp_db, capsys):
        """Test review detail output in plain text mode."""
        book = Book(
            title="Plain Review Book",
            author="Plain Author",
            pub_year=2024,
            pages=321,
            genre="fiction",
        )
        book_id = book.insert(temp_db)
        review = Review(
            book_id=book_id,
            rating=5,
            date_read="2024-06-15",
            review="Copy and paste review text.",
        )
        review_id = review.insert(temp_db)

        show_book_detail(temp_db, review_id, plain=True)

        output = capsys.readouterr().out
        assert "Title: Plain Review Book" in output
        assert "Author: Plain Author" in output
        assert "Review ID: 1" in output
        assert "My Review: Copy and paste review text." in output

    def test_show_book_only_detail_plain_output(self, temp_db, capsys):
        """Test book detail output in plain text mode."""
        book = Book(
            title="Plain Book",
            author="Book Author",
            pub_year=2023,
            pages=250,
            genre="nonfiction",
        )
        book_id = book.insert(temp_db)
        review = Review(book_id=book_id, rating=4, date_read="2023-09-01")
        review.insert(temp_db)

        show_book_only_detail(temp_db, book_id, plain=True)

        output = capsys.readouterr().out
        assert "Title: Plain Book" in output
        assert "Author: Book Author" in output
        assert "Reading Lists: None" in output
        assert "Reviews:" in output
        assert "Rating: 4" in output


class TestDatabaseInitialization:
    """Test database initialization and schema."""

    def test_init_db_creates_tables(self):
        """Test that init_db creates all required tables."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            db_path = temp_file.name

        try:
            # init_db expects a file path, not a connection
            init_db(db_path)

            # Connect to check tables were created
            db = sqlite3.connect(db_path)
            db.row_factory = sqlite3.Row

            # Check that all tables exist
            cursor = db.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = [
                "books",
                "reading_list_books",
                "reading_lists",
                "reviews",
            ]
            assert set(tables) == set(expected_tables)

            db.close()
        finally:
            Path(db_path).unlink()

    def test_database_schema_books(self, temp_db):
        """Test books table schema."""
        cursor = temp_db.cursor()
        cursor.execute("PRAGMA table_info(books)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        expected_columns = {
            "id": "INTEGER",
            "title": "TEXT",
            "author": "TEXT",
            "pub_year": "INTEGER",
            "pages": "INTEGER",
            "genre": "TEXT",
        }

        for col, col_type in expected_columns.items():
            assert col in columns
            assert columns[col] == col_type

    def test_database_schema_reviews(self, temp_db):
        """Test reviews table schema."""
        cursor = temp_db.cursor()
        cursor.execute("PRAGMA table_info(reviews)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        expected_columns = {
            "id": "INTEGER",
            "book_id": "INTEGER",
            "date_read": "DATE",
            "rating": "INTEGER",
            "review": "TEXT",
        }

        for col, col_type in expected_columns.items():
            assert col in columns
            assert columns[col] == col_type

    def test_database_foreign_keys(self, temp_db):
        """Test that foreign key constraints work."""
        # Try to insert review with non-existent book_id
        cursor = temp_db.cursor()

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")

        # This should fail due to foreign key constraint
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO reviews (book_id, rating, date_read, review)
                VALUES (999, 5, '2023-01-01', 'Great book!')
            """)

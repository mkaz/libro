"""Tests for libro models."""

import sqlite3
from datetime import date

import pytest

from libro.models import Book, Review, ReadingList, ReadingListBook


class TestBook:
    """Test Book model."""

    def test_book_creation(self, sample_book_data):
        """Test creating a Book instance."""
        book = Book(**sample_book_data)
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.pub_year == 2023
        assert book.pages == 300
        assert book.genre == "fiction"
        assert book.id is None  # Not inserted yet

    def test_book_insert(self, temp_db, sample_book_data):
        """Test inserting a book into the database."""
        book = Book(**sample_book_data)
        book_id = book.insert(temp_db)
        
        assert book_id is not None
        assert book.id == book_id
        
        # Verify it's in the database
        cursor = temp_db.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["title"] == "Test Book"
        assert row["author"] == "Test Author"

    def test_book_find_by_title_author(self, temp_db, sample_book_data):
        """Test finding a book by title and author."""
        book = Book(**sample_book_data)
        book.insert(temp_db)
        
        found_book = Book.find_by_title_author(temp_db, "Test Book", "Test Author")
        assert found_book is not None
        assert found_book.title == "Test Book"
        assert found_book.author == "Test Author"
        
        # Test case insensitive search
        found_book = Book.find_by_title_author(temp_db, "test book", "test author")
        assert found_book is not None

    def test_book_not_found(self, temp_db):
        """Test finding a non-existent book."""
        found_book = Book.find_by_title_author(temp_db, "Non-existent", "Author")
        assert found_book is None


class TestReview:
    """Test Review model."""

    def test_review_creation(self, sample_review_data):
        """Test creating a Review instance."""
        review = Review(book_id=1, **sample_review_data)
        assert review.book_id == 1
        assert review.rating == 4
        assert review.date_read == "2023-12-01"
        assert review.review == "Great book!"

    def test_review_insert(self, temp_db, sample_book_data, sample_review_data):
        """Test inserting a review into the database."""
        # First create a book
        book = Book(**sample_book_data)
        book_id = book.insert(temp_db)
        
        # Then create a review
        review = Review(book_id=book_id, **sample_review_data)
        review_id = review.insert(temp_db)
        
        assert review_id is not None
        assert review.id == review_id
        
        # Verify it's in the database
        cursor = temp_db.cursor()
        cursor.execute("SELECT * FROM reviews WHERE id = ?", (review_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["book_id"] == book_id
        assert row["rating"] == 4

    def test_review_with_date_object(self, temp_db, sample_book_data):
        """Test review with date object instead of string."""
        book = Book(**sample_book_data)
        book_id = book.insert(temp_db)
        
        review = Review(
            book_id=book_id,
            rating=5,
            date_read=date(2023, 12, 15),
            review="Excellent!"
        )
        review_id = review.insert(temp_db)
        
        assert review_id is not None


class TestReadingList:
    """Test ReadingList model."""

    def test_reading_list_creation(self):
        """Test creating a ReadingList instance."""
        reading_list = ReadingList(name="To Read", description="Books I want to read")
        assert reading_list.name == "To Read"
        assert reading_list.description == "Books I want to read"
        assert reading_list.id is None

    def test_reading_list_insert(self, temp_db):
        """Test inserting a reading list into the database."""
        reading_list = ReadingList(name="Sci-Fi Classics", description="Classic science fiction")
        list_id = reading_list.insert(temp_db)
        
        assert list_id is not None
        assert reading_list.id == list_id
        
        # Verify it's in the database
        cursor = temp_db.cursor()
        cursor.execute("SELECT * FROM reading_lists WHERE id = ?", (list_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["name"] == "Sci-Fi Classics"
        assert row["description"] == "Classic science fiction"

    def test_reading_list_get_by_name(self, temp_db):
        """Test finding a reading list by name."""
        reading_list = ReadingList(name="Fantasy", description="Fantasy novels")
        reading_list.insert(temp_db)
        
        found_list = ReadingList.get_by_name(temp_db, "Fantasy")
        assert found_list is not None
        assert found_list.name == "Fantasy"
        assert found_list.description == "Fantasy novels"

    def test_reading_list_get_by_id(self, temp_db):
        """Test finding a reading list by ID."""
        reading_list = ReadingList(name="Mystery", description="Mystery novels")
        list_id = reading_list.insert(temp_db)
        
        found_list = ReadingList.get_by_id(temp_db, list_id)
        assert found_list is not None
        assert found_list.id == list_id
        assert found_list.name == "Mystery"


class TestReadingListBook:
    """Test ReadingListBook model."""

    def test_reading_list_book_creation(self):
        """Test creating a ReadingListBook instance."""
        rlb = ReadingListBook(list_id=1, book_id=2, priority=1)
        assert rlb.list_id == 1
        assert rlb.book_id == 2
        assert rlb.priority == 1

    def test_reading_list_book_insert(self, temp_db, sample_book_data):
        """Test inserting a reading list book association."""
        # Create book and reading list
        book = Book(**sample_book_data)
        book_id = book.insert(temp_db)
        
        reading_list = ReadingList(name="Test List", description="Test")
        list_id = reading_list.insert(temp_db)
        
        # Create association
        rlb = ReadingListBook(list_id=list_id, book_id=book_id, priority=1)
        rlb_id = rlb.insert(temp_db)
        
        assert rlb_id is not None
        assert rlb.id == rlb_id
        
        # Verify it's in the database
        cursor = temp_db.cursor()
        cursor.execute("SELECT * FROM reading_list_books WHERE id = ?", (rlb_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["list_id"] == list_id
        assert row["book_id"] == book_id

    def test_get_lists_for_book(self, temp_db, sample_book_data):
        """Test getting reading lists that contain a book."""
        # Create book
        book = Book(**sample_book_data)
        book_id = book.insert(temp_db)
        
        # Create two reading lists
        list1 = ReadingList(name="List 1", description="First list")
        list1_id = list1.insert(temp_db)
        
        list2 = ReadingList(name="List 2", description="Second list")
        list2_id = list2.insert(temp_db)
        
        # Add book to both lists
        ReadingListBook(list_id=list1_id, book_id=book_id).insert(temp_db)
        ReadingListBook(list_id=list2_id, book_id=book_id).insert(temp_db)
        
        # Get lists for book
        lists = ReadingListBook.get_lists_for_book(temp_db, book_id)
        assert len(lists) == 2
        assert "List 1" in lists
        assert "List 2" in lists
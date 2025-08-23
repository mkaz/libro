"""Test configuration and fixtures for libro tests."""

import sqlite3
import tempfile
from pathlib import Path
from typing import Generator

import pytest


def init_test_db(db_connection: sqlite3.Connection) -> None:
    """Initialize database tables for testing."""
    cursor = db_connection.cursor()
    
    cursor.execute("""CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            pub_year INTEGER,
            pages INTEGER,
            genre TEXT
        )
    """)
    
    cursor.execute("""CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            date_read DATE,
            rating INTEGER,
            review TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)
    
    cursor.execute("""CREATE TABLE reading_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_date DATE DEFAULT CURRENT_DATE
        )
    """)
    
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
    
    db_connection.commit()


@pytest.fixture
def temp_db() -> Generator[sqlite3.Connection, None, None]:
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        db_path = temp_file.name
    
    # Initialize the database
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    init_test_db(db)
    
    yield db
    
    # Clean up
    db.close()
    Path(db_path).unlink()


@pytest.fixture
def sample_book_data():
    """Sample book data for testing."""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "pub_year": 2023,
        "pages": 300,
        "genre": "fiction"
    }


@pytest.fixture
def sample_review_data():
    """Sample review data for testing."""
    return {
        "rating": 4,
        "date_read": "2023-12-01",
        "review": "Great book!"
    }
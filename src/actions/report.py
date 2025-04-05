# Bar chart of books read by year

from datetime import datetime
import sqlite3
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box


def get_books_by_year(db):
    """Get count of books read per year."""
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT strftime('%Y', date_read) as year, COUNT(*) as count
            FROM books
            WHERE date_read IS NOT NULL
            GROUP BY year
            ORDER BY year
        """
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def report(db, args):
    """Display a bar chart of books read per year."""
    books_by_year = get_books_by_year(db)
    if not books_by_year:
        print("No books found with read dates.")
        return

    console = Console()
    table = Table(show_header=True, title="Books Read by Year", box=box.SIMPLE)
    table.add_column("Year", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Bar", style="blue")

    max_count = max(count for _, count in books_by_year)

    for year, count in books_by_year:
        # Create a bar using block characters
        bar_length = int((count / max_count) * 50)  # Scale to 50 characters
        bar = "▄" * bar_length

        table.add_row(year, str(count), bar)

    console.print(table)

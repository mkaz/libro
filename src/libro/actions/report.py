# Bar chart of books read by year

import sqlite3
from rich.console import Console
from rich.table import Table
from rich import box


def report(db, args):
    """Main report function that routes to specific report types based on args."""
    if args.get("author") is True:
        show_author_report(db, args)
    else:
        show_year_report(db)


def get_books_by_year(db):
    """Get count of books read per year."""
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT strftime('%Y', r.date_read) as year, COUNT(*) as count
            FROM reviews r
            JOIN books b ON r.book_id = b.id
            WHERE r.date_read IS NOT NULL
            GROUP BY year
            ORDER BY year
        """
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def show_author_report(db, args):
    """Display a report of most read authors."""

    limit = args["limit"]
    # If the --limit argument was not provided, args["limit"] will be None.
    # In that case, we default to 3.
    if limit is None:
        limit = 3
    where_clause = (
        "" if args.get("undated") is True else "WHERE r.date_read IS NOT NULL"
    )

    try:
        cursor = db.cursor()
        query = f"""
            SELECT b.author, COUNT(*) as count
            FROM reviews r
            JOIN books b ON r.book_id = b.id
            {where_clause}
            GROUP BY b.author
            HAVING count >= :limit
            ORDER BY count DESC
        """
        cursor.execute(query, {"limit": limit})
        authors = cursor.fetchall()

        if not authors:
            print(f"No authors found with more than {limit} books read.")
            return

        console = Console()
        table = Table(show_header=True, title="Most Read Authors", box=box.SIMPLE)
        table.add_column("Author", style="cyan")
        table.add_column("Books Read", style="green")

        for author, count in authors:
            table.add_row(author, str(count))

        console.print(table)

    except sqlite3.Error as e:
        print(f"Database error: {e}")


def show_year_report(db):
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

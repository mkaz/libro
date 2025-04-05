import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table


def show_books(db, args={}):
    # By year is default
    # Current year is default year if not specified
    year = args.get("year", datetime.now().year)

    books = get_books(db, year)
    if not books:
        print("No books found for the specified year.")
        return

    console = Console()
    table = Table(show_header=True, title=f"Books Read in {year}")
    table.add_column("id")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Rating")
    table.add_column("Date Read")

    # Sort books by genre (fiction first) and then by date
    sorted_books = sorted(books, key=lambda x: (x[5] != "fiction", x[4] or ""))

    current_genre = None
    for book in sorted_books:
        # Add genre separator if genre changes
        if book[5] != current_genre:
            if current_genre is not None:  # Don't add separator before first genre
                table.add_row("", "", "", "", "", style="dim")
            current_genre = book[5]
            table.add_row(
                f"[bold]{current_genre.title()}[/bold]",
                "",
                "",
                "",
                "",
                style="bold cyan",
            )

        # Format the date
        date_str = book[4]  # date_read is the 5th column (index 4)
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%b %d, %Y")
            except ValueError:
                formatted_date = date_str
        else:
            formatted_date = ""

        table.add_row(str(book[0]), book[1], book[2], str(book[3]), formatted_date)

    console.print(table)


def get_books(db, year):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, title, author_firstname || ' ' || author_lastname, rating, date_read, genre
            FROM books
            WHERE strftime('%Y', date_read) = ?
            ORDER BY date_read ASC
        """,
            (str(year),),
        )
        books = cursor.fetchall()
        return books
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

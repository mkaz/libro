import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table


def show_books(db, args={}):
    # By year is default
    # Current year is default year if not specified
    year = args.get("year", datetime.now().year)

    # if id is not none, show book detail
    if args.get("id") is not None:
        show_book_detail(db, args.get("id"))
        return

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
    sorted_books = sorted(
        books, key=lambda x: (x["genre"] != "fiction", x["date_read"] or "")
    )

    ## Count books by genre
    count = {}
    for book in books:
        count[book["genre"]] = count.get(book["genre"], 0) + 1

    current_genre = None
    for book in sorted_books:
        # Add genre separator if genre changes
        if book["genre"] != current_genre:
            if current_genre is not None:  # Don't add separator before first genre
                table.add_row("", "", "", "", "", style="dim")
            current_genre = book["genre"]
            table.add_row(
                "",
                f"[bold]{current_genre.title()} ({count[current_genre]})[/bold]",
                "",
                "",
                "",
                style="bold cyan",
            )

        # Format the date
        date_str = book["date_read"]
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%b %d, %Y")
            except ValueError:
                formatted_date = date_str
        else:
            formatted_date = ""

        table.add_row(
            str(book["id"]),
            book["title"],
            book["author"],
            str(book["rating"]),
            formatted_date,
        )

    console.print(table)


def show_book_detail(db, id):
    cursor = db.cursor()
    cursor.execute(
        """SELECT b.id, b.title, b.author, b.pub_year, b.pages, b.genre,
                  r.rating, r.date_read, r.review
        FROM books b
        LEFT JOIN reviews r ON b.id = r.book_id
        WHERE r.id = ?""",
        (id,),
    )
    book = cursor.fetchone()

    if not book:
        print(f"No book found with ID {id}")
        return

    console = Console()
    table = Table(show_header=True, title="Book Details")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    # Map of column names to display names
    display_names = [
        "ID",
        "Title",
        "Author",
        "Publication Year",
        "Pages",
        "Genre",
        "Rating",
        "Date Read",
        "My Review",
    ]

    for col, value in zip(range(len(display_names)), book):
        table.add_row(display_names[col], str(value))

    console.print(table)


def get_books(db, year):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.id, b.title, b.author, b.genre, r.rating, r.date_read
            FROM reviews r
            LEFT JOIN books b ON r.book_id = b.id
            WHERE strftime('%Y', r.date_read) = ?
            ORDER BY r.date_read ASC
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

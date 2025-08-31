import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table
from libro.models import ReadingListBook


def show_books(db, args={}):
    # if id is not none, show book detail
    if args.get("id") is not None:
        show_book_detail(db, args.get("id"))
        return

    # Check if filtering by author
    if args.get("author"):
        books = get_reviews(db, author_name=args.get("author"))
        table_title = f"Books by {args.get('author')}"
    else:
        # By year is default
        # Current year is default year if not specified
        year = args.get("year", datetime.now().year)
        books = get_reviews(db, year=year)
        table_title = f"Books Read in {year}"
    if not books:
        print("No books found for the specified year.")
        return

    console = Console()
    table = Table(show_header=True, title=table_title)
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Genre")
    table.add_column("Rating")
    table.add_column("Date Read")

    # Books are sorted by date from SQL query, now group them by Fiction/Nonfiction
    fiction_books = []
    nonfiction_books = []

    for book in books:
        if book["genre"] != "nonfiction":
            fiction_books.append(book)
        else:
            nonfiction_books.append(book)

    # Combine with Fiction first, then Nonfiction (both already sorted by date DESC)
    grouped_books = fiction_books + nonfiction_books

    ## Count books by Fiction/Nonfiction grouping
    count = {"Fiction": len(fiction_books), "Nonfiction": len(nonfiction_books)}

    current_group = None
    for book in grouped_books:
        # Determine which group this book belongs to
        book_group = "Fiction" if book["genre"] != "nonfiction" else "Nonfiction"

        # Add group separator if group changes
        if book_group != current_group:
            if current_group is not None:  # Don't add separator before first group
                table.add_row("", "", "", "", "", "", style="dim")
            current_group = book_group
            table.add_row(
                "",
                f"[bold]{current_group} ({count[current_group]})[/bold]",
                "",
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
            str(book["review_id"]),
            book["title"],
            book["author"],
            book["genre"] or "Unknown",
            str(book["rating"]),
            formatted_date,
        )

    console.print(table)


def show_book_detail(db, review_id):
    """Show details for a review (this is what the main show command calls)"""
    cursor = db.cursor()
    cursor.execute(
        """SELECT b.id, b.title, b.author, b.pub_year, b.pages, b.genre,
                  r.id, r.rating, r.date_read, r.review
        FROM books b
        LEFT JOIN reviews r ON b.id = r.book_id
        WHERE r.id = ?""",
        (review_id,),
    )
    book = cursor.fetchone()

    if not book:
        print(f"No review found with Review ID {review_id}")
        return

    console = Console()
    table = Table(
        show_header=True, title=f"Book & Review Details (Review ID: {review_id})"
    )
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    # Map of column names to display names
    display_names = [
        "Book ID",
        "Title",
        "Author",
        "Publication Year",
        "Pages",
        "Genre",
        "Review ID",
        "Rating",
        "Date Read",
        "My Review",
    ]

    for col, value in zip(range(len(display_names)), book):
        display_value = str(value) if value is not None else "Not set"
        table.add_row(display_names[col], display_value)

    console.print(table)

    # Show reading lists that contain this book
    book_id = book[0]  # First column is book ID
    reading_lists = ReadingListBook.get_lists_for_book(db, book_id)

    if reading_lists:
        console.print(f"\n📚 [cyan]Reading Lists:[/cyan] {', '.join(reading_lists)}")


def show_books_only(db, args={}):
    """Show books without review information (for libro book show)"""
    # if id is not none, show book detail
    if args.get("id") is not None:
        show_book_only_detail(db, args.get("id"))
        return

    # Check if filtering by author, title, or year
    author = args.get("author")
    title = args.get("title")
    year = args.get("year")
    year_explicit = args.get("year_explicit", False)

    if author:
        books = get_books_only(db, author_name=author)
        table_title = f"Books by {author}"
    elif title:
        books = get_books_only(db, title=title)
        table_title = f"Books with title containing '{title}'"
    elif year_explicit:
        books = get_books_only(db, year=year)
        table_title = f"Books Published in {year}"
    else:
        # Show most recent books (when no year was explicitly provided)
        books = get_books_only(db)
        table_title = "Recent Books (Latest 20)"

    if not books:
        print("No books found.")
        return

    console = Console()
    table = Table(show_header=True, title=table_title)
    table.add_column("Book ID")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Genre")
    table.add_column("Year")
    table.add_column("Pages")

    for book in books:
        table.add_row(
            str(book["id"]),
            book["title"],
            book["author"],
            book["genre"] or "Not set",
            str(book["pub_year"]) if book["pub_year"] else "Not set",
            str(book["pages"]) if book["pages"] else "Not set",
        )

    console.print(table)


def show_book_only_detail(db, book_id):
    """Show details for a specific book without reviews"""
    cursor = db.cursor()
    cursor.execute(
        """SELECT id, title, author, pub_year, pages, genre
        FROM books
        WHERE id = ?""",
        (book_id,),
    )
    book = cursor.fetchone()

    if not book:
        print(f"No book found with Book ID {book_id}")
        return

    console = Console()
    table = Table(show_header=True, title=f"Book Details (Book ID: {book_id})")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    book_fields = [
        ("Book ID", book["id"]),
        ("Title", book["title"]),
        ("Author", book["author"]),
        ("Publication Year", book["pub_year"]),
        ("Pages", book["pages"]),
        ("Genre", book["genre"]),
    ]

    for field, value in book_fields:
        display_value = str(value) if value is not None else "Not set"
        table.add_row(field, display_value)

    console.print(table)

    # Show reading lists that contain this book
    reading_lists = ReadingListBook.get_lists_for_book(db, book_id)

    if reading_lists:
        console.print(f"\n[cyan]Reading Lists:[/cyan] {', '.join(reading_lists)}")
    else:
        console.print("\n[dim]This book is not in any reading lists.[/dim]")
        console.print("[dim]Add it to a list with: libro list add <list_id>[/dim]")

    # Show reviews for this book
    cursor.execute(
        """SELECT id, rating, date_read
        FROM reviews
        WHERE book_id = ?
        ORDER BY date_read DESC""",
        (book_id,),
    )
    reviews = cursor.fetchall()

    if reviews:
        console.print("\n[cyan]Reviews:[/cyan]")
        review_table = Table()
        review_table.add_column("Review ID")
        review_table.add_column("Rating")
        review_table.add_column("Date Read")

        for review in reviews:
            review_table.add_row(
                str(review["id"]),
                str(review["rating"]) if review["rating"] else "Not rated",
                str(review["date_read"]) if review["date_read"] else "Not set",
            )
        console.print(review_table)
    else:
        console.print("\n📝 [dim]No reviews for this book yet.[/dim]")
        console.print(f"[dim]Add a review with: libro review add {book_id}[/dim]")


def get_books_only(db, author_name=None, year=None, title=None):
    """Get books without review info, optionally filtered by author, publication year, or title"""
    try:
        cursor = db.cursor()
        if author_name:
            cursor.execute(
                """
                SELECT id, title, author, pub_year, pages, genre
                FROM books
                WHERE LOWER(author) LIKE LOWER(?)
                ORDER BY LOWER(title)
            """,
                (f"%{author_name}%",),
            )
        elif year:
            cursor.execute(
                """
                SELECT id, title, author, pub_year, pages, genre
                FROM books
                WHERE pub_year = ?
                ORDER BY LOWER(title)
            """,
                (year,),
            )
        elif title:
            cursor.execute(
                """
                SELECT id, title, author, pub_year, pages, genre
                FROM books
                WHERE LOWER(title) LIKE LOWER(?)
                ORDER BY LOWER(title)
            """,
                (f"%{title}%",),
            )
        else:
            cursor.execute(
                """
                SELECT id, title, author, pub_year, pages, genre
                FROM books
                ORDER BY id DESC
                LIMIT 20
            """
            )
        books = cursor.fetchall()
        return books
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_reviews(db, year=None, author_name=None):
    """Get reviews with book info, optionally filtered by year or author"""
    try:
        cursor = db.cursor()
        if year:
            cursor.execute(
                """
                SELECT r.id as review_id, b.id as book_id, b.title, b.author, b.genre, r.rating, r.date_read
                FROM reviews r
                LEFT JOIN books b ON r.book_id = b.id
                WHERE strftime('%Y', r.date_read) = ?
                ORDER BY r.date_read ASC
            """,
                (str(year),),
            )
        elif author_name:
            cursor.execute(
                """
                SELECT r.id as review_id, b.id as book_id, b.title, b.author, b.genre, r.rating, r.date_read
                FROM reviews r
                LEFT JOIN books b ON r.book_id = b.id
                WHERE LOWER(b.author) LIKE LOWER(?)
                ORDER BY r.date_read ASC
            """,
                (f"%{author_name}%",),
            )
        books = cursor.fetchall()
        return books
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def show_recent_reviews(db, args={}):
    """Show recent reviews (latest 20) or filtered reviews"""
    try:
        cursor = db.cursor()

        # Check for filtering options
        author = args.get("author")
        title = args.get("title")
        year = args.get("year")

        if author:
            cursor.execute(
                """
                SELECT r.id as review_id, b.title, b.author, b.genre, r.rating, r.date_read
                FROM reviews r
                JOIN books b ON r.book_id = b.id
                WHERE LOWER(b.author) LIKE LOWER(?)
                ORDER BY r.date_read ASC
                """,
                (f"%{author}%",),
            )
            table_title = f"Reviews by {author}"
        elif title:
            cursor.execute(
                """
                SELECT r.id as review_id, b.title, b.author, b.genre, r.rating, r.date_read
                FROM reviews r
                JOIN books b ON r.book_id = b.id
                WHERE LOWER(b.title) LIKE LOWER(?)
                ORDER BY r.date_read ASC
                """,
                (f"%{title}%",),
            )
            table_title = f"Reviews for books with title containing '{title}'"
        elif year:
            cursor.execute(
                """
                SELECT r.id as review_id, b.title, b.author, b.genre, r.rating, r.date_read
                FROM reviews r
                JOIN books b ON r.book_id = b.id
                WHERE strftime('%Y', r.date_read) = ?
                ORDER BY r.date_read ASC
                """,
                (str(year),),
            )
            table_title = f"Reviews from {year}"
        else:
            cursor.execute(
                """
                SELECT r.id as review_id, b.title, b.author, b.genre, r.rating, r.date_read
                FROM reviews r
                JOIN books b ON r.book_id = b.id
                ORDER BY r.id DESC
                LIMIT 20
                """
            )
            table_title = "Recent Reviews (Latest 20)"

        reviews = cursor.fetchall()

        if not reviews:
            print("No reviews found.")
            return

        console = Console()
        table = Table(show_header=True, title=table_title)
        table.add_column("Review ID")
        table.add_column("Title")
        table.add_column("Author")
        table.add_column("Genre")
        table.add_column("Rating")
        table.add_column("Date Read")

        for review in reviews:
            # Format the date
            date_str = review["date_read"]
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%b %d, %Y")
                except ValueError:
                    formatted_date = date_str
            else:
                formatted_date = "Not set"

            table.add_row(
                str(review["review_id"]),
                review["title"],
                review["author"],
                review["genre"] or "Not set",
                str(review["rating"]) if review["rating"] else "Not rated",
                formatted_date,
            )

        console.print(table)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

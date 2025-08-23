from pathlib import Path
import csv
import re
from datetime import datetime, date
from libro.models import Book, Review, ReadingList, ReadingListBook
from rich.console import Console


def import_books(db, args):
    f = args["file"]
    print(f"Importing books from {f}")

    # check file exists
    if not Path(f).is_file():
        print(f"File {f} not found")
        return

    # read file
    count = 0
    with open(f, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Author field includes where spacing and tabs, so we need to clean it up
            author = row["Author"].replace("\t", " ").replace("  ", " ").strip()
            while "  " in author:
                author = author.replace("  ", " ")

            # @TODO: Make this a import flag
            # Title field includes series info that is not the title
            # For example: Ender's Game (Ender's Saga, #1)
            raw_title = row["Title"].strip()
            # Regex to capture the title part before parenthesis *only if* the parenthesis contains '#'
            series_pattern = re.compile(r"^(.*?)\s*\([^#]*#.*\)$")
            match = series_pattern.match(raw_title)
            if match:
                # If it matches the series pattern (contains '#'), take the part before the parenthesis
                title = match.group(1).strip()
            else:
                # Otherwise (no parenthesis or parenthesis without '#'), use the raw title as is
                title = raw_title

            # @TODO: Make this a import flag
            # Moar cleanup - annoying non-fiction books have a colon and extra junk to promote.
            # Remove colon and everything after it
            # For example: Eats, Shoots & Leaves: The Zero Tolerance Approach to Punctuation
            title = title.split(":")[0].strip()

            pub_year = row["Original Publication Year"].strip()
            pages = row["Number of Pages"].strip()
            # Note: Ensure 'from datetime import datetime' is present at the top of the file.
            raw_date_read = row["Date Read"].strip()
            date_read = None  # Default to None if empty or invalid
            if raw_date_read:
                try:
                    # Parse the date assuming Goodreads format YYYY/MM/DD
                    date_obj = datetime.strptime(raw_date_read, "%Y/%m/%d")
                    # Format to YYYY-MM-DD, which is suitable for SQLite and the Review model
                    date_read = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    # Handle cases where the date format might be different or invalid
                    print(
                        f"Warning: Could not parse 'Date Read' field ('{raw_date_read}') for {title}. Setting date to None."
                    )
            rating = row["My Rating"].strip()
            review = row["My Review"].strip()

            # There are many lets combine and look for "read"
            # Bookshelves, Bookshelves with positions, Exclusive Shelf into a set
            shelf1 = row["Bookshelves"]
            shelf2 = row["Bookshelves with positions"]
            shelf3 = row["Exclusive Shelf"]
            shelf_str = ",".join([s.strip() for s in [shelf1, shelf2, shelf3] if s])
            shelf_list = shelf_str.split(",")
            shelf = set(shelf_list)

            if "read" in shelf:
                count += 1

                # Create and insert book
                book = Book(
                    title=title,
                    author=author,
                    pub_year=int(pub_year) if pub_year else None,
                    pages=int(pages) if pages else None,
                    genre="fiction",  # Default to fiction, could be improved
                )
                book_id = book.insert(db)

                # Create and insert review
                review_obj = Review(
                    book_id=book_id,
                    date_read=date.fromisoformat(date_read) if date_read else None,
                    rating=int(rating) if rating else None,
                    review=review,
                )
                review_obj.insert(db)

    print(f"Imported {count} books")


def import_csv_to_list(db, args):
    """Import books from CSV file to a specific reading list."""
    console = Console()
    list_id = args.get("id")
    list_name = args.get("name")
    list_description = args.get("description")
    csv_file = args["file"]

    # Validate arguments - either id or name must be provided
    if not list_id and not list_name:
        console.print("[red]Either --id or --name must be provided.[/red]")
        return

    if list_id and list_name:
        console.print("[red]Cannot specify both --id and --name. Choose one.[/red]")
        return

    # Get or create reading list
    if list_id:
        # Use existing list
        reading_list = ReadingList.get_by_id(db, list_id)
        if not reading_list:
            console.print(f"[red]Reading list with ID {list_id} not found.[/red]")
            return
    else:
        # Create new list
        existing_list = ReadingList.get_by_name(db, list_name)
        if existing_list:
            console.print(
                f"[red]A reading list named '{list_name}' already exists.[/red]"
            )
            return

        reading_list = ReadingList(name=list_name, description=list_description)
        list_id = reading_list.insert(db)
        console.print(
            f"[green]Created new reading list '[bold]{list_name}[/bold]'[/green]"
        )
        if list_description:
            console.print(f"Description: {list_description}")
        console.print(f"List ID: {list_id}\n")

    # Check if CSV file exists
    if not Path(csv_file).is_file():
        console.print(f"[red]CSV file '{csv_file}' not found.[/red]")
        return

    console.print(
        f"[blue]Importing books from '{csv_file}' to reading list '{reading_list.name}'[/blue]\n"
    )

    imported_count = 0
    existing_count = 0
    error_count = 0

    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            # Detect if CSV has headers by checking first few lines
            sample = file.read(1024)
            file.seek(0)

            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(sample)

            reader = csv.reader(file)

            # Skip header row if present
            if has_header:
                next(reader)
                console.print("[dim]CSV header detected, skipping first row[/dim]")

            for row_num, row in enumerate(reader, start=2 if has_header else 1):
                if len(row) < 5:
                    console.print(
                        f"[yellow]Row {row_num}: Skipping incomplete row (expected 5 fields, got {len(row)})[/yellow]"
                    )
                    error_count += 1
                    continue

                # Extract fields: Title, Author, Publication Year, Pages, Genre
                title = row[0].strip()
                author = row[1].strip()
                pub_year_str = row[2].strip()
                pages_str = row[3].strip()
                genre = row[4].strip()

                if not title or not author:
                    console.print(
                        f"[yellow]Row {row_num}: Skipping row with missing title or author[/yellow]"
                    )
                    error_count += 1
                    continue

                # Convert numeric fields
                pub_year = None
                if pub_year_str:
                    try:
                        pub_year = int(pub_year_str)
                    except ValueError:
                        console.print(
                            f"[yellow]Row {row_num}: Invalid publication year '{pub_year_str}' for '{title}'[/yellow]"
                        )

                pages = None
                if pages_str:
                    try:
                        pages = int(pages_str)
                    except ValueError:
                        console.print(
                            f"[yellow]Row {row_num}: Invalid pages '{pages_str}' for '{title}'[/yellow]"
                        )

                # Check if book already exists by matching title and author
                existing_book = Book.find_by_title_author(db, title, author)

                if existing_book:
                    book_id = existing_book.id
                    if book_id is None:
                        raise RuntimeError(f"Existing book '{title}' has no ID")
                    console.print(
                        f"[dim]Row {row_num}: Book '{title}' by {author} already exists (ID: {book_id})[/dim]"
                    )
                    existing_count += 1
                else:
                    # Create new book
                    book = Book(
                        title=title,
                        author=author,
                        pub_year=pub_year,
                        pages=pages,
                        genre=genre or None,
                    )
                    book_id = book.insert(db)
                    console.print(
                        f"[green]Row {row_num}: Added new book '{title}' by {author} (ID: {book_id})[/green]"
                    )
                    imported_count += 1

                # Add book to the reading list (check if already in list first)
                cursor = db.cursor()
                cursor.execute(
                    "SELECT id FROM reading_list_books WHERE list_id = ? AND book_id = ?",
                    (list_id, book_id),
                )
                if not cursor.fetchone():
                    reading_list_book = ReadingListBook(
                        list_id=list_id, book_id=book_id
                    )
                    reading_list_book.insert(db)
                    console.print(
                        f"[cyan]  → Added to reading list '{reading_list.name}'[/cyan]"
                    )
                else:
                    console.print(
                        f"[dim]  → Already in reading list '{reading_list.name}'[/dim]"
                    )

    except Exception as e:
        console.print(f"[red]Error reading CSV file: {e}[/red]")
        return

    # Print summary
    console.print("\n[bold]Import Summary:[/bold]")
    console.print(f"  [green]New books imported: {imported_count}[/green]")
    console.print(f"  [yellow]Existing books found: {existing_count}[/yellow]")
    console.print(f"  [red]Errors/skipped rows: {error_count}[/red]")
    console.print(
        f"  [blue]Total books processed: {imported_count + existing_count}[/blue]"
    )
    console.print(
        f"\nAll books have been added to reading list '[cyan]{reading_list.name}[/cyan]'"
    )

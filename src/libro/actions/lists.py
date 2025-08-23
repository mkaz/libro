import sqlite3
from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich import box
from rich.prompt import Confirm

from libro.models import ReadingList, ReadingListBook, Book


style = Style.from_dict(
    {
        "prompt": "ansiyellow",
    }
)


class NonEmptyValidator(Validator):
    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(message="This field cannot be empty")


def manage_lists(db: sqlite3.Connection, args: dict):
    """Main function to route list management commands."""
    action = args.get("list_action")

    match action:
        case "create":
            create_list(db, args)
        case "show":
            show_lists(db, args)
        case "add":
            add_book_to_list(db, args)
        case "remove":
            remove_book_from_list(db, args)
        case "stats":
            show_list_stats(db, args)
        case "edit":
            edit_list(db, args)
        case "delete":
            delete_list(db, args)
        case "import":
            from libro.actions.importer import import_csv_to_list

            import_csv_to_list(db, args)
        case _:
            show_lists(db, args)


def create_list(db: sqlite3.Connection, args: dict):
    """Create a new reading list."""
    console = Console()
    name = args["name"]
    description = args.get("description")

    # Check if list already exists
    existing_list = ReadingList.get_by_name(db, name)
    if existing_list:
        console.print(f"[red]A reading list named '{name}' already exists.[/red]")
        return

    # Create the new list
    reading_list = ReadingList(name=name, description=description)
    list_id = reading_list.insert(db)

    console.print(f"[green]Created reading list '[bold]{name}[/bold]'[/green]")
    if description:
        console.print(f"Description: {description}")
    console.print(f"List ID: {list_id}")


def show_lists(db: sqlite3.Connection, args: dict):
    """Show reading lists or specific list contents."""
    console = Console()
    list_id = args.get("id")

    if list_id:
        # Show specific list contents
        show_specific_list(db, list_id, console)
    else:
        # Show all lists
        show_all_lists(db, console)


def show_all_lists(db: sqlite3.Connection, console: Console):
    """Show all reading lists with summary statistics."""
    lists = ReadingList.get_all(db)

    if not lists:
        console.print("[yellow]No reading lists found.[/yellow]")
        console.print("Create a new list with: [cyan]libro list create <name>[/cyan]")
        return

    table = Table(show_header=True, title="Reading Lists", box=box.ROUNDED)
    table.add_column("ID", justify="center", style="bold cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Total Books", justify="center")
    table.add_column("Read", justify="center", style="green")
    table.add_column("Unread", justify="center", style="red")
    table.add_column("Progress", justify="center")

    for reading_list in lists:
        if reading_list.id is None:
            continue  # Skip lists without IDs
        stats = ReadingListBook.get_list_stats(db, reading_list.id)

        # Create progress bar representation
        progress_text = f"{stats['completion_percentage']:.1f}%"
        if stats["total_books"] > 0:
            progress_bar = "█" * int(stats["completion_percentage"] / 10)
            progress_bar += "░" * (10 - int(stats["completion_percentage"] / 10))
            progress_display = f"{progress_bar} {progress_text}"
        else:
            progress_display = "—"

        table.add_row(
            str(reading_list.id),
            reading_list.name,
            reading_list.description or "",
            str(stats["total_books"]),
            str(stats["books_read"]),
            str(stats["books_unread"]),
            progress_display,
        )

    console.print(table)
    console.print(
        "\n[dim]Use 'libro list show <id>' to see books in a specific list[/dim]"
    )


def show_specific_list(db: sqlite3.Connection, list_id: int, console: Console):
    """Show contents of a specific reading list."""
    reading_list = ReadingList.get_by_id(db, list_id)
    if not reading_list:
        console.print(f"[red]Reading list with ID {list_id} not found.[/red]")
        return

    if reading_list.id is None:
        console.print(f"[red]Reading list '{reading_list.name}' has no ID.[/red]")
        return

    books = ReadingListBook.get_books_in_list(db, reading_list.id)

    if not books:
        console.print(f"[yellow]Reading list '{reading_list.name}' is empty.[/yellow]")
        console.print(f"Add books with: [cyan]libro list add {list_id}[/cyan]")
        return

    # Get statistics
    stats = ReadingListBook.get_list_stats(db, reading_list.id)

    # Create table
    table_title = f"📚 {reading_list.name}"
    if reading_list.description:
        table_title += f" - {reading_list.description}"

    table = Table(show_header=True, title=table_title, box=box.ROUNDED)
    table.add_column("ID", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Title", style="bold")
    table.add_column("Author")
    table.add_column("Genre")
    table.add_column("Rating", justify="center")
    table.add_column("Date Read", justify="center")

    # Sort books: unread first, then by added date
    sorted_books = sorted(books, key=lambda x: (x["is_read"], x["added_date"]))

    for book in sorted_books:
        status = "✅" if book["is_read"] else "📖"
        rating_str = str(book["rating"]) if book["rating"] else "—"
        date_str = book["date_read"] if book["date_read"] else "—"

        # Style rows differently for read vs unread
        row_style = "dim" if book["is_read"] else None

        table.add_row(
            str(book["book_id"]),
            status,
            book["title"],
            book["author"],
            book["genre"] or "",
            rating_str,
            date_str,
            style=row_style,
        )

    console.print(table)

    # Show statistics
    progress_text = f"{stats['completion_percentage']:.1f}%"
    console.print(
        f"\n📊 Progress: [green]{stats['books_read']}[/green] read, "
        f"[red]{stats['books_unread']}[/red] unread "
        f"([cyan]{progress_text}[/cyan] complete)"
    )


def add_book_to_list(db: sqlite3.Connection, args: dict):
    """Add a book to a reading list."""
    console = Console()
    list_id = args["id"]
    book_ids = args.get("book_ids", [])

    # Check if list exists
    reading_list = ReadingList.get_by_id(db, list_id)
    if not reading_list:
        console.print(f"[red]Reading list with ID {list_id} not found.[/red]")
        return

    if reading_list.id is None:
        console.print(f"[red]Reading list '{reading_list.name}' has no ID.[/red]")
        return

    # If book IDs were provided, add existing books
    if book_ids:
        _add_existing_books_to_list(db, reading_list, book_ids, console)
    else:
        # Original behavior: prompt for new book details
        _add_new_book_to_list(db, reading_list, console)


def _add_existing_books_to_list(
    db: sqlite3.Connection,
    reading_list: ReadingList,
    book_ids: list[int],
    console: Console,
):
    """Add existing books by their IDs to a reading list."""
    assert reading_list.id is not None, "Reading list must have an ID"
    added_count = 0
    errors = []

    for book_id in book_ids:
        try:
            # Check if book exists
            book = Book.get_by_id(db, book_id)
            if not book:
                errors.append(f"Book ID {book_id} not found")
                continue

            # Check if book is already in the list
            existing_books = ReadingListBook.get_books_in_list(db, reading_list.id)
            if any(b["book_id"] == book_id for b in existing_books):
                errors.append(
                    f"Book '{book.title}' (ID {book_id}) is already in the list"
                )
                continue

            # Add book to the list
            reading_list_book = ReadingListBook(
                list_id=reading_list.id, book_id=book_id
            )
            reading_list_book.insert(db)

            console.print(
                f"[green]✅ Added '{book.title}' by {book.author} to '{reading_list.name}'[/green]"
            )
            added_count += 1

        except Exception as e:
            errors.append(f"Error adding book ID {book_id}: {str(e)}")

    # Summary
    if added_count > 0:
        console.print(
            f"\n[green]Successfully added {added_count} book(s) to '{reading_list.name}'[/green]"
        )

    if errors:
        console.print("\n[yellow]Issues encountered:[/yellow]")
        for error in errors:
            console.print(f"[red]• {error}[/red]")


def _add_new_book_to_list(
    db: sqlite3.Connection, reading_list: ReadingList, console: Console
):
    """Add a new book to a reading list using interactive prompts."""
    assert reading_list.id is not None, "Reading list must have an ID"
    session: PromptSession[str] = PromptSession(style=style)
    console.print(f"[blue]Adding book to '{reading_list.name}' reading list[/blue]\n")

    try:
        # Get book details
        title = _prompt_with_retry(
            session, "Book title: ", validator=NonEmptyValidator()
        )
        author = _prompt_with_retry(session, "Author: ", validator=NonEmptyValidator())

        # Optional fields
        pub_year_str = session.prompt("Publication year (optional): ")
        pub_year = _convert_to_int_or_none(pub_year_str)

        pages_str = session.prompt("Number of pages (optional): ")
        pages = _convert_to_int_or_none(pages_str)

        genre = session.prompt("Genre (optional): ").strip().lower() or None

        # Create the book
        book = Book(
            title=title,
            author=author,
            pub_year=pub_year,
            pages=pages,
            genre=genre,
        )
        book_id = book.insert(db)

        # Add book to the list
        reading_list_book = ReadingListBook(list_id=reading_list.id, book_id=book_id)
        reading_list_book.insert(db)

        console.print(
            f"\n[green]✅ Added '{title}' by {author} to '{reading_list.name}' list[/green]"
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled adding book to list.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error adding book to list: {e}[/red]")


def remove_book_from_list(db: sqlite3.Connection, args: dict):
    """Remove a book from a reading list."""
    console = Console()
    list_id = args["id"]
    book_id = args["book_id"]

    # Check if list exists
    reading_list = ReadingList.get_by_id(db, list_id)
    if not reading_list:
        console.print(f"[red]Reading list with ID {list_id} not found.[/red]")
        return

    if reading_list.id is None:
        console.print(f"[red]Reading list '{reading_list.name}' has no ID.[/red]")
        return

    # Check if book exists in the list
    books = ReadingListBook.get_books_in_list(db, reading_list.id)
    book_in_list = next((b for b in books if b["book_id"] == book_id), None)

    if not book_in_list:
        console.print(
            f"[red]Book ID {book_id} not found in list '{reading_list.name}'.[/red]"
        )
        return

    # Confirm removal
    if Confirm.ask(
        f"Remove '{book_in_list['title']}' by {book_in_list['author']} from '{reading_list.name}'?"
    ):
        ReadingListBook.remove_book_from_list(db, reading_list.id, book_id)
        console.print(f"[green]✅ Removed book from '{reading_list.name}' list[/green]")
    else:
        console.print("[yellow]Cancelled.[/yellow]")


def show_list_stats(db: sqlite3.Connection, args: dict):
    """Show statistics for reading lists."""
    console = Console()
    list_id = args.get("id")

    if list_id:
        # Show stats for specific list
        show_specific_list_stats(db, list_id, console)
    else:
        # Show stats for all lists
        show_all_list_stats(db, console)


def show_specific_list_stats(db: sqlite3.Connection, list_id: int, console: Console):
    """Show detailed statistics for a specific reading list."""
    reading_list = ReadingList.get_by_id(db, list_id)
    if not reading_list:
        console.print(f"[red]Reading list with ID {list_id} not found.[/red]")
        return

    if reading_list.id is None:
        console.print(f"[red]Reading list '{reading_list.name}' has no ID.[/red]")
        return

    stats = ReadingListBook.get_list_stats(db, reading_list.id)

    console.print(f"[bold]📊 Statistics for '{reading_list.name}'[/bold]\n")

    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Total Books", str(stats["total_books"]))
    table.add_row("Books Read", f"[green]{stats['books_read']}[/green]")
    table.add_row("Books Unread", f"[red]{stats['books_unread']}[/red]")
    table.add_row("Completion", f"[cyan]{stats['completion_percentage']:.1f}%[/cyan]")

    console.print(table)

    # Progress bar
    if stats["total_books"] > 0:
        console.print("\n[bold]Progress:[/bold]")
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task(f"{reading_list.name}", total=stats["total_books"])
            progress.update(task, completed=stats["books_read"])


def show_all_list_stats(db: sqlite3.Connection, console: Console):
    """Show summary statistics for all reading lists."""
    lists = ReadingList.get_all(db)

    if not lists:
        console.print("[yellow]No reading lists found.[/yellow]")
        return

    console.print("[bold]📊 Reading List Statistics[/bold]\n")

    total_books = 0
    total_read = 0

    for reading_list in lists:
        if reading_list.id is None:
            continue  # Skip lists without IDs
        stats = ReadingListBook.get_list_stats(db, reading_list.id)
        total_books += stats["total_books"]
        total_read += stats["books_read"]

        console.print(
            f"[cyan]{reading_list.name}[/cyan]: {stats['books_read']}/{stats['total_books']} books ({stats['completion_percentage']:.1f}%)"
        )

    overall_percentage = (total_read / total_books * 100) if total_books > 0 else 0
    console.print(
        f"\n[bold]Overall Progress:[/bold] {total_read}/{total_books} books ({overall_percentage:.1f}%)"
    )


def edit_list(db: sqlite3.Connection, args: dict):
    """Edit a reading list's name and/or description."""
    console = Console()
    session: PromptSession[str] = PromptSession(style=style)
    list_id = args["id"]
    new_name = args.get("name")
    new_description = args.get("description")

    # Check if list exists
    reading_list = ReadingList.get_by_id(db, list_id)
    if not reading_list:
        console.print(f"[red]Reading list with ID {list_id} not found.[/red]")
        return

    console.print(f"[blue]Editing reading list '{reading_list.name}'[/blue]\n")

    try:
        # If arguments not provided via CLI, prompt for them
        if new_name is None:
            current_name_display = f"[dim](current: {reading_list.name})[/dim]"
            console.print(f"Name {current_name_display}")
            new_name = session.prompt(
                "New name (press Enter to keep current): "
            ).strip()
            if not new_name:
                new_name = reading_list.name

        if new_description is None:
            current_desc_display = (
                f"[dim](current: {reading_list.description or 'None'})[/dim]"
            )
            console.print(f"Description {current_desc_display}")
            new_description = session.prompt(
                "New description (press Enter to keep current): "
            ).strip()
            if not new_description:
                new_description = reading_list.description

        # Check if new name conflicts with existing lists (excluding current list)
        if new_name != reading_list.name:
            existing_list = ReadingList.get_by_name(db, new_name)
            if existing_list and existing_list.id != reading_list.id:
                console.print(
                    f"[red]A reading list named '{new_name}' already exists.[/red]"
                )
                return

        # Update the reading list
        reading_list.name = new_name
        reading_list.description = new_description if new_description else None
        reading_list.update(db)

        console.print(
            f"\n[green]✅ Updated reading list '[bold]{new_name}[/bold]'[/green]"
        )
        if new_description:
            console.print(f"Description: {new_description}")

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled editing reading list.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error editing reading list: {e}[/red]")


def delete_list(db: sqlite3.Connection, args: dict):
    """Delete a reading list."""
    console = Console()
    list_id = args["id"]

    # Check if list exists
    reading_list = ReadingList.get_by_id(db, list_id)
    if not reading_list:
        console.print(f"[red]Reading list with ID {list_id} not found.[/red]")
        return

    if reading_list.id is None:
        console.print(f"[red]Reading list '{reading_list.name}' has no ID.[/red]")
        return

    # Get list stats to show user what they're deleting
    stats = ReadingListBook.get_list_stats(db, reading_list.id)

    console.print(
        f"[yellow]This will delete the reading list '{reading_list.name}' containing {stats['total_books']} books.[/yellow]"
    )
    console.print(
        "[dim]Note: The books themselves will not be deleted, only their association with this list.[/dim]"
    )

    if Confirm.ask(
        f"Are you sure you want to delete the '{reading_list.name}' reading list?"
    ):
        reading_list.delete(db)
        console.print(f"[green]✅ Deleted reading list '{reading_list.name}'[/green]")
    else:
        console.print("[yellow]Cancelled.[/yellow]")


def _prompt_with_retry(session: PromptSession, message: str, validator=None):
    """Helper function to prompt with retry on validation error."""
    while True:
        try:
            return session.prompt(message, validator=validator)
        except ValidationError:
            continue
        except KeyboardInterrupt:
            raise


def _convert_to_int_or_none(value_str: str) -> int | None:
    """Helper function to convert string to int or None."""
    try:
        return int(value_str.strip()) if value_str.strip() else None
    except ValueError:
        return None

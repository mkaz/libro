"""TUI interface for Libro using Textual"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    Button,
    Input,
    TextArea,
    Select,
)
from textual.screen import ModalScreen
from textual.binding import Binding

from libro.actions.show import get_reviews
from libro.models import ReadingListBook, Book, Review


class BookDetailScreen(ModalScreen):
    """Modal screen to display book and review details"""

    CSS = """
    BookDetailScreen {
        align: center middle;
    }
    
    .detail-container {
        width: 80;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    .detail-table {
        height: auto;
        margin-bottom: 1;
    }
    
    .close-button {
        width: 100%;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
    ]

    def __init__(self, db_path: str, review_id: int):
        super().__init__()
        self.db_path = db_path
        self.review_id = review_id

    def compose(self) -> ComposeResult:
        """Create the book detail view"""
        with Container(classes="detail-container"):
            yield Label(f"Review Details - ID: {self.review_id}", classes="title")
            yield DataTable(id="detail_table", classes="detail-table")
            yield Button("Close", id="close_button", classes="close-button")

    def on_mount(self) -> None:
        """Load book details when screen opens"""
        self.load_book_details()

    def load_book_details(self) -> None:
        """Load and display book and review details"""
        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            # Get book and review details (same query as CLI show command)
            cursor = db.cursor()
            cursor.execute(
                """SELECT b.id, b.title, b.author, b.pub_year, b.pages, b.genre,
                          r.id, r.rating, r.date_read, r.review
                FROM books b
                LEFT JOIN reviews r ON b.id = r.book_id
                WHERE r.id = ?""",
                (self.review_id,),
            )
            book_data = cursor.fetchone()

            if not book_data:
                self.notify(f"No review found with ID {self.review_id}")
                self.app.pop_screen()
                return

            # Set up the detail table
            table = self.query_one("#detail_table", DataTable)
            table.add_column("Field", width=20)
            table.add_column("Value", width=50)

            # Field mappings
            display_data = [
                ("Book ID", book_data[0]),
                ("Title", book_data[1]),
                ("Author", book_data[2]),
                ("Publication Year", book_data[3]),
                ("Pages", book_data[4]),
                ("Genre", book_data[5]),
                ("Review ID", book_data[6]),
                ("Rating", book_data[7]),
                ("Date Read", book_data[8]),
                ("My Review", book_data[9]),
            ]

            for field, value in display_data:
                display_value = str(value) if value is not None else "Not set"
                table.add_row(field, display_value)

            # Show reading lists that contain this book
            book_id = book_data[0]
            reading_lists = ReadingListBook.get_lists_for_book(db, book_id)

            if reading_lists:
                table.add_row("Reading Lists", ", ".join(reading_lists))

        except sqlite3.Error as e:
            self.notify(f"Database error: {e}")
        finally:
            if "db" in locals():
                db.close()

    def on_button_pressed(self, event) -> None:
        """Handle button presses"""
        if event.button.id == "close_button":
            self.action_close()

    def action_close(self) -> None:
        """Close the detail screen"""
        self.app.pop_screen()


class AddBookScreen(ModalScreen):
    """Modal screen for adding a new book and review"""

    CSS = """
    AddBookScreen {
        align: center middle;
    }
    
    .form-container {
        width: 80;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    .form-section {
        margin-bottom: 1;
    }
    
    .form-field {
        margin-bottom: 1;
    }
    
    .form-buttons {
        width: 100%;
        margin-top: 1;
    }
    
    .button-row {
        width: 100%;
        height: 3;
    }
    
    Input, Select, TextArea {
        width: 100%;
    }
    
    TextArea {
        height: 4;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        """Create the add book form"""
        with Container(classes="form-container"):
            yield Label("Add New Book & Review", classes="title")

            # Book Information Section
            with Container(classes="form-section"):
                yield Label("[bold cyan]Book Information[/bold cyan]")
                with Container(classes="form-field"):
                    yield Label("Title *")
                    yield Input(placeholder="Enter book title", id="title_input")

                with Container(classes="form-field"):
                    yield Label("Author *")
                    yield Input(placeholder="Enter author name", id="author_input")

                with Container(classes="form-field"):
                    yield Label("Publication Year")
                    yield Input(placeholder="YYYY", id="year_input")

                with Container(classes="form-field"):
                    yield Label("Pages")
                    yield Input(placeholder="Number of pages", id="pages_input")

                with Container(classes="form-field"):
                    yield Label("Genre")
                    yield Select(
                        [
                            ("", ""),
                            ("fiction", "Fiction"),
                            ("non-fiction", "Non-Fiction"),
                            ("mystery", "Mystery"),
                            ("science-fiction", "Science Fiction"),
                            ("fantasy", "Fantasy"),
                            ("romance", "Romance"),
                            ("thriller", "Thriller"),
                            ("biography", "Biography"),
                            ("history", "History"),
                            ("philosophy", "Philosophy"),
                            ("other", "Other"),
                        ],
                        id="genre_select",
                    )

            # Review Information Section
            with Container(classes="form-section"):
                yield Label("[bold cyan]Review Information[/bold cyan]")
                with Container(classes="form-field"):
                    yield Label("Date Read")
                    yield Input(placeholder="YYYY-MM-DD", id="date_input")

                with Container(classes="form-field"):
                    yield Label("Rating (1-5)")
                    yield Input(placeholder="1-5", id="rating_input")

                with Container(classes="form-field"):
                    yield Label("Your Review")
                    yield TextArea(id="review_textarea")

            # Buttons
            with Horizontal(classes="form-buttons"):
                yield Button("Save", id="save_button", variant="primary")
                yield Button("Cancel", id="cancel_button")

    def on_button_pressed(self, event) -> None:
        """Handle button presses"""
        if event.button.id == "save_button":
            self.action_save()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def action_save(self) -> None:
        """Save the new book and review"""
        # Get form values
        title = self.query_one("#title_input", Input).value.strip()
        author = self.query_one("#author_input", Input).value.strip()
        year_str = self.query_one("#year_input", Input).value.strip()
        pages_str = self.query_one("#pages_input", Input).value.strip()
        genre_value = self.query_one("#genre_select", Select).value
        genre = str(genre_value) if genre_value else None
        date_str = self.query_one("#date_input", Input).value.strip()
        rating_str = self.query_one("#rating_input", Input).value.strip()
        review_text = self.query_one("#review_textarea", TextArea).text.strip()

        # Validate required fields
        if not title:
            self.notify("Title is required")
            return
        if not author:
            self.notify("Author is required")
            return

        # Validate and convert numeric fields
        pub_year = None
        if year_str:
            try:
                pub_year = int(year_str)
                if pub_year < 0 or pub_year > datetime.now().year + 10:
                    self.notify("Invalid publication year")
                    return
            except ValueError:
                self.notify("Publication year must be a number")
                return

        pages = None
        if pages_str:
            try:
                pages = int(pages_str)
                if pages < 0:
                    self.notify("Pages must be positive")
                    return
            except ValueError:
                self.notify("Pages must be a number")
                return

        rating = None
        if rating_str:
            try:
                rating = int(rating_str)
                if rating < 1 or rating > 5:
                    self.notify("Rating must be between 1 and 5")
                    return
            except ValueError:
                self.notify("Rating must be a number")
                return

        # Validate date format
        date_read = None
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                date_read = date_obj.date()
            except ValueError:
                self.notify("Date must be in YYYY-MM-DD format")
                return

        # Save to database
        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            # Create and insert book
            book = Book(
                title=title,
                author=author,
                pub_year=pub_year,
                pages=pages,
                genre=genre,
            )
            book_id = book.insert(db)

            # Create and insert review
            review = Review(
                book_id=book_id,
                date_read=date_read,
                rating=rating,
                review=review_text if review_text else None,
            )
            review.insert(db)

            self.notify(f"Successfully added '{title}'!")

            # Refresh the main screen before closing
            main_screen = self.app.screen_stack[0]  # Main screen is at the bottom
            if hasattr(main_screen, "load_books_data"):
                main_screen.load_books_data()

            self.app.pop_screen()

        except sqlite3.Error as e:
            self.notify(f"Database error: {e}")
        except Exception as e:
            self.notify(f"Error: {e}")
        finally:
            if "db" in locals():
                db.close()

    def action_cancel(self) -> None:
        """Cancel adding book"""
        self.app.pop_screen()


class LibroTUI(App):
    """Main TUI application for Libro"""

    CSS = """
    Screen {
        background: $background;
    }
    
    .header {
        dock: top;
        height: 3;
        background: $primary;
        content-align: center middle;
        color: $text;
    }
    
    .main-container {
        height: 1fr;
        padding: 1;
    }
    
    .footer-menu {
        dock: bottom;
        height: 3;
        background: $surface;
        color: $text;
        content-align: center middle;
    }
    
    DataTable {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("a", "add_book", "Add Book"),
        Binding("b", "books_view", "Books"),
        Binding("l", "lists_view", "Lists"),
        Binding("enter", "view_details", "View Details"),
        Binding("question_mark", "help", "Help"),
    ]

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self.current_year = datetime.now().year

    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header()

        with Container(classes="header"):
            yield Label(f"Libro - Books Read in {self.current_year}", classes="title")

        with Container(classes="main-container"):
            yield DataTable(id="books_table")

        with Container(classes="footer-menu"):
            yield Label(
                "q: Quit | r: Refresh | a: Add Book | b: Books | l: Lists | ?: Help"
            )

    def on_mount(self) -> None:
        """Initialize the table when the app starts"""
        self.theme = "nord"
        self.load_books_data()

    def load_books_data(self) -> None:
        """Load and display books read in current year"""
        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            # Get books for current year (same logic as CLI report command)
            books = get_reviews(db, year=self.current_year)

            table = self.query_one("#books_table", DataTable)
            table.clear(columns=True)

            # Add columns
            table.add_column("Review ID", width=10)
            table.add_column("Title", width=30)
            table.add_column("Author", width=25)
            table.add_column("Genre", width=15)
            table.add_column("Rating", width=8)
            table.add_column("Date Read", width=12)

            if not books:
                table.add_row("No books found for current year", "", "", "", "", "")
                return

            # Group by genre and add rows
            current_genre = None
            genre_counts: dict[str, int] = {}
            for book in books:
                genre_key = book["genre"] or "Unknown"
                genre_counts[genre_key] = genre_counts.get(genre_key, 0) + 1

            for book in books:
                # Add genre separator if genre changes
                if book["genre"] != current_genre:
                    if current_genre is not None:
                        table.add_row("", "", "", "", "", "")  # Empty separator row

                    current_genre = book["genre"]
                    genre_display = (
                        current_genre.title() if current_genre else "Unknown"
                    )
                    genre_key = current_genre or "Unknown"
                    genre_header = f"{genre_display} ({genre_counts[genre_key]})"
                    table.add_row("", genre_header, "", "", "", "")

                # Format date
                date_str = book["date_read"]
                if date_str:
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%b %d")
                    except ValueError:
                        formatted_date = date_str
                else:
                    formatted_date = ""

                table.add_row(
                    str(book["review_id"]),
                    book["title"],
                    book["author"],
                    book["genre"] or "",
                    str(book["rating"]) if book["rating"] else "",
                    formatted_date,
                )

        except sqlite3.Error as e:
            table = self.query_one("#books_table", DataTable)
            table.clear(columns=True)
            table.add_column("Error", width=50)
            table.add_row(f"Database error: {e}")
        finally:
            if "db" in locals():
                db.close()

    async def action_quit(self) -> None:
        """Exit the application"""
        self.exit()

    def action_refresh(self) -> None:
        """Refresh the current view"""
        self.load_books_data()

    def action_view_details(self) -> None:
        """View details of the selected book"""
        table = self.query_one("#books_table", DataTable)

        if table.cursor_row is None:
            self.notify("No row selected")
            return

        # Get the selected row data
        row_data = table.get_row_at(table.cursor_row)

        if not row_data or len(row_data) == 0:
            self.notify("Invalid selection")
            return

        # The first column should be the Review ID
        review_id_str = str(row_data[0])

        # Skip empty rows and genre headers
        if not review_id_str or review_id_str == "":
            self.notify("Select a book row to view details")
            return

        try:
            review_id = int(review_id_str)
            # Open the book detail screen
            self.push_screen(BookDetailScreen(self.db_path, review_id))
        except ValueError:
            self.notify("Select a book row to view details")
            return

    def action_add_book(self) -> None:
        """Add a new book and review"""
        self.push_screen(AddBookScreen(self.db_path))

    def action_books_view(self) -> None:
        """Switch to books-only view (placeholder for now)"""
        self.notify("Books view coming soon!")

    def action_lists_view(self) -> None:
        """Switch to reading lists view (placeholder for now)"""
        self.notify("Lists view coming soon!")

    def action_help(self) -> None:
        """Show help dialog (placeholder for now)"""
        self.notify("Help: Use arrow keys to navigate, Enter to select, q to quit")


def launch_tui(db_path: str) -> None:
    """Launch the TUI application"""
    app = LibroTUI(db_path)
    app.run()

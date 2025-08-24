"""Book detail screen for displaying book and review information"""

import sqlite3
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, DataTable, Label
from textual.screen import ModalScreen
from textual.binding import Binding

from libro.models import ReadingListBook


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

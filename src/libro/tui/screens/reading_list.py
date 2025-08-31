"""Reading list screen for displaying books in a specific list"""

import sqlite3
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Label
from textual.screen import ModalScreen
from textual.binding import Binding

from libro.models import ReadingList, ReadingListBook


class ReadingListScreen(ModalScreen):
    """Modal screen to display books in a specific reading list"""

    CSS = """
    ReadingListScreen {
        align: center middle;
    }

    .list-container {
        width: 95;
        height: 45;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    .list-header {
        color: $text;
        background: $accent;
        padding: 0 1;
        margin: 0 0 1 0;
        text-style: bold;
    }

    .list-table {
        height: 1fr;
        margin: 1 0;
    }

    .stats-row {
        margin: 1 0 0 0;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "view_book", "View Book"),
    ]

    def __init__(self, db_path: str, list_id: int):
        super().__init__()
        self.db_path = db_path
        self.list_id = list_id

    def compose(self) -> ComposeResult:
        """Create the reading list view"""
        with Container(classes="list-container"):
            yield Label("Loading...", classes="list-header", id="list_header")
            yield DataTable(cursor_type="row", classes="list-table", id="list_table")
            yield Label("", classes="stats-row", id="stats_label")

    def on_mount(self) -> None:
        """Load reading list details when screen opens"""
        self.load_list_details()

    def load_list_details(self) -> None:
        """Load and display reading list contents"""
        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            # Get reading list details
            reading_list = ReadingList.get_by_id(db, self.list_id)
            if not reading_list:
                self.notify(f"Reading list with ID {self.list_id} not found")
                self.app.pop_screen()
                return

            if reading_list.id is None:
                self.notify("Reading list has no ID")
                self.app.pop_screen()
                return

            # Update header
            header_text = f"📚 {reading_list.name}"
            if reading_list.description:
                header_text += f" - {reading_list.description}"

            header_label = self.query_one("#list_header", Label)
            header_label.update(header_text)

            # Get books in this list
            books = ReadingListBook.get_books_in_list(db, reading_list.id)

            # Set up the table
            table = self.query_one("#list_table", DataTable)
            table.clear(columns=True)
            table.add_column("ID", width=6)
            table.add_column("", width=4)
            table.add_column("Title", width=30)
            table.add_column("Author", width=25)
            table.add_column("Year", width=8)

            if not books:
                table.add_row("", "", "No books in this list", "", "")
            else:
                # Sort books: unread first, then by added date
                sorted_books = sorted(
                    books, key=lambda x: (x["is_read"], x["added_date"])
                )

                for book in sorted_books:
                    status = "✅" if book["is_read"] else ""

                    table.add_row(
                        str(book["book_id"]),
                        status,
                        book["title"],
                        book["author"],
                        str(book["pub_year"]) if book["pub_year"] else "",
                        key=str(
                            book["book_id"]
                        ),  # Use book_id as row key for navigation
                    )

            # Get and display statistics
            stats = ReadingListBook.get_list_stats(db, reading_list.id)
            progress_text = f"{stats['completion_percentage']:.1f}%"
            stats_text = (
                f"📊 Progress: {stats['books_read']} read, "
                f"{stats['books_unread']} unread ({progress_text} complete)"
            )

            stats_label = self.query_one("#stats_label", Label)
            stats_label.update(stats_text)

        except sqlite3.Error as e:
            self.notify(f"Database error: {e}")
        finally:
            if "db" in locals():
                db.close()

    def action_view_book(self) -> None:
        """View details of the selected book"""
        table = self.query_one("#list_table", DataTable)

        row_data = table.get_row_at(table.cursor_row)
        if not row_data or len(row_data) == 0:
            self.notify("Invalid selection")
            return

        # Get the book ID from the first column
        book_id_str = str(row_data[0])
        if not book_id_str or book_id_str == "":
            self.notify("No book to view")
            return

        try:
            book_id = int(book_id_str)

            # Find a review for this book to show in book detail screen
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(
                "SELECT id FROM reviews WHERE book_id = ? ORDER BY date_read DESC LIMIT 1",
                (book_id,),
            )
            review = cursor.fetchone()
            db.close()

            if review:
                from .book_detail import BookDetailScreen

                self.app.push_screen(BookDetailScreen(self.db_path, review["id"]))
            else:
                # For books without reviews, show book information in a simple way
                self.notify("No review found for this book")

        except ValueError:
            self.notify("Invalid book ID")
        except sqlite3.Error as e:
            self.notify(f"Database error: {e}")

    def on_data_table_row_selected(self, event) -> None:
        """Handle row selection in the data table"""
        self.action_view_book()

    def action_close(self) -> None:
        """Close the reading list screen"""
        self.app.pop_screen()

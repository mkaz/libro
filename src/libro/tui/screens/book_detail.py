"""Book detail screen for displaying book and review information"""

import sqlite3
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Label, TextArea
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
        padding: 0 1 1 1;
    }

    .section-card {
        border: round $accent;
        padding: 0 1 1 1;
        margin: 1 0;
        height: auto;
    }

    .section-header {
        color: $text;
        background: $accent;
        padding: 0 1;
        margin: -1 -1 1 -1;
        text-style: bold;
    }

    .field-row {
        margin: 0 1;
    }

    .review {
        height: 6;
    }

    .close-button {
        width: 100%;
        margin-top: 1;
    }

    .field-row Button {
        width: 100%;
        text-align: left;
        background: $surface;
        border: none;
        height: 1;
        margin: 0;
        padding: 0 1;
    }

    .field-row Button:hover {
        background: $primary-lighten-1;
        color: $text;
    }

    .field-row Button:focus {
        background: $primary;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("e", "edit", "Edit"),
    ]

    def __init__(self, db_path: str, review_id: int):
        super().__init__()
        self.db_path = db_path
        self.review_id = review_id
        self.reading_lists: list[tuple[int, str]] = []

    def compose(self) -> ComposeResult:
        """Create the book detail view"""
        with Container(classes="detail-container"):
            yield Label(f"Book & Review Details - Review ID: {self.review_id}")

            # Book Details Card
            with Container(classes="section-card", id="book_section"):
                yield Label("Book Information", classes="section-header")

            # Review Details Card
            with Container(classes="section-card", id="review_section"):
                yield Label("Review Information", classes="section-header")

            # Reading Lists Card
            with Container(classes="section-card", id="lists_section"):
                yield Label("Reading Lists", classes="section-header")

            yield Button("Close", id="close_button", classes="close-button")

    def on_mount(self) -> None:
        """Load book details when screen opens"""
        self.load_book_details()

    def load_book_details(self) -> None:
        """Load and display book and review details in cards"""
        # Clear existing content first
        book_section = self.query_one("#book_section", Container)
        review_section = self.query_one("#review_section", Container)
        lists_section = self.query_one("#lists_section", Container)

        # Remove all children except the header labels
        for child in list(book_section.children)[1:]:  # Keep first child (header)
            child.remove()
        for child in list(review_section.children)[1:]:  # Keep first child (header)
            child.remove()
        for child in list(lists_section.children)[1:]:  # Keep first child (header)
            child.remove()

        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            # Get book and review details
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

            # Populate Book Information card
            book_section = self.query_one("#book_section", Container)
            book_fields = [
                ("Book ID", book_data[0]),
                ("Title", book_data[1]),
                ("Author", book_data[2]),
                ("Publication Year", book_data[3] if book_data[3] else "Unknown"),
                ("Pages", book_data[4] if book_data[4] else "Unknown"),
                ("Genre", book_data[5] if book_data[5] else "Unknown"),
            ]

            for field, value in book_fields:
                book_section.mount(Label(f"{field}: {value}", classes="field-row"))

            # Populate Review Information card
            review_section = self.query_one("#review_section", Container)
            review_fields = [
                ("Review ID", book_data[6]),
                ("Rating", f"{book_data[7]}/5" if book_data[7] else "Not rated"),
                ("Date Read", book_data[8] if book_data[8] else "Not set"),
            ]

            for field, value in review_fields:
                review_section.mount(Label(f"{field}: {value}", classes="field-row"))

            # Add review text if it exists
            if book_data[9]:
                review_section.mount(Label("Review:", classes="field-row"))
                review_section.mount(
                    TextArea(
                        f"{book_data[9]}",
                        classes="review",
                        read_only=True,
                    )
                )
            else:
                review_section.mount(
                    Label("Review: No review written", classes="field-row")
                )

            # Populate Reading Lists card
            lists_section = self.query_one("#lists_section", Container)
            book_id = book_data[0]
            self.reading_lists = ReadingListBook.get_lists_with_ids_for_book(
                db, book_id
            )

            if self.reading_lists:
                for list_id, list_name in self.reading_lists:
                    button = Button(
                        f"📚 {list_name}",
                        id=f"list_button_{list_id}",
                        classes="field-row",
                    )
                    button.styles.width = "100%"
                    button.styles.text_align = "left"
                    lists_section.mount(button)
            else:
                lists_section.mount(
                    Label("Not in any reading lists", classes="field-row")
                )

        except sqlite3.Error as e:
            self.notify(f"Database error: {e}")
        finally:
            if "db" in locals():
                db.close()

    def on_button_pressed(self, event) -> None:
        """Handle button presses"""
        if event.button.id == "close_button":
            self.action_close()
        elif event.button.id and event.button.id.startswith("list_button_"):
            # Extract list ID from button ID
            try:
                list_id_str = event.button.id.replace("list_button_", "")
                list_id = int(list_id_str)
                self.open_reading_list(list_id)
            except ValueError:
                self.notify("Invalid reading list ID")

    def open_reading_list(self, list_id: int) -> None:
        """Open the reading list screen"""
        from .reading_list import ReadingListScreen

        self.app.push_screen(ReadingListScreen(self.db_path, list_id))

    def action_close(self) -> None:
        """Close the detail screen"""
        self.app.pop_screen()

    def action_edit(self) -> None:
        """Open edit screen for this book and review"""
        from .edit_book import EditBookScreen

        self.app.push_screen(EditBookScreen(self.db_path, self.review_id))

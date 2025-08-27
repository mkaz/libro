"""Add book screen with form for creating new books and reviews"""

import sqlite3
from datetime import datetime
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Label, Select, TextArea
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.suggester import Suggester

from libro.models import Book, Review


class AuthorSuggester(Suggester):
    """Suggester for author names based on existing books in database"""

    def __init__(self, db_path: str):
        super().__init__(use_cache=True, case_sensitive=False)
        self.db_path = db_path
        self._authors: list[str] | None = None

    def _get_authors(self) -> list[str]:
        """Get all unique authors from the database"""
        if self._authors is None:
            try:
                db = sqlite3.connect(self.db_path)
                cursor = db.cursor()
                cursor.execute("""
                    SELECT DISTINCT author
                    FROM books
                    WHERE author IS NOT NULL AND author != ''
                    ORDER BY author
                """)
                self._authors = [row[0] for row in cursor.fetchall()]
            except sqlite3.Error:
                self._authors = []
            finally:
                if "db" in locals():
                    db.close()
        return self._authors

    async def get_suggestion(self, value: str) -> str | None:
        """Get author suggestion based on partial input"""
        if not value:
            return None

        authors = self._get_authors()
        value_lower = value.lower()

        # Find the first author that starts with the input value
        for author in authors:
            if author.lower().startswith(value_lower):
                return author

        return None


class AddBookScreen(ModalScreen):
    """Modal screen for adding a new book and review"""

    CSS = """
    AddBookScreen {
        align: center middle;
    }

    .form-container {
        width: 80;
        background: $surface;
        border: thick $primary;
        padding: 1;
        height: 48;
    }

    .section-card-book {
        border: round $accent;
        padding: 0 1;
        margin: 1 0;
        height: 17;
    }

    .section-card-review {
        border: round $accent;
        padding: 0 1;
        margin: 1 0;
        height: 22;
    }

    Input {
        margin: 0;
        padding: 0 1;
    }

    .mt-1 {
        margin-top: 1;
    }

    .mr-1 {
        margin-right: 2;
    }

    .ml-1 {
        margin-left: 2;
    }

    .mb-1 {
        margin-bottom: 1;
    }

    .horiz-row {
        margin-top: 1;
        height: 3;
    }

    TextArea {
        height: 8;
    }

    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self.genre_options = self._get_genre_options()
        self.author_suggester = AuthorSuggester(db_path)

    def _get_genre_options(self):
        """Get genre options from existing books in database"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT DISTINCT genre
                FROM books
                WHERE genre IS NOT NULL AND genre != ''
                ORDER BY genre
            """
            )
            genres = [("", "")]  # Empty option first
            for row in cursor.fetchall():
                genre = row[0]
                genres.append((genre, genre.title()))
            return genres
        except sqlite3.Error:
            # Fallback to basic genres if DB query fails
            return [("", ""), ("fiction", "fiction"), ("nonfiction", "nonfiction")]
        finally:
            if "db" in locals():
                db.close()

    def compose(self) -> ComposeResult:
        """Create the add book form"""
        with Container(classes="form-container"):
            yield Label("Add New Book & Review")

            # Book Information Card
            with Container(classes="section-card-book"):
                yield Label("[bold cyan]Book Information[/bold cyan]")
                yield Label("Title *", classes="mt-1")
                yield Input(
                    placeholder="Enter book title", id="title_input", compact=True
                )

                yield Label("Author *", classes="mt-1")
                yield Input(
                    placeholder="Enter author name",
                    id="author_input",
                    suggester=self.author_suggester,
                    compact=True,
                )

                with Horizontal(classes="horiz-row"):
                    with Container(classes="mr-1"):
                        yield Label("Publication Year")
                        yield Input(
                            placeholder="YYYY",
                            id="year_input",
                            type="integer",
                            compact=True,
                        )
                    with Container(classes="ml-1"):
                        yield Label("Pages")
                        yield Input(
                            placeholder="Number of pages",
                            id="pages_input",
                            type="integer",
                            compact=True,
                        )

                yield Label("Genre")
                yield Select(self.genre_options, id="genre_select")

            # Review Information Card
            with Container(classes="section-card-review"):
                yield Label("[bold cyan]Review Information[/bold cyan]")
                yield Label("Date Read", classes="mt-1")
                yield Input(placeholder="YYYY-MM-DD", id="date_input", compact=True)

                yield Label("Rating (1-5)", classes="mt-1")
                yield Input(
                    placeholder="1-5", id="rating_input", type="integer", compact=True
                )

                yield Label("Your Review", classes="mt-1")
                yield TextArea(id="review_textarea")

            with Horizontal():
                yield Button("Save", id="save_button", variant="primary", compact=True)
                yield Button("Cancel", id="cancel_button", compact=True)

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

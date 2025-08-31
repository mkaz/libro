"""Edit book screen with form for updating existing books and reviews

This screen allows editing both book metadata (title, author, year, pages, genre)
and review data (rating, date read, review text) for an existing book/review pair.

Key features:
- Pre-populates all form fields with existing data
- Validates changes and only updates what was modified
- Supports genre selection with database-driven options
- Author name auto-completion based on existing authors
- Refreshes parent screens after successful update
"""

import sqlite3
from datetime import datetime
from typing import Any
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Label, Select, TextArea
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.suggester import Suggester


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


class EditBookScreen(ModalScreen):
    """Modal screen for editing an existing book and review"""

    CSS = """
    EditBookScreen {
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

    def __init__(self, db_path: str, review_id: int):
        super().__init__()
        self.db_path = db_path
        self.review_id = review_id
        self.book_id = None
        self.original_book_data: dict[str, Any] = {}
        self.original_review_data: dict[str, Any] = {}
        self.current_genre: str | None = None
        self.genre_options = self._get_genre_options()
        self.author_suggester = AuthorSuggester(db_path)

        # Load book data early so we can set initial values in compose
        self._load_initial_data()

    def _load_initial_data(self) -> None:
        """Load existing book and review data for initialization"""
        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            cursor = db.cursor()
            cursor.execute(
                """SELECT b.id, b.title, b.author, b.pub_year, b.pages, b.genre,
                          r.id, r.rating, r.date_read, r.review
                FROM books b
                LEFT JOIN reviews r ON b.id = r.book_id
                WHERE r.id = ?""",
                (self.review_id,),
            )
            data = cursor.fetchone()

            if not data:
                return

            # Store all the data for use in compose and later
            self.book_id = data[0]
            self.original_book_data = {
                "id": data[0],
                "title": data[1],
                "author": data[2],
                "pub_year": data[3],
                "pages": data[4],
                "genre": data[5],
            }
            self.original_review_data = {
                "id": data[6],
                "rating": data[7],
                "date_read": data[8],
                "review": data[9],
            }
            self.current_genre = data[5]
        except sqlite3.Error:
            pass  # Will leave data as defaults
        finally:
            if "db" in locals():
                db.close()

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
                genres.append((genre, genre))  # Use same value for both key and display
            return genres
        except sqlite3.Error:
            # Fallback to basic genres if DB query fails
            return [("", ""), ("fiction", "fiction"), ("nonfiction", "nonfiction")]
        finally:
            if "db" in locals():
                db.close()

    def compose(self) -> ComposeResult:
        """Create the edit book form"""
        with Container(classes="form-container"):
            yield Label("Edit Book & Review")

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
                # Ensure the value exists in options before setting it
                valid_genre = ""
                if self.current_genre:
                    for option_value, option_display in self.genre_options:
                        if option_value == self.current_genre:
                            valid_genre = self.current_genre
                            break

                yield Select(self.genre_options, value=valid_genre, id="genre_select")

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

    def on_mount(self) -> None:
        """Populate form fields when screen opens"""
        self._populate_form_fields()

    def _populate_form_fields(self) -> None:
        """Populate form fields with loaded data"""
        if not self.original_book_data:
            self.notify(f"No review found with ID {self.review_id}")
            self.app.pop_screen()
            return

        # Populate form fields with loaded data
        self.query_one("#title_input", Input).value = (
            self.original_book_data["title"] or ""
        )
        self.query_one("#author_input", Input).value = (
            self.original_book_data["author"] or ""
        )
        self.query_one("#year_input", Input).value = (
            str(self.original_book_data["pub_year"])
            if self.original_book_data["pub_year"]
            else ""
        )
        self.query_one("#pages_input", Input).value = (
            str(self.original_book_data["pages"])
            if self.original_book_data["pages"]
            else ""
        )

        self.query_one("#date_input", Input).value = (
            str(self.original_review_data["date_read"])
            if self.original_review_data["date_read"]
            else ""
        )
        self.query_one("#rating_input", Input).value = (
            str(self.original_review_data["rating"])
            if self.original_review_data["rating"]
            else ""
        )
        self.query_one("#review_textarea", TextArea).text = (
            self.original_review_data["review"] or ""
        )

    def on_button_pressed(self, event) -> None:
        """Handle button presses"""
        if event.button.id == "save_button":
            self.action_save()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def action_save(self) -> None:
        """Save the updated book and review"""
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

        # Check if any changes were made
        book_changed = (
            title != self.original_book_data["title"]
            or author != self.original_book_data["author"]
            or pub_year != self.original_book_data["pub_year"]
            or pages != self.original_book_data["pages"]
            or genre != self.original_book_data["genre"]
        )

        review_changed = (
            rating != self.original_review_data["rating"]
            or date_read != self.original_review_data["date_read"]
            or (review_text if review_text else None)
            != self.original_review_data["review"]
        )

        if not book_changed and not review_changed:
            self.notify("No changes made")
            self.app.pop_screen()
            return

        # Save to database
        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            changes_made = []

            # Update book if changed
            if book_changed:
                cursor = db.cursor()
                cursor.execute(
                    """UPDATE books 
                       SET title = ?, author = ?, pub_year = ?, pages = ?, genre = ?
                       WHERE id = ?""",
                    (title, author, pub_year, pages, genre, self.book_id),
                )
                changes_made.append("book")

            # Update review if changed
            if review_changed:
                cursor = db.cursor()
                cursor.execute(
                    """UPDATE reviews 
                       SET rating = ?, date_read = ?, review = ?
                       WHERE id = ?""",
                    (
                        rating,
                        date_read,
                        review_text if review_text else None,
                        self.review_id,
                    ),
                )
                changes_made.append("review")

            db.commit()

            if changes_made:
                changes_str = " and ".join(changes_made)
                self.notify(f"Successfully updated {changes_str} for '{title}'!")

            # Refresh the main screen and book detail screen before closing
            main_screen = self.app.screen_stack[0]  # Main screen is at the bottom
            if hasattr(main_screen, "load_books_data"):
                main_screen.load_books_data()

            # Find and refresh book detail screen if it exists in the stack
            for screen in self.app.screen_stack:
                if hasattr(screen, "load_book_details") and hasattr(
                    screen, "review_id"
                ):
                    if screen.review_id == self.review_id:
                        screen.load_book_details()

            self.app.pop_screen()

        except sqlite3.Error as e:
            self.notify(f"Database error: {e}")
        except Exception as e:
            self.notify(f"Error: {e}")
        finally:
            if "db" in locals():
                db.close()

    def action_cancel(self) -> None:
        """Cancel editing book"""
        self.app.pop_screen()

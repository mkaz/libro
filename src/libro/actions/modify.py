import sqlite3

from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import FormattedText
from datetime import date
import re  # for date validation
from rich.console import Console

from libro.models import BookReview, Book, Review


class AuthorCompleter(Completer):
    """Provides tab completion for author names based on frequency of books."""

    def __init__(self, db):
        self.db = db
        self._authors = None

    def _get_authors_by_frequency(self):
        """Get authors ordered by number of books (most to least)"""
        if self._authors is None:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT author, COUNT(*) as book_count 
                FROM books 
                GROUP BY LOWER(author)
                ORDER BY book_count DESC, LOWER(author) ASC
            """)
            self._authors = [row[0] for row in cursor.fetchall()]
        return self._authors

    def get_completions(self, document, complete_event):
        current_text = document.text
        current_lower = current_text.lower()

        for author in self._get_authors_by_frequency():
            if author.lower().startswith(current_lower) and len(current_text) < len(
                author
            ):
                # Calculate how much more text is needed
                remaining = author[len(current_text) :]

                # Create completion with gray styling for the incomplete part
                display = FormattedText(
                    [
                        ("", current_text),  # What user has typed (normal color)
                        (
                            "class:completion.incomplete",
                            remaining,
                        ),  # Incomplete part (gray)
                    ]
                )

                yield Completion(
                    text=author, start_position=-len(current_text), display=display
                )


class GenreCompleter(Completer):
    """Provides tab completion for genre names based on existing genres in the database."""

    def __init__(self, db):
        self.db = db
        self._genres = None

    def _get_existing_genres(self):
        """Get all unique genres from the database, ordered alphabetically"""
        if self._genres is None:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT DISTINCT genre 
                FROM books 
                WHERE genre IS NOT NULL AND genre != ''
                ORDER BY LOWER(genre) ASC
            """)
            self._genres = [row[0] for row in cursor.fetchall()]
        return self._genres

    def get_completions(self, document, complete_event):
        current_text = document.text
        current_lower = current_text.lower()

        for genre in self._get_existing_genres():
            if genre.lower().startswith(current_lower) and len(current_text) < len(
                genre
            ):
                # Calculate how much more text is needed
                remaining = genre[len(current_text) :]

                # Create completion with gray styling for the incomplete part
                display = FormattedText(
                    [
                        ("", current_text),  # What user has typed (normal color)
                        (
                            "class:completion.incomplete",
                            remaining,
                        ),  # Incomplete part (gray)
                    ]
                )

                yield Completion(
                    text=genre, start_position=-len(current_text), display=display
                )


# Define the style for prompts
style = Style.from_dict(
    {
        "prompt": "ansiyellow",
        # Completion menu styling for dark terminals
        "completion-menu.completion": "bg:ansiblack fg:ansiwhite",  # Normal completions
        "completion-menu.completion.current": "bg:ansiblue fg:ansiwhite bold",  # Selected completion
        "completion-menu.scrollbar": "bg:ansibrightblack",  # Scrollbar
        "completion-menu": "bg:ansiblack",  # Menu background
        # Style for the incomplete text within completions
        "completion.incomplete": "fg:ansibrightblack",  # Dimmed gray for incomplete text
    }
)


def add_book_review(db, args):
    session: PromptSession[str] = PromptSession(style=style)
    console = Console()

    try:
        console.print("ADDING NEW BOOK:\n---------------\n", style="blue")

        # Book details
        title = _prompt_with_retry(session, "Title: ", validator=NonEmptyValidator())
        author = _prompt_with_retry(
            session,
            "Author: ",
            validator=NonEmptyValidator(),
            completer=AuthorCompleter(db),
        )

        # Publication year with validation and conversion
        pub_year_str = _prompt_with_retry(
            session, "Publication year: ", validator=IntValidator()
        )
        pub_year = _convert_to_int_or_none(pub_year_str)

        # Pages with validation and conversion
        pages_str = _prompt_with_retry(
            session, "Number of pages: ", validator=IntValidator()
        )
        pages = _convert_to_int_or_none(pages_str)

        # Genre with validation and conversion
        genre_str = _prompt_with_retry(
            session, "Genre: ", validator=GenreValidator(), completer=GenreCompleter(db)
        )
        genre = _convert_genre_to_lowercase(genre_str)

        console.print("\nYOUR REVIEW DETAILS:\n-------------------\n", style="blue")

        # Date read with validation
        date_read = _prompt_with_retry(
            session, "Date read (YYYY-MM-DD): ", validator=DateValidator()
        )
        if not date_read:  # Handle empty input
            date_read = None

        # Rating with validation and conversion
        rating_str = _prompt_with_retry(
            session, "Rating (1-5): ", validator=RatingValidator()
        )
        rating = _convert_to_int_or_none(rating_str)

        # Review text (multiline)
        my_review = _prompt_with_retry(
            session, "Your review (Esc+Enter to finish):\n", multiline=True
        )
        if not my_review:  # Handle empty input
            my_review = None

        # Create and insert book using the internal model
        book = Book(  # Using _Book for insertion
            title=title, author=author, pub_year=pub_year, pages=pages, genre=genre
        )
        book_id = book.insert(db)

        # Create and insert review using the internal model
        review = Review(  # Using _Review for insertion
            book_id=book_id, date_read=date_read, rating=rating, review=my_review
        )
        review.insert(db)

        print(f"\nSuccessfully added '{title}' to the database!")

    except KeyboardInterrupt:
        print("\n\nAdd book cancelled. No changes made.")
        return
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def add_book(db, args):
    """Add a book without a review."""
    session: PromptSession[str] = PromptSession(style=style)
    console = Console()

    try:
        console.print(
            "ADDING NEW BOOK (no review):\n---------------------------\n", style="blue"
        )

        # Book details
        title = _prompt_with_retry(session, "Title: ", validator=NonEmptyValidator())
        author = _prompt_with_retry(
            session,
            "Author: ",
            validator=NonEmptyValidator(),
            completer=AuthorCompleter(db),
        )

        # Publication year with validation and conversion
        pub_year_str = _prompt_with_retry(
            session, "Publication year: ", validator=IntValidator()
        )
        pub_year = _convert_to_int_or_none(pub_year_str)

        # Pages with validation and conversion
        pages_str = _prompt_with_retry(
            session, "Number of pages: ", validator=IntValidator()
        )
        pages = _convert_to_int_or_none(pages_str)

        # Genre with validation and conversion
        genre_str = _prompt_with_retry(
            session, "Genre: ", validator=GenreValidator(), completer=GenreCompleter(db)
        )
        genre = _convert_genre_to_lowercase(genre_str)

        # Create and insert book using the internal model
        book = Book(
            title=title, author=author, pub_year=pub_year, pages=pages, genre=genre
        )
        book_id = book.insert(db)

        console.print(
            f"\n✅ Successfully added book '{title}' (Book ID: {book_id})",
            style="green",
        )
        console.print(
            "💡 Use 'libro review add {book_id}' to add a review later.", style="dim"
        )

    except KeyboardInterrupt:
        print("\n\nAdd book cancelled. No changes made.")
        return
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def add_review(db, args):
    """Add a review to an existing book."""
    book_id = args["book_id"]
    session: PromptSession[str] = PromptSession(style=style)
    console = Console()

    try:
        # First, verify the book exists and show its details
        book = Book.get_by_id(db, book_id)

        if not book:
            print(f"Error: Book with ID {book_id} not found.")
            return

        console.print("ADDING REVIEW FOR:\n------------------", style="blue")
        console.print(f"Book ID: {book_id}")
        console.print(f"Title: {book.title}")
        console.print(f"Author: {book.author}\n")

        # Date read with validation
        date_read = _prompt_with_retry(
            session, "Date read (YYYY-MM-DD): ", validator=DateValidator()
        )
        if not date_read:  # Handle empty input
            date_read = None

        # Rating with validation and conversion
        rating_str = _prompt_with_retry(
            session, "Rating (1-5): ", validator=RatingValidator()
        )
        rating = _convert_to_int_or_none(rating_str)

        # Review text (multiline)
        my_review = _prompt_with_retry(
            session, "Your review (Esc+Enter to finish):\n", multiline=True
        )
        if not my_review:  # Handle empty input
            my_review = None

        # Create and insert review
        review = Review(
            book_id=book_id, date_read=date_read, rating=rating, review=my_review
        )
        review_id = review.insert(db)

        console.print(
            f"\n✅ Successfully added review for '{book.title}' (Review ID: {review_id})",
            style="green",
        )

    except KeyboardInterrupt:
        print("\n\nAdd review cancelled. No changes made.")
        return
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def _prompt_with_retry(
    session,
    prompt_text,
    default_value="",
    validator=None,
    multiline=False,
    completer=None,
):
    """Helper function to handle prompting with error retry logic."""
    while True:
        try:
            if multiline:
                # Create new session for multiline to avoid validator inheritance
                multiline_session: PromptSession[str] = PromptSession(style=style)
                return multiline_session.prompt(
                    prompt_text, default=default_value, multiline=True
                )
            else:
                return session.prompt(
                    prompt_text,
                    default=default_value,
                    validator=validator,
                    completer=completer,
                )
        except Exception as e:
            print(f"Error: {e}")
            continue


def _update_field(
    session,
    current_value,
    prompt_text,
    validator=None,
    converter=None,
    multiline=False,
    completer=None,
):
    """Generic helper to update a field and return the new value if changed."""
    # Convert current value to string for display
    current_str = str(current_value) if current_value is not None else ""

    # Get new value from user
    new_str = _prompt_with_retry(
        session, prompt_text, current_str, validator, multiline, completer
    )

    # Convert back to appropriate type
    if converter:
        new_value = converter(new_str)
    else:
        new_value = new_str if new_str else None

    # Return new value if it's different from current
    return new_value if new_value != current_value else None


def edit_book(db, args):
    """Edit only the book data."""
    book_id = int(args["id"])

    # Check if book exists and get current data
    book = Book.get_by_id(db, book_id)

    if not book:
        print(f"Error: Book with ID {book_id} not found.")
        return

    session: PromptSession[str] = PromptSession(style=style)
    console = Console()

    try:
        console.print(
            f"EDITING BOOK ID {book_id}:\n------------------------\n", style="blue"
        )

        updated_book_data = {}

        # Title and Author (no conversion needed)
        updated_book_data["title"] = _update_field(
            session, book.title, "Title: ", validator=NonEmptyValidator()
        )

        updated_book_data["author"] = _update_field(
            session,
            book.author,
            "Author: ",
            validator=NonEmptyValidator(),
            completer=AuthorCompleter(db),
        )

        # Publication year (integer conversion)
        updated_book_data["pub_year"] = _update_field(
            session,
            book.pub_year,
            "Publication year: ",
            IntValidator(),
            _convert_to_int_or_none,
        )

        # Pages (integer conversion)
        updated_book_data["pages"] = _update_field(
            session,
            book.pages,
            "Number of pages: ",
            IntValidator(),
            _convert_to_int_or_none,
        )

        # Genre (lowercase conversion)
        updated_book_data["genre"] = _update_field(
            session,
            book.genre,
            "Genre: ",
            GenreValidator(),
            _convert_genre_to_lowercase,
            completer=GenreCompleter(db),
        )

        # Update database (only book data)
        _update_book_database(db, updated_book_data, book_id)

    except KeyboardInterrupt:
        print("\n\nEdit cancelled. No changes made.")
        return


def _update_book_database(db, updated_book_data, book_id):
    """Handle the database update operations for book-only edits."""
    try:
        cursor = db.cursor()

        # Filter out None values (unchanged fields)
        filtered_book_data = {
            k: v for k, v in updated_book_data.items() if v is not None
        }

        if filtered_book_data:
            # Construct UPDATE query for books table only
            book_update_query = (
                "UPDATE books SET "
                + ", ".join([f"{key} = ?" for key in filtered_book_data.keys()])
                + " WHERE id = ?"
            )
            book_update_values = list(filtered_book_data.values()) + [book_id]
            cursor.execute(book_update_query, book_update_values)
            print(f"Updated book with ID {book_id}.")
            db.commit()
        else:
            print("\nNo changes made.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        db.rollback()
    except Exception as e:
        print(f"Error during update: {e}")
        db.rollback()


def edit_review(db, args):
    """Edit only the review data, display book data for context."""
    review_id = int(args["id"])
    book_review = BookReview.get_by_id(db, review_id)
    if not book_review:
        print(f"Error: Review with ID {review_id} not found.")
        return

    session: PromptSession[str] = PromptSession(style=style)
    console = Console()

    try:
        # Display book information for context (read-only)
        console.print(
            f"BOOK ID {book_review.book_id}:\n-------------------------\n", style="dim"
        )
        console.print(f"Title: {book_review.book_title}", style="dim")
        console.print(f"Author: {book_review.book_author}", style="dim")
        console.print(
            f"Publication Year: {book_review.book_pub_year or 'N/A'}", style="dim"
        )
        console.print(f"Pages: {book_review.book_pages or 'N/A'}", style="dim")
        console.print(f"Genre: {book_review.book_genre or 'N/A'}", style="dim")

        # Edit only review fields
        console.print("\nEDIT REVIEW:\n-------------------------\n", style="blue")

        updated_review_data = {}

        # Date read (string conversion, stored as string)
        updated_review_data["date_read"] = _update_field(
            session, book_review.date_read, "Date read (YYYY-MM-DD): ", DateValidator()
        )

        # Rating (integer conversion)
        updated_review_data["rating"] = _update_field(
            session,
            book_review.rating,
            "Rating (1-5): ",
            RatingValidator(),
            _convert_to_int_or_none,
        )

        # Review text (multiline)
        updated_review_data["review"] = _update_field(
            session,
            book_review.review_text,
            "Your review (Esc+Enter to finish):\n",
            multiline=True,
        )

        # Update database (only review data)
        _update_review_database(db, updated_review_data, book_review)

    except KeyboardInterrupt:
        print("\n\nEdit cancelled. No changes made.")
        return


def _update_review_database(db, updated_review_data, book_review):
    """Handle the database update operations for review-only edits."""
    try:
        cursor = db.cursor()

        # Filter out None values (unchanged fields)
        filtered_review_data = {
            k: v for k, v in updated_review_data.items() if v is not None
        }

        if filtered_review_data:
            # Construct UPDATE query for reviews table only
            review_update_query = (
                "UPDATE reviews SET "
                + ", ".join([f"{key} = ?" for key in filtered_review_data.keys()])
                + " WHERE id = ?"
            )
            review_update_values = list(filtered_review_data.values()) + [
                book_review.review_id
            ]
            cursor.execute(review_update_query, review_update_values)
            print(f"Updated review with ID {book_review.review_id}.")
            db.commit()
        else:
            print("\nNo changes made.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        db.rollback()
    except Exception as e:
        print(f"Error during update: {e}")
        db.rollback()


def _convert_to_int_or_none(value):
    """Convert string to int or None if empty."""
    return int(value) if value else None


def _convert_genre_to_lowercase(value):
    """Convert genre to lowercase or None if empty."""
    return value.lower() if value else None


class IntValidator(Validator):
    def validate(self, document):
        text = document.text
        if text == "":
            return
        try:
            int(text)
        except ValueError:
            raise ValidationError(
                message="Please enter a valid integer.", cursor_position=len(text)
            )


class RatingValidator(Validator):
    def validate(self, document):
        text = document.text
        if text == "":
            return
        try:
            rating = int(text)
            if not (1 <= rating <= 5):
                raise ValidationError(
                    message="Rating must be between 1 and 5.", cursor_position=len(text)
                )
        except ValueError:
            raise ValidationError(
                message="Please enter a valid integer.", cursor_position=len(text)
            )


class GenreValidator(Validator):
    def validate(self, document):
        # Allow any string for genre - no validation needed
        pass


class DateValidator(Validator):
    def validate(self, document):
        text = document.text
        if text == "":
            return
        # Basic YYYY-MM-DD format validation
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", text):
            raise ValidationError(
                message="Invalid date format. Use YYYY-MM-DD.",
                cursor_position=len(text),
            )
        try:
            date.fromisoformat(text)
        except ValueError:
            raise ValidationError(message="Invalid date.", cursor_position=len(text))


class NonEmptyValidator(Validator):
    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(
                message="This field cannot be empty.",
                cursor_position=len(document.text),
            )

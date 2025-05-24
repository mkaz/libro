import sqlite3

from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style
from datetime import date
import re  # for date validation
from rich.console import Console

from libro.models import BookReview, Book, Review

# Define the style for prompts
style = Style.from_dict(
    {
        "prompt": "ansiyellow",
    }
)


def add_book(db, args):
    session = PromptSession(style=style)
    console = Console()

    try:
        console.print("ADDING NEW BOOK:\n---------------\n", style="blue")

        # Book details
        title = _prompt_with_retry(session, "Title: ", validator=NonEmptyValidator())
        author = _prompt_with_retry(session, "Author: ", validator=NonEmptyValidator())

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
            session, "Genre (fiction/nonfiction): ", validator=GenreValidator()
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


def edit_book(db, args):
    review_id = int(args["id"])
    book_review = BookReview.get_by_id(db, review_id)
    if not book_review:
        print(f"Error: Review with ID {review_id} not found.")
        return

    session = PromptSession(style=style)
    console = Console()

    try:
        updated_book_data = {}
        updated_review_data = {}

        # --- Book Fields ---
        console.print("BOOK DETAILS:\n---------------\n", style="blue")

        # Title and Author (no conversion needed)
        updated_book_data["title"] = _update_field(
            session, book_review.book_title, "Title: ", validator=NonEmptyValidator()
        )

        updated_book_data["author"] = _update_field(
            session, book_review.book_author, "Author: ", validator=NonEmptyValidator()
        )

        # Publication year (integer conversion)
        updated_book_data["pub_year"] = _update_field(
            session,
            book_review.book_pub_year,
            "Publication year: ",
            IntValidator(),
            _convert_to_int_or_none,
        )

        # Pages (integer conversion)
        updated_book_data["pages"] = _update_field(
            session,
            book_review.book_pages,
            "Number of pages: ",
            IntValidator(),
            _convert_to_int_or_none,
        )

        # Genre (lowercase conversion)
        updated_book_data["genre"] = _update_field(
            session,
            book_review.book_genre,
            "Genre (fiction/nonfiction): ",
            GenreValidator(),
            _convert_genre_to_lowercase,
        )

        # --- Review Fields ---
        console.print("\nYOUR REVIEW DETAILS:\n-------------------\n", style="blue")

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

        # Update database
        _update_database(db, updated_book_data, updated_review_data, book_review)

    except KeyboardInterrupt:
        print("\n\nEdit cancelled. No changes made.")
        return


def _prompt_with_retry(
    session, prompt_text, default_value="", validator=None, multiline=False
):
    """Helper function to handle prompting with error retry logic."""
    while True:
        try:
            if multiline:
                # Create new session for multiline to avoid validator inheritance
                multiline_session = PromptSession(style=style)
                return multiline_session.prompt(
                    prompt_text, default=default_value, multiline=True
                )
            else:
                return session.prompt(
                    prompt_text, default=default_value, validator=validator
                )
        except Exception as e:
            print(f"Error: {e}")
            continue


def _update_field(
    session, current_value, prompt_text, validator=None, converter=None, multiline=False
):
    """Generic helper to update a field and return the new value if changed."""
    # Convert current value to string for display
    current_str = str(current_value) if current_value is not None else ""

    # Get new value from user
    new_str = _prompt_with_retry(
        session, prompt_text, current_str, validator, multiline
    )

    # Convert back to appropriate type
    if converter:
        new_value = converter(new_str)
    else:
        new_value = new_str if new_str else None

    # Return new value if it's different from current
    return new_value if new_value != current_value else None


def _update_database(db, updated_book_data, updated_review_data, book_review):
    """Handle the database update operations."""
    try:
        cursor = db.cursor()

        # Filter out None values (unchanged fields)
        filtered_book_data = {
            k: v for k, v in updated_book_data.items() if v is not None
        }
        filtered_review_data = {
            k: v for k, v in updated_review_data.items() if v is not None
        }

        if filtered_book_data:
            # Construct UPDATE query for books table
            book_update_query = (
                "UPDATE books SET "
                + ", ".join([f"{key} = ?" for key in filtered_book_data.keys()])
                + " WHERE id = ?"
            )
            book_update_values = list(filtered_book_data.values()) + [
                book_review.book_id
            ]
            cursor.execute(book_update_query, book_update_values)
            print(f"Updated book with ID {book_review.book_id}.")

        if filtered_review_data:
            # Construct UPDATE query for reviews table
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

        if filtered_book_data or filtered_review_data:
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
        text = document.text.lower()
        if text == "":
            return
        if text not in ["fiction", "nonfiction"]:
            raise ValidationError(
                message="Genre must be 'fiction' or 'nonfiction'.",
                cursor_position=len(text),
            )


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

import sqlite3

from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style
from datetime import date
import re  # for date validation
from rich.console import Console

from libro.utils import get_valid_input, validate_and_convert_date
from libro.models import BookReview, Book, Review

# Define the style for prompts
style = Style.from_dict(
    {
        "prompt": "ansiyellow",
    }
)


# Define validators for prompt_toolkit
class YearValidator(Validator):
    def validate(self, document):
        text = document.text
        if text == "":
            return
        try:
            year = int(text)
            # Basic year range check, adjust as needed
            if not (1000 <= year <= date.today().year + 5):
                raise ValidationError(
                    message="Invalid year.", cursor_position=len(text)
                )
        except ValueError:
            raise ValidationError(
                message="Please enter a valid year.", cursor_position=len(text)
            )


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


def add_book(db, args):
    try:
        print("Enter book details:")
        # Note: This still uses the old get_valid_input, not prompt_toolkit
        title = get_valid_input("Title: ")
        author = get_valid_input("Author: ")

        pub_year = get_valid_input(
            "Publication year: ",
            lambda x: validate_and_convert_date(x, "pub_year"),
            allow_empty=True,
        )
        pages = get_valid_input("Number of pages: ", allow_empty=True)
        genre = get_genre()

        date_read = get_valid_input(
            "Date read (YYYY-MM-DD): ",
            lambda x: validate_and_convert_date(x, "date_read"),
            allow_empty=True,
        )
        rating = get_valid_input("Rating (1-5): ", allow_empty=True)
        my_review = get_valid_input("Your review:", allow_empty=True, multiline=True)

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

    # Collect updated values
    updated_book_data = {}
    updated_review_data = {}

    # --- Book Fields ---
    console.print("BOOK DETAILS:\n---------------\n", style="blue")
    while True:
        try:
            new_title = session.prompt("Title: ", default=book_review.book_title)
            if new_title != book_review.book_title:
                updated_book_data["title"] = new_title
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    while True:
        try:
            new_author = session.prompt("Author: ", default=book_review.book_author)
            if new_author != book_review.book_author:
                updated_book_data["author"] = new_author
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    # Need to handle Optional[int] and empty string input
    current_pub_year_str = (
        str(book_review.book_pub_year) if book_review.book_pub_year is not None else ""
    )
    while True:
        try:
            new_pub_year_str = session.prompt(
                "Publication year: ",
                default=current_pub_year_str,
                validator=YearValidator(),
            )
            # Convert back to Optional[int]
            new_pub_year = int(new_pub_year_str) if new_pub_year_str else None
            if new_pub_year != book_review.book_pub_year:
                updated_book_data["pub_year"] = new_pub_year
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    current_pages_str = (
        str(book_review.book_pages) if book_review.book_pages is not None else ""
    )
    while True:
        try:
            new_pages_str = session.prompt(
                "Number of pages: ",
                default=current_pages_str,
                validator=IntValidator(),
            )
            # Convert back to Optional[int]
            new_pages = int(new_pages_str) if new_pages_str else None
            if new_pages != book_review.book_pages:
                updated_book_data["pages"] = new_pages
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    current_genre = book_review.book_genre if book_review.book_genre is not None else ""
    while True:
        try:
            # Convert empty string back to None if needed, though validator handles empty
            new_genre = session.prompt(
                "Genre (fiction/nonfiction): ",
                default=current_genre,
                validator=GenreValidator(),
            ).lower()
            if new_genre == "":
                new_genre = None
            if new_genre != book_review.book_genre:
                updated_book_data["genre"] = new_genre
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    # --- Review Fields ---

    console.print("\nYOUR REVIEW DETAILS:\n-------------------\n", style="blue")
    # Need to handle Optional[date] and empty string input
    current_date_read_str = (
        str(book_review.date_read) if book_review.date_read is not None else ""
    )
    while True:
        try:
            new_date_read_str = session.prompt(
                "Date read (YYYY-MM-DD): ",
                default=current_date_read_str,
                validator=DateValidator(),
            )
            # Convert string back to Optional[date]. Store as string in DB.
            if new_date_read_str != current_date_read_str:  # Compare string values
                updated_review_data["date_read"] = (
                    new_date_read_str if new_date_read_str else None
                )  # Store as string or None
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    current_rating_str = (
        str(book_review.rating) if book_review.rating is not None else ""
    )
    while True:
        try:
            new_rating_str = session.prompt(
                "Rating (1-5): ",
                default=current_rating_str,
                validator=RatingValidator(),
            )
            # Convert back to Optional[int]
            new_rating = int(new_rating_str) if new_rating_str else None
            if new_rating != book_review.rating:
                updated_review_data["rating"] = new_rating
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    current_review_text = (
        book_review.review_text if book_review.review_text is not None else ""
    )
    while True:
        try:
            # Create a new session specifically for multiline input to avoid validator inheritance
            multiline_session = PromptSession(style=style)
            new_review_text = multiline_session.prompt(
                "Your review (Esc+Enter to finish):\n",
                default=current_review_text,
                multiline=True,
            )
            if new_review_text != book_review.review_text:
                updated_review_data["review"] = new_review_text
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    # Perform database updates if there are changes
    try:
        cursor = db.cursor()

        if updated_book_data:
            # Construct UPDATE query for books table
            book_update_query = (
                "UPDATE books SET "
                + ", ".join([f"{key} = ?" for key in updated_book_data.keys()])
                + " WHERE id = ?"
            )
            book_update_values = list(updated_book_data.values()) + [
                book_review.book_id
            ]
            cursor.execute(book_update_query, book_update_values)
            print(f"Updated book with ID {book_review.book_id}.")

        if updated_review_data:
            # Construct UPDATE query for reviews table
            review_update_query = (
                "UPDATE reviews SET "
                + ", ".join([f"{key} = ?" for key in updated_review_data.keys()])
                + " WHERE id = ?"
            )
            review_update_values = list(updated_review_data.values()) + [
                book_review.review_id
            ]
            cursor.execute(review_update_query, review_update_values)
            print(f"Updated review with ID {book_review.review_id}.")

        if updated_book_data or updated_review_data:
            db.commit()
            print("\nSuccessfully updated the database.")
        else:
            print("\nNo changes were made.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        db.rollback()  # Rollback changes if an error occurs
    except Exception as e:
        print(f"Error during update: {e}")
        db.rollback()  # Rollback changes


def get_genre():
    while True:
        genre = input("Genre (fiction/nonfiction): ").strip().lower()
        if genre in ["fiction", "nonfiction"]:
            return genre
        print("Please enter either 'fiction' or 'nonfiction'")

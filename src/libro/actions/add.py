import sqlite3

from libro.utils import get_valid_input, validate_and_convert_date


def add_book(db, args):
    try:
        cursor = db.cursor()

        print("Enter book details:")
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

        # @TODO: Check if book already exists

        # Insert into books table
        cursor.execute(
            """
            INSERT INTO books (
                title, author, pages, pub_year, genre
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                title,
                author,  # Using full author name as per schema
                pages,
                pub_year,
                genre,
            ),
        )

        # Get the book ID of the newly inserted book
        book_id = cursor.lastrowid

        # Insert into reviews table
        cursor.execute(
            """
            INSERT INTO reviews (
                book_id, date_read, rating, review
            ) VALUES (?, ?, ?, ?)
        """,
            (
                book_id,
                date_read,
                rating,
                my_review,
            ),
        )

        db.commit()
        print(f"\nSuccessfully added '{title}' to the database!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if db:
            db.close()


def get_genre():
    while True:
        genre = input("Genre (fiction/nonfiction): ").strip().lower()
        if genre in ["fiction", "nonfiction"]:
            return genre
        print("Please enter either 'fiction' or 'nonfiction'")

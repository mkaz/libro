import sqlite3

from libro.utils import get_valid_input, validate_and_convert_date


def add_book(db, args):
    try:
        cursor = db.cursor()

        print("Enter book details:")
        title = get_valid_input("Title: ")

        author_normal = get_valid_input("Author (First Last): ")
        author_lastname = author_normal.split()[-1]
        author_firstname = " ".join(author_normal.split()[:-1])

        pub_year = get_valid_input(
            "Publication year: ",
            lambda x: validate_and_convert_date(x, "publication_year"),
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

        # Insert into database
        cursor.execute(
            """
            INSERT INTO books (
                title, author_lastname, author_firstname, rating,
                pages, publication_year, date_read, my_review, genre
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                title,
                author_lastname,
                author_firstname,
                rating,
                pages,
                pub_year,
                date_read,
                my_review,
                genre,
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

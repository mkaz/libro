from pathlib import Path
import csv
import re
from datetime import datetime
from libro.models import Book, Review


def import_books(db, args):
    f = args["file"]
    print(f"Importing books from {f}")

    # check file exists
    if not Path(f).is_file():
        print(f"File {f} not found")
        return

    # read file
    count = 0
    with open(f, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Author field includes where spacing and tabs, so we need to clean it up
            author = row["Author"].replace("\t", " ").replace("  ", " ").strip()
            while "  " in author:
                author = author.replace("  ", " ")

            # @TODO: Make this a import flag
            # Title field includes series info that is not the title
            # For example: Ender's Game (Ender's Saga, #1)
            raw_title = row["Title"].strip()
            # Regex to capture the title part before parenthesis *only if* the parenthesis contains '#'
            series_pattern = re.compile(r"^(.*?)\s*\([^#]*#.*\)$")
            match = series_pattern.match(raw_title)
            if match:
                # If it matches the series pattern (contains '#'), take the part before the parenthesis
                title = match.group(1).strip()
            else:
                # Otherwise (no parenthesis or parenthesis without '#'), use the raw title as is
                title = raw_title

            # @TODO: Make this a import flag
            # Moar cleanup - annoying non-fiction books have a colon and extra junk to promote.
            # Remove colon and everything after it
            # For example: Eats, Shoots & Leaves: The Zero Tolerance Approach to Punctuation
            title = title.split(":")[0].strip()

            pub_year = row["Original Publication Year"].strip()
            pages = row["Number of Pages"].strip()
            # Note: Ensure 'from datetime import datetime' is present at the top of the file.
            raw_date_read = row["Date Read"].strip()
            date_read = None  # Default to None if empty or invalid
            if raw_date_read:
                try:
                    # Parse the date assuming Goodreads format YYYY/MM/DD
                    date_obj = datetime.strptime(raw_date_read, "%Y/%m/%d")
                    # Format to YYYY-MM-DD, which is suitable for SQLite and the Review model
                    date_read = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    # Handle cases where the date format might be different or invalid
                    print(
                        f"Warning: Could not parse 'Date Read' field ('{raw_date_read}') for {title}. Setting date to None."
                    )
            rating = row["My Rating"].strip()
            review = row["My Review"].strip()

            # There are many lets combine and look for "read"
            # Bookshelves, Bookshelves with positions, Exclusive Shelf into a set
            shelf1 = row["Bookshelves"]
            shelf2 = row["Bookshelves with positions"]
            shelf3 = row["Exclusive Shelf"]
            shelf = ",".join([s.strip() for s in [shelf1, shelf2, shelf3] if s])
            shelf = shelf.split(",")
            shelf = set(shelf)

            if "read" in shelf:
                count += 1

                # Create and insert book
                book = Book(
                    title=title,
                    author=author,
                    pub_year=pub_year,
                    pages=pages,
                    genre="fiction",  # Default to fiction, could be improved
                )
                book_id = book.insert(db)

                # Create and insert review
                review = Review(
                    book_id=book_id, date_read=date_read, rating=rating, review=review
                )
                review.insert(db)

    print(f"Imported {count} books")

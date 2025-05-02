import sqlite3
import sys
from pathlib import Path

from libro.config import init_args
from libro.actions.show import show_books
from libro.actions.report import report
from libro.actions.add import add_book
from libro.actions.db import init_db
from libro.actions.importer import import_books


def main():
    print("")  # give me some space
    args = init_args()

    dbfile = Path(args["db"])
    if args["info"]:
        print(f"Using libro.db {dbfile}")

    # check if taskdb exists
    is_new_db = not dbfile.is_file()
    if is_new_db:
        response = input(f"Create new database at {dbfile}? [Y/n] ").lower()
        if response not in ["", "y", "yes"]:
            print("No database created")
            sys.exit(1)

        init_db(dbfile)
        print("Database created")

    try:
        db = sqlite3.connect(dbfile)
        # Default to using column names instead of index
        db.row_factory = sqlite3.Row

        match args["command"]:
            case "add":
                print("Add new book read")
                add_book(db, args)
            case "show":
                show_books(db, args)
            case "report":
                report(db, args)
            case "import":
                import_books(db, args)
            case _:
                print("Not yet implemented")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

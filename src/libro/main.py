import sqlite3
import sys
import os
from pathlib import Path

from libro.config import init_args
from libro.actions.show import show_book_detail, show_books_only
from libro.actions.report import report
from libro.actions.modify import add_book_review, add_book, add_review, edit_book, edit_review
from libro.actions.db import init_db, migrate_db
from libro.actions.importer import import_books
from libro.actions.lists import manage_lists


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
        
        # Run migration for existing databases
        migrate_db(db)

        match args["command"]:
            case "add":
                add_book_review(db, args)
            case "report":
                report(db, args)
            case "import":
                import_books(db, args)
            case "list":
                manage_lists(db, args)
            case "book":
                book_action = args.get("book_action")
                if book_action is None:
                    # Show help for book command
                    os.system("libro book --help")
                else:
                    match book_action:
                        case "add":
                            add_book(db, args)
                        case "edit":
                            edit_book(db, args)
                        case "show":
                            show_books_only(db, args)
                        case _:
                            print("Book action not recognized")
            case "review":
                review_action = args.get("review_action")
                if review_action is None:
                    # Show help for review command
                    os.system("libro review --help")
                else:
                    match review_action:
                        case "add":
                            add_review(db, args)
                        case "edit":
                            edit_review(db, args)
                        case "show":
                            if args.get("id"):
                                show_book_detail(db, args["id"])  # Same as default show
                            else:
                                print("Please specify a review ID: libro review show <review_id>")
                        case _:
                            print("Review action not recognized")
            case _:
                print("Not yet implemented")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

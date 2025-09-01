import sqlite3
import sys
from pathlib import Path

from libro.config import init_args


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

        from libro.actions.db import init_db

        init_db(dbfile)
        print("Database created")

    try:
        db = sqlite3.connect(dbfile)
        # Default to using column names instead of index
        db.row_factory = sqlite3.Row

        # Run migration for existing databases
        from libro.actions.db import migrate_db

        migrate_db(db)

        match args["command"]:
            case "add":
                from libro.actions.modify import add_book_review

                add_book_review(db, args)
            case "report":
                from libro.actions.report import report

                report(db, args)
            case "import":
                from libro.actions.importer import import_books

                import_books(db, args)
            case "list":
                from libro.actions.lists import manage_lists

                manage_lists(db, args)
            case "book":
                from libro.actions.show import show_books_only
                from libro.actions.modify import add_book, edit_book

                action_or_id = args.get("action_or_id")
                if action_or_id is None:
                    # No argument - show recent books
                    show_books_only(db, args)
                elif action_or_id == "add":
                    # Add a new book
                    add_book(db, args)
                elif action_or_id == "edit":
                    # Edit a book - need edit_id
                    edit_id = args.get("edit_id")
                    if edit_id is None:
                        print(
                            "Please specify a book ID to edit: libro book edit <book_id>"
                        )
                    else:
                        # Update args to use the edit_id as the main id
                        args["id"] = edit_id
                        edit_book(db, args)
                else:
                    # Try to parse as book ID
                    try:
                        book_id = int(action_or_id)
                        args["id"] = book_id
                        show_books_only(db, args)
                    except ValueError:
                        print(f"Unknown book action or invalid ID: {action_or_id}")
                        print("Valid actions: add, edit, or a book ID number")
            case "review":
                from libro.actions.show import show_recent_reviews, show_book_detail
                from libro.actions.modify import add_review, edit_review

                action_or_id = args.get("action_or_id")
                if action_or_id is None:
                    # No argument - show recent reviews (or filtered reviews)
                    show_recent_reviews(db, args)
                elif action_or_id == "add":
                    # Add a review - need target_id (book_id)
                    target_id = args.get("target_id")
                    if target_id is None:
                        print(
                            "Please specify a book ID to add review to: libro review add <book_id>"
                        )
                    else:
                        # Update args to use the target_id as book_id
                        args["book_id"] = target_id
                        add_review(db, args)
                elif action_or_id == "edit":
                    # Edit a review - need target_id (review_id)
                    target_id = args.get("target_id")
                    if target_id is None:
                        print(
                            "Please specify a review ID to edit: libro review edit <review_id>"
                        )
                    else:
                        # Update args to use the target_id as the main id
                        args["id"] = target_id
                        edit_review(db, args)
                else:
                    # Try to parse as review ID
                    try:
                        review_id = int(action_or_id)
                        show_book_detail(db, review_id)
                    except ValueError:
                        print(f"Unknown review action or invalid ID: {action_or_id}")
                        print("Valid actions: add, edit, or a review ID number")
            case "tui":
                from libro.tui import launch_tui

                launch_tui(str(dbfile))
            case _:
                print("Not yet implemented")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

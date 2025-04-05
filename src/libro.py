import sqlite3
import sys
from pathlib import Path

from config import init_args
from actions.show import show_books


def main():
    args = init_args()

    dbfile = Path(args["db"])
    if args["info"]:
        print(f"Using libro.db {dbfile}")

    # check if taskdb exists
    is_new_db = not dbfile.is_file()
    if is_new_db:
        print("TODO: Need to create new database")
        sys.exit(1)

    try:
        db = sqlite3.connect(dbfile)

        command = args["command"]
        if command == "add":
            pass
        elif command == "show":
            show_books(db, args)
        else:
            print("Not yet implemented")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

import argparse
import os
import sys
from pathlib import Path
from typing import Dict
from datetime import datetime
from appdirs import AppDirs
import importlib.metadata

__version__ = importlib.metadata.version("libro-book")


def init_args() -> Dict:
    """Parse and return the arguments."""
    parser = argparse.ArgumentParser(description="Book list")
    parser.add_argument("--db", help="SQLite file")
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("-i", "--info", action="store_true")

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Report command with its specific arguments
    report = subparsers.add_parser("report", help="Show reports")
    report.add_argument("--chart", action="store_true", help="Show chart view of books by year")
    report.add_argument("--author", action="store_true", help="Show author report")
    report.add_argument("--limit", type=int, help="Minimum books read by author")
    report.add_argument("--undated", action="store_true", help="Include undated books")
    report.add_argument("--year", type=int, help="Year to filter books")
    report.add_argument("id", type=int, nargs="?", help="Show book ID details")


    # Add command with its specific arguments (backward compatibility - creates book + review)
    subparsers.add_parser("add", help="Add a book with review")


    # Book management subcommands
    book_parser = subparsers.add_parser("book", help="Manage books")
    book_subparsers = book_parser.add_subparsers(dest="book_action", help="Book actions")
    
    # Book add subcommand
    book_subparsers.add_parser("add", help="Add a book (without review)")
    
    # Book edit subcommand
    book_edit_parser = book_subparsers.add_parser("edit", help="Edit book details")
    book_edit_parser.add_argument("id", type=int, help="Book ID to edit")
    
    # Book show subcommand
    book_show_parser = book_subparsers.add_parser("show", help="Show books")
    book_show_parser.add_argument("id", type=int, nargs="?", help="Show specific book ID")
    book_show_parser.add_argument("--author", type=str, help="Show books by specific author")
    book_show_parser.add_argument("--year", type=int, help="Year to filter books")

    # Review management subcommands
    review_parser = subparsers.add_parser("review", help="Manage reviews")
    review_subparsers = review_parser.add_subparsers(dest="review_action", help="Review actions")
    
    # Review add subcommand
    review_add_parser = review_subparsers.add_parser("add", help="Add a review to existing book")
    review_add_parser.add_argument("book_id", type=int, help="Book ID to add review to")
    
    # Review edit subcommand
    review_edit_parser = review_subparsers.add_parser("edit", help="Edit review details")
    review_edit_parser.add_argument("id", type=int, help="Review ID to edit")
    
    # Review show subcommand
    review_show_parser = review_subparsers.add_parser("show", help="Show reviews")
    review_show_parser.add_argument("id", type=int, nargs="?", help="Show specific review ID")

    # Import command with its specific arguments
    imp = subparsers.add_parser("import", help="Import books")
    imp.add_argument("file", type=str, help="Goodreads CSV export file")

    # List command with subcommands for reading list management
    list_parser = subparsers.add_parser("list", help="Manage reading lists")
    list_subparsers = list_parser.add_subparsers(dest="list_action", help="List actions")

    # List create subcommand
    list_create = list_subparsers.add_parser("create", help="Create a new reading list")
    list_create.add_argument("name", type=str, help="Name of the reading list")
    list_create.add_argument(
        "--description", type=str, help="Optional description of the reading list"
    )

    # List show subcommand
    list_show = list_subparsers.add_parser("show", help="Show reading lists")
    list_show.add_argument(
        "id", type=int, nargs="?", help="ID of specific list to show (optional)"
    )

    # List add subcommand
    list_add = list_subparsers.add_parser("add", help="Add a book to a reading list")
    list_add.add_argument("id", type=int, help="ID of the reading list")

    # List remove subcommand
    list_remove = list_subparsers.add_parser(
        "remove", help="Remove a book from a reading list"
    )
    list_remove.add_argument("id", type=int, help="ID of the reading list")
    list_remove.add_argument("book_id", type=int, help="ID of the book to remove")

    # List stats subcommand
    list_stats = list_subparsers.add_parser("stats", help="Show reading list statistics")
    list_stats.add_argument(
        "id", type=int, nargs="?", help="ID of specific list for stats (optional)"
    )

    # List edit subcommand
    list_edit = list_subparsers.add_parser("edit", help="Edit a reading list")
    list_edit.add_argument("id", type=int, help="ID of the reading list to edit")
    list_edit.add_argument("--name", type=str, help="New name for the reading list")
    list_edit.add_argument("--description", type=str, help="New description for the reading list")

    # List delete subcommand
    list_delete = list_subparsers.add_parser("delete", help="Delete a reading list")
    list_delete.add_argument("id", type=int, help="ID of the reading list to delete")

    # List import subcommand
    list_import = list_subparsers.add_parser("import", help="Import books from CSV to reading list")
    list_import.add_argument("file", type=str, help="CSV file to import (Title, Author, Publication Year, Pages, Genre)")
    list_import.add_argument("--id", type=int, help="ID of existing reading list to import to")
    list_import.add_argument("--name", type=str, help="Name for new reading list (creates list if provided)")
    list_import.add_argument("--description", type=str, help="Description for new reading list")

    args = vars(parser.parse_args())

    if args["version"]:
        print(f"libro v{__version__}")
        sys.exit()

    # if not specified on command-line figure it out
    if args["db"] is None:
        args["db"] = get_db_loc()

    if args["command"] is None:
        args["command"] = "report"

    if args.get("year") is None:
        args["year"] = datetime.now().year

    return args


def get_db_loc() -> Path:
    """Figure out where the libro.db file is.
    See README for spec"""

    # check if tasks.db exists in current dir
    cur_dir = Path(Path.cwd(), "libro.db")
    if cur_dir.is_file():
        return cur_dir

    # check for env LIBRO_DB
    env_var = os.environ.get("LIBRO_DB")
    if env_var is not None:
        return Path(env_var)

    # Finally use system specific data dir
    dirs = AppDirs("Libro", "mkaz")

    # No config file, default to data dir
    data_dir = Path(dirs.user_data_dir)
    if not data_dir.is_dir():
        data_dir.mkdir()

    return Path(dirs.user_data_dir, "libro.db")

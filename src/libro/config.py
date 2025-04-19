import argparse
import os
import sys
from pathlib import Path
from typing import Dict
from datetime import datetime
from appdirs import AppDirs

__version__ = "0.1.0"


def init_args() -> Dict:
    """Parse and return the arguments."""
    parser = argparse.ArgumentParser(description="Book list")
    parser.add_argument("--db", help="SQLite file")
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("-i", "--info", action="store_true")

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Report command with its specific arguments
    report_parser = subparsers.add_parser("report", help="Show reports")
    report_parser.add_argument(
        "--author", action="store_true", help="Show author report"
    )
    report_parser.add_argument("--year", type=int, help="Year to filter books")

    # Show command with its specific arguments
    show_parser = subparsers.add_parser("show", help="Show books")
    show_parser.add_argument("--year", type=int, help="Year to filter books")
    show_parser.add_argument(
        "id", type=int, nargs="?", help="Show details for a specific book ID"
    )

    # Add command with its specific arguments
    add_parser = subparsers.add_parser("add", help="Add a book")
    add_parser.add_argument("--title", type=str, help="Title of the book")
    add_parser.add_argument("--author", type=str, help="Author of the book")
    add_parser.add_argument("--year", type=int, help="Year of the book")

    # Add command with its specific arguments
    import_parser = subparsers.add_parser("import", help="Import books")
    import_parser.add_argument("file", type=str, help="Goodreads CSV export file")

    args = vars(parser.parse_args())

    if args["version"]:
        print(f"libro v{__version__}")
        sys.exit()

    # if not specified on command-line figure it out
    if args["db"] is None:
        args["db"] = get_db_loc()

    if args["command"] is None:
        args["command"] = "show"

    if args.get("year") is None:
        args["year"] = datetime.now().year

    return args


def get_db_loc() -> Path:
    """Figure out where the libro.db file should be.
    See README for spec"""

    # check if tasks.db exists in current dir
    cur_dir = Path(Path.cwd(), "libro.db")
    if cur_dir.is_file():
        return cur_dir

    # check for env TASKS_DB
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

import argparse
import os
import sys
from pathlib import Path
from typing import Dict
from datetime import datetime
from appdirs import AppDirs

cmds = ["add", "del", "edit", "show", "search"]
__version__ = "0.1.0"


def init_args() -> Dict:
    """Parse and return the arguments."""
    parser = argparse.ArgumentParser(description="Book list")
    parser.add_argument("--db", help="SQLite file")
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("-i", "--info", action="store_true")
    parser.add_argument(
        "--year", type=int, help="Year to filter books (defaults to current year)"
    )
    parser.add_argument("command", choices=cmds, nargs="?")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = vars(parser.parse_args())

    if args["version"]:
        print(f"libro v{__version__}")
        sys.exit()

    # if not specified on command-line figure it out
    if args["db"] is None:
        args["db"] = get_db_loc()

    if args["command"] is None:
        args["command"] = "show"

    if args["year"] is None:
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

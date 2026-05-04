# AGENTS.md

This file provides guidance to LLMs working with code in this repository.

## Project Overview

Libro is a terminal-based reading tracker written in Python that stores data in a local SQLite database. It is a pure CLI tool, interactive input uses `prompt_toolkit` for field prompts with validation and autocomplete. Output is formatted with `rich` Python library.

## Development Commands

### Running

```bash
# Run the application
uv run libro              # Show books read this year
uv run libro add          # Add a book + review
uv run libro report       # Same as default
uv run libro --db ./libro.db report  # Use specific database file
```

### Using Justfile

```bash
just run          # Run the app
just test         # Run pytest tests
just lint         # Check with ruff
just lint-fix     # Fix lint issues
just type-check   # Run mypy
just ci           # Run all checks (lint, type-check, test)
just install      # Install dependencies with uv sync
just dev-install  # Install dev dependencies
just build        # Build the package
```

### Testing and Quality

```bash
uv run python -m pytest tests/ -v
uv run python -m ruff check src/libro/
uv run python -m mypy --package libro
```

## Code Architecture

### Project Structure

```
libro/
├── src/libro/
│   ├── main.py           # Entry point, command routing via match/case
│   ├── config.py         # Argument parsing and database location logic
│   ├── models.py         # Dataclasses: Book, Review, BookReview, ReadingList, ReadingListBook
│   └── actions/
│       ├── db.py         # Database init and migration
│       ├── show.py       # Display functions (rich tables)
│       ├── report.py     # Report views (author stats, yearly charts)
│       ├── modify.py     # Add/edit books and reviews (prompt_toolkit input)
│       ├── lists.py      # Reading list management
│       └── importer.py   # CSV import (Goodreads format and generic CSV)
└── tests/
```

### Key Technologies

- **CLI Parsing**: argparse with subparsers
- **Interactive Input**: prompt_toolkit (PromptSession with validators and completers)
- **Terminal Output**: rich (tables, progress bars, styled text)
- **Database**: SQLite3 (stdlib)
- **Package Manager**: uv

## Data Model

### Books vs Reviews

The application separates **books** from **reviews** to support:
- Books without reviews (unread books on a reading list)
- Multiple reviews per book (re-reads)

**Tables:**
1. `books` - Book metadata (title, author, pub_year, pages, genre)
2. `reviews` - Reading records (book_id, date_read, rating, review)
3. `reading_lists` - Curated book collections
4. `reading_list_books` - Many-to-many join table (with priority and added_date)

**Models** (all dataclasses in `models.py`):
- `Book` - Single book entity with `insert()`, `get_by_id()`, `find_by_title_author()`
- `Review` - Single review entity with `insert()`
- `BookReview` - Combined book + review, most commonly used for display; has `get_by_id()`
- `ReadingList` - List entity with full CRUD methods
- `ReadingListBook` - Association with `get_books_in_list()`, `get_list_stats()`

### Database Schema

```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    pub_year INTEGER,
    pages INTEGER,
    genre TEXT
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    date_read DATE,
    rating INTEGER,
    review TEXT,
    FOREIGN KEY(book_id) REFERENCES books(id)
);

CREATE TABLE reading_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE reading_list_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    added_date DATE DEFAULT CURRENT_DATE,
    priority INTEGER DEFAULT 0,
    FOREIGN KEY(list_id) REFERENCES reading_lists(id) ON DELETE CASCADE,
    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE(list_id, book_id)
);
```

## Application Flow

### Entry Point

`main.py` calls `init_args()` from `config.py`, connects to the database, runs `migrate_db()`, then routes to the correct action via `match args["command"]`.

### Database Location Priority

1. `--db` command-line flag
2. `libro.db` in current directory
3. `LIBRO_DB` environment variable
4. Platform-specific data directory (via `appdirs`):
   - Linux: `~/.local/share/Libro/mkaz/libro.db`
   - macOS: `~/Library/Application Support/Libro/mkaz/libro.db`
   - Windows: `%APPDATA%\mkaz\Libro\libro.db`

## CLI Commands

```bash
# Default - show books read this year
libro
libro report

# Year chart of books read
libro report --chart

# Author stats (all authors with counts)
libro report --author
# Books by specific author
libro report --author "Stephen King"

# Show book/review detail by review ID
libro report <id>

# Filter by year
libro report --year 2024

# Add book + review (interactive prompts)
libro add

# Book management
libro book                    # Show recent books
libro book <id>               # Show specific book
libro book add                # Add book only (no review)
libro book edit <id>          # Edit book details
libro book --author "King"    # Filter by author
libro book --title "Found"    # Filter by title
libro book --year 2024        # Filter by year

# Review management
libro review                  # Show recent reviews
libro review <id>             # Show review detail
libro review add <book_id>    # Add review to existing book
libro review edit <id>        # Edit review
libro review --author "King"  # Filter by author
libro review --year 2024      # Filter by year

# Reading list management
libro list create "Name" --description "..."
libro list show               # All lists
libro list show <id>          # Specific list
libro list add <list_id> [book_ids...]  # Add books to list (interactive if no IDs)
libro list remove <list_id> <book_id>
libro list stats              # All list stats
libro list stats <id>         # Specific list stats
libro list edit <id> --name "New Name"
libro list delete <id>
libro list import <file.csv> --name "List Name"

# Import from Goodreads CSV
libro import <file.csv>
```

## Important Patterns

### Interactive Input (modify.py)

`add_book_review()`, `add_book()`, `add_review()`, `edit_book()`, `edit_review()` all use `prompt_toolkit.PromptSession` with:
- **Validators**: `NonEmptyValidator`, `IntValidator`, `RatingValidator` (1-5), `DateValidator` (YYYY-MM-DD)
- **Completers**: `AuthorCompleter` (sorted by frequency), `GenreCompleter`
- Tab completion works in any field with a completer attached

### Date Handling

Dates are stored as ISO 8601 strings. `models.py` registers a SQLite adapter/converter:

```python
sqlite3.register_adapter(date, adapt_date_iso)     # date -> "YYYY-MM-DD"
sqlite3.register_converter("date", convert_date)   # bytes -> date
```

The connection must be opened with `detect_types=sqlite3.PARSE_DECLTYPES` for converters to fire, but the current code uses `db.row_factory = sqlite3.Row` without `detect_types`. Date fields come back as strings; convert with `date.fromisoformat()` if needed.

### Adding a New Action

1. Add argument parsing to `config.py` (argparse subparser or flag)
2. Create or update a function in the appropriate `actions/` file
3. Add a case in `main.py`'s `match args["command"]` block
4. Use `rich.Table` or `rich.console` for output; use `PromptSession` for interactive input

### Adding a New Store Query

SQL lives directly in the model methods (`models.py`) and action files. There is no separate store layer. Keep SELECT queries in model classmethods when returning typed objects; put display-only queries in `show.py` or `report.py`.

## Troubleshooting

### Duplicate Book on Import

`importer.py` calls `Book.find_by_title_author()` before inserting. If a book already exists, it skips the insert and adds a review to the existing book.

### Date Shows Wrong Value

Check that the date string is valid ISO format (`YYYY-MM-DD`). The `DateValidator` in `modify.py` enforces this on input. For database reads without `detect_types`, call `date.fromisoformat(row["date_read"])` explicitly.

### Reading List Migration

Old databases without reading list tables are handled by `migrate_db()` in `actions/db.py`, which runs on every startup and creates missing tables idempotently.

## Code Style

- Python 3.10+ (`match/case`, `list[str]` type hints)
- Dataclasses for models
- Type hints throughout; mypy enforced via `just type-check`
- ruff for linting and formatting
- No global state; `db` connection passed explicitly to every function

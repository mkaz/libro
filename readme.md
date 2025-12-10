# Libro

📚 Libro: A terminal-based tool to track your reading history, with your data stored locally in a SQLite database.

## Core Concepts

Libro separates **books** and **reviews** to give you flexibility in how you track your reading:

- **Books**: Store information about the book itself (title, author, pages, genre, publication year)
- **Reviews**: Track your personal reading experience (date read, rating, review text)

This separation allows you to:
- Add books to your database without having read them yet
- Add multiple reviews for the same book (re-reads)
- Maintain a clean library of books separate from your reading history

## Interface

Libro provides two ways to interact with your reading data:

### Interactive TUI (Default)

Launch with `libro` (no arguments) to start the interactive terminal interface:

**Key Bindings:**
- `↑/↓` or `j/k` - Navigate through the book list
- `/` - Search by title or author
- `a` - Toggle search between current year and all years (when searching)
- `a` - Add new book + review (when not searching)
- `y` - Select year to view
- `Enter` - View detailed information for selected book
- `Esc` - Clear search and return to year view
- `q` - Quit

**Features:**
- Browse books read by year
- Search across your entire reading history
- Year selector showing book counts per year
- Detailed book view with all information and reviews
- Add books and reviews in a single two-page form
- Autocomplete for author and genre fields (press Ctrl+E)

### Command Line Interface

**Report Command:**

Display a table of recent reviews (default: 50 most recent):
```bash
libro report
```

Filter by author (searches author field only):
```bash
libro report --author "Stephen King"
```

Filter by title (searches title field only):
```bash
libro report --title "Foundation"
```

Filter by year (shows books read in that year):
```bash
libro report --year 2024
```

Combine filters (e.g., books by an author read in a specific year):
```bash
libro report --author "King" --year 2024
```

**Chart Command:**

View yearly reading statistics:
```bash
libro chart
```

Example output:
```
                         Books Read by Year

  Year   Count   Bar
 ───────────────────────────────────────────────────────────────────
  2020   27      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2021   28      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2022   27      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2023   32      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2024   30      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2025   17      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
```

View monthly breakdown for a specific year:
```bash
libro chart --year 2024
```

Example output:
```
                    Books Read by Month in 2024

  Month        Count   Bar
 ───────────────────────────────────────────────────────────────────
  January      3       ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  February     2       ▄▄▄▄▄▄▄▄▄▄
  March        4       ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  April        2       ▄▄▄▄▄▄▄▄▄▄
```

## Install

### From Source

```bash
git clone https://github.com/mkaz/libro.git
cd libro
go build -o libro cmd/libro/main.go
./libro --help
```

You can copy the `libro` binary to somewhere in your PATH:

```bash
cp libro /usr/local/bin/
# or
cp libro ~/bin/
```

### Requirements

- Go 1.25 or higher
- SQLite3 (usually pre-installed on most systems)

## Setup

On first run, libro will create a `libro.db` database file. It will prompt for confirmation to proceed, which also shows the location where the file will be created.

**Database locations:**

The following order is used to determine the database location:

1. Using the `--db` flag on command-line
2. `libro.db` in current directory
3. Environment variable `LIBRO_DB` to specify custom file/location
4. Finally, the user's platform-specific data directory
    * Linux: `~/.local/share/libro/libro.db`
    * macOS: `~/Library/Application Support/libro/libro.db`
    * Windows: `%APPDATA%\libro\libro.db`

For example, if you want to create a new database file in the current directory:

```bash
libro --db ./libro.db
```

### Import from Goodreads

Libro can import your reading history from a Goodreads export CSV file:

```bash
libro import goodreads_library_export.csv
```

The `genre` field is not available in Goodreads exports. You can edit books to add genres after import through the TUI.

## Database Schema

### Books table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| title | string | Book title |
| author | string | Book author |
| pages | int | Number of pages in book |
| pub_year | int | Year book was published |
| genre | string | Genre (any string value) |

### Reviews table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| book_id | foreign key | Book identifier |
| date_read | date | Date book was read |
| rating | int | Rating between 1 and 5 |
| review | text | Review of book |

### Reading Lists table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| name | string | Reading list name (unique) |
| description | string | Optional description |
| created_date | date | Date the list was created |

### Reading List Books table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| list_id | foreign key | Reading list identifier |
| book_id | foreign key | Book identifier |
| added_date | date | Date book was added to list |
| priority | int | Priority/order in list (default: 0) |

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.


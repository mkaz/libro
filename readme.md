# Libro

Track your books read on the command-line in a sqlite3 database.

## Usage

Add new book: `libro add`

Show books read by year: `libro show --year 2024`

Show book details by id: `libro show 123`

Show books read by year: `libro report`

Show books read by author: `libro report --author`

## Setup

On first run, libro will create a `libro.db` database file based on database location. It will prompt for confirmation to proceed also showing the location where the file will be created.

**Database locations:**

The following order is used to determine the database location:

1. Using the `--db` flag on command-line.

2. `libro.db` in current directory

3. Environment variable `LIBRO_DB` to specify custom file/location

4. Finally, the user's platform-specific data directory
    * Linux: `~/.local/share/libro/libro.db`
    * macOS: `~/Library/Application Support/libro/libro.db`
    * Windows: `%APPDATA%\libro\libro.db`



# Database Schema

## Books table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| title | string | Book title |
| author | string | Book author |
| pages | int | Number of pages in book |
| pub_year | int | Year book was published |
| genre | string | Fiction or nonfiction |

## Reviews table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| book_id | foreign key | Book identifier |
| date_read | date | Date book was read |
| rating | float | Number between 0 and 5 |
| review | text | Review of book |


## TODO

- [ ] Init database
- [ ] Import Goodreads CSV
- [ ] Package for PyPI
- [ ] Edit Book
- [ ] Add flag --limit to author


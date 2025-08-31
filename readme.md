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

**Interactive TUI (Default):**
- `libro` - Launch the interactive terminal interface with search and navigation
- Navigate with arrow keys, search with `/`, add books with `a`, view lists with `l`
- Press `q` to quit, `?` for help with key bindings

**Command Line Interface:**
- `libro report` - Reading history table  
- `libro report --author` - Author statistics (most read authors)
- `libro report --author "Name"` - Books/reviews by specific author  
- `libro report --chart` - Yearly reading chart
- `libro report 123` - Book/review details for review id
- `libro add` - Add book + review
- `libro book` - Book management (show, add, edit)
- `libro review` - Review management (show, add, edit)
- `libro list` - Reading list management

## Usage

**Add books and review:**: `libro add`


### Book Management

Add book only (no review): `libro book add`

Show recent books: `libro book` (shows latest 20 books by default)

Show specific book: `libro book 42`

Edit book details only: `libro book edit 42`

**Search and filter books:**

Show books by author: `libro book --author "Stephen King"`

Show books by title: `libro book --title "Foundation"`

Show books published in specific year: `libro book --year 2024`

All search options support partial matching, so `--author "King"` will find "Stephen King", "Tabitha King", etc.


### Review Management

Show recent reviews: `libro review` (shows latest 20 reviews by default)

Show specific review: `libro review 123`

Add review to existing book: `libro review add 42`

Edit review details only: `libro review edit 123`

**Search and filter reviews:**

Show reviews by author: `libro review --author "Stephen King"` (searches book authors)

Show reviews by book title: `libro review --title "Foundation"` (searches book titles)

Show reviews from specific year: `libro review --year 2024` (searches by date_read)

All search options support partial matching, and year filtering uses the date the review was made, not the book's publication year.

### Reading Lists

Create a reading list: `libro list create "My Reading List" --description "Books to read"`

Show all reading lists: `libro list show`

Show specific list: `libro list show 1`

Import books to a new list: `libro list import books.csv --name "Sci-Fi Classics" --description "Science fiction must-reads"`

See: `libro --help` for more information.

### Examples

#### Interactive TUI Interface

The default interface is an interactive terminal application with search capabilities:

- Launch with `libro` (no arguments)
- Use arrow keys to navigate between books
- Press `/` to search by title or author
- Press `Enter` to view book details
- Press `a` to add new books
- Press `l` to view reading lists

#### CLI Report View

Access the traditional table view with `libro report`:

```
❯ libro report
                                 Books Read in 2025
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ ID         ┃ Title                        ┃ Author               ┃ Rating ┃ Date Read    ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Fiction    │                              │                      │        │              │
│ 1          │ Cujo                         │ Stephen King         │ 3      │ Jan 05, 2025 │
│ 585        │ The Midnight Library         │ Matt Haig            │ 5      │ Jan 13, 2025 │
│ 587        │ The Maid                     │ Nita Prose           │ 4      │ Jan 20, 2025 │
│ 589        │ Into the Water               │ Paula Hawkins        │ 2      │ Feb 02, 2025 │
│ 584        │ Salem's Lot                  │ Stephen King         │ 3      │ Mar 12, 2025 │
│ 595        │ The Thursday Murder Club     │ Richard Osman        │ 3      │ Mar 20, 2025 │
│ 596        │ Remarkably Bright Creatures  │ Shelby Van Pelt      │ 5      │ Mar 27, 2025 │
│ 598        │ Colorless Tsukuru Tazaki     │ Haruki Murakami      │ 3      │ Apr 09, 2025 │
│ 599        │ Ten                          │ Gretchen McNeil      │ 3      │ Apr 16, 2025 │
│            │                              │                      │        │              │
│ Nonfiction │                              │                      │        │              │
│ 586        │ The Art Thief                │ Michael Finkel       │ 4      │ Jan 14, 2025 │
│ 588        │ All the Pieces Matter        │ Jonathan Abrams      │ 3      │ Jan 27, 2025 │
│ 590        │ Supercommunicators           │ Charles Duhigg       │ 4      │ Feb 04, 2025 │
│ 593        │ Leonardo da Vinci            │ Walter Isaacson      │ 3      │ Mar 02, 2025 │
│ 594        │ The Leap to Leader           │ Adam Bryant          │ 3      │ Mar 08, 2025 │
│ 597        │ Team of Rivals               │ Doris Kearns Goodwin │ 3      │ Apr 06, 2025 │
└────────────┴──────────────────────────────┴──────────────────────┴────────┴──────────────┘
```


#### Books by Year Chart

```
❯ libro report --chart

                         Books Read by Year

  Year   Count   Bar
 ───────────────────────────────────────────────────────────────────
  2013   3       ▄▄▄▄
  2014   4       ▄▄▄▄▄▄
  2015   11      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2016   30      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2017   21      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2018   27      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2019   29      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2020   27      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2021   28      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2022   27      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2023   32      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2024   30      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  2025   17      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
```

#### Author Report and Filtering

Show author statistics (most read authors):
```
❯ libro report --author

         Most Read Authors

  Author                Books Read
 ──────────────────────────────────
  Stephen King          15
  George R.R. Martin    5
  Timothy Zahn          4
  Grady Hendrix         4
  Andy Weir             4
  William Zinsser       3
  Roald Dahl            3
  Riley Sager           3
  Philip K. Dick        3
  Neil Gaiman           3
  Natalie D. Richards   3
  Lucy Foley            3
  Cory Doctorow         3
```

Show books/reviews by specific author:
```
❯ libro report --author "Stephen King"

                                Books by Stephen King
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ ID ┃ Title                        ┃ Author        ┃ Rating ┃ Date Read    ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 1  │ Cujo                         │ Stephen King  │ 3      │ Jan 05, 2025 │
│ 584│ Salem's Lot                  │ Stephen King  │ 3      │ Mar 12, 2025 │
└────┴──────────────────────────────┴───────────────┴────────┴──────────────┘
```

## Reading Lists

Reading lists allow you to organize books into curated collections. You can create lists for different genres, themes, or reading goals.

### Creating and Managing Lists

Create a new reading list:
```bash
libro list create "2025 Reading Goals" --description "Books I want to read this year"
```

View all your reading lists:
```bash
❯ libro list show

                                    Reading Lists
┏━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Name               ┃ Description                      ┃ Total Books ┃ Read ┃ Unread ┃ Progress         ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 1  │ Sci-Fi Classics    │ Science fiction must-reads       │ 50          │ 12   │ 38     │ ██░░░░░░░░ 24.0% │
│ 2  │ Horror Collection  │ Spine-tingling tales             │ 30          │ 8    │ 22     │ ███░░░░░░░ 26.7% │
│ 3  │ Literary Classics  │ Timeless masterpieces            │ 45          │ 15   │ 30     │ ███░░░░░░░ 33.3% │
└────┴────────────────────┴──────────────────────────────────┴─────────────┴──────┴────────┴──────────────────┘

Use 'libro list show <id>' to see books in a specific list
```

View books in a specific list:
```bash
❯ libro list show 1

                           📚 Sci-Fi Classics - Science fiction must-reads
┏━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID ┃ Status ┃ Title                                    ┃ Author                 ┃ Genre           ┃ Rating ┃ Date Read  ┃
┡━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━┩
│ 42 │ 📖     │ Foundation                               │ Isaac Asimov           │ science fiction │ —      │ —          │
│ 43 │ 📖     │ Dune                                     │ Frank Herbert          │ science fiction │ —      │ —          │
│ 44 │ ✅     │ The Left Hand of Darkness                │ Ursula K. Le Guin      │ science fiction │ 5      │ 2024-12-15 │
│ 45 │ ✅     │ Neuromancer                              │ William Gibson         │ science fiction │ 4      │ 2024-11-20 │
└────┴────────┴──────────────────────────────────────────┴────────────────────────┴─────────────────┴────────┴────────────┘

📊 Progress: 12 read, 38 unread (24.0% complete)
```

### Adding Books to Lists

Add a new book to an existing list:
```bash
libro list add 1
```

This will prompt you to enter book details interactively.

### Importing Books to Lists

Import books from a CSV file and create a new list at the same time:
```bash
libro list import books.csv --name "Mystery Novels" --description "Page-turners and whodunits"
```

Import books to an existing list:
```bash
libro list import more-books.csv --id 1
```

**CSV Format**: The CSV file should have the following columns in order:
- Title
- Author  
- Publication Year (optional)
- Pages (optional)
- Genre (optional)

Example CSV:
```csv
Title,Author,Publication Year,Pages,Genre
The Martian,Andy Weir,2011,369,science fiction
Klara and the Sun,Kazuo Ishiguro,2021,303,literary fiction
```

### List Management

Edit a list's name or description:
```bash
libro list edit 1 --name "Updated Name" --description "New description"
```

Add a book to a list:
```bash
libro list add 1 42
```

Remove a book from a list:
```bash
libro list remove 1 42
```

Delete an entire list:
```bash
libro list delete 1
```

View statistics for all lists:
```bash
libro list stats
```

View statistics for a specific list:
```bash
libro list stats 1
```

## Install

Libro is packaged as `libro-book` on PyPI.

```
pip install libro-book
```

You can also clone this repository and install it locally:

```
git clone https://github.com/mkaz/libro.git
cd libro
pip install -e .
```

## Setup

On first run, libro will create a `libro.db` database file based on database location. It will prompt for confirmation to proceed which also shows the location where the file will be created.

**Database locations:**

The following order is used to determine the database location:

1. Using the `--db` flag on command-line.

2. `libro.db` in current directory

3. Environment variable `LIBRO_DB` to specify custom file/location

4. Finally, the user's platform-specific data directory
    * Linux: `~/.local/share/libro/libro.db`
    * macOS: `~/Library/Application Support/libro/libro.db`
    * Windows: `%APPDATA%\libro\libro.db`


For example, if you want to create a new database file in the current directory, you can use the following command:

```
libro --db ./libro.db
```

### Import from Goodreads

Libro can import your reading history from a Goodreads export CSV file.

```
libro import goodreads_library_export.csv
```

There is a `genre` field that accepts any string value, but this data is not available in the Goodreads export. You can edit books to add or change the genre after import.

# Database Schema

## Books table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| title | string | Book title |
| author | string | Book author |
| pages | int | Number of pages in book |
| pub_year | int | Year book was published |
| genre | string | Genre (any string value) |

## Reviews table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| book_id | foreign key | Book identifier |
| date_read | date | Date book was read |
| rating | float | Number between 0 and 5 |
| review | text | Review of book |

## Reading Lists table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| name | string | Reading list name (unique) |
| description | string | Optional description |
| created_date | date | Date the list was created |

## Reading List Books table

| Field | Type | Description |
|-------|------|-------------|
| id | primary key | Unique identifier |
| list_id | foreign key | Reading list identifier |
| book_id | foreign key | Book identifier |
| added_date | date | Date book was added to list |
| priority | int | Priority/order in list (default: 0) |

# Changelog

See [GitHub Releases](https://github.com/mkaz/libro/releases) for the changelog.


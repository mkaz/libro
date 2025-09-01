"""Main TUI application for Libro"""

import sqlite3
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Header, Input, Label
from textual.binding import Binding

# Removed get_reviews import - now using custom filtered query
# Screen imports are now lazy-loaded when needed


class LibroTUI(App):
    """Main TUI application for Libro"""

    TITLE = "Libro"

    CSS = """
    .footer-menu {
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text;
        content-align: center middle;
    }

    .search-bar {
        dock: bottom;
        height: 1;
        background: $primary;
        display: none;
    }

    .search-bar.visible {
        display: block;
    }

    .search-input {
        width: 100%;
        background: transparent;
        border: none;
    }

    .genre-table {
        margin-bottom: 0;
    }

    .header-label {
        margin-top: 1;
    }

    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("a", "add_book", "Add Book"),
        Binding("y", "select_year", "Select Year"),
        Binding("l", "lists_view", "Lists"),
        Binding("s", "cycle_sort", "Sort"),
        Binding("/", "search", "Search"),
        Binding("escape", "exit_search", "Exit Search"),
        Binding("enter", "view_details", "View Details"),
    ]

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self.current_year = datetime.now().year
        # Sorting state: 0=Date, 1=Title, 2=Author, 3=Genre, 4=Rating
        self.sort_column = 0
        self.sort_columns = ["Date", "Title", "Author", "Genre", "Rating"]
        # Search state
        self.current_search = ""
        self.show_all_years = False
        self.search_visible = False

    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header()
        yield Container(id="books_container")
        yield Container(
            Label(
                "q: Quit | /: Search | Esc: Exit Search | a: Add Book | y: Year | s: Sort | l: Lists"
            ),
            classes="footer-menu",
        )
        yield Container(
            Input(
                placeholder="Search title/author...",
                id="search_input",
                classes="search-input",
            ),
            classes="search-bar",
            id="search_container",
        )

    def on_mount(self) -> None:
        """Initialize the table when the app starts"""
        self.theme = "textual-dark"
        # If there's a current search, show the search bar
        if self.current_search:
            self.search_visible = True
            search_container = self.query_one("#search_container", Container)
            search_container.add_class("visible")
            search_input = self.query_one("#search_input", Input)
            search_input.value = self.current_search
        self.update_subtitle()
        self.load_books_data()

    def update_subtitle(self) -> None:
        """Update the subtitle to show current year, search, and sorting"""
        sort_name = self.sort_columns[self.sort_column]

        # Build subtitle with search info
        if self.show_all_years:
            year_info = "All Years"
        else:
            year_info = f"{self.current_year}"

        if self.current_search:
            search_str = f" | Search: {self.current_search}"
        else:
            search_str = ""

        self.sub_title = (
            f"Books Read in {year_info} - Sorted by {sort_name}{search_str}"
        )

    def load_books_data(self) -> None:
        """Load and display books with current filters applied"""
        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            # Get books with filters applied
            books = self._get_filtered_books(db)

            # Clear the books container
            container = self.query_one("#books_container", Container)
            container.remove_children()

            if not books:
                if self.current_search:
                    container.mount(
                        Label(f"No books found matching '{self.current_search}'")
                    )
                elif self.show_all_years:
                    container.mount(Label("No books found"))
                else:
                    container.mount(Label(f"No books found for {self.current_year}"))
                return

            # Sort books based on current sort column
            sorted_books = self._sort_books(list(books))

            # Group books by Fiction/Nonfiction
            fiction_books = []
            nonfiction_books = []

            for book in sorted_books:
                if book["genre"] != "nonfiction":
                    fiction_books.append(book)
                else:
                    nonfiction_books.append(book)

            # Create tables for Fiction and Nonfiction groups
            groups = [("Fiction", fiction_books), ("Nonfiction", nonfiction_books)]

            for group_name, group_books in groups:
                if not group_books:  # Skip empty groups
                    continue

                # Add group header label
                header_label = Label(
                    f"[bold cyan]{group_name} ({len(group_books)})[/bold cyan]",
                    classes="header-label",
                )
                container.mount(header_label)

                # Create table for this group
                table: DataTable = DataTable(cursor_type="row", classes="genre-table")
                table.add_column("Review ID", width=10)
                table.add_column("Title", width=30)
                table.add_column("Author", width=25)
                table.add_column("Genre", width=15)
                table.add_column("Rating", width=8)
                table.add_column("Date Read", width=12)

                # Add books for this group
                for book in group_books:
                    # Format date
                    date_str = book["date_read"]
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                            formatted_date = date_obj.strftime("%b %d")
                        except ValueError:
                            formatted_date = date_str
                    else:
                        formatted_date = ""

                    table.add_row(
                        str(book["review_id"]),
                        book["title"],
                        book["author"],
                        book["genre"] or "",
                        str(book["rating"]) if book["rating"] else "",
                        formatted_date,
                    )

                container.mount(table)

        except sqlite3.Error as e:
            container = self.query_one("#books_container", Container)
            container.remove_children()
            container.mount(Label(f"Database error: {e}"))
        finally:
            if "db" in locals():
                db.close()

    def _sort_books(self, books: list) -> list:
        """Sort books based on the current sort column"""
        if self.sort_column == 0:  # Date
            return sorted(books, key=lambda x: x["date_read"] or "", reverse=False)
        elif self.sort_column == 1:  # Title
            return sorted(books, key=lambda x: (x["title"] or "").lower())
        elif self.sort_column == 2:  # Author
            return sorted(books, key=lambda x: (x["author"] or "").lower())
        elif self.sort_column == 3:  # Genre
            return sorted(books, key=lambda x: (x["genre"] or "").lower())
        elif self.sort_column == 4:  # Rating
            return sorted(books, key=lambda x: x["rating"] or 0, reverse=True)
        else:
            return books

    def _get_filtered_books(self, db):
        """Get books with current search and year selection applied"""
        # Start with base query
        query = """
            SELECT 
                r.id as review_id, 
                b.id as book_id,
                b.title, 
                b.author, 
                b.genre, 
                b.pub_year,
                b.pages,
                r.rating, 
                r.date_read,
                r.review
            FROM reviews r
            JOIN books b ON r.book_id = b.id
            WHERE 1=1
        """
        params = []

        # Apply year filter
        if not self.show_all_years:
            query += " AND strftime('%Y', r.date_read) = ?"
            params.append(str(self.current_year))

        # Apply search filter (title or author)
        if self.current_search:
            search_term = f"%{self.current_search}%"
            query += (
                " AND (LOWER(b.title) LIKE LOWER(?) OR LOWER(b.author) LIKE LOWER(?))"
            )
            params.extend([search_term, search_term])

        query += " ORDER BY r.date_read DESC"

        cursor = db.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def action_search(self) -> None:
        """Toggle search bar visibility"""
        search_container = self.query_one("#search_container", Container)

        if not self.search_visible:
            # Show search bar
            search_container.add_class("visible")
            self.search_visible = True
            # Focus the search input and restore current search
            search_input = self.query_one("#search_input", Input)
            search_input.value = self.current_search  # Restore current search term
            search_input.focus()
            # If there's existing search text, show all years
            if self.current_search:
                self.show_all_years = True
        else:
            self.action_exit_search()

    def action_exit_search(self) -> None:
        """Exit search mode if active, otherwise do nothing"""
        if self.search_visible:
            search_container = self.query_one("#search_container", Container)
            search_container.remove_class("visible")
            self.search_visible = False
            self.current_search = ""
            self.show_all_years = False
            self.query_one("#search_input", Input).value = ""
            self.update_subtitle()
            self.load_books_data()

    def on_input_changed(self, event) -> None:
        """Handle live search as user types in search bar"""
        if event.input.id == "search_input" and self.search_visible:
            search_text = event.value.strip()
            self.current_search = search_text

            # Show all years when searching, return to year view when cleared
            if search_text:
                self.show_all_years = True
            else:
                self.show_all_years = False

            self.update_subtitle()
            self.load_books_data()

            # Keep search bar visible as long as we're in search mode
            # (The bar should only hide when user explicitly exits search mode)

    async def action_quit(self) -> None:
        """Exit the application"""
        self.exit()

    def action_refresh(self) -> None:
        """Refresh the current view"""
        self.load_books_data()

    def action_view_details(self) -> None:
        """View details of the selected book"""
        self._view_selected_book()

    def on_data_table_row_selected(self, event) -> None:
        """Handle row selection in the data table"""
        self._view_selected_book()

    def _view_selected_book(self) -> None:
        """View details of the currently selected book"""
        # Find the currently focused table
        focused_widget = self.focused
        if not isinstance(focused_widget, DataTable):
            self.notify("Select a book row first")
            return

        table = focused_widget

        # Get the selected row data
        row_data = table.get_row_at(table.cursor_row)

        if not row_data or len(row_data) == 0:
            self.notify("Invalid selection")
            return

        # The first column should be the Review ID
        review_id_str = str(row_data[0])

        # Skip empty rows
        if not review_id_str or review_id_str == "":
            self.notify("Select a book row to view details")
            return

        try:
            review_id = int(review_id_str)
            # Open the book detail screen
            from .screens.book_detail import BookDetailScreen

            self.push_screen(BookDetailScreen(self.db_path, review_id))
        except ValueError:
            self.notify("Select a book row to view details")
            return

    def action_add_book(self) -> None:
        """Add a new book and review"""
        from .screens.add_book import AddBookScreen

        self.push_screen(AddBookScreen(self.db_path))

    def action_select_year(self) -> None:
        """Open year selection dialog"""
        from .screens.year_select import YearSelectScreen

        self.push_screen(YearSelectScreen(self.db_path, self.current_year))

    def change_year(self, new_year: int) -> None:
        """Change the current year and reload data"""
        self.current_year = new_year
        self.update_subtitle()
        self.load_books_data()

    def action_cycle_sort(self) -> None:
        """Cycle through different sorting options"""
        self.sort_column = (self.sort_column + 1) % len(self.sort_columns)
        sort_name = self.sort_columns[self.sort_column]
        self.notify(f"Sorting by {sort_name}")
        self.update_subtitle()
        self.load_books_data()

    def action_lists_view(self) -> None:
        """Switch to reading lists view"""
        from .screens.reading_lists import ReadingListsScreen

        self.push_screen(ReadingListsScreen(self.db_path))

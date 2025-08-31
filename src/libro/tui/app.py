"""Main TUI application for Libro"""

import sqlite3
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Header, Label
from textual.binding import Binding

from libro.actions.show import get_reviews
from .screens.book_detail import BookDetailScreen
from .screens.add_book import AddBookScreen
from .screens.year_select import YearSelectScreen
from .screens.reading_lists import ReadingListsScreen


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
        Binding("b", "books_view", "Books"),
        Binding("l", "lists_view", "Lists"),
        Binding("s", "cycle_sort", "Sort"),
        Binding("enter", "view_details", "View Details"),
        Binding("question_mark", "help", "Help"),
    ]

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self.current_year = datetime.now().year
        # Sorting state: 0=Date, 1=Title, 2=Author, 3=Genre, 4=Rating
        self.sort_column = 0
        self.sort_columns = ["Date", "Title", "Author", "Genre", "Rating"]

    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header()
        yield Container(id="books_container")
        yield Container(
            Label(
                "q: Quit | r: Refresh | a: Add Book | y: Select Year | s: Sort | Enter: View Details | ?: Help"
            ),
            classes="footer-menu",
        )

    def on_mount(self) -> None:
        """Initialize the table when the app starts"""
        self.theme = "textual-dark"
        self.update_subtitle()
        self.load_books_data()

    def update_subtitle(self) -> None:
        """Update the subtitle to show current year and sorting"""
        sort_name = self.sort_columns[self.sort_column]
        self.sub_title = f"Books Read in {self.current_year} - Sorted by {sort_name}"

    def load_books_data(self) -> None:
        """Load and display books read in current year with Fiction/Nonfiction grouping"""
        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            # Get books for current year (same logic as CLI report command)
            books = get_reviews(db, year=self.current_year)

            # Clear the books container
            container = self.query_one("#books_container", Container)
            container.remove_children()

            if not books:
                container.mount(Label("No books found for current year"))
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
            self.push_screen(BookDetailScreen(self.db_path, review_id))
        except ValueError:
            self.notify("Select a book row to view details")
            return

    def action_add_book(self) -> None:
        """Add a new book and review"""
        self.push_screen(AddBookScreen(self.db_path))

    def action_select_year(self) -> None:
        """Open year selection dialog"""
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

    def action_books_view(self) -> None:
        """Switch to books-only view (placeholder for now)"""
        self.notify("Books view coming soon!")

    def action_lists_view(self) -> None:
        """Switch to reading lists view"""
        self.push_screen(ReadingListsScreen(self.db_path))

    def action_help(self) -> None:
        """Show help dialog (placeholder for now)"""
        self.notify("Help: Use arrow keys to navigate, Enter to select, q to quit")

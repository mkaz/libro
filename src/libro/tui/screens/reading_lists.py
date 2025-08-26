"""Reading lists overview screen for displaying all reading lists"""

import sqlite3
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Label
from textual.screen import ModalScreen
from textual.binding import Binding

from libro.models import ReadingList, ReadingListBook


class ReadingListsScreen(ModalScreen):
    """Modal screen to display all reading lists with statistics"""

    CSS = """
    ReadingListsScreen {
        align: center middle;
    }

    .lists-container {
        width: 95;
        height: 45;
        max-height: 20;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    .lists-header {
        color: $text;
        background: $accent;
        padding: 0 1;
        margin: 0 0 1 0;
        text-style: bold;
        text-align: center;
    }

    .lists-table {
        height: auto;
        max-height: 15;
        margin: 1 0;
    }

    .help-text {
        margin: 1 0 0 0;
        color: $text-muted;
        text-align: center;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "view_list", "View List"),
    ]

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        """Create the reading lists view"""
        with Container(classes="lists-container"):
            yield Label("📚 Reading Lists", classes="lists-header")
            yield DataTable(cursor_type="row", classes="lists-table", id="lists_table")

    def on_mount(self) -> None:
        """Load reading lists when screen opens"""
        self.load_reading_lists()

    def load_reading_lists(self) -> None:
        """Load and display all reading lists with statistics"""
        try:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row

            # Get all reading lists
            lists = ReadingList.get_all(db)

            # Set up the table
            table = self.query_one("#lists_table", DataTable)
            table.clear(columns=True)
            table.add_column("ID", width=6, key="id")
            table.add_column("Name", width=35, key="name")
            table.add_column("Total", width=8, key="total")
            table.add_column("Read", width=6, key="read")
            table.add_column("Unread", width=8, key="unread")
            table.add_column("Progress", width=15, key="progress")

            if not lists:
                table.add_row("", "No reading lists found", "", "", "", "")
                table.add_row(
                    "",
                    "Create a list with: libro list create <name>",
                    "",
                    "",
                    "",
                    "",
                )
            else:
                for reading_list in lists:
                    if reading_list.id is None:
                        continue  # Skip lists without IDs

                    # Get statistics for this list
                    stats = ReadingListBook.get_list_stats(db, reading_list.id)

                    # Create progress bar representation
                    progress_text = f"{stats['completion_percentage']:.0f}%"
                    if stats["total_books"] > 0:
                        progress_bar = "█" * int(stats["completion_percentage"] / 10)
                        progress_bar += "░" * (
                            10 - int(stats["completion_percentage"] / 10)
                        )
                        progress_display = f"{progress_bar} {progress_text}"
                    else:
                        progress_display = "—"

                    table.add_row(
                        str(reading_list.id),
                        reading_list.name,
                        str(stats["total_books"]),
                        str(stats["books_read"]),
                        str(stats["books_unread"]),
                        progress_display,
                        key=str(
                            reading_list.id
                        ),  # Use list ID as row key for navigation
                    )

        except sqlite3.Error as e:
            table = self.query_one("#lists_table", DataTable)
            table.clear(columns=True)
            table.add_column("Error", width=50)
            table.add_row(f"Database error: {e}")
        finally:
            if "db" in locals():
                db.close()

    def action_view_list(self) -> None:
        """View details of the selected reading list"""
        table = self.query_one("#lists_table", DataTable)

        row_data = table.get_row_at(table.cursor_row)
        if not row_data or len(row_data) == 0:
            self.notify("Invalid selection")
            return

        # Get the list ID from the first column
        list_id_str = str(row_data[0])
        if not list_id_str or list_id_str == "":
            self.notify("No reading list to view")
            return

        try:
            list_id = int(list_id_str)
            from .reading_list import ReadingListScreen

            self.app.push_screen(ReadingListScreen(self.db_path, list_id))
        except ValueError:
            self.notify("Invalid reading list ID")

    def on_data_table_row_selected(self, event) -> None:
        """Handle row selection in the data table"""
        self.action_view_list()

    def action_close(self) -> None:
        """Close the reading lists screen"""
        self.app.pop_screen()

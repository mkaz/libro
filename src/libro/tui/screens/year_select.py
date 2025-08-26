"""Year selection screen for filtering books by year"""

import sqlite3
from datetime import datetime
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, OptionList
from textual.screen import ModalScreen
from textual.binding import Binding


class YearSelectScreen(ModalScreen):
    """Modal screen for selecting a year to view books from"""

    CSS = """
    YearSelectScreen {
        align: center middle;
    }
    
    .year-container {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, db_path: str, current_year: int):
        super().__init__()
        self.db_path = db_path
        self.current_year = current_year
        self.available_years = self._get_available_years()

    def _get_available_years(self):
        """Get all years that have books with reviews in the database"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            cursor.execute("""
                SELECT DISTINCT strftime('%Y', r.date_read) as year
                FROM reviews r
                WHERE r.date_read IS NOT NULL
                ORDER BY year DESC
            """)

            years = []
            for row in cursor.fetchall():
                year = row[0]  # Keep as string
                years.append(year)

            # If no years found, add current year as fallback
            if not years:
                current = str(datetime.now().year)
                years.append(current)

            return years

        except sqlite3.Error:
            # Fallback to current year if DB query fails
            current = str(datetime.now().year)
            return [current]
        finally:
            if "db" in locals():
                db.close()

    def compose(self) -> ComposeResult:
        """Create the year selection interface"""
        with Container(classes="year-container"):
            yield Label("Select Year to View")
            yield Label(f"Currently showing: {self.current_year}")
            yield OptionList(*self.available_years, id="year_options")

    def on_option_list_option_selected(self, event) -> None:
        """Handle year selection from option list"""
        if event.option_list.id == "year_options":
            selected_year_str = str(event.option.prompt)
            selected_year = int(selected_year_str)

            # Get the main app screen properly
            main_app = self.app
            if hasattr(main_app, "change_year"):
                main_app.change_year(selected_year)
            else:
                # Try to access the main screen through screen stack
                if main_app.screen_stack:
                    main_screen = main_app.screen_stack[0]
                    if hasattr(main_screen, "change_year"):
                        main_screen.change_year(selected_year)

            # Close the year selection screen
            self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel year selection"""
        self.app.pop_screen()

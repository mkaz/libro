"""TUI interface for Libro using Textual"""

from .app import LibroTUI


def launch_tui(db_path: str) -> None:
    """Launch the TUI application"""
    app = LibroTUI(db_path)
    app.run()


__all__ = ["launch_tui", "LibroTUI"]

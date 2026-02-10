"""
Diff Visualization for A-Team CLI.
"""

import difflib
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


class DiffViewer:
    """
    Handles generating and displaying diffs in the terminal.
    """

    @staticmethod
    def show_diff(console: Console, path: str, old_content: str, new_content: str):
        """
        Displays a side-by-side or unified diff of a proposed file change.
        """
        if old_content == new_content:
            console.print(f"[yellow]No changes proposed for {path}.[/yellow]")
            return

        diff_lines = list(difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{path}",
            tofile=f"b/{path}"
        ))

        if not diff_lines:
            console.print(f"[yellow]No structural changes proposed for {path}.[/yellow]")
            return

        table = Table(title=f"📝 Proposed Changes: {path}", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Type", width=10)
        table.add_column("Content")

        for line in diff_lines[2:]: # Skip header
            if line.startswith("+"):
                table.add_row(Text("ADDED", style="green"), Text(line[1:].rstrip(), style="green"))
            elif line.startswith("-"):
                table.add_row(Text("REMOVED", style="red"), Text(line[1:].rstrip(), style="red"))
            elif line.startswith(" "):
                # Context lines - maybe show only a few?
                pass

        console.print(table)
        
        # Also provide a 'Syntax' view of the new content for context
        console.print(Panel(
            Syntax(new_content, lexer="python", line_numbers=True, theme="monokai", word_wrap=True),
            title="Full Content Preview",
            border_style="dim"
        ))

from __future__ import annotations

import json
from typing import Any, Iterable

from rich.console import Console
from rich.json import JSON
from rich.markdown import Markdown
from rich.table import Table


class Printer:
    def __init__(self, *, json_output: bool = False) -> None:
        self.console = Console()
        self.json_output = json_output

    def print_json(self, payload: Any) -> None:
        self.console.print(JSON.from_data(payload))

    def print_message(self, message: str, *, style: str = "green") -> None:
        self.console.print(message, style=style)

    def print_error(self, message: str) -> None:
        self.console.print(message, style="bold red")

    def print_markdown(self, content: str) -> None:
        self.console.print(Markdown(content))

    def print_table(self, title: str, columns: list[str], rows: Iterable[Iterable[Any]]) -> None:
        if self.json_output:
            payload = [dict(zip(columns, [self._normalize_cell(cell) for cell in row], strict=False)) for row in rows]
            self.print_json(payload)
            return

        table = Table(title=title)
        for column in columns:
            table.add_column(column)
        for row in rows:
            table.add_row(*[self._normalize_cell(cell) for cell in row])
        self.console.print(table)

    def emit(self, payload: Any, *, title: str | None = None) -> None:
        if self.json_output:
            self.print_json(payload)
            return
        if isinstance(payload, str):
            self.console.print(payload)
            return
        formatted = json.dumps(payload, indent=2, default=str)
        if title:
            self.console.rule(title)
        self.console.print(formatted)

    @staticmethod
    def _normalize_cell(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return str(value)


from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterable
from typing import Any

import yaml
from rich.console import Console
from rich.json import JSON
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


class Printer:
    def __init__(self, json_output: bool = False) -> None:
        self.console = Console()
        self.json_output = json_output

    def emit(self, payload: Any, title: str | None = None) -> None:
        if self.json_output:
            self.console.print(JSON.from_data(payload))
            return
        if isinstance(payload, str):
            self.console.print(payload)
            return
        text = json.dumps(payload, indent=2, default=str)
        if title:
            self.console.print(Panel.fit(text, title=title))
        else:
            self.console.print(text)

    def table(self, title: str, columns: list[str], rows: Iterable[Iterable[Any]]) -> None:
        table = Table(title=title)
        for column in columns:
            table.add_column(column)
        for row in rows:
            table.add_row(*[self._cell(value) for value in row])
        self.console.print(table)

    def render_format(self, payload: list[dict[str, Any]] | dict[str, Any], output: str) -> None:
        if output == "json":
            self.console.print(JSON.from_data(payload))
            return
        if output == "yaml":
            self.console.print(yaml.safe_dump(payload, sort_keys=False))
            return
        if output == "csv":
            rows = payload if isinstance(payload, list) else [payload]
            output_buffer = io.StringIO()
            if rows:
                writer = csv.DictWriter(output_buffer, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            self.console.print(output_buffer.getvalue().rstrip())
            return
        if isinstance(payload, dict):
            self.emit(payload)
            return
        self.table(
            "Output",
            list(payload[0].keys()) if payload else [],
            [[row.get(key, "") for key in payload[0].keys()] for row in payload] if payload else [],
        )

    def markdown(self, content: str) -> None:
        self.console.print(Markdown(content))

    def success(self, message: str) -> None:
        self.console.print(message, style="bold green")

    def warning(self, message: str) -> None:
        self.console.print(message, style="yellow")

    def error(self, message: str) -> None:
        self.console.print(message, style="bold red")

    @staticmethod
    def _cell(value: Any) -> str:
        return "" if value is None else str(value)

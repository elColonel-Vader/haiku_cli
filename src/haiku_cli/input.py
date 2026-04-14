from __future__ import annotations

import sys

import click


def read_haiku_text() -> str:
    if not sys.stdin.isatty():
        return sys.stdin.read()

    click.echo("Haiku eingeben:")
    lines = []
    for index in range(1, 4):
        line = click.prompt(f"Zeile {index}", prompt_suffix=" > ", type=str).strip()
        lines.append(line)
    return "\n".join(lines)

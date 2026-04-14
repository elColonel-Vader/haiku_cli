from __future__ import annotations

from typing import Any

from rich.console import Console

from haiku_cli.models import HaikuAnalysis


def _status_markup(valid: bool) -> tuple[str, str]:
    return ("[green]✓[/green]", "gruen") if valid else ("[red]✗[/red]", "rot")


def render_error(message: str) -> None:
    console = Console()
    console.print(f"[red]Fehler:[/red] {message}")


def render_analysis(analysis: HaikuAnalysis, *, debug: bool = False) -> None:
    console = Console()
    for index, line in enumerate(analysis.lines, start=1):
        symbol, _ = _status_markup(line.valid)
        console.print(f"{symbol} Zeile {index}: {line.total} Silben ({line.expected} erwartet)")

        if debug and line.words:
            pieces = " ".join(f"{word.display} ({word.syllables})" for word in line.words)
            end_symbol = "✓" if line.valid else "✗"
            console.print(f"    {pieces} = {line.total} {end_symbol}")

    if analysis.valid_structure:
        console.print("[green]✓ Struktur: gültiges 5-7-5[/green]")
    else:
        console.print("[red]✗ Struktur: kein gültiges 5-7-5[/red]")


def _print_criterion(console: Console, label: str, valid: bool, detail: str) -> None:
    symbol, _ = _status_markup(valid)
    console.print(f"{symbol} {label}: {detail}")


def render_ai_feedback(
    result: dict[str, Any],
    analysis: HaikuAnalysis,
    *,
    strict: bool = False,
    computed_score: int,
) -> None:
    console = Console()

    kigo = result.get("kigo") or {}
    juxtaposition = result.get("juxtaposition") or {}
    mono_no_aware = result.get("mono_no_aware") or {}
    kireji = result.get("kireji") or {}
    suggestions = result.get("suggestions") or []

    _print_criterion(
        console,
        "Silben (Programm)",
        analysis.valid_structure,
        "gültiges 5-7-5" if analysis.valid_structure else "kein gültiges 5-7-5",
    )
    _print_criterion(
        console,
        "Kigo",
        bool(kigo.get("present")),
        ("vorhanden" if kigo.get("present") else "nicht erkannt")
        + (f" ({kigo.get('word')}, {kigo.get('season')})" if kigo.get("word") else ""),
    )
    _print_criterion(
        console,
        "Kireji",
        bool(kireji.get("present")),
        ("vorhanden" if kireji.get("present") else "nicht erkannt")
        + (f" - {kireji.get('description')}" if kireji.get("description") else ""),
    )
    _print_criterion(
        console,
        "Naturbild",
        bool(result.get("nature_imagery")),
        "ja" if result.get("nature_imagery") else "nein",
    )
    _print_criterion(
        console,
        "Gegenwart",
        bool(result.get("present_tense")),
        "ja" if result.get("present_tense") else "nein",
    )
    _print_criterion(
        console,
        "Gegenüberstellung",
        bool(juxtaposition.get("present")),
        ("ja" if juxtaposition.get("present") else "nein")
        + (f" - {juxtaposition.get('description')}" if juxtaposition.get("description") else ""),
    )
    if mono_no_aware.get("present") or mono_no_aware.get("description"):
        console.print(
            "[yellow]Hinweis:[/yellow] Mono no aware:"
            f" {mono_no_aware.get('description') or 'vorhanden'}"
        )

    console.print(f"[cyan]Gesamtwertung:[/cyan] {computed_score}/10")

    if suggestions:
        heading = "Vorschläge" if strict else "Hinweise"
        console.print(f"[cyan]{heading}:[/cyan]")
        for item in suggestions:
            console.print(f"  - {item}")


def render_warnings(warnings: list[str]) -> None:
    if not warnings:
        return

    console = Console()
    for warning in warnings:
        console.print(f"[yellow]Warnung:[/yellow] {warning}")

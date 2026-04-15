from __future__ import annotations

from typing import Any

from rich.console import Console

from haiku_cli.models import HaikuAnalysis
from haiku_cli.scoring import (
    ScoreBreakdown,
    get_image_coherence_level,
    get_juxtaposition_level,
    get_kigo_level,
    get_kireji_level,
    get_mono_no_aware_level,
    get_nature_imagery_level,
    get_present_tense_level,
    get_show_not_tell_level,
)


def _status_markup(valid: bool) -> tuple[str, str]:
    return ("[green]✓[/green]", "gruen") if valid else ("[red]✗[/red]", "rot")


def _format_score(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def _level_markup(level: str) -> str:
    styles = {
        "strong": "green",
        "coherent": "green",
        "showing": "green",
        "present": "green",
        "weak": "yellow",
        "loosely_connected": "yellow",
        "mixed": "yellow",
        "absent": "red",
        "fragmented": "red",
        "telling": "red",
    }
    style = styles.get(level, "white")
    return f"[{style}]{level}[/{style}]"


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


def _criterion_explanation(value: Any, *, fallback: str = "") -> str:
    if isinstance(value, dict):
        explanation = value.get("explanation") or value.get("description")
        if explanation:
            return str(explanation)
        word = value.get("word")
        season = value.get("season")
        if word and season:
            return f"{word} ({season})"
        if word:
            return str(word)
    return fallback


def _print_level_criterion(console: Console, label: str, level: str, detail: str) -> None:
    if detail:
        console.print(f"• {label}: {_level_markup(level)} - {detail}")
        return
    console.print(f"• {label}: {_level_markup(level)}")


def render_ai_feedback(
    result: dict[str, Any],
    analysis: HaikuAnalysis,
    *,
    strict: bool = False,
    score_breakdown: ScoreBreakdown,
) -> None:
    console = Console()

    suggestions = result.get("suggestions") or []

    console.print(
        f"[cyan]Form:[/cyan] {_format_score(score_breakdown.form)}/{ScoreBreakdown.FORM_MAX}"
    )
    _print_criterion(
        console,
        "Silben (Programm)",
        analysis.valid_structure,
        "gültiges 5-7-5" if analysis.valid_structure else "kein gültiges 5-7-5",
    )

    console.print(
        f"[cyan]Haiku-Qualität:[/cyan] {_format_score(score_breakdown.quality)}/"
        f"{ScoreBreakdown.QUALITY_MAX}"
    )
    _print_level_criterion(
        console,
        "Kigo",
        get_kigo_level(result),
        _criterion_explanation(result.get("kigo"), fallback="Kein klarer Saisonbezug erkannt."),
    )
    _print_level_criterion(
        console,
        "Kireji",
        get_kireji_level(result),
        _criterion_explanation(result.get("kireji"), fallback="Keine markante Zäsur erkannt."),
    )
    _print_level_criterion(
        console,
        "Naturbild",
        get_nature_imagery_level(result),
        _criterion_explanation(result.get("nature_imagery"), fallback="Kein konkretes Naturbild erkannt."),
    )
    _print_level_criterion(
        console,
        "Gegenwart",
        get_present_tense_level(result),
        _criterion_explanation(result.get("present_tense"), fallback="Zeitbezug ist nicht klar im Präsens verankert."),
    )
    _print_level_criterion(
        console,
        "Gegenüberstellung",
        get_juxtaposition_level(result),
        _criterion_explanation(result.get("juxtaposition"), fallback="Kein produktiver Kontrast erkannt."),
    )
    _print_level_criterion(
        console,
        "Bildkohärenz",
        get_image_coherence_level(result),
        _criterion_explanation(result.get("image_coherence"), fallback="Die Bilder bilden keinen klaren Strang."),
    )
    _print_level_criterion(
        console,
        "Show vs. Tell",
        get_show_not_tell_level(result),
        _criterion_explanation(result.get("show_not_tell"), fallback="Die Bildsprache bleibt nicht durchgehend konkret."),
    )

    console.print(f"[cyan]Gesamtwertung:[/cyan] {score_breakdown.overall}/10")
    _print_level_criterion(
        console,
        "Mono no aware",
        get_mono_no_aware_level(result),
        _criterion_explanation(
            result.get("mono_no_aware"),
            fallback="Keine zusätzliche Vergänglichkeits-Schicht erkennbar.",
        ),
    )
    console.print(
        f"• Normalisiert: {score_breakdown.normalized}/{ScoreBreakdown.OVERALL_MAX}"
    )
    if score_breakdown.mono_no_aware_bonus:
        console.print(f"• Mono no aware Bonus: +{score_breakdown.mono_no_aware_bonus}")
    if score_breakdown.suggestions_cap_applied:
        console.print(
            "• Hinweis-Deckel: 10/10 wurde wegen offener Hinweise auf 9/10 reduziert."
        )

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

from __future__ import annotations

from typing import Any, Iterable

from rich.console import Console

from haiku_cli.models import HaikuAnalysis
from haiku_cli.scoring import ScoreBreakdown


def _status_markup(valid: bool) -> tuple[str, str]:
    return ("[green]✓[/green]", "gruen") if valid else ("[red]✗[/red]", "rot")


def _format_score(value: float) -> str:
    return f"{value:.1f}"


def _summary_style(verdict: str) -> tuple[str, str]:
    if verdict in {"MEISTERHAFT", "GUT"}:
        return "[green]✓[/green]", "green"
    if verdict == "ORDENTLICH":
        return "[yellow]⚠[/yellow]", "yellow"
    return "[red]✗[/red]", "red"


def _note(value: Any, *, fallback: str = "") -> str:
    if isinstance(value, dict):
        note = value.get("note")
        if isinstance(note, str) and note.strip():
            return note.strip()
    return fallback


def _string_list(value: Any, key: str) -> list[str]:
    if not isinstance(value, dict):
        return []
    raw = value.get(key)
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if str(item).strip()]


def _detail_text(parts: Iterable[str]) -> str:
    filtered = [part for part in parts if part]
    return " | ".join(filtered)


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


def render_quiet_ai_feedback(score_breakdown: ScoreBreakdown) -> None:
    console = Console()
    symbol, style = _summary_style(score_breakdown.verdict)
    console.print(
        f"{symbol} [{style}]{score_breakdown.verdict}[/{style}] "
        f"{_format_score(score_breakdown.overall)}/10"
    )


def render_ai_feedback(
    result: dict[str, Any],
    analysis: HaikuAnalysis,
    *,
    strict: bool = False,
    score_breakdown: ScoreBreakdown,
) -> None:
    del strict
    console = Console()

    symbol, style = _summary_style(score_breakdown.verdict)
    console.print(
        f"{symbol} [{style}]Verdict:[/{style}] [{style}]{score_breakdown.verdict}[/{style}] "
        f"({_format_score(score_breakdown.overall)}/10)"
    )
    console.print(
        f"[cyan]Form:[/cyan] {'gültig' if analysis.valid_structure else 'ungültig'}es 5-7-5"
    )

    reasoning = result.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        console.print(f"[cyan]Reasoning:[/cyan] {reasoning.strip()}")

    kigo = result.get("kigo")
    kigo_details = _detail_text(
        (
            f"Wort: {kigo.get('word')}" if isinstance(kigo, dict) and kigo.get("word") else "",
            f"Jahreszeit: {kigo.get('season')}"
            if isinstance(kigo, dict) and kigo.get("season")
            else "",
            _note(kigo, fallback="Kein klares Jahreszeitenwort erkannt."),
        )
    )
    console.print(f"• Kigo: {score_breakdown.kigo}/3 - {kigo_details}")

    kireji = result.get("kireji")
    kireji_details = _detail_text(
        (
            f"Schnitt: {kireji.get('cut_point')}"
            if isinstance(kireji, dict) and kireji.get("cut_point")
            else "",
            _note(kireji, fallback="Keine tragfähige Zäsur erkannt."),
        )
    )
    console.print(f"• Kireji: {score_breakdown.kireji}/3 - {kireji_details}")

    bild = result.get("bild")
    bild_details = _detail_text(
        (
            f"Konkrete Bilder: {', '.join(_string_list(bild, 'concrete_images'))}"
            if _string_list(bild, "concrete_images")
            else "",
            f"Abstrakta: {', '.join(_string_list(bild, 'abstract_words'))}"
            if _string_list(bild, "abstract_words")
            else "",
            _note(bild, fallback="Die Bildsprache bleibt unklar."),
        )
    )
    console.print(f"• Bild / Sinneseindruck: {score_breakdown.bild}/3 - {bild_details}")

    gegenwart = result.get("gegenwart")
    gegenwart_details = _detail_text(
        (
            f"Zeitprobleme: {', '.join(_string_list(gegenwart, 'tense_issues'))}"
            if _string_list(gegenwart, "tense_issues")
            else "",
            _note(gegenwart, fallback="Der Augenblick ist nicht konsequent im Präsens verankert."),
        )
    )
    console.print(f"• Gegenwart: {score_breakdown.gegenwart}/2 - {gegenwart_details}")

    natur = result.get("natur")
    natur_details = _detail_text(
        (
            f"Naturelemente: {', '.join(_string_list(natur, 'elements'))}"
            if _string_list(natur, "elements")
            else "",
            _note(natur, fallback="Kein tragender Naturbezug erkennbar."),
        )
    )
    console.print(f"• Naturbezug: {score_breakdown.natur}/2 - {natur_details}")

    verdichtung = result.get("verdichtung")
    verdichtung_details = _detail_text(
        (
            f"Füllwörter: {', '.join(_string_list(verdichtung, 'filler_words'))}"
            if _string_list(verdichtung, "filler_words")
            else "",
            _note(verdichtung, fallback="Der Ausdruck ist nicht maximal verdichtet."),
        )
    )
    console.print(f"• Verdichtung: {score_breakdown.verdichtung}/2 - {verdichtung_details}")

    console.print(
        f"[cyan]Gewichtete Punkte:[/cyan] "
        f"{score_breakdown.weighted_points}/{ScoreBreakdown.MAX_POSSIBLE}"
    )
    console.print(f"[cyan]Gesamtwertung:[/cyan] {_format_score(score_breakdown.overall)}/10")
    if score_breakdown.hard_fail_triggered:
        reason = score_breakdown.hard_fail_reason or "Hard-Fail-Bedingung ausgelöst."
        console.print(
            f"[red]Hard Fail:[/red] Ja ({reason}) -> Deckel auf "
            f"{_format_score(ScoreBreakdown.HARD_FAIL_CAP)}/10"
        )
    else:
        console.print("[green]Hard Fail:[/green] Nein")

    suggestions = [str(item) for item in result.get("suggestions") or [] if str(item).strip()]
    if suggestions:
        console.print("[cyan]Vorschläge:[/cyan]")
        for item in suggestions:
            console.print(f"  - {item}")


def render_warnings(warnings: list[str]) -> None:
    if not warnings:
        return

    console = Console()
    for warning in warnings:
        console.print(f"[yellow]Warnung:[/yellow] {warning}")

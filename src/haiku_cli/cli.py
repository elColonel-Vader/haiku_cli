from __future__ import annotations

import click

from haiku_cli import __version__
from haiku_cli.ai.runner import (
    AIResponseError,
    ProviderUnavailable,
    evaluate_strict_result,
    run_ai_check,
)
from haiku_cli.ai.suggestions import sanitize_suggestions
from haiku_cli.input import read_haiku_text
from haiku_cli.output import render_ai_feedback, render_analysis, render_error, render_warnings
from haiku_cli.parser import ParseError, parse_haiku
from haiku_cli.scoring import ScoreBreakdown, compute_score
from haiku_cli.validate import validate_haiku


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
@click.option("--check", is_flag=True, help="Führt zusätzlich eine KI-Haikuprüfung aus.")
@click.option("--fix", is_flag=True, help="Liefert KI-Verbesserungsvorschläge.")
@click.option("--strict", is_flag=True, help="Bewertet traditionelle Haiku-Regeln strenger.")
@click.option("--quiet", is_flag=True, help="Keine Ausgabe, nur Exit-Code.")
@click.option("--debug", is_flag=True, help="Zeigt Silbenaufschlüsselung pro Wort.")
@click.option(
    "--provider",
    type=click.Choice(["auto", "ollama", "lmstudio", "claude"], case_sensitive=False),
    default="auto",
    show_default=True,
    help="KI-Provider für --check und --fix. auto prüft zuerst LM Studio, dann Ollama.",
)
@click.option("--model", default=None, help="Optionaler Modellname für den KI-Provider.")
def main(
    check: bool,
    fix: bool,
    strict: bool,
    quiet: bool,
    debug: bool,
    provider: str,
    model: str | None,
) -> None:
    try:
        text = read_haiku_text()
        lines = parse_haiku(text)
    except ParseError as exc:
        if not quiet:
            render_error(str(exc))
        raise SystemExit(2) from exc

    analysis = validate_haiku(lines)
    warnings: list[str] = []
    ai_result: dict | None = None
    score_breakdown: ScoreBreakdown | None = None

    if check or fix or strict:
        try:
            ai_result = run_ai_check(
                lines,
                analysis,
                provider=provider.lower(),
                strict=strict,
                fix=fix,
                model=model,
            )
            ai_result["suggestions"] = sanitize_suggestions(
                list(ai_result.get("suggestions") or []),
                valid_structure=analysis.valid_structure,
            )
            score_breakdown = compute_score(
                analysis, ai_result, suggestions=list(ai_result.get("suggestions") or [])
            )
            ai_result["overall_score"] = score_breakdown.overall
        except (ProviderUnavailable, AIResponseError) as exc:
            warnings.append(str(exc))

    if not quiet:
        render_analysis(analysis, debug=debug)
        if ai_result is not None and score_breakdown is not None:
            render_ai_feedback(
                ai_result,
                analysis,
                strict=strict,
                score_breakdown=score_breakdown,
            )
        render_warnings(warnings)

    exit_code = 0 if analysis.valid_structure else 1
    if strict and ai_result is not None and not evaluate_strict_result(ai_result):
        exit_code = 1

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()

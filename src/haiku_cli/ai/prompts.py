from __future__ import annotations

from haiku_cli.models import HaikuAnalysis


def build_system_prompt(*, strict: bool, fix: bool) -> str:
    strict_note = (
        "Bewerte streng nach traditionellen Haiku-Merkmalen."
        if strict
        else "Bewerte ausgewogen und praxisnah."
    )
    fix_note = (
        "Liefere konkrete Verbesserungsvorschläge, wenn Regeln nicht erfüllt sind."
        if fix
        else "Liefere nur Hinweise, keine Umschreibung des Haikus."
    )
    return (
        "Du bist ein Haiku-Experte. Analysiere das folgende deutsche Haiku. "
        "Antworte ausschließlich als JSON ohne Markdown. "
        "Die vom Programm gelieferte Silbenanalyse ist verbindlich und darf nicht "
        "widersprochen werden. Poetische Inversion oder ungewöhnliche Wortstellung "
        "ist nicht automatisch erklärende Prosa. "
        f"{strict_note} {fix_note}"
    )


def build_user_prompt(lines: tuple[str, str, str], analysis: HaikuAnalysis) -> str:
    line1, line2, line3 = lines
    structure = "gültig" if analysis.valid_structure else "ungültig"
    syllable_summary = "\n".join(
        (
            f"- Zeile {index}: {line.total}/{line.expected} Silben -> "
            f"{'OK' if line.valid else 'NICHT OK'}"
        )
        for index, line in enumerate(analysis.lines, start=1)
    )
    return f"""Analysiere dieses deutsche Haiku.

Haiku:
{line1}
{line2}
{line3}

Verbindliche Silbenanalyse des Programms:
{syllable_summary}
- Struktur insgesamt: {structure}

Wichtige Regeln für deine Analyse:
- Widersprich der verbindlichen Silbenanalyse nicht.
- Behaupte nicht, die Form sei kein 5-7-5, wenn die Struktur insgesamt als gültig markiert ist.
- Kritisiere poetische Inversion oder ungewöhnliche Wortstellung
  nicht pauschal als erklärend oder prosaisch.

Antworte ausschließlich in JSON mit diesem Schema:
{{
  "kigo": {{"present": bool, "word": str, "season": str}},
  "kireji": {{"present": bool, "description": str}},
  "present_tense": bool,
  "nature_imagery": bool,
  "juxtaposition": {{"present": bool, "description": str}},
  "mono_no_aware": {{"present": bool, "description": str}},
  "suggestions": ["string"],
  "syllable_check": {{
    "line1": {{"words": [{{"word": str, "syllables": int}}], "total": int}},
    "line2": {{"words": [{{"word": str, "syllables": int}}], "total": int}},
    "line3": {{"words": [{{"word": str, "syllables": int}}], "total": int}}
  }}
}}"""

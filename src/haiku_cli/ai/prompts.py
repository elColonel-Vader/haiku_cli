from __future__ import annotations


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
        f"{strict_note} {fix_note}"
    )


def build_user_prompt(lines: tuple[str, str, str]) -> str:
    line1, line2, line3 = lines
    return f"""Analysiere dieses deutsche Haiku.

Haiku:
{line1}
{line2}
{line3}

Antworte ausschließlich in JSON mit diesem Schema:
{{
  "kigo": {{"present": bool, "word": str, "season": str}},
  "kireji": {{"present": bool, "description": str}},
  "present_tense": bool,
  "nature_imagery": bool,
  "juxtaposition": {{"present": bool, "description": str}},
  "mono_no_aware": {{"present": bool, "description": str}},
  "overall_score": 1,
  "suggestions": ["string"],
  "syllable_check": {{
    "line1": {{"words": [{{"word": str, "syllables": int}}], "total": int}},
    "line2": {{"words": [{{"word": str, "syllables": int}}], "total": int}},
    "line3": {{"words": [{{"word": str, "syllables": int}}], "total": int}}
  }}
}}"""

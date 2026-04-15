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
- Bewerte Kigo, Kireji, Naturbild, Gegenwart und Gegenüberstellung
  mit den Stufen strong | weak | absent.
- Bewerte image_coherence mit coherent | loosely_connected | fragmented.
- Bewerte show_not_tell mit showing | mixed | telling.
- Bewerte mono_no_aware nur mit present | absent.

Leitplanken für die Stufen:
- Kigo strong: konkrete jahreszeitliche Referenz, die Stimmung trägt.
- Kigo weak: Naturbezug ohne klare saisonale Verankerung.
- Kireji strong: deutliche Zäsur mit Spannung oder Schnittwirkung.
- Kireji weak: hörbare Pause ohne markante Kontrastwirkung.
- Naturbild strong: konkret, sensorisch, spezifisch.
- Naturbild weak: Natur nur generisch oder als Kulisse.
- Gegenwart strong: der Moment ist klar im Präsens gefasst.
- Gegenwart weak: überwiegend Präsens, aber zeitlich unscharf.
- Gegenüberstellung strong: zwei Ebenen erzeugen produktive Spannung.
- Gegenüberstellung weak: mehrere Bilder sind da, aber die Spannung bleibt flach.
- image_coherence coherent: Motive greifen ineinander oder beleuchten sich rückwirkend.
- image_coherence loosely_connected: Zusammenhang ist da, aber die Bildsprünge bleiben spürbar.
- image_coherence fragmented: jede Zeile eröffnet eine neue Bildwelt.
- show_not_tell showing: Emotionen entstehen aus konkreten Bildern.
- show_not_tell mixed: überwiegend bildlich, aber mit erklärendem abstrakten Anteil.
- show_not_tell telling: Abstrakta oder Zustände werden direkt benannt.
- mono_no_aware present: Vergänglichkeit schwingt still mit, ohne explizit benannt zu werden.

Antworte ausschließlich in JSON mit diesem Schema:
{{
  "kigo": {{"level": "strong|weak|absent", "explanation": str}},
  "kireji": {{"level": "strong|weak|absent", "explanation": str}},
  "present_tense": {{"level": "strong|weak|absent", "explanation": str}},
  "nature_imagery": {{"level": "strong|weak|absent", "explanation": str}},
  "juxtaposition": {{"level": "strong|weak|absent", "explanation": str}},
  "image_coherence": {{"level": "coherent|loosely_connected|fragmented", "explanation": str}},
  "show_not_tell": {{"level": "showing|mixed|telling", "explanation": str}},
  "mono_no_aware": {{"level": "present|absent", "explanation": str}},
  "suggestions": ["string"],
  "syllable_check": {{
    "line1": {{"words": [{{"word": str, "syllables": int}}], "total": int}},
    "line2": {{"words": [{{"word": str, "syllables": int}}], "total": int}},
    "line3": {{"words": [{{"word": str, "syllables": int}}], "total": int}}
  }}
}}"""

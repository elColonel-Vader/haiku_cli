from __future__ import annotations

from haiku_cli.models import HaikuAnalysis


def build_system_prompt(*, strict: bool, fix: bool) -> str:
    del strict
    suggestions_note = (
        "Formuliere die Verbesserungsvorschläge konkret und umsetzbar."
        if fix
        else "Formuliere höchstens drei knappe Verbesserungsvorschläge."
    )
    return (
        "Du bist ein strenger Haiku-Meister mit tiefem Verständnis für die japanische "
        "Haiku-Tradition. Bewerte das folgende Haiku KRITISCH. Sei NICHT nachsichtig. "
        "Ein gutes Haiku erreicht 7+/10. Die meisten Haiku sind mittelmäßig (4-6). "
        "Antworte AUSSCHLIESSLICH in kompaktem JSON. Sprache für Beschreibungen: Deutsch. "
        "Die vom Programm gelieferte Silbenanalyse ist verbindlich und darf nicht "
        "widersprochen werden. Die 5-7-5-Prüfung wird lokal und programmatisch "
        "entschieden, nicht vom Modell. Nutze die unten definierte Bewertungsrubrik "
        "und gib nur Felder aus, die im JSON-Schema verlangt werden. "
        f"{suggestions_note}"
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
    return f"""Analysiere dieses deutsche Haiku nach Haiku CLI v2 Strict.

Haiku:
{line1}
{line2}
{line3}

Verbindliche Silbenanalyse des Programms:
{syllable_summary}
- Struktur insgesamt: {structure}

Bewertungskategorien (gewichtet):

1. KIGO (Jahreszeitenwort) — Gewicht: 25%
   - Explizites Jahreszeitenwort vorhanden? (z. B. Kirschblüte, Schnee, Zikade)
   - Nicht: vage Stimmungen oder Tageszeiten ohne Jahreszeitbezug
   - Streng: "Nacht" allein = kein Kigo. "Mondnacht im Herbst" = Kigo.
   - Score 0: kein Kigo erkennbar
   - Score 1: implizit oder vage
   - Score 2: klares, erkennbares Jahreszeitenwort
   - Score 3: starkes, spezifisches Kigo mit kultureller Tiefe

2. KIREJI (Schnitt oder Zäsur) — Gewicht: 20%
   - Gibt es einen klaren Bruch zwischen zwei Bildern oder Gedanken?
   - Im Deutschen: Gedankenstrich, Punkt, Doppelpunkt oder klare Zäsur
   - Streng: Bloßer Zeilenumbruch ist kein Kireji.
   - Score 0: kein Schnitt
   - Score 1: leichte Zäsur, Bilder zu ähnlich
   - Score 2: klarer Schnitt zwischen verschiedenen Bildern
   - Score 3: meisterhafter Schnitt mit überraschendem Kontrast

3. KONKRETES BILD / SINNESEINDRUCK — Gewicht: 25%
   - Jede Zeile soll ein konkretes, sinnliches Bild erzeugen
   - Streng: abstrakte Begriffe wie Geduld, Liebe, Zeit, Hoffnung = Punktabzug
   - Zeigen, nicht erzählen; keine Moral
   - Score 0: überwiegend abstrakt, kein Bild
   - Score 1: ein konkretes Bild, Rest abstrakt
   - Score 2: durchgehend bildlich, aber konventionell
   - Score 3: lebendige, überraschende Sinneseindrücke

4. GEGENWART & UNMITTELBARKEIT — Gewicht: 10%
   - Haiku steht im Präsens und beschreibt einen Augenblick
   - Keine Vergangenheit, keine Zukunft, kein "wird", kein "war"
   - Score 0: Vergangenheit oder Zukunft
   - Score 1: überwiegend Gegenwart mit Ausnahmen
   - Score 2: konsequent im Augenblick

5. NATURBEZUG — Gewicht: 10%
   - Bezug zur natürlichen Welt (Tiere, Pflanzen, Wetter, Landschaft)
   - Streng: rein urbane oder technische Motive = max. Score 1
   - Score 0: kein Naturbezug
   - Score 1: minimaler oder metaphorischer Naturbezug
   - Score 2: starker, authentischer Naturbezug

6. VERDICHTUNG & ÖKONOMIE — Gewicht: 10%
   - Kein überflüssiges Wort. Jedes Wort trägt Bedeutung.
   - Füllwörter (und, der, ein, es, so, auch) = Punktabzug
   - Streng: "Ein Frosch springt in das Wasser" enthält mehrere Füllwörter.
   - Score 0: viele Füllwörter, aufgebläht
   - Score 1: einige überflüssige Wörter
   - Score 2: maximal verdichtet, jedes Wort zählt

Hard-Fail-Bedingungen (Gesamtscore wird auf max. 3.0 gedeckelt):
- Haiku erklärt oder moralisiert
- Haiku ist ein verkappter Aphorismus oder Sprichwort
- Alle drei Zeilen beschreiben denselben Gedanken ohne Kontrast
- Reine Abstraktion ohne ein einziges konkretes Bild

Scoring:
- Berechne den gewichteten Durchschnitt skaliert auf 1-10.
- Formel: ((kigo*25 + kireji*20 + bild*25 + gegenwart*10 + natur*10 + verdichtung*10) / 270) * 10
- Runde auf eine Dezimalstelle.
- Wenn Hard Fail ausgelöst wird, setze overall_score auf höchstens 3.0.

Verdict-Skala:
- 8.0-10.0 = MEISTERHAFT
- 6.5-7.9 = GUT
- 4.5-6.4 = ORDENTLICH
- 2.5-4.4 = SCHWACH
- 0.0-2.4 = UNGENÜGEND

Kalibrierungsbeispiele:
1. Alter Teich —
   Frosch springt hinein.
   Wasserklang.
   Erwartung: starkes Naturbild, klarer Schnitt, dichter Ausdruck; nach obiger Formel ca. 9.1.

2. Geduld ist eine Kraft
   die uns durch den Winter trägt
   bis Frühling dann kommt
   Erwartung: Hard Fail wegen Aphorismus und Abstraktion; overall_score höchstens 3.0.

3. Frühlingsnacht, lauwarm —
   Triebe zeichnen neues Bild.
   Geduld ist Pflaster.
   Erwartung: klar erkennbares Haiku mit abstrakter Schwäche; mittlerer bis guter Bereich.

Gib eine knappe Gesamtbegründung nur im Feld "reasoning" wieder, nicht außerhalb des JSON.
Halte alle Notizen kurz, damit die JSON-Antwort vollständig geschlossen wird.

Antworte ausschließlich in JSON mit diesem Schema:
{{
  "reasoning": "knappe Gesamtbegründung in Deutsch",
  "kigo": {{
    "score": 0,
    "word": null,
    "season": null,
    "note": "kurze Begründung"
  }},
  "kireji": {{
    "score": 0,
    "cut_point": "wo ist der Schnitt",
    "note": "kurze Begründung"
  }},
  "bild": {{
    "score": 0,
    "concrete_images": ["Liste"],
    "abstract_words": ["Liste"],
    "note": "kurze Begründung"
  }},
  "gegenwart": {{
    "score": 0,
    "tense_issues": ["Liste"],
    "note": "kurze Begründung"
  }},
  "natur": {{
    "score": 0,
    "elements": ["Liste"],
    "note": "kurze Begründung"
  }},
  "verdichtung": {{
    "score": 0,
    "filler_words": ["Liste"],
    "note": "kurze Begründung"
  }},
  "hard_fail": {{
    "triggered": false,
    "reason": null
  }},
  "overall_score": 0.0,
  "verdict": "MEISTERHAFT|GUT|ORDENTLICH|SCHWACH|UNGENÜGEND",
  "suggestions": ["max 3 konkrete Verbesserungsvorschläge"]
}}"""

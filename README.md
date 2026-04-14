# Haiku CLI

Ein deutschsprachiges CLI zum Prüfen von Haikus auf 5-7-5.

## Installation

```bash
pip install -e .
```

Optional mit KI-Extras:

```bash
pip install -e ".[ai,dev]"
```

## Verwendung

Interaktiv:

```bash
haiku
```

Beispiel:

```text
Haiku eingeben:
Zeile 1 > Kirschblüten fallen
Zeile 2 > leiser Regen über Moos
Zeile 3 > Frühling atmet still
```

Mit Pipe:

```bash
printf "Kirschblüten fallen\nleiser Regen über Moos\nFrühling atmet still\n" | haiku
```

Debug-Ausgabe:

```bash
haiku --debug
```

Optionale KI-Prüfung:

```bash
haiku --check --provider ollama
```

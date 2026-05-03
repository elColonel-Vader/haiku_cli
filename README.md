# Haiku CLI

Ein deutschsprachiges CLI zum Prüfen von Haikus auf 5-7-5 mit optionaler
KI-Analyse.

## Voraussetzungen

- Python `3.11` oder neuer
- `pip` oder `pipx`
- Optional für lokale KI-Checks (siehe Abschnitt **KI-Prüfung**):
  - **LM Studio** (OpenAI-kompatibler Local Server; Standardmodell-ID: `google/gemma-4-e4b`) oder **Ollama**
  - bei `--provider auto` wird zuerst LM Studio versucht, danach Ollama

Das Projekt ist als normales Python-Paket gebaut und funktioniert auf
macOS, Linux und Windows.

## Installation

Es gibt zwei sinnvolle Wege:

### Option A: globales CLI für Endnutzer mit `pipx`

Wenn `haiku` systemweit als Befehl verfügbar sein soll, ist `pipx` die
einfachste und portabelste Lösung.

1. Repository klonen oder herunterladen
2. Im Projektordner installieren:

```bash
pipx install .
```

Mit KI-Abhängigkeiten:

```bash
pipx install ".[ai]"
```

Danach sollte `haiku` direkt im Terminal verfügbar sein.

Installation von `pipx`:

- macOS: `brew install pipx`
- Linux: `python3 -m pip install --user pipx`
- Windows (PowerShell): `py -m pip install --user pipx`

Wenn `haiku` nach der Installation nicht gefunden wird, öffne ein neues
Terminal oder führe `pipx ensurepath` aus.

### Option B: lokale Installation in einer virtuellen Umgebung

Das ist die beste Variante für Entwicklung oder wenn du lieber mit einem
projektlokalen Python arbeitest.

#### 1. Virtuelle Umgebung anlegen

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows cmd.exe:

```bat
py -m venv .venv
.\.venv\Scripts\activate.bat
```

#### 2. Paket installieren

Normale CLI-Nutzung:

```bash
python -m pip install -e .
```

Mit KI-Abhängigkeiten:

```bash
python -m pip install -e ".[ai]"
```

Für Entwicklung:

```bash
python -m pip install -e ".[ai,dev]"
```

Für breitere deutsche Compound-Erkennung:

```bash
python -m pip install -e ".[compounds]"
```

Ab Python 3.12 wird dafür `charsplit-fst` genutzt. Unter Python 3.11 fällt das
Extra auf `compound-split` zurück, damit die deklarierte Python-3.11-Unterstützung
installierbar bleibt.

Wichtig: In dieser Variante funktioniert `haiku` nur, solange die virtuelle
Umgebung aktiv ist.

## Erste Prüfung nach der Installation

```bash
haiku --help
haiku --version
```

## Verwendung

### Interaktiv

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

### Mit detaillierter Silbenanalyse

```bash
haiku --debug
```

### Nur Exit-Code, keine Ausgabe

```bash
haiku --quiet
```

Mit KI-Prüfung bleibt `--quiet` absichtlich nicht komplett stumm, sondern
gibt nur `VERDICT SCORE/10` aus:

```bash
haiku --check --quiet
```

### Pipe-Modus

macOS / Linux:

```bash
printf "Kirschblüten fallen\nleiser Regen über Moos\nFrühling atmet still\n" | haiku
```

Windows PowerShell:

```powershell
"Kirschblüten fallen`nleiser Regen über Moos`nFrühling atmet still" | haiku
```

## Bewertungssystem

Die Strukturprüfung und die Haiku-Bewertung sind getrennt:

- **Form**: Die 5-7-5-Silbenprüfung wird lokal und deterministisch entschieden.
- **Inhalt**: Die KI liefert Kategorie-Scores und Begründungen im v2-JSON-Schema.
- **Gesamtwertung**: Das CLI berechnet `overall_score` immer lokal neu und
  vertraut nicht blind auf modellgelieferte Scores oder Verdicts.

### Bewertete Kategorien

| Kategorie | Bereich | Gewicht |
| --- | --- | --- |
| Kigo | `0-3` | `25%` |
| Kireji | `0-3` | `20%` |
| Bild / Sinneseindruck | `0-3` | `25%` |
| Gegenwart | `0-2` | `10%` |
| Naturbezug | `0-2` | `10%` |
| Verdichtung | `0-2` | `10%` |

### Formel

```text
overall_score = round(
  ((kigo*25 + kireji*20 + bild*25 + gegenwart*10 + natur*10 + verdichtung*10) / 270) * 10,
  1
)
```

Wenn `hard_fail.triggered = true`, wird `overall_score` auf maximal `3.0`
gedeckelt.

Wichtig: Die **Formel ist die Quelle der Wahrheit**. Beispielwerte im Prompt
oder in der Doku dienen nur der Kalibrierung.

### Verdict-Skala

| Score | Verdict |
| --- | --- |
| `8.0-10.0` | `MEISTERHAFT` |
| `6.5-7.9` | `GUT` |
| `4.5-6.4` | `ORDENTLICH` |
| `2.5-4.4` | `SCHWACH` |
| `0.0-2.4` | `UNGENÜGEND` |

### Strict-Modus

- `--strict` besteht nur bei gültigem `5-7-5` **und** `overall_score >= 6.5`.
- `4.5-6.4` bleibt textlich `ORDENTLICH`, endet unter `--strict` aber mit
  Exit-Code `1`.
- Wenn keine KI-Bewertung ausgeführt werden kann, schlägt `--strict` ebenfalls
  fehl.

### Beispielausgabe

```text
✓ Verdict: GUT (7.0/10)
Form: gültiges 5-7-5
Reasoning: Kategorie für Kategorie geprüft.
• Kigo: 2/3 - Wort: Kirschblüten | Jahreszeit: Frühling | Klares Kigo.
• Kireji: 2/3 - Schnitt: nach Zeile 1 | Saubere Zäsur.
• Bild / Sinneseindruck: 2/3 - Konkrete Bilder: Kirschblüten, Regen, Moos | Konkrete Bilder tragen das Haiku.
• Gegenwart: 2/2 - Im Augenblick gehalten.
• Naturbezug: 2/2 - Naturelemente: Kirschblüten, Regen, Moos | Starker Naturbezug.
• Verdichtung: 1/2 - Knapper Ausdruck.
Gewichtete Punkte: 190/270
Gesamtwertung: 7.0/10
Hard Fail: Nein
```

## KI-Prüfung

Die KI-Funktionen sind optional. Das CLI funktioniert auch ohne lokale
Server oder Claude.

### Provider `lmstudio` (Standard)

Ohne `--provider` nutzt das CLI **`lmstudio`**. Das ist der bevorzugte
Standardfall für lokale Checks.

```bash
haiku --check
```

Wenn du stattdessen eine automatische Fallback-Kette willst:

```bash
haiku --check --provider auto
```

`auto` versucht zuerst **LM Studio** und fällt bei Nichterreichbarkeit oder
Fehlschlag auf **Ollama** zurück.

### LM Studio

[LM Studio](https://lmstudio.ai/) stellt einen OpenAI-kompatiblen **Local Server**
bereit (Doku: [OpenAI Compatibility](https://lmstudio.ai/docs/developer/openai-compat),
Server starten: [Core Server](https://lmstudio.ai/docs/developer/core/server)).
Standard-**Base-URL** im CLI: `http://127.0.0.1:1234/v1` (Port 1234; damit
umgeht man häufige `localhost`→IPv6-Probleme; bei Bedarf `LMSTUDIO_BASE_URL`
setzen). Standard-**Modell-ID** (wie unter „Loaded Models“ in LM Studio):

```text
google/gemma-4-e4b
```

1. LM Studio öffnen, das Modell laden und den **Local Server** starten
   (Menü: Server läuft auf Port 1234).
2. `haiku` muss den **gleichen Rechner** erreichen wie LM Studio: `localhost`
   im Terminal ist nur der Rechner, auf dem der Befehl läuft (bei **SSH auf einen
   anderen Host** daher `export LMSTUDIO_BASE_URL=http://<IP-des-Mac>:1234` mit
   erreichbarer IP/Firewall).
3. Haiku prüfen:

```bash
haiku --check --provider lmstudio
```

Oder über **`auto`** (siehe oben), wenn du den Ollama-Fallback ausdrücklich
aktivieren willst.

Basis-URL anpassen (anderer Port oder anderer Host):

```bash
export LMSTUDIO_BASE_URL=http://127.0.0.1:1234
haiku --check --provider lmstudio
```

Weitere Varianten:

```bash
haiku --fix
haiku --strict
haiku --check --provider lmstudio --model google/gemma-4-e4b
```

Ohne `--model` nutzt das CLI **`google/gemma-4-e4b`**. Abweichende Bezeichnung in
deiner LM-Studio-Liste per `--model "<id>"` setzen. Die Anfrage nutzt LM Studios
strukturiertes JSON-Schema; falls ein Modell die Antwort trotzdem wegen des
Tokenlimits abschneidet, kann das Limit angepasst werden:

```bash
export LMSTUDIO_MAX_TOKENS=2400
haiku --strict --provider lmstudio
```

### Ollama

Standardmodell im Projekt (Ollama verwendet **eigene** Modellnamen, nicht
zwingend dieselbe Zeichenkette wie LM Studio):

```text
gemma4:e4b
```

Ollama starten:

```bash
ollama serve
```

Prüfen, ob das Modell vorhanden ist:

```bash
ollama list
```

Falls es fehlt:

```bash
ollama pull gemma4:e4b
```

Dann:

```bash
haiku --check --provider ollama
```

Weitere Varianten:

```bash
haiku --check --provider ollama
haiku --fix
haiku --strict
haiku --model gemma4:e4b
```

### Claude

Wenn du Claude nutzen willst:

```bash
export ANTHROPIC_API_KEY=...
haiku --check --provider claude
```

Unter Windows PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="..."
haiku --check --provider claude
```

## Entwicklung

Tests:

```bash
pytest -q
```

Lint:

```bash
ruff check src tests
```

## Lizenz

Dieses Projekt steht unter der **MIT License**; siehe die Datei `LICENSE` im
Repository.

## Hinweise

- Das CLI ist derzeit auf **deutsche Haikus** ausgelegt.
- Die 5-7-5-Prüfung erfolgt lokal und deterministisch.
- Die traditionelle Haiku-Bewertung ist modellgestützt, aber das finale
  Scoring wird lokal im CLI berechnet.
- Die frühere deutsche 10-14-Silben-Regel ist bewusst entfernt; Standard bleibt
  strikt `5-7-5`.

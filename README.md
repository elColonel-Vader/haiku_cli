# Haiku CLI

Ein deutschsprachiges CLI zum Prüfen von Haikus auf 5-7-5 mit optionaler
KI-Analyse.

## Voraussetzungen

- Python `3.11` oder neuer
- `pip` oder `pipx`
- Optional für lokale KI-Checks (siehe Abschnitt **KI-Prüfung**):
  - **Ollama** (Standard bei `--provider auto`) oder **LM Studio** (OpenAI-kompatibler Local Server)
  - bei Ollama: laufender Dienst und ein passendes Modell (Projektstandard: `gemma4:e4b`)

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

### Pipe-Modus

macOS / Linux:

```bash
printf "Kirschblüten fallen\nleiser Regen über Moos\nFrühling atmet still\n" | haiku
```

Windows PowerShell:

```powershell
"Kirschblüten fallen`nleiser Regen über Moos`nFrühling atmet still" | haiku
```

## KI-Prüfung

Die KI-Funktionen sind optional. Das CLI funktioniert auch ohne lokale
Server oder Claude.

### Provider `auto` (Standard)

Ohne `--provider` nutzt das CLI **`auto`**: Es versucht zuerst **Ollama**, und
wenn dieser nicht erreichbar ist oder fehlschlägt, **LM Studio** (Local Server
auf `http://localhost:1234/v1`). So kannst du eine Installation nutzen, ohne
jedes Mal explizit wechseln.

```bash
haiku --check
```

Explizit:

```bash
haiku --check --provider auto
```

### Ollama

Standardmodell im Projekt:

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
haiku --check
```

Weitere Varianten:

```bash
haiku --check --provider ollama
haiku --fix
haiku --strict
haiku --model gemma4:e4b
```

### LM Studio

[LM Studio](https://lmstudio.ai/) stellt einen OpenAI-kompatiblen **Local Server**
bereit (Standard-URL: `http://localhost:1234/v1`). Im CLI:

1. LM Studio öffnen, ein Modell laden und den **Local Server** starten.
2. Haiku prüfen mit explizitem Provider oder über **`auto`**, wenn Ollama nicht läuft:

```bash
haiku --check --provider lmstudio
```

Optional: Basis-URL setzen (z. B. anderer Port), wenn der Server nicht auf
`localhost:1234` lauscht:

```bash
export LMSTUDIO_BASE_URL=http://127.0.0.1:1234
haiku --check --provider lmstudio
```

Mit `--model` kannst du einen konkreten Modellnamen erzwingen; sonst wird das
erste Modell aus der LM-Studio-API (`/v1/models`) verwendet.

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
- Die traditionelle Haiku-Bewertung (`Kigo`, `Kireji`, `Naturbild`,
`Gegenüberstellung` usw.) ist modellgestützt.


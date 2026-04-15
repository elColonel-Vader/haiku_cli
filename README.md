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

## Bewertungssystem

Die CLI trennt zwischen **Form**, **Haiku-Qualität** und **Gesamtwertung**.

- **Form**: `0` oder `2` Punkte, je nachdem ob die 5-7-5-Struktur erfüllt ist.
- **Haiku-Qualität**: bis zu `12` Punkte aus sieben Merkmalen.
- **Gesamtwertung**: aus `14` Rohpunkten auf `10` normalisiert.

### Qualitätsmerkmale

Die KI bewertet diese Felder nicht mehr nur binär, sondern in Stufen:

| Merkmal | Stufen | Max |
| --- | --- | --- |
| Kigo | `absent`, `weak`, `strong` | 2 |
| Kireji | `absent`, `weak`, `strong` | 1 |
| Naturbild | `absent`, `weak`, `strong` | 2 |
| Gegenwart | `absent`, `weak`, `strong` | 1 |
| Gegenüberstellung | `absent`, `weak`, `strong` | 2 |
| Bildkohärenz | `fragmented`, `loosely_connected`, `coherent` | 2 |
| Show vs. Tell | `telling`, `mixed`, `showing` | 2 |

### Formel

```text
raw_total = form + quality
normalized = round((raw_total / 14) * 10)
```

Optional kommt **Mono no aware** als Bonus dazu:

```text
if mono_no_aware == "present" and normalized < 10:
    overall = normalized + 1
else:
    overall = normalized
```

Wichtig: Eine **10/10** wird nur dann auf **9/10** reduziert, wenn gleichzeitig
noch `suggestions` vorhanden sind. Die Abstufung ist also **nicht pauschal**,
sondern signalisiert: formal und qualitativ sehr stark, aber noch nicht ganz
abschließend.

### Beispielausgabe

```text
Form: 2/2
✓ Silben (Programm): gültiges 5-7-5

Haiku-Qualität: 10.5/12
• Kigo: strong - April verankert die Szene klar im Frühling.
• Bildkohärenz: coherent - Alle Bilder greifen ineinander.

Gesamtwertung: 9/10
• Mono no aware: present - Vergänglichkeit schwingt still mit.
• Normalisiert: 9/10
• Mono no aware Bonus: +1
• Hinweis-Deckel: 10/10 wurde wegen offener Hinweise auf 9/10 reduziert.
```

## KI-Prüfung

Die KI-Funktionen sind optional. Das CLI funktioniert auch ohne lokale
Server oder Claude.

### Provider `auto` (Standard)

Ohne `--provider` nutzt das CLI **`auto`**: Es versucht zuerst **LM Studio**
(OpenAI-kompatible Base-URL, Standard im CLI: `http://127.0.0.1:1234/v1`; siehe
[LM Studio OpenAI-Compat](https://lmstudio.ai/docs/developer/openai-compat)),
und wenn dieser nicht erreichbar ist oder fehlschlägt, **Ollama**. So kannst du
zwischen den beiden wechseln, ohne jedes Mal explizit den Provider zu setzen.

```bash
haiku --check
```

Explizit:

```bash
haiku --check --provider auto
```

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

Oder über **`auto`** (siehe oben).

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
deiner LM-Studio-Liste per `--model "<id>"` setzen.

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
- Die traditionelle Haiku-Bewertung (`Kigo`, `Kireji`, `Naturbild`,
`Gegenüberstellung` usw.) ist modellgestützt.

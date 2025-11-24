# 🔍 Obsidian Spellcheck GUI (Dark Mode)

Eine Anwendung zur automatischen Rechtschreibkorrektur von Markdown- und Textdateien.  
Geeignet für Obsidian-Nutzer, Dokumentation, Notizen und technische Texte.

Das Tool bietet:

- Dark Mode GUI  
- automatische Rechtschreibkorrektur  
- Schutz von Markdown-Codeblöcken  
- Drag & Drop von Dateien  
- Diff-Ansicht (Vorher/Nachher)  
- editierbare Whitelist für bestimmte Begriffe  
- direkte Speicherung der korrigierten Datei  

---

## ✨ Funktionen

### ✔ Dark Mode GUI  
Modernes, dunkles Design – ideal für längere Sessions.

### ✔ Automatische Rechtschreibkorrektur  
- erkennt Deutsch oder Englisch automatisch  
- korrigiert Rechtschreibfehler  
- speichert die Datei direkt  
- Änderungen werden im GUI-Log angezeigt  

### ✔ Schutz für Codeblöcke  
Markdown-Codeblöcke wie:

\`\`\`bash  
\`\`\`yaml  
\`\`\`json  
\`\`\`

…werden **nicht verändert**.

### ✔ Drag & Drop  
Datei einfach in das Fenster ziehen → automatische Korrektur startet sofort.

### ✔ Diff-Ansicht  
Vergleicht Originaltext (links) mit korrigierter Version (rechts).

### ✔ Whitelist (benutzerdefiniert)  
Liste von Begriffen, die **niemals** korrigiert werden sollen.  
Perfekt für Fachbegriffe, Produktnamen, Abkürzungen oder technische Wörter.

- wird aus `whitelist.txt` geladen  
- kann im GUI bearbeitet werden  
- wird beim ersten Start automatisch erzeugt

> Hinweis:  
> Für öffentliche Repos empfiehlt es sich, `whitelist.txt` in `.gitignore` aufzunehmen.

---

## 🚀 Installation

### 1. Repository klonen

```bash
git clone <repo-url>
cd <repo>
````

### 2. Virtuelle Umgebung erstellen

```bash
python -m venv .venv
.\.venv\Scripts\activate      # Windows
source .venv/bin/activate     # macOS/Linux
```

### 3. Abhängigkeiten installieren

```bash
pip install language-tool-python langdetect tkinterdnd2
```

### 4. Java installieren (erforderlich für LanguageTool)

Download OpenJDK 17:
[https://adoptium.net/de/temurin/releases/?version=17](https://adoptium.net/de/temurin/releases/?version=17)

Prüfen:

```bash
java -version
```

---

## 🖥️ Anwendung starten

```bash
python spellcheck_gui.py
```

Bedienung:

* Datei per Button auswählen **oder** per Drag & Drop ablegen
* automatische Korrektur läuft sofort
* Änderungen erscheinen im Log
* Diff anzeigen → Vorher/Nachher vergleichen
* Whitelist bearbeiten → Wörter hinzufügen/löschen

---

## 📂 Projektstruktur

```
spellcheck_gui.py       # Hauptanwendung (GUI & Spellcheck)
whitelist.txt           # Liste der Wörter, die nicht korrigiert werden sollen
README.md
```

---

## 🧩 Whitelist bearbeiten

Datei `whitelist.txt` wird beim ersten Start automatisch angelegt.
Sie enthält Begriffe, die nicht korrigiert werden sollen.

Du kannst sie:

* manuell bearbeiten
* oder im GUI über **Whitelist bearbeiten** ändern

Beispiel:

```
exampleword
technischerbegriff
produktname
```

---

## 📄 Diff-Modus

Über den Button **„Diff anzeigen“**:

* linke Seite: Original
* rechte Seite: korrigierte Version

Damit lassen sich Änderungen einfach überprüfen.

---

## 🖱️ Drag & Drop

Unterstützt `.md` und `.txt` Dateien.

Ablage im Fenster → automatische Korrektur → Ergebnis anzeigen → speichern.

---

## 🤝 Mitwirken

Pull Requests und Verbesserungen sind willkommen.

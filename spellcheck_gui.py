import re
from pathlib import Path

import language_tool_python
from langdetect import detect
from tkinter import (
    Text, Scrollbar, Label, Button, Toplevel,
    RIGHT, Y, END
)
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

# ------------------------
# Dark Mode Colors
# ------------------------
BG = "#1e1e1e"
FG = "#ffffff"
ACCENT = "#3a3d41"

# ------------------------
# Globale Zustände für Diff
# ------------------------
last_original_text = ""
last_final_text = ""
last_file_path: Path | None = None

# ------------------------
# Whitelist aus Datei laden
# ------------------------
def load_whitelist() -> set[str]:
    wl_path = Path("whitelist.txt")
    if not wl_path.exists():
        # leere Datei erzeugen, damit der User sie leicht befüllen kann
        wl_path.write_text("", encoding="utf-8")
    words = wl_path.read_text(encoding="utf-8").splitlines()
    return {w.strip().lower() for w in words if w.strip()}

WHITELIST = load_whitelist()


# ------------------------
# Codeblöcke erkennen / schützen
# ------------------------
def remove_code_blocks(text: str):
    """
    Entfernt Codeblöcke (```...```) aus dem Text
    und ersetzt sie durch Platzhalter, damit sie
    nicht von LanguageTool korrigiert werden.
    """
    blocks = re.findall(r"```.*?```", text, flags=re.DOTALL)
    placeholders: list[tuple[str, str]] = []

    cleaned_text = text
    for i, block in enumerate(blocks):
        placeholder = f"__CODEBLOCK_{i}__"
        placeholders.append((placeholder, block))
        cleaned_text = cleaned_text.replace(block, placeholder, 1)

    return cleaned_text, placeholders


def restore_code_blocks(text: str, placeholders: list[tuple[str, str]]) -> str:
    """
    Setzt zuvor entfernte Codeblöcke wieder
    an ihre Platzhalter-Stellen ein.
    """
    restored = text
    for placeholder, block in placeholders:
        restored = restored.replace(placeholder, block, 1)
    return restored


# ------------------------
# Sprache erkennen
# ------------------------
def detect_language(text: str) -> str:
    lang = detect(text)
    if lang.startswith("de"):
        return "de-DE"
    return "en-US"


# ------------------------
# Fehlerlänge bestimmen
# ------------------------
def get_error_length(match) -> int:
    if hasattr(match, "error_length"):
        return match.error_length
    if hasattr(match, "errorLength"):
        return match.errorLength
    return len(match.context)


# ------------------------
# Hauptlogik für eine Datei
# ------------------------
def process_path(path: Path):
    global last_original_text, last_final_text, last_file_path, WHITELIST

    if not path.is_file():
        messagebox.showerror("Fehler", f"Pfad ist keine Datei:\n{path}")
        return

    original_text = path.read_text(encoding="utf-8")

    # Codeblöcke entfernen, sodass sie nicht korrigiert werden
    text_without_code, placeholders = remove_code_blocks(original_text)

    # Sprache erkennen
    lang = detect_language(text_without_code or original_text)
    tool = language_tool_python.LanguageTool(lang)

    matches = tool.check(text_without_code)
    corrected = text_without_code

    text_output.delete(1.0, END)
    text_output.insert(END, f"Datei: {path}\n", "bold")
    text_output.insert(END, f"Sprache erkannt: {lang}\n\n")
    text_output.insert(END, "Automatische Korrekturen (Whitelist + Codeblöcke geschützt):\n\n")

    # von hinten nach vorne iterieren, damit Offsets stabil bleiben
    for match in sorted(matches, key=lambda m: m.offset, reverse=True):
        if not match.replacements:
            continue

        start = match.offset
        end = start + get_error_length(match)
        original_word = corrected[start:end]

        # Whitelist: technische Begriffe nie ändern
        if original_word.lower() in WHITELIST:
            text_output.insert(END, f"⏭ Ignoriert (Whitelist): {original_word}\n")
            continue

        replacement = match.replacements[0]
        corrected = corrected[:start] + replacement + corrected[end:]

        text_output.insert(END, f"✔ {original_word} → {replacement}\n")

    # Codeblöcke wieder an ihren Platz
    final_text = restore_code_blocks(corrected, placeholders)

    # Datei überschreiben
    path.write_text(final_text, encoding="utf-8")

    # Zustände für Diff merken
    last_original_text = original_text
    last_final_text = final_text
    last_file_path = path

    messagebox.showinfo("Fertig!", "Die Datei wurde korrigiert und gespeichert.")


# ------------------------
# Datei-Auswahl (Button)
# ------------------------
def process_file_dialog():
    filepath = filedialog.askopenfilename(
        filetypes=[("Markdown Dateien", "*.md"), ("Text Dateien", "*.txt")]
    )
    if not filepath:
        return
    process_path(Path(filepath))


# ------------------------
# Drag & Drop Handler
# ------------------------
def on_drop(event):
    data = event.data
    # können in geschweiften Klammern kommen, wenn Leerzeichen im Pfad sind
    if data.startswith("{") and data.endswith("}"):
        data = data[1:-1]
    dropped_path = Path(data)
    process_path(dropped_path)


# ------------------------
# Diff-Fenster anzeigen
# ------------------------
def show_diff():
    if not last_file_path:
        messagebox.showinfo("Info", "Noch keine Datei verarbeitet – kein Diff vorhanden.")
        return

    popup = Toplevel(root)
    popup.title(f"Diff – {last_file_path.name}")
    popup.configure(bg=BG)
    popup.geometry("1000x600")

    lbl_left = Label(popup, text="Vorher", bg=BG, fg=FG, font=("Arial", 12, "bold"))
    lbl_left.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    lbl_right = Label(popup, text="Nachher", bg=BG, fg=FG, font=("Arial", 12, "bold"))
    lbl_right.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    # linker Text
    left_scroll = Scrollbar(popup)
    left_scroll.grid(row=2, column=0, sticky="nse", padx=(0, 0))

    left_text = Text(
        popup,
        bg="#181818",
        fg=FG,
        insertbackground=FG,
        font=("Consolas", 10),
        yscrollcommand=left_scroll.set,
        wrap="word",
        height=30,
        width=60,
    )
    left_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
    left_scroll.config(command=left_text.yview)

    # rechter Text
    right_scroll = Scrollbar(popup)
    right_scroll.grid(row=2, column=1, sticky="nse", padx=(0, 0))

    right_text = Text(
        popup,
        bg="#181818",
        fg=FG,
        insertbackground=FG,
        font=("Consolas", 10),
        yscrollcommand=right_scroll.set,
        wrap="word",
        height=30,
        width=60,
    )
    right_text.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
    right_scroll.config(command=right_text.yview)

    # Inhalt einfügen
    left_text.insert(END, last_original_text)
    right_text.insert(END, last_final_text)

    # Grid-Konfiguration für saubere Skalierung
    popup.grid_rowconfigure(1, weight=1)
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_columnconfigure(1, weight=1)


# ------------------------
# Whitelist im GUI bearbeiten
# ------------------------
def edit_whitelist():
    global WHITELIST

    popup = Toplevel(root)
    popup.title("Whitelist bearbeiten")
    popup.configure(bg=BG)
    popup.geometry("400x500")

    Label(
        popup,
        text="Ein Begriff pro Zeile.\n(technische Wörter, die nie korrigiert werden)",
        bg=BG,
        fg=FG,
        font=("Arial", 10),
    ).pack(pady=5)

    scroll = Scrollbar(popup)
    scroll.pack(side=RIGHT, fill=Y)

    wl_text = Text(
        popup,
        bg="#181818",
        fg=FG,
        insertbackground=FG,
        font=("Consolas", 10),
        yscrollcommand=scroll.set,
    )
    wl_text.pack(padx=10, pady=10, fill="both", expand=True)
    scroll.config(command=wl_text.yview)

    # aktuelle Whitelist ins Textfeld schreiben
    wl_content = "\n".join(sorted(WHITELIST))
    wl_text.insert(END, wl_content)

    def save_wl():
        global WHITELIST
        content = wl_text.get("1.0", END)
        lines = content.splitlines()
        cleaned = {ln.strip().lower() for ln in lines if ln.strip()}
        wl_path = Path("whitelist.txt")
        wl_path.write_text("\n".join(sorted(cleaned)), encoding="utf-8")
        WHITELIST = load_whitelist()
        messagebox.showinfo("Gespeichert", "Whitelist aktualisiert.")
        popup.destroy()

    Button(
        popup,
        text="Speichern",
        command=save_wl,
        bg=ACCENT,
        fg=FG,
        font=("Arial", 11),
        activebackground="#505357",
    ).pack(pady=10)


# ------------------------
# GUI Setup
# ------------------------
root = TkinterDnD.Tk()
root.title("Obsidian Spellcheck – Dark Mode")
root.geometry("900x650")
root.configure(bg=BG)

header = Label(
    root,
    text="Obsidian Spellcheck\n(Datei auswählen oder hierher ziehen)",
    bg=BG,
    fg=FG,
    font=("Arial", 14),
)
header.pack(pady=10)

btn_frame = Text(root, height=1, width=1, bg=BG, borderwidth=0, highlightthickness=0)
btn_frame.pack()

btn_select = Button(
    root,
    text="Datei auswählen",
    command=process_file_dialog,
    bg=ACCENT,
    fg=FG,
    font=("Arial", 12),
    activebackground="#505357",
    width=18,
)
btn_select.pack(pady=5)

btn_diff = Button(
    root,
    text="Diff anzeigen",
    command=show_diff,
    bg=ACCENT,
    fg=FG,
    font=("Arial", 12),
    activebackground="#505357",
    width=18,
)
btn_diff.pack(pady=5)

btn_wl = Button(
    root,
    text="Whitelist bearbeiten",
    command=edit_whitelist,
    bg=ACCENT,
    fg=FG,
    font=("Arial", 12),
    activebackground="#505357",
    width=18,
)
btn_wl.pack(pady=5)

# Scroll + Log-Output
scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

text_output = Text(
    root,
    bg="#181818",
    fg=FG,
    insertbackground=FG,
    font=("Consolas", 10),
    height=25,
    width=100,
    yscrollcommand=scrollbar.set,
)
text_output.pack(padx=10, pady=10, fill="both", expand=True)
scrollbar.config(command=text_output.yview)

text_output.tag_configure("bold", font=("Consolas", 10, "bold"))

# Drag & Drop aktivieren
root.drop_target_register(DND_FILES)
root.dnd_bind("<<Drop>>", on_drop)

root.mainloop()

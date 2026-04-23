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
# Global state for Diff
# ------------------------
last_original_text = ""
last_final_text = ""
last_file_path = None

# ------------------------
# Whitelist handling
# ------------------------
def load_whitelist():
    wl = Path("whitelist.txt")
    if not wl.exists():
        wl.write_text("", encoding="utf-8")
    return {w.strip().lower() for w in wl.read_text(encoding="utf-8").splitlines() if w.strip()}

WHITELIST = load_whitelist()

# ------------------------
# Code block protection
# ------------------------
def remove_code_blocks(text):
    blocks = re.findall(r"```.*?```", text, flags=re.DOTALL)
    placeholders = []
    cleaned = text

    for i, block in enumerate(blocks):
        placeholder = f"__CODEBLOCK_{i}__"
        placeholders.append((placeholder, block))
        cleaned = cleaned.replace(block, placeholder, 1)

    return cleaned, placeholders

def restore_code_blocks(text, placeholders):
    for placeholder, block in placeholders:
        text = text.replace(placeholder, block, 1)
    return text

# ------------------------
# Language detection
# ------------------------
def detect_language(text):
    lang = detect(text)
    return "de-DE" if lang.startswith("de") else "en-US"

# ------------------------
# Error length helper
# ------------------------
def get_error_length(match):
    if hasattr(match, "error_length"):
        return match.error_length
    if hasattr(match, "errorLength"):
        return match.errorLength
    return len(match.context)

# ------------------------
# Main processing
# ------------------------
def process_path(path: Path):
    global last_original_text, last_final_text, last_file_path, WHITELIST

    if not path.is_file():
        messagebox.showerror("Error", f"Not a file:\n{path}")
        return

    original = path.read_text(encoding="utf-8")
    text, placeholders = remove_code_blocks(original)

    tool = language_tool_python.LanguageTool(detect_language(text))
    matches = tool.check(text)
    corrected = text

    log.delete(1.0, END)
    log.insert(END, f"File: {path}\n\n", "bold")

    for m in sorted(matches, key=lambda x: x.offset, reverse=True):
        if not m.replacements:
            continue

        start = m.offset
        end = start + get_error_length(m)
        word = corrected[start:end]

        if word.lower() in WHITELIST:
            log.insert(END, f"⏭ Ignored (whitelist): {word}\n")
            continue

        replacement = m.replacements[0]
        corrected = corrected[:start] + replacement + corrected[end:]
        log.insert(END, f"✔ {word} → {replacement}\n")

    final = restore_code_blocks(corrected, placeholders)
    path.write_text(final, encoding="utf-8")

    last_original_text = original
    last_final_text = final
    last_file_path = path

    messagebox.showinfo("Done", "File corrected and saved.")

# ------------------------
# File selection
# ------------------------
def open_file():
    f = filedialog.askopenfilename(filetypes=[("Markdown/Text", "*.md *.txt")])
    if f:
        process_path(Path(f))

# ------------------------
# Drag & Drop
# ------------------------
def on_drop(event):
    p = event.data.strip("{}")
    process_path(Path(p))

# ------------------------
# Diff window
# ------------------------
def show_diff():
    if not last_file_path:
        return

    win = Toplevel(root)
    win.title(f"Diff – {last_file_path.name}")
    win.configure(bg=BG)
    win.geometry("1000x600")

    left = Text(win, bg="#181818", fg=FG, font=("Consolas", 10))
    right = Text(win, bg="#181818", fg=FG, font=("Consolas", 10))

    left.pack(side="left", fill="both", expand=True)
    right.pack(side="right", fill="both", expand=True)

    left.insert(END, last_original_text)
    right.insert(END, last_final_text)

# ------------------------
# Whitelist editor
# ------------------------
def edit_whitelist():
    win = Toplevel(root)
    win.title("Edit Whitelist")
    win.configure(bg=BG)
    win.geometry("400x500")

    txt = Text(win, bg="#181818", fg=FG, font=("Consolas", 10))
    txt.pack(fill="both", expand=True, padx=10, pady=10)

    txt.insert(END, "\n".join(sorted(WHITELIST)))

    def save():
        wl = {w.strip().lower() for w in txt.get("1.0", END).splitlines() if w.strip()}
        Path("whitelist.txt").write_text("\n".join(sorted(wl)), encoding="utf-8")
        global WHITELIST
        WHITELIST = wl
        win.destroy()

    Button(win, text="Save", command=save, bg=ACCENT, fg=FG).pack(pady=5)

# ------------------------
# GUI
# ------------------------
root = TkinterDnD.Tk()
root.title("Obsidian Spellcheck")
root.geometry("900x650")
root.configure(bg=BG)

Label(root, text="Drag & drop a file or choose one", bg=BG, fg=FG, font=("Arial", 14)).pack(pady=10)

Button(root, text="Open file", command=open_file, bg=ACCENT, fg=FG).pack()
Button(root, text="Show diff", command=show_diff, bg=ACCENT, fg=FG).pack(pady=5)
Button(root, text="Edit whitelist", command=edit_whitelist, bg=ACCENT, fg=FG).pack(pady=5)

scroll = Scrollbar(root)
scroll.pack(side=RIGHT, fill=Y)

log = Text(root, bg="#181818", fg=FG, font=("Consolas", 10), yscrollcommand=scroll.set)
log.pack(fill="both", expand=True, padx=10, pady=10)
scroll.config(command=log.yview)

log.tag_configure("bold", font=("Consolas", 10, "bold"))

root.drop_target_register(DND_FILES)
root.dnd_bind("<<Drop>>", on_drop)

root.mainloop()

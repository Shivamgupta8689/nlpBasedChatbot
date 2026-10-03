import json
import os
import re
from difflib import get_close_matches
from tkinter import Tk, Frame, Entry, Button, Text, Scrollbar, messagebox

# Phrases such as "what is ..." / "tell me about ..." are removed from the query
FILLER = re.compile(
    r"^(what is|what are|what's|define|definition of|tell me about|explain|meaning of)"
    r"\s+(an?\s+|the\s+)?",
    re.I,
)


class Chatbot:

    def __init__(self, window):
        window.title('Iris: NLP-Based Environmental Glossary Chatbot')
        window.geometry('900x650')          # <-- window size (width x height)
        window.minsize(600, 450)            # smallest size allowed
        window.configure(bg="#2b2b2b")

        # NOTE: Tk's pack() gives space in the order widgets are packed.
        # The bottom input bar is packed FIRST so it always keeps its space,
        # then the chat area takes whatever is left.

        # ---------- Input area (stays at the bottom) ----------
        input_frame = Frame(window, bg="#2b2b2b")
        input_frame.pack(side="bottom", fill="x", padx=15, pady=(5, 15))

        self.send_button = Button(
            input_frame, text="Send", fg="white", bg="blue", activebackground="#1a1aa6",
            activeforeground="white", width=10, font=("Times", 15), relief="flat",
            command=self.reply_to_you)
        self.send_button.pack(side="right", padx=(10, 0), ipady=4)

        self.Message_Entry = Entry(input_frame, font=("Times", 16))
        self.Message_Entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.Message_Entry.bind("<Return>", self.reply_to_you)
        self.Message_Entry.focus()

        # ---------- Chat area (expands with the window) ----------
        chat_frame = Frame(window, bg="#2b2b2b")
        chat_frame.pack(side="top", fill="both", expand=True, padx=15, pady=(15, 5))

        # width/height=1 -> tiny *requested* size; the real size comes from pack(expand)
        self.message_session = Text(
            chat_frame, bd=3, relief="flat", font=("Times", 15), undo=True,
            wrap="word", bg="#596", fg="white", state="disabled",
            width=1, height=1, padx=10, pady=10, spacing3=4)
        self.message_session.tag_config("user", foreground="#ffeb99")
        self.message_session.tag_config("iris", foreground="white")

        self.overscroll = Scrollbar(chat_frame, command=self.message_session.yview, width=20)
        self.message_session["yscrollcommand"] = self.overscroll.set

        self.overscroll.pack(side="right", fill="y")
        self.message_session.pack(side="left", fill="both", expand=True)

        self.load_brain()

    def load_brain(self):
        """Load knowledge.json and normalise keys/definitions once."""
        try:
            # Look for knowledge.json next to this script, not in the current folder
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge.json")
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Could not load knowledge.json:\n{e}")
            raise SystemExit

        self.Brain = {}
        for key, defs in raw.items():
            clean = [d.replace("\\n", " ").strip() for d in defs]
            self.Brain.setdefault(key.lower().strip(), []).extend(clean)
        self.keys = list(self.Brain)

    def add_chat(self, message, tag=None):
        self.message_session.config(state="normal")
        self.message_session.insert("end", message, tag)
        self.message_session.see("end")
        self.message_session.config(state="disabled")

    def find_answer(self, text):
        """Preprocess query, try exact match, then fuzzy match."""
        text = FILLER.sub("", text).rstrip("?!. ")
        if text in self.Brain:                         # exact match first
            return self.Brain[text]
        match = get_close_matches(text, self.keys, n=1, cutoff=0.75)
        return self.Brain[match[0]] if match else None

    def reply_to_you(self, event=None):
        original = self.Message_Entry.get().strip()
        if not original:
            return
        self.Message_Entry.delete(0, "end")
        self.add_chat(f"You: {original}\n", "user")

        defs = self.find_answer(original.lower())
        if defs:
            if len(defs) > 1:
                body = "\n".join(f"  {i}. {d}" for i, d in enumerate(defs, 1))
                self.add_chat(f"Iris:\n{body}\n\n", "iris")
            else:
                self.add_chat(f"Iris: {defs[0]}\n\n", "iris")
        else:
            self.add_chat("Iris: I can't find that in my knowledge base.\n\n", "iris")


if __name__ == "__main__":
    root = Tk()
    Chatbot(root)
    root.mainloop()

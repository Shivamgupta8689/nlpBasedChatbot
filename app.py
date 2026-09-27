import json
from difflib import get_close_matches
from tkinter import Tk, Entry, Button, Text, Scrollbar


class Chatbot:

    def __init__(self, window):

        window.title('Iris Assistant')
        window.geometry('405x400')
        window.resizable(0, 0)

        # Chat display
        self.message_session = Text(
            window,
            bd=3,
            relief="flat",
            font=("Times", 10),
            undo=True,
            wrap="word",
            width=45,
            height=15,
            bg="#596",
            fg="white",
            state="disabled"
        )

        # Scrollbar
        self.overscroll = Scrollbar(
            window,
            command=self.message_session.yview
        )

        self.overscroll.config(width=20)

        self.message_session["yscrollcommand"] = self.overscroll.set

        # Send button
        self.send_button = Button(
            window,
            text="Send",
            fg="white",
            bg="blue",
            width=9,
            font=("Times", 12),
            relief="flat",
            command=self.reply_to_you
        )

        # Message input
        self.Message_Entry = Entry(
            window,
            width=40,
            font=("Times", 12)
        )

        self.Message_Entry.bind(
            "<Return>",
            self.reply_to_you
        )

        # Position widgets
        self.message_session.place(
            x=20,
            y=20
        )

        self.overscroll.place(
            x=370,
            y=50
        )

        self.send_button.place(
            x=0,
            y=360
        )

        self.Message_Entry.place(
            x=135,
            y=365
        )

        # Load knowledge base
        with open("knowledge.json", "r", encoding="utf-8") as file:
            self.Brain = json.load(file)

    def add_chat(self, message):

        self.message_session.config(state="normal")

        self.message_session.insert(
            "end",
            message
        )

        self.message_session.see("end")

        self.message_session.config(state="disabled")

    def reply_to_you(self, event=None):

        # Get user's actual message
        user_message = self.Message_Entry.get().lower().strip()

        # Don't process empty messages
        if not user_message:
            return

        # Display user's message
        display_message = "You: " + user_message + "\n"

        # Find closest match in knowledge base
        close_match = get_close_matches(
            user_message,
            self.Brain.keys(),
            n=1,
            cutoff=0.6
        )

        # Generate reply
        if close_match:

            matched_key = close_match[0]

            reply = (
                "Iris: "
                + self.Brain[matched_key][0]
                + "\n"
            )

        else:

            reply = (
                "Iris: "
                "I can't find that in my knowledge base.\n"
            )

        # Display conversation
        self.add_chat(display_message)
        self.add_chat(reply)


# Start application
root = Tk()

Chatbot(root)

root.mainloop()
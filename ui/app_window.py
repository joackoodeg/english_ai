import tkinter as tk
from tkinter import scrolledtext
from config import *
from core.chat_manager import handle_user_input

def start_app():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry(WINDOW_SIZE)
    root.configure(bg=BG_COLOR)

    FONT = (FONT_FAMILY, FONT_SIZE)

    chat_area = scrolledtext.ScrolledText(
        root, wrap=tk.WORD, font=FONT,
        bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
        relief="sunken", bd=2
    )
    chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    chat_area.config(state=tk.DISABLED)

    # Estilo para correcciones
    chat_area.tag_config("system", foreground="#FFD700")

    entry_frame = tk.Frame(root, bg=BG_COLOR)
    entry_frame.pack(padx=10, pady=5, fill=tk.X)

    user_input = tk.Entry(entry_frame, font=FONT, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="groove", bd=2)
    user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    def on_send():
        message = user_input.get().strip()
        if message:
            handle_user_input(message, chat_area)
            user_input.delete(0, tk.END)

    send_button = tk.Button(entry_frame, text="Send", command=on_send, font=FONT, bg=BUTTON_BG, fg=TEXT_COLOR, relief="raised", bd=2)
    send_button.pack(side=tk.RIGHT)

    root.mainloop()


import tkinter as tk
from tkinter import scrolledtext, font
from config import *
from core.chat_manager import handle_user_input

def start_app():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry(WINDOW_SIZE)
    root.configure(bg=BG_COLOR)
    
    # Make window responsive
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Create main container frame
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    main_frame.grid_rowconfigure(1, weight=1)  # Chat area gets the weight
    main_frame.grid_columnconfigure(0, weight=1)
    
    # Add a compact header
    header_frame = tk.Frame(main_frame, bg=BG_COLOR, height=25)
    header_frame.grid(row=0, column=0, sticky="ew")
    header_frame.grid_columnconfigure(0, weight=1)  # Push status to right
    
    # Title as a small label on the left
    title_label = tk.Label(
        header_frame,
        text=APP_TITLE,
        font=(FONT_FAMILY, 10, "bold"),
        fg=SYSTEM_COLOR,
        bg=BG_COLOR,
        anchor="w",
    )
    title_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
    
    # Status indicator on the right
    status_frame = tk.Frame(header_frame, bg=BG_COLOR)
    status_frame.grid(row=0, column=1, sticky="e")
    
    status_indicator = tk.Canvas(status_frame, width=10, height=10, bg=BG_COLOR, highlightthickness=0)
    status_indicator.create_oval(2, 2, 8, 8, fill="#00FF00")
    status_indicator.pack(side=tk.LEFT, padx=2)
    
    status_label = tk.Label(
        status_frame,
        text="ONLINE",
        font=(FONT_FAMILY, 8),
        fg="#00FF00",
        bg=BG_COLOR
    )
    status_label.pack(side=tk.LEFT, padx=2)
    
    # Thin separator
    separator = tk.Frame(main_frame, height=1, bg="#444444")
    separator.grid(row=0, column=0, sticky="ews", pady=(25, 0))
    
    # Chat display area with border
    chat_container = tk.Frame(
        main_frame, 
        bg=BG_COLOR,
        highlightbackground="#444444",
        highlightthickness=1
    )
    chat_container.grid(row=1, column=0, sticky="nsew", pady=5)
    chat_container.grid_rowconfigure(0, weight=1)
    chat_container.grid_columnconfigure(0, weight=1)
    
    chat_area = scrolledtext.ScrolledText(
        chat_container, 
        wrap=tk.WORD, 
        font=(FONT_FAMILY, FONT_SIZE),
        bg=ENTRY_BG, 
        fg=TEXT_COLOR, 
        insertbackground=TEXT_COLOR,
        relief="flat", 
        bd=0,
        padx=10,
        pady=10
    )
    chat_area.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    chat_area.config(state=tk.DISABLED)
    
    # Style text tags
    chat_area.tag_config("user", foreground=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE, "bold"))
    chat_area.tag_config("system", foreground=SYSTEM_COLOR)
    chat_area.tag_config("ai", foreground=HIGHLIGHT_COLOR)
    chat_area.tag_config("correction", foreground="#FFD700")  # Gold for corrections
    
    # Full-width input area at bottom
    input_frame = tk.Frame(main_frame, bg=BG_COLOR)
    input_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
    input_frame.grid_columnconfigure(1, weight=1)  # Entry gets all extra space
    
    # Compact prompt symbol
    prompt_label = tk.Label(
        input_frame,
        text=">",
        font=(FONT_FAMILY, FONT_SIZE, "bold"),
        fg=TEXT_COLOR,
        bg=BG_COLOR,
        width=1
    )
    prompt_label.grid(row=0, column=0, sticky="w")
    
    # Full-width input field
    user_input = tk.Entry(
        input_frame, 
        font=(FONT_FAMILY, FONT_SIZE), 
        bg=ENTRY_BG, 
        fg=TEXT_COLOR, 
        insertbackground=TEXT_COLOR, 
        relief="flat", 
        highlightbackground="#444444",
        highlightthickness=1,
        insertwidth=2
    )
    user_input.grid(row=0, column=1, sticky="ew", padx=(2, 5))
    
    # Function to handle sending messages
    def send_message():
        message = user_input.get().strip()
        if message:
            handle_user_input(message, chat_area)
            user_input.delete(0, tk.END)
    
    # Compact send button
    send_button = tk.Button(
        input_frame, 
        text="SEND", 
        command=send_message, 
        font=(FONT_FAMILY, 10, "bold"), 
        bg=BUTTON_BG, 
        fg=TEXT_COLOR, 
        activebackground="#333333",
        activeforeground=TEXT_COLOR,
        relief="raised", 
        bd=1,
        padx=5,
        pady=1,
        width=6
    )
    send_button.grid(row=0, column=2, padx=(0, 0))
    
    # Bind Enter key to send message
    user_input.bind("<Return>", lambda event: send_message())
    
    # Set focus to input field
    user_input.focus_set()
    
    # Add startup text
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"{APP_TITLE} - Ready\n\n", "system")
    chat_area.config(state=tk.DISABLED)
    
    root.mainloop()
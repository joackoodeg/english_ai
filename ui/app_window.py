import tkinter as tk
from tkinter import scrolledtext, font
from config import *
from core.chat_manager import handle_user_input, suggest_topic, reset_conversation
# Importar ctypes para la personalización de Windows
from ctypes import windll, byref, sizeof, c_int

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
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    main_frame.grid_rowconfigure(1, weight=1)  # Chat area gets the weight
    main_frame.grid_columnconfigure(0, weight=1)
    
    # Add a stylized header
    header_frame = tk.Frame(main_frame, bg=BG_COLOR, height=30)
    header_frame.grid(row=0, column=0, sticky="ew")
    header_frame.grid_columnconfigure(0, weight=1)  # Push status to right
    
    # Title with ASCII styling
    title_text = f"┌─── {APP_TITLE} ───┐"
    title_label = tk.Label(
        header_frame,
        text=title_text,
        font=(FONT_FAMILY, 12, "bold"),
        fg=SYSTEM_COLOR,
        bg=BG_COLOR,
        anchor="w",
    )
    title_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
    # Status indicator on the right with enhanced styling
    status_frame = tk.Frame(header_frame, bg=BG_COLOR)
    status_frame.grid(row=0, column=1, sticky="e")
    
    # ASCII-style status
    status_text = "[ ONLINE ]"
    status_label = tk.Label(
        status_frame,
        text=status_text,
        font=(FONT_FAMILY, 10, "bold"),
        fg="#00FF00",
        bg=BG_COLOR
    )
    status_label.pack(side=tk.RIGHT, padx=5)
    
    # ASCII-style separator
    separator_text = "═" * 80  # Unicode box drawing character
    separator = tk.Label(
        main_frame,
        text=separator_text,
        font=(FONT_FAMILY, 8),
        fg="#444444",
        bg=BG_COLOR
    )
    separator.grid(row=0, column=0, sticky="ews", pady=(30, 0))
    
    # Chat display area with stylized border
    chat_container = tk.Frame(
        main_frame, 
        bg=BG_COLOR,
        highlightbackground="#444444",
        highlightthickness=1,
        bd=0
    )
    chat_container.grid(row=1, column=0, sticky="nsew", pady=10)
    chat_container.grid_rowconfigure(0, weight=1)
    chat_container.grid_columnconfigure(0, weight=1)
    
    # Custom scrollbar styling
    scrollbar_style = {
        "troughcolor": ENTRY_BG,
        "background": BUTTON_BG,
        "activebackground": TEXT_COLOR
    }
    
    chat_area = scrolledtext.ScrolledText(
        chat_container, 
        wrap=tk.WORD, 
        font=(FONT_FAMILY, FONT_SIZE),
        bg=ENTRY_BG, 
        fg=TEXT_COLOR, 
        insertbackground=TEXT_COLOR,
        relief="flat", 
        bd=0,
        padx=15,
        pady=15
    )
    chat_area.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    chat_area.config(state=tk.DISABLED)
    
    # Apply scrollbar styling
    chat_area.vbar.config(**scrollbar_style)
    
    # Style text tags with improved colors
    chat_area.tag_config("user", foreground=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE, "bold"))
    chat_area.tag_config("system", foreground=SYSTEM_COLOR)
    chat_area.tag_config("ai", foreground=HIGHLIGHT_COLOR)
    chat_area.tag_config("correction", foreground="#FFD700")  # Gold for corrections
    chat_area.tag_config("separator", foreground="#444444")  # For separators
    chat_area.tag_config("waiting", foreground="#FF6600")    # Orange for waiting messages
    
    # Control buttons frame
    control_frame = tk.Frame(main_frame, bg=BG_COLOR)
    control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
    
    # Helper Buttons
    suggest_button = tk.Button(
        control_frame, 
        text="[ SUGGEST TOPIC ]", 
        command=lambda: suggest_topic(chat_area), 
        font=(FONT_FAMILY, 8, "bold"), 
        bg=BUTTON_BG, 
        fg=TEXT_COLOR, 
        activebackground="#333333",
        activeforeground=TEXT_COLOR,
        relief="flat", 
        bd=1,
        padx=5,
        pady=1
    )
    suggest_button.pack(side=tk.LEFT, padx=(0, 5))
    
    reset_button = tk.Button(
        control_frame, 
        text="[ RESET CHAT ]", 
        command=lambda: reset_conversation(chat_area), 
        font=(FONT_FAMILY, 8, "bold"), 
        bg=BUTTON_BG, 
        fg=TEXT_COLOR, 
        activebackground="#333333",
        activeforeground=TEXT_COLOR,
        relief="flat", 
        bd=1,
        padx=5,
        pady=1
    )
    reset_button.pack(side=tk.LEFT)
    
    # Status indicator for processing
    processing_label = tk.Label(
        control_frame,
        text="",
        font=(FONT_FAMILY, 8, "bold"),
        fg="#FF6600",  # Orange for processing
        bg=BG_COLOR
    )
    processing_label.pack(side=tk.RIGHT, padx=5)
    
    # Input area with ASCII styling
    input_frame = tk.Frame(main_frame, bg=BG_COLOR)
    input_frame.grid(row=3, column=0, sticky="ew", pady=(5, 0))
    input_frame.grid_columnconfigure(1, weight=1)  # Entry gets all extra space
    
    # Stylized prompt symbol
    prompt_label = tk.Label(
        input_frame,
        text="[ > ]",
        font=(FONT_FAMILY, FONT_SIZE, "bold"),
        fg=SYSTEM_COLOR,
        bg=BG_COLOR,
        width=4
    )
    prompt_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
    
    # Full-width input field with better styling
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
    user_input.grid(row=0, column=1, sticky="ew", padx=(0, 5))
    
    # Function to handle sending messages with UI feedback
    def send_message():
        message = user_input.get().strip()
        if message:
            # Clear the input field immediately
            user_input.delete(0, tk.END)
            
            # Disable input and buttons while processing
            user_input.config(state=tk.DISABLED)
            send_button.config(state=tk.DISABLED)
            processing_label.config(text="[ PROCESSING... ]")
            
            # Reset UI after handling the input
            def reset_ui():
                user_input.config(state=tk.NORMAL)
                send_button.config(state=tk.NORMAL)
                processing_label.config(text="")
                user_input.focus_set()
            
            # Process the message
            handle_user_input(message, chat_area)
            
            # Schedule UI reset to happen after message is handled
            root.after(100, reset_ui)
    
    # Improved send button with ASCII styling
    send_button = tk.Button(
        input_frame, 
        text="[ SEND ]", 
        command=send_message, 
        font=(FONT_FAMILY, 10, "bold"), 
        bg=BUTTON_BG, 
        fg=TEXT_COLOR, 
        activebackground="#333333",
        activeforeground=TEXT_COLOR,
        relief="flat", 
        bd=1,
        padx=8,
        pady=2,
        width=8
    )
    send_button.grid(row=0, column=2, padx=(0, 0))
    
    # Bind Enter key to send message
    user_input.bind("<Return>", lambda event: send_message())
    
    # Set focus to input field
    user_input.focus_set()
    
    # Add improved startup text with simple ASCII banner
    chat_area.config(state=tk.NORMAL)
    
    # Simplified ASCII banner
    banner = """
    ===============================================
                ENGLISH AI TERMINAL                
    ===============================================
    """
    
    chat_area.insert(tk.END, banner + "\n", "system")
    chat_area.insert(tk.END, "System initialized and ready for interaction.\n", "system")
    chat_area.insert(tk.END, "Type your English text below to check grammar and practice conversation.\n", "system")
    chat_area.insert(tk.END, "Use the [SUGGEST TOPIC] button if you need conversation ideas.\n\n", "system")
    
    # Add an initial topic suggestion
    suggest_topic(chat_area)
    
    chat_area.config(state=tk.DISABLED)
    
    # Enable dark mode title bar on Windows if possible
    try:
        from ctypes import windll
        windll.dwmapi.DwmSetWindowAttribute(
            root.winfo_id(), 
            20,  # DWMWA_USE_IMMERSIVE_DARK_MODE
            byref(c_int(1)), 
            sizeof(c_int)
        )
    except:
        pass  # Silently fail if not on Windows or if the call fails
    
    root.mainloop()
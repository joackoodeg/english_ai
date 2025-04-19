import tkinter as tk
from tkinter import scrolledtext, font, ttk, Menu
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
    
    # Add learning mode selector
    mode_frame = tk.Frame(header_frame, bg=BG_COLOR)
    mode_frame.grid(row=0, column=1, sticky="e")
    
    mode_label = tk.Label(
        mode_frame,
        text="Learning Focus:",
        font=(FONT_FAMILY, 9),
        fg=TEXT_COLOR,
        bg=BG_COLOR
    )
    mode_label.pack(side=tk.LEFT, padx=5)
    
    # Learning mode combobox
    mode_var = tk.StringVar(value="General")
    modes = ["General", "Verb Tenses", "Vocabulary", "Expressions", "Pronunciation"]
    mode_selector = ttk.Combobox(
        mode_frame, 
        textvariable=mode_var,
        values=modes,
        width=12,
        state="readonly"
    )
    mode_selector.pack(side=tk.LEFT, padx=5)
    
    # Status indicator on the right with enhanced styling
    status_frame = tk.Frame(header_frame, bg=BG_COLOR)
    status_frame.grid(row=0, column=2, sticky="e")
    
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
    chat_area.tag_config("error", foreground="#FF0000")      # Red for errors
    chat_area.tag_config("tip", foreground="#00FFFF")        # Cyan for learning tips
    
    # Progress bar for language learning progress
    progress_frame = tk.Frame(main_frame, bg=BG_COLOR)
    progress_frame.grid(row=2, column=0, sticky="ew", pady=(5, 10))
    
    progress_label = tk.Label(
        progress_frame,
        text="Learning Progress:",
        font=(FONT_FAMILY, 9),
        fg=TEXT_COLOR,
        bg=BG_COLOR
    )
    progress_label.pack(side=tk.LEFT, padx=5)
    
    # Progress bar styled to match the terminal theme
    style = ttk.Style()
    style.theme_use('default')
    style.configure(
        "TProgressbar",
        troughcolor=ENTRY_BG,
        background=SYSTEM_COLOR,
        thickness=10
    )
    
    progress = ttk.Progressbar(
        progress_frame,
        style="TProgressbar",
        orient="horizontal",
        length=200,
        mode="determinate"
    )
    progress.pack(side=tk.LEFT, padx=5)
    progress["value"] = 0  # Start with 0%
    
    # Session stats
    stats_label = tk.Label(
        progress_frame,
        text="Session: 0 messages | 0 corrections",
        font=(FONT_FAMILY, 8),
        fg=TEXT_COLOR,
        bg=BG_COLOR
    )
    stats_label.pack(side=tk.RIGHT, padx=5)
    
    # Control buttons frame
    control_frame = tk.Frame(main_frame, bg=BG_COLOR)
    control_frame.grid(row=3, column=0, sticky="ew", pady=(0, 5))
    
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
        command=lambda: reset_chat(), 
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
    
    # New button for vocabulary review
    vocab_button = tk.Button(
        control_frame, 
        text="[ VOCAB REVIEW ]", 
        command=lambda: show_vocab_review(), 
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
    vocab_button.pack(side=tk.LEFT, padx=5)
    
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
    input_frame.grid(row=4, column=0, sticky="ew", pady=(5, 0))
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
    prompt_label.pack(side=tk.LEFT, padx=(0, 5))
    
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
    user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    # Session variables for stats
    session_messages = 0
    session_corrections = 0
    
    # Vocabulary learned (for review feature)
    vocabulary_learned = []
    
    # Function to show vocabulary review
    def show_vocab_review():
        if not vocabulary_learned:
            # Show message if no vocabulary learned yet
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(tk.END, "[No vocabulary items saved yet. Continue chatting to build your vocabulary list.]\n\n", "system")
            chat_area.config(state=tk.DISABLED)
            chat_area.yview(tk.END)
            return
            
        # Create popup window for vocabulary review
        vocab_window = tk.Toplevel(root)
        vocab_window.title("Vocabulary Review")
        vocab_window.geometry("500x400")
        vocab_window.configure(bg=BG_COLOR)
        
        # Make window modal
        vocab_window.transient(root)
        vocab_window.grab_set()
        
        # Header
        tk.Label(
            vocab_window,
            text="Vocabulary Review",
            font=(FONT_FAMILY, 14, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR
        ).pack(pady=10)
        
        # Create scrollable list
        vocab_frame = tk.Frame(vocab_window, bg=BG_COLOR)
        vocab_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vocab_list = scrolledtext.ScrolledText(
            vocab_frame,
            font=(FONT_FAMILY, FONT_SIZE),
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            relief="flat",
            height=15
        )
        vocab_list.pack(fill=tk.BOTH, expand=True)
        
        # Insert vocabulary items
        for item in vocabulary_learned:
            word = item["word"]
            definition = item["definition"]
            example = item["example"]
            
            vocab_list.insert(tk.END, f"{word}\n", "user")
            vocab_list.insert(tk.END, f"Definition: {definition}\n", "ai")
            vocab_list.insert(tk.END, f"Example: {example}\n\n", "system")
        
        vocab_list.config(state=tk.DISABLED)
        
        # Close button
        tk.Button(
            vocab_window,
            text="[ CLOSE ]",
            command=vocab_window.destroy,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            relief="flat",
            padx=10,
            pady=5
        ).pack(pady=10)
    
    # Function to handle sending messages with improved feedback
    def send_message():
        nonlocal session_messages, session_corrections
        
        message = user_input.get().strip()
        if message:
            # Clear the input field immediately
            user_input.delete(0, tk.END)
            
            # Disable input and buttons while processing
            user_input.config(state=tk.DISABLED)
            send_button.config(state=tk.DISABLED)
            processing_label.config(text="[ PROCESSING... ]")
            
            # Update session stats
            session_messages += 1
            
            # Check if the message needs correction (simplified for this example)
            original_message = message
            handle_user_input(message, chat_area)
            
            # If message was corrected, update count
            if message != original_message:
                session_corrections += 1
            
            # Update session stats display
            stats_label.config(text=f"Session: {session_messages} messages | {session_corrections} corrections")
            
            # Update progress bar (simple algorithm: progress based on messages and correction ratio)
            if session_messages > 0:
                success_ratio = 1 - (session_corrections / session_messages)
                # Weight: 30% message count + 70% success ratio
                progress_value = min(100, (0.3 * min(session_messages, 30) * (100/30)) + (0.7 * success_ratio * 100))
                progress["value"] = progress_value
            
            # Reset UI after handling the input
            def reset_ui():
                user_input.config(state=tk.NORMAL)
                send_button.config(state=tk.NORMAL)
                processing_label.config(text="")
                user_input.focus_set()
            
            # Schedule UI reset 
            root.after(100, reset_ui)
    
    # Function to reset the chat and session stats
    def reset_chat():
        nonlocal session_messages, session_corrections
        
        # Reset conversation
        reset_conversation(chat_area)
        
        # Reset session stats
        session_messages = 0
        session_corrections = 0
        stats_label.config(text=f"Session: {session_messages} messages | {session_corrections} corrections")
        
        # Reset progress bar
        progress["value"] = 0
    
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
    send_button.pack(side=tk.RIGHT, padx=(0, 0))
    
    # Bind Enter key to send message
    user_input.bind("<Return>", lambda event: send_message())
    
    # Create menu
    menu_bar = Menu(root, bg=BG_COLOR, fg=TEXT_COLOR)
    root.config(menu=menu_bar)
    
    # File menu
    file_menu = Menu(menu_bar, tearoff=0, bg=ENTRY_BG, fg=TEXT_COLOR)
    file_menu.add_command(label="Save Conversation", command=lambda: save_conversation())
    file_menu.add_command(label="Export Vocabulary List", command=lambda: export_vocabulary())
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    # Tools menu
    tools_menu = Menu(menu_bar, tearoff=0, bg=ENTRY_BG, fg=TEXT_COLOR)
    tools_menu.add_command(label="Grammar Check", command=lambda: grammar_check_mode())
    tools_menu.add_command(label="Free Conversation", command=lambda: conversation_mode())
    tools_menu.add_command(label="Vocabulary Builder", command=lambda: vocabulary_mode())
    menu_bar.add_cascade(label="Learning Tools", menu=tools_menu)
    
    # Help menu
    help_menu = Menu(menu_bar, tearoff=0, bg=ENTRY_BG, fg=TEXT_COLOR)
    help_menu.add_command(label="About", command=lambda: show_about())
    help_menu.add_command(label="Usage Tips", command=lambda: show_tips())
    menu_bar.add_cascade(label="Help", menu=help_menu)
    
    # Placeholder functions for menu items
    def save_conversation():
        # Placeholder - would save the conversation to a file
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, "[Conversation saved feature coming soon]\n", "system")
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)
    
    def export_vocabulary():
        # Placeholder - would export vocabulary list
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, "[Vocabulary export feature coming soon]\n", "system")
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)
    
    def grammar_check_mode():
        # Set focus to grammar checking
        mode_var.set("Verb Tenses")
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, "[Grammar check mode activated - focus on verb tenses and grammar rules]\n", "system")
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)
    
    def conversation_mode():
        # Set focus to free conversation
        mode_var.set("General")
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, "[Free conversation mode activated - practice natural discussions]\n", "system")
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)
    
    def vocabulary_mode():
        # Set focus to vocabulary building
        mode_var.set("Vocabulary")
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, "[Vocabulary builder mode activated - focus on learning new words and expressions]\n", "system")
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)
    
    def show_about():
        # Display about information
        about_window = tk.Toplevel(root)
        about_window.title("About English AI Terminal")
        about_window.geometry("400x300")
        about_window.configure(bg=BG_COLOR)
        
        # Make window modal
        about_window.transient(root)
        about_window.grab_set()
        
        # Content
        tk.Label(
            about_window,
            text="English AI Terminal",
            font=(FONT_FAMILY, 14, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR
        ).pack(pady=10)
        
        tk.Label(
            about_window,
            text="An AI-powered English learning assistant\nusing local language models with Ollama.",
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            justify=tk.CENTER
        ).pack(pady=10)
        
        tk.Label(
            about_window,
            text="Features include grammar correction, expression improvement, \nvocabulary building, and natural conversation practice.",
            font=(FONT_FAMILY, 9),
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Close button
        tk.Button(
            about_window,
            text="[ CLOSE ]",
            command=about_window.destroy,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            relief="flat",
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def show_tips():
        # Display usage tips
        tips_window = tk.Toplevel(root)
        tips_window.title("Usage Tips")
        tips_window.geometry("500x400")
        tips_window.configure(bg=BG_COLOR)
        
        # Make window modal
        tips_window.transient(root)
        tips_window.grab_set()
        
        # Content
        tk.Label(
            tips_window,
            text="Usage Tips",
            font=(FONT_FAMILY, 14, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR
        ).pack(pady=10)
        
        tips_text = scrolledtext.ScrolledText(
            tips_window,
            font=(FONT_FAMILY, FONT_SIZE),
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            relief="flat",
            height=15
        )
        tips_text.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Insert tips
        tips = [
            "1. Type naturally to practice conversation",
            "2. Watch for grammar corrections highlighted in gold",
            "3. Use the 'SUGGEST TOPIC' button if you're not sure what to talk about",
            "4. Try different learning modes from the dropdown menu",
            "5. Review your vocabulary list to reinforce learning",
            "6. Reset the chat to start a fresh conversation",
            "7. Aim to reduce corrections over time to see your progress",
            "8. Practice regularly for best results",
            "9. Experiment with different tenses and expressions",
            "10. Have fun - enjoyable learning is more effective!"
        ]
        
        for tip in tips:
            tips_text.insert(tk.END, f"{tip}\n\n", "correction")
        
        tips_text.config(state=tk.DISABLED)
        
        # Close button
        tk.Button(
            tips_window,
            text="[ CLOSE ]",
            command=tips_window.destroy,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            relief="flat",
            padx=10,
            pady=5
        ).pack(pady=10)
    
    # Set focus to input field
    user_input.focus_set()
    
    # Add improved startup text with simple ASCII banner
    chat_area.config(state=tk.NORMAL)
    
    # Simplified ASCII banner
    banner = """
    ===============================================
            ENGLISH AI TERMINAL v2.0      
    ===============================================
    """
    
    chat_area.insert(tk.END, banner + "\n", "system")
    chat_area.insert(tk.END, "System initialized and ready for interaction.\n", "system")
    chat_area.insert(tk.END, "This enhanced version includes:\n", "system")
    chat_area.insert(tk.END, " • Advanced grammar and verb tense correction\n", "tip")
    chat_area.insert(tk.END, " • Expression improvements and alternatives\n", "tip")
    chat_area.insert(tk.END, " • Vocabulary building with review feature\n", "tip")
    chat_area.insert(tk.END, " • Learning progress tracking\n", "tip")
    chat_area.insert(tk.END, " • Multiple learning modes\n\n", "tip")
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
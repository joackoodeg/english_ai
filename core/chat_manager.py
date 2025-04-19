from core.ollama_client import get_ai_response
from core.grammar_checker import correct_text
import tkinter as tk

chat_history = ""

def handle_user_input(message, chat_area):
    global chat_history

    chat_area.config(state="normal")
    
    # Insert user message with simplified styling
    chat_area.insert("end", "USER: ", "system")
    chat_area.insert("end", f"{message}\n", "user")
    chat_area.yview("end")
    chat_area.update()

    # Show checking indicator
    processing_pos = chat_area.index("end-1c")
    chat_area.insert("end", "[Checking grammar...]\n", "system")
    chat_area.yview("end")
    chat_area.update()
    
    # Get grammar correction
    corrected, issues = correct_text(message)

    # Remove processing indicator
    chat_area.delete(processing_pos, "end")
    chat_area.update()
    
    # Display corrections with simpler styling
    if corrected != message:
        chat_area.insert("end", "GRAMMAR: ", "correction")
        chat_area.insert("end", f"{corrected}\n", "correction")
        
        if issues:
            chat_area.insert("end", "ISSUES FOUND:\n", "correction")
            for i in issues:
                chat_area.insert("end", f" • {i}\n", "correction")
        chat_area.insert("end", "\n", "system")
    else:
        chat_area.insert("end", "[✓ Grammar OK]\n\n", "correction")
    
    chat_area.yview("end")
    chat_area.update()

    # Update chat history with corrected text
    chat_history += f"User: {corrected}\n"
    
    # Show thinking animation
    chat_area.insert("end", "AI: ", "system")
    
    # Get AI response
    ai_response = get_ai_response(chat_history)
    chat_history += f"AI: {ai_response}\n"
    
    # Show the AI response with simplified styling
    chat_area.insert("end", f"{ai_response.strip()}\n", "ai")
    
    # Add simple separator
    chat_area.insert("end", "\n" + "-" * 50 + "\n\n", "separator")
    
    chat_area.config(state="disabled")
    chat_area.yview("end")
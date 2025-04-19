from core.ollama_client import get_ai_response
from core.grammar_checker import correct_text
import time

chat_history = ""

def handle_user_input(message, chat_area):
    global chat_history

    chat_area.config(state="normal")
    
    # Insert user message
    chat_area.insert("end", "> ", "system")
    chat_area.insert("end", f"{message}\n", "user")
    chat_area.yview("end")
    chat_area.update()

    # Show "checking" indicator
    processing_pos = chat_area.index("end-1c")
    chat_area.insert("end", "Checking grammar...", "system")
    chat_area.yview("end")
    chat_area.update()
    
    # Get grammar correction
    corrected, issues = correct_text(message)

    # Remove processing indicator
    chat_area.delete(processing_pos, "end")
    chat_area.update()
    
    # Display corrections if any (on separate lines)
    if corrected != message:
        chat_area.insert("end", "(Corrected): ", "correction")
        chat_area.insert("end", f"{corrected}\n", "correction")
        
        if issues:
            chat_area.insert("end", "(Corrections):\n", "correction")
            for i in issues:
                chat_area.insert("end", f" - {i}\n", "correction")
            # Add an extra line after corrections
            chat_area.insert("end", "\n", "system")
    else:
        chat_area.insert("end", "✔ Grammar OK\n\n", "correction")
    
    chat_area.yview("end")
    chat_area.update()

    # Update chat history with corrected text
    chat_history += f"User: {corrected}\n"
    
    # Show AI response on a new line with a clear label
    chat_area.insert("end", "AI: ", "system")
    chat_area.yview("end")
    
    # Get AI response
    ai_response = get_ai_response(chat_history)
    chat_history += f"AI: {ai_response}\n"
    
    # Show the AI response
    chat_area.insert("end", f"{ai_response.strip()}\n", "ai")
    
    # Add separator for better readability
    chat_area.insert("end", "\n" + "-" * 40 + "\n\n", "system")
    
    chat_area.config(state="disabled")
    chat_area.yview("end")
    
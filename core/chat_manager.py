from core.ollama_client import get_ai_response
from core.grammar_checker import correct_text

chat_history = ""

def handle_user_input(message, chat_area):
    global chat_history

    chat_area.config(state="normal")
    chat_area.insert("end", f"> {message}\n", "user")

    corrected, issues = correct_text(message)

    if corrected != message:
        chat_area.insert("end", f"(Corrected): {corrected}\n", "system")
        if issues:
            chat_area.insert("end", "(Corrections):\n", "system")
            for i in issues:
                chat_area.insert("end", f" - {i}\n", "system")
    else:
        chat_area.insert("end", "✔ OK, bien\n", "system")

    chat_history += f"User: {corrected}\n"
    ai_response = get_ai_response(chat_history)
    chat_history += f"AI: {ai_response}\n"

    chat_area.insert("end", f"AI: {ai_response.strip()}\n", "ai")
    chat_area.config(state="disabled")
    chat_area.yview("end")


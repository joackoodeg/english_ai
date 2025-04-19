from core.ollama_client import get_ai_response
from core.grammar_checker import correct_text
from core.prompt_loader import load_starters
import tkinter as tk
import random
import time

# Initialize with conversation starters and a system prompt
STARTERS = load_starters()
SYSTEM_PROMPT = """
You are an English learning assistant. Your job is to:
1. Always respond in English, even if the user writes in another language
2. Keep the conversation going by asking engaging follow-up questions
3. Gently correct any English errors in the user's messages
4. Use simple, clear language appropriate for language learners
5. Introduce new vocabulary and idioms with explanations
6. Encourage the user to express themselves and practice more
7. Suggest topics if the conversation stalls
8. Be patient, encouraging, and supportive

Remember that your main goal is to keep the conversation flowing naturally while helping
the user improve their English skills.
"""

chat_history = SYSTEM_PROMPT

def handle_user_input(message, chat_area):
    global chat_history

    chat_area.config(state="normal")
    
    # Insert user message with simplified styling
    chat_area.insert("end", "USER: ", "system")
    chat_area.insert("end", f"{message}\n", "user")
    chat_area.yview("end")
    chat_area.update()

    # Show checking indicator on a new line
    chat_area.insert("end", "[Checking grammar...]\n", "system")
    chat_area.yview("end")
    chat_area.update()
    
    # Get grammar correction
    corrected, issues = correct_text(message)

    # Display corrections with simpler styling - always on a new line
    if corrected != message:
        chat_area.insert("end", "GRAMMAR:\n", "correction")
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

    # AI waiting message on a new line
    chat_area.insert("end", "AI: ", "system")
    chat_area.insert("end", "[Thinking...]\n", "system")
    chat_area.yview("end")
    chat_area.update()
    
    # Update chat history with corrected text
    chat_history += f"\nUser: {corrected}"
    
    # Add a prompt to encourage conversation
    prompt = chat_history + "\n\nPlease respond in a conversational way and ask a follow-up question to keep the dialogue going."
    
    # Get AI response
    ai_response = get_ai_response(prompt)
    chat_history += f"\nAI: {ai_response}"
    
    # Remove the "Thinking..." line
    chat_area.delete("end-2l", "end-1l")
    
    # Show the AI response with simplified styling
    chat_area.insert("end", f"{ai_response.strip()}\n", "ai")
    
    # Add simple separator
    chat_area.insert("end", "\n" + "-" * 50 + "\n\n", "separator")
    
    chat_area.config(state="disabled")
    chat_area.yview("end")

def suggest_topic(chat_area):
    """Suggest a conversation topic to the user"""
    if not STARTERS:
        return
        
    suggestion = random.choice(STARTERS)
    
    chat_area.config(state="normal")
    chat_area.insert("end", "SUGGESTION: ", "system")
    chat_area.insert("end", f"{suggestion}\n\n", "correction")
    chat_area.config(state="disabled")
    chat_area.yview("end")

def reset_conversation(chat_area):
    """Reset the conversation history"""
    global chat_history
    chat_history = SYSTEM_PROMPT
    
    chat_area.config(state="normal")
    chat_area.insert("end", "[Conversation reset]\n\n", "system")
    chat_area.config(state="disabled")
    chat_area.yview("end")
    
    # Suggest a starter topic
    suggest_topic(chat_area)
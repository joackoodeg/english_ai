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
2. LISTEN CAREFULLY to what the user says and acknowledge their statements before responding
3. RESPECT the user's preferences and opinions - if they say they don't like something, acknowledge it
4. Keep the conversation going by asking engaging follow-up questions about topics the user IS interested in
5. Gently correct any English errors in the user's messages
6. Use simple, clear language appropriate for language learners
7. Introduce new vocabulary and idioms with explanations when appropriate
8. Encourage the user to express themselves and practice more
9. Suggest alternative topics if the conversation stalls or if the user expresses disinterest in the current topic
10. Be patient, encouraging, and supportive

Remember that your main goal is to keep the conversation flowing naturally while helping
the user improve their English skills. Always validate what they say before moving on.
"""

chat_history = SYSTEM_PROMPT

def detect_disinterest(message):
    """
    Detect if user is expressing disinterest in the current topic
    
    Args:
        message: The user's message
        
    Returns:
        tuple: (is_disinterested, topic_to_avoid)
    """
    message = message.lower()
    
    # Common phrases indicating disinterest
    disinterest_phrases = [
        "don't like", "dont like", "not interested", 
        "boring", "don't want to", "dont want to",
        "not my thing", "hate", "dislike",
        "don't enjoy", "dont enjoy"
    ]
    
    # Check if any disinterest phrase is in the message
    is_disinterested = any(phrase in message for phrase in disinterest_phrases)
    
    # Try to identify the topic they're not interested in
    topic_to_avoid = None
    if is_disinterested:
        # Common topics that might be mentioned
        topics = ["book", "movie", "music", "sport", "travel", "food", 
                 "hobby", "pet", "vacation", "weekend", "season"]
        
        # Find which topic they mentioned
        for topic in topics:
            if topic in message:
                topic_to_avoid = topic
                break
    
    return is_disinterested, topic_to_avoid

def suggest_topic(chat_area, avoid_topic=None):
    """
    Suggest a conversation topic to the user, avoiding a specific topic if provided
    
    Args:
        chat_area: The text area to display the suggestion
        avoid_topic: Optional keyword to avoid in the suggested topic
    """
    if not STARTERS:
        return
    
    # If we need to avoid a specific topic, filter out starters containing that keyword
    available_starters = STARTERS
    if avoid_topic:
        avoid_topic = avoid_topic.lower()
        available_starters = [s for s in STARTERS if avoid_topic not in s.lower()]
    
    # If no suitable starters remain, use the full list
    if not available_starters:
        available_starters = STARTERS
        
    suggestion = random.choice(available_starters)
    
    chat_area.config(state="normal")
    chat_area.insert("end", "SUGGESTION: ", "system")
    chat_area.insert("end", f"{suggestion}\n\n", "correction")
    chat_area.config(state="disabled")
    chat_area.yview("end")

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

    # Check for disinterest and suggest a new topic if needed
    is_disinterested, topic_to_avoid = detect_disinterest(corrected)
    
    if is_disinterested and topic_to_avoid:
        chat_area.insert("end", f"[Detected disinterest in topic: {topic_to_avoid}. Suggesting alternative...]\n", "system")
        suggest_topic(chat_area, topic_to_avoid)
        chat_area.yview("end")
        chat_area.update()

    # AI waiting message on a new line
    chat_area.insert("end", "AI: ", "system")
    chat_area.insert("end", "[Thinking...]\n", "system")
    chat_area.yview("end")
    chat_area.update()
    
    # Format chat history with a clearer structure
    last_message = f"User's most recent message: \"{corrected}\". "
    
    if is_disinterested:
        last_message += f"The user has expressed they DON'T LIKE {topic_to_avoid if topic_to_avoid else 'the current topic'}. "
        last_message += "Acknowledge this and change the subject to something different."
    else:
        last_message += "Make sure to respond directly to this."
    
    # Update chat history with corrected text and emphasize the current message
    chat_history += f"\nUser: {corrected}"
    
    # Add a prompt to encourage better understanding and response
    prompt = chat_history + f"\n\n{last_message}\nRespond conversationally and ask a follow-up question about something the user might be interested in."
    
    # Get AI response
    ai_response = get_ai_response(prompt)
    chat_history += f"\nAI: {ai_response}"
    
    # Limit chat history length to prevent context overflow with smaller models
    # Keep only the last 10 exchanges plus the system prompt
    history_lines = chat_history.split('\n')
    if len(history_lines) > 20:  # System prompt + 10 exchanges (2 lines each)
        system_prompt_lines = SYSTEM_PROMPT.strip().split('\n')
        chat_history = '\n'.join(system_prompt_lines + history_lines[-20:])
    
    # Remove the "Thinking..." line
    chat_area.delete("end-2l", "end-1l")
    
    # Show the AI response with simplified styling
    chat_area.insert("end", f"{ai_response.strip()}\n", "ai")
    
    # Add simple separator
    chat_area.insert("end", "\n" + "-" * 50 + "\n\n", "separator")
    
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
from core.ollama_client import get_ai_response
from core.grammar_checker import correct_text, get_alternative_expressions
from core.prompt_loader import load_starters
import tkinter as tk
import random
import time

# Initialize with conversation starters and an enhanced system prompt
STARTERS = load_starters()
SYSTEM_PROMPT = """
You are an advanced English learning assistant. Your job is to:
1. Always respond in English, even if the user writes in another language
2. LISTEN CAREFULLY to what the user says and acknowledge their statements before responding
3. RESPECT the user's preferences and opinions - if they say they don't like something, acknowledge it
4. Keep the conversation going by asking engaging follow-up questions about topics the user IS interested in
5. Gently but thoroughly correct English errors in the user's messages:
   - Focus on verb tense consistency
   - Suggest more natural-sounding expressions
   - Provide simple explanations for corrections
6. Use simple, clear language appropriate for language learners
7. Introduce new vocabulary and idioms with explanations when appropriate
8. Encourage the user to express themselves and practice more
9. Suggest alternative topics if the conversation stalls or if the user expresses disinterest in the current topic
10. Be patient, encouraging, and supportive

Important teaching techniques:
- When you suggest a better expression, explain WHY it's better
- Identify patterns in the user's errors to provide focused help
- Praise good language use to reinforce learning
- Use examples to illustrate correct usage
- If appropriate, teach common collocations and context-specific vocabulary

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
        "don't enjoy", "dont enjoy", "don't care",
        "dont care", "let's change", "lets change"
    ]
    
    # Check if any disinterest phrase is in the message
    is_disinterested = any(phrase in message for phrase in disinterest_phrases)
    
    # Try to identify the topic they're not interested in
    topic_to_avoid = None
    if is_disinterested:
        # Common topics that might be mentioned
        topics = ["book", "movie", "music", "sport", "travel", "food", 
                 "hobby", "pet", "vacation", "weekend", "season",
                 "politics", "weather", "technology", "history", "news"]
        
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

def format_learning_feedback(categorized_issues, expression_suggestions):
    """
    Format the learning feedback in a structured, educational way
    
    Args:
        categorized_issues: Dictionary of issues by category
        expression_suggestions: List of alternative expressions
        
    Returns:
        Formatted feedback string
    """
    feedback = []
    
    # Add verb tense feedback if present
    if categorized_issues['VERB_TENSE']:
        feedback.append("VERB TENSE ISSUES:")
        for issue in categorized_issues['VERB_TENSE'][:3]:  # Limit to top 3
            feedback.append(f" • {issue}")
    
    # Add expression feedback if present
    if categorized_issues['EXPRESSION'] or expression_suggestions:
        feedback.append("\nEXPRESSION IMPROVEMENTS:")
        
        # Add categorized expression issues
        for issue in categorized_issues['EXPRESSION'][:2]:  # Limit to top 2
            feedback.append(f" • {issue}")
            
        # Add our custom expression suggestions
        for orig, alt in expression_suggestions[:3]:  # Limit to top 3
            feedback.append(f" • Consider using '{alt}' instead of '{orig}' for more natural expression")
    
    # Add grammar feedback if present
    if categorized_issues['GRAMMAR']:
        feedback.append("\nGRAMMAR NOTES:")
        for issue in categorized_issues['GRAMMAR'][:3]:  # Limit to top 3
            feedback.append(f" • {issue}")
    
    # Add a learning tip based on the most common issue category
    most_issues = max(categorized_issues.items(), key=lambda x: len(x[1]) if isinstance(x[1], list) else 0)
    category = most_issues[0]
    
    if category == 'VERB_TENSE' and categorized_issues['VERB_TENSE']:
        feedback.append("\nLEARNING TIP: Pay attention to keeping your verb tenses consistent throughout your sentences. If you start in past tense, continue in past tense unless there's a specific reason to change.")
    elif category == 'EXPRESSION' and (categorized_issues['EXPRESSION'] or expression_suggestions):
        feedback.append("\nLEARNING TIP: Native speakers often use specific word combinations (collocations). Learning these will make your English sound more natural.")
    elif category == 'GRAMMAR' and categorized_issues['GRAMMAR']:
        feedback.append("\nLEARNING TIP: Focus on the structure of your sentences. English often follows Subject-Verb-Object order.")
    
    return "\n".join(feedback) if feedback else "[✓ Your English is excellent!]"

def handle_user_input(message, chat_area):
    global chat_history

    chat_area.config(state="normal")
    
    # Insert user message with simplified styling
    chat_area.insert("end", "USER: ", "system")
    chat_area.insert("end", f"{message}\n", "user")
    chat_area.yview("end")
    chat_area.update()

    # Show checking indicator on a new line
    chat_area.insert("end", "[Analyzing language...]\n", "system")
    chat_area.yview("end")
    chat_area.update()
    
    # Get enhanced grammar correction
    corrected, issues, categorized_issues = correct_text(message)
    
    # Get alternative expression suggestions
    expression_suggestions = get_alternative_expressions(message)

    # Display corrections with better formatting
    if corrected != message or expression_suggestions:
        chat_area.insert("end", "CORRECTION:\n", "correction")
        chat_area.insert("end", f"{corrected}\n\n", "correction")
        
        # Display comprehensive feedback
        learning_feedback = format_learning_feedback(categorized_issues, expression_suggestions)
        chat_area.insert("end", "LEARNING NOTES:\n", "correction") 
        chat_area.insert("end", f"{learning_feedback}\n\n", "correction")
    else:
        chat_area.insert("end", "[✓ Your English looks good!]\n\n", "correction")
    
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
    
    # Prepare instruction for the AI based on the corrections and user's intent
    instruction = "Please respond to the user. "
    
    # Add information about corrections made
    if corrected != message:
        instruction += "I've corrected some grammar issues in their message. "
    
    if expression_suggestions:
        instruction += "I've suggested some more natural expressions. "
    
    # Add information about most common issue category for focused help
    most_issues = max(categorized_issues.items(), key=lambda x: len(x[1]) if isinstance(x[1], list) else 0)
    category, issues_list = most_issues
    
    if issues_list:
        instruction += f"Their most common issue is with {category.lower().replace('_', ' ')}. Please subtly incorporate correct usage of this in your response. "
    
    # Add disinterest information
    if is_disinterested:
        instruction += f"The user has expressed they DON'T LIKE {topic_to_avoid if topic_to_avoid else 'the current topic'}. Acknowledge this and change the subject to something different. "
    
    # Format chat history with a clearer structure
    last_message = f"User's message: \"{corrected}\". {instruction} Respond conversationally and end with a question to keep the conversation going."
    
    # Update chat history with corrected text
    chat_history += f"\nUser: {corrected}"
    
    # Get AI response with enhanced prompting
    prompt = chat_history + f"\n\n{last_message}"
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
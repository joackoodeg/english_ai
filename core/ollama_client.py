import requests
import time
import random
from config import OLLAMA_API_URL, OLLAMA_MODEL

# Enhanced system instructions for language learning
INSTRUCTION_TEMPLATES = [
    # Template focusing on verb tense consistency
    """
    As an English learning assistant, help the user with their question below.
    Pay special attention to verb tense consistency in your response. 
    Use {tense} tense predominantly in your answer to model correct usage.
    Respond conversationally and ask a follow-up question at the end.
    """,
    
    # Template focusing on vocabulary enrichment
    """
    As an English learning assistant, help the user with their question below.
    In your response, introduce 1-2 useful expressions or idioms related to {topic}.
    Briefly explain what each expression means.
    Respond conversationally and ask a follow-up question at the end.
    """,
    
    # Template focusing on sentence structure 
    """
    As an English learning assistant, help the user with their question below.
    In your response, use a variety of sentence structures including:
    - A complex sentence (with dependent and independent clauses)
    - A question
    - A sentence with a conditional (if/then)
    Respond conversationally and end with a question.
    """
]

# Topics for vocabulary enrichment
VOCAB_TOPICS = [
    "time", "business", "education", "travel", "food", 
    "relationships", "work", "technology", "health", "opinions",
    "comparing things", "describing feelings", "making plans",
    "agreeing and disagreeing", "giving advice"
]

# Verb tenses to model
VERB_TENSES = [
    "present simple", "present continuous", "past simple", 
    "past continuous", "present perfect", "future with will",
    "future with going to", "present perfect continuous"
]

def get_ai_response(prompt: str) -> str:
    """
    Get a response from the Ollama API with improved parameters for better language learning.
    
    Args:
        prompt: The user prompt with conversation history
        
    Returns:
        The AI response as a string
    """
    try:
        # Start time to calculate response time
        start_time = time.time()
        
        # Randomly select an instruction template to vary the language focus
        template = random.choice(INSTRUCTION_TEMPLATES)
        
        # Fill in the template with appropriate values
        if "{tense}" in template:
            filled_template = template.format(tense=random.choice(VERB_TENSES))
        elif "{topic}" in template:
            filled_template = template.format(topic=random.choice(VOCAB_TOPICS))
        else:
            filled_template = template
            
        # Combine the instruction template with the user prompt
        enhanced_prompt = filled_template + "\n\n" + prompt
        
        # Create a more complete request with parameters to guide the conversation
        response = requests.post(OLLAMA_API_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": enhanced_prompt,
            "stream": False,
            # Add parameters to make responses more conversational and educational
            "options": {
                "temperature": 0.7,  # Slightly lower temperature for more coherent responses
                "top_p": 0.9,        # Nucleus sampling for more diverse text
                "top_k": 40,         # Consider more token options
                "num_predict": 350,  # Allow for longer responses
                "stop": ["User:"]    # Stop generating when the user would speak next
            }
        })
        
        response.raise_for_status()
        data = response.json()
        ai_response = data.get("response", "[No response from model]")
        
        # Clean up any trailing conversation markers the model might add
        ai_response = ai_response.replace("AI:", "").strip()
        
        # Ensure the response has a question at the end to encourage conversation
        if not any(ai_response.strip().endswith(c) for c in ["?", "?"]):
            # Check if the response is too short
            if len(ai_response.split()) < 15:
                retry_prompt = prompt + "\n\nPlease provide a detailed response that directly addresses what the user just said and ends with a question."
                return get_ai_response(retry_prompt)
            
            # If not interrogative but substantial response, add a follow-up question based on content
            follow_up_questions = [
                "What do you think about that?",
                "How does that sound to you?",
                "Would you like to know more about this topic?",
                "Have you had any experiences with this?",
                "How would you approach this situation?",
                "Would you agree with that perspective?",
                "Does that make sense to you?",
                "What else would you like to discuss?"
            ]
            ai_response += "\n\n" + random.choice(follow_up_questions)
            
        return ai_response
    except requests.exceptions.ConnectionError:
        return "[Error: Connection to Ollama failed. Make sure Ollama is running on your machine and the model is downloaded.]"
    except requests.exceptions.RequestException as e:
        return f"[Error: Request to Ollama failed: {e}]"
    except Exception as e:
        return f"[Error: {e}]"
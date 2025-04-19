import requests
from config import OLLAMA_API_URL, OLLAMA_MODEL

def get_ai_response(prompt: str) -> str:
    """
    Get a response from the Ollama API with improved parameters for better conversation.
    
    Args:
        prompt: The user prompt with conversation history
        
    Returns:
        The AI response as a string
    """
    try:
        # Create a more complete request with parameters to guide the conversation
        response = requests.post(OLLAMA_API_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            # Add parameters to make responses more conversational and engaging
            "options": {
                "temperature": 0.8,  # Higher temperature for more creative responses
                "top_p": 0.9,        # Nucleus sampling for more diverse text
                "top_k": 40,         # Consider more token options
                "num_predict": 300,  # Allow for longer responses
                "stop": ["User:"]    # Stop generating when the user would speak next
            }
        })
        
        response.raise_for_status()
        data = response.json()
        ai_response = data.get("response", "[No response from model]")
        
        # Clean up any trailing conversation markers the model might add
        ai_response = ai_response.replace("AI:", "").strip()
        
        # If response is too short, retry with a more direct prompt
        if len(ai_response.split()) < 10:
            retry_prompt = prompt + "\n\nPlease provide a more detailed response and ask a follow-up question to keep the conversation going."
            return get_ai_response(retry_prompt)
            
        return ai_response
    except Exception as e:
        return f"[Error: {e}]"
APP_TITLE = "English AI Terminal"
WINDOW_SIZE = "900x600"  # Increased size for better readability and more features

# Font configuration
FONT_FAMILY = "Courier New"  # Monospace font for terminal look
FONT_SIZE = 12

# Enhanced terminal color scheme
BG_COLOR = "#121212"  # Slightly lighter than pure black for better contrast
TEXT_COLOR = "#33FF33"  # Vibrant terminal green
ENTRY_BG = "#1A1A1A"  # Slightly lighter than background for input areas
BUTTON_BG = "#222222"  # Dark gray for buttons
HIGHLIGHT_COLOR = "#00CCFF"  # Bright cyan for AI responses
SYSTEM_COLOR = "#FFD700"  # Gold for system messages
ERROR_COLOR = "#FF4500"  # Orange-red for errors
TIP_COLOR = "#00FFAA"  # Bright mint for learning tips

# IA local
# alt: tinyllama / gemma:2b
OLLAMA_MODEL = "gemma:2b"  # Can be changed to any Ollama-supported model
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Learning settings
LEARNING_LEVELS = ["Beginner", "Intermediate", "Advanced"]
DEFAULT_LEVEL = "Intermediate"

# Grammar check settings
GRAMMAR_FOCUS_OPTIONS = ["All", "Verb Tenses", "Prepositions", "Articles", "Word Order"]
DEFAULT_GRAMMAR_FOCUS = "All"

# Vocabulary settings
VOCAB_REVIEW_FREQUENCY = 10  # How often to suggest vocabulary review (in messages)
MAX_VOCABULARY_LIST = 200  # Maximum vocabulary items to store

# Feature toggles
ENABLE_PRONUNCIATION_TIPS = True  # Enable pronunciation tips (text-based)
ENABLE_LEARNING_PROGRESS = True  # Enable progress tracking
ENABLE_VOCABULARY_BUILDER = True  # Enable vocabulary builder
ENABLE_EXPRESSION_IMPROVEMENT = True  # Enable better expression suggestions
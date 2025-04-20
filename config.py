# Configuración de la aplicación
APP_TITLE = "English AI Terminal"
WINDOW_SIZE = "1000x700"  # Tamaño aumentado para acomodar nuevas funcionalidades

# Configuración de fuente
FONT_FAMILY = "Courier New"  # Fuente monoespaciada para aspecto de terminal
FONT_SIZE = 12

# Esquema de colores del terminal mejorado
BG_COLOR = "#121212"  # Negro ligeramente más claro para mejor contraste
TEXT_COLOR = "#33FF33"  # Verde vibrante de terminal
ENTRY_BG = "#1A1A1A"  # Ligeramente más claro que el fondo para áreas de entrada
BUTTON_BG = "#222222"  # Gris oscuro para botones
HIGHLIGHT_COLOR = "#00CCFF"  # Cian brillante para respuestas de IA
SYSTEM_COLOR = "#FFD700"  # Dorado para mensajes del sistema
ERROR_COLOR = "#FF4500"  # Naranja-rojo para errores
TIP_COLOR = "#00FFAA"  # Menta brillante para consejos de aprendizaje

# IA local
# alt: tinyllama / gemma:2b / llama2:7b etc.
OLLAMA_MODEL = "gemma:2b"  # Puede cambiarse a cualquier modelo compatible con Ollama
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Configuración de aprendizaje
LEARNING_LEVELS = ["Principiante", "Intermedio", "Avanzado"]
DEFAULT_LEVEL = "Intermedio"

# Configuración de verificación gramatical
GRAMMAR_FOCUS_OPTIONS = ["Todo", "Tiempos Verbales", "Preposiciones", "Artículos", "Orden de Palabras"]
DEFAULT_GRAMMAR_FOCUS = "Todo"

# Configuración de vocabulario
VOCAB_REVIEW_FREQUENCY = 10  # Con qué frecuencia sugerir revisión de vocabulario (en mensajes)
MAX_VOCABULARY_LIST = 500  # Máximo de elementos de vocabulario para almacenar
VOCAB_FILE = "data/vocabulary.json"  # Archivo para almacenar el vocabulario

# Rutas de archivos
DATA_DIR = "data"  # Directorio para almacenar datos del usuario
LOG_FILE = "data/app.log"  # Archivo de registro
CONVERSATION_EXPORT_DIR = "data/conversations"  # Directorio para exportar conversaciones

# Configuración de reconocimiento de voz
SPEECH_RECOGNITION_TIMEOUT = 5  # Tiempo máximo de escucha en segundos
SPEECH_ENERGY_THRESHOLD = 4000  # Umbral de energía para detección de voz

# Configuración de repetición espaciada
SPACED_REPETITION_INITIAL_INTERVAL = 1  # Intervalo inicial en días
SPACED_REPETITION_EASY_FACTOR = 2.5  # Factor de facilidad para palabras fáciles
SPACED_REPETITION_HARD_FACTOR = 1.3  # Factor de facilidad para palabras difíciles

# Activadores de funciones
ENABLE_PRONUNCIATION_TIPS = True  # Habilitar consejos de pronunciación (basados en texto)
ENABLE_LEARNING_PROGRESS = True  # Habilitar seguimiento de progreso
ENABLE_VOCABULARY_BUILDER = True  # Habilitar constructor de vocabulario
ENABLE_EXPRESSION_IMPROVEMENT = True  # Habilitar sugerencias de mejores expresiones
ENABLE_SPEECH_RECOGNITION = True  # Habilitar reconocimiento de voz
ENABLE_SPEECH_SYNTHESIS = True  # Habilitar síntesis de voz
ENABLE_SPACED_REPETITION = True  # Habilitar sistema de repetición espaciada
ENABLE_CUSTOM_THEMES = True  # Habilitar temas personalizables
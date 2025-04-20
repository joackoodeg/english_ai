import language_tool_python
import re
from typing import Dict, List, Tuple, Any, Optional
import json
import os
from config import DATA_DIR

# Inicializar la herramienta
tool = language_tool_python.LanguageTool('en-US')

# Categorizar problemas por tipo para mejor retroalimentación
VERB_TENSE_RULES = [
    'TENSE_SEQUENCE',
    'TENSE_SIMPLE_PAST',
    'PAST_TENSE',
    'CONDITIONAL_PERFECT',
    'VERB_FORM',
    'VERB_TENSE',
]

EXPRESSION_IMPROVEMENT_RULES = [
    'COLLOCATION',
    'REDUNDANCY',
    'WORDINESS',
    'INFORMAL_EXPRESSIONS',
]

PRONUNCIATION_CHALLENGES = {
    # sonidos de vocales
    'æ': ['cat', 'bat', 'hat', 'mat', 'sat'],
    'ɑː': ['car', 'far', 'hard', 'park', 'dark'],
    'ɒ': ['hot', 'pot', 'lot', 'not', 'got'],
    'ɔː': ['more', 'door', 'floor', 'four', 'jaw'],
    'ʊ': ['book', 'look', 'cook', 'good', 'foot'],
    'uː': ['food', 'mood', 'moon', 'soon', 'cool'],
    'ʌ': ['cut', 'but', 'much', 'such', 'luck'],
    'ɜː': ['bird', 'word', 'turn', 'learn', 'earn'],
    # sonidos de consonantes
    'θ': ['thank', 'think', 'three', 'throw', 'through'],
    'ð': ['this', 'that', 'these', 'those', 'there'],
    'ʃ': ['she', 'ship', 'fish', 'wish', 'dish'],
    'ʒ': ['measure', 'pleasure', 'treasure', 'vision', 'decision'],
    'h': ['house', 'hand', 'heart', 'hair', 'happy'],
    'r': ['red', 'right', 'run', 'read', 'real'],
    'ŋ': ['sing', 'ring', 'bring', 'king', 'thing'],
    'dʒ': ['jump', 'job', 'jam', 'judge', 'journey'],
    'tʃ': ['chair', 'church', 'cheese', 'choose', 'champion'],
}

# Cargar o crear base de conocimiento persistente
class KnowledgeBase:
    def __init__(self, file_path: str = "data/language_knowledge.json"):
        self.file_path = file_path
        self.data = {
            "common_errors": {},       # Errores comunes del usuario
            "learned_vocabulary": {},  # Vocabulario aprendido
            "error_patterns": {},      # Patrones de errores
            "idioms_learned": {},      # Expresiones idiomáticas aprendidas
            "pronunciation_challenges": {}  # Desafíos de pronunciación específicos
        }
        self.load()
    
    def load(self):
        """Cargar base de conocimiento desde archivo"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
        except Exception as e:
            print(f"Error al cargar base de conocimiento: {e}")
            # Asegurarse de que el directorio exista
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    def save(self):
        """Guardar base de conocimiento en archivo"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error al guardar base de conocimiento: {e}")
    
    def record_error(self, error_type: str, error_text: str, context: str):
        """Registrar un error en la base de conocimiento"""
        if error_type not in self.data["common_errors"]:
            self.data["common_errors"][error_type] = {}
        
        if error_text in self.data["common_errors"][error_type]:
            self.data["common_errors"][error_type][error_text]["count"] += 1
            
            # Añadir contexto si no se ha visto antes
            if context not in self.data["common_errors"][error_type][error_text]["contexts"]:
                self.data["common_errors"][error_type][error_text]["contexts"].append(context)
        else:
            self.data["common_errors"][error_type][error_text] = {
                "count": 1,
                "contexts": [context]
            }
        
        self.save()
    
    def add_vocabulary(self, word: str, definition: str, example: str, tags: List[str] = None):
        """Añadir vocabulario aprendido"""
        self.data["learned_vocabulary"][word] = {
            "definition": definition,
            "example": example,
            "tags": tags or [],
            "date_added": self.get_current_date_string()
        }
        self.save()
    
    def get_current_date_string(self) -> str:
        """Obtener fecha actual como string (para serialización JSON)"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_common_errors(self, limit: int = 5) -> List[Dict]:
        """Obtener los errores más comunes"""
        all_errors = []
        
        for error_type, errors in self.data["common_errors"].items():
            for error_text, data in errors.items():
                all_errors.append({
                    "type": error_type,
                    "text": error_text,
                    "count": data["count"],
                    "contexts": data["contexts"]
                })
        
        # Ordenar por frecuencia (más común primero)
        all_errors.sort(key=lambda x: x["count"], reverse=True)
        
        return all_errors[:limit]
    
    def add_pronunciation_challenge(self, phoneme: str, word: str):
        """Registrar un desafío de pronunciación para el usuario"""
        if phoneme not in self.data["pronunciation_challenges"]:
            self.data["pronunciation_challenges"][phoneme] = []
        
        if word not in self.data["pronunciation_challenges"][phoneme]:
            self.data["pronunciation_challenges"][phoneme].append(word)
            self.save()
    
    def get_pronunciation_exercises(self, count: int = 3) -> List[Dict]:
        """Obtener ejercicios de pronunciación personalizados"""
        exercises = []
        
        # Primero intentar con desafíos específicos del usuario
        for phoneme, words in self.data["pronunciation_challenges"].items():
            if words and len(exercises) < count:
                # Obtener palabras adicionales de nuestro diccionario de desafíos
                additional_words = PRONUNCIATION_CHALLENGES.get(phoneme, [])
                
                # Combinar palabras del usuario con palabras predefinidas
                all_words = list(set(words + additional_words))
                
                exercises.append({
                    "phoneme": phoneme,
                    "words": all_words[:5],  # Limitar a 5 palabras por ejercicio
                    "instruction": f"Practica el sonido '{phoneme}' en las siguientes palabras"
                })
        
        # Si no hay suficientes, añadir ejercicios generales
        if len(exercises) < count:
            general_phonemes = list(PRONUNCIATION_CHALLENGES.keys())
            
            # Filtrar los que ya están incluidos
            used_phonemes = [ex["phoneme"] for ex in exercises]
            general_phonemes = [p for p in general_phonemes if p not in used_phonemes]
            
            # Añadir ejercicios adicionales
            import random
            random.shuffle(general_phonemes)
            
            for phoneme in general_phonemes[:count - len(exercises)]:
                exercises.append({
                    "phoneme": phoneme,
                    "words": PRONUNCIATION_CHALLENGES[phoneme],
                    "instruction": f"Practica el sonido '{phoneme}' en las siguientes palabras"
                })
        
        return exercises


# Crear instancia de base de conocimiento
knowledge_base = KnowledgeBase()

def categorize_issue(rule_id: str, message: str) -> str:
    """Categorizar el tipo de problema gramatical"""
    rule_id = rule_id.upper()
    
    # Problemas de tiempos verbales
    if any(tense_rule in rule_id for tense_rule in VERB_TENSE_RULES) or 'TENSE' in rule_id:
        return 'VERB_TENSE'
    
    # Mejoras de expresión
    if any(expr_rule in rule_id for expr_rule in EXPRESSION_IMPROVEMENT_RULES):
        return 'EXPRESSION'
        
    # Categorías comunes
    if 'GRAMMAR' in rule_id:
        return 'GRAMMAR'
    elif 'SPELL' in rule_id:
        return 'SPELLING'
    elif 'PUNCT' in rule_id:
        return 'PUNCTUATION'
    elif 'STYLE' in rule_id:
        return 'STYLE'
    elif 'AGREEMENT' in rule_id:
        return 'AGREEMENT'
    else:
        return 'OTHER'

def suggest_better_expression(match: Any) -> str:
    """Generar una sugerencia para una mejor expresión basada en la coincidencia"""
    replacement = match.replacements[0] if match.replacements else None
    
    if replacement:
        return f"Consider using '{replacement}' instead of '{match.context}'"
    else:
        return f"This expression could be improved: '{match.context}'"

def detect_learner_native_language(text: str) -> Optional[str]:
    """
    Detectar posible lengua materna del aprendiz basada en patrones de error
    
    Args:
        text: El texto a analizar
        
    Returns:
        Optional[str]: Lengua materna detectada o None
    """
    # Patrones de error comunes por lengua materna
    language_patterns = {
        "spanish": [
            r'\bthe\s+\w+s\b',  # artículos incorrectos con plurales
            r'\bpersons\b',      # "persons" en lugar de "people"
            r'\bin\s+the\s+\d{4}\b',  # "in the 2020" en lugar de "in 2020"
            r'\bis\s+raining\b',  # omisión de "it" en expresiones como "it's raining"
            r'\bhave\s+\d+\s+years\b'  # literal "have X years" en lugar de "am X years old"
        ],
        "french": [
            r'\ba\s+[aeiou]\w+\b',  # "a" seguido de palabra que empieza por vocal
            r'\bactually\b',  # falso amigo "actually" (que significa "realmente" no "actualmente")
            r'\bpersonnes\b',  # uso de "personnes" 
            r'\bsympathetic\b'  # falso amigo "sympathetic"
        ],
        "german": [
            r'\bbecause\s+[^,]+?(?:,|$)',  # "because" sin separar con coma
            r'\bbecome\b',  # falso amigo "become" (no significa "bekommen" - recibir)
            r'\bI\s+(?:agree|disagree|think|believe)(?:,|\.|\s)+that\s+\w+\s+\w+\s+\w+\b',  # orden de palabras alemán
        ],
        "chinese": [
            r'\b(?:he|she|it)\s+(?:go|eat|like|have|do)s\b',  # omisión de "s" en tercera persona
            r'\bno\s+(?:have|like|want)\b',  # estructura de negación directa
            r'\bvery\s+very\b',  # duplicación de intensificadores
            r'\byesterday\s+I\s+(?:go|eat|see|meet)\b',  # omisión de tiempo pasado
        ]
    }
    
    # Contar coincidencias para cada lengua
    matches = {}
    for language, patterns in language_patterns.items():
        matches[language] = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches[language] += 1
    
    # Encontrar la lengua con más coincidencias
    max_matches = 0
    detected_language = None
    
    for language, count in matches.items():
        if count > max_matches:
            max_matches = count
            detected_language = language
    
    # Solo devolver si hay al menos 2 coincidencias
    if max_matches >= 2:
        return detected_language
    
    return None

def extract_vocabulary_candidates(text: str) -> List[Dict]:
    """
    Extraer palabras candidatas para la lista de vocabulario.
    Busca palabras poco comunes, expresiones idiomáticas, etc.
    
    Args:
        text: El texto a analizar
        
    Returns:
        List[Dict]: Lista de candidatos con palabra y tipo
    """
    # Lista de palabras comunes en inglés para excluir
    with open("data/common_words.txt", "r", encoding="utf-8") as f:
        common_words = set(word.strip().lower() for word in f)
    
    # Extraer todas las palabras
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    
    # Filtrar palabras comunes
    uncommon_words = [word for word in words if word not in common_words]
    
    # Buscar expresiones idiomáticas comunes
    idiom_patterns = [
        r'break a leg',
        r'hit the nail on the head',
        r'piece of cake',
        r'cost an arm and a leg',
        r'under the weather',
        r'bite the bullet',
        r'cut corners',
        r'call it a day',
        r'get your act together',
        r'hang in there'
        # Añadir más expresiones idiomáticas según sea necesario
    ]
    
    idioms = []
    for pattern in idiom_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            idioms.append(re.search(pattern, text, re.IGNORECASE).group(0))
    
    # Buscar phrasal verbs
    phrasal_verb_patterns = [
        r'\b(?:look|turn|put|get|bring|go|come) (?:up|down|on|off|in|out|away|back|over|through)\b',
        r'\b(?:break|give|take|make|set|run|call|fall) (?:up|down|on|off|in|out|away|back|over|through)\b'
    ]
    
    phrasal_verbs = []
    for pattern in phrasal_verb_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            phrasal_verbs.append(match.group(0))
    
    # Crear lista de candidatos
    candidates = []
    
    # Añadir palabras poco comunes
    for word in set(uncommon_words):
        candidates.append({
            "word": word,
            "type": "uncommon_word"
        })
    
    # Añadir expresiones idiomáticas
    for idiom in idioms:
        candidates.append({
            "word": idiom,
            "type": "idiom"
        })
    
    # Añadir phrasal verbs
    for phrasal_verb in phrasal_verbs:
        candidates.append({
            "word": phrasal_verb,
            "type": "phrasal_verb"
        })
    
    return candidates

def correct_text(text: str) -> Tuple[str, List[str], Dict[str, List[str]]]:
    """
    Corregir texto y proporcionar retroalimentación detallada por categoría.
    
    Args:
        text: El texto de entrada para verificar
        
    Returns:
        Tuple con:
        - texto corregido
        - lista de problemas
        - diccionario de sugerencias categorizadas
    """
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    
    # Lista básica de problemas
    issues = [f"{m.ruleIssueType.upper()}: {m.message}" for m in matches]
    
    # Sugerencias categorizadas con explicaciones
    categorized = {
        'VERB_TENSE': [],
        'EXPRESSION': [],
        'GRAMMAR': [],
        'SPELLING': [],
        'PUNCTUATION': [],
        'STYLE': [],
        'AGREEMENT': [],
        'OTHER': []
    }
    
    # Registrar errores en la base de conocimiento
    for match in matches:
        category = categorize_issue(match.ruleId, match.message)
        
        # Registrar error
        error_text = match.context
        knowledge_base.record_error(category, error_text, text)
        
        # Mensaje básico
        message = f"{match.message}"
        
        # Añadir reemplazos si están disponibles
        if match.replacements:
            message += f" Suggestion: '{match.replacements[0]}'"
            
        # Para mejoras de expresión, añadir contexto adicional
        if category == 'EXPRESSION':
            message += "\n" + suggest_better_expression(match)
            
        # Para problemas de tiempos verbales, explicar el problema
        if category == 'VERB_TENSE':
            message += "\nConsistency in verb tense is important for clear communication."
            
        categorized[category].append(message)
    
    # Intenta detectar la lengua materna del aprendiz
    native_language = detect_learner_native_language(text)
    if native_language:
        # Añadir consejos específicos para hablantes de esa lengua
        if native_language == "spanish":
            categorized['OTHER'].append(
                "Tip for Spanish speakers: Remember, in English we don't use articles with plural general nouns. "
                "For example, say 'I like dogs' not 'I like the dogs' when talking about dogs in general."
            )
        elif native_language == "french":
            categorized['OTHER'].append(
                "Tip for French speakers: Be careful with 'false friends' like 'actually' which means 'in fact' "
                "not 'currently' (actuellement in French)."
            )
        elif native_language == "german":
            categorized['OTHER'].append(
                "Tip for German speakers: In English, verbs usually stay in second position only in questions. "
                "After 'because', 'if', etc., use normal subject-verb order."
            )
        elif native_language == "chinese":
            categorized['OTHER'].append(
                "Tip for Chinese speakers: Remember to add '-s' to verbs with he/she/it, and use past tense forms "
                "for actions that happened in the past."
            )
    
    # Extraer candidatos de vocabulario
    vocab_candidates = extract_vocabulary_candidates(text)
    
    # Añadir cada candidato a la base de conocimiento
    for candidate in vocab_candidates[:3]:  # Limitar a 3 para no sobrecargar
        if candidate["type"] == "uncommon_word":
            # Aquí se podría hacer una llamada a un diccionario o API
            # Para simplificar, usamos una definición genérica
            knowledge_base.add_vocabulary(
                candidate["word"],
                f"A word that means '{candidate['word']}'", 
                f"I learned the word '{candidate['word']}' today.",
                [candidate["type"]]
            )
        elif candidate["type"] == "idiom":
            knowledge_base.add_vocabulary(
                candidate["word"],
                "An English idiom or expression", 
                f"The expression '{candidate['word']}' is used in English.",
                [candidate["type"]]
            )
        elif candidate["type"] == "phrasal_verb":
            knowledge_base.add_vocabulary(
                candidate["word"],
                "A phrasal verb in English", 
                f"The phrasal verb '{candidate['word']}' is commonly used.",
                [candidate["type"]]
            )
    
    return corrected, issues, categorized

def get_alternative_expressions(text: str) -> List[Tuple[str, str]]:
    """
    Encontrar alternativas naturales para expresiones comunes.
    
    Args:
        text: El texto de entrada
        
    Returns:
        Lista de tuplas con (frase original, mejor alternativa)
    """
    # Expresiones comunes y sus mejores alternativas
    expression_map = {
        r'\b(?:very|really|extremely) (\w+)\b': {
            'pattern': r'very|really|extremely',
            'examples': {
                'happy': ['delighted', 'thrilled', 'overjoyed'],
                'sad': ['devastated', 'heartbroken', 'miserable'],
                'tired': ['exhausted', 'drained', 'fatigued'],
                'big': ['enormous', 'massive', 'gigantic'],
                'small': ['tiny', 'miniature', 'minuscule'],
                'good': ['excellent', 'outstanding', 'superb'],
                'bad': ['terrible', 'awful', 'dreadful'],
                'hungry': ['famished', 'starving', 'ravenous'],
                'interesting': ['fascinating', 'captivating', 'intriguing'],
                'scared': ['terrified', 'petrified', 'horrified'],
            },
            'default': ['notably', 'particularly', 'remarkably']
        },
        r'\bI think\b': {
            'alternatives': ['I believe', 'In my opinion', 'I consider', 'From my perspective']
        },
        r'\ba lot of\b': {
            'alternatives': ['many', 'numerous', 'plenty of', 'a great deal of']
        },
        r'\bnice\b': {
            'alternatives': ['pleasant', 'enjoyable', 'delightful', 'charming']
        },
        r'\bgood\b': {
            'alternatives': ['excellent', 'superb', 'outstanding', 'wonderful']
        },
        r'\bbad\b': {
            'alternatives': ['poor', 'terrible', 'unpleasant', 'disappointing']
        },
        r'\bsaid\b': {
            'alternatives': ['mentioned', 'stated', 'explained', 'described']
        },
        r'\blike\b': {
            'alternatives': ['enjoy', 'appreciate', 'favor', 'prefer']
        },
    }
    
    suggestions = []
    
    for pattern, info in expression_map.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            original = match.group(0)
            
            # Para los modificadores de intensidad (very, really, etc.)
            if 'pattern' in info:
                intensity_word = re.search(info['pattern'], original, re.IGNORECASE).group(0)
                adjective = match.group(1).lower()
                
                if adjective in info['examples']:
                    alternatives = info['examples'][adjective]
                else:
                    alternatives = info['default']
                    
                for alt in alternatives:
                    suggestions.append((original, alt))
                    
            # Para reemplazos simples
            elif 'alternatives' in info:
                for alt in info['alternatives']:
                    suggestions.append((original, alt))
    
    return suggestions if suggestions else []

def get_personalized_exercises(text: str, learner_level: str = "Intermediate") -> Dict:
    """
    Generar ejercicios personalizados basados en errores y nivel del aprendiz.
    
    Args:
        text: El texto a analizar
        learner_level: Nivel del aprendiz (Beginner, Intermediate, Advanced)
        
    Returns:
        Dict: Ejercicios personalizados por categoría
    """
    # Obtener errores comunes
    common_errors = knowledge_base.get_common_errors()
    
    # Tipos de ejercicios por nivel
    exercise_types = {
        "Principiante": ["fill-in-the-blank", "multiple-choice", "matching"],
        "Intermedio": ["fill-in-the-blank", "rewrite", "error-correction", "multiple-choice"],
        "Avanzado": ["rewrite", "error-correction", "transformation", "cloze-test"]
    }
    
    # Seleccionar tipos de ejercicios según el nivel
    level_key = "Intermedio"  # valor predeterminado
    for key in exercise_types.keys():
        if key.lower() == learner_level.lower():
            level_key = key
            break
            
    applicable_types = exercise_types[level_key]
    
    # Generar ejercicios
    exercises = {}
    
    # 1. Ejercicios de tiempos verbales
    verb_tense_errors = [err for err in common_errors if err["type"] == "VERB_TENSE"]
    if verb_tense_errors and "fill-in-the-blank" in applicable_types:
        exercises["verb_tense"] = {
            "type": "fill-in-the-blank",
            "title": "Practice Verb Tenses",
            "instructions": "Fill in the blanks with the correct verb tense:",
            "items": []
        }
        
        # Generar elementos basados en errores comunes
        for error in verb_tense_errors[:3]:
            # Extraer contexto
            context = error["contexts"][0] if error["contexts"] else ""
            # Simplificar para el ejercicio
            sentence = re.sub(r'\b' + re.escape(error["text"]) + r'\b', "______", context)
            
            if sentence and "______" in sentence:
                exercises["verb_tense"]["items"].append({
                    "question": sentence,
                    "answer": error["text"]
                })
    
    # 2. Ejercicios de vocabulario
    if "multiple-choice" in applicable_types:
        vocab_candidates = extract_vocabulary_candidates(text)
        
        if vocab_candidates:
            exercises["vocabulary"] = {
                "type": "multiple-choice",
                "title": "Vocabulary Practice",
                "instructions": "Choose the best definition for each word:",
                "items": []
            }
            
            import random
            for candidate in vocab_candidates[:3]:
                # Crear opciones de respuesta (se podría mejorar con un diccionario real)
                options = ["A definition for this term", 
                          "Another possible meaning", 
                          "A third definition option", 
                          "The correct definition"]
                random.shuffle(options)
                
                correct_index = options.index("The correct definition")
                
                exercises["vocabulary"]["items"].append({
                    "question": candidate["word"],
                    "options": options,
                    "correct": correct_index
                })
    
    # 3. Ejercicios de pronunciación
    pronunciation_exercises = knowledge_base.get_pronunciation_exercises(3)
    if pronunciation_exercises:
        exercises["pronunciation"] = {
            "type": "pronunciation-practice",
            "title": "Pronunciation Practice",
            "instructions": "Practice pronouncing these challenging sounds:",
            "items": pronunciation_exercises
        }
    
    return exercises

def detect_learning_progress(history: List[Dict]) -> Dict:
    """
    Analizar el progreso del aprendizaje basado en el historial de conversaciones.
    
    Args:
        history: Historial de conversaciones con errores y correcciones
        
    Returns:
        Dict: Análisis de progreso
    """
    if not history:
        return {
            "progress": 0,
            "strengths": [],
            "weaknesses": [],
            "next_steps": []
        }
    
    # Contar errores por tipo
    error_counts = {}
    total_messages = len(history)
    total_errors = 0
    
    for entry in history:
        errors = entry.get("errors", {})
        for category, category_errors in errors.items():
            if category not in error_counts:
                error_counts[category] = 0
            error_counts[category] += len(category_errors)
            total_errors += len(category_errors)
    
    # Calcular tasa de error
    error_rate = total_errors / max(1, total_messages)
    
    # Calcular progreso (menor tasa de error = mayor progreso)
    progress = max(0, min(100, int(100 * (1 - error_rate / 5))))  # Normalizar a 0-100
    
    # Identificar fortalezas (categorías con menos errores)
    strengths = []
    for category, count in sorted(error_counts.items(), key=lambda x: x[1]):
        if count <= total_errors / (len(error_counts) * 2):  # Menos que la mitad del promedio
            strengths.append(category)
    
    # Identificar debilidades (categorías con más errores)
    weaknesses = []
    for category, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= total_errors / len(error_counts):  # Más que el promedio
            weaknesses.append(category)
    
    # Generar recomendaciones
    next_steps = []
    if weaknesses:
        main_weakness = weaknesses[0]
        if main_weakness == "VERB_TENSE":
            next_steps.append("Practice using consistent verb tenses in past/present/future")
        elif main_weakness == "EXPRESSION":
            next_steps.append("Work on using more natural expressions and collocations")
        elif main_weakness == "GRAMMAR":
            next_steps.append("Review basic sentence structure and grammar rules")
        elif main_weakness == "SPELLING":
            next_steps.append("Practice spelling with commonly misspelled words")
        elif main_weakness == "PUNCTUATION":
            next_steps.append("Review punctuation rules, especially commas and apostrophes")
        else:
            next_steps.append(f"Focus on improving your {main_weakness.lower()} skills")
    
    # Añadir recomendación general
    if progress < 30:
        next_steps.append("Continue with basic practice exercises to build foundation")
    elif progress < 70:
        next_steps.append("Try more challenging conversation topics to expand vocabulary")
    else:
        next_steps.append("Focus on advanced expressions and idioms to sound more natural")
    
    return {
        "progress": progress,
        "strengths": strengths[:3],  # Limitar a top 3
        "weaknesses": weaknesses[:3],  # Limitar a top 3
        "next_steps": next_steps
    }

# Asegurarse de que el archivo de palabras comunes exista
def initialize_common_words():
    """Inicializar archivo de palabras comunes si no existe"""
    common_words_file = "data/common_words.txt"
    os.makedirs(os.path.dirname(common_words_file), exist_ok=True)
    
    if not os.path.exists(common_words_file):
        # Lista básica de palabras comunes en inglés
        common_words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
            "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"
        ]
        
        # Guardar a archivo
        with open(common_words_file, "w", encoding="utf-8") as f:
            for word in common_words:
                f.write(f"{word}\n")

# Inicializar recursos
initialize_common_words()
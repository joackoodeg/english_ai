import speech_recognition as sr
import pyttsx3
import threading
import queue
import time

class SpeechModule:
    def __init__(self):
        # Inicializar reconocimiento de voz
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Ajustar según ruido ambiente
        self.recognizer.dynamic_energy_threshold = True
        
        # Inicializar sintetizador de voz
        self.engine = pyttsx3.init()
        # Configurar voces - intentar obtener voz en inglés si está disponible
        voices = self.engine.getProperty('voices')
        english_voice = None
        for voice in voices:
            if "english" in voice.name.lower():
                english_voice = voice.id
                break
        
        if english_voice:
            self.engine.setProperty('voice', english_voice)
        
        # Configurar velocidad y volumen
        self.engine.setProperty('rate', 150)  # 150 palabras por minuto
        self.engine.setProperty('volume', 0.8)  # Volumen (0.0 a 1.0)
        
        # Cola para comunicación entre hilos
        self.speech_queue = queue.Queue()
        self.is_listening = False
        self.is_speaking = False
        
    def listen(self, callback, error_callback=None, timeout=5):
        """
        Escucha entrada de voz y devuelve texto transcrito
        
        Args:
            callback: Función para procesar texto reconocido
            error_callback: Función para manejar errores
            timeout: Tiempo máximo de escucha en segundos
        """
        if self.is_listening:
            return False
            
        # Función para ejecutar en un hilo separado
        def listen_thread():
            self.is_listening = True
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                    
                try:
                    text = self.recognizer.recognize_google(audio, language="en-US")
                    if callback:
                        callback(text)
                except sr.UnknownValueError:
                    if error_callback:
                        error_callback("No se pudo entender el audio")
                except sr.RequestError as e:
                    if error_callback:
                        error_callback(f"Error con el servicio de reconocimiento: {e}")
            except Exception as e:
                if error_callback:
                    error_callback(f"Error: {e}")
            finally:
                self.is_listening = False
        
        # Iniciar hilo para no bloquear la UI
        threading.Thread(target=listen_thread, daemon=True).start()
        return True
    
    def speak(self, text):
        """
        Sintetiza texto a voz
        
        Args:
            text: Texto a sintetizar
        """
        if self.is_speaking:
            self.speech_queue.put(text)
            return
            
        # Función para ejecutar en un hilo separado
        def speak_thread():
            self.is_speaking = True
            try:
                # Primero procesar el texto actual
                self.engine.say(text)
                self.engine.runAndWait()
                
                # Luego procesar cualquier otro texto en la cola
                while not self.speech_queue.empty():
                    next_text = self.speech_queue.get()
                    self.engine.say(next_text)
                    self.engine.runAndWait()
            finally:
                self.is_speaking = False
        
        # Iniciar hilo para no bloquear la UI
        threading.Thread(target=speak_thread, daemon=True).start()
    
    def check_pronunciation(self, original_text, spoken_text):
        """
        Compara texto original con texto hablado para análisis básico de pronunciación
        
        Args:
            original_text: Texto que se debía pronunciar
            spoken_text: Texto reconocido del habla
            
        Returns:
            dict: Resultados del análisis
        """
        # Normalizar texto para comparación
        original = original_text.lower().strip()
        spoken = spoken_text.lower().strip()
        
        # Tokenizar en palabras
        original_words = original.split()
        spoken_words = spoken.split()
        
        # Analizar palabras correctas/incorrectas
        total_words = len(original_words)
        correct_words = 0
        mispronounced = []
        
        # Comparar palabras
        for i, orig_word in enumerate(original_words):
            if i < len(spoken_words):
                if orig_word == spoken_words[i]:
                    correct_words += 1
                else:
                    mispronounced.append((orig_word, spoken_words[i]))
            else:
                mispronounced.append((orig_word, "[omitido]"))
        
        # Calcular puntuación
        accuracy = correct_words / total_words if total_words > 0 else 0
        
        return {
            "accuracy": accuracy,
            "score": int(accuracy * 100),
            "mispronounced": mispronounced,
            "correct_words": correct_words,
            "total_words": total_words
        }
    
    def get_available_voices(self):
        """
        Obtener lista de voces disponibles
        
        Returns:
            list: Nombres de voces disponibles
        """
        voices = self.engine.getProperty('voices')
        return [voice.name for voice in voices]
    
    def set_voice(self, voice_id):
        """
        Establecer voz específica
        
        Args:
            voice_id: ID de la voz a usar
        """
        self.engine.setProperty('voice', voice_id)
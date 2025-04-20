from ctypes import windll, byref, sizeof, c_int
import tkinter as tk
from tkinter import scrolledtext, font, ttk, Menu, filedialog, messagebox
import os
from config import *
from core.chat_manager import handle_user_input, suggest_topic, reset_conversation
from core.speech_module import SpeechModule
from core.spaced_repetition import VocabularyManager

class EnhancedAppWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BG_COLOR)
        
        # Inicializar módulos
        self.init_modules()
        
        # Configurar UI
        self.setup_ui()
        
        # Variables de sesión
        self.session_messages = 0
        self.session_corrections = 0
        self.is_listening = False
        
        # Mostrar mensaje de bienvenida
        self.show_welcome_message()
        
    def init_modules(self):
        """Inicializa los módulos de la aplicación"""
        # Módulo de voz
        self.speech_module = SpeechModule()
        
        # Módulo de vocabulario
        self.vocab_manager = VocabularyManager()
        
        # Crear directorio de datos si no existe
        os.makedirs("data", exist_ok=True)
        
    def setup_ui(self):
        """Configura toda la interfaz de usuario"""
        # Hacer que la ventana sea responsiva
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Contenedor principal
        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)  # El área de chat obtiene el peso
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar componentes principales
        self.setup_header()
        self.setup_chat_area()
        self.setup_progress_area()
        self.setup_control_area()
        self.setup_input_area()
        self.setup_menu()
        
        # Configurar estilo de progreso
        self.configure_styles()
        
        # Configurar atajo de teclado
        self.root.bind("<F2>", lambda event: self.toggle_voice_input())
        
    def setup_header(self):
        """Configura la sección de encabezado"""
        # Marco del encabezado
        self.header_frame = tk.Frame(self.main_frame, bg=BG_COLOR, height=30)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)  # Empujar estado a la derecha
        
        # Texto del título con estilo ASCII
        title_text = f"┌─── {APP_TITLE} v3.0 ───┐"
        self.title_label = tk.Label(
            self.header_frame,
            text=title_text,
            font=(FONT_FAMILY, 12, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR,
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Selector de modo de aprendizaje
        self.mode_frame = tk.Frame(self.header_frame, bg=BG_COLOR)
        self.mode_frame.grid(row=0, column=1, sticky="e")
        
        self.mode_label = tk.Label(
            self.mode_frame,
            text="Enfoque:",
            font=(FONT_FAMILY, 9),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.mode_label.pack(side=tk.LEFT, padx=5)
        
        # Combobox de modo de aprendizaje
        self.mode_var = tk.StringVar(value="General")
        modes = ["General", "Tiempos Verbales", "Vocabulario", "Expresiones", "Pronunciación", "Escritura", "Lectura"]
        self.mode_selector = ttk.Combobox(
            self.mode_frame, 
            textvariable=self.mode_var,
            values=modes,
            width=12,
            state="readonly"
        )
        self.mode_selector.pack(side=tk.LEFT, padx=5)
        
        # Selector de nivel
        self.level_label = tk.Label(
            self.mode_frame,
            text="Nivel:",
            font=(FONT_FAMILY, 9),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.level_label.pack(side=tk.LEFT, padx=5)
        
        self.level_var = tk.StringVar(value="Intermedio")
        levels = ["Principiante", "Intermedio", "Avanzado"]
        self.level_selector = ttk.Combobox(
            self.mode_frame, 
            textvariable=self.level_var,
            values=levels,
            width=10,
            state="readonly"
        )
        self.level_selector.pack(side=tk.LEFT, padx=5)
        
        # Indicador de estado en la derecha con estilo mejorado
        self.status_frame = tk.Frame(self.header_frame, bg=BG_COLOR)
        self.status_frame.grid(row=0, column=2, sticky="e")
        
        # Estado con estilo ASCII
        self.status_text = "[ ONLINE ]"
        self.status_label = tk.Label(
            self.status_frame,
            text=self.status_text,
            font=(FONT_FAMILY, 10, "bold"),
            fg="#00FF00",
            bg=BG_COLOR
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Separador con estilo ASCII
        separator_text = "═" * 80  # Carácter Unicode box drawing
        self.separator = tk.Label(
            self.main_frame,
            text=separator_text,
            font=(FONT_FAMILY, 8),
            fg="#444444",
            bg=BG_COLOR
        )
        self.separator.grid(row=0, column=0, sticky="ews", pady=(30, 0))
        
    def setup_chat_area(self):
        """Configura el área de chat"""
        # Contenedor de chat con borde estilizado
        self.chat_container = tk.Frame(
            self.main_frame, 
            bg=BG_COLOR,
            highlightbackground="#444444",
            highlightthickness=1,
            bd=0
        )
        self.chat_container.grid(row=1, column=0, sticky="nsew", pady=10)
        self.chat_container.grid_rowconfigure(0, weight=1)
        self.chat_container.grid_columnconfigure(0, weight=1)
        
        # Estilo de scrollbar personalizado
        scrollbar_style = {
            "troughcolor": ENTRY_BG,
            "background": BUTTON_BG,
            "activebackground": TEXT_COLOR
        }
        
        self.chat_area = scrolledtext.ScrolledText(
            self.chat_container, 
            wrap=tk.WORD, 
            font=(FONT_FAMILY, FONT_SIZE),
            bg=ENTRY_BG, 
            fg=TEXT_COLOR, 
            insertbackground=TEXT_COLOR,
            relief="flat", 
            bd=0,
            padx=15,
            pady=15
        )
        self.chat_area.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.chat_area.config(state=tk.DISABLED)
        
        # Aplicar estilo de scrollbar
        self.chat_area.vbar.config(**scrollbar_style)
        
        # Configurar etiquetas de texto con colores mejorados
        self.chat_area.tag_config("user", foreground=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE, "bold"))
        self.chat_area.tag_config("system", foreground=SYSTEM_COLOR)
        self.chat_area.tag_config("ai", foreground=HIGHLIGHT_COLOR)
        self.chat_area.tag_config("correction", foreground="#FFD700")  # Dorado para correcciones
        self.chat_area.tag_config("separator", foreground="#444444")  # Para separadores
        self.chat_area.tag_config("waiting", foreground="#FF6600")    # Naranja para mensajes de espera
        self.chat_area.tag_config("error", foreground="#FF0000")      # Rojo para errores
        self.chat_area.tag_config("tip", foreground="#00FFFF")        # Cian para consejos de aprendizaje
        self.chat_area.tag_config("pronunciation", foreground="#FF77FF")  # Púrpura para pronunciación
        self.chat_area.tag_config("vocabulary", foreground="#00FF99")  # Verde claro para vocabulario
        
    def setup_progress_area(self):
        """Configura el área de progreso"""
        # Marco de progreso
        self.progress_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.progress_frame.grid(row=2, column=0, sticky="ew", pady=(5, 10))
        
        # Área de progreso principal
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Progreso:",
            font=(FONT_FAMILY, 9),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        # Barra de progreso estilizada para combinar con el tema de terminal
        self.progress = ttk.Progressbar(
            self.progress_frame,
            style="TProgressbar",
            orient="horizontal",
            length=200,
            mode="determinate"
        )
        self.progress.pack(side=tk.LEFT, padx=5)
        self.progress["value"] = 0  # Comenzar con 0%
        
        # Estadísticas de sesión
        self.stats_label = tk.Label(
            self.progress_frame,
            text="Sesión: 0 mensajes | 0 correcciones",
            font=(FONT_FAMILY, 8),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.stats_label.pack(side=tk.RIGHT, padx=5)
        
        # Indicador de vocabulario pendiente
        self.vocab_due_label = tk.Label(
            self.progress_frame,
            text="",
            font=(FONT_FAMILY, 8),
            fg=HIGHLIGHT_COLOR,
            bg=BG_COLOR
        )
        self.vocab_due_label.pack(side=tk.RIGHT, padx=5)
        
        # Actualizar contador de vocabulario
        self.update_vocab_due_count()
        
    def update_vocab_due_count(self):
        """Actualiza el contador de vocabulario pendiente"""
        due_items = self.vocab_manager.get_due_for_review()
        if due_items:
            self.vocab_due_label.config(text=f"Vocabulario para revisar: {len(due_items)}")
        else:
            self.vocab_due_label.config(text="")
        
    def setup_control_area(self):
        """Configura el área de controles"""
        # Marco de controles
        self.control_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.control_frame.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        
        # Botones de ayuda
        self.suggest_button = tk.Button(
            self.control_frame, 
            text="[ SUGERIR TEMA ]", 
            command=lambda: suggest_topic(self.chat_area), 
            font=(FONT_FAMILY, 8, "bold"), 
            bg=BUTTON_BG, 
            fg=TEXT_COLOR, 
            activebackground="#333333",
            activeforeground=TEXT_COLOR,
            relief="flat", 
            bd=1,
            padx=5,
            pady=1
        )
        self.suggest_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reset_button = tk.Button(
            self.control_frame, 
            text="[ REINICIAR CHAT ]", 
            command=self.reset_chat, 
            font=(FONT_FAMILY, 8, "bold"), 
            bg=BUTTON_BG, 
            fg=TEXT_COLOR, 
            activebackground="#333333",
            activeforeground=TEXT_COLOR,
            relief="flat", 
            bd=1,
            padx=5,
            pady=1
        )
        self.reset_button.pack(side=tk.LEFT)
        
        # Nuevo botón para repaso de vocabulario
        self.vocab_button = tk.Button(
            self.control_frame, 
            text="[ REPASO VOCAB ]", 
            command=self.show_vocab_review, 
            font=(FONT_FAMILY, 8, "bold"), 
            bg=BUTTON_BG, 
            fg=TEXT_COLOR, 
            activebackground="#333333",
            activeforeground=TEXT_COLOR,
            relief="flat", 
            bd=1,
            padx=5,
            pady=1
        )
        self.vocab_button.pack(side=tk.LEFT, padx=5)
        
        # Botón para entrada de voz
        self.voice_button = tk.Button(
            self.control_frame, 
            text="[ ACTIVAR VOZ ]", 
            command=self.toggle_voice_input, 
            font=(FONT_FAMILY, 8, "bold"), 
            bg=BUTTON_BG, 
            fg=TEXT_COLOR, 
            activebackground="#333333",
            activeforeground=TEXT_COLOR,
            relief="flat", 
            bd=1,
            padx=5,
            pady=1
        )
        self.voice_button.pack(side=tk.LEFT, padx=5)
        
        # Indicador de procesamiento
        self.processing_label = tk.Label(
            self.control_frame,
            text="",
            font=(FONT_FAMILY, 8, "bold"),
            fg="#FF6600",  # Naranja para procesamiento
            bg=BG_COLOR
        )
        self.processing_label.pack(side=tk.RIGHT, padx=5)
        
    def setup_input_area(self):
        """Configura el área de entrada"""
        # Marco de entrada con estilo ASCII
        self.input_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.input_frame.grid(row=4, column=0, sticky="ew", pady=(5, 0))
        self.input_frame.grid_columnconfigure(1, weight=1)  # La entrada obtiene todo el espacio extra
        
        # Símbolo de prompt estilizado
        self.prompt_label = tk.Label(
            self.input_frame,
            text="[ > ]",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR,
            width=4
        )
        self.prompt_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Campo de entrada de ancho completo con mejor estilo
        self.user_input = tk.Entry(
            self.input_frame, 
            font=(FONT_FAMILY, FONT_SIZE), 
            bg=ENTRY_BG, 
            fg=TEXT_COLOR, 
            insertbackground=TEXT_COLOR, 
            relief="flat", 
            highlightbackground="#444444",
            highlightthickness=1,
            insertwidth=2
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Botón de envío mejorado con estilo ASCII
        self.send_button = tk.Button(
            self.input_frame, 
            text="[ ENVIAR ]", 
            command=self.send_message, 
            font=(FONT_FAMILY, 10, "bold"), 
            bg=BUTTON_BG, 
            fg=TEXT_COLOR, 
            activebackground="#333333",
            activeforeground=TEXT_COLOR,
            relief="flat", 
            bd=1,
            padx=8,
            pady=2,
            width=8
        )
        self.send_button.pack(side=tk.RIGHT, padx=(0, 0))
        
        # Vincular tecla Enter para enviar mensaje
        self.user_input.bind("<Return>", lambda event: self.send_message())
        
    def setup_menu(self):
        """Configura la barra de menú"""
        self.menu_bar = Menu(self.root, bg=BG_COLOR, fg=TEXT_COLOR)
        self.root.config(menu=self.menu_bar)
        
        # Menú Archivo
        self.file_menu = Menu(self.menu_bar, tearoff=0, bg=ENTRY_BG, fg=TEXT_COLOR)
        self.file_menu.add_command(label="Guardar Conversación", command=self.save_conversation)
        self.file_menu.add_command(label="Exportar Lista de Vocabulario", command=self.export_vocabulary)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=self.root.quit)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)
        
        # Menú Herramientas
        self.tools_menu = Menu(self.menu_bar, tearoff=0, bg=ENTRY_BG, fg=TEXT_COLOR)
        self.tools_menu.add_command(label="Revisión Gramatical", command=self.grammar_check_mode)
        self.tools_menu.add_command(label="Conversación Libre", command=self.conversation_mode)
        self.tools_menu.add_command(label="Constructor de Vocabulario", command=self.vocabulary_mode)
        self.tools_menu.add_command(label="Práctica de Pronunciación", command=self.pronunciation_mode)
        self.tools_menu.add_command(label="Revisión de Vocabulario", command=self.show_vocab_review)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="Estadísticas de Aprendizaje", command=self.show_learning_stats)
        self.menu_bar.add_cascade(label="Herramientas de Aprendizaje", menu=self.tools_menu)
        
        # Menú Temas
        self.themes_menu = Menu(self.menu_bar, tearoff=0, bg=ENTRY_BG, fg=TEXT_COLOR)
        self.themes_menu.add_command(label="Terminal Clásico (Verde)", command=lambda: self.change_theme("classic"))
        self.themes_menu.add_command(label="Hacker (Verde sobre Negro)", command=lambda: self.change_theme("hacker"))
        self.themes_menu.add_command(label="Ciberpunk (Neón)", command=lambda: self.change_theme("cyberpunk"))
        self.themes_menu.add_command(label="Retro (Ámbar)", command=lambda: self.change_theme("retro"))
        self.themes_menu.add_command(label="Oscuro (Azul)", command=lambda: self.change_theme("dark_blue"))
        self.menu_bar.add_cascade(label="Temas", menu=self.themes_menu)
        
        # Menú Ayuda
        self.help_menu = Menu(self.menu_bar, tearoff=0, bg=ENTRY_BG, fg=TEXT_COLOR)
        self.help_menu.add_command(label="Acerca de", command=self.show_about)
        self.help_menu.add_command(label="Consejos de Uso", command=self.show_tips)
        self.help_menu.add_command(label="Atajos de Teclado", command=self.show_keyboard_shortcuts)
        self.menu_bar.add_cascade(label="Ayuda", menu=self.help_menu)
        
    def configure_styles(self):
        """Configura estilos personalizados para widgets"""
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "TProgressbar",
            troughcolor=ENTRY_BG,
            background=SYSTEM_COLOR,
            thickness=10
        )
        
    def show_welcome_message(self):
        """Muestra el mensaje de bienvenida inicial"""
        # Texto de inicio mejorado con banner ASCII simple
        self.chat_area.config(state=tk.NORMAL)
        
        # Banner ASCII simplificado
        banner = """
    ===============================================
          ENGLISH AI TERMINAL v3.0      
    ===============================================
    """
        
        self.chat_area.insert(tk.END, banner + "\n", "system")
        self.chat_area.insert(tk.END, "Sistema inicializado y listo para interacción.\n", "system")
        self.chat_area.insert(tk.END, "Esta versión mejorada incluye:\n", "system")
        self.chat_area.insert(tk.END, " • Reconocimiento y síntesis de voz\n", "tip")
        self.chat_area.insert(tk.END, " • Sistema avanzado de repetición espaciada para vocabulario\n", "tip")
        self.chat_area.insert(tk.END, " • Corrección gramatical y de tiempos verbales avanzada\n", "tip")
        self.chat_area.insert(tk.END, " • Mejoras de expresiones y alternativas\n", "tip")
        self.chat_area.insert(tk.END, " • Construcción de vocabulario con función de repaso\n", "tip")
        self.chat_area.insert(tk.END, " • Seguimiento de progreso de aprendizaje\n", "tip")
        self.chat_area.insert(tk.END, " • Múltiples modos de aprendizaje\n", "tip")
        self.chat_area.insert(tk.END, " • Temas personalizables\n\n", "tip")
        
        self.chat_area.insert(tk.END, "Teclea tu texto en inglés debajo para verificar la gramática y practicar conversación.\n", "system")
        self.chat_area.insert(tk.END, "Usa el botón [SUGERIR TEMA] si necesitas ideas para la conversación.\n", "system")
        self.chat_area.insert(tk.END, "Presiona F2 o utiliza el botón [ACTIVAR VOZ] para hablar en inglés.\n\n", "system")
        
        # Añadir una sugerencia de tema inicial
        suggest_topic(self.chat_area)
        
        self.chat_area.config(state=tk.DISABLED)
        
    def send_message(self):
        """Procesa y envía el mensaje del usuario"""
        message = self.user_input.get().strip()
        if message:
            # Limpiar el campo de entrada inmediatamente
            self.user_input.delete(0, tk.END)
            
            # Deshabilitar entrada y botones durante el procesamiento
            self.user_input.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)
            self.processing_label.config(text="[ PROCESANDO... ]")
            
            # Actualizar estadísticas de sesión
            self.session_messages += 1
            
            # Comprobar si el mensaje necesita corrección (simplificado para este ejemplo)
            original_message = message
            handle_user_input(message, self.chat_area)
            
            # Si se corrigió el mensaje, actualizar el recuento
            if message != original_message:
                self.session_corrections += 1
            
            # Actualizar visualización de estadísticas de sesión
            self.stats_label.config(text=f"Sesión: {self.session_messages} mensajes | {self.session_corrections} correcciones")
            
            # Actualizar barra de progreso (algoritmo simple: progreso basado en mensajes y ratio de corrección)
            if self.session_messages > 0:
                success_ratio = 1 - (self.session_corrections / self.session_messages)
                # Peso: 30% recuento de mensajes + 70% ratio de éxito
                progress_value = min(100, (0.3 * min(self.session_messages, 30) * (100/30)) + (0.7 * success_ratio * 100))
                self.progress["value"] = progress_value
            
            # Actualizar el contador de vocabulario pendiente
            self.update_vocab_due_count()
            
            # Restablecer la interfaz después de manejar la entrada
            def reset_ui():
                self.user_input.config(state=tk.NORMAL)
                self.send_button.config(state=tk.NORMAL)
                self.processing_label.config(text="")
                self.user_input.focus_set()
            
            # Programar restablecimiento de la interfaz
            self.root.after(100, reset_ui)
    
    def reset_chat(self):
        """Restablece la conversación y las estadísticas de sesión"""
        # Restablecer conversación
        reset_conversation(self.chat_area)
        
        # Restablecer estadísticas de sesión
        self.session_messages = 0
        self.session_corrections = 0
        self.stats_label.config(text=f"Sesión: {self.session_messages} mensajes | {self.session_corrections} correcciones")
        
        # Restablecer barra de progreso
        self.progress["value"] = 0
        
    def toggle_voice_input(self):
        """Activa/desactiva la entrada por voz"""
        if self.is_listening:
            # Ya está escuchando, cancelar
            self.is_listening = False
            self.voice_button.config(text="[ ACTIVAR VOZ ]")
            self.processing_label.config(text="")
            return
        
        # Iniciar escucha
        self.is_listening = True
        self.voice_button.config(text="[ ESCUCHANDO... ]", fg="#FF0000")
        self.processing_label.config(text="[ HABLA AHORA ]")
        
        # Callback para cuando se reconozca la voz
        def voice_recognized(text):
            self.is_listening = False
            self.voice_button.config(text="[ ACTIVAR VOZ ]", fg=TEXT_COLOR)
            self.processing_label.config(text="")
            
            if text:
                # Insertar texto reconocido en el campo de entrada
                self.user_input.delete(0, tk.END)
                self.user_input.insert(0, text)
                
                # Mostrar lo que se entendió
                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(tk.END, "[Voz reconocida]: ", "system")
                self.chat_area.insert(tk.END, f"{text}\n", "pronunciation")
                self.chat_area.config(state=tk.DISABLED)
                self.chat_area.yview(tk.END)
                
                # Enviar el mensaje después de un breve retraso
                self.root.after(500, self.send_message)
        
        # Callback para errores
        def voice_error(error_msg):
            self.is_listening = False
            self.voice_button.config(text="[ ACTIVAR VOZ ]", fg=TEXT_COLOR)
            self.processing_label.config(text="")
            
            # Mostrar error
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"[Error de voz]: {error_msg}\n", "error")
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.yview(tk.END)
        
        # Iniciar reconocimiento
        success = self.speech_module.listen(voice_recognized, voice_error)
        
        if not success:
            self.is_listening = False
            self.voice_button.config(text="[ ACTIVAR VOZ ]")
            self.processing_label.config(text="")
            
            # Mostrar error
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, "[Error: Ya está escuchando o no se pudo iniciar el reconocimiento]\n", "error")
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.yview(tk.END)
    
    def text_to_speech(self, text):
        """Convierte texto a voz"""
        self.speech_module.speak(text)
    
    def show_vocab_review(self):
        """Muestra la ventana de repaso de vocabulario"""
        # Obtener elementos para revisar
        review_items = self.vocab_manager.get_review_session(n=10)
        
        if not review_items:
            # Mostrar mensaje si no hay elementos de vocabulario aún
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, "[No hay elementos de vocabulario guardados aún. Continúa charlando para construir tu lista de vocabulario.]\n\n", "system")
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.yview(tk.END)
            return
            
        # Crear ventana emergente para repaso de vocabulario
        vocab_window = tk.Toplevel(self.root)
        vocab_window.title("Repaso de Vocabulario")
        vocab_window.geometry("600x500")
        vocab_window.configure(bg=BG_COLOR)
        
        # Hacer ventana modal
        vocab_window.transient(self.root)
        vocab_window.grab_set()
        
        # Encabezado
        tk.Label(
            vocab_window,
            text="Sistema de Repetición Espaciada",
            font=(FONT_FAMILY, 14, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR
        ).pack(pady=10)
        
        # Marco de instrucciones
        instruction_frame = tk.Frame(vocab_window, bg=BG_COLOR)
        instruction_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(
            instruction_frame,
            text="Evalúa tu conocimiento de cada palabra (0-5):",
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            justify=tk.LEFT
        ).pack(anchor="w")
        
        tk.Label(
            instruction_frame,
            text="0: Olvidada | 1: Difícil de recordar | 3: Con dudas | 5: Perfecta",
            font=(FONT_FAMILY, 9),
            fg=HIGHLIGHT_COLOR,
            bg=BG_COLOR,
            justify=tk.LEFT
        ).pack(anchor="w")
        
        # Contenedor para tarjetas de repaso
        review_container = tk.Frame(vocab_window, bg=BG_COLOR)
        review_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Variables para seguimiento
        current_index = [0]  # Usar lista para que sea mutable en funciones anidadas
        item_widgets = []    # Guardar widgets para cada elemento
        quality_vars = []    # Variables para calificaciones
        
        # Función para mostrar el elemento actual
        def show_current_item():
            # Ocultar todos los elementos
            for widgets in item_widgets:
                for widget in widgets:
                    widget.pack_forget()
            
            # Mostrar solo el elemento actual
            if 0 <= current_index[0] < len(item_widgets):
                for widget in item_widgets[current_index[0]]:
                    widget.pack(fill=tk.X, pady=2)
                
                # Actualizar contador
                counter_label.config(text=f"Palabra {current_index[0]+1} de {len(review_items)}")
        
        # Crear widgets para cada elemento
        for i, item in enumerate(review_items):
            # Contenedor para este elemento
            item_frame = tk.Frame(review_container, bg=ENTRY_BG, padx=10, pady=10)
            
            # Palabra
            word_label = tk.Label(
                item_frame,
                text=item.word.upper(),
                font=(FONT_FAMILY, 16, "bold"),
                fg=HIGHLIGHT_COLOR,
                bg=ENTRY_BG
            )
            
            # Definición
            definition_label = tk.Label(
                item_frame,
                text=f"Definición: {item.definition}",
                font=(FONT_FAMILY, 12),
                fg=TEXT_COLOR,
                bg=ENTRY_BG,
                wraplength=550,
                justify=tk.LEFT
            )
            
            # Ejemplo
            example_label = tk.Label(
                item_frame,
                text=f"Ejemplo: {item.example}",
                font=(FONT_FAMILY, 11, "italic"),
                fg=TEXT_COLOR,
                bg=ENTRY_BG,
                wraplength=550,
                justify=tk.LEFT
            )
            
            # Información de repaso
            review_info = tk.Label(
                item_frame,
                text=f"Nivel de dominio: {item.repetition_number} | " +
                     f"Última revisión: {item.last_review_date or 'Nunca'}",
                font=(FONT_FAMILY, 9),
                fg="#AAAAAA",
                bg=ENTRY_BG
            )
            
            # Frame para calificación
            rating_frame = tk.Frame(item_frame, bg=ENTRY_BG)
            
            # Variable para la calificación
            quality_var = tk.IntVar(value=3)  # Valor por defecto
            quality_vars.append(quality_var)
            
            # Botones de calificación
            for q in range(6):  # 0-5
                btn = tk.Button(
                    rating_frame,
                    text=str(q),
                    width=2,
                    bg=BUTTON_BG,
                    fg=TEXT_COLOR,
                    activebackground="#333333",
                    activeforeground=TEXT_COLOR,
                    relief="flat",
                    command=lambda q=q, var=quality_var: var.set(q)
                )
                btn.pack(side=tk.LEFT, padx=2)
            
            # Escuchar pronunciación
            speak_btn = tk.Button(
                item_frame,
                text="[ ESCUCHAR ]",
                font=(FONT_FAMILY, 9),
                bg=BUTTON_BG,
                fg=TEXT_COLOR,
                activebackground="#333333",
                activeforeground=TEXT_COLOR,
                relief="flat",
                command=lambda w=item.word: self.text_to_speech(w)
            )
            speak_btn.pack(pady=5)
            
            # Guardar widgets para este elemento
            item_widgets.append([item_frame, word_label, definition_label, 
                                example_label, review_info, rating_frame, speak_btn])
        
        # Panel de navegación
        nav_frame = tk.Frame(vocab_window, bg=BG_COLOR)
        nav_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Contador de palabras
        counter_label = tk.Label(
            nav_frame,
            text=f"Palabra 1 de {len(review_items)}",
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        counter_label.pack(side=tk.TOP, pady=5)
        
        # Botones de navegación
        button_frame = tk.Frame(nav_frame, bg=BG_COLOR)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Botón anterior
        prev_btn = tk.Button(
            button_frame,
            text="[ ANTERIOR ]",
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            activebackground="#333333",
            activeforeground=TEXT_COLOR,
            relief="flat",
            state=tk.DISABLED,
            command=lambda: (
                setattr(current_index, 0, max(0, current_index[0] - 1)),
                show_current_item(),
                next_btn.config(state=tk.NORMAL),
                prev_btn.config(state=tk.DISABLED if current_index[0] == 0 else tk.NORMAL)
            )
        )
        prev_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón siguiente
        next_btn = tk.Button(
            button_frame,
            text="[ SIGUIENTE ]",
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            activebackground="#333333",
            activeforeground=TEXT_COLOR,
            relief="flat",
            command=lambda: (
                setattr(current_index, 0, min(len(review_items) - 1, current_index[0] + 1)),
                show_current_item(),
                prev_btn.config(state=tk.NORMAL),
                next_btn.config(state=tk.DISABLED if current_index[0] == len(review_items) - 1 else tk.NORMAL)
            )
        )
        next_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón finalizar
        finish_btn = tk.Button(
            button_frame,
            text="[ FINALIZAR REPASO ]",
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            activebackground="#333333",
            activeforeground=TEXT_COLOR,
            relief="flat",
            command=lambda: self.finish_vocab_review(vocab_window, review_items, quality_vars)
        )
        finish_btn.pack(side=tk.RIGHT, padx=5)
        
        # Mostrar el primer elemento
        show_current_item()
    
    def finish_vocab_review(self, window, items, quality_vars):
        """Finaliza el repaso de vocabulario y actualiza las programaciones"""
        # Actualizar cada elemento con su calificación
        for i, item in enumerate(items):
            if i < len(quality_vars):
                quality = quality_vars[i].get()
                item.update_review_schedule(quality)
        
        # Guardar cambios
        self.vocab_manager.save_vocabulary()
        
        # Actualizar contador de pendientes
        self.update_vocab_due_count()
        
        # Cerrar ventana
        window.destroy()
        
        # Mostrar mensaje de confirmación
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "[Repaso de vocabulario completado. Programación de repaso actualizada.]\n\n", "system")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)
    
    def save_conversation(self):
        """Guarda la conversación en un archivo"""
        # Obtener el contenido completo de la conversación
        self.chat_area.config(state=tk.NORMAL)
        conversation_text = self.chat_area.get(1.0, tk.END)
        
        # Solicitar ubicación para guardar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar conversación"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(conversation_text)
                
                # Mostrar mensaje de éxito
                self.chat_area.insert(tk.END, f"[Conversación guardada en {file_path}]\n", "system")
            except Exception as e:
                # Mostrar error
                self.chat_area.insert(tk.END, f"[Error al guardar: {e}]\n", "error")
        
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)
    
    def export_vocabulary(self):
        """Exporta la lista de vocabulario"""
        # Obtener todos los elementos de vocabulario
        items = list(self.vocab_manager.vocabulary_items.values())
        
        if not items:
            # Mostrar mensaje si no hay elementos
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, "[No hay elementos de vocabulario para exportar.]\n", "system")
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.yview(tk.END)
            return
        
        # Solicitar ubicación para guardar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx"), ("Texto", "*.txt")],
            title="Exportar vocabulario"
        )
        
        if not file_path:
            return
            
        try:
            # Exportar según la extensión
            ext = file_path.split(".")[-1].lower()
            
            if ext == "csv":
                # Exportar como CSV
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Palabra,Definición,Ejemplo,Fecha de adición,Etiquetas,Nivel de dominio\n")
                    for item in items:
                        tags = ";".join(item.tags)
                        f.write(f'"{item.word}","{item.definition}","{item.example}",' +
                                f'"{item.date_added.strftime("%Y-%m-%d")}","{tags}",{item.repetition_number}\n')
            
            elif ext == "xlsx":
                # Aquí se implementaría la exportación a Excel
                # Requiere la biblioteca openpyxl o similar
                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(tk.END, "[Exportación a Excel: Función no implementada aún.]\n", "system")
                self.chat_area.config(state=tk.DISABLED)
                self.chat_area.yview(tk.END)
                return
            
            else:
                # Exportar como texto plano
                with open(file_path, "w", encoding="utf-8") as f:
                    for item in items:
                        f.write(f"PALABRA: {item.word}\n")
                        f.write(f"DEFINICIÓN: {item.definition}\n")
                        f.write(f"EJEMPLO: {item.example}\n")
                        f.write(f"AÑADIDO: {item.date_added.strftime('%Y-%m-%d')}\n")
                        f.write(f"ETIQUETAS: {', '.join(item.tags)}\n")
                        f.write(f"NIVEL: {item.repetition_number}\n")
                        f.write("-" * 50 + "\n\n")
            
            # Mostrar mensaje de éxito
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"[Vocabulario exportado a {file_path}]\n", "system")
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.yview(tk.END)
            
        except Exception as e:
            # Mostrar error
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"[Error al exportar: {e}]\n", "error")
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.yview(tk.END)
    
    def grammar_check_mode(self):
        """Activa el modo de revisión gramatical"""
        # Establecer enfoque en revisión gramatical
        self.mode_var.set("Tiempos Verbales")
        
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "[Modo de revisión gramatical activado - enfoque en tiempos verbales y reglas gramaticales]\n", "system")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)
    
    def conversation_mode(self):
        """Activa el modo de conversación libre"""
        # Establecer enfoque en conversación libre
        self.mode_var.set("General")
        
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "[Modo de conversación libre activado - practica discusiones naturales]\n", "system")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)
    
    def vocabulary_mode(self):
        """Activa el modo de construcción de vocabulario"""
        # Establecer enfoque en construcción de vocabulario
        self.mode_var.set("Vocabulario")
        
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "[Modo de construcción de vocabulario activado - enfoque en aprender nuevas palabras y expresiones]\n", "system")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)
    
    def pronunciation_mode(self):
        """Activa el modo de práctica de pronunciación"""
        # Establecer enfoque en pronunciación
        self.mode_var.set("Pronunciación")
        
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "[Modo de práctica de pronunciación activado - habla en inglés y recibe retroalimentación]\n", "system")
        self.chat_area.insert(tk.END, "Presiona el botón [ACTIVAR VOZ] o F2 para comenzar a hablar.\n", "system")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        # Ventana de información
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de English AI Terminal")
        about_window.geometry("500x400")
        about_window.configure(bg=BG_COLOR)
        
        # Hacer ventana modal
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Contenido
        tk.Label(
            about_window,
            text="English AI Terminal v3.0",
            font=(FONT_FAMILY, 14, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR
        ).pack(pady=10)
        
        tk.Label(
            about_window,
            text="Un asistente de aprendizaje de inglés potenciado por IA\nutilizando modelos de lenguaje locales con Ollama.",
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            justify=tk.CENTER
        ).pack(pady=10)
        
        tk.Label(
            about_window,
            text="Características incluidas:",
            font=(FONT_FAMILY, 12, "bold"),
            fg=HIGHLIGHT_COLOR,
            bg=BG_COLOR
        ).pack(pady=5)
        
        features = [
            "• Corrección gramatical y mejora de expresiones",
            "• Construcción y repaso de vocabulario con repetición espaciada",
            "• Reconocimiento y síntesis de voz para práctica oral",
            "• Conversación natural para práctica del idioma",
            "• Seguimiento de progreso y estadísticas de aprendizaje",
            "• Múltiples modos de aprendizaje y temas personalizables"
        ]
        
        for feature in features:
            tk.Label(
                about_window,
                text=feature,
                font=(FONT_FAMILY, 9),
                fg=TEXT_COLOR,
                bg=BG_COLOR,
                justify=tk.LEFT
            ).pack(anchor="w", padx=50)
        
        # Botón cerrar
        tk.Button(
            about_window,
            text="[ CERRAR ]",
            command=about_window.destroy,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            relief="flat",
            padx=10,
            pady=5
        ).pack(pady=20)
    
    def show_tips(self):
        """Muestra consejos de uso"""
        # Ventana de consejos
        tips_window = tk.Toplevel(self.root)
        tips_window.title("Consejos de Uso")
        tips_window.geometry("600x500")
        tips_window.configure(bg=BG_COLOR)
        
        # Hacer ventana modal
        tips_window.transient(self.root)
        tips_window.grab_set()
        
        # Contenido
        tk.Label(
            tips_window,
            text="Consejos para Mejorar tu Aprendizaje",
            font=(FONT_FAMILY, 14, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR
        ).pack(pady=10)
        
        tips_text = scrolledtext.ScrolledText(
            tips_window,
            font=(FONT_FAMILY, FONT_SIZE),
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            relief="flat",
            height=18
        )
        tips_text.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Insertar consejos
        tips = [
            "1. Practica regularmente - El aprendizaje de idiomas requiere consistencia",
            "2. Utiliza el reconocimiento de voz para mejorar tu pronunciación",
            "3. Revisa tu vocabulario diariamente con el sistema de repetición espaciada",
            "4. Presta atención a las correcciones gramaticales destacadas en dorado",
            "5. Usa el botón 'SUGERIR TEMA' si no estás seguro de qué hablar",
            "6. Prueba diferentes modos de aprendizaje según tus necesidades",
            "7. Cambia el nivel de dificultad a medida que mejores",
            "8. Exporta tu vocabulario para estudiar offline",
            "9. Guarda conversaciones interesantes para referencia futura",
            "10. Utiliza el modo de pronunciación para practicar hablando",
            "11. Revisa tus estadísticas de aprendizaje para trackear tu progreso",
            "12. Personaliza el tema de la aplicación para reducir fatiga visual",
            "13. Escucha la pronunciación correcta de palabras nuevas",
            "14. Intenta escribir párrafos completos para practicar la coherencia",
            "15. No tengas miedo de cometer errores - son parte del aprendizaje"
        ]
        
        for tip in tips:
            tips_text.insert(tk.END, f"{tip}\n\n", "correction")
        
        tips_text.config(state=tk.DISABLED)
        
        # Botón cerrar
        tk.Button(
            tips_window,
            text="[ CERRAR ]",
            command=tips_window.destroy,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            relief="flat",
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def show_keyboard_shortcuts(self):
        """Muestra los atajos de teclado disponibles"""
        # Ventana de atajos
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Atajos de Teclado")
        shortcuts_window.geometry("400x300")
        shortcuts_window.configure(bg=BG_COLOR)
        
        # Hacer ventana modal
        shortcuts_window.transient(self.root)
        shortcuts_window.grab_set()
        
        # Contenido
        tk.Label(
            shortcuts_window,
            text="Atajos de Teclado",
            font=(FONT_FAMILY, 14, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR
        ).pack(pady=10)
        
        shortcuts = [
            ("F2", "Activar/Desactivar reconocimiento de voz"),
            ("Enter", "Enviar mensaje"),
            ("Ctrl+S", "Guardar conversación"),
            ("Ctrl+R", "Reiniciar chat"),
            ("Ctrl+V", "Abrir revisión de vocabulario"),
            ("Ctrl+G", "Modo de revisión gramatical"),
            ("Ctrl+P", "Modo de pronunciación"),
            ("Esc", "Cancelar operación actual")
        ]
        
        # Crear tabla de atajos
        for key, description in shortcuts:
            frame = tk.Frame(shortcuts_window, bg=BG_COLOR)
            frame.pack(fill=tk.X, padx=20, pady=2)
            
            tk.Label(
                frame,
                text=key,
                font=(FONT_FAMILY, 10, "bold"),
                fg=HIGHLIGHT_COLOR,
                bg=BG_COLOR,
                width=10,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            tk.Label(
                frame,
                text=description,
                font=(FONT_FAMILY, 10),
                fg=TEXT_COLOR,
                bg=BG_COLOR,
                anchor="w"
            ).pack(side=tk.LEFT, padx=10)
        
        # Botón cerrar
        tk.Button(
            shortcuts_window,
            text="[ CERRAR ]",
            command=shortcuts_window.destroy,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            relief="flat",
            padx=10,
            pady=5
        ).pack(pady=20)
    
    def show_learning_stats(self):
        """Muestra estadísticas de aprendizaje"""
        # Obtener estadísticas
        vocab_stats = self.vocab_manager.get_learning_stats()
        
        # Crear ventana
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estadísticas de Aprendizaje")
        stats_window.geometry("600x500")
        stats_window.configure(bg=BG_COLOR)
        
        # Hacer ventana modal
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Contenido
        tk.Label(
            stats_window,
            text="Estadísticas de Aprendizaje",
            font=(FONT_FAMILY, 14, "bold"),
            fg=SYSTEM_COLOR,
            bg=BG_COLOR
        ).pack(pady=10)
        
        # Marco de estadísticas principales
        main_stats_frame = tk.Frame(stats_window, bg=BG_COLOR)
        main_stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Estadísticas generales
        tk.Label(
            main_stats_frame,
            text=f"Total de vocabulario: {vocab_stats['total_items']} palabras",
            font=(FONT_FAMILY, 12),
            fg=HIGHLIGHT_COLOR,
            bg=BG_COLOR
        ).pack(anchor="w")
        
        tk.Label(
            main_stats_frame,
            text=f"Pendientes para repaso hoy: {vocab_stats['due_items']} palabras",
            font=(FONT_FAMILY, 12),
            fg=HIGHLIGHT_COLOR,
            bg=BG_COLOR
        ).pack(anchor="w")
        
        # Niveles de dominio
        mastery_frame = tk.Frame(stats_window, bg=ENTRY_BG, padx=15, pady=15)
        mastery_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            mastery_frame,
            text="Niveles de Dominio",
            font=(FONT_FAMILY, 12, "bold"),
            fg=TEXT_COLOR,
            bg=ENTRY_BG
        ).pack(anchor="w")
        
        mastery_levels = vocab_stats["mastery_levels"]
        
        # Crear barras para cada nivel
        for level, count in [
            ("Dominado", mastery_levels["mastered"]),
            ("Familiar", mastery_levels["familiar"]),
            ("Aprendiendo", mastery_levels["learning"])
        ]:
            level_frame = tk.Frame(mastery_frame, bg=ENTRY_BG)
            level_frame.pack(fill=tk.X, pady=5)
            
            # Etiqueta
            tk.Label(
                level_frame,
                text=f"{level}:",
                font=(FONT_FAMILY, 10),
                fg=TEXT_COLOR,
                bg=ENTRY_BG,
                width=12,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            # Valor
            tk.Label(
                level_frame,
                text=str(count),
                font=(FONT_FAMILY, 10),
                fg=HIGHLIGHT_COLOR,
                bg=ENTRY_BG,
                width=5
            ).pack(side=tk.LEFT)
            
            # Barra
            total = max(1, vocab_stats["total_items"])  # Evitar división por cero
            percentage = min(100, int((count / total) * 100))
            
            # Colores según nivel
            bar_color = "#00FF00" if level == "Dominado" else \
                        "#FFFF00" if level == "Familiar" else \
                        "#FF6600"
            
            bar_frame = tk.Frame(level_frame, bg="#444444", height=15, width=300)
            bar_frame.pack(side=tk.LEFT, padx=10)
            
            bar = tk.Frame(bar_frame, bg=bar_color, height=15, width=int(300 * percentage / 100))
            bar.place(x=0, y=0)
            
            # Porcentaje
            tk.Label(
                level_frame,
                text=f"{percentage}%",
                font=(FONT_FAMILY, 9),
                fg=TEXT_COLOR,
                bg=ENTRY_BG
            ).pack(side=tk.LEFT, padx=5)
        
        # Próximos repasos
        upcoming_frame = tk.Frame(stats_window, bg=ENTRY_BG, padx=15, pady=15)
        upcoming_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            upcoming_frame,
            text="Próximos Repasos",
            font=(FONT_FAMILY, 12, "bold"),
            fg=TEXT_COLOR,
            bg=ENTRY_BG
        ).pack(anchor="w")
        
        # Crear una entrada para cada periodo
        for days, count in vocab_stats["upcoming_reviews"].items():
            period_frame = tk.Frame(upcoming_frame, bg=ENTRY_BG)
            period_frame.pack(fill=tk.X, pady=2)
            
            period_text = f"Próximos {days} días:" if days > 1 else "Hoy:"
            
            tk.Label(
                period_frame,
                text=period_text,
                font=(FONT_FAMILY, 10),
                fg=TEXT_COLOR,
                bg=ENTRY_BG,
                width=15,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            tk.Label(
                period_frame,
                text=f"{count} palabras",
                font=(FONT_FAMILY, 10),
                fg=HIGHLIGHT_COLOR,
                bg=ENTRY_BG
            ).pack(side=tk.LEFT)
        
        # Botón cerrar
        tk.Button(
            stats_window,
            text="[ CERRAR ]",
            command=stats_window.destroy,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            relief="flat",
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def change_theme(self, theme_name):
        """Cambia el tema de la aplicación"""
        # Definir temas
        themes = {
            "classic": {  # Verde sobre negro (tema actual)
                "bg": "#121212",
                "text": "#33FF33",
                "entry_bg": "#1A1A1A",
                "button_bg": "#222222",
                "highlight": "#00CCFF",
                "system": "#FFD700"
            },
            "hacker": {  # Verde más intenso sobre negro
                "bg": "#000000",
                "text": "#00FF00",
                "entry_bg": "#0A0A0A",
                "button_bg": "#111111",
                "highlight": "#00FF00",
                "system": "#00FF00"
            },
            "cyberpunk": {  # Neón con toques púrpura
                "bg": "#0D001A",
                "text": "#FF00FF",
                "entry_bg": "#1A0033",
                "button_bg": "#330066",
                "highlight": "#00FFFF",
                "system": "#FFFF00"
            },
            "retro": {  # Ámbar sobre negro
                "bg": "#121212",
                "text": "#FFB000",
                "entry_bg": "#1A1A1A",
                "button_bg": "#222222",
                "highlight": "#FFA500",
                "system": "#FFFFFF"
            },
            "dark_blue": {  # Azul sobre negro
                "bg": "#0A0A1A",
                "text": "#4488FF",
                "entry_bg": "#0F0F2A",
                "button_bg": "#1A1A3A",
                "highlight": "#00CCFF",
                "system": "#FFFFFF"
            }
        }
        
        # Verificar si el tema existe
        if theme_name not in themes:
            return
            
        # Obtener configuración del tema
        theme = themes[theme_name]
        
        # Actualizar variables globales de color
        global BG_COLOR, TEXT_COLOR, ENTRY_BG, BUTTON_BG, HIGHLIGHT_COLOR, SYSTEM_COLOR
        BG_COLOR = theme["bg"]
        TEXT_COLOR = theme["text"]
        ENTRY_BG = theme["entry_bg"]
        BUTTON_BG = theme["button_bg"]
        HIGHLIGHT_COLOR = theme["highlight"]
        SYSTEM_COLOR = theme["system"]
        
        # Actualizar colores en la interfaz
        self.root.configure(bg=BG_COLOR)
        self.main_frame.configure(bg=BG_COLOR)
        self.header_frame.configure(bg=BG_COLOR)
        self.title_label.configure(bg=BG_COLOR, fg=SYSTEM_COLOR)
        self.mode_frame.configure(bg=BG_COLOR)
        self.mode_label.configure(bg=BG_COLOR, fg=TEXT_COLOR)
        self.level_label.configure(bg=BG_COLOR, fg=TEXT_COLOR)
        self.status_frame.configure(bg=BG_COLOR)
        
        self.separator.configure(bg=BG_COLOR)
        self.chat_container.configure(bg=BG_COLOR)
        self.chat_area.configure(bg=ENTRY_BG, fg=TEXT_COLOR)
        
        self.progress_frame.configure(bg=BG_COLOR)
        self.progress_label.configure(bg=BG_COLOR, fg=TEXT_COLOR)
        self.stats_label.configure(bg=BG_COLOR, fg=TEXT_COLOR)
        self.vocab_due_label.configure(bg=BG_COLOR, fg=HIGHLIGHT_COLOR)
        
        self.control_frame.configure(bg=BG_COLOR)
        self.processing_label.configure(bg=BG_COLOR)
        
        self.input_frame.configure(bg=BG_COLOR)
        self.prompt_label.configure(bg=BG_COLOR, fg=SYSTEM_COLOR)
        self.user_input.configure(bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        
        # Actualizar botones
        for btn in [self.suggest_button, self.reset_button, self.vocab_button, 
                   self.voice_button, self.send_button]:
            btn.configure(bg=BUTTON_BG, fg=TEXT_COLOR, activebackground="#333333")
        
        # Actualizar etiquetas de texto
        self.chat_area.tag_config("user", foreground=TEXT_COLOR)
        self.chat_area.tag_config("system", foreground=SYSTEM_COLOR)
        self.chat_area.tag_config("ai", foreground=HIGHLIGHT_COLOR)
        
        # Configurar estilo de la barra de progreso
        style = ttk.Style()
        style.configure(
            "TProgressbar",
            troughcolor=ENTRY_BG,
            background=SYSTEM_COLOR,
            thickness=10
        )
        
        # Mostrar mensaje
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"[Tema cambiado a: {theme_name}]\n", "system")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)


def start_app():
    root = tk.Tk()
    app = EnhancedAppWindow(root)
    
    # Habilitar modo oscuro en la barra de título en Windows si es posible
    try:
        from ctypes import windll
        windll.dwmapi.DwmSetWindowAttribute(
            root.winfo_id(), 
            20,  # DWMWA_USE_IMMERSIVE_DARK_MODE
            byref(c_int(1)), 
            sizeof(c_int)
        )
    except:
        pass  # Fallar silenciosamente si no estamos en Windows o si la llamada falla
    
    root.mainloop()
import datetime
import json
import os
import random
from typing import Dict, List, Any

class VocabularyItem:
    def __init__(
        self, 
        word: str, 
        definition: str, 
        example: str, 
        date_added: datetime.datetime = None,
        tags: List[str] = None
    ):
        self.word = word
        self.definition = definition
        self.example = example
        self.date_added = date_added or datetime.datetime.now()
        self.tags = tags or []
        
        # Parámetros para el algoritmo SM-2
        self.easiness_factor = 2.5  # Factor de facilidad (1.3 - 2.5)
        self.repetition_number = 0  # Número de repeticiones exitosas consecutivas
        self.next_review_date = self.date_added.date()  # Próxima fecha de revisión
        self.last_review_date = None  # Última fecha de revisión
        self.interval = 0  # Intervalo en días
    
    def update_review_schedule(self, quality: int) -> None:
        """
        Actualiza el programa de revisión basado en la calidad de la respuesta.
        
        Args:
            quality: Calidad de la respuesta (0-5)
                0: Completamente olvidado
                1: Respuesta incorrecta, pero recordada al verla
                2: Respuesta incorrecta, pero familiar
                3: Respuesta correcta, pero con dificultad
                4: Respuesta correcta con leve duda
                5: Respuesta perfecta
        """
        if quality < 0:
            quality = 0
        if quality > 5:
            quality = 5
            
        # Actualizar el factor de facilidad
        self.easiness_factor = max(1.3, self.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # Registrar la fecha de revisión
        today = datetime.datetime.now().date()
        self.last_review_date = today
        
        if quality < 3:
            # Si la calidad es menos de 3, reiniciar repeticiones
            self.repetition_number = 0
            self.interval = 1
        else:
            # Calcular nuevo intervalo
            if self.repetition_number == 0:
                self.interval = 1
            elif self.repetition_number == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.easiness_factor)
                
            self.repetition_number += 1
        
        # Calcular próxima fecha de revisión
        self.next_review_date = today + datetime.timedelta(days=self.interval)
    
    def is_due_for_review(self) -> bool:
        """
        Verifica si el elemento está pendiente para revisión.
        
        Returns:
            bool: True si el elemento debe ser revisado hoy o antes.
        """
        return datetime.datetime.now().date() >= self.next_review_date
    
    def days_until_review(self) -> int:
        """
        Calcula días hasta la próxima revisión.
        
        Returns:
            int: Número de días hasta la próxima revisión.
        """
        today = datetime.datetime.now().date()
        delta = self.next_review_date - today
        return max(0, delta.days)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto a un diccionario para serialización.
        
        Returns:
            Dict: Representación del objeto como diccionario.
        """
        return {
            "word": self.word,
            "definition": self.definition,
            "example": self.example,
            "date_added": self.date_added.isoformat(),
            "tags": self.tags,
            "easiness_factor": self.easiness_factor,
            "repetition_number": self.repetition_number,
            "next_review_date": self.next_review_date.isoformat(),
            "last_review_date": self.last_review_date.isoformat() if self.last_review_date else None,
            "interval": self.interval
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VocabularyItem':
        """
        Crea un objeto VocabularyItem desde un diccionario.
        
        Args:
            data: Diccionario con datos del elemento de vocabulario.
            
        Returns:
            VocabularyItem: Nuevo objeto.
        """
        item = cls(
            word=data["word"],
            definition=data["definition"],
            example=data["example"],
            date_added=datetime.datetime.fromisoformat(data["date_added"]),
            tags=data.get("tags", [])
        )
        
        item.easiness_factor = data.get("easiness_factor", 2.5)
        item.repetition_number = data.get("repetition_number", 0)
        item.next_review_date = datetime.date.fromisoformat(data["next_review_date"])
        
        if data.get("last_review_date"):
            item.last_review_date = datetime.date.fromisoformat(data["last_review_date"])
            
        item.interval = data.get("interval", 0)
        
        return item


class VocabularyManager:
    def __init__(self, storage_file: str = "data/vocabulary.json"):
        self.storage_file = storage_file
        self.vocabulary_items: Dict[str, VocabularyItem] = {}
        self.load_vocabulary()
    
    def load_vocabulary(self) -> None:
        """Carga el vocabulario desde el archivo de almacenamiento"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                for item_data in data:
                    item = VocabularyItem.from_dict(item_data)
                    self.vocabulary_items[item.word] = item
            else:
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        except Exception as e:
            print(f"Error al cargar vocabulario: {e}")
    
    def save_vocabulary(self) -> None:
        """Guarda el vocabulario en el archivo de almacenamiento"""
        try:
            data = [item.to_dict() for item in self.vocabulary_items.values()]
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error al guardar vocabulario: {e}")
    
    def add_vocabulary_item(self, word: str, definition: str, example: str, tags: List[str] = None) -> VocabularyItem:
        """
        Añade un nuevo elemento de vocabulario.
        
        Args:
            word: Palabra o frase
            definition: Definición
            example: Ejemplo de uso
            tags: Etiquetas para categorización
        
        Returns:
            VocabularyItem: El elemento añadido
        """
        word = word.lower().strip()
        
        # Actualizar si ya existe
        if word in self.vocabulary_items:
            item = self.vocabulary_items[word]
            item.definition = definition
            item.example = example
            if tags:
                item.tags = tags
        else:
            # Crear nuevo elemento
            item = VocabularyItem(word, definition, example, tags=tags)
            self.vocabulary_items[word] = item
        
        self.save_vocabulary()
        return item
    
    def get_vocabulary_item(self, word: str) -> VocabularyItem:
        """
        Obtiene un elemento de vocabulario por palabra.
        
        Args:
            word: Palabra a buscar
        
        Returns:
            VocabularyItem: El elemento encontrado o None
        """
        return self.vocabulary_items.get(word.lower().strip())
    
    def get_due_for_review(self, limit: int = None) -> List[VocabularyItem]:
        """
        Obtiene elementos pendientes para revisión.
        
        Args:
            limit: Número máximo de elementos a devolver
        
        Returns:
            List[VocabularyItem]: Lista de elementos pendientes
        """
        due_items = [
            item for item in self.vocabulary_items.values()
            if item.is_due_for_review()
        ]
        
        # Ordenar por prioridad: primero los que llevan más tiempo pendientes
        due_items.sort(key=lambda x: x.next_review_date)
        
        if limit is not None and limit > 0:
            return due_items[:limit]
        return due_items
    
    def get_items_by_tag(self, tag: str) -> List[VocabularyItem]:
        """
        Obtiene elementos por etiqueta.
        
        Args:
            tag: Etiqueta a buscar
        
        Returns:
            List[VocabularyItem]: Lista de elementos con la etiqueta
        """
        return [
            item for item in self.vocabulary_items.values()
            if tag in item.tags
        ]
    
    def remove_vocabulary_item(self, word: str) -> bool:
        """
        Elimina un elemento de vocabulario.
        
        Args:
            word: Palabra a eliminar
        
        Returns:
            bool: True si se eliminó correctamente
        """
        word = word.lower().strip()
        if word in self.vocabulary_items:
            del self.vocabulary_items[word]
            self.save_vocabulary()
            return True
        return False
    
    def get_review_session(self, n: int = 10) -> List[VocabularyItem]:
        """
        Obtiene una sesión de revisión.
        
        Args:
            n: Número de elementos para la sesión
        
        Returns:
            List[VocabularyItem]: Lista de elementos para revisar
        """
        # Primero obtener elementos pendientes
        due_items = self.get_due_for_review()
        
        # Si no hay suficientes, añadir elementos aleatorios
        if len(due_items) < n:
            available_items = [
                item for item in self.vocabulary_items.values()
                if item not in due_items
            ]
            random.shuffle(available_items)
            additional_items = available_items[:n - len(due_items)]
            review_items = due_items + additional_items
        else:
            review_items = due_items[:n]
        
        random.shuffle(review_items)
        return review_items
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de aprendizaje.
        
        Returns:
            Dict: Estadísticas del vocabulario
        """
        today = datetime.datetime.now().date()
        
        # Contar elementos por estado
        total_items = len(self.vocabulary_items)
        due_items = len(self.get_due_for_review())
        
        # Contar por nivel de dominio
        mastered = sum(1 for item in self.vocabulary_items.values() 
                    if item.repetition_number >= 3 and item.easiness_factor >= 2.0)
        familiar = sum(1 for item in self.vocabulary_items.values() 
                     if item.repetition_number >= 1 and item.repetition_number < 3)
        learning = total_items - mastered - familiar
        
        # Contar por etiquetas
        tag_counts = {}
        for item in self.vocabulary_items.values():
            for tag in item.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Calcular elementos para los próximos días
        upcoming_reviews = {1: 0, 3: 0, 7: 0, 14: 0, 30: 0}
        for item in self.vocabulary_items.values():
            days = item.days_until_review()
            if days <= 1:
                upcoming_reviews[1] += 1
            if days <= 3:
                upcoming_reviews[3] += 1
            if days <= 7:
                upcoming_reviews[7] += 1
            if days <= 14:
                upcoming_reviews[14] += 1
            if days <= 30:
                upcoming_reviews[30] += 1
        
        return {
            "total_items": total_items,
            "due_items": due_items,
            "mastery_levels": {
                "mastered": mastered,
                "familiar": familiar,
                "learning": learning
            },
            "tag_distribution": tag_counts,
            "upcoming_reviews": upcoming_reviews
        }
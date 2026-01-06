import tkinter as tk
from tkinter import ttk
from datetime import datetime

class ReportHeader(ttk.Frame):
    """Encabezado de reporte con título, entidad y fecha"""
    
    def __init__(self, parent, title="", entity="Gerencia Administrativa"):
        super().__init__(parent)
        self.title = title
        self.entity = entity
        self._create_widgets()
    
    def _create_widgets(self):
        # Título del reporte
        self.title_label = ttk.Label(
            self, 
            text=self.title, 
            font=('Arial', 14, 'bold')
        )
        self.title_label.grid(row=0, column=0, sticky='w', padx=5, pady=2)
        
        # Entidad
        self.entity_label = ttk.Label(
            self, 
            text=f"Entidad: {self.entity}",
            font=('Arial', 10)
        )
        self.entity_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
        
        # Fecha y hora de generación
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.time_label = ttk.Label(
            self, 
            text=f"Generado: {current_time}",
            font=('Arial', 9, 'italic')
        )
        self.time_label.grid(row=2, column=0, sticky='w', padx=5, pady=2)
    
    def update_title(self, new_title):
        """Actualiza el título del reporte"""
        self.title_label.config(text=new_title)
        self.title = new_title
    
    def update_time(self):
        """Actualiza la fecha/hora de generación"""
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.time_label.config(text=f"Generado: {current_time}")
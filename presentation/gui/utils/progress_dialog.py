import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

class ProgressDialog(tk.Toplevel):
    """Diálogo modal para mostrar progreso de operaciones largas"""
    
    def __init__(self, parent: tk.Tk, title: str = "Procesando...", 
                 message: str = "Por favor espere"):
        super().__init__(parent)
        
        self.parent = parent
        self.title(title)
        self.transient(parent)
        self.grab_set()
        
        # Configurar ventana
        self.geometry("400x150")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._do_nothing)
        
        # Centrar en pantalla
        self._center_on_parent()
        
        # Variables
        self.is_running = True
        
        # Crear widgets
        self._create_widgets(message)
        
        # Variables para seguimiento
        self.current_progress = 0
        self.current_message = message
        self.current_detail = ""
        
        # Iniciar actualizaciones periódicas
        self._update_display()
    
    def _center_on_parent(self):
        """Centra la ventana sobre su padre"""
        self.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (self.winfo_width() // 2)
        y = parent_y + (parent_height // 2) - (self.winfo_height() // 2)
        
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self, initial_message: str):
        """Crea los widgets de la ventana de progreso"""
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje principal
        self.message_label = ttk.Label(
            main_frame, 
            text=initial_message,
            font=('Arial', 11),
            wraplength=350
        )
        self.message_label.pack(pady=(0, 10))
        
        # Barra de progreso determinada
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=350,
            maximum=100
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Contador de progreso
        self.progress_label = ttk.Label(
            main_frame,
            text="0%",
            font=('Arial', 10),
            foreground='#2c3e50'
        )
        self.progress_label.pack(pady=(0, 5))
        
        # Etiqueta de detalle
        self.detail_label = ttk.Label(
            main_frame,
            text="",
            font=('Arial', 9),
            foreground='#7f8c8d'
        )
        self.detail_label.pack()
    
    def _update_display(self):
        """Actualiza periódicamente la pantalla"""
        if self.is_running:
            # Solo actualiza la barra y etiquetas
            self.progress_bar['value'] = self.current_progress
            self.progress_label.config(text=f"{int(self.current_progress)}%")
            self.message_label.config(text=self.current_message)
            self.detail_label.config(text=self.current_detail)
            
            # Programa la próxima actualización
            self.after(100, self._update_display)
    
    def update_progress(self, progress: int, message: str = "", detail: str = ""):
        """Actualiza el progreso actual (llamar desde el hilo principal)"""
        self.current_progress = min(100, max(0, progress))
        if message:
            self.current_message = message
        if detail:
            self.current_detail = detail
    
    def run_task(self, task_func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta una tarea larga en un hilo separado y muestra progreso
        """
        result = None
        exception = None
        
        def task_wrapper():
            nonlocal result, exception
            try:
                result = task_func(self.update_progress, *args, **kwargs)
            except Exception as e:
                exception = e
            finally:
                self.is_running = False
                self.after(0, self.destroy)
        
        # Iniciar tarea en hilo separado
        thread = threading.Thread(target=task_wrapper, daemon=True)
        thread.start()
        
        # Mostrar ventana modal
        self.wait_window()
        
        # Verificar si hubo excepción
        if exception:
            raise exception
        
        return result
    
    def _do_nothing(self):
        """No hacer nada al intentar cerrar la ventana"""
        pass


def show_progress_dialog(parent: tk.Tk, task_func: Callable, 
                        task_name: str = "Operación", 
                        *args, **kwargs) -> Any:
    """
    Función de conveniencia para mostrar diálogo de progreso
    """
    dialog = ProgressDialog(parent, f"{task_name}...", f"Iniciando {task_name.lower()}...")
    
    try:
        return dialog.run_task(task_func, *args, **kwargs)
    except Exception as e:
        dialog.destroy()
        raise e
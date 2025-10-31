import tkinter as tk

class WindowUtils:
    """Utilidades para manejo de ventanas y centrado"""
    
    @staticmethod
    def center_window(window, parent=None):
        """
        Centra una ventana con respecto a su ventana padre o en la pantalla
        
        Args:
            window: Ventana a centrar
            parent: Ventana padre (si es None, se centra en la pantalla)
        """
        window.update_idletasks()
        
        if parent is None:
            # Centrar en pantalla
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - window.winfo_width()) // 2
            y = (screen_height - window.winfo_height()) // 2
        else:
            # Centrar respecto a la ventana padre
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            
            x = parent_x + (parent_width - window.winfo_width()) // 2
            y = parent_y + (parent_height - window.winfo_height()) // 2
        
        # Asegurar que la ventana no se salga de la pantalla
        x = max(0, min(x, window.winfo_screenwidth() - window.winfo_width()))
        y = max(0, min(y, window.winfo_screenheight() - window.winfo_height()))
        
        window.geometry(f"+{x}+{y}")
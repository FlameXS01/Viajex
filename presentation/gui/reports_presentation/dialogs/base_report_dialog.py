"""
base_report_dialog.py
Clase base para todos los diálogos de reportes del sistema VIAJEX.
Proporciona funcionalidad común y estructura estandarizada.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable
import logging


class BaseReportDialog(tk.Toplevel):
    """Clase base abstracta para diálogos de configuración de reportes"""
    
    def __init__(self, parent, title: str = "Configurar Reporte", 
                 width: int = 400, height: int = 300):
        """
        Inicializa el diálogo base.
        
        Args:
            parent: Ventana padre
            title: Título del diálogo
            width: Ancho del diálogo
            height: Alto del diálogo
        """
        super().__init__(parent)
        
        # Configuración básica
        self.title(title)
        self.result: Optional[Dict[str, Any]] = None
        self.parent = parent
        
        # Configurar tamaño y posición
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        
        # Establecer ícono (si está disponible)
        try:
            self.iconbitmap('icon.ico')
        except:
            pass
        
        # Variables para validación
        self.validation_errors = []
        
        # Crear widgets
        self._create_widgets()
        
        # Centrar en pantalla
        self._center_on_screen()
        
        # Enfocar esta ventana
        self.focus_set()
        
        # Bind de teclas
        self.bind('<Escape>', lambda e: self._on_cancel())
        self.bind('<Return>', lambda e: self._on_accept())
        
        # Configurar protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _create_widgets(self) -> None:
        """Método abstracto para crear widgets. Debe ser implementado por subclases."""
        # Frame principal con padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar pesos de filas/columnas
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Label por defecto (subclases deben sobreescribir)
        ttk.Label(
            main_frame, 
            text="Este diálogo debe ser implementado por una subclase",
            font=('Arial', 10, 'italic')
        ).grid(row=0, column=0, padx=10, pady=10)
        
        # Frame para botones (común a todos los diálogos)
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        
        # Botones estándar
        self.accept_button = ttk.Button(
            self.button_frame, 
            text="Aceptar", 
            command=self._on_accept,
            width=10
        )
        self.accept_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.cancel_button = ttk.Button(
            self.button_frame, 
            text="Cancelar", 
            command=self._on_cancel,
            width=10
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Configurar expansión del frame de botones
        self.button_frame.columnconfigure(0, weight=1)
    
    def _center_on_screen(self) -> None:
        """Centra el diálogo en la pantalla."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Obtener dimensiones de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calcular posición
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _on_accept(self) -> None:
        """
        Maneja el evento de aceptación.
        Valida los datos y cierra el diálogo con resultado.
        """
        if self._validate():
            self.result = self._get_result_data()
            self.destroy()
    
    def _on_cancel(self) -> None:
        """Maneja el evento de cancelación."""
        self.result = None
        self.destroy()
    
    def _validate(self) -> bool:
        """
        Valida los datos del formulario.
        
        Returns:
            bool: True si los datos son válidos, False en caso contrario
        """
        self.validation_errors = []
        
        # Validación base (puede ser extendida por subclases)
        if not self._validate_required_fields():
            return False
        
        # Validaciones específicas de subclase
        self._custom_validate()
        
        if self.validation_errors:
            self._show_validation_errors()
            return False
        
        return True
    
    def _validate_required_fields(self) -> bool:
        """
        Valida campos requeridos genéricos.
        Debe ser extendido por subclases para campos específicos.
        """
        return True
    
    def _custom_validate(self) -> None:
        """
        Método para validaciones personalizadas.
        Las subclases deben sobreescribir este método para agregar validaciones específicas.
        """
        pass
    
    def _get_result_data(self) -> Dict[str, Any]:
        """
        Obtiene los datos del formulario para retornar como resultado.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos del formulario
        """
        # Este método debe ser implementado por subclases
        return {}
    
    def _show_validation_errors(self) -> None:
        """Muestra los errores de validación al usuario."""
        error_message = "Se encontraron los siguientes errores:\n\n"
        error_message += "\n".join(f"• {error}" for error in self.validation_errors)
        
        messagebox.showerror(
            "Errores de Validación",
            error_message,
            parent=self
        )
    
    def _add_validation_error(self, error_message: str) -> None:
        """Agrega un mensaje de error a la lista de errores de validación."""
        self.validation_errors.append(error_message)
    
    def show(self) -> Optional[Dict[str, Any]]:
        """
        Muestra el diálogo modalmente y espera resultado.
        
        Returns:
            Optional[Dict[str, Any]]: Diccionario con resultados o None si se canceló
        """
        self.wait_window(self)
        return self.result
    
    def _create_labeled_widget(self, parent, label_text: str, widget_class, 
                              row: int, column: int = 0, **widget_kwargs) -> Any:
        """
        Crea un widget con su etiqueta en una grilla.
        
        Args:
            parent: Widget padre
            label_text: Texto de la etiqueta
            widget_class: Clase del widget a crear
            row: Fila en la grilla
            column: Columna en la grilla
            **widget_kwargs: Argumentos para el widget
            
        Returns:
            El widget creado
        """
        # Etiqueta
        ttk.Label(parent, text=label_text + ":").grid(
            row=row, column=column, sticky="w", padx=(0, 10), pady=5
        )
        
        # Widget
        widget = widget_class(parent, **widget_kwargs)
        widget.grid(row=row, column=column + 1, sticky="ew", padx=(0, 0), pady=5)
        
        return widget
    
    def _create_section(self, parent, title: str, row: int) -> ttk.Frame:
        """
        Crea una sección con título para agrupar widgets relacionados.
        
        Args:
            parent: Widget padre
            title: Título de la sección
            row: Fila en la grilla
            
        Returns:
            ttk.Frame: Frame de la sección
        """
        # Frame con borde
        section_frame = ttk.LabelFrame(parent, text=title, padding="10")
        section_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10, 5))
        
        # Configurar expansión
        section_frame.columnconfigure(1, weight=1)
        
        return section_frame
    
    def _create_button(self, parent, text: str, command: Callable, 
                      style: str = None, width: int = None) -> ttk.Button:
        """
        Crea un botón con estilo consistente.
        
        Args:
            parent: Widget padre
            text: Texto del botón
            command: Función a ejecutar al hacer clic
            style: Estilo del botón (opcional)
            width: Ancho del botón (opcional)
            
        Returns:
            ttk.Button: Botón creado
        """
        kwargs = {
            'text': text,
            'command': command
        }
        
        if style:
            kwargs['style'] = style
        
        if width:
            kwargs['width'] = width
        
        return ttk.Button(parent, **kwargs)


# Ejemplo de uso para debugging
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Crear instancia del diálogo base
    dialog = BaseReportDialog(root, "Diálogo de Ejemplo")
    result = dialog.show()
    
    if result:
        print("Resultado:", result)
    else:
        print("Diálogo cancelado")
    
    root.destroy()
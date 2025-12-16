"""
export_options_dialog.py
Diálogo para configurar opciones de exportación de reportes.
Proporciona opciones para exportar reportes en diferentes formatos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog


class ExportOptionsDialog(BaseReportDialog):
    """Diálogo para configurar opciones de exportación"""
    
    def __init__(self, parent, 
                 report_name: str = "Reporte",
                 available_formats: Optional[List[str]] = None,
                 default_filename: Optional[str] = None):
        """
        Inicializa el diálogo de opciones de exportación.
        
        Args:
            parent: Ventana padre
            report_name: Nombre del reporte a exportar
            available_formats: Formatos disponibles para exportación
            default_filename: Nombre de archivo por defecto
        """
        self.report_name = report_name
        self.available_formats = available_formats or [
            "Excel (.xlsx)",
            "PDF (.pdf)",
            "CSV (.csv)",
            "HTML (.html)",
            "Texto (.txt)",
            "JSON (.json)",
            "XML (.xml)",
            "Imagen (.png)"
        ]
        
        self.default_filename = default_filename or f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        super().__init__(parent, f"Exportar {report_name}", width=550, height=550)
    
    def _create_widgets(self) -> None:
        """Crea los widgets del diálogo."""
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar expansión
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título descriptivo
        ttk.Label(
            main_frame,
            text=f"Configurar Exportación: {self.report_name}",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Sección de formato de exportación
        format_frame = self._create_section(main_frame, "Formato de Exportación", 1)
        
        # Selección de formato
        ttk.Label(format_frame, text="Formato de salida:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.format_var = tk.StringVar(value=self.available_formats[0])
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=self.available_formats,
            state='readonly',
            width=25
        )
        format_combo.grid(row=0, column=1, sticky="w", pady=10)
        format_combo.bind('<<ComboboxSelected>>', self._on_format_change)
        
        # Opciones específicas del formato
        self.format_options_frame = ttk.Frame(format_frame)
        self.format_options_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Inicializar opciones de formato
        self._create_format_options()
        
        # Sección de nombre y ubicación
        file_frame = self._create_section(main_frame, "Nombre y Ubicación del Archivo", 2)
        
        # Nombre del archivo
        ttk.Label(file_frame, text="Nombre del archivo:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.filename_var = tk.StringVar(value=self.default_filename)
        filename_entry = ttk.Entry(
            file_frame,
            textvariable=self.filename_var,
            width=40
        )
        filename_entry.grid(row=0, column=1, sticky="w", pady=10)
        
        # Botón para seleccionar ubicación
        ttk.Label(file_frame, text="Guardar en:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        location_frame = ttk.Frame(file_frame)
        location_frame.grid(row=1, column=1, sticky="ew", pady=10)
        
        self.location_var = tk.StringVar(value="Documentos")
        ttk.Entry(
            location_frame,
            textvariable=self.location_var,
            state='readonly',
            width=35
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            location_frame,
            text="📁",
            command=self._select_location,
            width=3
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Opciones de nombre de archivo
        ttk.Label(file_frame, text="Opciones de nombre:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        name_options_frame = ttk.Frame(file_frame)
        name_options_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        self.include_date_var = tk.BooleanVar(value=True)
        self.include_time_var = tk.BooleanVar(value=True)
        self.include_user_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(
            name_options_frame,
            text="Incluir fecha",
            variable=self.include_date_var,
            command=self._update_filename_preview
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            name_options_frame,
            text="Incluir hora",
            variable=self.include_time_var,
            command=self._update_filename_preview
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            name_options_frame,
            text="Incluir usuario",
            variable=self.include_user_var,
            command=self._update_filename_preview
        ).pack(side=tk.LEFT)
        
        # Vista previa del nombre
        ttk.Label(file_frame, text="Vista previa:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.filename_preview_var = tk.StringVar()
        ttk.Label(
            file_frame,
            textvariable=self.filename_preview_var,
            font=('Arial', 9, 'italic'),
            foreground='blue'
        ).grid(row=3, column=1, sticky="w", pady=10)
        
        # Actualizar vista previa inicial
        self._update_filename_preview()
        
        # Sección de opciones de contenido
        content_frame = self._create_section(main_frame, "Opciones de Contenido", 3)
        
        # Incluir metadatos
        self.include_metadata_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            content_frame,
            text="Incluir metadatos del reporte (fecha, usuario, etc.)",
            variable=self.include_metadata_var
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Incluir firmas
        self.include_signatures_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            content_frame,
            text="Incluir firmas y aprobaciones",
            variable=self.include_signatures_var
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Incluir logotipo
        self.include_logo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            content_frame,
            text="Incluir logotipo de la empresa",
            variable=self.include_logo_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Comprimir archivo
        self.compress_file_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            content_frame,
            text="Comprimir archivo (.zip)",
            variable=self.compress_file_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Sección de opciones avanzadas
        advanced_frame = self._create_section(main_frame, "Opciones Avanzadas", 4)
        
        # Calidad de exportación
        ttk.Label(advanced_frame, text="Calidad/Resolución:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.quality_var = tk.StringVar(value="normal")
        quality_combo = ttk.Combobox(
            advanced_frame,
            textvariable=self.quality_var,
            values=["Baja (rápido)", "Normal", "Alta (mejor calidad)", "Máxima"],
            state='readonly',
            width=20
        )
        quality_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Codificación de caracteres
        ttk.Label(advanced_frame, text="Codificación:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.encoding_var = tk.StringVar(value="UTF-8")
        encoding_combo = ttk.Combobox(
            advanced_frame,
            textvariable=self.encoding_var,
            values=["UTF-8", "UTF-16", "ISO-8859-1", "Windows-1252", "ASCII"],
            state='readonly',
            width=20
        )
        encoding_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Separador para CSV
        ttk.Label(advanced_frame, text="Separador (CSV):").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.separator_var = tk.StringVar(value=";")
        separator_combo = ttk.Combobox(
            advanced_frame,
            textvariable=self.separator_var,
            values=["; (punto y coma)", ", (coma)", "\\t (tabulación)", "| (pipe)", "  (espacio)"],
            state='readonly',
            width=20
        )
        separator_combo.grid(row=2, column=1, sticky="w", pady=10)
        
        # Opciones de PDF
        self.pdf_options_frame = ttk.Frame(advanced_frame)
        self.pdf_options_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.include_bookmarks_var = tk.BooleanVar(value=True)
        self.pdfa_compliant_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(
            self.pdf_options_frame,
            text="Incluir marcadores (bookmarks)",
            variable=self.include_bookmarks_var
        ).pack(anchor='w')
        
        ttk.Checkbutton(
            self.pdf_options_frame,
            text="PDF/A compliant (archivo)",
            variable=self.pdfa_compliant_var
        ).pack(anchor='w', pady=(2, 0))
        
        # Frame para botones especiales
        special_buttons_frame = ttk.Frame(main_frame)
        special_buttons_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            special_buttons_frame,
            text="Vista Previa Exportación",
            command=self._show_export_preview,
            width=20
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            special_buttons_frame,
            text="Enviar por Email",
            command=self._send_by_email,
            width=20
        ).pack(side=tk.LEFT)
        
        # Frame para botones principales
        self.button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        # Cambiar texto del botón Aceptar
        self.accept_button.config(text="Exportar")
    
    def _create_format_options(self) -> None:
        """Crea opciones específicas según el formato seleccionado."""
        # Limpiar frame
        for widget in self.format_options_frame.winfo_children():
            widget.destroy()
        
        format_name = self.format_var.get()
        
        if "Excel" in format_name:
            # Opciones para Excel
            self.excel_options_frame = ttk.Frame(self.format_options_frame)
            self.excel_options_frame.pack(anchor='w')
            
            self.include_formulas_var = tk.BooleanVar(value=False)
            self.include_charts_var = tk.BooleanVar(value=True)
            self.multiple_sheets_var = tk.BooleanVar(value=True)
            
            ttk.Checkbutton(
                self.excel_options_frame,
                text="Incluir fórmulas",
                variable=self.include_formulas_var
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Checkbutton(
                self.excel_options_frame,
                text="Incluir gráficos",
                variable=self.include_charts_var
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Checkbutton(
                self.excel_options_frame,
                text="Múltiples hojas",
                variable=self.multiple_sheets_var
            ).pack(side=tk.LEFT)
        
        elif "PDF" in format_name:
            # Opciones para PDF
            self.pdf_options_frame = ttk.Frame(self.format_options_frame)
            self.pdf_options_frame.pack(anchor='w')
            
            self.landscape_var = tk.BooleanVar(value=False)
            self.protect_pdf_var = tk.BooleanVar(value=False)
            
            ttk.Checkbutton(
                self.pdf_options_frame,
                text="Orientación horizontal",
                variable=self.landscape_var
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Checkbutton(
                self.pdf_options_frame,
                text="Proteger con contraseña",
                variable=self.protect_pdf_var
            ).pack(side=tk.LEFT)
            
            # Frame para contraseña si se selecciona protección
            if self.protect_pdf_var.get():
                password_frame = ttk.Frame(self.pdf_options_frame)
                password_frame.pack(anchor='w', pady=(5, 0))
                
                ttk.Label(password_frame, text="Contraseña:").pack(side=tk.LEFT)
                self.pdf_password_var = tk.StringVar()
                ttk.Entry(password_frame, textvariable=self.pdf_password_var, 
                         width=15, show="*").pack(side=tk.LEFT, padx=(5, 0))
        
        elif "HTML" in format_name:
            # Opciones para HTML
            self.html_options_frame = ttk.Frame(self.format_options_frame)
            self.html_options_frame.pack(anchor='w')
            
            self.include_css_var = tk.BooleanVar(value=True)
            self.include_js_var = tk.BooleanVar(value=False)
            self.standalone_var = tk.BooleanVar(value=True)
            
            ttk.Checkbutton(
                self.html_options_frame,
                text="Incluir estilos CSS",
                variable=self.include_css_var
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Checkbutton(
                self.html_options_frame,
                text="Incluir JavaScript",
                variable=self.include_js_var
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Checkbutton(
                self.html_options_frame,
                text="Archivo independiente",
                variable=self.standalone_var
            ).pack(side=tk.LEFT)
    
    def _on_format_change(self, event=None) -> None:
        """Actualiza opciones cuando cambia el formato."""
        self._create_format_options()
        self._update_filename_preview()
        
        # Mostrar/ocultar opciones específicas
        format_name = self.format_var.get()
        
        if "PDF" in format_name:
            self.pdf_options_frame.grid()
        else:
            self.pdf_options_frame.grid_remove()
    
    def _select_location(self) -> None:
        """Abre diálogo para seleccionar ubicación de guardado."""
        try:
            from tkinter import filedialog
            
            # Obtener extensión del formato seleccionado
            format_name = self.format_var.get()
            extension = self._get_extension_from_format(format_name)
            
            # Construir nombre de archivo con extensión
            filename = self.filename_var.get()
            if not filename.endswith(extension):
                filename += extension
            
            # Abrir diálogo de guardado
            filepath = filedialog.asksaveasfilename(
                parent=self,
                title="Guardar reporte como",
                initialfile=filename,
                defaultextension=extension,
                filetypes=self._get_filetypes_for_format(format_name)
            )
            
            if filepath:
                # Actualizar ubicación y nombre
                import os
                self.location_var.set(os.path.dirname(filepath))
                self.filename_var.set(os.path.basename(filepath).replace(extension, ""))
                self._update_filename_preview()
                
        except ImportError:
            messagebox.showwarning(
                "No disponible",
                "El selector de archivos no está disponible en este entorno.",
                parent=self
            )
    
    def _get_extension_from_format(self, format_name: str) -> str:
        """Obtiene extensión de archivo del formato."""
        if "Excel" in format_name:
            return ".xlsx"
        elif "PDF" in format_name:
            return ".pdf"
        elif "CSV" in format_name:
            return ".csv"
        elif "HTML" in format_name:
            return ".html"
        elif "Texto" in format_name:
            return ".txt"
        elif "JSON" in format_name:
            return ".json"
        elif "XML" in format_name:
            return ".xml"
        elif "Imagen" in format_name:
            return ".png"
        else:
            return ""
    
    def _get_filetypes_for_format(self, format_name: str) -> List[Tuple[str, str]]:
        """Obtiene tipos de archivo para el diálogo de guardado."""
        if "Excel" in format_name:
            return [("Excel files", "*.xlsx"), ("All files", "*.*")]
        elif "PDF" in format_name:
            return [("PDF files", "*.pdf"), ("All files", "*.*")]
        elif "CSV" in format_name:
            return [("CSV files", "*.csv"), ("All files", "*.*")]
        elif "HTML" in format_name:
            return [("HTML files", "*.html"), ("All files", "*.*")]
        elif "Texto" in format_name:
            return [("Text files", "*.txt"), ("All files", "*.*")]
        elif "JSON" in format_name:
            return [("JSON files", "*.json"), ("All files", "*.*")]
        elif "XML" in format_name:
            return [("XML files", "*.xml"), ("All files", "*.*")]
        elif "Imagen" in format_name:
            return [("PNG files", "*.png"), ("All files", "*.*")]
        else:
            return [("All files", "*.*")]
    
    def _update_filename_preview(self) -> None:
        """Actualiza la vista previa del nombre de archivo."""
        base_name = self.filename_var.get().strip()
        if not base_name:
            base_name = self.report_name
        
        # Agregar componentes según opciones
        components = [base_name]
        
        if self.include_date_var.get():
            components.append(datetime.now().strftime("%Y%m%d"))
        
        if self.include_time_var.get():
            components.append(datetime.now().strftime("%H%M%S"))
        
        if self.include_user_var.get():
            import getpass
            components.append(getpass.getuser())
        
        # Unir componentes
        filename = "_".join(components)
        
        # Agregar extensión
        format_name = self.format_var.get()
        extension = self._get_extension_from_format(format_name)
        filename += extension
        
        # Actualizar variable
        self.filename_preview_var.set(filename)
    
    def _show_export_preview(self) -> None:
        """Muestra vista previa de la exportación."""
        format_name = self.format_var.get()
        filename = self.filename_preview_var.get()
        
        preview_text = f"Vista previa de exportación:\n\n"
        preview_text += f"Formato: {format_name}\n"
        preview_text += f"Archivo: {filename}\n"
        preview_text += f"Ubicación: {self.location_var.get()}\n\n"
        
        # Opciones específicas
        if "Excel" in format_name:
            preview_text += "Opciones Excel:\n"
            if hasattr(self, 'include_formulas_var'):
                preview_text += f"• Fórmulas: {'Sí' if self.include_formulas_var.get() else 'No'}\n"
            if hasattr(self, 'include_charts_var'):
                preview_text += f"• Gráficos: {'Sí' if self.include_charts_var.get() else 'No'}\n"
        
        elif "PDF" in format_name:
            preview_text += "Opciones PDF:\n"
            if hasattr(self, 'landscape_var'):
                preview_text += f"• Horizontal: {'Sí' if self.landscape_var.get() else 'No'}\n"
            if hasattr(self, 'protect_pdf_var'):
                preview_text += f"• Protegido: {'Sí' if self.protect_pdf_var.get() else 'No'}\n"
        
        preview_text += f"\nTamaño estimado: 1-5 MB\n"
        preview_text += f"Tiempo estimado: 2-10 segundos"
        
        messagebox.showinfo("Vista Previa de Exportación", preview_text, parent=self)
    
    def _send_by_email(self) -> None:
        """Configura envío por email."""
        messagebox.showinfo(
            "Enviar por Email",
            "Esta función enviaría el reporte exportado por email:\n"
            "• Configurar destinatarios\n"
            "• Agregar asunto y mensaje\n"
            "• Adjuntar archivo exportado\n"
            "• Enviar copia a archivo",
            parent=self
        )
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos requeridos."""
        errors = []
        
        # Validar nombre de archivo
        filename = self.filename_var.get().strip()
        if not filename:
            errors.append("El nombre del archivo es requerido")
        
        # Validar caracteres no permitidos en nombre de archivo
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in filename:
                errors.append(f"Nombre de archivo no puede contener '{char}'")
                break
        
        # Validar contraseña si PDF protegido
        format_name = self.format_var.get()
        if "PDF" in format_name:
            if hasattr(self, 'protect_pdf_var') and self.protect_pdf_var.get():
                if not hasattr(self, 'pdf_password_var') or not self.pdf_password_var.get():
                    errors.append("Ingrese contraseña para PDF protegido")
                elif len(self.pdf_password_var.get()) < 4:
                    errors.append("La contraseña debe tener al menos 4 caracteres")
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de configuración de exportación."""
        format_name = self.format_var.get()
        extension = self._get_extension_from_format(format_name)
        
        # Construir nombre de archivo completo
        base_name = self.filename_var.get().strip()
        components = [base_name]
        
        if self.include_date_var.get():
            components.append(datetime.now().strftime("%Y%m%d"))
        
        if self.include_time_var.get():
            components.append(datetime.now().strftime("%H%M%S"))
        
        if self.include_user_var.get():
            import getpass
            components.append(getpass.getuser())
        
        filename = "_".join(components) + extension
        full_path = f"{self.location_var.get()}/{filename}"
        
        # Obtener opciones específicas del formato
        format_options = {}
        
        if "Excel" in format_name:
            if hasattr(self, 'include_formulas_var'):
                format_options['include_formulas'] = self.include_formulas_var.get()
            if hasattr(self, 'include_charts_var'):
                format_options['include_charts'] = self.include_charts_var.get()
            if hasattr(self, 'multiple_sheets_var'):
                format_options['multiple_sheets'] = self.multiple_sheets_var.get()
        
        elif "PDF" in format_name:
            if hasattr(self, 'landscape_var'):
                format_options['landscape'] = self.landscape_var.get()
            if hasattr(self, 'protect_pdf_var'):
                format_options['protect_pdf'] = self.protect_pdf_var.get()
                if self.protect_pdf_var.get() and hasattr(self, 'pdf_password_var'):
                    format_options['pdf_password'] = self.pdf_password_var.get()
            if hasattr(self, 'include_bookmarks_var'):
                format_options['include_bookmarks'] = self.include_bookmarks_var.get()
            if hasattr(self, 'pdfa_compliant_var'):
                format_options['pdfa_compliant'] = self.pdfa_compliant_var.get()
        
        elif "HTML" in format_name:
            if hasattr(self, 'include_css_var'):
                format_options['include_css'] = self.include_css_var.get()
            if hasattr(self, 'include_js_var'):
                format_options['include_js'] = self.include_js_var.get()
            if hasattr(self, 'standalone_var'):
                format_options['standalone'] = self.standalone_var.get()
        
        # Obtener separador para CSV
        separator = self.separator_var.get().split(" ")[0]  # Obtener solo el carácter
        
        return {
            'format': format_name,
            'format_extension': extension,
            'filename': filename,
            'full_path': full_path,
            'location': self.location_var.get(),
            'include_metadata': self.include_metadata_var.get(),
            'include_signatures': self.include_signatures_var.get(),
            'include_logo': self.include_logo_var.get(),
            'compress_file': self.compress_file_var.get(),
            'quality': self.quality_var.get(),
            'encoding': self.encoding_var.get(),
            'separator': separator,
            'format_options': format_options,
            'timestamp': datetime.now()
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Crear diálogo
    dialog = ExportOptionsDialog(
        parent=root,
        report_name="Reporte_Tarjetas_Caja",
        available_formats=["Excel (.xlsx)", "PDF (.pdf)", "CSV (.csv)"],
        default_filename="tarjetas_caja"
    )
    result = dialog.show()
    
    if result:
        print("Configuración de Exportación:")
        print(f"  Formato: {result['format']}")
        print(f"  Archivo: {result['filename']}")
        print(f"  Ubicación: {result['location']}")
        print(f"  Ruta completa: {result['full_path']}")
        print(f"  Incluir metadatos: {result['include_metadata']}")
        print(f"  Calidad: {result['quality']}")
        print(f"  Codificación: {result['encoding']}")
        print(f"  Separador: {result['separator']}")
        
        if result['format_options']:
            print(f"  Opciones específicas:")
            for key, value in result['format_options'].items():
                print(f"    {key}: {value}")
    else:
        print("Exportación cancelada")
    
    root.destroy()
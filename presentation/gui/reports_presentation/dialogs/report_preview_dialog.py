"""
report_preview_dialog.py
Diálogo para vista previa de reportes antes de generarlos o exportarlos.
Muestra una representación del reporte con los parámetros configurados.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog


class ReportPreviewDialog(BaseReportDialog):
    """Diálogo para vista previa de reportes"""
    
    def __init__(self, parent, 
                 report_name: str = "Reporte",
                 report_params: Optional[Dict[str, Any]] = None,
                 sample_data: Optional[List[Tuple]] = None,
                 columns: Optional[List[str]] = None):
        """
        Inicializa el diálogo de vista previa de reportes.
        
        Args:
            parent: Ventana padre
            report_name: Nombre del reporte
            report_params: Parámetros del reporte
            sample_data: Datos de ejemplo para la vista previa
            columns: Nombres de columnas
        """
        self.report_name = report_name
        self.report_params = report_params or {}
        self.sample_data = sample_data
        self.columns = columns or []
        
        # Generar datos de ejemplo si no se proporcionan
        if not self.sample_data:
            self._generate_sample_data()
        
        super().__init__(parent, f"Vista Previa: {report_name}", width=800, height=650)
    
    def _generate_sample_data(self) -> None:
        """Genera datos de ejemplo para la vista previa."""
        # Datos de ejemplo según el tipo de reporte
        report_name_lower = self.report_name.lower()
        
        if "tarjeta" in report_name_lower and "caja" in report_name_lower:
            # Tarjetas en caja central
            self.columns = ["Tarjeta", "PIN", "Saldo (CUP)"]
            self.sample_data = [
                ("9580130010006207", "5629", "7,352.20"),
                ("9580130010010506", "236", "6,600.35"),
                ("9580130010006215", "0132", "6,561.90"),
                ("9580130010006231", "8615", "4,000.00"),
                ("9580130010006322", "2410", "4,000.00"),
                ("9580130010014409", "8415", "4,000.00"),
                ("9580130010006264", "1174", "2,960.10"),
                ("9580130010006314", "2420", "2,488.65"),
                ("9580130010014375", "1142", "1,600.00"),
                ("9580130010006506", "4601", "400.40")
            ]
        
        elif "anticipo" in report_name_lower and "liquidar" in report_name_lower:
            # Anticipos sin liquidar
            self.columns = ["Nombre", "Anticipo", "ImporteCUP", "HospedajeCUC", "Tarjeta", "Regreso", "Días"]
            self.sample_data = [
                ("Brigada Mito Luis Miguel Jimenez Martínez", "1758", "22,000.00", "0.00", "", "05/12/2025", ""),
                ("Almacen Regulador Miguel Angel Bettrán Valdivia", "1761", "22,000.00", "0.00", "", "05/12/2025", ""),
                ("BRIGADA DE INVERSION Jose Luis García Collado", "1757", "400.00", "0.00", "", "25/11/2025", "2")
            ]
        
        elif "comprobante" in report_name_lower and "contable" in report_name_lower:
            # Comprobante contable
            self.columns = ["Trans", "Operación", "Consecutivo", "Fecha", "Cuenta", "CCosto", "DebeCUP", "HaberCUP"]
            self.sample_data = [
                ("1", "Anticipo", "1731", "21/11/2025", "16101001", "CCS2410", "400.00", ""),
                ("", "", "", "21/11/2025", "10110200", "CCS2410", "", "400.00"),
                ("", "Anticipo", "1732", "21/11/2025", "16101001", "CCS2410", "400.00", ""),
                ("", "", "", "21/11/2025", "10110200", "CCS2410", "", "400.00"),
                ("", "Anticipo", "1733", "21/11/2025", "16101001", "CCS2410", "400.00", ""),
                ("", "", "", "21/11/2025", "10110200", "CCS2410", "", "400.00")
            ]
        
        elif "cuenta" in report_name_lower:
            # Cuentas para reportes
            self.columns = ["Cuenta", "Descripción"]
            self.sample_data = [
                ("83609800", "Gastos financieros/Compra Tarj"),
                ("14701002", "Pago Anticipado Tarjeta"),
                ("10110804", "Efectivo en caja /Tarjetas"),
                ("16201002", "Anticipo para Tarjeta"),
                ("16101001", "Anticipo para Dieta"),
                ("10110200", "Efectivo en Caja /Fondo")
            ]
        
        elif "centro" in report_name_lower and "costo" in report_name_lower:
            # Centro de costo
            self.columns = ["Dpto", "Nombre", "CCosto", "Cta Gasto Alim.", "Cta Gasto Hosp."]
            self.sample_data = [
                ("01", "Gerencia General", "CCS2410101", "82244400", "82344500"),
                ("02", "Gerencia Economía", "CCS2410102", "82244400", "82344500"),
                ("03", "Grupo Informática", "CCS2410103", "82244400", "82344500"),
                ("04", "Gerencia R. Humanos", "CCS2410104", "82244400", "82344500"),
                ("05", "Gerencia Auditoría", "CCS2410105", "82344400", "82344500")
            ]
        
        else:
            # Datos genéricos
            self.columns = ["Columna 1", "Columna 2", "Columna 3", "Columna 4"]
            self.sample_data = [
                ("Dato 1A", "Dato 1B", "Dato 1C", "100.00"),
                ("Dato 2A", "Dato 2B", "Dato 2C", "200.00"),
                ("Dato 3A", "Dato 3B", "Dato 3C", "300.00"),
                ("Dato 4A", "Dato 4B", "Dato 4C", "400.00"),
                ("Dato 5A", "Dato 5B", "Dato 5C", "500.00")
            ]
    
    def _create_widgets(self) -> None:
        """Crea los widgets del diálogo."""
        # Frame principal
        main_frame = ttk.Frame(self, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar expansión
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header con información del reporte
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Nombre del reporte
        ttk.Label(
            header_frame,
            text=f"Vista Previa: {self.report_name}",
            font=('Arial', 14, 'bold')
        ).pack(anchor='w')
        
        # Información de parámetros
        if self.report_params:
            params_text = self._format_params_text()
            params_label = ttk.Label(
                header_frame,
                text=params_text,
                font=('Arial', 9),
                foreground='darkblue'
            )
            params_label.pack(anchor='w', pady=(5, 0))
        
        # Frame para pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky="nsew")
        
        # Pestaña 1: Vista de tabla
        table_frame = ttk.Frame(notebook, padding="10")
        notebook.add(table_frame, text="Vista Tabular")
        
        # Área de texto con scroll para la vista de tabla
        self.table_text = scrolledtext.ScrolledText(
            table_frame,
            wrap=tk.NONE,
            width=90,
            height=20,
            font=('Courier', 9)
        )
        self.table_text.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 2: Vista de texto
        text_frame = ttk.Frame(notebook, padding="10")
        notebook.add(text_frame, text="Vista de Texto")
        
        # Área de texto con scroll para vista de texto
        self.text_view = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=90,
            height=20,
            font=('Arial', 9)
        )
        self.text_view.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 3: Estadísticas
        stats_frame = ttk.Frame(notebook, padding="10")
        notebook.add(stats_frame, text="Estadísticas")
        
        # Frame para estadísticas con scroll
        stats_scroll_frame = ttk.Frame(stats_frame)
        stats_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para scroll
        stats_canvas = tk.Canvas(stats_scroll_frame)
        stats_scrollbar = ttk.Scrollbar(stats_scroll_frame, orient="vertical", command=stats_canvas.yview)
        self.stats_content = ttk.Frame(stats_canvas)
        
        stats_canvas.configure(yscrollcommand=stats_scrollbar.set)
        
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        stats_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_canvas.create_window((0, 0), window=self.stats_content, anchor="nw")
        
        # Frame para controles en la parte inferior
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        
        # Botones de navegación
        nav_frame = ttk.Frame(controls_frame)
        nav_frame.pack(side=tk.LEFT)
        
        ttk.Button(
            nav_frame,
            text="⏪ Primera Página",
            command=lambda: self._show_page(1),
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            nav_frame,
            text="◀ Anterior",
            command=self._prev_page,
            width=10
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_label = ttk.Label(
            nav_frame,
            text="Página 1 de 1",
            font=('Arial', 9, 'bold')
        )
        self.page_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            nav_frame,
            text="Siguiente ▶",
            command=self._next_page,
            width=10
        ).pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Button(
            nav_frame,
            text="Última Página ⏩",
            command=self._last_page,
            width=15
        ).pack(side=tk.LEFT)
        
        # Botones de acción
        action_frame = ttk.Frame(controls_frame)
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            action_frame,
            text="Copiar al Portapapeles",
            command=self._copy_to_clipboard,
            width=18
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_frame,
            text="Imprimir Vista",
            command=self._print_preview,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_frame,
            text="Exportar Vista...",
            command=self._export_preview,
            width=15
        ).pack(side=tk.LEFT)
        
        # Estado de la vista previa
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="",
            font=('Arial', 9, 'italic')
        )
        self.status_label.pack(anchor='w')
        
        # Variables de estado
        self.current_page = 1
        self.total_pages = 1
        self.formatted_data = []
        
        # Frame para botones principales
        self.button_frame.grid(row=4, column=0, sticky="ew", pady=(15, 0))
        
        # Cambiar texto del botón Aceptar
        self.accept_button.config(text="Cerrar Vista Previa")
        
        # Cargar datos en las vistas
        self._load_preview_data()
        self._update_page_info()
        self._update_status("Vista previa cargada correctamente")
    
    def _format_params_text(self) -> str:
        """Formatea los parámetros para mostrar en el header."""
        if not self.report_params:
            return "Sin parámetros configurados"
        
        params_list = []
        for key, value in self.report_params.items():
            if key not in ['report_name', 'timestamp', 'selected_info', 'selected_metrics', 'format_options']:
                if isinstance(value, datetime):
                    params_list.append(f"{key}: {value.strftime('%d/%m/%Y')}")
                elif isinstance(value, bool):
                    params_list.append(f"{key}: {'Sí' if value else 'No'}")
                elif value:
                    params_list.append(f"{key}: {value}")
        
        return " | ".join(params_list[:5]) + ("..." if len(params_list) > 5 else "")
    
    def _load_preview_data(self) -> None:
        """Carga los datos en las diferentes vistas."""
        # Generar vista tabular
        table_view = self._generate_table_view()
        self.table_text.delete(1.0, tk.END)
        self.table_text.insert(1.0, table_view)
        self.table_text.config(state='disabled')
        
        # Generar vista de texto
        text_view = self._generate_text_view()
        self.text_view.delete(1.0, tk.END)
        self.text_view.insert(1.0, text_view)
        self.text_view.config(state='disabled')
        
        # Generar estadísticas
        self._generate_statistics()
    
    def _generate_table_view(self) -> str:
        """Genera la vista tabular del reporte."""
        if not self.columns or not self.sample_data:
            return "No hay datos para mostrar"
        
        # Calcular anchos de columna
        col_widths = []
        for i, col in enumerate(self.columns):
            max_len = len(str(col))
            for row in self.sample_data:
                if i < len(row):
                    max_len = max(max_len, len(str(row[i])))
            col_widths.append(max_len + 2)  # +2 para padding
        
        # Construir encabezado
        header = ""
        for i, col in enumerate(self.columns):
            header += f"{col:<{col_widths[i]}}"
        header += "\n"
        
        # Línea separadora
        separator = ""
        for width in col_widths:
            separator += "-" * width
        separator += "\n"
        
        # Construir filas
        rows = ""
        for row in self.sample_data:
            row_str = ""
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    # Formatear números con alineación a la derecha
                    if isinstance(cell, str) and any(c.isdigit() for c in cell.replace('.', '').replace(',', '')):
                        # Es un número, alinear a la derecha
                        row_str += f"{cell:>{col_widths[i]}}"
                    else:
                        # Es texto, alinear a la izquierda
                        row_str += f"{cell:<{col_widths[i]}}"
            rows += row_str + "\n"
        
        # Totales si aplica
        totals = ""
        if any("Saldo" in col or "Importe" in col or "Total" in col for col in self.columns):
            totals = "\n" + "-" * sum(col_widths) + "\n"
            
            # Calcular totales para columnas numéricas
            for i, col in enumerate(self.columns):
                if any(keyword in col for keyword in ["Saldo", "Importe", "Total", "Monto", "CUP", "CUC"]):
                    total = 0
                    for row in self.sample_data:
                        if i < len(row):
                            cell = row[i]
                            # Limpiar y convertir a número
                            if isinstance(cell, str):
                                clean = cell.replace(',', '').replace(' ', '')
                                try:
                                    total += float(clean)
                                except:
                                    pass
                    
                    if total > 0:
                        total_str = f"{total:,.2f}"
                        # Encontrar la posición correcta para el total
                        padding = sum(col_widths[:i]) + col_widths[i] - len(total_str) - 2
                        totals += " " * padding + f"Total: {total_str}\n"
                        break
        
        return header + separator + rows + totals
    
    def _generate_text_view(self) -> str:
        """Genera la vista de texto del reporte."""
        if not self.columns or not self.sample_data:
            return "No hay datos para mostrar"
        
        # Encabezado del reporte
        text = f"REPORTE: {self.report_name}\n"
        text += f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        
        if self.report_params:
            text += "\nPARÁMETROS CONFIGURADOS:\n"
            for key, value in self.report_params.items():
                if key not in ['report_name', 'timestamp', 'selected_info', 'selected_metrics', 'format_options']:
                    if isinstance(value, datetime):
                        text += f"  • {key}: {value.strftime('%d/%m/%Y')}\n"
                    elif isinstance(value, bool):
                        text += f"  • {key}: {'Sí' if value else 'No'}\n"
                    elif value:
                        text += f"  • {key}: {value}\n"
        
        text += "\n" + "=" * 60 + "\n"
        text += "DETALLE DEL REPORTE:\n"
        text += "=" * 60 + "\n\n"
        
        # Generar contenido
        if len(self.sample_data) > 0:
            for i, row in enumerate(self.sample_data, 1):
                text += f"Registro #{i}:\n"
                for j, col in enumerate(self.columns):
                    if j < len(row):
                        value = row[j]
                        text += f"  {col}: {value}\n"
                text += "\n"
        
        # Resumen
        text += "=" * 60 + "\n"
        text += "RESUMEN:\n"
        text += f"Total de registros: {len(self.sample_data)}\n"
        text += f"Total de columnas: {len(self.columns)}\n"
        
        # Calcular totales si hay columnas numéricas
        numeric_cols = []
        for i, col in enumerate(self.columns):
            if any(keyword in col for keyword in ["Saldo", "Importe", "Total", "Monto", "CUP", "CUC"]):
                numeric_cols.append((i, col))
        
        if numeric_cols:
            text += "\nTOTALES:\n"
            for col_idx, col_name in numeric_cols:
                total = 0
                for row in self.sample_data:
                    if col_idx < len(row):
                        cell = row[col_idx]
                        if isinstance(cell, str):
                            clean = cell.replace(',', '').replace(' ', '')
                            try:
                                total += float(clean)
                            except:
                                pass
                
                if total > 0:
                    text += f"  {col_name}: {total:,.2f} CUP\n"
        
        return text
    
    def _generate_statistics(self) -> None:
        """Genera estadísticas del reporte."""
        # Limpiar frame de estadísticas
        for widget in self.stats_content.winfo_children():
            widget.destroy()
        
        # Estadísticas básicas
        stats = [
            ("Total de registros", len(self.sample_data)),
            ("Total de columnas", len(self.columns)),
            ("Fecha de vista previa", datetime.now().strftime("%d/%m/%Y %H:%M")),
            ("Tamaño estimado del reporte", f"{len(str(self.sample_data)) / 1024:.1f} KB")
        ]
        
        # Análisis de columnas
        col_types = []
        for i, col in enumerate(self.columns):
            numeric_count = 0
            text_count = 0
            empty_count = 0
            
            for row in self.sample_data:
                if i < len(row):
                    cell = row[i]
                    if isinstance(cell, str):
                        clean = cell.strip()
                        if clean == "":
                            empty_count += 1
                        elif clean.replace('.', '').replace(',', '').isdigit():
                            numeric_count += 1
                        else:
                            text_count += 1
            
            total = len(self.sample_data)
            col_type = "Texto"
            if numeric_count > total * 0.7:
                col_type = "Numérico"
            elif empty_count > total * 0.5:
                col_type = "Parcial"
            
            col_types.append((col, col_type, numeric_count, text_count, empty_count))
        
        # Frame para estadísticas básicas
        basic_frame = ttk.LabelFrame(self.stats_content, text="Estadísticas Básicas", padding="10")
        basic_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(basic_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=(0, 10), pady=2)
            ttk.Label(basic_frame, text=str(value), font=('Arial', 9, 'bold')).grid(row=i, column=1, sticky="w", pady=2)
        
        # Frame para análisis de columnas
        cols_frame = ttk.LabelFrame(self.stats_content, text="Análisis de Columnas", padding="10")
        cols_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Treeview para análisis de columnas
        tree_columns = ("Columna", "Tipo", "Numéricos", "Texto", "Vacíos")
        tree = ttk.Treeview(cols_frame, columns=tree_columns, show="headings", height=min(6, len(col_types)))
        
        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        
        # Insertar datos
        for col_data in col_types:
            tree.insert("", "end", values=col_data)
        
        tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(cols_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configurar expansión
        cols_frame.columnconfigure(0, weight=1)
        cols_frame.rowconfigure(0, weight=1)
        
        # Frame para resumen numérico
        if any(col[2] > 0 for col in col_types):  # Si hay columnas numéricas
            numeric_frame = ttk.LabelFrame(self.stats_content, text="Resumen Numérico", padding="10")
            numeric_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
            
            # Calcular totales por columna numérica
            row_idx = 0
            for i, col in enumerate(self.columns):
                if any(keyword in col for keyword in ["Saldo", "Importe", "Total", "Monto", "CUP", "CUC"]):
                    total = 0
                    max_val = 0
                    min_val = float('inf')
                    
                    for row in self.sample_data:
                        if i < len(row):
                            cell = row[i]
                            if isinstance(cell, str):
                                clean = cell.replace(',', '').replace(' ', '')
                                try:
                                    val = float(clean)
                                    total += val
                                    max_val = max(max_val, val)
                                    if val > 0:
                                        min_val = min(min_val, val)
                                except:
                                    pass
                    
                    if total > 0:
                        avg = total / len(self.sample_data)
                        ttk.Label(numeric_frame, text=f"{col}:").grid(row=row_idx, column=0, sticky="w", padx=(0, 10), pady=2)
                        ttk.Label(numeric_frame, text=f"Total: {total:,.2f} | Prom: {avg:,.2f} | Máx: {max_val:,.2f} | Mín: {min_val:,.2f}", 
                                 font=('Arial', 9)).grid(row=row_idx, column=1, sticky="w", pady=2)
                        row_idx += 1
        
        # Configurar scroll del canvas
        self.stats_content.update_idletasks()
        stats_canvas = self.stats_content.master.master  # Acceder al canvas padre
        stats_canvas.configure(scrollregion=stats_canvas.bbox("all"))
        
        # Bind para scroll con mouse
        self.stats_content.bind_all("<MouseWheel>", lambda e: stats_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def _show_page(self, page: int) -> None:
        """Muestra una página específica."""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self._update_page_info()
            self._update_status(f"Mostrando página {page} de {self.total_pages}")
    
    def _prev_page(self) -> None:
        """Muestra la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_page_info()
            self._update_status(f"Página anterior: {self.current_page}")
    
    def _next_page(self) -> None:
        """Muestra la página siguiente."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._update_page_info()
            self._update_status(f"Página siguiente: {self.current_page}")
    
    def _last_page(self) -> None:
        """Muestra la última página."""
        self.current_page = self.total_pages
        self._update_page_info()
        self._update_status(f"Última página: {self.current_page}")
    
    def _update_page_info(self) -> None:
        """Actualiza la información de página."""
        self.page_label.config(text=f"Página {self.current_page} de {self.total_pages}")
    
    def _update_status(self, message: str) -> None:
        """Actualiza el mensaje de estado."""
        self.status_label.config(text=f"Estado: {message}")
    
    def _copy_to_clipboard(self) -> None:
        """Copia el contenido actual al portapapeles."""
        try:
            # Obtener el contenido de la pestaña activa
            notebook = self.button_frame.master.master.winfo_children()[1]  # El notebook
            current_tab = notebook.select()
            tab_text = notebook.tab(current_tab, "text")
            
            if "Tabular" in tab_text:
                content = self.table_text.get(1.0, tk.END)
            else:
                content = self.text_view.get(1.0, tk.END)
            
            self.clipboard_clear()
            self.clipboard_append(content.strip())
            
            self._update_status("Contenido copiado al portapapeles")
            messagebox.showinfo("Copiado", "El contenido ha sido copiado al portapapeles.", parent=self)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar al portapapeles: {str(e)}", parent=self)
    
    def _print_preview(self) -> None:
        """Muestra vista previa de impresión."""
        messagebox.showinfo(
            "Vista Previa de Impresión",
            "Esta función mostraría una vista previa de impresión:\n"
            "• Configurar página y márgenes\n"
            "• Vista previa WYSIWYG\n"
            "• Seleccionar impresora\n"
            "• Ajustar orientación",
            parent=self
        )
    
    def _export_preview(self) -> None:
        """Exporta la vista previa."""
        from .export_options_dialog import ExportOptionsDialog
        
        dialog = ExportOptionsDialog(
            self,
            report_name=f"VistaPrevia_{self.report_name}",
            default_filename=f"vista_previa_{self.report_name.lower().replace(' ', '_')}"
        )
        
        result = dialog.show()
        if result:
            self._update_status(f"Exportación configurada: {result['format']}")
            messagebox.showinfo(
                "Exportar Vista Previa",
                f"Vista previa lista para exportar en formato {result['format']}.\n"
                f"Archivo: {result['filename']}\n\n"
                "Nota: En una implementación real, aquí se generaría el archivo.",
                parent=self
            )
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos (siempre válido para vista previa)."""
        return True
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de la vista previa."""
        return {
            'report_name': self.report_name,
            'preview_generated': True,
            'timestamp': datetime.now(),
            'data_rows': len(self.sample_data),
            'data_columns': len(self.columns),
            'current_page': self.current_page,
            'total_pages': self.total_pages
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Crear diálogo con datos de ejemplo
    sample_params = {
        'report_name': 'Tarjetas en Caja Central',
        'fecha': datetime.now(),
        'entidad': 'CIMEX - Gerencia Administrativa',
        'cajero': 'KAREN GUZMAN FIGUEROA',
        'include_totals': True
    }
    
    dialog = ReportPreviewDialog(
        parent=root,
        report_name="Tarjetas en Caja Central",
        report_params=sample_params
    )
    result = dialog.show()
    
    if result:
        print("Vista previa generada:")
        print(f"  Reporte: {result['report_name']}")
        print(f"  Filas: {result['data_rows']}")
        print(f"  Columnas: {result['data_columns']}")
        print(f"  Página actual: {result['current_page']}")
        print(f"  Total páginas: {result['total_pages']}")
        print(f"  Generado: {result['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
    else:
        print("Vista previa cerrada")
    
    root.destroy()
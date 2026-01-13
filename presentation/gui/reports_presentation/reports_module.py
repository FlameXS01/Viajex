# presentation/gui/reports_presentation/reports_module.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any
import traceback
from presentation.gui.utils.data_exporter import TreeviewExporter, create_export_button


class ReportModule(ttk.Frame):
    """
    Módulo de reportes del sistema - Versión completa con filtros por columna
    """
    
    def __init__(self, parent, report_service, department_service, 
                 user_service, card_service, diet_service=None, 
                 request_user_service=None):
        super().__init__(parent)
        self.report_service = report_service
        self.department_service = department_service
        self.user_service = user_service
        self.card_service = card_service
        self.diet_service = diet_service
        self.request_user_service = request_user_service
        
        # Datos actuales
        self.current_data = []
        self.current_report_type = None  # "cards" o "diets"
        
        # Diccionario para almacenar las entradas de filtro por columna
        self.filter_entries = {}
        
        self.create_widgets()
        self.show_initial_message()
    
    def create_widgets(self):
        """Crea todos los widgets del módulo"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 1. Selector de tipo de reporte
        self._create_report_selector(main_frame)
        
        
        # 3. Frame para la tabla
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # 2. Frame para filtros (se llenará dinámicamente)
        self.filter_frame = ttk.LabelFrame(main_frame, text="🔍 Filtros por Columna")
        self.filter_frame.pack(fill=tk.X, pady=(10, 5))
        # 4. Crear tabla
        self._create_table(table_frame)
        
        # 5. Botón de exportación (se mostrará solo para dietas)
        self.export_button_frame = ttk.Frame(main_frame)
        self.export_button_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 6. Botón de limpiar filtros
        ttk.Button(main_frame, text="🧹 Limpiar Filtros", 
                  command=self.clear_filters).pack(side=tk.RIGHT, padx=5)
        
        # 7. Botón de actualizar
        ttk.Button(main_frame, text="🔄 Actualizar", 
                  command=self.refresh_report).pack(side=tk.RIGHT, padx=5)
    
    def _create_report_selector(self, parent):
        """Crea el selector de tipo de reporte"""
        selector_frame = ttk.LabelFrame(parent, text="📊 Tipo de Reporte")
        selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Variable para los radio buttons
        self.report_type_var = tk.StringVar(value="cards")
        
        # Radio buttons
        cards_rb = ttk.Radiobutton(
            selector_frame, 
            text="💳 Reporte de Tarjetas", 
            variable=self.report_type_var, 
            value="cards",
            command=self.on_report_type_changed
        )
        cards_rb.pack(side=tk.LEFT, padx=20, pady=5)
        
        diets_rb = ttk.Radiobutton(
            selector_frame, 
            text="🍽️ Reporte de Dietas", 
            variable=self.report_type_var, 
            value="diets",
            command=self.on_report_type_changed
        )
        diets_rb.pack(side=tk.LEFT, padx=20, pady=5)
    
    def _create_table(self, parent):
        """Crea la tabla para mostrar los reportes"""
        # Frame para tabla con scrollbars
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview
        self.tree = ttk.Treeview(table_container, show="headings")
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configurar pesos
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Configurar evento de selección
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)
    
    def on_report_type_changed(self):
        """Se ejecuta cuando cambia el tipo de reporte"""
        report_type = self.report_type_var.get()
        self.current_report_type = report_type
        
        # Actualizar filtros
        self.update_filter_fields()
        
        # Cargar datos
        self.load_report_data()
        
        # Mostrar/ocultar botón de exportación
        self.update_export_button()
    
    def update_filter_fields(self):
        """Actualiza los campos de filtro según el tipo de reporte"""
        # Limpiar frame de filtros
        for widget in self.filter_frame.winfo_children():
            widget.destroy()
        
        self.filter_entries.clear()
        
        # Definir columnas según tipo de reporte
        if self.current_report_type == "cards":
            columns = [
                ("Número de Tarjeta", "numero_tarjeta", 150),
                ("PIN", "pin", 100),
                ("Balance", "balance", 120),
                ("Estado", "estado", 120)
            ]
        else:  # diets
            columns = [
                ("No. Anticipo", "no_anticipo", 100),
                ("No. Liquidación", "no_liquidacion", 120),
                ("Descripción", "descripcion", 200),
                ("Solicitante", "solicitante", 150),
                ("Departamento", "departamento", 150),
                ("Fecha Inicio", "fecha_inicio", 100),
                ("Fecha Fin", "fecha_fin", 100),
                ("Fecha Solicitud", "fecha_solicitud", 120),
                ("Fecha Liquidación", "fecha_liquidacion", 120),
                ("Monto Solicitado", "monto_solicitado", 120)
            ]
        
        # Crear etiquetas y entradas para cada columna
        for idx, (display_name, key, width) in enumerate(columns):
            # Frame para cada filtro
            filter_item_frame = ttk.Frame(self.filter_frame)
            filter_item_frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Etiqueta
            label = ttk.Label(filter_item_frame, text=display_name, font=("Arial", 9, "bold"))
            label.pack(anchor="w")
            
            # Entrada de filtro
            entry = ttk.Entry(filter_item_frame, width=15)
            entry.pack(fill=tk.X)
            
            # Vincular evento de tecla para filtrado en tiempo real
            entry.bind("<KeyRelease>", lambda e, k=key: self.apply_filters())
            
            # Guardar referencia
            self.filter_entries[key] = entry
    
    def load_report_data(self):
        """Carga los datos del reporte seleccionado"""
        try:
            if self.current_report_type == "cards":
                self.current_data = self.report_service.get_all_cards_report()
                self._setup_columns_for_cards()
            else:  # diets
                self.current_data = self.report_service.get_all_diets_report()
                self._setup_columns_for_diets()
            
            # Aplicar filtros si existen
            self.apply_filters()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{str(e)}")
            traceback.print_exc()
            self.current_data = []
            self._clear_table()
    
    def _setup_columns_for_cards(self):
        """Configura las columnas para el reporte de tarjetas"""
        # Limpiar columnas existentes
        self._clear_table()
        
        # Definir columnas
        columns = [
            ("Número de Tarjeta", 150),
            ("PIN", 100),
            ("Balance", 120, "e"),  # 'e' para alineación derecha
            ("Estado", 120)
        ]
        
        # Configurar columnas
        col_ids = ["#{}".format(i+1) for i in range(len(columns))]
        self.tree["columns"] = col_ids
        
        for i, (text, width, *align) in enumerate(columns):
            col_id = col_ids[i]
            anchor = "e" if align and align[0] == "e" else "w"
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, anchor=anchor)
    
    def _setup_columns_for_diets(self):
        """Configura las columnas para el reporte de dietas"""
        # Limpiar columnas existentes
        self._clear_table()
        
        # Definir columnas
        columns = [
            ("No. Anticipo", 100, "c"),  # 'c' para centrado
            ("No. Liquidación", 120, "c"),
            ("Descripción", 200),
            ("Solicitante", 150),
            ("Departamento", 150),
            ("Fecha Inicio", 100, "c"),
            ("Fecha Fin", 100, "c"),
            ("Fecha Solicitud", 120, "c"),
            ("Fecha Liquidación", 120, "c"),
            ("Monto Solicitado", 120, "e")
        ]
        
        # Configurar columnas
        col_ids = ["#{}".format(i+1) for i in range(len(columns))]
        self.tree["columns"] = col_ids
        
        for i, (text, width, *align) in enumerate(columns):
            col_id = col_ids[i]
            if align and align[0] == "e":
                anchor = "e"
            elif align and align[0] == "c":
                anchor = "center"
            else:
                anchor = "w"
            
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, anchor=anchor)
    
    def _clear_table(self):
        """Limpia la tabla completamente"""
        # Eliminar todas las columnas
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
        
        # Eliminar todas las filas
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def apply_filters(self):
        """Aplica los filtros de todas las columnas"""
        if not self.current_data:
            return
        
        # Obtener valores de filtro
        filters = {}
        for key, entry in self.filter_entries.items():
            value = entry.get().strip()
            if value:
                filters[key] = value
        
        try:
            # Filtrar datos
            if self.current_report_type == "cards":
                filtered_data = self.report_service.filter_cards_report(filters)
            else:  # diets
                filtered_data = self.report_service.filter_diets_report(filters)
            
            # Actualizar tabla
            self._populate_table(filtered_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros:\n{str(e)}")
    
    def _populate_table(self, data):
        """Pobla la tabla con los datos proporcionados"""
        # Limpiar filas existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not data:
            return
        
        # Insertar datos
        for item in data:
            if self.current_report_type == "cards":
                values = (
                    item.get("numero_tarjeta", ""),
                    item.get("pin", ""),
                    item.get("balance", ""),
                    item.get("estado", "")
                )
            else:  # diets
                values = (
                    item.get("no_anticipo", ""),
                    item.get("no_liquidacion", ""),
                    item.get("descripcion", ""),
                    item.get("solicitante", ""),
                    item.get("departamento", ""),
                    item.get("fecha_inicio", ""),
                    item.get("fecha_fin", ""),
                    item.get("fecha_solicitud", ""),
                    item.get("fecha_liquidacion", ""),
                    item.get("monto_solicitado", "")
                )
            
            self.tree.insert("", tk.END, values=values)
        
        # Actualizar contador
        self.update_status_bar(len(data))
    
    def update_status_bar(self, count):
        """Actualiza la barra de estado con el conteo de registros"""
        # Puedes implementar una barra de estado si es necesario
        pass
    
    def clear_filters(self):
        """Limpia todos los filtros"""
        for entry in self.filter_entries.values():
            entry.delete(0, tk.END)
        
        # Aplicar filtros (que ahora estarán vacíos)
        self.apply_filters()
    
    def refresh_report(self):
        """Refresca el reporte actual"""
        self.load_report_data()
    
    def on_item_selected(self, event):
        """Maneja la selección de un item en la tabla"""
        selection = self.tree.selection()
        if not selection:
            return
         
    def update_export_button(self):
        """Actualiza el botón de exportación"""
        # Limpiar frame del botón
        for widget in self.export_button_frame.winfo_children():
            widget.destroy()
        
        # Solo mostrar para reporte de dietas
        if self.current_report_type == "diets":
            title = "Reporte de Dietas - Sistema de Gestión de Dietas"
            create_export_button(
                self.export_button_frame,
                self.tree,
                title,
                button_text="📤 Exportar Reporte de Dietas",
                pack_options={'side': tk.RIGHT, 'padx': 5, 'pady': 5},
                include_print=True
            )
    
    def show_initial_message(self):
        """Muestra mensaje inicial"""
        self._clear_table()
        
        # Mostrar mensaje en la tabla
        self.tree["columns"] = ("#1",)
        self.tree.heading("#1", text="Seleccione un tipo de reporte")
        self.tree.column("#1", width=400, anchor="center")
        
        self.tree.insert("", tk.END, values=("👈 Use los botones de arriba para seleccionar el tipo de reporte",))
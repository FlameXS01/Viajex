import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any
import traceback
from datetime import datetime
from tkcalendar import DateEntry
from presentation.gui.utils.data_exporter import TreeviewExporter, create_export_button


class ReportModule(ttk.Frame):
    
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
        
        self.current_data = []
        self.current_report_type = None
        self.filter_entries = {}
        
        self.create_widgets()
        self.show_initial_message()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_report_selector(main_frame)
        
        self.date_filter_frame = ttk.LabelFrame(main_frame, text="📅 Filtro por Rango de Fechas")
        
        self.filter_frame = ttk.LabelFrame(main_frame, text="🔍 Filtros por Columna")
        self.filter_frame.pack(fill=tk.X, pady=(10, 5))
        
        self._create_date_filter_widgets()
        
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        self._create_table(table_frame)
        
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.export_button_frame = ttk.Frame(self.button_frame)
        self.export_button_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.button_frame, text="🔄 Actualizar", 
                  command=self.refresh_report).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(self.button_frame, text="🧹 Limpiar Filtros", 
                  command=self.clear_filters).pack(side=tk.RIGHT, padx=5)
    
    def _create_report_selector(self, parent):
        selector_frame = ttk.LabelFrame(parent, text="📊 Tipo de Reporte")
        selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.report_type_var = tk.StringVar(value="cards")
        
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
    
    def on_report_type_changed(self):
        report_type = self.report_type_var.get()
        self.current_report_type = report_type
        
        if report_type == "diets":
            self.date_filter_frame.pack(fill=tk.X, pady=(10, 5), before=self.filter_frame)
        else:
            self.date_filter_frame.pack_forget()
        
        self.update_filter_fields()
        self.load_report_data()
        self.update_export_button()
    
    def _create_date_filter_widgets(self):
        self.date_filter_type = tk.StringVar(value="solicitud")
        
        type_frame = ttk.Frame(self.date_filter_frame)
        type_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        ttk.Label(type_frame, text="Filtrar por:").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            type_frame, 
            text="Fecha de Solicitud", 
            variable=self.date_filter_type, 
            value="solicitud",
            command=self.apply_date_filter
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            type_frame, 
            text="Fecha de Liquidación", 
            variable=self.date_filter_type, 
            value="liquidacion",
            command=self.apply_date_filter
        ).pack(side=tk.LEFT, padx=5)
        
        range_frame = ttk.Frame(self.date_filter_frame)
        range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(range_frame, text="Desde:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.date_from_entry = DateEntry(
            range_frame,
            date_pattern='dd/mm/yyyy',
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            locale='es_ES'
        )
        self.date_from_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(range_frame, text="Hasta:").pack(side=tk.LEFT, padx=(10, 5))
        
        self.date_to_entry = DateEntry(
            range_frame,
            date_pattern='dd/mm/yyyy',
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            locale='es_ES'
        )
        self.date_to_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            range_frame, 
            text="Aplicar Filtro de Fechas", 
            command=self.apply_date_filter
        ).pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Button(
            range_frame, 
            text="Limpiar Fechas", 
            command=self.clear_date_filter
        ).pack(side=tk.LEFT, padx=5)
        
        self.date_from_entry.bind("<<DateEntrySelected>>", lambda e: self.apply_date_filter())
        self.date_to_entry.bind("<<DateEntrySelected>>", lambda e: self.apply_date_filter())
    
    def _create_table(self, parent):
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(table_container, show="headings")
        
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)
    
    def update_filter_fields(self):
        for widget in self.filter_frame.winfo_children():
            widget.destroy()
        
        self.filter_entries.clear()
        
        if self.current_report_type == "cards":
            columns = [
                ("Número de Tarjeta", "numero_tarjeta", 150, "entry"),
                ("PIN", "pin", 100, "entry"),
                ("Balance", "balance", 120, "entry"),
                ("Estado", "estado", 120, "entry")
            ]
            filters_per_row = 4
        else:
            columns = [
                ("No.A", "no_anticipo", 100, "entry"),
                ("No.L", "no_liquidacion", 120, "entry"),
                ("Descripción", "descripcion", 200, "entry"),
                ("Solicitante", "solicitante", 150, "entry"),
                ("Departamento", "departamento", 150, "entry"),
                ("Fecha Inicio", "fecha_inicio", 100, "entry"),
                ("Fecha Fin", "fecha_fin", 100, "entry"),
                ("Fecha Solicitud", "fecha_solicitud", 120, "entry"),
                ("Fecha Liquidación", "fecha_liquidacion", 120, "entry"),
                ("Estado", "estado", 120, "combobox") 
            ]
            filters_per_row = max(7, min(14, self.filter_frame.winfo_width() // 160))
        
        for idx, (display_name, key, width, widget_type) in enumerate(columns):
            row = idx // filters_per_row
            col = idx % filters_per_row
            
            filter_item_frame = ttk.Frame(self.filter_frame)
            filter_item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            label = ttk.Label(filter_item_frame, text=display_name, font=("Arial", 9, "bold"))
            label.pack(anchor="w")
            
            if widget_type == "combobox" and key == "estado":
                combo = ttk.Combobox(filter_item_frame, width=13, state="readonly")
                combo['values'] = ("Todas", "Solicitadas", "Liquidadas")
                combo.set("Todas")
                combo.pack(fill=tk.X)
                combo.bind("<<ComboboxSelected>>", lambda e, k=key: self.apply_filters())
                self.filter_entries[key] = combo
            else:
                entry = ttk.Entry(filter_item_frame, width=15)
                entry.pack(fill=tk.X)
                entry.bind("<KeyRelease>", lambda e, k=key: self.apply_filters())
                self.filter_entries[key] = entry
        
        for i in range(filters_per_row):
            self.filter_frame.columnconfigure(i, weight=1)
    
    def load_report_data(self):
        try:
            if self.current_report_type == "cards":
                self.current_data = self.report_service.get_all_cards_report()
                self._setup_columns_for_cards()
                self.clear_date_filter()
            else:
                self.current_data = self.report_service.get_all_diets_report()
                self._setup_columns_for_diets()
            
            self.apply_filters()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{str(e)}")
            traceback.print_exc()
            self.current_data = []
            self._clear_table()
    
    def _setup_columns_for_cards(self):
        self._clear_table()
        
        columns = [
            ("Número de Tarjeta", 150),
            ("PIN", 100),
            ("Balance", 120, "e"),
            ("Estado", 120)
        ]
        
        col_ids = ["#{}".format(i+1) for i in range(len(columns))]
        self.tree["columns"] = col_ids
        
        for i, (text, width, *align) in enumerate(columns):
            col_id = col_ids[i]
            anchor = "e" if align and align[0] == "e" else "w"
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, anchor=anchor)
    
    def _setup_columns_for_diets(self):
        self._clear_table()
        
        columns = [
            ("No.A", 100, "c"),
            ("No.L", 120, "c"),
            ("Descripción", 200),
            ("Solicitante", 150),
            ("Departamento", 150),
            ("Fecha Inicio", 100, "c"),
            ("Fecha Fin", 100, "c"),
            ("Fecha Solicitud", 120, "c"),
            ("Fecha Liquidación", 120, "c"),
            ("S.E", 120, "e"),
            ("S.T", 120, "e"),
            ("G.E", 120, "e"),
            ("G.T", 120, "e"),
            ("Monto", 120, "e"),
            ("Estado", 120, "e")
        ]
        
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
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def apply_filters(self):
        if not self.current_data:
            return
        
        filters = {}
        for key, widget in self.filter_entries.items():
            value = widget.get().strip()
            
            if key == "estado" and self.current_report_type == "diets":
                if value == "Todas":
                    continue
                elif value == "Solicitadas":
                    value = "REQUESTED"
                elif value == "Liquidadas":
                    value = "LIQUIDATED"
            
            if value:
                filters[key] = value
        
        try:
            if self.current_report_type == "cards":
                filtered_data = self.report_service.filter_cards_report(filters)
            else:
                filtered_data = self.report_service.filter_diets_report(filters)
            
            self._populate_table(filtered_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros:\n{str(e)}")
    
    def apply_date_filter(self):
        if self.current_report_type != "diets" or not self.current_data:
            return
        
        try:
            date_from_obj = self.date_from_entry.get_date()
            date_to_obj = self.date_to_entry.get_date()
            
            date_from_str = date_from_obj.strftime("%d/%m/%Y")
            date_to_str = date_to_obj.strftime("%d/%m/%Y")
        except Exception:
            date_from_str = ""
            date_to_str = ""
        
        filter_type = self.date_filter_type.get()
        
        if not date_from_str and not date_to_str:
            self.apply_filters()
            return
        
        try:
            date_from = None
            date_to = None
            
            if date_from_str:
                date_from = datetime.strptime(date_from_str, "%d/%m/%Y")
            
            if date_to_str:
                date_to = datetime.strptime(date_to_str, "%d/%m/%Y")
            
            filtered_data = []
            for item in self.current_data:
                if filter_type == "solicitud":
                    date_str = item.get("fecha_solicitud", "")
                else:
                    date_str = item.get("fecha_liquidacion", "")
                
                if not date_str or date_str == "N/A":
                    continue
                
                try:
                    item_date = datetime.strptime(date_str, "%d/%m/%Y")
                except ValueError:
                    continue
                
                in_range = True
                
                if date_from and item_date < date_from:
                    in_range = False
                
                if date_to and item_date > date_to:
                    in_range = False
                
                if in_range:
                    filtered_data.append(item)
            
            self._populate_table(filtered_data)
            
        except ValueError:
            messagebox.showwarning("Formato inválido", "Por favor ingrese fechas en formato dd/mm/yyyy")
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtro de fechas:\n{str(e)}")
    
    def _populate_table(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not data:
            return
        
        for item in data:
            if self.current_report_type == "cards":
                values = (
                    item.get("numero_tarjeta", ""),
                    item.get("pin", ""),
                    item.get("balance", ""),
                    item.get("estado", "")
                )
            else:
                estado_raw = item.get("estado", "").upper()
                if estado_raw == "LIQUIDATED":
                    estado = "Liquidado"
                elif estado_raw == "REQUESTED":
                    estado = "Solicitado"
                else:
                    estado = estado_raw

                monto = item.get("raw_gasto", "0.0") 

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
                    item.get("monto_solicitado_efec", ""),
                    item.get("monto_solicitado_card", ""), 
                    item.get("gasto_efec", ""),   
                    item.get("gasto_card", ""),
                    monto,
                    estado
                )
            
            self.tree.insert("", tk.END, values=values)
        
        self.update_status_bar(len(data))
    
    def update_status_bar(self, count):
        pass
    
    def clear_filters(self):
        for key, widget in self.filter_entries.items():
            if isinstance(widget, ttk.Combobox) and key == "estado" and self.current_report_type == "diets":
                widget.set("Todas")
            else:
                widget.delete(0, tk.END)
        
        if self.current_report_type == "diets":
            self.clear_date_filter()
        else:
            self.apply_filters()
    
    def clear_date_filter(self):
        today = datetime.now()
        
        self.date_from_entry.set_date(today)
        self.date_to_entry.set_date(today)
        
        self.date_filter_type.set("solicitud")
        
        if self.current_report_type == "diets":
            self.apply_filters()
    
    def refresh_report(self):
        self.load_report_data()
    
    def on_item_selected(self, event):
        selection = self.tree.selection()
        if not selection:
            return
    
    def update_export_button(self):
        for widget in self.export_button_frame.winfo_children():
            widget.destroy()
        
        if self.current_report_type == "diets":
            title = "Reportes Generales"
            create_export_button(
                self.export_button_frame,
                self.tree,
                title,
                button_text="📤 Exportar Reporte",
                pack_options={'side': tk.RIGHT, 'padx': 5, 'pady': 5},
                include_print=True, 
                export_type='report_module'
            )
    
    def show_initial_message(self):
        self._clear_table()
        
        self.tree["columns"] = ("#1",)
        self.tree.heading("#1", text="Seleccione un tipo de reporte")
        self.tree.column("#1", width=400, anchor="center")
        
        self.tree.insert("", tk.END, values=("👈 Use los botones de arriba para seleccionar el tipo de reporte",))
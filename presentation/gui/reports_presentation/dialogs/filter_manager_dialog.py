"""
filter_manager_dialog.py
Diálogo para gestionar filtros guardados para reportes.
Permite guardar, cargar, editar y eliminar configuraciones de filtros.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog


class FilterManagerDialog(BaseReportDialog):
    """Diálogo para gestionar filtros guardados de reportes"""
    
    def __init__(self, parent, 
                 report_name: str = "Reporte",
                 available_filters: Optional[List[Dict[str, Any]]] = None):
        """
        Inicializa el diálogo para gestión de filtros.
        
        Args:
            parent: Ventana padre
            report_name: Nombre del reporte asociado
            available_filters: Lista de filtros disponibles
        """
        self.report_name = report_name
        
        # Filtros de ejemplo organizados por categoría
        self.available_filters = available_filters or [
            {
                'id': 1,
                'name': 'Tarjetas Vencidas',
                'category': 'Tarjetas',
                'description': 'Filtra tarjetas con anticipos vencidos',
                'created_by': 'admin',
                'created_date': '2024-01-15',
                'usage_count': 42,
                'is_shared': True,
                'filters': {
                    'advance_status': 'vencidos',
                    'min_days': 3,
                    'highlight_expired': True
                }
            },
            {
                'id': 2,
                'name': 'Anticipos Pendientes',
                'category': 'Anticipos',
                'description': 'Anticipos sin liquidar por departamento',
                'created_by': 'contabilidad',
                'created_date': '2024-01-20',
                'usage_count': 28,
                'is_shared': True,
                'filters': {
                    'advance_status': 'pendientes',
                    'include_subdepts': True,
                    'department': 'TODOS'
                }
            },
            {
                'id': 3,
                'name': 'Reporte Mensual Comercial',
                'category': 'Departamentos',
                'description': 'Configuración para reporte mensual de gerencia comercial',
                'created_by': 'comercial',
                'created_date': '2024-02-01',
                'usage_count': 15,
                'is_shared': True,
                'filters': {
                    'department': '16',
                    'period_type': 'mes_actual',
                    'include_comparisons': True
                }
            },
            {
                'id': 4,
                'name': 'Mi Filtro Personal',
                'category': 'Personal',
                'description': 'Configuración personalizada para análisis rápido',
                'created_by': 'usuario_actual',
                'created_date': '2024-02-10',
                'usage_count': 8,
                'is_shared': False,
                'filters': {
                    'min_amount': 1000,
                    'max_amount': 10000,
                    'expense_type': 'tarjetas'
                }
            }
        ]
        
        super().__init__(parent, f"Gestor de Filtros: {report_name}", width=800, height=700)
    
    def _create_widgets(self) -> None:
        """Crea los widgets del diálogo."""
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar expansión
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título descriptivo
        ttk.Label(
            main_frame,
            text=f"Gestor de Filtros Guardados: {self.report_name}",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Información del gestor
        info_text = "💾 Gestione sus configuraciones de filtros guardadas.\n"
        info_text += "Guarde configuraciones frecuentes para aplicarlas rápidamente en el futuro."
        
        ttk.Label(
            main_frame,
            text=info_text,
            font=('Arial', 9),
            foreground='darkgreen'
        ).grid(row=1, column=0, sticky="w", pady=(0, 20))
        
        # Frame para controles superiores
        top_controls_frame = ttk.Frame(main_frame)
        top_controls_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        # Búsqueda
        ttk.Label(top_controls_frame, text="Buscar:").pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            top_controls_frame,
            textvariable=self.search_var,
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=(5, 20))
        search_entry.bind('<KeyRelease>', self._on_search)
        
        # Categorías
        ttk.Label(top_controls_frame, text="Categoría:").pack(side=tk.LEFT)
        
        categories = ["Todas", "Tarjetas", "Anticipos", "Departamentos", "Personal", "Compartidos", "Frecuentes"]
        self.category_var = tk.StringVar(value="Todas")
        category_combo = ttk.Combobox(
            top_controls_frame,
            textvariable=self.category_var,
            values=categories,
            state='readonly',
            width=15
        )
        category_combo.pack(side=tk.LEFT, padx=(5, 0))
        category_combo.bind('<<ComboboxSelected>>', self._on_category_change)
        
        # Ordenar por
        ttk.Label(top_controls_frame, text="Ordenar por:").pack(side=tk.LEFT, padx=(20, 5))
        
        sort_options = ["Nombre (A-Z)", "Nombre (Z-A)", "Más usados", "Más recientes", "Creador"]
        self.sort_var = tk.StringVar(value="Más usados")
        sort_combo = ttk.Combobox(
            top_controls_frame,
            textvariable=self.sort_var,
            values=sort_options,
            state='readonly',
            width=15
        )
        sort_combo.pack(side=tk.LEFT)
        sort_combo.bind('<<ComboboxSelected>>', self._on_sort_change)
        
        # Frame principal con pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=3, column=0, sticky="nsew", pady=(0, 15))
        
        # Configurar expansión
        main_frame.rowconfigure(3, weight=1)
        
        # Pestaña 1: Lista de filtros
        list_frame = ttk.Frame(notebook, padding="10")
        notebook.add(list_frame, text="Lista de Filtros")
        
        # Treeview para mostrar filtros
        columns = ("Nombre", "Categoría", "Descripción", "Creador", "Usos", "Compartido")
        self.filters_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=15,
            selectmode="browse"
        )
        
        # Configurar columnas
        col_widths = [150, 100, 250, 100, 60, 80]
        for col, width in zip(columns, col_widths):
            self.filters_tree.heading(col, text=col)
            self.filters_tree.column(col, width=width, minwidth=50)
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.filters_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.filters_tree.xview)
        self.filters_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid para treeview y scrollbars
        self.filters_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configurar expansión
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Pestaña 2: Vista detallada
        detail_frame = ttk.Frame(notebook, padding="10")
        notebook.add(detail_frame, text="Detalle del Filtro")
        
        # Configurar expansión
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(1, weight=1)
        
        # Información básica del filtro seleccionado
        self.detail_info_frame = ttk.LabelFrame(detail_frame, text="Información del Filtro", padding="10")
        self.detail_info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Labels para información
        self.detail_name_var = tk.StringVar(value="Seleccione un filtro")
        self.detail_category_var = tk.StringVar()
        self.detail_creator_var = tk.StringVar()
        self.detail_date_var = tk.StringVar()
        self.detail_usage_var = tk.StringVar()
        self.detail_shared_var = tk.StringVar()
        self.detail_desc_var = tk.StringVar()
        
        ttk.Label(self.detail_info_frame, text="Nombre:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ttk.Label(self.detail_info_frame, textvariable=self.detail_name_var, 
                 font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky="w")
        
        ttk.Label(self.detail_info_frame, text="Categoría:").grid(row=0, column=2, sticky="w", padx=(20, 5))
        ttk.Label(self.detail_info_frame, textvariable=self.detail_category_var).grid(row=0, column=3, sticky="w")
        
        ttk.Label(self.detail_info_frame, text="Creador:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        ttk.Label(self.detail_info_frame, textvariable=self.detail_creator_var).grid(row=1, column=1, sticky="w")
        
        ttk.Label(self.detail_info_frame, text="Fecha creación:").grid(row=1, column=2, sticky="w", padx=(20, 5))
        ttk.Label(self.detail_info_frame, textvariable=self.detail_date_var).grid(row=1, column=3, sticky="w")
        
        ttk.Label(self.detail_info_frame, text="Usos:").grid(row=2, column=0, sticky="w", padx=(0, 5))
        ttk.Label(self.detail_info_frame, textvariable=self.detail_usage_var).grid(row=2, column=1, sticky="w")
        
        ttk.Label(self.detail_info_frame, text="Compartido:").grid(row=2, column=2, sticky="w", padx=(20, 5))
        ttk.Label(self.detail_info_frame, textvariable=self.detail_shared_var).grid(row=2, column=3, sticky="w")
        
        # Descripción
        ttk.Label(self.detail_info_frame, text="Descripción:").grid(row=3, column=0, sticky="nw", padx=(0, 5), pady=(10, 0))
        desc_label = ttk.Label(self.detail_info_frame, textvariable=self.detail_desc_var, wraplength=600)
        desc_label.grid(row=3, column=1, columnspan=3, sticky="w", pady=(10, 0), padx=(0, 0))
        
        # Parámetros del filtro
        params_frame = ttk.LabelFrame(detail_frame, text="Parámetros Configurados", padding="10")
        params_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        # Configurar expansión
        params_frame.columnconfigure(0, weight=1)
        params_frame.rowconfigure(0, weight=1)
        
        # Área de texto para parámetros
        self.params_text = scrolledtext.ScrolledText(
            params_frame,
            wrap=tk.WORD,
            width=80,
            height=10,
            font=('Courier', 9),
            state='disabled'
        )
        self.params_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame para botones de acción en detalle
        detail_actions_frame = ttk.Frame(detail_frame)
        detail_actions_frame.grid(row=2, column=0, sticky="ew")
        
        ttk.Button(
            detail_actions_frame,
            text="Aplicar Este Filtro",
            command=self._apply_selected_filter,
            width=18
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            detail_actions_frame,
            text="Editar Filtro",
            command=self._edit_filter,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            detail_actions_frame,
            text="Crear Copia",
            command=self._create_copy,
            width=15
        ).pack(side=tk.LEFT)
        
        # Pestaña 3: Nuevo filtro
        new_frame = ttk.Frame(notebook, padding="10")
        notebook.add(new_frame, text="Guardar Nuevo Filtro")
        
        # Formulario para nuevo filtro
        form_frame = ttk.LabelFrame(new_frame, text="Información del Nuevo Filtro", padding="15")
        form_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Nombre del filtro
        ttk.Label(form_frame, text="Nombre del filtro:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=10)
        self.new_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.new_name_var, width=40).grid(row=0, column=1, sticky="w", pady=10)
        
        # Categoría
        ttk.Label(form_frame, text="Categoría:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=10)
        self.new_category_var = tk.StringVar(value="Personal")
        category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.new_category_var,
            values=["Personal", "Tarjetas", "Anticipos", "Departamentos", "Comercial", "Financiero", "Otros"],
            state='readonly',
            width=20
        )
        category_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=2, column=0, sticky="nw", padx=(0, 10), pady=10)
        self.new_desc_text = scrolledtext.ScrolledText(
            form_frame,
            wrap=tk.WORD,
            width=40,
            height=4,
            font=('Arial', 9)
        )
        self.new_desc_text.grid(row=2, column=1, sticky="w", pady=10)
        self.new_desc_text.insert(1.0, "Descripción del filtro...")
        
        # Compartir
        self.new_shared_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            form_frame,
            text="Compartir este filtro con otros usuarios",
            variable=self.new_shared_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Parámetros actuales
        current_frame = ttk.LabelFrame(new_frame, text="Parámetros Actuales a Guardar", padding="15")
        current_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        # Configurar expansión
        new_frame.columnconfigure(0, weight=1)
        new_frame.rowconfigure(1, weight=1)
        current_frame.columnconfigure(0, weight=1)
        current_frame.rowconfigure(0, weight=1)
        
        # Área de texto para parámetros actuales
        self.current_params_text = scrolledtext.ScrolledText(
            current_frame,
            wrap=tk.WORD,
            width=80,
            height=8,
            font=('Courier', 9)
        )
        self.current_params_text.pack(fill=tk.BOTH, expand=True)
        
        # Cargar parámetros de ejemplo
        self._load_example_params()
        
        # Botón para guardar nuevo filtro
        save_frame = ttk.Frame(new_frame)
        save_frame.grid(row=2, column=0, sticky="ew")
        
        ttk.Button(
            save_frame,
            text="Guardar Filtro",
            command=self._save_new_filter,
            width=20
        ).pack(pady=10)
        
        # Frame para botones de acción principales
        action_buttons_frame = ttk.Frame(main_frame)
        action_buttons_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(
            action_buttons_frame,
            text="Cargar Filtro",
            command=self._load_selected_filter,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_buttons_frame,
            text="Eliminar Filtro",
            command=self._delete_filter,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_buttons_frame,
            text="Exportar Filtros",
            command=self._export_filters,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_buttons_frame,
            text="Importar Filtros",
            command=self._import_filters,
            width=15
        ).pack(side=tk.LEFT)
        
        # Frame para botones principales
        self.button_frame.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        
        # Cambiar texto del botón Aceptar
        self.accept_button.config(text="Cerrar Gestor")
        
        # Cargar filtros en el treeview
        self._load_filters()
        
        # Bind eventos
        self.filters_tree.bind('<<TreeviewSelect>>', self._on_filter_select)
    
    def _load_filters(self) -> None:
        """Carga los filtros en el treeview."""
        # Limpiar treeview
        for item in self.filters_tree.get_children():
            self.filters_tree.delete(item)
        
        # Aplicar filtros
        filtered_filters = self._apply_filters()
        
        # Aplicar ordenamiento
        sorted_filters = self._apply_sorting(filtered_filters)
        
        # Insertar en treeview
        for filtro in sorted_filters:
            shared_text = "Sí" if filtro['is_shared'] else "No"
            self.filters_tree.insert(
                "", "end",
                iid=str(filtro['id']),
                values=(
                    filtro['name'],
                    filtro['category'],
                    filtro['description'][:50] + "..." if len(filtro['description']) > 50 else filtro['description'],
                    filtro['created_by'],
                    filtro['usage_count'],
                    shared_text
                )
            )
    
    def _apply_filters(self) -> List[Dict[str, Any]]:
        """Aplica los filtros de búsqueda y categoría."""
        search_term = self.search_var.get().lower()
        category = self.category_var.get()
        
        filtered = []
        for filtro in self.available_filters:
            # Filtrar por búsqueda
            if search_term:
                searchable = (
                    filtro['name'].lower() + 
                    filtro['description'].lower() + 
                    filtro['category'].lower() + 
                    filtro['created_by'].lower()
                )
                if search_term not in searchable:
                    continue
            
            # Filtrar por categoría
            if category != "Todas":
                if category == "Compartidos" and not filtro['is_shared']:
                    continue
                elif category == "Frecuentes" and filtro['usage_count'] < 10:
                    continue
                elif category not in ["Compartidos", "Frecuentes"] and filtro['category'] != category:
                    continue
            
            filtered.append(filtro)
        
        return filtered
    
    def _apply_sorting(self, filters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aplica el ordenamiento seleccionado."""
        sort_by = self.sort_var.get()
        
        if sort_by == "Nombre (A-Z)":
            return sorted(filters, key=lambda x: x['name'].lower())
        elif sort_by == "Nombre (Z-A)":
            return sorted(filters, key=lambda x: x['name'].lower(), reverse=True)
        elif sort_by == "Más usados":
            return sorted(filters, key=lambda x: x['usage_count'], reverse=True)
        elif sort_by == "Más recientes":
            return sorted(filters, key=lambda x: x['created_date'], reverse=True)
        elif sort_by == "Creador":
            return sorted(filters, key=lambda x: x['created_by'].lower())
        else:
            return filters
    
    def _on_search(self, event=None) -> None:
        """Actualiza la lista cuando se realiza una búsqueda."""
        self._load_filters()
    
    def _on_category_change(self, event=None) -> None:
        """Actualiza la lista cuando cambia la categoría."""
        self._load_filters()
    
    def _on_sort_change(self, event=None) -> None:
        """Actualiza la lista cuando cambia el ordenamiento."""
        self._load_filters()
    
    def _on_filter_select(self, event=None) -> None:
        """Actualiza el detalle cuando se selecciona un filtro."""
        selection = self.filters_tree.selection()
        if not selection:
            return
        
        filter_id = selection[0]
        filtro = next((f for f in self.available_filters if str(f['id']) == filter_id), None)
        
        if filtro:
            # Actualizar información básica
            self.detail_name_var.set(filtro['name'])
            self.detail_category_var.set(filtro['category'])
            self.detail_creator_var.set(filtro['created_by'])
            self.detail_date_var.set(filtro['created_date'])
            self.detail_usage_var.set(str(filtro['usage_count']))
            self.detail_shared_var.set("Sí" if filtro['is_shared'] else "No")
            self.detail_desc_var.set(filtro['description'])
            
            # Actualizar parámetros
            self.params_text.config(state='normal')
            self.params_text.delete(1.0, tk.END)
            
            # Formatear parámetros JSON
            import json
            formatted_params = json.dumps(filtro['filters'], indent=2, ensure_ascii=False)
            self.params_text.insert(1.0, formatted_params)
            self.params_text.config(state='disabled')
    
    def _load_example_params(self) -> None:
        """Carga parámetros de ejemplo en el formulario nuevo."""
        import json
        
        example_params = {
            "report_name": self.report_name,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "entidad": "CIMEX - Gerencia Administrativa",
            "filters": {
                "advance_status": "pendientes",
                "min_amount": 1000,
                "max_amount": 10000,
                "include_totals": True,
                "output_format": "Pantalla"
            },
            "saved_by": "usuario_actual",
            "saved_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        formatted = json.dumps(example_params, indent=2, ensure_ascii=False)
        self.current_params_text.delete(1.0, tk.END)
        self.current_params_text.insert(1.0, formatted)
    
    def _apply_selected_filter(self) -> None:
        """Aplica el filtro seleccionado."""
        selection = self.filters_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un filtro para aplicar", parent=self)
            return
        
        filter_id = selection[0]
        filtro = next((f for f in self.available_filters if str(f['id']) == filter_id), None)
        
        if filtro:
            # Incrementar contador de uso
            filtro['usage_count'] += 1
            
            messagebox.showinfo(
                "Filtro Aplicado",
                f"Se aplicó el filtro '{filtro['name']}'.\n\n"
                f"Los parámetros configurados han sido cargados en el reporte.",
                parent=self
            )
            
            # Recargar lista para actualizar contador
            self._load_filters()
    
    def _load_selected_filter(self) -> None:
        """Carga el filtro seleccionado para edición."""
        selection = self.filters_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un filtro para cargar", parent=self)
            return
        
        filter_id = selection[0]
        filtro = next((f for f in self.available_filters if str(f['id']) == filter_id), None)
        
        if filtro:
            # Incrementar contador de uso
            filtro['usage_count'] += 1
            
            # Cargar en formulario nuevo (para edición)
            self.new_name_var.set(filtro['name'])
            self.new_category_var.set(filtro['category'])
            self.new_desc_text.delete(1.0, tk.END)
            self.new_desc_text.insert(1.0, filtro['description'])
            self.new_shared_var.set(filtro['is_shared'])
            
            # Cambiar a pestaña de nuevo filtro
            notebook = self.filters_tree.master.master.master  # Acceder al notebook
            notebook.select(2)  # Índice de la pestaña "Nuevo filtro"
            
            # Cargar parámetros en área de texto
            import json
            formatted_params = json.dumps(filtro['filters'], indent=2, ensure_ascii=False)
            self.current_params_text.delete(1.0, tk.END)
            self.current_params_text.insert(1.0, formatted_params)
            
            messagebox.showinfo(
                "Filtro Cargado",
                f"Filtro '{filtro['name']}' cargado para edición.\n"
                f"Contador de uso incrementado a {filtro['usage_count']}.",
                parent=self
            )
            
            # Recargar lista para actualizar contador
            self._load_filters()
    
    def _edit_filter(self) -> None:
        """Edita el filtro seleccionado."""
        selection = self.filters_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un filtro para editar", parent=self)
            return
        
        filter_id = selection[0]
        filtro = next((f for f in self.available_filters if str(f['id']) == filter_id), None)
        
        if filtro:
            # Obtener nuevos valores
            new_name = self.detail_name_var.get()
            new_desc = self.detail_desc_var.get()
            
            if new_name != filtro['name'] or new_desc != filtro['description']:
                filtro['name'] = new_name
                filtro['description'] = new_desc
                
                messagebox.showinfo(
                    "Filtro Editado",
                    f"El filtro ha sido actualizado correctamente.",
                    parent=self
                )
                
                # Recargar lista
                self._load_filters()
            else:
                messagebox.showinfo(
                    "Sin Cambios",
                    "No se detectaron cambios en el filtro.",
                    parent=self
                )
    
    def _create_copy(self) -> None:
        """Crea una copia del filtro seleccionado."""
        selection = self.filters_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un filtro para copiar", parent=self)
            return
        
        filter_id = selection[0]
        original = next((f for f in self.available_filters if str(f['id']) == filter_id), None)
        
        if original:
            # Crear nueva ID
            new_id = max(f['id'] for f in self.available_filters) + 1
            
            # Crear copia
            import copy
            new_filter = copy.deepcopy(original)
            new_filter['id'] = new_id
            new_filter['name'] = f"Copia de {original['name']}"
            new_filter['created_by'] = "usuario_actual"
            new_filter['created_date'] = datetime.now().strftime("%Y-%m-%d")
            new_filter['usage_count'] = 0
            new_filter['is_shared'] = False
            
            # Agregar a la lista
            self.available_filters.append(new_filter)
            
            messagebox.showinfo(
                "Copia Creada",
                f"Se creó una copia del filtro '{original['name']}'.\n"
                f"La copia se ha agregado a sus filtros personales.",
                parent=self
            )
            
            # Recargar lista
            self._load_filters()
    
    def _save_new_filter(self) -> None:
        """Guarda un nuevo filtro."""
        # Validar campos
        name = self.new_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "El nombre del filtro es requerido", parent=self)
            return
        
        category = self.new_category_var.get()
        description = self.new_desc_text.get(1.0, tk.END).strip()
        is_shared = self.new_shared_var.get()
        
        # Obtener parámetros del área de texto
        params_text = self.current_params_text.get(1.0, tk.END).strip()
        
        try:
            import json
            params = json.loads(params_text)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Los parámetros no tienen un formato JSON válido", parent=self)
            return
        
        # Crear nuevo filtro
        new_id = max(f['id'] for f in self.available_filters) + 1
        
        new_filter = {
            'id': new_id,
            'name': name,
            'category': category,
            'description': description,
            'created_by': 'usuario_actual',
            'created_date': datetime.now().strftime("%Y-%m-%d"),
            'usage_count': 0,
            'is_shared': is_shared,
            'filters': params.get('filters', params)  # Manejar ambos formatos
        }
        
        # Agregar a la lista
        self.available_filters.append(new_filter)
        
        messagebox.showinfo(
            "Filtro Guardado",
            f"El filtro '{name}' ha sido guardado exitosamente.\n\n"
            f"Categoría: {category}\n"
            f"Compartido: {'Sí' if is_shared else 'No'}\n"
            f"Parámetros guardados: {len(params)}",
            parent=self
        )
        
        # Limpiar formulario
        self.new_name_var.set("")
        self.new_category_var.set("Personal")
        self.new_desc_text.delete(1.0, tk.END)
        self.new_desc_text.insert(1.0, "Descripción del filtro...")
        self.new_shared_var.set(False)
        
        # Recargar lista
        self._load_filters()
        
        # Cambiar a pestaña de lista
        notebook = self.filters_tree.master.master.master
        notebook.select(0)
    
    def _delete_filter(self) -> None:
        """Elimina el filtro seleccionado."""
        selection = self.filters_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un filtro para eliminar", parent=self)
            return
        
        filter_id = selection[0]
        filtro = next((f for f in self.available_filters if str(f['id']) == filter_id), None)
        
        if filtro:
            # Confirmar eliminación
            confirm = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar el filtro '{filtro['name']}'?\n\n"
                f"Categoría: {filtro['category']}\n"
                f"Usos: {filtro['usage_count']}\n"
                f"Creado por: {filtro['created_by']}\n\n"
                f"Esta acción no se puede deshacer.",
                parent=self
            )
            
            if confirm:
                # Eliminar de la lista
                self.available_filters = [f for f in self.available_filters if f['id'] != filtro['id']]
                
                messagebox.showinfo(
                    "Filtro Eliminado",
                    f"El filtro '{filtro['name']}' ha sido eliminado.",
                    parent=self
                )
                
                # Recargar lista
                self._load_filters()
                
                # Limpiar detalle
                self.detail_name_var.set("Seleccione un filtro")
                self.detail_category_var.set("")
                self.detail_creator_var.set("")
                self.detail_date_var.set("")
                self.detail_usage_var.set("")
                self.detail_shared_var.set("")
                self.detail_desc_var.set("")
                
                self.params_text.config(state='normal')
                self.params_text.delete(1.0, tk.END)
                self.params_text.config(state='disabled')
    
    def _export_filters(self) -> None:
        """Exporta los filtros a un archivo."""
        try:
            from tkinter import filedialog
            
            filepath = filedialog.asksaveasfilename(
                parent=self,
                title="Exportar filtros a archivo",
                initialfile=f"filtros_{self.report_name}_{datetime.now().strftime('%Y%m%d')}.json",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filepath:
                import json
                
                # Preparar datos para exportar
                export_data = {
                    'report_name': self.report_name,
                    'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'total_filters': len(self.available_filters),
                    'filters': self.available_filters
                }
                
                # Escribir archivo
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo(
                    "Exportación Exitosa",
                    f"Se exportaron {len(self.available_filters)} filtros a:\n{filepath}",
                    parent=self
                )
                
        except Exception as e:
            messagebox.showerror("Error de Exportación", f"No se pudo exportar: {str(e)}", parent=self)
    
    def _import_filters(self) -> None:
        """Importa filtros desde un archivo."""
        try:
            from tkinter import filedialog
            
            filepath = filedialog.askopenfilename(
                parent=self,
                title="Importar filtros desde archivo",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filepath:
                import json
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                # Validar estructura
                if 'filters' not in import_data:
                    messagebox.showerror("Error", "El archivo no contiene filtros válidos", parent=self)
                    return
                
                # Obtener nueva ID base
                current_max_id = max(f['id'] for f in self.available_filters) if self.available_filters else 0
                new_id_base = current_max_id + 1000  # Espacio para evitar conflictos
                
                # Procesar filtros importados
                imported_count = 0
                for filtro in import_data['filters']:
                    # Ajustar ID para evitar conflictos
                    filtro['id'] = new_id_base + imported_count
                    imported_count += 1
                    
                    # Agregar a la lista
                    self.available_filters.append(filtro)
                
                messagebox.showinfo(
                    "Importación Exitosa",
                    f"Se importaron {imported_count} filtros desde:\n{filepath}\n\n"
                    f"Total de filtros ahora: {len(self.available_filters)}",
                    parent=self
                )
                
                # Recargar lista
                self._load_filters()
                
        except Exception as e:
            messagebox.showerror("Error de Importación", f"No se pudo importar: {str(e)}", parent=self)
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos (siempre válido para gestor de filtros)."""
        return True
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos del gestor de filtros."""
        selected_filter = None
        selection = self.filters_tree.selection()
        if selection:
            filter_id = selection[0]
            selected_filter = next((f for f in self.available_filters if str(f['id']) == filter_id), None)
        
        return {
            'report_name': self.report_name,
            'total_filters': len(self.available_filters),
            'selected_filter': selected_filter['name'] if selected_filter else None,
            'selected_filter_id': selected_filter['id'] if selected_filter else None,
            'timestamp': datetime.now()
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Crear diálogo
    dialog = FilterManagerDialog(
        parent=root,
        report_name="Reporte de Anticipos"
    )
    result = dialog.show()
    
    if result:
        print("Gestor de Filtros:")
        print(f"  Reporte: {result['report_name']}")
        print(f"  Total filtros: {result['total_filters']}")
        if result['selected_filter']:
            print(f"  Filtro seleccionado: {result['selected_filter']} (ID: {result['selected_filter_id']})")
        else:
            print(f"  Ningún filtro seleccionado")
        print(f"  Sesión: {result['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
    else:
        print("Gestor cerrado sin acción")
    
    root.destroy()
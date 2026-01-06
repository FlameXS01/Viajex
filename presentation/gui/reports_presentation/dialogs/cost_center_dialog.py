"""
cost_center_dialog.py
Diálogo para configurar el reporte de "Centro de costo".
Muestra departamentos con códigos contables asociados.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from presentation.gui.reports_presentation.dialogs.base_report_dialog import BaseReportDialog


class CostCenterDialog(BaseReportDialog):
    """Diálogo para configurar reporte de centros de costo"""
    
    def __init__(self, parent, 
                 departments: Optional[List[Tuple[str, str, str, str]]] = None,
                 entities: Optional[List[str]] = None):
        """
        Inicializa el diálogo para reporte de centros de costo.
        
        Args:
            parent: Ventana padre
            departments: Lista de departamentos (código, nombre, ccosto, cuentas)
            entities: Lista de entidades disponibles
        """
        # Datos de ejemplo del PDF (Page 4)
        default_departments = [
            ("01", "Gerencia General", "CCS2410101", ("82244400", "82344500")),
            ("02", "Gerencia Economía", "CCS2410102", ("82244400", "82344500")),
            ("03", "Grupo Informática", "CCS2410103", ("82244400", "82344500")),
            ("04", "Gerencia R. Humanos", "CCS2410104", ("82244400", "82344500")),
            ("05", "Gerencia Auditoría", "CCS2410105", ("82344400", "82344500")),
            ("06", "Grupo Protección", "CCS2410106", ("82244400", "82344500")),
            ("09", "Gastos Generales", "CCS2410109", ("82244400", "82344500")),
            ("10", "Capacitación", "CCS2410100", ("82244400", "82344500")),
            ("11", "Grupo Fincimex", "CCS2410101", ("82244400", "82344500")),
            ("13", "Seguridad Trabajo", "CCS2410103", ("82244400", "82344500")),
            ("14", "Reducción Desastres", "CCS2410104", ("82244400", "82344500")),
            ("15", "Ciencia y Tecnología", "CCS2410101", ("82244400", "82344500")),
            ("16", "Gerencia Comercial", "CCS2410102", ("82244400", "82344500")),
            ("17", "Publicidad directos", "CCS24104", ("70044400", "70144500")),
            ("21", "Transporte adm.", "CCS2410511", ("82844400", "82944500")),
            ("31", "Grupo Servicios", "CCS2410531", ("82844400", "82944500")),
            ("41", "Admita Mantenimiento", "CCS2410541", ("82844400", "82944500"))
        ]
        
        self.departments = departments or default_departments
        self.entities = entities or ["CIMEX - Gerencia Administrativa", "CIMEX - Otra Entidad"]
        
        super().__init__(parent, "Reporte de Centros de Costo", width=700, height=600)
    
    def _create_widgets(self) -> None:
        """Crea los widgets del diálogo."""
        # Crear Canvas con Scrollbar
        self._create_scrollable_frame()
    
    def _create_scrollable_frame(self) -> None:
        """Crea un frame desplazable para el diálogo."""
        # Crear contenedor principal con canvas y scrollbars
        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        
        # Configurar expansión del contenedor
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Crear canvas
        canvas = tk.Canvas(container)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        # Crear scrollbar vertical
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Crear scrollbar horizontal
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configurar canvas
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Crear frame interno dentro del canvas
        self.inner_frame = ttk.Frame(canvas)
        
        # Crear ventana en el canvas para el frame interno
        canvas_frame = canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # Configurar eventos de scroll
        def _configure_canvas(event):
            # Configurar región de scroll
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Hacer que el frame interno tenga el mismo ancho que el canvas
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind eventos
        canvas.bind("<Configure>", _configure_canvas)
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        # Permitir que el canvas se expanda
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Crear el contenido en el frame interno
        self._create_content()
    
    def _create_content(self) -> None:
        """Crea el contenido dentro del frame desplazable."""
        # Frame principal dentro del frame interno
        main_frame = ttk.Frame(self.inner_frame, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar expansión del frame interno
        self.inner_frame.rowconfigure(0, weight=1)
        self.inner_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título descriptivo
        ttk.Label(
            main_frame,
            text="Configurar reporte de Centros de Costo",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Información
        ttk.Label(
            main_frame,
            text="Muestra la relación de departamentos con sus códigos de centro de costo y cuentas asociadas.",
            font=('Arial', 9)
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        ttk.Label(
            main_frame,
            text="Para otras entidades, dejar en blanco el campo CCosto. El sistema tomará el definido en Configuración.",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Sección de filtros
        filters_frame = self._create_section(main_frame, "Filtros", 3)
        
        # Entidad
        ttk.Label(filters_frame, text="Entidad:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.entity_var = tk.StringVar(value=self.entities[0])
        entity_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.entity_var,
            values=self.entities,
            state='readonly',
            width=40
        )
        entity_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Tipo de departamento
        ttk.Label(filters_frame, text="Tipo de departamento:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.dept_type_var = tk.StringVar(value="todos")
        type_frame = ttk.Frame(filters_frame)
        type_frame.grid(row=1, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(
            type_frame,
            text="Todos",
            variable=self.dept_type_var,
            value="todos"
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            type_frame,
            text="Con CCosto definido",
            variable=self.dept_type_var,
            value="con_ccosto"
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            type_frame,
            text="Sin CCosto (usar configuración)",
            variable=self.dept_type_var,
            value="sin_ccosto"
        ).pack(side=tk.LEFT)
        
        # Frame para tabla de departamentos
        table_frame = self._create_section(main_frame, "Departamentos Disponibles", 4)
        
        # Configurar expansión de table_frame
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Crear frame para treeview y scrollbars
        tree_container = ttk.Frame(table_frame)
        tree_container.grid(row=0, column=0, sticky="nsew", columnspan=2)
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Treeview para mostrar departamentos
        columns = ("Depto", "Nombre", "CCosto", "Cta Alimentación", "Cta Hospedaje")
        self.departments_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=10,  # Aumentado para mostrar más filas
            selectmode="extended"
        )
        
        # Configurar columnas
        col_widths = [60, 220, 120, 130, 130]
        for col, width in zip(columns, col_widths):
            self.departments_tree.heading(col, text=col)
            self.departments_tree.column(col, width=width, minwidth=50)
        
        # Scrollbars para treeview
        tree_vsb = ttk.Scrollbar(
            tree_container, 
            orient="vertical", 
            command=self.departments_tree.yview
        )
        tree_hsb = ttk.Scrollbar(
            tree_container, 
            orient="horizontal", 
            command=self.departments_tree.xview
        )
        
        self.departments_tree.configure(
            yscrollcommand=tree_vsb.set, 
            xscrollcommand=tree_hsb.set
        )
        
        # Grid para treeview y scrollbars
        self.departments_tree.grid(row=0, column=0, sticky="nsew")
        tree_vsb.grid(row=0, column=1, sticky="ns")
        tree_hsb.grid(row=1, column=0, sticky="ew")
        
        # Botones para selección
        selection_frame = ttk.Frame(table_frame)
        selection_frame.grid(row=0, column=2, sticky="ns", padx=(10, 0))
        
        ttk.Button(
            selection_frame,
            text="Seleccionar\nTodo",
            command=lambda: self.departments_tree.selection_set(
                self.departments_tree.get_children()
            ),
            width=12
        ).pack(pady=(0, 5))
        
        ttk.Button(
            selection_frame,
            text="Deseleccionar\nTodo",
            command=lambda: self.departments_tree.selection_clear(
                self.departments_tree.get_children()
            ),
            width=12
        ).pack(pady=(0, 5))
        
        ttk.Button(
            selection_frame,
            text="Invertir\nSelección",
            command=self._invert_selection,
            width=12
        ).pack()
        
        # Opciones de visualización
        options_frame = self._create_section(main_frame, "Opciones de Visualización", 5)
        
        # Columnas a mostrar
        ttk.Label(options_frame, text="Columnas a incluir:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        columns_frame = ttk.Frame(options_frame)
        columns_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        self.show_depto_var = tk.BooleanVar(value=True)
        self.show_name_var = tk.BooleanVar(value=True)
        self.show_ccosto_var = tk.BooleanVar(value=True)
        self.show_aliment_var = tk.BooleanVar(value=True)
        self.show_hospedaje_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            columns_frame,
            text="Depto",
            variable=self.show_depto_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            columns_frame,
            text="Nombre",
            variable=self.show_name_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            columns_frame,
            text="CCosto",
            variable=self.show_ccosto_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            columns_frame,
            text="Cta Alim.",
            variable=self.show_aliment_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            columns_frame,
            text="Cta Hosp.",
            variable=self.show_hospedaje_var
        ).pack(side=tk.LEFT)
        
        # Agrupar por
        ttk.Label(options_frame, text="Agrupar por:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.group_by_var = tk.StringVar(value="ninguno")
        group_combo = ttk.Combobox(
            options_frame,
            textvariable=self.group_by_var,
            values=["Ninguno", "Por CCosto", "Por Cuenta de Alimentación", 
                   "Por Cuenta de Hospedaje"],
            state='readonly',
            width=30
        )
        group_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Formato de salida
        ttk.Label(options_frame, text="Formato de salida:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.output_format_var = tk.StringVar(value="Pantalla")
        format_combo = ttk.Combobox(
            options_frame,
            textvariable=self.output_format_var,
            values=["Pantalla", "PDF", "Excel", "CSV", "Tabla HTML"],
            state='readonly',
            width=30
        )
        format_combo.grid(row=2, column=1, sticky="w", pady=10)
        
        # Incluir totales
        self.include_totals_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Incluir resumen de totales por cuenta",
            variable=self.include_totals_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Frame para botones (fuera del scroll para que siempre estén visibles)
        # Cambiamos esto: poner botones en el frame interno, no en el canvas
        button_container = ttk.Frame(self.inner_frame)
        button_container.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        self.button_frame = ttk.Frame(button_container)
        self.button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Botones estándar
        ttk.Button(
            self.button_frame,
            text="Aceptar",
            command=self._on_ok,
            width=15
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            self.button_frame,
            text="Cancelar",
            command=self._on_cancel,
            width=15
        ).pack(side=tk.RIGHT)
        
        # Cargar departamentos en el treeview
        self._load_departments()
        
        # Bind eventos
        self.dept_type_var.trace_add('write', self._filter_departments)
        
        # Ajustar el tamaño mínimo del frame interno
        self.inner_frame.update_idletasks()
    
    def _create_section(self, parent: ttk.Frame, title: str, row: int) -> ttk.Frame:
        """Crea una sección con título."""
        frame = ttk.LabelFrame(parent, text=f" {title} ", padding="15")
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        frame.columnconfigure(1, weight=1)
        return frame
    
    def _load_departments(self) -> None:
        """Carga los departamentos en el Treeview."""
        # Limpiar treeview
        for item in self.departments_tree.get_children():
            self.departments_tree.delete(item)
        
        # Insertar departamentos
        for dept_code, dept_name, ccosto, cuentas in self.departments:
            cta_aliment, cta_hospedaje = cuentas
            self.departments_tree.insert(
                "", "end",
                values=(dept_code, dept_name, ccosto, cta_aliment, cta_hospedaje)
            )
    
    def _filter_departments(self, *args) -> None:
        """Filtra los departamentos según el tipo seleccionado."""
        filter_type = self.dept_type_var.get()
        
        # Mostrar todos los elementos primero
        for item in self.departments_tree.get_children():
            self.departments_tree.item(item, tags=())
        
        if filter_type == "todos":
            return
        
        # Aplicar filtro
        for item in self.departments_tree.get_children():
            values = self.departments_tree.item(item, "values")
            ccosto = values[2] if len(values) > 2 else ""
            
            if filter_type == "con_ccosto" and (not ccosto or ccosto.strip() == ""):
                self.departments_tree.detach(item)
            elif filter_type == "sin_ccosto" and ccosto and ccosto.strip() != "":
                self.departments_tree.detach(item)
    
    def _invert_selection(self) -> None:
        """Invierte la selección actual en el treeview."""
        all_items = self.departments_tree.get_children()
        selected_items = self.departments_tree.selection()
        
        # Deseleccionar todos
        self.departments_tree.selection_remove(all_items)
        
        # Seleccionar los no seleccionados anteriormente
        for item in all_items:
            if item not in selected_items:
                self.departments_tree.selection_add(item)
    
    def _get_selected_departments(self) -> List[Tuple]:
        """Obtiene los departamentos seleccionados."""
        selected = []
        for item in self.departments_tree.selection():
            values = self.departments_tree.item(item, "values")
            if len(values) >= 5:
                selected.append((
                    values[0],  # dept_code
                    values[1],  # dept_name
                    values[2],  # ccosto
                    (values[3], values[4])  # cuentas
                ))
        return selected
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos del formulario."""
        errors = []
        
        # Validar que al menos una columna esté seleccionada
        if not (self.show_depto_var.get() or 
                self.show_name_var.get() or 
                self.show_ccosto_var.get() or
                self.show_aliment_var.get() or
                self.show_hospedaje_var.get()):
            errors.append("Seleccione al menos una columna para mostrar")
        
        # Validar que haya departamentos seleccionados (si se filtra por selección)
        selected_departments = self._get_selected_departments()
        if len(selected_departments) == 0:
            messagebox.showwarning(
                "Advertencia",
                "No se han seleccionado departamentos. Se mostrarán todos los departamentos.",
                parent=self
            )
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de configuración del reporte."""
        # Obtener departamentos seleccionados o todos
        selected_departments = self._get_selected_departments()
        if not selected_departments:
            # Si no hay selección, usar todos
            selected_departments = self.departments
        
        # Determinar columnas a mostrar
        columns_to_show = []
        if self.show_depto_var.get():
            columns_to_show.append("depto")
        if self.show_name_var.get():
            columns_to_show.append("nombre")
        if self.show_ccosto_var.get():
            columns_to_show.append("ccosto")
        if self.show_aliment_var.get():
            columns_to_show.append("alimentacion")
        if self.show_hospedaje_var.get():
            columns_to_show.append("hospedaje")
        
        return {
            'entity': self.entity_var.get(),
            'dept_type_filter': self.dept_type_var.get(),
            'selected_departments': selected_departments,
            'columns_to_show': columns_to_show,
            'group_by': self.group_by_var.get(),
            'output_format': self.output_format_var.get(),
            'include_totals': self.include_totals_var.get(),
            'report_name': 'cost_center',
            'timestamp': datetime.now()
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Crear diálogo
    dialog = CostCenterDialog(root)
    result = dialog.show()
    
    if result:
        print("Configuración del reporte de Centros de Costo:")
        print(f"  Entidad: {result['entity']}")
        print(f"  Filtro tipo: {result['dept_type_filter']}")
        print(f"  Departamentos seleccionados: {len(result['selected_departments'])}")
        print(f"  Columnas a mostrar: {', '.join(result['columns_to_show'])}")
        print(f"  Agrupar por: {result['group_by']}")
        print(f"  Formato: {result['output_format']}")
        print(f"  Incluir totales: {result['include_totals']}")
        
        # Mostrar primeros 3 departamentos como ejemplo
        print("\n  Ejemplo de departamentos:")
        for i, dept in enumerate(result['selected_departments'][:3]):
            print(f"    {dept[0]} - {dept[1]}")
    else:
        print("Diálogo cancelado")
    
    root.destroy()
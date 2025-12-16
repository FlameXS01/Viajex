"""
department_report_dialog.py
Diálogo para configurar el reporte por departamento.
Muestra resultados y estadísticas agrupados por departamento.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog
from .date_range_dialog import DateRangeDialog


class DepartmentReportDialog(BaseReportDialog):
    """Diálogo para configurar reporte por departamento"""
    
    def __init__(self, parent, 
                 entities: Optional[List[str]] = None,
                 departments: Optional[List[Tuple[str, str, str]]] = None,
                 report_levels: Optional[List[str]] = None):
        """
        Inicializa el diálogo para reporte por departamento.
        
        Args:
            parent: Ventana padre
            entities: Lista de entidades disponibles
            departments: Lista de departamentos (código, nombre, costo_center)
            report_levels: Lista de niveles de reporte disponibles
        """
        self.entities = entities or ["CIMEX - Gerencia Administrativa"]
        
        # Departamentos con centros de costo del PDF (Page 4)
        self.departments = departments or [
            ("01", "Gerencia General", "CCS2410101"),
            ("02", "Gerencia Economía", "CCS2410102"),
            ("03", "Grupo Informática", "CCS2410103"),
            ("04", "Gerencia R. Humanos", "CCS2410104"),
            ("05", "Gerencia Auditoría", "CCS2410105"),
            ("06", "Grupo Protección", "CCS2410106"),
            ("09", "Gastos Generales", "CCS2410109"),
            ("10", "Capacitación", "CCS2410100"),
            ("11", "Grupo Fincimex", "CCS2410101"),
            ("13", "Seguridad Trabajo", "CCS2410103"),
            ("14", "Reducción Desastres", "CCS2410104"),
            ("15", "Ciencia y Tecnología", "CCS2410101"),
            ("16", "Gerencia Comercial", "CCS2410102"),
            ("17", "Publicidad directos", "CCS24104"),
            ("21", "Transporte adm.", "CCS2410511"),
            ("31", "Grupo Servicios", "CCS2410531"),
            ("41", "Admita Mantenimiento", "CCS2410541")
        ]
        
        self.report_levels = report_levels or [
            "Resumen ejecutivo",
            "Detallado con trabajadores",
            "Comparativo entre departamentos",
            "Evolución histórica",
            "Análisis de costos",
            "Presupuesto vs Real"
        ]
        
        super().__init__(parent, "Reporte por Departamento", width=700, height=700)
    
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
            text="Configurar Reporte por Departamento",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Información del reporte
        info_text = "🏢 Reporte agrupado por departamento.\n"
        info_text += "Muestra resultados, costos y estadísticas organizadas por estructura departamental."
        
        ttk.Label(
            main_frame,
            text=info_text,
            font=('Arial', 9),
            foreground='darkgreen'
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Sección de selección de departamentos
        dept_frame = self._create_section(main_frame, "Selección de Departamentos", 2)
        
        # Modo de selección
        ttk.Label(dept_frame, text="Seleccionar departamentos:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.selection_mode_var = tk.StringVar(value="todos")
        selection_frame = ttk.Frame(dept_frame)
        selection_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        selection_options = [
            ("Todos los departamentos", "todos"),
            ("Departamentos específicos", "especificos"),
            ("Por área funcional", "area"),
            ("Con centro de costo definido", "con_ccosto"),
            ("Sin centro de costo", "sin_ccosto")
        ]
        
        for i, (text, value) in enumerate(selection_options):
            ttk.Radiobutton(
                selection_frame,
                text=text,
                variable=self.selection_mode_var,
                value=value,
                command=self._update_dept_selection_controls
            ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame para controles de selección específica
        self.dept_selection_controls_frame = ttk.Frame(dept_frame)
        self.dept_selection_controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Inicializar controles de selección
        self._create_dept_selection_controls()
        
        # Sección de tipo y nivel de reporte
        report_frame = self._create_section(main_frame, "Tipo y Nivel de Reporte", 3)
        
        # Nivel de reporte
        ttk.Label(report_frame, text="Nivel de reporte:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.report_level_var = tk.StringVar(value=self.report_levels[0])
        level_combo = ttk.Combobox(
            report_frame,
            textvariable=self.report_level_var,
            values=self.report_levels,
            state='readonly',
            width=40
        )
        level_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Incluir subdepartamentos
        self.include_subdepts_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            report_frame,
            text="Incluir subdepartamentos y secciones",
            variable=self.include_subdepts_var
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Incluir comparativas
        self.include_comparisons_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            report_frame,
            text="Incluir comparativas con otros departamentos",
            variable=self.include_comparisons_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))
        
        # Incluir análisis de tendencias
        self.include_trends_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            report_frame,
            text="Incluir análisis de tendencias",
            variable=self.include_trends_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 0))
        
        # Sección de período
        period_frame = self._create_section(main_frame, "Período del Reporte", 4)
        
        # Tipo de período
        ttk.Label(period_frame, text="Período:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.period_type_var = tk.StringVar(value="mes_actual")
        period_type_frame = ttk.Frame(period_frame)
        period_type_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        period_options = [
            ("Mes actual", "mes_actual"),
            ("Rango personalizado", "rango"),
            ("Trimestre actual", "trimestre"),
            ("Año actual", "ano_actual"),
            ("Comparativo mes anterior", "mes_anterior"),
            ("Acumulado año", "acumulado_ano")
        ]
        
        for i, (text, value) in enumerate(period_options):
            ttk.Radiobutton(
                period_type_frame,
                text=text,
                variable=self.period_type_var,
                value=value,
                command=self._update_period_controls
            ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame para controles de fecha
        self.period_controls_frame = ttk.Frame(period_frame)
        self.period_controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Inicializar controles de período
        self._create_period_controls()
        
        # Sección de filtros
        filters_frame = self._create_section(main_frame, "Filtros Adicionales", 5)
        
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
        
        # Tipo de gasto
        ttk.Label(filters_frame, text="Tipo de gasto:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.expense_type_var = tk.StringVar(value="todos")
        expense_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.expense_type_var,
            values=["Todos", "Solo alimentación", "Solo hospedaje", 
                   "Solo transporte", "Solo otros gastos", "Por categoría"],
            state='readonly',
            width=40
        )
        expense_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Rango de importes
        ttk.Label(filters_frame, text="Filtrar por importe:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        amount_frame = ttk.Frame(filters_frame)
        amount_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        self.min_amount_var = tk.StringVar()
        self.max_amount_var = tk.StringVar()
        
        ttk.Entry(amount_frame, textvariable=self.min_amount_var, width=12).pack(side=tk.LEFT)
        ttk.Label(amount_frame, text=" a ").pack(side=tk.LEFT, padx=5)
        ttk.Entry(amount_frame, textvariable=self.max_amount_var, width=12).pack(side=tk.LEFT)
        ttk.Label(amount_frame, text=" CUP").pack(side=tk.LEFT, padx=(5, 0))
        
        # Sección de métricas a incluir
        metrics_frame = self._create_section(main_frame, "Métricas a Incluir", 6)
        
        # Checkboxes para métricas
        self.metric_vars = {}
        
        metrics = [
            ("total_gastos", "Total de gastos", True),
            ("promedio_por_trabajador", "Promedio por trabajador", True),
            ("porcentaje_presupuesto", "% del presupuesto", True),
            ("variacion_mes_anterior", "Variación vs mes anterior", True),
            ("tendencia_trimestral", "Tendencia trimestral", False),
            ("eficiencia_costos", "Índice de eficiencia de costos", False),
            ("comparativa_areas", "Comparativa con otras áreas", True),
            ("distribucion_gastos", "Distribución de gastos", True),
            ("proyeccion_mensual", "Proyección mensual", False),
            ("analisis_desviaciones", "Análisis de desviaciones", False)
        ]
        
        # Crear checkboxes en dos columnas
        left_frame = ttk.Frame(metrics_frame)
        left_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        right_frame = ttk.Frame(metrics_frame)
        right_frame.grid(row=0, column=1, sticky="w")
        
        for i, (key, label, default) in enumerate(metrics):
            frame = left_frame if i < len(metrics) // 2 else right_frame
            row = i if i < len(metrics) // 2 else i - len(metrics) // 2
            
            var = tk.BooleanVar(value=default)
            self.metric_vars[key] = var
            
            ttk.Checkbutton(
                frame,
                text=label,
                variable=var
            ).grid(row=row, column=0, sticky="w", pady=2)
        
        # Sección de formato y salida
        output_frame = self._create_section(main_frame, "Formato y Salida", 7)
        
        # Formato de salida
        ttk.Label(output_frame, text="Formato de salida:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.output_format_var = tk.StringVar(value="Pantalla")
        format_combo = ttk.Combobox(
            output_frame,
            textvariable=self.output_format_var,
            values=["Pantalla", "PDF", "Excel", "CSV", "HTML", "Presentación"],
            state='readonly',
            width=25
        )
        format_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Plantilla de reporte
        ttk.Label(output_frame, text="Plantilla de reporte:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.template_var = tk.StringVar(value="Estándar departamental")
        template_combo = ttk.Combobox(
            output_frame,
            textvariable=self.template_var,
            values=["Estándar departamental", "Resumen ejecutivo", 
                   "Detallado analítico", "Comparativo", "Personalizado"],
            state='readonly',
            width=25
        )
        template_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Opciones de agrupamiento
        ttk.Label(output_frame, text="Agrupar resultados por:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.group_by_var = tk.StringVar(value="departamento")
        group_combo = ttk.Combobox(
            output_frame,
            textvariable=self.group_by_var,
            values=["Departamento", "Centro de costo", "Tipo de gasto", 
                   "Período temporal", "Ninguno (lista simple)"],
            state='readonly',
            width=25
        )
        group_combo.grid(row=2, column=1, sticky="w", pady=10)
        
        # Opciones adicionales
        self.include_totales_var = tk.BooleanVar(value=True)
        self.include_graficos_var = tk.BooleanVar(value=True)
        self.include_detalle_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(
            output_frame,
            text="Incluir totales generales",
            variable=self.include_totales_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        ttk.Checkbutton(
            output_frame,
            text="Incluir gráficos y visualizaciones",
            variable=self.include_graficos_var
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(2, 0))
        
        ttk.Checkbutton(
            output_frame,
            text="Incluir detalle por trabajador",
            variable=self.include_detalle_var
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(2, 0))
        
        # Frame para botones especiales
        special_buttons_frame = ttk.Frame(main_frame)
        special_buttons_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            special_buttons_frame,
            text="Análisis Comparativo",
            command=self._show_comparative_analysis,
            width=18
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            special_buttons_frame,
            text="Generar Dashboard",
            command=self._generate_dashboard,
            width=18
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            special_buttons_frame,
            text="Exportar para SAP",
            command=self._export_for_sap,
            width=18
        ).pack(side=tk.LEFT)
        
        # Frame para botones principales
        self.button_frame.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(20, 0))
    
    def _create_dept_selection_controls(self) -> None:
        """Crea controles de selección de departamentos según el modo."""
        # Limpiar frame
        for widget in self.dept_selection_controls_frame.winfo_children():
            widget.destroy()
        
        selection_mode = self.selection_mode_var.get()
        
        if selection_mode == "especificos":
            # Selección específica de departamentos
            ttk.Label(self.dept_selection_controls_frame, text="Departamentos:").pack(anchor='w')
            
            # Frame con scroll para lista de departamentos
            list_frame = ttk.Frame(self.dept_selection_controls_frame)
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Listbox para selección múltiple
            self.departments_listbox = tk.Listbox(
                list_frame,
                selectmode=tk.MULTIPLE,
                yscrollcommand=scrollbar.set,
                height=6
            )
            self.departments_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.departments_listbox.yview)
            
            # Cargar departamentos en la lista
            for code, name, ccosto in self.departments:
                display_text = f"{code} - {name} [{ccosto}]"
                self.departments_listbox.insert(tk.END, display_text)
            
            # Botones de selección rápida
            button_frame = ttk.Frame(self.dept_selection_controls_frame)
            button_frame.pack(fill=tk.X, pady=(5, 0))
            
            ttk.Button(
                button_frame,
                text="Seleccionar Todo",
                command=lambda: self.departments_listbox.selection_set(0, tk.END),
                width=15
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Button(
                button_frame,
                text="Deseleccionar Todo",
                command=lambda: self.departments_listbox.selection_clear(0, tk.END),
                width=15
            ).pack(side=tk.LEFT)
        
        elif selection_mode == "area":
            # Selección por área funcional
            ttk.Label(self.dept_selection_controls_frame, text="Área funcional:").pack(side=tk.LEFT)
            
            self.area_var = tk.StringVar()
            area_combo = ttk.Combobox(
                self.dept_selection_controls_frame,
                textvariable=self.area_var,
                values=["Todas", "Gerencia", "Administración", "Operaciones", 
                       "Comercial", "Tecnología", "Servicios"],
                state='readonly',
                width=20
            )
            area_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        elif selection_mode in ["con_ccosto", "sin_ccosto"]:
            # Mensaje informativo
            message = "Se mostrarán todos los departamentos "
            if selection_mode == "con_ccosto":
                message += "CON centro de costo definido."
            else:
                message += "SIN centro de costo definido (usar configuración por defecto)."
            
            ttk.Label(
                self.dept_selection_controls_frame,
                text=message,
                font=('Arial', 9, 'italic')
            ).pack(anchor='w')
    
    def _create_period_controls(self) -> None:
        """Crea controles de período según el tipo seleccionado."""
        # Limpiar frame
        for widget in self.period_controls_frame.winfo_children():
            widget.destroy()
        
        period_type = self.period_type_var.get()
        
        if period_type == "rango":
            # Frame para rango de fechas
            range_frame = ttk.Frame(self.period_controls_frame)
            range_frame.pack(anchor='w')
            
            ttk.Label(range_frame, text="Desde:").pack(side=tk.LEFT)
            
            self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"))
            ttk.Entry(
                range_frame, 
                textvariable=self.start_date_var,
                width=12,
                state='readonly'
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Button(
                range_frame,
                text="📅",
                command=lambda: self._select_date(self.start_date_var),
                width=3
            ).pack(side=tk.LEFT, padx=(5, 10))
            
            ttk.Label(range_frame, text="Hasta:").pack(side=tk.LEFT)
            
            self.end_date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
            ttk.Entry(
                range_frame, 
                textvariable=self.end_date_var,
                width=12,
                state='readonly'
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Button(
                range_frame,
                text="📅",
                command=lambda: self._select_date(self.end_date_var),
                width=3
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            # Botón para usar diálogo de rango
            ttk.Button(
                range_frame,
                text="Usar diálogo de rango",
                command=self._use_date_range_dialog,
                width=18
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        else:
            # Mensaje informativo para otros tipos
            messages = {
                "mes_actual": f"Mes actual: {datetime.now().strftime('%B %Y')}",
                "trimestre": f"Trimestre actual: Q{(datetime.now().month - 1) // 3 + 1} {datetime.now().year}",
                "ano_actual": f"Año actual: {datetime.now().year}",
                "mes_anterior": f"Comparativo: {datetime.now().strftime('%B %Y')} vs {(datetime.now() - timedelta(days=30)).strftime('%B %Y')}",
                "acumulado_ano": f"Acumulado año: Enero - {datetime.now().strftime('%B %Y')} {datetime.now().year}"
            }
            
            if period_type in messages:
                ttk.Label(
                    self.period_controls_frame,
                    text=messages[period_type],
                    font=('Arial', 9, 'italic')
                ).pack(anchor='w')
    
    def _update_dept_selection_controls(self) -> None:
        """Actualiza controles cuando cambia el modo de selección de departamentos."""
        self._create_dept_selection_controls()
    
    def _update_period_controls(self) -> None:
        """Actualiza controles cuando cambia el tipo de período."""
        self._create_period_controls()
    
    def _select_date(self, date_var: tk.StringVar) -> None:
        """Abre diálogo para seleccionar fecha."""
        try:
            current_date_str = date_var.get()
            if current_date_str:
                current_date = datetime.strptime(current_date_str, "%d/%m/%Y")
            else:
                current_date = datetime.now()
            
            # Usar tkcalendar si está disponible
            try:
                from tkcalendar import Calendar
                
                top = tk.Toplevel(self)
                top.title("Seleccionar Fecha")
                top.transient(self)
                top.grab_set()
                
                cal = Calendar(top, selectmode='day', date_pattern='dd/mm/yyyy')
                cal.selection_set(current_date)
                cal.pack(padx=10, pady=10)
                
                def on_accept():
                    date_var.set(cal.get_date())
                    top.destroy()
                
                ttk.Button(top, text="Aceptar", command=on_accept).pack(pady=(0, 10))
                
                # Centrar
                top.update_idletasks()
                x = self.winfo_x() + (self.winfo_width() // 2) - (top.winfo_width() // 2)
                y = self.winfo_y() + (self.winfo_height() // 2) - (top.winfo_height() // 2)
                top.geometry(f"+{x}+{y}")
                
            except ImportError:
                # Fallback
                new_date = tk.simpledialog.askstring(
                    "Seleccionar Fecha",
                    "Ingrese fecha (DD/MM/AAAA):",
                    initialvalue=current_date_str,
                    parent=self
                )
                if new_date:
                    try:
                        datetime.strptime(new_date, "%d/%m/%Y")
                        date_var.set(new_date)
                    except ValueError:
                        messagebox.showerror("Error", "Formato inválido", parent=self)
                        
        except ValueError:
            messagebox.showerror("Error", "Fecha actual inválida", parent=self)
    
    def _use_date_range_dialog(self) -> None:
        """Usa diálogo de rango de fechas."""
        dialog = DateRangeDialog(
            self,
            title="Seleccionar Rango de Fechas"
        )
        
        result = dialog.show()
        if result:
            self.start_date_var.set(result['start_date_str'])
            self.end_date_var.set(result['end_date_str'])
    
    def _show_comparative_analysis(self) -> None:
        """Muestra análisis comparativo entre departamentos."""
        messagebox.showinfo(
            "Análisis Comparativo",
            "Esta función realizaría un análisis comparativo entre departamentos:\n"
            "• Ranking por eficiencia de costos\n"
            "• Comparativa de gastos por área\n"
            "• Análisis de tendencias comparativas\n"
            "• Benchmarking interno",
            parent=self
        )
    
    def _generate_dashboard(self) -> None:
        """Genera dashboard ejecutivo."""
        messagebox.showinfo(
            "Generar Dashboard",
            "Esta función generaría un dashboard ejecutivo con:\n"
            "• KPIs por departamento\n"
            "• Gráficos interactivos\n"
            "• Tablero de control\n"
            "• Alertas y notificaciones",
            parent=self
        )
    
    def _export_for_sap(self) -> None:
        """Exporta datos para sistema SAP."""
        messagebox.showinfo(
            "Exportar para SAP",
            "Esta función exportaría los datos en formato compatible con SAP:\n"
            "• Estructura de centros de costo\n"
            "• Asignaciones presupuestarias\n"
            "• Movimientos contables\n"
            "• Integración directa",
            parent=self
        )
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos requeridos."""
        errors = []
        
        # Validar selección de departamentos si es modo específico
        selection_mode = self.selection_mode_var.get()
        
        if selection_mode == "especificos":
            if hasattr(self, 'departments_listbox'):
                selected_indices = self.departments_listbox.curselection()
                if len(selected_indices) == 0:
                    errors.append("Seleccione al menos un departamento")
        
        elif selection_mode == "area":
            if not self.area_var.get():
                errors.append("Seleccione un área funcional")
        
        # Validar fechas si es rango personalizado
        period_type = self.period_type_var.get()
        
        if period_type == "rango":
            start_str = self.start_date_var.get().strip()
            end_str = self.end_date_var.get().strip()
            
            if not start_str:
                errors.append("La fecha de inicio es requerida")
            else:
                try:
                    start_date = datetime.strptime(start_str, "%d/%m/%Y")
                except ValueError:
                    errors.append("Formato de fecha inicio inválido")
            
            if not end_str:
                errors.append("La fecha de fin es requerida")
            else:
                try:
                    end_date = datetime.strptime(end_str, "%d/%m/%Y")
                except ValueError:
                    errors.append("Formato de fecha fin inválido")
            
            if not errors and start_str and end_str:
                try:
                    start_date = datetime.strptime(start_str, "%d/%m/%Y")
                    end_date = datetime.strptime(end_str, "%d/%m/%Y")
                    if end_date < start_date:
                        errors.append("La fecha fin debe ser mayor o igual a la fecha inicio")
                except:
                    pass
        
        # Validar importes
        min_amount = self.min_amount_var.get().strip()
        max_amount = self.max_amount_var.get().strip()
        
        if min_amount:
            try:
                float(min_amount)
                if float(min_amount) < 0:
                    errors.append("El importe mínimo no puede ser negativo")
            except ValueError:
                errors.append("Importe mínimo inválido")
        
        if max_amount:
            try:
                float(max_amount)
                if float(max_amount) < 0:
                    errors.append("El importe máximo no puede ser negativo")
            except ValueError:
                errors.append("Importe máximo inválido")
        
        if min_amount and max_amount:
            try:
                if float(min_amount) > float(max_amount):
                    errors.append("El importe mínimo no puede ser mayor al máximo")
            except:
                pass
        
        # Validar que se incluya al menos una métrica
        selected_metrics = [key for key, var in self.metric_vars.items() if var.get()]
        if len(selected_metrics) == 0:
            errors.append("Seleccione al menos una métrica a incluir")
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de configuración del reporte."""
        # Obtener departamentos seleccionados
        selection_mode = self.selection_mode_var.get()
        selected_departments = []
        
        if selection_mode == "especificos":
            if hasattr(self, 'departments_listbox'):
                selected_indices = self.departments_listbox.curselection()
                for index in selected_indices:
                    dept_str = self.departments_listbox.get(index)
                    dept_code = dept_str.split(" - ")[0] if " - " in dept_str else dept_str
                    selected_departments.append(dept_code)
        
        elif selection_mode == "area":
            area = self.area_var.get()
            # Nota: En implementación real, aquí se filtrarían los departamentos por área
        
        # Obtener configuración de período
        period_type = self.period_type_var.get()
        period_config = {'period_type': period_type}
        
        if period_type == "rango":
            start_str = self.start_date_var.get().strip()
            end_str = self.end_date_var.get().strip()
            
            period_config.update({
                'start_date': datetime.strptime(start_str, "%d/%m/%Y"),
                'end_date': datetime.strptime(end_str, "%d/%m/%Y"),
                'start_date_str': start_str,
                'end_date_str': end_str,
                'days': (datetime.strptime(end_str, "%d/%m/%Y") - datetime.strptime(start_str, "%d/%m/%Y")).days + 1
            })
        
        # Obtener métricas seleccionadas
        selected_metrics = [key for key, var in self.metric_vars.items() if var.get()]
        
        return {
            'selection_mode': selection_mode,
            'selected_departments': selected_departments,
            'area': self.area_var.get() if selection_mode == "area" else None,
            'report_level': self.report_level_var.get(),
            'include_subdepts': self.include_subdepts_var.get(),
            'include_comparisons': self.include_comparisons_var.get(),
            'include_trends': self.include_trends_var.get(),
            'period_config': period_config,
            'entity': self.entity_var.get(),
            'expense_type': self.expense_type_var.get(),
            'min_amount': self.min_amount_var.get().strip() if self.min_amount_var.get().strip() else None,
            'max_amount': self.max_amount_var.get().strip() if self.max_amount_var.get().strip() else None,
            'selected_metrics': selected_metrics,
            'output_format': self.output_format_var.get(),
            'template': self.template_var.get(),
            'group_by': self.group_by_var.get(),
            'include_totales': self.include_totales_var.get(),
            'include_graficos': self.include_graficos_var.get(),
            'include_detalle': self.include_detalle_var.get(),
            'report_name': 'department_report'
        }


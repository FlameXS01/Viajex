"""
employee_report_dialog.py
Diálogo para configurar el reporte por trabajador.
Muestra resultados detallados para empleados específicos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog
from .date_range_dialog import DateRangeDialog


class EmployeeReportDialog(BaseReportDialog):
    """Diálogo para configurar reporte por trabajador"""
    
    def __init__(self, parent, 
                 entities: Optional[List[str]] = None,
                 departments: Optional[List[Tuple[str, str]]] = None,
                 employees: Optional[List[Tuple[str, str, str]]] = None):
        """
        Inicializa el diálogo para reporte por trabajador.
        
        Args:
            parent: Ventana padre
            entities: Lista de entidades disponibles
            departments: Lista de departamentos (código, nombre)
            employees: Lista de empleados (código, nombre, departamento)
        """
        self.entities = entities or ["CIMEX - Gerencia Administrativa"]
        
        # Departamentos de ejemplo
        self.departments = departments or [
            ("01", "Gerencia General"),
            ("02", "Gerencia Economía"),
            ("03", "Grupo Informática"),
            ("04", "Gerencia R. Humanos"),
            ("05", "Gerencia Auditoría"),
            ("06", "Grupo Protección"),
            ("09", "Gastos Generales"),
            ("10", "Capacitación"),
            ("11", "Grupo Fincimex"),
            ("13", "Seguridad Trabajo"),
            ("14", "Reducción Desastres"),
            ("15", "Ciencia y Tecnología"),
            ("16", "Gerencia Comercial"),
            ("17", "Publicidad directos"),
            ("21", "Transporte adm."),
            ("31", "Grupo Servicios"),
            ("41", "Admita Mantenimiento")
        ]
        
        # Empleados de ejemplo del PDF (Page 7)
        self.employees = employees or [
            ("42", "Brigada Mito Luis Miguel Jimenez Martínez", "BRIGADA"),
            ("72", "Almacen Regulador Miguel Angel Bettrán Valdivia", "ALMACEN"),
            ("76", "BRIGADA DE INVERSION Jose Luis García Collado", "BRIGADA INVERSION")
        ]
        
        super().__init__(parent, "Reporte por Trabajador", width=700, height=700)
    
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
            text="Configurar Reporte por Trabajador",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Información del reporte
        info_text = "👤 Reporte detallado por trabajador.\n"
        info_text += "Muestra movimientos, anticipos, liquidaciones y estadísticas individuales."
        
        ttk.Label(
            main_frame,
            text=info_text,
            font=('Arial', 9),
            foreground='darkblue'
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Sección de selección de trabajador
        employee_frame = self._create_section(main_frame, "Selección de Trabajador", 2)
        
        # Modo de selección
        ttk.Label(employee_frame, text="Seleccionar trabajador:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.selection_mode_var = tk.StringVar(value="individual")
        selection_frame = ttk.Frame(employee_frame)
        selection_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(
            selection_frame,
            text="Individual",
            variable=self.selection_mode_var,
            value="individual",
            command=self._update_selection_controls
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            selection_frame,
            text="Varios trabajadores",
            variable=self.selection_mode_var,
            value="multiple",
            command=self._update_selection_controls
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            selection_frame,
            text="Por departamento",
            variable=self.selection_mode_var,
            value="department",
            command=self._update_selection_controls
        ).pack(side=tk.LEFT)
        
        # Frame para controles de selección
        self.selection_controls_frame = ttk.Frame(employee_frame)
        self.selection_controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Inicializar controles de selección
        self._create_selection_controls()
        
        # Sección de período
        period_frame = self._create_section(main_frame, "Período del Reporte", 3)
        
        # Tipo de período
        ttk.Label(period_frame, text="Período:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.period_type_var = tk.StringVar(value="rango")
        period_type_frame = ttk.Frame(period_frame)
        period_type_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        period_options = [
            ("Rango de fechas", "rango"),
            ("Últimos 30 días", "30_dias"),
            ("Mes actual", "mes_actual"),
            ("Año actual", "ano_actual"),
            ("Personalizado", "personalizado")
        ]
        
        for i, (text, value) in enumerate(period_options):
            ttk.Radiobutton(
                period_type_frame,
                text=text,
                variable=self.period_type_var,
                value=value
            ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame para controles de fecha
        self.date_controls_frame = ttk.Frame(period_frame)
        self.date_controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Inicializar controles de fecha
        self._create_date_controls()
        
        # Sección de filtros
        filters_frame = self._create_section(main_frame, "Filtros Adicionales", 4)
        
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
        
        # Tipo de movimiento
        ttk.Label(filters_frame, text="Tipo de movimiento:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.movement_type_var = tk.StringVar(value="todos")
        movement_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.movement_type_var,
            values=["Todos", "Solo anticipos", "Solo liquidaciones", 
                   "Solo recargas", "Solo gastos", "Movimientos pendientes"],
            state='readonly',
            width=40
        )
        movement_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Estado del anticipo
        ttk.Label(filters_frame, text="Estado de anticipos:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.advance_status_var = tk.StringVar(value="todos")
        status_frame = ttk.Frame(filters_frame)
        status_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        status_options = [
            ("Todos", "todos"),
            ("Pendientes", "pendientes"),
            ("Liquidados", "liquidados"),
            ("Vencidos", "vencidos"),
            ("En curso", "en_curso")
        ]
        
        for i, (text, value) in enumerate(status_options):
            ttk.Radiobutton(
                status_frame,
                text=text,
                variable=self.advance_status_var,
                value=value
            ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Rango de importes
        ttk.Label(filters_frame, text="Filtrar por importe:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        amount_frame = ttk.Frame(filters_frame)
        amount_frame.grid(row=3, column=1, sticky="w", pady=10)
        
        self.min_amount_var = tk.StringVar()
        self.max_amount_var = tk.StringVar()
        
        ttk.Entry(amount_frame, textvariable=self.min_amount_var, width=12).pack(side=tk.LEFT)
        ttk.Label(amount_frame, text=" a ").pack(side=tk.LEFT, padx=5)
        ttk.Entry(amount_frame, textvariable=self.max_amount_var, width=12).pack(side=tk.LEFT)
        ttk.Label(amount_frame, text=" CUP").pack(side=tk.LEFT, padx=(5, 0))
        
        # Sección de información a incluir
        info_frame = self._create_section(main_frame, "Información a Incluir", 5)
        
        # Checkboxes para diferentes tipos de información
        self.include_vars = {}
        
        info_categories = [
            ("info_basica", "Información básica del trabajador", True),
            ("movimientos", "Listado de movimientos", True),
            ("anticipos", "Anticipos recibidos", True),
            ("liquidaciones", "Liquidaciones realizadas", True),
            ("saldo_actual", "Saldo actual y disponible", True),
            ("estadisticas", "Estadísticas y promedios", True),
            ("comparativas", "Comparativas con otros trabajadores", False),
            ("graficos", "Gráficos de evolución", False),
            ("documentos", "Documentos asociados", False),
            ("observaciones", "Observaciones y comentarios", True)
        ]
        
        # Crear checkboxes en dos columnas
        left_frame = ttk.Frame(info_frame)
        left_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        right_frame = ttk.Frame(info_frame)
        right_frame.grid(row=0, column=1, sticky="w")
        
        for i, (key, label, default) in enumerate(info_categories):
            frame = left_frame if i < len(info_categories) // 2 else right_frame
            row = i if i < len(info_categories) // 2 else i - len(info_categories) // 2
            
            var = tk.BooleanVar(value=default)
            self.include_vars[key] = var
            
            ttk.Checkbutton(
                frame,
                text=label,
                variable=var
            ).grid(row=row, column=0, sticky="w", pady=2)
        
        # Sección de formato y salida
        output_frame = self._create_section(main_frame, "Formato y Salida", 6)
        
        # Formato de salida
        ttk.Label(output_frame, text="Formato de salida:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.output_format_var = tk.StringVar(value="Pantalla")
        format_combo = ttk.Combobox(
            output_frame,
            textvariable=self.output_format_var,
            values=["Pantalla", "PDF", "Excel", "CSV", "HTML", "Impresión"],
            state='readonly',
            width=25
        )
        format_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Plantilla de reporte
        ttk.Label(output_frame, text="Plantilla de reporte:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.template_var = tk.StringVar(value="Estándar")
        template_combo = ttk.Combobox(
            output_frame,
            textvariable=self.template_var,
            values=["Estándar", "Detallado", "Resumido", "Ejecutivo", "Personalizado"],
            state='readonly',
            width=25
        )
        template_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Opciones adicionales
        self.include_summary_var = tk.BooleanVar(value=True)
        self.include_totals_var = tk.BooleanVar(value=True)
        self.group_by_date_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(
            output_frame,
            text="Incluir resumen ejecutivo",
            variable=self.include_summary_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        ttk.Checkbutton(
            output_frame,
            text="Incluir totales y subtotales",
            variable=self.include_totals_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 0))
        
        ttk.Checkbutton(
            output_frame,
            text="Agrupar movimientos por fecha",
            variable=self.group_by_date_var
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(2, 0))
        
        # Frame para botones especiales
        special_buttons_frame = ttk.Frame(main_frame)
        special_buttons_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            special_buttons_frame,
            text="Ver Historial Completo",
            command=self._show_complete_history,
            width=18
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            special_buttons_frame,
            text="Generar Certificación",
            command=self._generate_certificate,
            width=18
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            special_buttons_frame,
            text="Exportar Datos",
            command=self._export_data,
            width=18
        ).pack(side=tk.LEFT)
        
        # Frame para botones principales
        self.button_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(20, 0))
    
    def _create_selection_controls(self) -> None:
        """Crea controles de selección según el modo."""
        # Limpiar frame
        for widget in self.selection_controls_frame.winfo_children():
            widget.destroy()
        
        selection_mode = self.selection_mode_var.get()
        
        if selection_mode == "individual":
            # Selección individual
            ttk.Label(self.selection_controls_frame, text="Trabajador:").pack(side=tk.LEFT)
            
            self.employee_var = tk.StringVar()
            employee_combo = ttk.Combobox(
                self.selection_controls_frame,
                textvariable=self.employee_var,
                values=[f"{code} - {name}" for code, name, _ in self.employees],
                state='readonly',
                width=50
            )
            employee_combo.pack(side=tk.LEFT, padx=(5, 0))
            
        elif selection_mode == "multiple":
            # Selección múltiple
            ttk.Label(self.selection_controls_frame, text="Seleccionar trabajadores:").pack(anchor='w')
            
            # Frame con scroll para lista de empleados
            list_frame = ttk.Frame(self.selection_controls_frame)
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Listbox para selección múltiple
            self.employees_listbox = tk.Listbox(
                list_frame,
                selectmode=tk.MULTIPLE,
                yscrollcommand=scrollbar.set,
                height=6
            )
            self.employees_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.employees_listbox.yview)
            
            # Cargar empleados en la lista
            for code, name, dept in self.employees:
                display_text = f"{code} - {name} ({dept})"
                self.employees_listbox.insert(tk.END, display_text)
            
            # Botones de selección rápida
            button_frame = ttk.Frame(self.selection_controls_frame)
            button_frame.pack(fill=tk.X, pady=(5, 0))
            
            ttk.Button(
                button_frame,
                text="Seleccionar Todo",
                command=lambda: self.employees_listbox.selection_set(0, tk.END),
                width=15
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Button(
                button_frame,
                text="Deseleccionar Todo",
                command=lambda: self.employees_listbox.selection_clear(0, tk.END),
                width=15
            ).pack(side=tk.LEFT)
            
        elif selection_mode == "department":
            # Selección por departamento
            ttk.Label(self.selection_controls_frame, text="Departamento:").pack(side=tk.LEFT)
            
            self.department_var = tk.StringVar()
            department_combo = ttk.Combobox(
                self.selection_controls_frame,
                textvariable=self.department_var,
                values=["TODOS"] + [f"{code} - {name}" for code, name in self.departments],
                state='readonly',
                width=40
            )
            department_combo.pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Label(self.selection_controls_frame, text="Incluir subdepartamentos:").pack(side=tk.LEFT, padx=(10, 5))
            
            self.include_subdepts_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                self.selection_controls_frame,
                text="Sí",
                variable=self.include_subdepts_var
            ).pack(side=tk.LEFT)
    
    def _create_date_controls(self) -> None:
        """Crea controles de fecha según el tipo de período."""
        # Limpiar frame
        for widget in self.date_controls_frame.winfo_children():
            widget.destroy()
        
        period_type = self.period_type_var.get()
        
        if period_type in ["rango", "personalizado"]:
            # Frame para rango de fechas
            range_frame = ttk.Frame(self.date_controls_frame)
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
            if period_type == "personalizado":
                ttk.Button(
                    range_frame,
                    text="Usar diálogo de rango",
                    command=self._use_date_range_dialog,
                    width=18
                ).pack(side=tk.LEFT, padx=(10, 0))
        
        elif period_type == "30_dias":
            ttk.Label(
                self.date_controls_frame,
                text="Período: Últimos 30 días (automático)",
                font=('Arial', 9, 'italic')
            ).pack(anchor='w')
        
        elif period_type == "mes_actual":
            current_month = datetime.now().strftime("%B %Y")
            ttk.Label(
                self.date_controls_frame,
                text=f"Período: Mes actual ({current_month})",
                font=('Arial', 9, 'italic')
            ).pack(anchor='w')
        
        elif period_type == "ano_actual":
            current_year = datetime.now().year
            ttk.Label(
                self.date_controls_frame,
                text=f"Período: Año actual ({current_year})",
                font=('Arial', 9, 'italic')
            ).pack(anchor='w')
    
    def _update_selection_controls(self) -> None:
        """Actualiza controles cuando cambia el modo de selección."""
        self._create_selection_controls()
    
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
    
    def _show_complete_history(self) -> None:
        """Muestra historial completo del trabajador seleccionado."""
        selection_mode = self.selection_mode_var.get()
        
        if selection_mode == "individual" and not self.employee_var.get():
            messagebox.showwarning("Advertencia", "Seleccione un trabajador primero", parent=self)
            return
        
        messagebox.showinfo(
            "Historial Completo",
            "Esta función mostraría el historial completo del trabajador:\n"
            "• Todos los movimientos desde el inicio\n"
            "• Estadísticas completas\n"
            "• Evolución temporal\n"
            "• Comparativas históricas",
            parent=self
        )
    
    def _generate_certificate(self) -> None:
        """Genera certificación para el trabajador."""
        selection_mode = self.selection_mode_var.get()
        
        if selection_mode == "individual" and not self.employee_var.get():
            messagebox.showwarning("Advertencia", "Seleccione un trabajador primero", parent=self)
            return
        
        messagebox.showinfo(
            "Generar Certificación",
            "Esta función generaría una certificación oficial:\n"
            "• Certificado de movimientos\n"
            "• Constancia de saldo\n"
            "• Certificado de anticipos\n"
            "• Documento con firma digital",
            parent=self
        )
    
    def _export_data(self) -> None:
        """Exporta datos del trabajador."""
        messagebox.showinfo(
            "Exportar Datos",
            "Esta función exportaría los datos del trabajador en formato:\n"
            "• Excel detallado\n"
            "• CSV para análisis\n"
            "• PDF con formato\n"
            "• XML para integración",
            parent=self
        )
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos requeridos."""
        errors = []
        
        # Validar selección de trabajador
        selection_mode = self.selection_mode_var.get()
        
        if selection_mode == "individual":
            if not self.employee_var.get():
                errors.append("Seleccione un trabajador")
        
        elif selection_mode == "multiple":
            if hasattr(self, 'employees_listbox'):
                selected_indices = self.employees_listbox.curselection()
                if len(selected_indices) == 0:
                    errors.append("Seleccione al menos un trabajador")
        
        elif selection_mode == "department":
            if not self.department_var.get():
                errors.append("Seleccione un departamento")
        
        # Validar fechas si es rango personalizado
        period_type = self.period_type_var.get()
        
        if period_type in ["rango", "personalizado"]:
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
        
        # Validar que se incluya al menos un tipo de información
        selected_info = [key for key, var in self.include_vars.items() if var.get()]
        if len(selected_info) == 0:
            errors.append("Seleccione al menos un tipo de información a incluir")
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de configuración del reporte."""
        # Obtener trabajadores seleccionados
        selection_mode = self.selection_mode_var.get()
        selected_employees = []
        
        if selection_mode == "individual":
            if self.employee_var.get():
                emp_str = self.employee_var.get()
                emp_code = emp_str.split(" - ")[0] if " - " in emp_str else emp_str
                selected_employees.append(emp_code)
        
        elif selection_mode == "multiple":
            if hasattr(self, 'employees_listbox'):
                selected_indices = self.employees_listbox.curselection()
                for index in selected_indices:
                    emp_str = self.employees_listbox.get(index)
                    emp_code = emp_str.split(" - ")[0] if " - " in emp_str else emp_str
                    selected_employees.append(emp_code)
        
        elif selection_mode == "department":
            dept_str = self.department_var.get()
            dept_code = dept_str.split(" - ")[0] if " - " in dept_str and dept_str != "TODOS" else dept_str
            # Nota: En implementación real, aquí se obtendrían los empleados del departamento
        
        # Obtener configuración de período
        period_type = self.period_type_var.get()
        period_config = {'period_type': period_type}
        
        if period_type in ["rango", "personalizado"]:
            start_str = self.start_date_var.get().strip()
            end_str = self.end_date_var.get().strip()
            
            period_config.update({
                'start_date': datetime.strptime(start_str, "%d/%m/%Y"),
                'end_date': datetime.strptime(end_str, "%d/%m/%Y"),
                'start_date_str': start_str,
                'end_date_str': end_str,
                'days': (datetime.strptime(end_str, "%d/%m/%Y") - datetime.strptime(start_str, "%d/%m/%Y")).days + 1
            })
        
        # Obtener información a incluir
        selected_info = [key for key, var in self.include_vars.items() if var.get()]
        
        return {
            'selection_mode': selection_mode,
            'selected_employees': selected_employees,
            'department': self.department_var.get() if selection_mode == "department" else None,
            'include_subdepts': self.include_subdepts_var.get() if selection_mode == "department" else False,
            'period_config': period_config,
            'entity': self.entity_var.get(),
            'movement_type': self.movement_type_var.get(),
            'advance_status': self.advance_status_var.get(),
            'min_amount': self.min_amount_var.get().strip() if self.min_amount_var.get().strip() else None,
            'max_amount': self.max_amount_var.get().strip() if self.max_amount_var.get().strip() else None,
            'selected_info': selected_info,
            'output_format': self.output_format_var.get(),
            'template': self.template_var.get(),
            'include_summary': self.include_summary_var.get(),
            'include_totals': self.include_totals_var.get(),
            'group_by_date': self.group_by_date_var.get(),
            'report_name': 'employee_report'
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Crear diálogo
    dialog = EmployeeReportDialog(root)
    result = dialog.show()
    
    if result:
        print("Configuración del Reporte por Trabajador:")
        print(f"  Modo selección: {result['selection_mode']}")
        
        if result['selected_employees']:
            print(f"  Trabajadores seleccionados: {len(result['selected_employees'])}")
        
        if result['department']:
            print(f"  Departamento: {result['department']}")
            print(f"  Incluir subdepartamentos: {result['include_subdepts']}")
        
        period_config = result['period_config']
        print(f"  Tipo período: {period_config['period_type']}")
        
        if 'start_date_str' in period_config:
            print(f"  Rango: {period_config['start_date_str']} a {period_config['end_date_str']}")
        
        print(f"  Entidad: {result['entity']}")
        print(f"  Tipo movimiento: {result['movement_type']}")
        print(f"  Estado anticipos: {result['advance_status']}")
        
        if result['min_amount'] or result['max_amount']:
            print(f"  Importe filtro: {result['min_amount'] or '0'} a {result['max_amount'] or '∞'}")
        
        print(f"  Información incluida: {len(result['selected_info'])} tipos")
        print(f"  Formato salida: {result['output_format']}")
        print(f"  Plantilla: {result['template']}")
        print(f"  Incluir resumen: {result['include_summary']}")
        print(f"  Incluir totales: {result['include_totals']}")
        print(f"  Agrupar por fecha: {result['group_by_date']}")
    else:
        print("Diálogo cancelado")
    
    root.destroy()
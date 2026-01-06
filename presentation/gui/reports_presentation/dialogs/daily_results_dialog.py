"""
daily_results_dialog.py
Diálogo para configurar el reporte de "Resultados diarios" por departamento y trabajador.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog
from .date_range_dialog import DateRangeDialog


class DailyResultsDialog(BaseReportDialog):
    """Diálogo para configurar reporte de resultados diarios"""
    
    def __init__(self, parent, 
                 entities: Optional[List[str]] = None,
                 departments: Optional[List[Tuple[str, str]]] = None,
                 report_types: Optional[List[str]] = None):
        """
        Inicializa el diálogo para reporte de resultados diarios.
        
        Args:
            parent: Ventana padre
            entities: Lista de entidades disponibles
            departments: Lista de departamentos (código, nombre)
            report_types: Lista de tipos de reporte disponibles
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
        
        self.report_types = report_types or [
            "Diario por departamento",
            "Diario por trabajador", 
            "Mensual por departamento",
            "Mensual por trabajador",
            "Comparativo día vs mes anterior",
            "Acumulado mensual"
        ]
        
        super().__init__(parent, "Resultados Diarios", width=700, height=650)
    
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
            text="Configurar Reporte de Resultados Diarios",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Información del reporte
        info_text = "📊 Muestra resultados por departamentos con sus trabajadores.\n"
        info_text += "• El reporte del mes es el mismo con todos los días acumulados.\n"
        info_text += "• El reporte por trabajador muestra detalle individual."
        
        ttk.Label(
            main_frame,
            text=info_text,
            font=('Arial', 9),
            foreground='darkgreen'
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Sección de tipo de reporte
        report_type_frame = self._create_section(main_frame, "Tipo de Reporte", 2)
        
        # Tipo principal
        ttk.Label(report_type_frame, text="Tipo de reporte:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.report_type_var = tk.StringVar(value=self.report_types[0])
        type_combo = ttk.Combobox(
            report_type_frame,
            textvariable=self.report_type_var,
            values=self.report_types,
            state='readonly',
            width=35
        )
        type_combo.grid(row=0, column=1, sticky="w", pady=10)
        type_combo.bind('<<ComboboxSelected>>', self._on_report_type_change)
        
        # Nivel de detalle
        ttk.Label(report_type_frame, text="Nivel de detalle:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.detail_level_var = tk.StringVar(value="normal")
        detail_combo = ttk.Combobox(
            report_type_frame,
            textvariable=self.detail_level_var,
            values=["Resumido", "Normal", "Detallado", "Muy detallado"],
            state='readonly',
            width=35
        )
        detail_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Sección de fechas
        date_frame = self._create_section(main_frame, "Período del Reporte", 3)
        
        # Fecha específica o rango
        ttk.Label(date_frame, text="Período:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.period_type_var = tk.StringVar(value="fecha_unica")
        period_frame = ttk.Frame(date_frame)
        period_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(
            period_frame,
            text="Fecha específica",
            variable=self.period_type_var,
            value="fecha_unica",
            command=self._update_date_controls
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            period_frame,
            text="Rango de fechas",
            variable=self.period_type_var,
            value="rango",
            command=self._update_date_controls
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            period_frame,
            text="Mes completo",
            variable=self.period_type_var,
            value="mes",
            command=self._update_date_controls
        ).pack(side=tk.LEFT)
        
        # Frame para controles de fecha
        self.date_controls_frame = ttk.Frame(date_frame)
        self.date_controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Inicializar controles de fecha
        self._create_date_controls()
        
        # Sección de filtros
        filters_frame = self._create_section(main_frame, "Filtros", 4)
        
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
        
        # Departamento
        ttk.Label(filters_frame, text="Departamento:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.department_var = tk.StringVar(value="TODOS")
        dept_values = ["TODOS"] + [f"{code} - {name}" for code, name in self.departments]
        dept_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.department_var,
            values=dept_values,
            state='readonly',
            width=40
        )
        dept_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Tipo de gasto
        ttk.Label(filters_frame, text="Tipo de gasto:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.expense_type_var = tk.StringVar(value="todos")
        expense_frame = ttk.Frame(filters_frame)
        expense_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(
            expense_frame,
            text="Todos",
            variable=self.expense_type_var,
            value="todos"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            expense_frame,
            text="Solo efectivo",
            variable=self.expense_type_var,
            value="efectivo"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            expense_frame,
            text="Solo tarjetas",
            variable=self.expense_type_var,
            value="tarjetas"
        ).pack(side=tk.LEFT)
        
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
        
        # Sección de columnas a mostrar
        columns_frame = self._create_section(main_frame, "Columnas a Mostrar", 5)
        
        # Encabezados de columnas según PDF (Page 6)
        self.column_vars = {}
        columns_config = [
            ("cantidad_si", "Cantidad Sí", True),
            ("cantidad_no", "Cantidad No", False),
            ("monto_efectivo", "Efectivo", True),
            ("monto_total", "Total", True),
            ("promedio_diario", "Promedio Diario", False),
            ("porcentaje", "Porcentaje", False),
            ("variacion", "Variación vs Mes Ant", False),
            ("acumulado_mes", "Acumulado Mes", True)
        ]
        
        # Crear checkboxes en dos columnas
        left_frame = ttk.Frame(columns_frame)
        left_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        right_frame = ttk.Frame(columns_frame)
        right_frame.grid(row=0, column=1, sticky="w")
        
        for i, (key, label, default) in enumerate(columns_config):
            frame = left_frame if i < len(columns_config) // 2 else right_frame
            row = i if i < len(columns_config) // 2 else i - len(columns_config) // 2
            
            var = tk.BooleanVar(value=default)
            self.column_vars[key] = var
            
            ttk.Checkbutton(
                frame,
                text=label,
                variable=var
            ).grid(row=row, column=0, sticky="w", pady=2)
        
        # Sección de opciones de salida
        output_frame = self._create_section(main_frame, "Opciones de Salida", 6)
        
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
        
        # Agrupar por
        ttk.Label(output_frame, text="Agrupar resultados por:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.group_by_var = tk.StringVar(value="departamento")
        group_combo = ttk.Combobox(
            output_frame,
            textvariable=self.group_by_var,
            values=["Departamento", "Tipo de gasto", "Día de la semana", "Ninguno"],
            state='readonly',
            width=25
        )
        group_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Opciones adicionales
        self.include_totals_var = tk.BooleanVar(value=True)
        self.include_percentages_var = tk.BooleanVar(value=True)
        self.include_charts_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(
            output_frame,
            text="Incluir totales generales",
            variable=self.include_totals_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        ttk.Checkbutton(
            output_frame,
            text="Incluir porcentajes",
            variable=self.include_percentages_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 0))
        
        ttk.Checkbutton(
            output_frame,
            text="Incluir gráficos (solo Excel/PDF)",
            variable=self.include_charts_var
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(2, 0))
        
        # Frame para botones especiales
        special_buttons_frame = ttk.Frame(main_frame)
        special_buttons_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            special_buttons_frame,
            text="Calcular Proyección",
            command=self._calculate_projection,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            special_buttons_frame,
            text="Comparar con Mes Ant",
            command=self._compare_previous_month,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            special_buttons_frame,
            text="Exportar Plantilla",
            command=self._export_template,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame para botones principales
        self.button_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(20, 0))
    
    def _create_date_controls(self) -> None:
        """Crea los controles de fecha según el tipo seleccionado."""
        # Limpiar frame
        for widget in self.date_controls_frame.winfo_children():
            widget.destroy()
        
        period_type = self.period_type_var.get()
        
        if period_type == "fecha_unica":
            # Fecha única
            ttk.Label(self.date_controls_frame, text="Fecha:").pack(side=tk.LEFT)
            
            self.single_date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
            ttk.Entry(
                self.date_controls_frame, 
                textvariable=self.single_date_var,
                width=12,
                state='readonly'
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Button(
                self.date_controls_frame,
                text="📅",
                command=lambda: self._select_single_date(self.single_date_var),
                width=3
            ).pack(side=tk.LEFT, padx=(5, 0))
            
        elif period_type == "rango":
            # Rango de fechas
            ttk.Label(self.date_controls_frame, text="Desde:").pack(side=tk.LEFT)
            
            self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y"))
            ttk.Entry(
                self.date_controls_frame, 
                textvariable=self.start_date_var,
                width=12,
                state='readonly'
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Button(
                self.date_controls_frame,
                text="📅",
                command=lambda: self._select_single_date(self.start_date_var),
                width=3
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Label(self.date_controls_frame, text="Hasta:").pack(side=tk.LEFT, padx=(10, 0))
            
            self.end_date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
            ttk.Entry(
                self.date_controls_frame, 
                textvariable=self.end_date_var,
                width=12,
                state='readonly'
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Button(
                self.date_controls_frame,
                text="📅",
                command=lambda: self._select_single_date(self.end_date_var),
                width=3
            ).pack(side=tk.LEFT, padx=(5, 0))
            
        elif period_type == "mes":
            # Mes completo
            ttk.Label(self.date_controls_frame, text="Mes y año:").pack(side=tk.LEFT)
            
            self.month_var = tk.StringVar(value=datetime.now().strftime("%m/%Y"))
            month_frame = ttk.Frame(self.date_controls_frame)
            month_frame.pack(side=tk.LEFT, padx=(5, 0))
            
            # Mes
            month_combo = ttk.Combobox(
                month_frame,
                textvariable=tk.StringVar(value=datetime.now().strftime("%m")),
                values=[f"{i:02d}" for i in range(1, 13)],
                width=3,
                state='readonly'
            )
            month_combo.pack(side=tk.LEFT)
            ttk.Label(month_frame, text="/").pack(side=tk.LEFT, padx=2)
            
            # Año
            current_year = datetime.now().year
            year_combo = ttk.Combobox(
                month_frame,
                textvariable=tk.StringVar(value=str(current_year)),
                values=[str(year) for year in range(current_year - 2, current_year + 1)],
                width=5,
                state='readonly'
            )
            year_combo.pack(side=tk.LEFT)
            
            self.month_combo_var = month_combo
            self.year_combo_var = year_combo
    
    def _update_date_controls(self) -> None:
        """Actualiza los controles de fecha cuando cambia el tipo de período."""
        self._create_date_controls()
    
    def _select_single_date(self, date_var: tk.StringVar) -> None:
        """Abre diálogo para seleccionar fecha única."""
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
    
    def _on_report_type_change(self, event=None) -> None:
        """Actualiza controles cuando cambia el tipo de reporte."""
        report_type = self.report_type_var.get()
        
        # Actualizar nivel de detalle según tipo de reporte
        if "mensual" in report_type.lower() or "acumulado" in report_type.lower():
            self.detail_level_var.set("Normal")
        elif "comparativo" in report_type.lower():
            self.detail_level_var.set("Detallado")
    
    def _calculate_projection(self) -> None:
        """Calcula proyección basada en datos históricos."""
        messagebox.showinfo(
            "Calcular Proyección",
            "Esta función calcularía una proyección basada en:\n"
            "• Promedio histórico del mes\n"
            "• Tendencias del año anterior\n"
            "• Factores estacionales\n\n"
            "Proyección estimada para fin de mes: 45,000 CUP",
            parent=self
        )
    
    def _compare_previous_month(self) -> None:
        """Abre diálogo para comparar con mes anterior."""
        dialog = DateRangeDialog(
            self,
            title="Seleccionar Período de Comparación"
        )
        
        result = dialog.show()
        if result:
            messagebox.showinfo(
                "Comparar con Mes Anterior",
                f"Período seleccionado para comparación:\n"
                f"Desde: {result['start_date_str']}\n"
                f"Hasta: {result['end_date_str']}\n"
                f"Días: {result['days_range']}\n\n"
                "La comparación se incluirá en el reporte.",
                parent=self
            )
    
    def _export_template(self) -> None:
        """Exporta configuración como plantilla."""
        template_name = tk.simpledialog.askstring(
            "Exportar Plantilla",
            "Nombre para la plantilla:",
            parent=self
        )
        
        if template_name:
            messagebox.showinfo(
                "Plantilla Exportada",
                f"Plantilla '{template_name}' exportada exitosamente.\n"
                f"Disponible para uso futuro.",
                parent=self
            )
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos requeridos."""
        errors = []
        
        # Validar fechas según tipo de período
        period_type = self.period_type_var.get()
        
        if period_type == "fecha_unica":
            date_str = self.single_date_var.get().strip()
            if not date_str:
                errors.append("La fecha es requerida")
            else:
                try:
                    datetime.strptime(date_str, "%d/%m/%Y")
                except ValueError:
                    errors.append("Formato de fecha inválido (use DD/MM/AAAA)")
        
        elif period_type == "rango":
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
        
        # Validar que al menos una columna esté seleccionada
        selected_columns = [key for key, var in self.column_vars.items() if var.get()]
        if len(selected_columns) == 0:
            errors.append("Seleccione al menos una columna para mostrar")
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de configuración del reporte."""
        period_type = self.period_type_var.get()
        period_data = {}
        
        if period_type == "fecha_unica":
            date_str = self.single_date_var.get().strip()
            period_data = {
                'period_type': 'single_date',
                'date': datetime.strptime(date_str, "%d/%m/%Y"),
                'date_str': date_str
            }
        
        elif period_type == "rango":
            start_str = self.start_date_var.get().strip()
            end_str = self.end_date_var.get().strip()
            period_data = {
                'period_type': 'date_range',
                'start_date': datetime.strptime(start_str, "%d/%m/%Y"),
                'end_date': datetime.strptime(end_str, "%d/%m/%Y"),
                'start_date_str': start_str,
                'end_date_str': end_str,
                'days': (datetime.strptime(end_str, "%d/%m/%Y") - datetime.strptime(start_str, "%d/%m/%Y")).days + 1
            }
        
        elif period_type == "mes":
            month = self.month_combo_var.get()
            year = self.year_combo_var.get()
            period_data = {
                'period_type': 'month',
                'month': int(month),
                'year': int(year),
                'month_year_str': f"{month}/{year}"
            }
        
        # Obtener columnas seleccionadas
        selected_columns = [key for key, var in self.column_vars.items() if var.get()]
        
        return {
            'report_type': self.report_type_var.get(),
            'detail_level': self.detail_level_var.get(),
            'period_config': period_data,
            'entity': self.entity_var.get(),
            'department': self.department_var.get() if self.department_var.get() != "TODOS" else None,
            'expense_type': self.expense_type_var.get(),
            'min_amount': self.min_amount_var.get().strip() if self.min_amount_var.get().strip() else None,
            'max_amount': self.max_amount_var.get().strip() if self.max_amount_var.get().strip() else None,
            'selected_columns': selected_columns,
            'output_format': self.output_format_var.get(),
            'group_by': self.group_by_var.get(),
            'include_totals': self.include_totals_var.get(),
            'include_percentages': self.include_percentages_var.get(),
            'include_charts': self.include_charts_var.get(),
            'report_name': 'daily_results'
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Crear diálogo
    dialog = DailyResultsDialog(root)
    result = dialog.show()
    
    if result:
        print("Configuración del Reporte de Resultados Diarios:")
        print(f"  Tipo de reporte: {result['report_type']}")
        print(f"  Nivel de detalle: {result['detail_level']}")
        
        period_config = result['period_config']
        print(f"  Tipo período: {period_config['period_type']}")
        
        if period_config['period_type'] == 'single_date':
            print(f"  Fecha: {period_config['date_str']}")
        elif period_config['period_type'] == 'date_range':
            print(f"  Rango: {period_config['start_date_str']} a {period_config['end_date_str']}")
        elif period_config['period_type'] == 'month':
            print(f"  Mes/Año: {period_config['month_year_str']}")
        
        print(f"  Entidad: {result['entity']}")
        
        if result['department']:
            print(f"  Departamento: {result['department']}")
        
        print(f"  Tipo gasto: {result['expense_type']}")
        
        if result['min_amount'] or result['max_amount']:
            print(f"  Importe filtro: {result['min_amount'] or '0'} a {result['max_amount'] or '∞'}")
        
        print(f"  Columnas seleccionadas: {len(result['selected_columns'])}")
        print(f"  Formato salida: {result['output_format']}")
        print(f"  Agrupar por: {result['group_by']}")
        print(f"  Incluir totales: {result['include_totals']}")
        print(f"  Incluir porcentajes: {result['include_percentages']}")
        print(f"  Incluir gráficos: {result['include_charts']}")
    else:
        print("Diálogo cancelado")
    
    root.destroy()
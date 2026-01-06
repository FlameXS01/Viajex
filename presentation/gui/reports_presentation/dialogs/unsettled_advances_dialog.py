"""
unsettled_advances_dialog.py
Diálogo para configurar el reporte de "Anticipos sin liquidar".
Muestra anticipos pendientes de liquidación con diferentes estados.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog
from .date_range_dialog import DateRangeDialog


class UnsettledAdvancesDialog(BaseReportDialog):
    """Diálogo para configurar reporte de anticipos sin liquidar"""
    
    def __init__(self, parent, 
                 entities: Optional[List[str]] = None,
                 departments: Optional[List[Tuple[str, str]]] = None,
                 employees: Optional[List[Tuple[str, str]]] = None):
        """
        Inicializa el diálogo para reporte de anticipos sin liquidar.
        
        Args:
            parent: Ventana padre
            entities: Lista de entidades disponibles
            departments: Lista de departamentos (código, nombre)
            employees: Lista de empleados (código, nombre)
        """
        self.entities = entities or ["CIMEX - Gerencia Administrativa"]
        
        # Departamentos de ejemplo del PDF (Page 4)
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
            ("42", "Brigada Mito Luis Miguel Jimenez Martínez"),
            ("72", "Almacen Regulador Miguel Angel Bettrán Valdivia"),
            ("76", "BRIGADA DE INVERSION Jose Luis García Collado")
        ]
        
        super().__init__(parent, "Anticipos Pendientes de Liquidar", width=650, height=650)
    
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
            text="Configurar reporte de Anticipos Pendientes de Liquidar",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Descripción e información importante
        info_text = "⚠️ Una persona no puede tener un anticipo pendiente para crear otro.\n"
        info_text += "El sistema mostrará anticipos vencidos en rojo y próximos a vencer en amarillo."
        
        ttk.Label(
            main_frame,
            text=info_text,
            font=('Arial', 9, 'italic'),
            foreground='darkorange'
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Sección de filtros principales
        filters_frame = self._create_section(main_frame, "Filtros Principales", 2)
        
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
        
        # Fecha de corte
        ttk.Label(filters_frame, text="Fecha de corte:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.cutoff_date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        date_frame = ttk.Frame(filters_frame)
        date_frame.grid(row=1, column=1, sticky="w", pady=10)
        
        ttk.Entry(
            date_frame, 
            textvariable=self.cutoff_date_var,
            width=12,
            state='readonly'
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            date_frame,
            text="📅",
            command=self._select_cutoff_date,
            width=3
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Días de gracia
        ttk.Label(date_frame, text="Días de gracia:").pack(side=tk.LEFT, padx=(10, 5))
        self.grace_days_var = tk.StringVar(value="3")
        grace_spinbox = tk.Spinbox(
            date_frame,
            from_=0,
            to=30,
            textvariable=self.grace_days_var,
            width=3
        )
        grace_spinbox.pack(side=tk.LEFT)
        
        # Estado del anticipo
        ttk.Label(filters_frame, text="Estado del anticipo:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.advance_status_var = tk.StringVar(value="todos")
        status_frame = ttk.Frame(filters_frame)
        status_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        status_options = [
            ("Todos", "todos"),
            ("Vencidos", "vencidos"),
            ("Por vencer (próximos 3 días)", "por_vencer"),
            ("Vigentes", "vigentes"),
            ("En mora (> 72h)", "en_mora")
        ]
        
        for i, (text, value) in enumerate(status_options):
            if i % 3 == 0 and i > 0:
                # Nueva fila cada 3 opciones
                status_frame = ttk.Frame(filters_frame)
                status_frame.grid(row=2 + (i // 3), column=1, sticky="w", pady=5)
            
            ttk.Radiobutton(
                status_frame,
                text=text,
                variable=self.advance_status_var,
                value=value
            ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Sección de filtros por personas/departamentos
        detail_filters_frame = self._create_section(main_frame, "Filtros por Persona/Departamento", 5)
        
        # Departamento
        ttk.Label(detail_filters_frame, text="Departamento:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.department_var = tk.StringVar(value="TODOS")
        dept_values = ["TODOS"] + [f"{code} - {name}" for code, name in self.departments]
        dept_combo = ttk.Combobox(
            detail_filters_frame,
            textvariable=self.department_var,
            values=dept_values,
            state='readonly',
            width=40
        )
        dept_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Empleado
        ttk.Label(detail_filters_frame, text="Empleado:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.employee_var = tk.StringVar(value="TODOS")
        emp_values = ["TODOS"] + [f"{code} - {name}" for code, name in self.employees]
        emp_combo = ttk.Combobox(
            detail_filters_frame,
            textvariable=self.employee_var,
            values=emp_values,
            state='readonly',
            width=40
        )
        emp_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Rango de importes
        ttk.Label(detail_filters_frame, text="Importe del anticipo:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        amount_frame = ttk.Frame(detail_filters_frame)
        amount_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        self.min_amount_var = tk.StringVar()
        self.max_amount_var = tk.StringVar()
        
        ttk.Entry(amount_frame, textvariable=self.min_amount_var, width=10).pack(side=tk.LEFT)
        ttk.Label(amount_frame, text=" a ").pack(side=tk.LEFT, padx=5)
        ttk.Entry(amount_frame, textvariable=self.max_amount_var, width=10).pack(side=tk.LEFT)
        ttk.Label(amount_frame, text=" CUP").pack(side=tk.LEFT, padx=(5, 0))
        
        # Rango de fechas de regreso
        ttk.Label(detail_filters_frame, text="Fecha de regreso:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        return_frame = ttk.Frame(detail_filters_frame)
        return_frame.grid(row=3, column=1, sticky="w", pady=10)
        
        self.return_start_var = tk.StringVar()
        self.return_end_var = tk.StringVar()
        
        ttk.Entry(return_frame, textvariable=self.return_start_var, 
                 width=10, state='readonly').pack(side=tk.LEFT)
        ttk.Label(return_frame, text=" a ").pack(side=tk.LEFT, padx=5)
        ttk.Entry(return_frame, textvariable=self.return_end_var, 
                 width=10, state='readonly').pack(side=tk.LEFT)
        
        ttk.Button(
            return_frame,
            text="📅",
            command=self._select_return_range,
            width=3
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Sección de opciones de visualización
        display_frame = self._create_section(main_frame, "Opciones de Visualización", 6)
        
        # Columnas a mostrar
        ttk.Label(display_frame, text="Columnas a incluir:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        columns_frame = ttk.Frame(display_frame)
        columns_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        # Primera fila de columnas
        row1_frame = ttk.Frame(columns_frame)
        row1_frame.pack(anchor='w')
        
        self.show_name_var = tk.BooleanVar(value=True)
        self.show_advance_num_var = tk.BooleanVar(value=True)
        self.show_amount_cup_var = tk.BooleanVar(value=True)
        self.show_amount_cuc_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            row1_frame,
            text="Nombre",
            variable=self.show_name_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row1_frame,
            text="N° Anticipo",
            variable=self.show_advance_num_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row1_frame,
            text="Importe CUP",
            variable=self.show_amount_cup_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row1_frame,
            text="Hospedaje CUC",
            variable=self.show_amount_cuc_var
        ).pack(side=tk.LEFT)
        
        # Segunda fila de columnas
        row2_frame = ttk.Frame(columns_frame)
        row2_frame.pack(anchor='w', pady=(5, 0))
        
        self.show_card_var = tk.BooleanVar(value=True)
        self.show_card_balance_var = tk.BooleanVar(value=True)
        self.show_return_date_var = tk.BooleanVar(value=True)
        self.show_days_trans_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            row2_frame,
            text="Tarjeta Asignada",
            variable=self.show_card_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row2_frame,
            text="Saldo Tarjeta",
            variable=self.show_card_balance_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row2_frame,
            text="Fecha Regreso",
            variable=self.show_return_date_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row2_frame,
            text="Días Transcurridos",
            variable=self.show_days_trans_var
        ).pack(side=tk.LEFT)
        
        # Colores para estados
        ttk.Label(display_frame, text="Colores de estado:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        colors_frame = ttk.Frame(display_frame)
        colors_frame.grid(row=1, column=1, sticky="w", pady=10)
        
        self.color_expired_var = tk.StringVar(value="rojo")
        self.color_near_var = tk.StringVar(value="amarillo")
        self.color_normal_var = tk.StringVar(value="normal")
        
        ttk.Label(colors_frame, text="Vencidos:").pack(side=tk.LEFT)
        ttk.Combobox(
            colors_frame,
            textvariable=self.color_expired_var,
            values=["rojo", "negrita", "subrayado", "normal"],
            width=10,
            state='readonly'
        ).pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(colors_frame, text="Próximos:").pack(side=tk.LEFT)
        ttk.Combobox(
            colors_frame,
            textvariable=self.color_near_var,
            values=["amarillo", "naranja", "negrita", "normal"],
            width=10,
            state='readonly'
        ).pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(colors_frame, text="Otros:").pack(side=tk.LEFT)
        ttk.Combobox(
            colors_frame,
            textvariable=self.color_normal_var,
            values=["normal", "gris", "negrita"],
            width=10,
            state='readonly'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Formato de salida
        ttk.Label(display_frame, text="Formato de salida:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.output_format_var = tk.StringVar(value="Pantalla")
        format_combo = ttk.Combobox(
            display_frame,
            textvariable=self.output_format_var,
            values=["Pantalla", "PDF", "Excel", "CSV", "Impresión Directa"],
            state='readonly',
            width=25
        )
        format_combo.grid(row=2, column=1, sticky="w", pady=10)
        
        # Incluir totales y resumen
        self.include_totals_var = tk.BooleanVar(value=True)
        self.include_summary_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            display_frame,
            text="Incluir totales de importes",
            variable=self.include_totals_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        ttk.Checkbutton(
            display_frame,
            text="Incluir resumen por estado",
            variable=self.include_summary_var
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Frame para botones
        self.button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        # Agregar botón de vista previa
        ttk.Button(
            self.button_frame,
            text="Vista Previa",
            command=self._show_preview,
            width=12
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Agregar botón para generar alertas
        ttk.Button(
            self.button_frame,
            text="Generar Alertas",
            command=self._generate_alerts,
            width=12
        ).pack(side=tk.LEFT, padx=(0, 5))
    
    def _select_cutoff_date(self) -> None:
        """Abre diálogo para seleccionar fecha de corte."""
        try:
            current_date_str = self.cutoff_date_var.get()
            if current_date_str:
                current_date = datetime.strptime(current_date_str, "%d/%m/%Y")
            else:
                current_date = datetime.now()
            
            # Usar tkcalendar si está disponible
            try:
                from tkcalendar import Calendar
                
                top = tk.Toplevel(self)
                top.title("Seleccionar Fecha de Corte")
                top.transient(self)
                top.grab_set()
                
                cal = Calendar(top, selectmode='day', date_pattern='dd/mm/yyyy')
                cal.selection_set(current_date)
                cal.pack(padx=10, pady=10)
                
                def on_accept():
                    self.cutoff_date_var.set(cal.get_date())
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
                    "Fecha de Corte",
                    "Ingrese fecha de corte (DD/MM/AAAA):",
                    initialvalue=current_date_str,
                    parent=self
                )
                if new_date:
                    try:
                        datetime.strptime(new_date, "%d/%m/%Y")
                        self.cutoff_date_var.set(new_date)
                    except ValueError:
                        messagebox.showerror("Error", "Formato inválido", parent=self)
                        
        except ValueError:
            messagebox.showerror("Error", "Fecha actual inválida", parent=self)
    
    def _select_return_range(self) -> None:
        """Abre diálogo para seleccionar rango de fechas de regreso."""
        dialog = DateRangeDialog(
            self,
            title="Seleccionar Rango de Fechas de Regreso"
        )
        
        result = dialog.show()
        if result:
            self.return_start_var.set(result['start_date_str'])
            self.return_end_var.set(result['end_date_str'])
    
    def _show_preview(self) -> None:
        """Muestra una vista previa del reporte."""
        if self._validate():
            params = self._get_result_data()
            
            preview_msg = f"Vista previa del reporte:\n\n"
            preview_msg += f"Fecha de corte: {params['cutoff_date_str']}\n"
            preview_msg += f"Días de gracia: {params['grace_days']}\n"
            preview_msg += f"Entidad: {params['entity']}\n"
            preview_msg += f"Estado: {params['advance_status']}\n"
            
            if params['department'] != "TODOS":
                preview_msg += f"Departamento: {params['department']}\n"
            
            if params['employee'] != "TODOS":
                preview_msg += f"Empleado: {params['employee']}\n"
            
            if params['min_amount'] or params['max_amount']:
                preview_msg += f"Importe: {params['min_amount'] or '0'} a {params['max_amount'] or '∞'} CUP\n"
            
            if params['return_start']:
                preview_msg += f"Fecha regreso: {params['return_start']} a {params['return_end']}\n"
            
            preview_msg += f"\nSe mostrarán anticipos pendientes de liquidación.\n"
            preview_msg += f"Vencidos en {params['color_expired']}, próximos en {params['color_near']}.\n"
            preview_msg += f"Formato: {params['output_format']}"
            
            messagebox.showinfo("Vista Previa", preview_msg, parent=self)
    
    def _generate_alerts(self) -> None:
        """Genera alertas para anticipos vencidos o próximos a vencer."""
        messagebox.showinfo(
            "Generar Alertas",
            "Esta función generaría alertas/recordatorios para:\n"
            "1. Anticipos vencidos (> 72h)\n"
            "2. Anticipos próximos a vencer (próximos 3 días)\n"
            "3. Envío de notificaciones a responsables\n\n"
            "Implementación pendiente de integración con módulo de notificaciones.",
            parent=self
        )
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos requeridos."""
        errors = []
        
        # Validar fecha de corte
        date_str = self.cutoff_date_var.get().strip()
        if not date_str:
            errors.append("La fecha de corte es requerida")
        else:
            try:
                datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                errors.append("Formato de fecha inválido (use DD/MM/AAAA)")
        
        # Validar días de gracia
        try:
            grace_days = int(self.grace_days_var.get())
            if grace_days < 0 or grace_days > 30:
                errors.append("Días de gracia deben estar entre 0 y 30")
        except ValueError:
            errors.append("Días de gracia inválidos")
        
        # Validar importes
        min_amount = self.min_amount_var.get().strip()
        max_amount = self.max_amount_var.get().strip()
        
        if min_amount:
            try:
                float(min_amount)
            except ValueError:
                errors.append("Importe mínimo inválido")
        
        if max_amount:
            try:
                float(max_amount)
            except ValueError:
                errors.append("Importe máximo inválido")
        
        if min_amount and max_amount:
            try:
                if float(min_amount) > float(max_amount):
                    errors.append("El importe mínimo no puede ser mayor al máximo")
            except:
                pass
        
        # Validar que al menos una columna esté seleccionada
        if not (self.show_name_var.get() or 
                self.show_advance_num_var.get() or 
                self.show_amount_cup_var.get() or
                self.show_amount_cuc_var.get() or
                self.show_card_var.get() or
                self.show_card_balance_var.get() or
                self.show_return_date_var.get() or
                self.show_days_trans_var.get()):
            errors.append("Seleccione al menos una columna para el reporte")
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de configuración del reporte."""
        date_str = self.cutoff_date_var.get().strip()
        cutoff_date = datetime.strptime(date_str, "%d/%m/%Y")
        
        # Procesar departamento
        department = self.department_var.get()
        dept_code = department.split(" - ")[0] if " - " in department else department
        
        # Procesar empleado
        employee = self.employee_var.get()
        emp_code = employee.split(" - ")[0] if " - " in employee else employee
        
        # Determinar columnas a incluir
        columns = []
        if self.show_name_var.get():
            columns.append("nombre")
        if self.show_advance_num_var.get():
            columns.append("numero_anticipo")
        if self.show_amount_cup_var.get():
            columns.append("importe_cup")
        if self.show_amount_cuc_var.get():
            columns.append("hospedaje_cuc")
        if self.show_card_var.get():
            columns.append("tarjeta")
        if self.show_card_balance_var.get():
            columns.append("saldo_tarjeta")
        if self.show_return_date_var.get():
            columns.append("fecha_regreso")
        if self.show_days_trans_var.get():
            columns.append("dias_transcurridos")
        
        return {
            'cutoff_date': cutoff_date,
            'cutoff_date_str': date_str,
            'grace_days': int(self.grace_days_var.get()),
            'entity': self.entity_var.get(),
            'advance_status': self.advance_status_var.get(),
            'department': dept_code if dept_code != "TODOS" else None,
            'department_display': department,
            'employee': emp_code if emp_code != "TODOS" else None,
            'employee_display': employee,
            'min_amount': self.min_amount_var.get().strip() if self.min_amount_var.get().strip() else None,
            'max_amount': self.max_amount_var.get().strip() if self.max_amount_var.get().strip() else None,
            'return_start': self.return_start_var.get().strip() if self.return_start_var.get().strip() else None,
            'return_end': self.return_end_var.get().strip() if self.return_end_var.get().strip() else None,
            'columns': columns,
            'color_expired': self.color_expired_var.get(),
            'color_near': self.color_near_var.get(),
            'color_normal': self.color_normal_var.get(),
            'output_format': self.output_format_var.get(),
            'include_totals': self.include_totals_var.get(),
            'include_summary': self.include_summary_var.get(),
            'report_name': 'unsettled_advances'
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Crear diálogo con datos de ejemplo
    dialog = UnsettledAdvancesDialog(root)
    result = dialog.show()
    
    if result:
        print("Configuración del reporte de Anticipos Sin Liquidar:")
        print(f"  Fecha de corte: {result['cutoff_date_str']}")
        print(f"  Días de gracia: {result['grace_days']}")
        print(f"  Entidad: {result['entity']}")
        print(f"  Estado: {result['advance_status']}")
        
        if result['department']:
            print(f"  Departamento: {result['department_display']}")
        
        if result['employee']:
            print(f"  Empleado: {result['employee_display']}")
        
        if result['min_amount'] or result['max_amount']:
            print(f"  Importe: {result['min_amount'] or '0'} a {result['max_amount'] or '∞'} CUP")
        
        if result['return_start']:
            print(f"  Fecha regreso: {result['return_start']} a {result['return_end']}")
        
        print(f"  Columnas: {', '.join(result['columns'])}")
        print(f"  Colores - Vencidos: {result['color_expired']}")
        print(f"  Colores - Próximos: {result['color_near']}")
        print(f"  Formato: {result['output_format']}")
        print(f"  Incluir totales: {result['include_totals']}")
        print(f"  Incluir resumen: {result['include_summary']}")
    else:
        print("Diálogo cancelado")
    
    root.destroy()
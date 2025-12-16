"""
cards_in_advance_dialog.py
Diálogo para configurar el reporte de "Tarjetas en anticipo".
Muestra tarjetas asignadas a trabajadores con anticipos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog
from .date_range_dialog import DateRangeDialog


class CardsInAdvanceDialog(BaseReportDialog):
    """Diálogo para configurar reporte de tarjetas en anticipo"""
    
    def __init__(self, parent, 
                 cashiers: Optional[List[str]] = None,
                 entities: Optional[List[str]] = None,
                 responsibles: Optional[List[str]] = None):
        """
        Inicializa el diálogo para reporte de tarjetas en anticipo.
        
        Args:
            parent: Ventana padre
            cashiers: Lista de cajeros disponibles
            entities: Lista de entidades disponibles
            responsibles: Lista de responsables disponibles
        """
        self.cashiers = cashiers or ["TODOS", "KAREN GUZMAN FIGUEROA", "OTRO CAJERO"]
        self.entities = entities or ["CIMEX - Gerencia Administrativa"]
        self.responsibles = responsibles or ["TODOS", "BRIGADA MITO LUIS", "ALMACEN REGULADOR MIGUEL"]
        
        super().__init__(parent, "Tarjetas en Anticipo", width=600, height=600)
    
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
            text="Configurar reporte de Tarjetas en Anticipo",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Descripción del reporte
        ttk.Label(
            main_frame,
            text="Reporte de submayor de la cuenta 16201002 - Tarjetas asignadas a trabajadores con anticipos.",
            font=('Arial', 9)
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Sección de parámetros básicos
        basic_frame = self._create_section(main_frame, "Parámetros del Reporte", 2)
        
        # Fecha del reporte
        ttk.Label(basic_frame, text="Fecha del reporte:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.report_date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        date_frame = ttk.Frame(basic_frame)
        date_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        ttk.Entry(
            date_frame, 
            textvariable=self.report_date_var,
            width=12,
            state='readonly'
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            date_frame,
            text="📅",
            command=self._select_date,
            width=3
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Hora del reporte
        ttk.Label(basic_frame, text="Hora del reporte:").grid(
            row=0, column=2, sticky="w", padx=(20, 10), pady=10
        )
        
        time_frame = ttk.Frame(basic_frame)
        time_frame.grid(row=0, column=3, sticky="w", pady=10)
        
        # Hora
        hour_var = tk.StringVar(value=str(datetime.now().hour).zfill(2))
        hour_combo = ttk.Combobox(
            time_frame,
            textvariable=hour_var,
            values=[str(i).zfill(2) for i in range(24)],
            width=3,
            state='readonly'
        )
        hour_combo.pack(side=tk.LEFT)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT, padx=2)
        
        # Minutos
        minute_var = tk.StringVar(value=str(datetime.now().minute).zfill(2))
        minute_combo = ttk.Combobox(
            time_frame,
            textvariable=minute_var,
            values=[str(i).zfill(2) for i in range(0, 60, 5)],
            width=3,
            state='readonly'
        )
        minute_combo.pack(side=tk.LEFT)
        
        self.hour_var = hour_var
        self.minute_var = minute_var
        
        # Entidad
        ttk.Label(basic_frame, text="Entidad:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.entity_var = tk.StringVar(value=self.entities[0])
        entity_combo = ttk.Combobox(
            basic_frame,
            textvariable=self.entity_var,
            values=self.entities,
            state='readonly',
            width=25
        )
        entity_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Cajero
        ttk.Label(basic_frame, text="Cajero:").grid(
            row=1, column=2, sticky="w", padx=(20, 10), pady=10
        )
        
        self.cashier_var = tk.StringVar(value="TODOS")
        cashier_combo = ttk.Combobox(
            basic_frame,
            textvariable=self.cashier_var,
            values=self.cashiers,
            state='readonly',
            width=25
        )
        cashier_combo.grid(row=1, column=3, sticky="w", pady=10)
        
        # Sección de filtros
        filters_frame = self._create_section(main_frame, "Filtros Avanzados", 3)
        
        # Responsable
        ttk.Label(filters_frame, text="Responsable:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.responsible_var = tk.StringVar(value="TODOS")
        responsible_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.responsible_var,
            values=self.responsibles,
            state='readonly',
            width=30
        )
        responsible_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Estado del anticipo
        ttk.Label(filters_frame, text="Estado del anticipo:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.advance_status_var = tk.StringVar(value="todos")
        status_frame = ttk.Frame(filters_frame)
        status_frame.grid(row=1, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(
            status_frame,
            text="Todos",
            variable=self.advance_status_var,
            value="todos"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            status_frame,
            text="Activos",
            variable=self.advance_status_var,
            value="activos"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            status_frame,
            text="Vencidos",
            variable=self.advance_status_var,
            value="vencidos"
        ).pack(side=tk.LEFT)
        
        # Días transcurridos
        ttk.Label(filters_frame, text="Días transcurridos:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        days_frame = ttk.Frame(filters_frame)
        days_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        self.min_days_var = tk.StringVar(value="0")
        self.max_days_var = tk.StringVar(value="999")
        
        ttk.Entry(days_frame, textvariable=self.min_days_var, width=5).pack(side=tk.LEFT)
        ttk.Label(days_frame, text=" a ").pack(side=tk.LEFT, padx=5)
        ttk.Entry(days_frame, textvariable=self.max_days_var, width=5).pack(side=tk.LEFT)
        
        # Rango de fechas de regreso
        ttk.Label(filters_frame, text="Fecha de regreso:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        return_frame = ttk.Frame(filters_frame)
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
        display_frame = self._create_section(main_frame, "Opciones de Visualización", 4)
        
        # Columnas a mostrar
        ttk.Label(display_frame, text="Columnas a incluir:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        columns_frame = ttk.Frame(display_frame)
        columns_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        # Primera fila de columnas
        row1_frame = ttk.Frame(columns_frame)
        row1_frame.pack(anchor='w')
        
        self.show_card_var = tk.BooleanVar(value=True)
        self.show_pin_var = tk.BooleanVar(value=True)
        self.show_balance_var = tk.BooleanVar(value=True)
        self.show_advance_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            row1_frame,
            text="Tarjeta",
            variable=self.show_card_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row1_frame,
            text="PIN",
            variable=self.show_pin_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row1_frame,
            text="Saldo",
            variable=self.show_balance_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row1_frame,
            text="Anticipo",
            variable=self.show_advance_var
        ).pack(side=tk.LEFT)
        
        # Segunda fila de columnas
        row2_frame = ttk.Frame(columns_frame)
        row2_frame.pack(anchor='w', pady=(5, 0))
        
        self.show_responsible_var = tk.BooleanVar(value=True)
        self.show_return_var = tk.BooleanVar(value=True)
        self.show_days_var = tk.BooleanVar(value=True)
        self.show_status_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            row2_frame,
            text="Responsable",
            variable=self.show_responsible_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row2_frame,
            text="Fecha Regreso",
            variable=self.show_return_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row2_frame,
            text="Días Trans.",
            variable=self.show_days_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            row2_frame,
            text="Estado",
            variable=self.show_status_var
        ).pack(side=tk.LEFT)
        
        # Resaltar vencidos
        ttk.Label(display_frame, text="Resaltar registros:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        highlight_frame = ttk.Frame(display_frame)
        highlight_frame.grid(row=1, column=1, sticky="w", pady=10)
        
        self.highlight_expired_var = tk.BooleanVar(value=True)
        self.highlight_near_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            highlight_frame,
            text="Vencidos (rojo)",
            variable=self.highlight_expired_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            highlight_frame,
            text="Por vencer en 72h (amarillo)",
            variable=self.highlight_near_var
        ).pack(side=tk.LEFT)
        
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
        
        # Incluir totales
        self.include_totals_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            display_frame,
            text="Incluir totales de saldo y anticipo",
            variable=self.include_totals_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Frame para botones
        self.button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        # Agregar botón de vista previa
        ttk.Button(
            self.button_frame,
            text="Vista Previa",
            command=self._show_preview,
            width=12
        ).pack(side=tk.LEFT, padx=(0, 5))
    
    def _select_date(self) -> None:
        """Abre diálogo para seleccionar fecha del reporte."""
        try:
            current_date_str = self.report_date_var.get()
            if current_date_str:
                current_date = datetime.strptime(current_date_str, "%d/%m/%Y")
            else:
                current_date = datetime.now()
            
            # Usar tkcalendar si está disponible
            try:
                from tkcalendar import Calendar
                
                top = tk.Toplevel(self)
                top.title("Seleccionar Fecha del Reporte")
                top.transient(self)
                top.grab_set()
                
                cal = Calendar(top, selectmode='day', date_pattern='dd/mm/yyyy')
                cal.selection_set(current_date)
                cal.pack(padx=10, pady=10)
                
                def on_accept():
                    self.report_date_var.set(cal.get_date())
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
                    "Fecha del Reporte",
                    "Ingrese fecha (DD/MM/AAAA):",
                    initialvalue=current_date_str,
                    parent=self
                )
                if new_date:
                    try:
                        datetime.strptime(new_date, "%d/%m/%Y")
                        self.report_date_var.set(new_date)
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
            
            # Construir mensaje de vista previa
            preview_msg = f"Parámetros configurados:\n\n"
            preview_msg += f"Fecha: {params['report_date_str']}\n"
            preview_msg += f"Hora: {params['report_time']}\n"
            preview_msg += f"Entidad: {params['entity']}\n"
            preview_msg += f"Cajero: {params['cashier']}\n"
            preview_msg += f"Responsable: {params['responsible']}\n"
            preview_msg += f"Estado: {params['advance_status']}\n"
            
            if params['min_days'] != 0 or params['max_days'] != 999:
                preview_msg += f"Días transcurridos: {params['min_days']} a {params['max_days']}\n"
            
            if params['return_start'] and params['return_end']:
                preview_msg += f"Fecha regreso: {params['return_start']} a {params['return_end']}\n"
            
            preview_msg += f"Columnas: {len(params['columns'])}\n"
            preview_msg += f"Resaltar vencidos: {'Sí' if params['highlight_expired'] else 'No'}\n"
            preview_msg += f"Formato: {params['output_format']}\n"
            preview_msg += f"Incluir totales: {'Sí' if params['include_totals'] else 'No'}"
            
            messagebox.showinfo("Vista Previa", preview_msg, parent=self)
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos requeridos."""
        errors = []
        
        # Validar fecha
        date_str = self.report_date_var.get().strip()
        if not date_str:
            errors.append("La fecha del reporte es requerida")
        else:
            try:
                datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                errors.append("Formato de fecha inválido (use DD/MM/AAAA)")
        
        # Validar hora
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                errors.append("Hora inválida")
        except ValueError:
            errors.append("Hora inválida")
        
        # Validar días transcurridos
        try:
            min_days = int(self.min_days_var.get()) if self.min_days_var.get().strip() else 0
            max_days = int(self.max_days_var.get()) if self.max_days_var.get().strip() else 999
            
            if min_days < 0 or max_days < 0:
                errors.append("Los días transcurridos no pueden ser negativos")
            if min_days > max_days:
                errors.append("El día mínimo no puede ser mayor al día máximo")
        except ValueError:
            errors.append("Días transcurridos inválidos")
        
        # Validar que al menos una columna esté seleccionada
        if not (self.show_card_var.get() or 
                self.show_pin_var.get() or 
                self.show_balance_var.get() or
                self.show_advance_var.get() or
                self.show_responsible_var.get() or
                self.show_return_var.get() or
                self.show_days_var.get() or
                self.show_status_var.get()):
            errors.append("Seleccione al menos una columna para el reporte")
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de configuración del reporte."""
        date_str = self.report_date_var.get().strip()
        report_date = datetime.strptime(date_str, "%d/%m/%Y")
        
        # Construir hora
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        report_time = f"{hour:02d}:{minute:02d}"
        
        # Determinar columnas a incluir
        columns = []
        if self.show_card_var.get():
            columns.append("tarjeta")
        if self.show_pin_var.get():
            columns.append("pin")
        if self.show_balance_var.get():
            columns.append("saldo")
        if self.show_advance_var.get():
            columns.append("anticipo")
        if self.show_responsible_var.get():
            columns.append("responsable")
        if self.show_return_var.get():
            columns.append("fecha_regreso")
        if self.show_days_var.get():
            columns.append("dias_transcurridos")
        if self.show_status_var.get():
            columns.append("estado")
        
        return {
            'report_date': report_date,
            'report_date_str': date_str,
            'report_time': report_time,
            'report_time_str': f"{date_str} {report_time}",
            'entity': self.entity_var.get(),
            'cashier': self.cashier_var.get(),
            'responsible': self.responsible_var.get(),
            'advance_status': self.advance_status_var.get(),
            'min_days': int(self.min_days_var.get()) if self.min_days_var.get().strip() else 0,
            'max_days': int(self.max_days_var.get()) if self.max_days_var.get().strip() else 999,
            'return_start': self.return_start_var.get().strip() if self.return_start_var.get().strip() else None,
            'return_end': self.return_end_var.get().strip() if self.return_end_var.get().strip() else None,
            'columns': columns,
            'highlight_expired': self.highlight_expired_var.get(),
            'highlight_near': self.highlight_near_var.get(),
            'output_format': self.output_format_var.get(),
            'include_totals': self.include_totals_var.get(),
            'report_name': 'cards_in_advance'
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Datos de ejemplo
    cashiers = ["TODOS", "KAREN GUZMAN FIGUEROA", "JUAN PEREZ"]
    entities = ["CIMEX - Gerencia Administrativa", "CIMEX - Gerencia Comercial"]
    responsibles = ["TODOS", "BRIGADA MITO LUIS", "ALMACEN REGULADOR MIGUEL", 
                   "BRIGADA DE INVERSION JOSE"]
    
    dialog = CardsInAdvanceDialog(
        root, 
        cashiers=cashiers, 
        entities=entities,
        responsibles=responsibles
    )
    result = dialog.show()
    
    if result:
        print("Configuración del reporte de Tarjetas en Anticipo:")
        print(f"  Fecha: {result['report_date_str']}")
        print(f"  Hora: {result['report_time']}")
        print(f"  Entidad: {result['entity']}")
        print(f"  Cajero: {result['cashier']}")
        print(f"  Responsable: {result['responsible']}")
        print(f"  Estado: {result['advance_status']}")
        print(f"  Días: {result['min_days']} - {result['max_days']}")
        if result['return_start']:
            print(f"  Fecha regreso: {result['return_start']} a {result['return_end']}")
        print(f"  Columnas: {', '.join(result['columns'])}")
        print(f"  Resaltar vencidos: {result['highlight_expired']}")
        print(f"  Formato: {result['output_format']}")
        print(f"  Incluir totales: {result['include_totals']}")
    else:
        print("Diálogo cancelado")
    
    root.destroy()
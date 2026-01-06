"""
cards_in_cash_dialog.py
Diálogo para configurar el reporte de "Tarjetas en la caja central".
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Dict, Any, List
from .base_report_dialog import BaseReportDialog
from .date_range_dialog import DateRangeDialog


class CardsInCashDialog(BaseReportDialog):
    """Diálogo para configurar reporte de tarjetas en caja central"""
    
    def __init__(self, parent, cashiers: Optional[List[str]] = None,
                 entities: Optional[List[str]] = None):
        """
        Inicializa el diálogo para reporte de tarjetas en caja.
        
        Args:
            parent: Ventana padre
            cashiers: Lista de cajeros disponibles
            entities: Lista de entidades disponibles
        """
        self.cashiers = cashiers or ["TODOS", "KAREN GUZMAN FIGUEROA", "OTRO CAJERO"]
        self.entities = entities or ["CIMEX - Gerencia Administrativa"]
        
        super().__init__(parent, "Tarjetas en Caja Central", width=500, height=450)
    
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
            text="Configurar reporte de Tarjetas en Caja Central",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Sección de parámetros básicos
        basic_frame = self._create_section(main_frame, "Parámetros Básicos", 1)
        
        # Fecha del reporte
        ttk.Label(basic_frame, text="Fecha del reporte:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.report_date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.report_date_entry = ttk.Entry(
            basic_frame, 
            textvariable=self.report_date_var,
            width=15,
            state='readonly'  # Solo se selecciona desde calendario
        )
        self.report_date_entry.grid(row=0, column=1, sticky="w", pady=10)
        
        # Botón calendario
        self.date_btn = ttk.Button(
            basic_frame,
            text="📅 Seleccionar",
            command=self._select_date,
            width=12
        )
        self.date_btn.grid(row=0, column=2, padx=(10, 0), pady=10)
        
        # Hora del reporte
        ttk.Label(basic_frame, text="Hora del reporte:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        # Frame para hora
        time_frame = ttk.Frame(basic_frame)
        time_frame.grid(row=1, column=1, sticky="w", pady=10)
        
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
            values=[str(i).zfill(2) for i in range(0, 60, 5)],  # Saltos de 5 min
            width=3,
            state='readonly'
        )
        minute_combo.pack(side=tk.LEFT)
        
        self.hour_var = hour_var
        self.minute_var = minute_var
        
        # Sección de filtros
        filters_frame = self._create_section(main_frame, "Filtros", 2)
        
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
            width=30
        )
        entity_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Cajero
        ttk.Label(filters_frame, text="Cajero:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.cashier_var = tk.StringVar(value="TODOS")
        cashier_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.cashier_var,
            values=self.cashiers,
            state='readonly',
            width=30
        )
        cashier_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Tipo de reporte
        ttk.Label(filters_frame, text="Tipo de reporte:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.report_type_var = tk.StringVar(value="Diario al final del día")
        report_type_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.report_type_var,
            values=["Diario al final del día", "Detallado por movimientos", "Resumen general"],
            state='readonly',
            width=30
        )
        report_type_combo.grid(row=2, column=1, sticky="w", pady=10)
        
        # Sección de opciones de salida
        output_frame = self._create_section(main_frame, "Opciones de Salida", 3)
        
        # Formato de salida
        ttk.Label(output_frame, text="Formato:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.format_var = tk.StringVar(value="Pantalla")
        format_combo = ttk.Combobox(
            output_frame,
            textvariable=self.format_var,
            values=["Pantalla", "PDF", "Excel", "CSV", "Impresión Directa"],
            state='readonly',
            width=20
        )
        format_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Incluir columnas
        ttk.Label(output_frame, text="Columnas a incluir:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        # Frame para checkboxes de columnas
        columns_frame = ttk.Frame(output_frame)
        columns_frame.grid(row=1, column=1, sticky="w", pady=10)
        
        # Variables para checkboxes
        self.include_card_var = tk.BooleanVar(value=True)
        self.include_pin_var = tk.BooleanVar(value=True)
        self.include_balance_var = tk.BooleanVar(value=True)
        self.include_status_var = tk.BooleanVar(value=False)
        self.include_owner_var = tk.BooleanVar(value=False)
        
        # Crear checkboxes
        ttk.Checkbutton(
            columns_frame,
            text="Número de Tarjeta",
            variable=self.include_card_var
        ).pack(anchor='w')
        
        ttk.Checkbutton(
            columns_frame,
            text="PIN",
            variable=self.include_pin_var
        ).pack(anchor='w')
        
        ttk.Checkbutton(
            columns_frame,
            text="Saldo",
            variable=self.include_balance_var
        ).pack(anchor='w')
        
        ttk.Checkbutton(
            columns_frame,
            text="Estado",
            variable=self.include_status_var
        ).pack(anchor='w')
        
        ttk.Checkbutton(
            columns_frame,
            text="Propietario",
            variable=self.include_owner_var
        ).pack(anchor='w')
        
        # Checkbox para incluir totales
        self.include_totals_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            output_frame,
            text="Incluir totales al final",
            variable=self.include_totals_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Frame para botones
        self.button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        # Agregar botón de vista previa
        self.preview_button = ttk.Button(
            self.button_frame,
            text="Vista Previa",
            command=self._show_preview,
            width=12
        )
        self.preview_button.pack(side=tk.LEFT, padx=(0, 5))
    
    def _select_date(self) -> None:
        """Abre diálogo para seleccionar fecha."""
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
                top.title("Seleccionar Fecha")
                top.transient(self)
                top.grab_set()
                
                cal = Calendar(top, selectmode='day', date_pattern='dd/mm/yyyy')
                cal.selection_set(current_date)
                cal.pack(padx=10, pady=10)
                
                def on_accept():
                    self.report_date_var.set(cal.get_date())
                    top.destroy()
                
                ttk.Button(top, text="Aceptar", command=on_accept).pack(pady=(0, 10))
                
                # Centrar en el diálogo principal
                top.update_idletasks()
                x = self.winfo_x() + (self.winfo_width() // 2) - (top.winfo_width() // 2)
                y = self.winfo_y() + (self.winfo_height() // 2) - (top.winfo_height() // 2)
                top.geometry(f"+{x}+{y}")
                
            except ImportError:
                # Fallback: pedir fecha manualmente
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
                        messagebox.showerror("Error", "Formato de fecha inválido", parent=self)
                        
        except ValueError:
            messagebox.showerror("Error", "Fecha actual inválida", parent=self)
    
    def _show_preview(self) -> None:
        """Muestra una vista previa del reporte con los parámetros actuales."""
        if self._validate():
            params = self._get_result_data()
            messagebox.showinfo(
                "Vista Previa",
                f"Parámetros configurados:\n\n"
                f"Fecha: {params['report_date_str']}\n"
                f"Hora: {params['report_time_str']}\n"
                f"Entidad: {params['entity']}\n"
                f"Cajero: {params['cashier']}\n"
                f"Tipo: {params['report_type']}\n"
                f"Formato: {params['output_format']}\n\n"
                f"El reporte mostrará las tarjetas disponibles en caja central.",
                parent=self
            )
    
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
        
        # Validar que al menos una columna esté seleccionada
        if not (self.include_card_var.get() or 
                self.include_pin_var.get() or 
                self.include_balance_var.get()):
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
        if self.include_card_var.get():
            columns.append("tarjeta")
        if self.include_pin_var.get():
            columns.append("pin")
        if self.include_balance_var.get():
            columns.append("saldo")
        if self.include_status_var.get():
            columns.append("estado")
        if self.include_owner_var.get():
            columns.append("propietario")
        
        return {
            'report_date': report_date,
            'report_date_str': date_str,
            'report_time': report_time,
            'report_time_str': f"{date_str} {report_time}",
            'entity': self.entity_var.get(),
            'cashier': self.cashier_var.get(),
            'report_type': self.report_type_var.get(),
            'output_format': self.format_var.get(),
            'include_totals': self.include_totals_var.get(),
            'columns': columns,
            'report_name': 'cards_in_cash'
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Datos de ejemplo
    cashiers = ["TODOS", "KAREN GUZMAN FIGUEROA", "JUAN PEREZ", "MARIA LOPEZ"]
    entities = ["CIMEX - Gerencia Administrativa", "CIMEX - Gerencia Comercial", "OTRA ENTIDAD"]
    
    dialog = CardsInCashDialog(root, cashiers=cashiers, entities=entities)
    result = dialog.show()
    
    if result:
        print("Configuración del reporte de Tarjetas en Caja Central:")
        print(f"  Fecha: {result['report_date_str']}")
        print(f"  Hora: {result['report_time']}")
        print(f"  Entidad: {result['entity']}")
        print(f"  Cajero: {result['cashier']}")
        print(f"  Tipo: {result['report_type']}")
        print(f"  Formato: {result['output_format']}")
        print(f"  Columnas: {', '.join(result['columns'])}")
        print(f"  Incluir totales: {result['include_totals']}")
    else:
        print("Diálogo cancelado")
    
    root.destroy()
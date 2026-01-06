"""
date_range_dialog.py
Diálogo para seleccionar rango de fechas para reportes.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .base_report_dialog import BaseReportDialog


class DateRangeDialog(BaseReportDialog):
    """Diálogo para seleccionar un rango de fechas"""
    
    def __init__(self, parent, 
                 default_start: Optional[datetime] = None,
                 default_end: Optional[datetime] = None,
                 title: str = "Seleccionar Rango de Fechas"):
        """
        Inicializa el diálogo de rango de fechas.
        
        Args:
            parent: Ventana padre
            default_start: Fecha de inicio por defecto (None para hoy)
            default_end: Fecha de fin por defecto (None para hoy)
            title: Título del diálogo
        """
        self.default_start = default_start or datetime.now()
        self.default_end = default_end or datetime.now()
        
        super().__init__(parent, title, width=450, height=350)
    
    def _create_widgets(self) -> None:
        """Crea los widgets específicos del diálogo de rango de fechas."""
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
            text="Seleccione el rango de fechas para el reporte:",
            font=('Arial', 10)
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Sección de fechas
        dates_frame = self._create_section(main_frame, "Rango de Fechas", 1)
        
        # Fecha de inicio
        ttk.Label(dates_frame, text="Fecha Inicio:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(
            dates_frame, 
            textvariable=self.start_date_var,
            width=15
        )
        self.start_date_entry.grid(row=0, column=1, sticky="w", pady=10)
        
        # Botón calendario para fecha inicio
        self.start_cal_btn = ttk.Button(
            dates_frame,
            text="📅",
            width=3,
            command=lambda: self._show_calendar(self.start_date_var)
        )
        self.start_cal_btn.grid(row=0, column=2, padx=(5, 0), pady=10)
        
        # Fecha de fin
        ttk.Label(dates_frame, text="Fecha Fin:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(
            dates_frame, 
            textvariable=self.end_date_var,
            width=15
        )
        self.end_date_entry.grid(row=1, column=1, sticky="w", pady=10)
        
        # Botón calendario para fecha fin
        self.end_cal_btn = ttk.Button(
            dates_frame,
            text="📅",
            width=3,
            command=lambda: self._show_calendar(self.end_date_var)
        )
        self.end_cal_btn.grid(row=1, column=2, padx=(5, 0), pady=10)
        
        # Opciones rápidas de rango
        quick_range_frame = self._create_section(main_frame, "Rangos Predefinidos", 2)
        
        # Botones de rangos rápidos
        ranges = [
            ("Hoy", 0),
            ("Ayer", 1),
            ("Últimos 7 días", 7),
            ("Últimos 30 días", 30),
            ("Este Mes", "month"),
            ("Mes Anterior", "last_month")
        ]
        
        for i, (text, days) in enumerate(ranges):
            btn = ttk.Button(
                quick_range_frame,
                text=text,
                command=lambda d=days: self._set_quick_range(d),
                width=15
            )
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5)
        
        # Información del rango seleccionado
        self.info_label = ttk.Label(
            main_frame,
            text="",
            font=('Arial', 9, 'italic'),
            foreground='blue'
        )
        self.info_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Frame para botones (heredado de BaseReportDialog)
        self.button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        # Configurar valores por defecto
        self._set_default_dates()
        
        # Bind eventos para actualizar información
        self.start_date_var.trace_add('write', self._update_range_info)
        self.end_date_var.trace_add('write', self._update_range_info)
    
    def _set_default_dates(self) -> None:
        """Establece las fechas por defecto."""
        date_format = "%d/%m/%Y"
        self.start_date_var.set(self.default_start.strftime(date_format))
        self.end_date_var.set(self.default_end.strftime(date_format))
        self._update_range_info()
    
    def _show_calendar(self, date_var: tk.StringVar) -> None:
        """Muestra un diálogo de calendario para seleccionar fecha."""
        # Nota: Para una implementación completa, se puede usar tkcalendar
        # Aquí se implementa una versión simple
        try:
            from tkcalendar import Calendar
            
            top = tk.Toplevel(self)
            top.title("Seleccionar Fecha")
            top.transient(self)
            top.grab_set()
            
            cal = Calendar(top, selectmode='day', date_pattern='dd/mm/yyyy')
            cal.pack(padx=10, pady=10)
            
            # Botón para aceptar
            def on_accept():
                date_var.set(cal.get_date())
                top.destroy()
            
            ttk.Button(top, text="Aceptar", command=on_accept).pack(pady=(0, 10))
            
            # Centrar en el diálogo principal
            top.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() // 2) - (top.winfo_width() // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (top.winfo_height() // 2)
            top.geometry(f"+{x}+{y}")
            
        except ImportError:
            # Fallback si tkcalendar no está instalado
            messagebox.showinfo(
                "Información",
                "Para usar el selector de fechas gráfico, instale tkcalendar:\n"
                "pip install tkcalendar\n\n"
                "Por ahora, ingrese la fecha manualmente en formato DD/MM/AAAA.",
                parent=self
            )
    
    def _set_quick_range(self, days: Any) -> None:
        """
        Establece un rango de fechas predefinido.
        
        Args:
            days: Número de días o string especial
        """
        today = datetime.now()
        date_format = "%d/%m/%Y"
        
        if days == 0:  # Hoy
            start_date = today
            end_date = today
        
        elif days == 1:  # Ayer
            start_date = today - timedelta(days=1)
            end_date = today - timedelta(days=1)
        
        elif isinstance(days, int):  # Últimos N días
            start_date = today - timedelta(days=days-1)
            end_date = today
        
        elif days == "month":  # Este mes
            start_date = today.replace(day=1)
            end_date = today
        
        elif days == "last_month":  # Mes anterior
            first_day_current = today.replace(day=1)
            end_date = first_day_current - timedelta(days=1)
            start_date = end_date.replace(day=1)
        
        else:
            return
        
        self.start_date_var.set(start_date.strftime(date_format))
        self.end_date_var.set(end_date.strftime(date_format))
    
    def _update_range_info(self, *args) -> None:
        """Actualiza la información del rango seleccionado."""
        try:
            start_str = self.start_date_var.get()
            end_str = self.end_date_var.get()
            
            if not start_str or not end_str:
                self.info_label.config(text="")
                return
            
            start_date = datetime.strptime(start_str, "%d/%m/%Y")
            end_date = datetime.strptime(end_str, "%d/%m/%Y")
            
            # Calcular diferencia
            delta = (end_date - start_date).days + 1
            
            if delta < 0:
                self.info_label.config(text="⚠️ Fecha fin debe ser mayor o igual a fecha inicio", 
                                     foreground='red')
            else:
                self.info_label.config(
                    text=f"Rango seleccionado: {delta} día{'s' if delta != 1 else ''}",
                    foreground='blue'
                )
                
        except ValueError:
            self.info_label.config(text="⚠️ Formato de fecha inválido (use DD/MM/AAAA)", 
                                 foreground='red')
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos de fecha requeridos."""
        errors = []
        
        # Validar fecha de inicio
        start_str = self.start_date_var.get().strip()
        if not start_str:
            errors.append("La fecha de inicio es requerida")
        else:
            try:
                start_date = datetime.strptime(start_str, "%d/%m/%Y")
            except ValueError:
                errors.append("Formato de fecha inicio inválido (use DD/MM/AAAA)")
        
        # Validar fecha de fin
        end_str = self.end_date_var.get().strip()
        if not end_str:
            errors.append("La fecha de fin es requerida")
        else:
            try:
                end_date = datetime.strptime(end_str, "%d/%m/%Y")
            except ValueError:
                errors.append("Formato de fecha fin inválido (use DD/MM/AAAA)")
        
        # Validar que fecha fin sea mayor o igual a fecha inicio
        if not errors:
            try:
                start_date = datetime.strptime(start_str, "%d/%m/%Y")
                end_date = datetime.strptime(end_str, "%d/%m/%Y")
                
                if end_date < start_date:
                    errors.append("La fecha fin debe ser mayor o igual a la fecha inicio")
            except:
                pass
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos del rango de fechas seleccionado."""
        start_str = self.start_date_var.get().strip()
        end_str = self.end_date_var.get().strip()
        
        start_date = datetime.strptime(start_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_str, "%d/%m/%Y")
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'start_date_str': start_str,
            'end_date_str': end_str,
            'days_range': (end_date - start_date).days + 1
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Diálogo con fechas por defecto
    dialog = DateRangeDialog(
        root,
        default_start=datetime.now() - timedelta(days=7),
        default_end=datetime.now()
    )
    
    result = dialog.show()
    
    if result:
        print("Rango seleccionado:")
        print(f"  Desde: {result['start_date_str']}")
        print(f"  Hasta: {result['end_date_str']}")
        print(f"  Días: {result['days_range']}")
    else:
        print("Diálogo cancelado")
    
    root.destroy()
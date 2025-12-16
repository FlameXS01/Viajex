"""
accounts_report_dialog.py
Diálogo para configurar el reporte de "Cuentas para reportes".
Muestra el catálogo de cuentas contables del sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog


class AccountsReportDialog(BaseReportDialog):
    """Diálogo para configurar reporte de cuentas contables"""
    
    def __init__(self, parent, 
                 account_types: Optional[List[Tuple[str, str]]] = None):
        """
        Inicializa el diálogo para reporte de cuentas.
        
        Args:
            parent: Ventana padre
            account_types: Lista de tipos de cuenta disponibles (código, descripción)
        """
        # Cuentas de ejemplo del PDF
        default_accounts = [
            ("83609800", "Gastos financieros/Compra Tarj"),
            ("14701002", "Pago Anticipado Tarjeta"),
            ("10110804", "Efectivo en caja /Tarjetas"),
            ("16201002", "Anticipo para Tarjeta"),
            ("16101001", "Anticipo para Dieta"),
            ("10110200", "Efectivo en Caja /Fondo")
        ]
        
        self.account_types = account_types or default_accounts
        
        super().__init__(parent, "Reporte de Cuentas Contables", width=550, height=500)
    
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
            text="Configurar reporte de Cuentas Contables",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Descripción
        ttk.Label(
            main_frame,
            text="Genera un catálogo de cuentas contables utilizadas en el sistema",
            font=('Arial', 9)
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Sección de selección de cuentas
        selection_frame = self._create_section(main_frame, "Selección de Cuentas", 2)
        
        # Opción: Todas las cuentas o seleccionadas
        ttk.Label(selection_frame, text="Mostrar:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.selection_mode_var = tk.StringVar(value="all")
        
        mode_frame = ttk.Frame(selection_frame)
        mode_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(
            mode_frame,
            text="Todas las cuentas",
            variable=self.selection_mode_var,
            value="all"
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            mode_frame,
            text="Cuentas seleccionadas",
            variable=self.selection_mode_var,
            value="selected"
        ).pack(side=tk.LEFT)
        
        # Frame para lista de cuentas seleccionables
        accounts_frame = ttk.LabelFrame(selection_frame, text="Cuentas Disponibles", padding="10")
        accounts_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 5))
        
        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(accounts_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lista de cuentas (Listbox con checkboxes simulados)
        self.accounts_listbox = tk.Listbox(
            accounts_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.MULTIPLE,
            height=8
        )
        self.accounts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.accounts_listbox.yview)
        
        # Botones para selección rápida
        btn_frame = ttk.Frame(accounts_frame)
        btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="Seleccionar\nTodo",
            command=self._select_all_accounts,
            width=10
        ).pack(pady=(0, 5))
        
        ttk.Button(
            btn_frame,
            text="Deseleccionar\nTodo",
            command=self._deselect_all_accounts,
            width=10
        ).pack(pady=(0, 5))
        
        ttk.Button(
            btn_frame,
            text="Invertir\nSelección",
            command=self._invert_selection,
            width=10
        ).pack()
        
        # Rango de cuentas
        ttk.Label(selection_frame, text="Rango de códigos:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        range_frame = ttk.Frame(selection_frame)
        range_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        self.start_account_var = tk.StringVar()
        self.end_account_var = tk.StringVar()
        
        ttk.Entry(range_frame, textvariable=self.start_account_var, width=10).pack(
            side=tk.LEFT
        )
        ttk.Label(range_frame, text=" a ").pack(side=tk.LEFT, padx=5)
        ttk.Entry(range_frame, textvariable=self.end_account_var, width=10).pack(
            side=tk.LEFT
        )
        
        ttk.Button(
            range_frame,
            text="Filtrar",
            command=self._filter_by_range,
            width=8
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Sección de opciones de formato
        format_frame = self._create_section(main_frame, "Opciones de Formato", 3)
        
        # Nivel de detalle
        ttk.Label(format_frame, text="Nivel de detalle:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.detail_level_var = tk.StringVar(value="normal")
        detail_combo = ttk.Combobox(
            format_frame,
            textvariable=self.detail_level_var,
            values=["Básico (solo código y descripción)", 
                   "Normal (con clasificación)",
                   "Detallado (con movimientos recientes)"],
            state='readonly',
            width=35
        )
        detail_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Formato de salida
        ttk.Label(format_frame, text="Formato de salida:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.output_format_var = tk.StringVar(value="Pantalla")
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.output_format_var,
            values=["Pantalla", "PDF", "Excel", "CSV", "Listado para Contabilidad"],
            state='readonly',
            width=35
        )
        format_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Ordenar por
        ttk.Label(format_frame, text="Ordenar por:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.sort_by_var = tk.StringVar(value="codigo")
        sort_frame = ttk.Frame(format_frame)
        sort_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(
            sort_frame,
            text="Código",
            variable=self.sort_by_var,
            value="codigo"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            sort_frame,
            text="Descripción",
            variable=self.sort_by_var,
            value="descripcion"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            sort_frame,
            text="Tipo",
            variable=self.sort_by_var,
            value="tipo"
        ).pack(side=tk.LEFT)
        
        # Incluir información adicional
        self.include_stats_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            format_frame,
            text="Incluir estadísticas de uso",
            variable=self.include_stats_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        self.include_empty_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            format_frame,
            text="Incluir cuentas sin movimientos",
            variable=self.include_empty_var
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Frame para botones
        self.button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        # Cargar cuentas en la lista
        self._load_accounts_list()
        
        # Bind eventos
        self.selection_mode_var.trace_add('write', self._on_selection_mode_change)
    
    def _load_accounts_list(self) -> None:
        """Carga las cuentas en el Listbox."""
        self.accounts_listbox.delete(0, tk.END)
        
        for account_code, account_desc in self.account_types:
            display_text = f"{account_code} - {account_desc}"
            self.accounts_listbox.insert(tk.END, display_text)
    
    def _select_all_accounts(self) -> None:
        """Selecciona todas las cuentas en la lista."""
        self.accounts_listbox.selection_set(0, tk.END)
    
    def _deselect_all_accounts(self) -> None:
        """Deselecciona todas las cuentas en la lista."""
        self.accounts_listbox.selection_clear(0, tk.END)
    
    def _invert_selection(self) -> None:
        """Invierte la selección actual."""
        all_indices = list(range(self.accounts_listbox.size()))
        selected_indices = self.accounts_listbox.curselection()
        
        # Crear nueva selección
        new_selection = [i for i in all_indices if i not in selected_indices]
        
        # Aplicar nueva selección
        self.accounts_listbox.selection_clear(0, tk.END)
        for index in new_selection:
            self.accounts_listbox.selection_set(index)
    
    def _filter_by_range(self) -> None:
        """Filtra las cuentas por rango de códigos."""
        start_code = self.start_account_var.get().strip()
        end_code = self.end_account_var.get().strip()
        
        if not start_code or not end_code:
            messagebox.showwarning("Advertencia", 
                                 "Ingrese ambos códigos para el rango",
                                 parent=self)
            return
        
        # Deseleccionar todo primero
        self._deselect_all_accounts()
        
        # Seleccionar cuentas en el rango
        for i in range(self.accounts_listbox.size()):
            item_text = self.accounts_listbox.get(i)
            account_code = item_text.split(" - ")[0]
            
            if start_code <= account_code <= end_code:
                self.accounts_listbox.selection_set(i)
    
    def _on_selection_mode_change(self, *args) -> None:
        """Habilita/deshabilita controles según el modo de selección."""
        mode = self.selection_mode_var.get()
        
        if mode == "all":
            # Deshabilitar controles de selección específica
            self.accounts_listbox.config(state='disabled')
            self.start_account_var.set("")
            self.end_account_var.set("")
        else:
            # Habilitar controles de selección específica
            self.accounts_listbox.config(state='normal')
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos del formulario."""
        errors = []
        
        # Validar que si se selecciona "cuentas seleccionadas", al menos una esté seleccionada
        if self.selection_mode_var.get() == "selected":
            selected_indices = self.accounts_listbox.curselection()
            if len(selected_indices) == 0:
                errors.append("Seleccione al menos una cuenta para el reporte")
        
        # Validar rango si se especificó
        start_code = self.start_account_var.get().strip()
        end_code = self.end_account_var.get().strip()
        
        if start_code and not end_code:
            errors.append("Ingrese el código final del rango")
        elif not start_code and end_code:
            errors.append("Ingrese el código inicial del rango")
        elif start_code and end_code:
            try:
                if int(start_code) > int(end_code):
                    errors.append("El código inicial debe ser menor o igual al código final")
            except ValueError:
                errors.append("Los códigos deben ser números")
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de configuración del reporte."""
        # Obtener cuentas seleccionadas
        selected_accounts = []
        if self.selection_mode_var.get() == "selected":
            selected_indices = self.accounts_listbox.curselection()
            for index in selected_indices:
                item_text = self.accounts_listbox.get(index)
                account_code, account_desc = item_text.split(" - ", 1)
                selected_accounts.append((account_code.strip(), account_desc.strip()))
        else:
            # Todas las cuentas
            selected_accounts = self.account_types
        
        return {
            'selection_mode': self.selection_mode_var.get(),
            'selected_accounts': selected_accounts,
            'detail_level': self.detail_level_var.get(),
            'output_format': self.output_format_var.get(),
            'sort_by': self.sort_by_var.get(),
            'include_stats': self.include_stats_var.get(),
            'include_empty': self.include_empty_var.get(),
            'start_code': self.start_account_var.get().strip(),
            'end_code': self.end_account_var.get().strip(),
            'report_name': 'accounts_report',
            'timestamp': datetime.now()
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Cuentas de ejemplo adicionales
    accounts = [
        ("83609800", "Gastos financieros/Compra Tarj"),
        ("14701002", "Pago Anticipado Tarjeta"),
        ("10110804", "Efectivo en caja /Tarjetas"),
        ("16201002", "Anticipo para Tarjeta"),
        ("16101001", "Anticipo para Dieta"),
        ("10110200", "Efectivo en Caja /Fondo"),
        ("82244400", "Gasto de Alimentación"),
        ("82344500", "Gasto de Hospedaje"),
        ("82844400", "Gasto de Mantenimiento"),
        ("82944500", "Gasto de Transporte")
    ]
    
    dialog = AccountsReportDialog(root, account_types=accounts)
    result = dialog.show()
    
    if result:
        print("Configuración del reporte de Cuentas Contables:")
        print(f"  Modo: {result['selection_mode']}")
        print(f"  Cuentas seleccionadas: {len(result['selected_accounts'])}")
        print(f"  Nivel de detalle: {result['detail_level']}")
        print(f"  Formato: {result['output_format']}")
        print(f"  Ordenar por: {result['sort_by']}")
        print(f"  Incluir estadísticas: {result['include_stats']}")
        print(f"  Incluir cuentas vacías: {result['include_empty']}")
        if result['start_code']:
            print(f"  Rango: {result['start_code']} - {result['end_code']}")
    else:
        print("Diálogo cancelado")
    
    root.destroy()
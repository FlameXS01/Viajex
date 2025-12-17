import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List

# Importar diálogos de reportes
from presentation.gui.reports_presentation.dialogs.accounting_voucher_dialog import AccountingVoucherDialog
from presentation.gui.reports_presentation.dialogs.accounts_report_dialog import AccountsReportDialog
from presentation.gui.reports_presentation.dialogs.cards_in_advance_dialog import CardsInAdvanceDialog
from presentation.gui.reports_presentation.dialogs.cards_in_cash_dialog import CardsInCashDialog
from presentation.gui.reports_presentation.dialogs.cost_center_dialog import CostCenterDialog
from presentation.gui.reports_presentation.dialogs.daily_results_dialog import DailyResultsDialog
from presentation.gui.reports_presentation.dialogs.department_report_dialog import DepartmentReportDialog
from presentation.gui.reports_presentation.dialogs.employee_report_dialog import EmployeeReportDialog
from presentation.gui.reports_presentation.dialogs.unsettled_advances_dialog import UnsettledAdvancesDialog
from presentation.gui.reports_presentation.dialogs.export_options_dialog import ExportOptionsDialog
from presentation.gui.reports_presentation.dialogs.email_report_dialog import EmailReportDialog
from presentation.gui.reports_presentation.dialogs.report_preview_dialog import ReportPreviewDialog
from presentation.gui.reports_presentation.dialogs.date_range_dialog import DateRangeDialog
from presentation.gui.reports_presentation.dialogs.filter_manager_dialog import FilterManagerDialog
from application.services.request_service import UserRequestService 

# Importar servicios necesarios
from application.services.card_service import CardService
from application.services.diet_service import DietService
from application.services.department_service import DepartmentService
from application.services.user_service import UserService



class ReportModule(ttk.Frame):
    """Módulo principal para generación de reportes e informes del sistema"""
    
    def __init__(self, parent, 
                 card_service: CardService,
                 diet_service: DietService,
                 department_service: DepartmentService,
                 user_service: UserService,
                 request_service: UserRequestService):
        """
        Inicializa el módulo de reportes.
        
        Args:
            parent: Widget padre
            card_service: Servicio de gestión de tarjetas
            diet_service: Servicio de gestión de dietas
            department_service: Servicio de departamentos
            user_service: Servicio de usuarios
            request_service: Servicio de solicitudes
        """
        super().__init__(parent, style='Content.TFrame')
        
        # Servicios
        self.card_service = card_service
        self.diet_service = diet_service
        self.department_service = department_service
        self.user_service = user_service
        self.request_service = request_service
        
        # Estado del módulo
        self.current_report_type = None
        self.current_filters = {}
        self.current_data = []
        
        # Configuración inicial
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self._create_widgets()
        self._setup_report_definitions()
        
    def _create_widgets(self):
        """Crea los componentes de la interfaz del módulo"""
        # Header del módulo
        header_frame = ttk.Frame(self, style='Content.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Título
        ttk.Label(header_frame, text="Generación de Reportes", 
                 font=('Arial', 18, 'bold'), style='Content.TLabel').grid(row=0, column=0, sticky='w')
        
        # Botón de ayuda/guía
        help_btn = ttk.Button(header_frame, text="Guía de Uso", 
                             command=self._show_help)
        help_btn.grid(row=0, column=1, sticky='e', padx=(0, 10))
        
        # Contenedor principal (selección de reportes + configuración)
        main_container = ttk.Frame(self, style='Content.TFrame')
        main_container.grid(row=1, column=0, sticky='nsew', pady=10)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Configurar proporciones de columnas
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)
        
        # Panel izquierdo: Frame contenedor con scrollbar
        left_container = ttk.Frame(main_container, style='Content.TFrame')
        left_container.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        left_container.columnconfigure(0, weight=1)
        left_container.rowconfigure(0, weight=1)
        
        # Crear Canvas y Scrollbar para el panel izquierdo
        left_canvas = tk.Canvas(left_container, highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=left_canvas.yview)
        
        # Frame que irá dentro del Canvas
        left_panel = ttk.LabelFrame(left_canvas, text="Tipos de Reporte", padding="15")
        
        # Configurar el scrolling
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        # Crear ventana en el canvas para el frame
        left_canvas_frame = left_canvas.create_window((0, 0), window=left_panel, anchor="nw")
        
        # Empaquetar canvas y scrollbar
        left_canvas.grid(row=0, column=0, sticky="nsew")
        left_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configurar el frame dentro del canvas
        left_panel.columnconfigure(0, weight=1)
        
        # Panel derecho: Configuración y acciones (también con scrollbar)
        right_container = ttk.Frame(main_container, style='Content.TFrame')
        right_container.grid(row=0, column=1, sticky='nsew')
        right_container.columnconfigure(0, weight=1)
        right_container.rowconfigure(0, weight=1)
        
        # Crear Canvas y Scrollbar para el panel derecho
        right_canvas = tk.Canvas(right_container, highlightthickness=0)
        right_scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=right_canvas.yview)
        
        # Frame que irá dentro del Canvas
        right_panel = ttk.LabelFrame(right_canvas, text="Configuración", padding="15")
        
        # Configurar el scrolling
        right_canvas.configure(yscrollcommand=right_scrollbar.set)
        
        # Crear ventana en el canvas para el frame
        right_canvas_frame = right_canvas.create_window((0, 0), window=right_panel, anchor="nw")
        
        # Empaquetar canvas y scrollbar
        right_canvas.grid(row=0, column=0, sticky="nsew")
        right_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configurar el frame dentro del canvas
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Crear botones de tipos de reporte
        self._create_report_buttons(left_panel)
        
        # Crear panel de configuración
        self._create_config_panel(right_panel)
        
        # Configurar eventos para ajustar el scroll region
        def configure_left_scroll(event):
            # Actualizar el scroll region del canvas
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
            # Asegurar que la ventana del canvas ocupe todo el ancho
            left_canvas.itemconfig(left_canvas_frame, width=event.width)
            
        def configure_right_scroll(event):
            # Actualizar el scroll region del canvas
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))
            # Asegurar que la ventana del canvas ocupe todo el ancho
            right_canvas.itemconfig(right_canvas_frame, width=event.width)
        
        # Vincular eventos de redimensionamiento
        left_panel.bind("<Configure>", configure_left_scroll)
        left_canvas.bind("<Configure>", lambda e: left_canvas.itemconfig(left_canvas_frame, width=e.width))
        
        right_panel.bind("<Configure>", configure_right_scroll)
        right_canvas.bind("<Configure>", lambda e: right_canvas.itemconfig(right_canvas_frame, width=e.width))
        
        # Habilitar scroll con rueda del mouse
        def bind_mouse_wheel(widget):
            widget.bind("<MouseWheel>", lambda e: widget.yview_scroll(int(-1*(e.delta/120)), "units"))
            widget.bind("<Button-4>", lambda e: widget.yview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e: widget.yview_scroll(1, "units"))
        
        bind_mouse_wheel(left_canvas)
        bind_mouse_wheel(right_canvas)
        
        # Panel inferior: Resultados/Exportación
        bottom_panel = ttk.Frame(self, style='Content.TFrame')
        bottom_panel.grid(row=2, column=0, sticky='ew', pady=(20, 0))
        bottom_panel.columnconfigure(1, weight=1)
        
        # Botones de acciones generales
        self._create_action_buttons(bottom_panel)
        
    def _create_report_buttons(self, parent):
        """Crea los botones para seleccionar tipos de reporte"""
        
        # Definición de categorías de reportes
        report_categories = {
            "Financieros": [
                ("Vales Contables", "accounting_voucher", self._open_accounting_voucher),
                ("Reporte de Cuentas", "accounts", self._open_accounts_report),
                ("Resultados Diarios", "daily_results", self._open_daily_results),
                ("Centro de Costos", "cost_center", self._open_cost_center),
            ],
            "Tarjetas y Dietas": [
                ("Tarjetas en Adelanto", "cards_advance", self._open_cards_advance),
                ("Tarjetas en Efectivo", "cards_cash", self._open_cards_cash),
                ("Adelantos no Liquidadas", "unsettled", self._open_unsettled_advances),
                ("Dietas Pendientes", "pending_diets", self._open_pending_diets),
            ],
            "Recursos Humanos": [
                ("Reporte por Departamento", "department", self._open_department_report),
                ("Reporte por Empleado", "employee", self._open_employee_report),
                ("Solicitudes Usuarios", "user_requests", self._open_user_requests),
            ],
            "Exportación": [
                ("Opciones de Exportación", "export", self._open_export_options),
                ("Enviar por Email", "email", self._open_email_report),
            ]
        }
        
        row = 0
        for category_name, reports in report_categories.items():
            # Encabezado de categoría
            ttk.Label(parent, text=category_name, 
                     font=('Arial', 11, 'bold'), 
                     style='Content.TLabel').grid(row=row, column=0, sticky='w', pady=(10, 5))
            row += 1
            
            # Botones de reportes
            for report_name, report_id, command in reports:
                btn = ttk.Button(parent, text=report_name, 
                                command=command,
                                style='Report.TButton' if report_id == self.current_report_type else 'TButton')
                btn.grid(row=row, column=0, sticky='ew', pady=2)
                row += 1
            
            # Separador entre categorías
            if category_name != list(report_categories.keys())[-1]:
                ttk.Separator(parent, orient='horizontal').grid(row=row, column=0, sticky='ew', pady=10)
                row += 1
    
    def _create_config_panel(self, parent):
        """Crea el panel de configuración de reportes"""
        
        # Frame para filtros básicos
        filter_frame = ttk.LabelFrame(parent, text="Filtros Básicos", padding="10")
        filter_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        
        # Rango de fechas
        ttk.Label(filter_frame, text="Rango de Fechas:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        self.date_range_btn = ttk.Button(filter_frame, text="Seleccionar Fechas",
                                        command=self._open_date_range)
        self.date_range_btn.grid(row=0, column=1, sticky='w')
        
        self.date_range_label = ttk.Label(filter_frame, text="No seleccionado", 
                                         font=('Arial', 9))
        self.date_range_label.grid(row=0, column=2, sticky='w', padx=10)
        
        # Filtros avanzados
        ttk.Label(filter_frame, text="Filtros Avanzados:").grid(row=1, column=0, sticky='w', 
                                                               padx=(0, 10), pady=(10, 0))
        
        self.advanced_filters_btn = ttk.Button(filter_frame, text="Gestionar Filtros",
                                              command=self._open_filter_manager)
        self.advanced_filters_btn.grid(row=1, column=1, sticky='w', pady=(10, 0))
        
        # Frame para configuración específica del reporte
        self.specific_config_frame = ttk.LabelFrame(parent, text="Configuración Específica", 
                                                   padding="10")
        self.specific_config_frame.grid(row=1, column=0, sticky='nsew', pady=10)
        self.specific_config_frame.columnconfigure(0, weight=1)
        
        # Label placeholder para configuración específica
        self.specific_config_label = ttk.Label(self.specific_config_frame, 
                                              text="Seleccione un tipo de reporte para configurar",
                                              font=('Arial', 10, 'italic'))
        self.specific_config_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        # Agregar más contenido para demostrar el scroll
        ttk.Label(self.specific_config_frame, 
                 text="\nConfiguraciones adicionales disponibles según el reporte seleccionado:\n",
                 font=('Arial', 9)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        for i in range(2, 10):
            ttk.Label(self.specific_config_frame, 
                     text=f"Opción de configuración {i-1}: Valor por defecto",
                     font=('Arial', 8)).grid(row=i, column=0, sticky='w', padx=15, pady=2)
        
        # Configurar expansión del panel
        parent.rowconfigure(1, weight=1)
        
    def _create_action_buttons(self, parent):
        """Crea los botones de acciones en la parte inferior"""
        
        # Botón de previsualización
        preview_btn = ttk.Button(parent, text="Previsualizar Reporte", 
                                command=self._preview_report,
                                state='disabled')
        preview_btn.grid(row=0, column=0, padx=(0, 10))
        self.preview_btn = preview_btn
        
        # Botón de generación
        generate_btn = ttk.Button(parent, text="Generar Reporte", 
                                 command=self._generate_report,
                                 state='disabled')
        generate_btn.grid(row=0, column=1)
        self.generate_btn = generate_btn
        
        # Botón de exportación
        export_btn = ttk.Button(parent, text="Exportar Reporte", 
                               command=self._export_report,
                               state='disabled')
        export_btn.grid(row=0, column=2, padx=10)
        self.export_btn = export_btn
        
        # Botón de limpiar
        clear_btn = ttk.Button(parent, text="Limpiar Configuración", 
                              command=self._clear_configuration)
        clear_btn.grid(row=0, column=3)
        
    def _setup_report_definitions(self):
        """Configura las definiciones de reportes disponibles"""
        self.report_definitions = {
            'accounting_voucher': {
                'name': 'Vales Contables',
                'description': 'Genera vales contables para gastos y dietas',
                'required_filters': ['date_range'],
                'service_method': None,  # Se implementará según necesidad
            },
            'accounts': {
                'name': 'Reporte de Cuentas',
                'description': 'Reporte detallado de cuentas por departamento',
                'required_filters': ['date_range', 'department'],
                'service_method': None #self.department_service.generate_accounts_report,
            },
            # ... añadir más definiciones según sea necesario
        }
    
    # =========================================================================
    # MÉTODOS PARA ABRIR DIÁLOGOS ESPECÍFICOS
    # =========================================================================
    
    def _open_accounting_voucher(self):
        """Abre el diálogo de vales contables"""
        self._select_report_type('accounting_voucher')
        dialog = AccountingVoucherDialog(self.winfo_toplevel(), 
                                        self.diet_service,
                                        self.department_service)
        dialog.show()
    
    def _open_accounts_report(self):
        """Abre el diálogo de reporte de cuentas"""
        self._select_report_type('accounts')
        dialog = AccountsReportDialog(self.winfo_toplevel(),
                                     self.department_service)
        dialog.show()
    
    def _open_cards_advance(self):
        """Abre el diálogo de tarjetas en adelanto"""
        self._select_report_type('cards_advance')
        dialog = CardsInAdvanceDialog(self.winfo_toplevel(),
                                     self.card_service)
        dialog.show()
    
    def _open_cards_cash(self):
        """Abre el diálogo de tarjetas en efectivo"""
        self._select_report_type('cards_cash')
        dialog = CardsInCashDialog(self.winfo_toplevel(),
                                  self.card_service)
        dialog.show()
    
    def _open_cost_center(self):
        """Abre el diálogo de centro de costos"""
        self._select_report_type('cost_center')
        dialog = CostCenterDialog(self.winfo_toplevel(),
                                 self.department_service)
        dialog.show()
    
    def _open_daily_results(self):
        """Abre el diálogo de resultados diarios"""
        self._select_report_type('daily_results')
        dialog = DailyResultsDialog(self.winfo_toplevel(),
                                   self.diet_service,
                                   self.card_service)
        dialog.show()
    
    def _open_department_report(self):
        """Abre el diálogo de reporte por departamento"""
        self._select_report_type('department')
        dialog = DepartmentReportDialog(self.winfo_toplevel(),
                                       self.department_service,
                                       self.user_service)
        dialog.show()
    
    def _open_employee_report(self):
        """Abre el diálogo de reporte por empleado"""
        self._select_report_type('employee')
        dialog = EmployeeReportDialog(self.winfo_toplevel(),
                                     self.user_service,
                                     self.diet_service)
        dialog.show()
    
    def _open_unsettled_advances(self):
        """Abre el diálogo de adelantos no liquidadas"""
        self._select_report_type('unsettled')
        dialog = UnsettledAdvancesDialog(self.winfo_toplevel(),
                                        self.diet_service)
        dialog.show()
    
    def _open_pending_diets(self):
        """Abre el diálogo de dietas pendientes (método placeholder)"""
        self._select_report_type('pending_diets')
        # Por implementar
        messagebox.showinfo("Información", "Reporte de Dietas Pendientes - En desarrollo")
    
    def _open_user_requests(self):
        """Abre el diálogo de solicitudes de usuarios (método placeholder)"""
        self._select_report_type('user_requests')
        # Por implementar
        messagebox.showinfo("Información", "Reporte de Solicitudes - En desarrollo")
    
    def _open_export_options(self):
        """Abre el diálogo de opciones de exportación"""
        self._select_report_type('export')
        dialog = ExportOptionsDialog(self.winfo_toplevel())
        result = dialog.show()
        if result:
            self._handle_export_options(result)
    
    def _open_email_report(self):
        """Abre el diálogo para enviar reporte por email"""
        self._select_report_type('email')
        if not self.current_data:
            messagebox.showwarning("Advertencia", 
                                 "Genere un reporte primero para poder enviarlo por email")
            return
        
        dialog = EmailReportDialog(self.winfo_toplevel(),
                                  self.current_data,
                                  self.current_report_type)
        dialog.show()
    
    def _open_date_range(self):
        """Abre el diálogo para seleccionar rango de fechas"""
        dialog = DateRangeDialog(self.winfo_toplevel())
        date_range = dialog.show()
        
        if date_range:
            start_date, end_date = date_range
            self.current_filters['date_range'] = {
                'start': start_date,
                'end': end_date
            }
            self.date_range_label.config(
                text=f"{start_date} a {end_date}"
            )
            self._update_button_states()
    
    def _open_filter_manager(self):
        """Abre el diálogo para gestionar filtros avanzados"""
        dialog = FilterManagerDialog(self.winfo_toplevel(),
                                    self.current_filters,
                                    self.current_report_type)
        updated_filters = dialog.show()
        
        if updated_filters is not None:
            self.current_filters.update(updated_filters)
            self._update_button_states()
    
    def _preview_report(self):
        """Muestra una previsualización del reporte"""
        if not self._validate_report_configuration():
            return
        
        # Generar datos para previsualización
        preview_data = self._generate_report_data(preview=True)
        
        if preview_data:
            dialog = ReportPreviewDialog(self.winfo_toplevel(),
                                        preview_data,
                                        self.current_report_type)
            dialog.show()
    
    def _generate_report(self):
        """Genera el reporte completo"""
        if not self._validate_report_configuration():
            return
        
        try:
            self.current_data = self._generate_report_data(preview=False)
            
            if self.current_data:
                messagebox.showinfo("Éxito", 
                                  f"Reporte generado exitosamente.\n"
                                  f"Registros procesados: {len(self.current_data)}")
                
                # Habilitar botones de exportación y email
                self.export_btn.config(state='normal')
                self._update_button_states()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _export_report(self):
        """Exporta el reporte generado"""
        if not self.current_data:
            messagebox.showwarning("Advertencia", 
                                 "No hay datos para exportar. Genere un reporte primero.")
            return
        
        dialog = ExportOptionsDialog(self.winfo_toplevel())
        options = dialog.show()
        
        if options:
            try:
                # Aquí se implementaría la lógica de exportación
                # según las opciones seleccionadas (PDF, Excel, CSV, etc.)
                messagebox.showinfo("Exportación", 
                                  f"Reporte exportado con éxito.\n"
                                  f"Formato: {options['format']}\n"
                                  f"Ubicación: {options.get('path', 'N/A')}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    # =========================================================================
    # MÉTODOS AUXILIARES
    # =========================================================================
    
    def _select_report_type(self, report_type):
        """Selecciona un tipo de reporte y actualiza la UI"""
        self.current_report_type = report_type
        self._update_specific_configuration()
        self._update_button_states()
    
    def _update_specific_configuration(self):
        """Actualiza el panel de configuración específica según el tipo de reporte"""
        if not self.current_report_type:
            self.specific_config_label.config(
                text="Seleccione un tipo de reporte para configurar"
            )
            return
        
        definition = self.report_definitions.get(self.current_report_type, {})
        
        # Actualizar etiqueta con información del reporte
        config_text = f"Reporte: {definition.get('name', self.current_report_type)}\n"
        config_text += f"Descripción: {definition.get('description', 'Sin descripción')}\n\n"
        config_text += f"Filtros requeridos: {', '.join(definition.get('required_filters', []))}"
        
        self.specific_config_label.config(text=config_text)
    
    def _update_button_states(self):
        """Actualiza el estado de los botones según la configuración actual"""
        has_report_type = bool(self.current_report_type)
        has_required_filters = self._check_required_filters()
        
        # Habilitar/deshabilitar botones según las condiciones
        if has_report_type and has_required_filters:
            self.preview_btn.config(state='normal')
            self.generate_btn.config(state='normal')
        else:
            self.preview_btn.config(state='disabled')
            self.generate_btn.config(state='disabled')
        
        # Solo habilitar exportación si hay datos
        if has_report_type and self.current_data:
            self.export_btn.config(state='normal')
        else:
            self.export_btn.config(state='disabled')
    
    def _check_required_filters(self):
        """Verifica que se hayan configurados los filtros requeridos"""
        if not self.current_report_type:
            return False
        
        definition = self.report_definitions.get(self.current_report_type, {})
        required_filters = definition.get('required_filters', [])
        
        for filter_name in required_filters:
            if filter_name not in self.current_filters:
                return False
        
        return True
    
    def _validate_report_configuration(self):
        """Valida que la configuración del reporte sea correcta"""
        if not self.current_report_type:
            messagebox.showwarning("Advertencia", "Seleccione un tipo de reporte")
            return False
        
        if not self._check_required_filters():
            missing = self._get_missing_filters()
            messagebox.showwarning("Advertencia", 
                                 f"Faltan filtros requeridos: {', '.join(missing)}")
            return False
        
        return True
    
    def _get_missing_filters(self):
        """Obtiene la lista de filtros requeridos que faltan"""
        if not self.current_report_type:
            return []
        
        definition = self.report_definitions.get(self.current_report_type, {})
        required_filters = definition.get('required_filters', [])
        
        missing = []
        for filter_name in required_filters:
            if filter_name not in self.current_filters:
                missing.append(filter_name)
        
        return missing
    
    def _generate_report_data(self, preview=False):
        """
        Genera los datos del reporte.
        
        Args:
            preview: Si es True, genera datos limitados para previsualización
        
        Returns:
            Lista de datos del reporte
        """
        # Este método debe ser implementado según el tipo de reporte
        # Por ahora, retorna datos de ejemplo
        if preview:
            return [{"ejemplo": "datos de previsualización"}]
        else:
            return [{"campo1": "valor1", "campo2": "valor2"}]
    
    def _handle_export_options(self, options):
        """Maneja las opciones de exportación seleccionadas"""
        # Implementar lógica según las opciones
        print(f"Opciones de exportación: {options}")
    
    def _clear_configuration(self):
        """Limpia toda la configuración del reporte"""
        self.current_report_type = None
        self.current_filters = {}
        self.current_data = []
        
        # Resetear UI
        self.date_range_label.config(text="No seleccionado")
        self._update_specific_configuration()
        self._update_button_states()
        
        messagebox.showinfo("Información", "Configuración limpiada exitosamente")
    
    def _show_help(self):
        """Muestra la guía de uso del módulo de reportes"""
        help_text = """
        GUÍA DE USO - MÓDULO DE REPORTES
        
        1. SELECCIÓN DE REPORTE:
           - Elija un tipo de reporte de la lista izquierda
           - Use la barra de desplazamiento si hay muchos reportes
        
        2. CONFIGURACIÓN DE FILTROS:
           - Configure el rango de fechas requerido
           - Use 'Gestionar Filtros' para opciones avanzadas
           - Desplácese hacia abajo para ver todas las opciones
        
        3. GENERACIÓN:
           - Use 'Previsualizar' para ver una vista previa
           - Use 'Generar Reporte' para crear el reporte completo
        
        4. EXPORTACIÓN:
           - Una vez generado, puede exportar el reporte
           - Opciones: PDF, Excel, CSV, o enviar por email
        
        TIP: Cada tipo de reporte tiene requisitos específicos
             que se mostrarán en el panel de configuración.
        """
        
        messagebox.showinfo("Guía de Uso - Reportes", help_text)


# Estilo personalizado para botones de reportes
def configure_report_styles():
    """Configura estilos personalizados para el módulo de reportes"""
    style = ttk.Style()
    
    # Estilo para botones de reporte seleccionado
    style.configure('Report.TButton', 
                   font=('Arial', 10, 'bold'),
                   foreground='blue',
                   padding=5)


# Si se ejecuta directamente (para pruebas)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Módulo de Reportes - Prueba")
    root.geometry("900x700")
    
    # Configurar estilos
    configure_report_styles()
    
    # Crear servicios mock para pruebas
    class MockService:
        def __init__(self, name):
            self.name = name
        
        def dummy_method(self, *args, **kwargs):
            return [{"test": "data"}]
    
    # Instanciar módulo con servicios mock
    module = ReportModule(root,
                          MockService("Card"),
                          MockService("Diet"),
                          MockService("Department"),
                          MockService("User"),
                          MockService("Request"))
    module.pack(fill='both', expand=True, padx=20, pady=20)
    
    root.mainloop()
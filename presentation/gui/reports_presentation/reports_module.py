import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

from application.services.card_service import CardService
from application.services.diet_service import DietAppService
from application.services.request_service import UserRequestService
from application.services.department_service import DepartmentService

class ReportModule(ttk.Frame):
    """Módulo de generación de reportes para el sistema de dietas"""
    
    def __init__(self, parent, card_service: CardService, diet_service: DietAppService, 
                 request_service: UserRequestService, department_service: DepartmentService):
        super().__init__(parent, style='Content.TFrame')
        self.card_service = card_service
        self.diet_service = diet_service
        self.request_service = request_service
        self.department_service = department_service
        
        self.report_types = [
            "Reporte General de Tarjetas",
            "Reporte de Tarjetas Activas",
            "Reporte de Tarjetas Inactivas",
            "Reporte de Movimientos por Tarjeta",
            "Reporte de Saldos",
            "Reporte de Solicitantes por Departamento",
            "Reporte General de Solicitantes",
            "Reporte de Departamentos",
            "Reporte de Estadísticas del Sistema"
        ]
        
        self.formats = ["PDF", "Excel (XLSX)"]
        
        self._create_widgets()

    def _create_widgets(self):
        """Crea la interfaz del módulo de reportes"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header del módulo
        header_frame = ttk.Frame(self, style='Content.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Título
        ttk.Label(header_frame, text="Generador de Reportes", 
                  font=('Arial', 18, 'bold'), style='Content.TLabel').grid(row=0, column=0, sticky='w')
        
        # Contenedor principal
        main_frame = ttk.Frame(self, style='Content.TFrame')
        main_frame.grid(row=1, column=0, sticky='nsew')
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Selección de tipo de reporte
        ttk.Label(main_frame, text="Tipo de Reporte:", 
                  font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.report_combo = ttk.Combobox(main_frame, values=self.report_types, 
                                         state='readonly', font=('Arial', 10))
        self.report_combo.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        self.report_combo.set(self.report_types[0])
        self.report_combo.bind('<<ComboboxSelected>>', self._on_report_type_change)
        
        # Frame para parámetros específicos
        self.params_frame = ttk.LabelFrame(main_frame, text="Parámetros del Reporte", padding="15")
        self.params_frame.grid(row=2, column=0, sticky='ew', pady=(0, 20))
        self.params_frame.columnconfigure(0, weight=1)
        
        # Inicializar parámetros para el primer reporte
        self._create_card_report_params()
        
        # Selección de formato
        format_frame = ttk.Frame(main_frame, style='Content.TFrame')
        format_frame.grid(row=3, column=0, sticky='ew', pady=(0, 20))
        format_frame.columnconfigure(1, weight=1)
        
        ttk.Label(format_frame, text="Formato de Salida:", 
                  font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        self.format_combo = ttk.Combobox(format_frame, values=self.formats, 
                                         state='readonly', font=('Arial', 10), width=15)
        self.format_combo.grid(row=0, column=1, sticky='w')
        self.format_combo.set(self.formats[0])
        
        # Botones de acción
        buttons_frame = ttk.Frame(main_frame, style='Content.TFrame')
        buttons_frame.grid(row=4, column=0, sticky='se')
        buttons_frame.columnconfigure(0, weight=1)
        
        self.generate_btn = ttk.Button(buttons_frame, text="Generar Reporte", 
                                       command=self._generate_report, style='Accent.TButton')
        self.generate_btn.grid(row=0, column=0, sticky='e', padx=(0, 10))
        
        self.preview_btn = ttk.Button(buttons_frame, text="Vista Previa", 
                                      command=self._preview_report, state=tk.DISABLED)
        self.preview_btn.grid(row=0, column=1, sticky='e')

    def _on_report_type_change(self, event):
        """Cambia los parámetros según el tipo de reporte seleccionado"""
        # Limpiar frame de parámetros
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        report_type = self.report_combo.get()
        
        if "Tarjeta" in report_type:
            self._create_card_report_params()
        elif "Solicitante" in report_type:
            self._create_request_user_report_params()
        elif "Departamento" in report_type:
            self._create_department_report_params()
        elif "Estadísticas" in report_type:
            self._create_statistics_params()
            
        # Actualizar estado del botón de vista previa
        self.preview_btn['state'] = tk.DISABLED if "Excel" in self.format_combo.get() else tk.NORMAL

    def _create_card_report_params(self):
        """Crea parámetros para reportes de tarjetas"""
        # Filtro por estado
        status_frame = ttk.Frame(self.params_frame)
        status_frame.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        ttk.Label(status_frame, text="Estado:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.status_var = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(status_frame, textvariable=self.status_var, 
                                    values=["Todos", "Activas", "Inactivas"], 
                                    state='readonly', width=15)
        status_combo.grid(row=0, column=1, sticky='w')
        
        # Filtro por saldo mínimo
        balance_frame = ttk.Frame(self.params_frame)
        balance_frame.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        ttk.Label(balance_frame, text="Saldo Mínimo:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.min_balance_var = tk.DoubleVar(value=0.0)
        min_balance_spin = ttk.Spinbox(balance_frame, from_=0, to=100000, 
                                       textvariable=self.min_balance_var, width=15)
        min_balance_spin.grid(row=0, column=1, sticky='w')
        
        # Ordenar por
        sort_frame = ttk.Frame(self.params_frame)
        sort_frame.grid(row=2, column=0, sticky='w')
        
        ttk.Label(sort_frame, text="Ordenar por:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.sort_var = tk.StringVar(value="Número")
        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, 
                                  values=["Número", "Saldo", "Fecha de Creación"], 
                                  state='readonly', width=15)
        sort_combo.grid(row=0, column=1, sticky='w')

    def _create_request_user_report_params(self):
        """Crea parámetros para reportes de solicitantes"""
        # Filtro por departamento
        dept_frame = ttk.Frame(self.params_frame)
        dept_frame.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        ttk.Label(dept_frame, text="Departamento:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.dept_filter_var = tk.StringVar(value="Todos")
        
        # Obtener departamentos para el combobox
        try:
            departments = self.department_service.get_all_departments()
            dept_names = ["Todos"] + [dept.name for dept in departments]
        except:
            dept_names = ["Todos"]
            
        dept_combo = ttk.Combobox(dept_frame, textvariable=self.dept_filter_var, 
                                  values=dept_names, state='readonly', width=20)
        dept_combo.grid(row=0, column=1, sticky='w')

    def _create_department_report_params(self):
        """Crea parámetros para reportes de departamentos"""
        # Opción de incluir conteo de solicitantes
        include_frame = ttk.Frame(self.params_frame)
        include_frame.grid(row=0, column=0, sticky='w')
        
        self.include_count_var = tk.BooleanVar(value=True)
        include_check = ttk.Checkbutton(include_frame, text="Incluir conteo de solicitantes", 
                                        variable=self.include_count_var)
        include_check.grid(row=0, column=0, sticky='w')

    def _create_statistics_params(self):
        """Crea parámetros para reporte de estadísticas"""
        info_label = ttk.Label(self.params_frame, 
                               text="Este reporte genera estadísticas generales del sistema.")
        info_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

    def _generate_report(self):
        """Genera el reporte según los parámetros seleccionados"""
        report_type = self.report_combo.get()
        output_format = self.format_combo.get()
        
        if not report_type:
            messagebox.showwarning("Advertencia", "Seleccione un tipo de reporte")
            return
        
        try:
            # Generar datos según el tipo de reporte
            if "Tarjeta" in report_type:
                data = self._get_card_data(report_type)
                default_name = f"reporte_tarjetas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            elif "Solicitante" in report_type:
                data = self._get_request_user_data(report_type)
                default_name = f"reporte_solicitantes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            elif "Departamento" in report_type:
                data = self._get_department_data(report_type)
                default_name = f"reporte_departamentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            elif "Estadísticas" in report_type:
                data = self._get_statistics_data()
                default_name = f"reporte_estadisticas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            else:
                messagebox.showerror("Error", "Tipo de reporte no implementado")
                return
            
            # Generar en el formato seleccionado
            if "Excel" in output_format:
                self._generate_excel(data, report_type, default_name)
            else:
                self._generate_pdf(data, report_type, default_name)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {str(e)}")
            import traceback
            traceback.print_exc()

    def _get_card_data(self, report_type: str) -> List[Dict[str, Any]]:
        """Obtiene datos para reportes de tarjetas"""
        cards = self.card_service.get_all_cards()
        data = []
        
        for card in cards:
            # Aplicar filtros
            if "Activas" in report_type and not card.is_active:
                continue
            if "Inactivas" in report_type and card.is_active:
                continue
            
            if hasattr(card, 'balance') and card.balance < self.min_balance_var.get():
                continue
            
            card_data = {
                'Número': card.card_number,
                'Saldo': f"${getattr(card, 'balance', 0):.2f}",
                'Estado': 'Activa' if card.is_active else 'Inactiva',
                'PIN': getattr(card, 'card_pin', 'N/A'),
                'Creada': getattr(card, 'created_at', 'N/A'),
                'Última Actualización': getattr(card, 'updated_at', 'N/A')
            }
            data.append(card_data)
        
        # Ordenar datos
        sort_key = self.sort_var.get()
        if sort_key == "Número":
            data.sort(key=lambda x: x['Número'])
        elif sort_key == "Saldo":
            data.sort(key=lambda x: float(x['Saldo'].replace('$', '').replace(',', '')), reverse=True)
        
        return data

    def _get_request_user_data(self, report_type: str) -> List[Dict[str, Any]]:
        """Obtiene datos para reportes de solicitantes"""
        request_users = self.request_service.get_all_request_users()
        data = []
        
        for user in request_users:
            # Aplicar filtro por departamento
            dept_filter = self.dept_filter_var.get()
            if dept_filter != "Todos" and hasattr(user, 'department'):
                if user.department.name != dept_filter:
                    continue
            
            user_data = {
                'Nombre': user.fullname,
                'CI': user.ci,
                'Departamento': user.department.name if hasattr(user, 'department') else 'N/A',
                'Email': getattr(user, 'email', 'N/A'),
                'Teléfono': getattr(user, 'phone', 'N/A'),
                'Fecha Registro': getattr(user, 'created_at', 'N/A')
            }
            data.append(user_data)
        
        return data

    def _get_department_data(self, report_type: str) -> List[Dict[str, Any]]:
        """Obtiene datos para reportes de departamentos"""
        departments = self.department_service.get_all_departments()
        data = []
        
        for dept in departments:
            dept_data = {
                'Nombre': dept.name,
                'ID': dept.id,
                'Fecha Creación': getattr(dept, 'created_at', 'N/A')
            }
            
            if self.include_count_var.get():
                # Contar solicitantes en este departamento
                count = 0
                try:
                    request_users = self.request_service.get_all_request_users()
                    count = sum(1 for user in request_users 
                              if hasattr(user, 'department') and user.department.id == dept.id)
                except:
                    pass
                dept_data['Solicitantes'] = count
            
            data.append(dept_data)
        
        return data

    def _get_statistics_data(self) -> Dict[str, Any]:
        """Obtiene datos estadísticos del sistema"""
        stats = {}
        
        try:
            # Estadísticas de tarjetas
            cards = self.card_service.get_all_cards()
            stats['total_tarjetas'] = len(cards)
            stats['tarjetas_activas'] = sum(1 for c in cards if c.is_active)
            stats['tarjetas_inactivas'] = sum(1 for c in cards if not c.is_active)
            stats['saldo_total'] = sum(getattr(c, 'balance', 0) for c in cards)
            
            # Estadísticas de solicitantes
            request_users = self.request_service.get_all_request_users()
            stats['total_solicitantes'] = len(request_users)
            
            # Estadísticas de departamentos
            departments = self.department_service.get_all_departments()
            stats['total_departamentos'] = len(departments)
            
            # Fecha de generación
            stats['fecha_generacion'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats

    def _generate_pdf(self, data: Any, report_type: str, default_name: str):
        """Genera un reporte en formato PDF"""
        # Solicitar ubicación para guardar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"{default_name}.pdf",
            title="Guardar Reporte PDF"
        )
        
        if not file_path:
            return  # Usuario canceló
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4, 
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=72)
            
            elements = []
            styles = getSampleStyleSheet()
            
            # Estilo para título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Centrado
            )
            
            # Título del reporte
            elements.append(Paragraph(report_type, title_style))
            
            # Información de generación
            date_str = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            elements.append(Paragraph(f"Generado: {date_str}", styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Contenido según tipo de datos
            if isinstance(data, list) and data:
                # Crear tabla para datos tabulares
                if data and isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    table_data = [headers]
                    
                    for row in data:
                        table_data.append([str(row.get(h, '')) for h in headers])
                    
                    # Crear tabla
                    table = Table(table_data, repeatRows=1)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('WORDWRAP', (0, 0), (-1, -1), True),
                    ]))
                    
                    elements.append(table)
            
            elif isinstance(data, dict):
                # Mostrar estadísticas como lista
                for key, value in data.items():
                    if key != 'error':
                        elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
                        elements.append(Spacer(1, 5))
            
            # Generar PDF
            doc.build(elements)
            messagebox.showinfo("Éxito", f"Reporte PDF generado exitosamente:\n{file_path}")
            
            # Abrir el archivo si es posible
            if messagebox.askyesno("Abrir Reporte", "¿Desea abrir el reporte generado?"):
                os.startfile(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {str(e)}")

    def _generate_excel(self, data: Any, report_type: str, default_name: str):
        """Genera un reporte en formato Excel"""
        # Solicitar ubicación para guardar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"{default_name}.xlsx",
            title="Guardar Reporte Excel"
        )
        
        if not file_path:
            return  # Usuario canceló
        
        try:
            if isinstance(data, list) and data:
                # Datos tabulares
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False, sheet_name=report_type[:31])
                
            elif isinstance(data, dict):
                # Datos de estadísticas
                df = pd.DataFrame([data])
                df.to_excel(file_path, index=False, sheet_name="Estadísticas")
            
            messagebox.showinfo("Éxito", f"Reporte Excel generado exitosamente:\n{file_path}")
            
            # Abrir el archivo si es posible
            if messagebox.askyesno("Abrir Reporte", "¿Desea abrir el reporte generado?"):
                os.startfile(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el Excel: {str(e)}")

    def _preview_report(self):
        """Muestra una vista previa del reporte (solo para PDF)"""
        report_type = self.report_combo.get()
        
        if "Excel" in self.format_combo.get():
            messagebox.showinfo("Información", "Vista previa no disponible para formato Excel")
            return
        
        # Aquí podríamos implementar una ventana de vista previa
        # Por ahora, simplemente generamos un PDF temporal y lo mostramos
        try:
            temp_file = "temp_preview.pdf"
            
            # Similar a _generate_pdf pero con archivo temporal
            # (implementación simplificada)
            messagebox.showinfo("Vista Previa", 
                              "La vista previa se abrirá en el visor de PDF predeterminado.\n"
                              "Nota: Esta es una funcionalidad básica de demostración.")
            
            # Generar y abrir PDF temporal
            # self._generate_pdf_temporary(temp_file)
            # os.startfile(temp_file)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la vista previa: {str(e)}")

    def refresh_data(self):
        """Actualiza los datos del módulo"""
        # Este método puede ser llamado desde el dashboard principal
        # para refrescar comboboxes o datos en caché
        pass
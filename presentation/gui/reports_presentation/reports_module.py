import os
import tempfile
import subprocess
import platform
from io import BytesIO
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

from application.services.card_service import CardService
from application.services.diet_service import DietAppService
from application.services.request_service import UserRequestService
from application.services.department_service import DepartmentService

# Importaciones opcionales para vista previa mejorada
try:
    import fitz  # PyMuPDF
    from PIL import Image, ImageTk
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


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
        self.current_preview_data = None  # Para almacenar datos de vista previa

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
        self.format_combo.bind('<<ComboboxSelected>>', self._on_format_change)
        
        # Botones de acción
        buttons_frame = ttk.Frame(main_frame, style='Content.TFrame')
        buttons_frame.grid(row=4, column=0, sticky='se')
        buttons_frame.columnconfigure(0, weight=1)
        
        self.generate_btn = ttk.Button(buttons_frame, text="Generar Reporte", 
                                       command=self._generate_report, style='Accent.TButton')
        self.generate_btn.grid(row=0, column=0, sticky='e', padx=(0, 10))
        
        self.preview_btn = ttk.Button(buttons_frame, text="Vista Previa", 
                                      command=self._preview_report, state=tk.NORMAL)
        self.preview_btn.grid(row=0, column=1, sticky='e')

    def _on_report_type_change(self, event=None):
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
        self._update_preview_button_state()

    def _on_format_change(self, event=None):
        """Actualiza el estado del botón de vista previa según el formato"""
        self._update_preview_button_state()

    def _update_preview_button_state(self):
        """Actualiza el estado del botón de vista previa"""
        output_format = self.format_combo.get()
        self.preview_btn['state'] = tk.DISABLED if "Excel" in output_format else tk.NORMAL

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

    # ============================================================================
    # VISTA PREVIA MEJORADA
    # ============================================================================

    def _preview_report(self):
        """Muestra una vista previa del reporte con opciones de visualización"""
        report_type = self.report_combo.get()
        
        if "Excel" in self.format_combo.get():
            messagebox.showinfo("Información", "Vista previa no disponible para formato Excel")
            return
        
        try:
            # Obtener datos para el reporte
            data = self._get_report_data_for_preview(report_type)
            
            if data is None or (hasattr(data, '__len__') and len(data) == 0):
                messagebox.showwarning("Sin datos", "No hay datos para generar la vista previa")
                return
            
            # Guardar datos para uso posterior
            self.current_preview_data = data
            
            # Generar PDF en memoria
            pdf_buffer = self._generate_pdf_buffer(data, report_type)
            
            if pdf_buffer is None or pdf_buffer.getbuffer().nbytes == 0:
                messagebox.showerror("Error", "No se pudo generar la vista previa del PDF")
                return
            
            # Mostrar opciones de vista previa
            self._show_preview_options(pdf_buffer, data, report_type)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la vista previa: {str(e)}")
            import traceback
            traceback.print_exc()

    def _get_report_data_for_preview(self, report_type):
        """Obtiene datos específicos para vista previa"""
        if "Tarjeta" in report_type:
            return self._get_card_data(report_type)
        elif "Solicitante" in report_type:
            return self._get_request_user_data(report_type)
        elif "Departamento" in report_type:
            return self._get_department_data(report_type)
        elif "Estadísticas" in report_type:
            return self._get_statistics_data()
        return None

    def _generate_pdf_buffer(self, data: Any, report_type: str):
        """Genera un PDF en memoria y retorna un buffer BytesIO"""
        try:
            buffer = BytesIO()
            
            # Configuración del documento
            doc = SimpleDocTemplate(buffer, pagesize=A4,
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
            
            # Título del reporte (con "Vista Previa")
            preview_title = f"{report_type} - Vista Previa"
            elements.append(Paragraph(preview_title, title_style))
            
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
                    
                    # Limitar a 20 filas para vista previa
                    max_rows = min(20, len(data))
                    for i in range(max_rows):
                        row = data[i]
                        table_data.append([str(row.get(h, '')) for h in headers])
                    
                    # Si hay más filas, agregar nota
                    if len(data) > max_rows:
                        table_data.append([f"... y {len(data) - max_rows} filas más"] * len(headers))
                    
                    # Crear tabla
                    table = Table(table_data, repeatRows=1)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ]))
                    
                    elements.append(table)
                    
                    # Nota sobre límite de filas
                    if len(data) > max_rows:
                        elements.append(Spacer(1, 10))
                        note = Paragraph(
                            f"<i>Nota: Vista previa limitada a {max_rows} filas. El reporte completo tendrá {len(data)} filas.</i>",
                            styles['Italic']
                        )
                        elements.append(note)
            
            elif isinstance(data, dict):
                # Mostrar estadísticas como lista
                for key, value in data.items():
                    if key != 'error':
                        elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
                        elements.append(Spacer(1, 5))
            
            # Agregar pie de página
            elements.append(Spacer(1, 20))
            footer = Paragraph("<i>Vista Previa Generada - Reporte del Sistema de Dietas</i>", styles['Italic'])
            elements.append(footer)
            
            # Construir PDF
            doc.build(elements)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"Error al generar PDF en memoria: {e}")
            return None

    def _show_preview_options(self, pdf_buffer, data, report_type):
        """Muestra ventana con opciones de vista previa"""
        preview_window = tk.Toplevel(self)
        preview_window.title("Opciones de Vista Previa")
        preview_window.geometry("400x400")
        preview_window.resizable(False, False)
        preview_window.transient(self)
        preview_window.grab_set()
        
        # Centrar ventana
        preview_window.update_idletasks()
        width = preview_window.winfo_width()
        height = preview_window.winfo_height()
        x = (preview_window.winfo_screenwidth() // 2) - (width // 2)
        y = (preview_window.winfo_screenheight() // 2) - (height // 2)
        preview_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = ttk.Frame(preview_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Vista Previa del Reporte", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Información del reporte
        info_text = f"Tipo: {report_type}\n"
        if isinstance(data, list):
            info_text += f"Registros: {len(data)}"
        elif isinstance(data, dict):
            info_text += f"Estadísticas: {len(data)} items"
        
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # Botones de opciones
        
        # Opción 1: Abrir con visor del sistema
        btn_viewer = ttk.Button(
            main_frame, 
            text="📄 Abrir en Visor de PDF", 
            command=lambda: self._open_with_system_viewer(pdf_buffer, preview_window),
            width=30
        )
        btn_viewer.pack(pady=10)
        
        # Opción 2: Mostrar en ventana interna (solo si PyMuPDF está disponible)
        if PYMUPDF_AVAILABLE:
            btn_window = ttk.Button(
                main_frame, 
                text="👁️ Mostrar en Ventana Interna", 
                command=lambda: self._show_pdf_in_window(pdf_buffer, report_type, preview_window),
                width=30
            )
            btn_window.pack(pady=10)
        else:
            # Mostrar mensaje de instalación
            install_label = ttk.Label(
                main_frame,
                text="Para vista en ventana instale:\npip install PyMuPDF pillow",
                foreground="gray",
                font=("Arial", 8)
            )
            install_label.pack(pady=5)
        
        # Opción 3: Guardar como archivo temporal
        btn_save = ttk.Button(
            main_frame, 
            text="💾 Guardar Archivo Temporal", 
            command=lambda: self._save_temp_pdf(pdf_buffer, preview_window),
            width=30
        )
        btn_save.pack(pady=10)
        
        # Opción 4: Ver resumen de datos
        btn_summary = ttk.Button(
            main_frame,
            text="📊 Ver Resumen de Datos",
            command=lambda: self._show_data_summary(data, report_type),
            width=30
        )
        btn_summary.pack(pady=10)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Botón Cancelar
        ttk.Button(main_frame, text="Cancelar", 
                  command=preview_window.destroy).pack(pady=2)

    def _open_with_system_viewer(self, pdf_buffer, parent_window=None):
        """Abre el PDF con el visor predeterminado del sistema"""
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, delete_on_close=False) as tmp:
                tmp.write(pdf_buffer.getvalue())
                temp_path = tmp.name
            
            # Abrir según sistema operativo
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(temp_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', temp_path])
            else:  # Linux
                subprocess.run(['xdg-open', temp_path])
            
            if parent_window:
                parent_window.destroy()
            
            messagebox.showinfo("Vista Previa", "Reporte abierto en el visor de PDF predeterminado.")
            return temp_path
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el visor de PDF: {str(e)}")
            return None

    def _save_temp_pdf(self, pdf_buffer, parent_window=None):
        """Guarda el PDF como archivo temporal"""
        try:
            # Crear directorio de temporales si no existe
            temp_dir = os.path.join(os.getcwd(), "temp_previews")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"vista_previa_{timestamp}.pdf"
            filepath = os.path.join(temp_dir, filename)
            
            # Guardar archivo
            with open(filepath, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            if parent_window:
                parent_window.destroy()
            
            messagebox.showinfo(
                "Archivo Guardado", 
                f"Vista previa guardada en:\n{filepath}\n\n"
                "Puede abrir este archivo manualmente con su visor de PDF."
            )
            return filepath
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")
            return None

    def _show_pdf_in_window(self, pdf_buffer, report_type, parent_window=None):
        """Muestra el PDF en una ventana interna usando PyMuPDF"""
        if not PYMUPDF_AVAILABLE:
            messagebox.showerror(
                "Error", 
                "PyMuPDF no está instalado.\n"
                "Instálelo con: pip install PyMuPDF pillow"
            )
            return
        
        try:
            if parent_window:
                parent_window.destroy()
            
            # Crear ventana de vista previa
            pdf_window = tk.Toplevel(self)
            pdf_window.title(f"{report_type} - Vista Previa")
            pdf_window.geometry("900x700")
            
            # Frame principal
            main_frame = ttk.Frame(pdf_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Canvas con scrollbar
            canvas = tk.Canvas(main_frame, bg='white')
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Convertir PDF a imágenes
            doc = fitz.open(stream=pdf_buffer.getvalue(), filetype="pdf")
            pdf_images = []  # Para mantener referencia a las imágenes
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                
                # Convertir a imagen PIL
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Redimensionar si es muy ancha
                max_width = 850
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                img_tk = ImageTk.PhotoImage(img)
                pdf_images.append(img_tk)  # Guardar referencia
                
                # Mostrar imagen
                label = tk.Label(scrollable_frame, image=img_tk, bg='white')
                label.image = img_tk
                label.pack(pady=10, padx=10)
                
                # Número de página
                page_label = tk.Label(
                    scrollable_frame, 
                    text=f"Página {page_num + 1} de {len(doc)}",
                    font=("Arial", 10), 
                    bg='white'
                )
                page_label.pack(pady=(0, 10))
            
            doc.close()
            
            # Guardar referencia a las imágenes para evitar garbage collection
            pdf_window.pdf_images = pdf_images
            
            # Frame de botones
            btn_frame = ttk.Frame(pdf_window)
            btn_frame.pack(pady=10)
            
            ttk.Button(btn_frame, text="Cerrar", 
                      command=pdf_window.destroy).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(btn_frame, text="Guardar como...", 
                      command=lambda: self._save_pdf_as(pdf_buffer)).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(btn_frame, text="Generar Reporte Completo", 
                      command=lambda: self._generate_from_preview(pdf_window)).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar el PDF: {str(e)}")

    def _show_data_summary(self, data, report_type):
        """Muestra un resumen de los datos"""
        summary_text = f"=== RESUMEN DEL REPORTE ===\n\n"
        summary_text += f"Tipo: {report_type}\n"
        summary_text += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if isinstance(data, list):
            summary_text += f"Total de registros: {len(data)}\n"
            if data and isinstance(data[0], dict):
                summary_text += f"Campos: {', '.join(data[0].keys())}\n\n"
                # Mostrar primeros 3 registros como ejemplo
                summary_text += "Primeros 3 registros:\n"
                for i in range(min(3, len(data))):
                    summary_text += f"{i+1}. {data[i]}\n"
        
        elif isinstance(data, dict):
            summary_text += "Estadísticas:\n"
            for key, value in data.items():
                if key != 'error':
                    summary_text += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        # Mostrar en messagebox
        messagebox.showinfo("Resumen de Datos", summary_text)

    def _save_pdf_as(self, pdf_buffer):
        """Guarda el PDF con diálogo de guardar"""
        report_type = self.report_combo.get()
        default_name = f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=default_name,
            title="Guardar Vista Previa como PDF"
        )
        
        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    f.write(pdf_buffer.getvalue())
                messagebox.showinfo("Éxito", f"PDF guardado en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def _generate_from_preview(self, preview_window):
        """Genera el reporte completo desde la vista previa"""
        if self.current_preview_data is not None:
            preview_window.destroy()
            self._generate_report()

    # ============================================================================
    # MÉTODOS ORIGINALES (sin cambios, excepto pequeñas adaptaciones)
    # ============================================================================

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

    def refresh_data(self):
        """Actualiza los datos del módulo"""
        # Este método puede ser llamado desde el dashboard principal
        # para refrescar comboboxes o datos en caché
        pass


# Método de prueba si se ejecuta el archivo directamente
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba de ReportModule")
    
    # Mock de servicios para pruebas
    class MockService:
        def get_all_cards(self):
            return []
        
        def get_all_request_users(self):
            return []
        
        def get_all_departments(self):
            return []
    
    # Crear instancia del módulo con servicios mock
    report_module = ReportModule(
        root,
        MockService(),
        MockService(),
        MockService(),
        MockService()
    )
    
    report_module.pack(fill=tk.BOTH, expand=True)
    root.geometry("800x600")
    root.mainloop()
# data_exporter.py
"""
Módulo para exportar datos de Treeview a diferentes formatos.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List, Any
import os
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

HAS_EXCEL = True
HAS_WORD = True
HAS_PDF = True

class TreeviewExporter:
    """Exportador genérico para Treeview de tkinter"""
    
    @staticmethod
    def get_treeview_data(tree: ttk.Treeview) -> tuple:
        """
        Extrae todos los datos del Treeview
        
        Returns:
            tuple: (encabezados, datos)
        """
        # Obtener encabezados
        columns = tree['columns']
        headers = []
        for col in columns:
            header = tree.heading(col)['text']
            headers.append(header)
        
        # Obtener datos
        data = []
        for item in tree.get_children():
            values = tree.item(item)['values']
            data.append(values)
        
        return headers, data
    
    @staticmethod
    def export_to_excel(tree: ttk.Treeview, title: str, filename: str = None) -> Optional[str]:
        """Exporta Treeview a Excel"""
        if not HAS_EXCEL:
            messagebox.showerror("Error", "openpyxl no está instalado. Instálelo con: pip install openpyxl")
            return None
        
        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar como Excel"
            )
            
        if not filename:
            return None
        
        try:
            headers, data = TreeviewExporter.get_treeview_data(tree)
            
            if not headers or not data:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return None
            
            # Crear workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte"
            
            # Escribir título
            ws.merge_cells(f'A1:{get_column_letter(len(headers))}1')
            title_cell = ws['A1']
            title_cell.value = title
            title_cell.font = Font(size=14, bold=True)
            title_cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Escribir encabezados
            for col_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=3, column=col_idx, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.font = Font(color="FFFFFF", bold=True)
                cell.alignment = Alignment(horizontal='center')
                
                # Ajustar ancho de columna
                col_letter = get_column_letter(col_idx)
                ws.column_dimensions[col_letter].width = max(len(str(header)) + 2, 12)
            
            # Escribir datos
            for row_idx, row_data in enumerate(data, start=4):
                for col_idx, cell_data in enumerate(row_data, start=1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=cell_data)
                    
                    # Formatear números/montos
                    if isinstance(cell_data, str) and cell_data.startswith('$'):
                        cell.alignment = Alignment(horizontal='right')
                    elif isinstance(cell_data, (int, float)):
                        cell.alignment = Alignment(horizontal='right')
                    
                    # Alternar colores de fila
                    if row_idx % 2 == 0:
                        cell.fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
            
            # Agregar bordes
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            for row in ws.iter_rows(min_row=3, max_row=len(data)+3, min_col=1, max_col=len(headers)):
                for cell in row:
                    cell.border = thin_border
            
            # Agregar metadatos
            ws['A' + str(len(data) + 5)] = f"Total de registros: {len(data)}"
            ws['A' + str(len(data) + 5)].font = Font(italic=True)
            ws['A' + str(len(data) + 6)] = f"Fecha de exportación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            ws['A' + str(len(data) + 6)].font = Font(italic=True, size=9)
            
            wb.save(filename)
            messagebox.showinfo("Éxito", f"Archivo exportado exitosamente:\n{filename}")
            return filename
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel:\n{str(e)}")
            return None
    
    @staticmethod
    def export_to_word(tree: ttk.Treeview, title: str, filename: str = None) -> Optional[str]:
        """Exporta Treeview a Word"""
        if not HAS_WORD:
            messagebox.showerror("Error", "python-docx no está instalado. Instálelo con: pip install python-docx")
            return None
        
        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word files", "*.docx"), ("All files", "*.*")],
                title="Guardar como Word"
            )
            
        if not filename:
            return None
        
        try:
            headers, data = TreeviewExporter.get_treeview_data(tree)
            
            if not headers or not data:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return None
            
            # Crear documento
            doc = Document()
            
            # Agregar título
            title_para = doc.add_paragraph()
            title_run = title_para.add_run(title)
            title_run.font.size = Pt(14)
            title_run.font.bold = True
            title_run.font.color.rgb = RGBColor(0, 51, 102)
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph()  # Espacio
            
            # Crear tabla
            table = doc.add_table(rows=1, cols=len(headers))
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            # Agregar encabezados
            header_cells = table.rows[0].cells
            for i, header in enumerate(headers):
                header_cells[i].text = str(header)
                header_cells[i].paragraphs[0].runs[0].font.bold = True
                header_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                header_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                
                
            
            # Agregar datos
            for row_idx, row_data in enumerate(data):
                row_cells = table.add_row().cells
                for i, cell_data in enumerate(row_data):
                    row_cells[i].text = str(cell_data)
                    
                    # Alinear números a la derecha
                    cell_str = str(cell_data)
                    if cell_str.startswith('$') or cell_str.replace('.', '', 1).isdigit():
                        row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    
                    # Color alternado para filas
                    if row_idx % 2 == 1:
                        shading = row_cells[i]._element.xpath('.//w:shd')
                        if shading:
                            shading[0].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill', 'F2F2F2')
            
            # Agregar información
            doc.add_paragraph()  # Espacio
            total_para = doc.add_paragraph(f"Total de registros: {len(data)}")
            total_para.runs[0].italic = True
            
            date_para = doc.add_paragraph(f"Fecha de exportación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            date_para.runs[0].font.size = Pt(9)
            date_para.runs[0].italic = True
            
            doc.save(filename)
            messagebox.showinfo("Éxito", f"Archivo exportado exitosamente:\n{filename}")
            return filename
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Word:\n{str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def export_to_pdf(tree: ttk.Treeview, title: str, filename: str = None) -> Optional[str]:
        """Exporta Treeview a PDF"""
        if not HAS_PDF:
            messagebox.showerror("Error", "reportlab no está instalado. Instálelo con: pip install reportlab")
            return None
        
        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Guardar como PDF"
            )
            
        if not filename:
            return None
        
        try:
            headers, data = TreeviewExporter.get_treeview_data(tree)
            
            if not headers or not data:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return None
            
            # Crear documento PDF
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                  topMargin=0.5*inch, bottomMargin=0.5*inch,
                                  leftMargin=0.5*inch, rightMargin=0.5*inch)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=14,
                spaceAfter=12,
                alignment=1,
                textColor=colors.HexColor('#2c3e50')
            )
            
            title_para = Paragraph(title, title_style)
            elements.append(title_para)
            elements.append(Spacer(1, 0.2*inch))
            
            # Preparar datos para la tabla
            table_data = [headers] + data
            
            # Crear tabla
            col_widths = [doc.width/len(headers)] * len(headers)
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Estilo de la tabla
            table.setStyle(TableStyle([
                # Encabezados
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Datos
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                
                # Alternar colores de fila
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
                
                # Alinear montos a la derecha
                ('ALIGN', (len(headers)-1, 1), (len(headers)-1, -1), 'RIGHT'),
            ]))
            
            elements.append(table)
            
            # Agregar información
            elements.append(Spacer(1, 0.3*inch))
            
            total_text = f"<b>Total de registros:</b> {len(data)}"
            total_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=10,
                spaceAfter=6
            )
            total_para = Paragraph(total_text, total_style)
            elements.append(total_para)
            
            date_text = f"<i>Fecha de exportación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>"
            date_style = ParagraphStyle(
                'CustomItalic',
                parent=styles['Italic'],
                fontSize=8,
                textColor=colors.gray
            )
            date_para = Paragraph(date_text, date_style)
            elements.append(date_para)
            
            doc.build(elements)
            messagebox.showinfo("Éxito", f"Archivo exportado exitosamente:\n{filename}")
            return filename
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a PDF:\n{str(e)}")
            return None
    
    @staticmethod
    def export_to_csv(tree: ttk.Treeview, title: str, filename: str = None) -> Optional[str]:
        """Exporta Treeview a CSV"""
        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar como CSV"
            )
            
        if not filename:
            return None
        
        try:
            import csv
            
            headers, data = TreeviewExporter.get_treeview_data(tree)
            
            if not headers or not data:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return None
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Escribir título como comentario
                csvfile.write(f"# {title}\n")
                csvfile.write(f"# Fecha de exportación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                csvfile.write(f"# Total de registros: {len(data)}\n")
                
                # Escribir encabezados
                writer.writerow(headers)
                
                # Escribir datos
                writer.writerows(data)
            
            messagebox.showinfo("Éxito", f"Archivo exportado exitosamente:\n{filename}")
            return filename
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a CSV:\n{str(e)}")
            return None
    
    @staticmethod
    def create_export_button(parent, tree: ttk.Treeview, title: str, 
                           button_text: str = "📤 Exportar", 
                           pack_options: dict = None) -> ttk.Button:
        """
        Crea un botón de exportación con menú desplegable
        
        Args:
            parent: Widget padre
            tree: Treeview a exportar
            title: Título del reporte
            button_text: Texto del botón
            pack_options: Opciones para pack() del botón
            
        Returns:
            ttk.Button: Botón creado
        """
        from tkinter import Menu
        
        def show_export_menu(event=None):
            """Muestra el menú de exportación"""
            menu = Menu(parent, tearoff=0)
            
            # Solo agregar opciones disponibles
            available_formats = []
            
            if HAS_EXCEL:
                menu.add_command(
                    label="Exportar a Excel (.xlsx)",
                    command=lambda: TreeviewExporter.export_to_excel(tree, title)
                )
                available_formats.append("Excel")
            
            if HAS_WORD:
                menu.add_command(
                    label="Exportar a Word (.docx)",
                    command=lambda: TreeviewExporter.export_to_word(tree, title)
                )
                available_formats.append("Word")
            
            if HAS_PDF:
                menu.add_command(
                    label="Exportar a PDF (.pdf)",
                    command=lambda: TreeviewExporter.export_to_pdf(tree, title)
                )
                available_formats.append("PDF")
            
            menu.add_command(
                label="Exportar a CSV (.csv)",
                command=lambda: TreeviewExporter.export_to_csv(tree, title)
            )
            available_formats.append("CSV")
            
            # Agregar separador y opción de ayuda
            menu.add_separator()
            
            if len(available_formats) < 4:
                menu.add_command(
                    label="Instalar dependencias faltantes",
                    command=TreeviewExporter.show_dependency_help
                )
            
            # Mostrar menú
            if event:
                try:
                    menu.tk_popup(event.x_root, event.y_root)
                finally:
                    menu.grab_release()
            else:
                # Si se llama sin evento, mostrar cerca del botón
                x = parent.winfo_rootx() + export_btn.winfo_x() + export_btn.winfo_width()
                y = parent.winfo_rooty() + export_btn.winfo_y() + export_btn.winfo_height()
                menu.tk_popup(x, y)
        
        # Crear botón
        export_btn = ttk.Button(
            parent,
            text=button_text,
            command=show_export_menu
        )
        
        # Configurar pack si se proporcionaron opciones
        if pack_options:
            export_btn.pack(**pack_options)
        else:
            export_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # También agregar menú contextual al Treeview
        tree.bind("<Button-3>", show_export_menu)
        
        return export_btn
    
    @staticmethod
    def show_dependency_help():
        """Muestra ayuda para instalar dependencias"""
        help_text = """
Para exportar en todos los formatos, instale las siguientes bibliotecas:

Excel: pip install openpyxl
Word:  pip install python-docx
PDF:   pip install reportlab

O instale todas con:
pip install openpyxl python-docx reportlab
        """
        messagebox.showinfo("Dependencias requeridas", help_text)


# Función de conveniencia para uso rápido
def create_export_button(parent, tree: ttk.Treeview, title: str, **kwargs) -> ttk.Button:
    """Crea un botón de exportación (alias para TreeviewExporter.create_export_button)"""
    return TreeviewExporter.create_export_button(parent, tree, title, **kwargs)
# smart_treeview.py
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from datetime import datetime

class SmartTreeview(ttk.Treeview):
    """
    Treeview mejorado con autoajuste inteligente, tooltips y personalización
    """
    
    def __init__(self, parent, columns_config=None, *args, **kwargs):
        """
        Inicializa el SmartTreeview
        
        Args:
            parent: Widget padre
            columns_config: Configuración de columnas (opcional)
            *args, **kwargs: Argumentos para Treeview
        """
        super().__init__(parent, *args, **kwargs)
        
        # Configurar estilos
        self.configure_style()
        
        # Variables para tooltips
        self.tooltips = {}
        self.column_tooltips = {}
        
        # Configurar eventos
        self.setup_events()
        
        # Configurar menú contextual
        self.setup_context_menu()
        
        # Configurar columnas si se proporciona configuración
        if columns_config:
            self.setup_columns(columns_config)
    
    def configure_style(self):
        """Configurar estilos para mejor legibilidad"""
        style = ttk.Style()
        
        # Configurar fuentes más legibles
        style.configure("Treeview", 
                       font=("Segoe UI", 9),  # Cambiar por fuente disponible
                       rowheight=28,  # Más altura para mejor lectura
                       background="#FFFFFF",
                       fieldbackground="#FFFFFF",
                       borderwidth=0)
        
        style.configure("Treeview.Heading", 
                       font=("Segoe UI", 9, "bold"),
                       background="#2C3E50",
                       foreground="white",
                       relief="flat",
                       borderwidth=1)
        
        # Configurar colores para filas alternadas y selección
        style.map("Treeview", 
                 background=[("selected", "#3498DB")],
                 foreground=[("selected", "white")])
        
        # Colores alternados para filas
        self.tag_configure('oddrow', background='#F8F9FA')
        self.tag_configure('evenrow', background='#FFFFFF')
    
    def setup_events(self):
        """Configurar eventos del Treeview"""
        self.bind("<Configure>", self.on_resize)
        self.bind("<Visibility>", self.on_visibility)
        
        # Evento para alternar colores de filas
        self.bind("<<TreeviewOpen>>", self.update_row_tags)
        self.bind("<<TreeviewClose>>", self.update_row_tags)
        
        # Evento para tooltips de contenido largo
        self.bind("<Motion>", self.show_content_tooltip)
        self.bind("<Leave>", self.hide_content_tooltip)
    
    def setup_columns(self, columns_config):
        """
        Configurar columnas con especificaciones detalladas
        
        Args:
            columns_config: Lista de diccionarios con configuración de columnas
                Ejemplo: [
                    {"id": "id", "display": "ID", "width": 60, "min_width": 40, "max_width": 80, "anchor": "center"},
                    {"id": "nombre", "display": "Nombre Completo", "width": 200, "ellipsis": True, "priority": 1}
                ]
        """
        # Extraer IDs de columnas
        column_ids = [col["id"] for col in columns_config]
        self["columns"] = column_ids
        self["show"] = "headings"
        
        # Configurar cada columna
        for col_config in columns_config:
            col_id = col_config["id"]
            
            # Configurar encabezado
            display_text = col_config.get("display", col_id.replace("_", " ").title())
            self.heading(col_id, 
                        text=display_text,
                        anchor=col_config.get("anchor", "w"),
                        command=lambda c=col_id: self.sort_column(c))
            
            # Configurar columna
            width = col_config.get("width", 100)
            min_width = col_config.get("min_width", 50)
            max_width = col_config.get("max_width", 400)
            
            self.column(col_id, 
                       width=width,
                       minwidth=min_width,
                       anchor=col_config.get("anchor", "w"),
                       stretch=col_config.get("stretch", True))
            
            # Guardar configuración para uso futuro
            if not hasattr(self, '_columns_config'):
                self._columns_config = {}
            self._columns_config[col_id] = col_config
            
            # Tooltip para encabezado si es largo
            if len(display_text) > 12:
                self.create_header_tooltip(col_id, display_text)
        
        # Autoajustar después de un breve delay
        self.after(100, self.auto_adjust_columns)
    
    def create_header_tooltip(self, column, text):
        """Crear tooltip para encabezados largos"""
        def show_header_tooltip(event):
            # Solo mostrar si no hay tooltip activo
            if column not in self.tooltips:
                x, y = event.x_root, event.y_root
                tw = tk.Toplevel(self)
                tw.wm_overrideredirect(True)
                tw.wm_geometry(f"+{x+10}+{y+10}")
                
                # Estilo del tooltip
                label = tk.Label(tw, text=text, 
                               background="#FFFFE0",
                               relief="solid",
                               borderwidth=1,
                               font=("Segoe UI", 9),
                               padx=8, pady=4)
                label.pack()
                self.tooltips[column] = tw
                
                # Auto-ocultar después de 3 segundos
                self.after(3000, lambda c=column: self.hide_tooltip(c))
            
        def hide_header_tooltip(event):
            self.hide_tooltip(column)
        
        # Vincular eventos
        header_id = self.winfo_parent() + ".heading." + column
        self.bind_class(header_id, "<Enter>", show_header_tooltip)
        self.bind_class(header_id, "<Leave>", hide_header_tooltip)
    
    def show_content_tooltip(self, event):
        """Mostrar tooltip para contenido de celda largo"""
        # Identificar la región bajo el cursor
        region = self.identify_region(event.x, event.y)
        
        if region == "cell":
            # Obtener columna y elemento
            col = self.identify_column(event.x)
            item = self.identify_row(event.y)
            
            if item and col:
                col_index = int(col.replace('#', '')) - 1
                columns = self["columns"]
                
                if 0 <= col_index < len(columns):
                    col_id = columns[col_index]
                    value = self.set(item, col_id)
                    
                    # Mostrar tooltip si el contenido es largo
                    if value and len(str(value)) > 25:
                        # Crear tooltip
                        x, y = event.x_root, event.y_root
                        
                        # Limpiar tooltip anterior
                        if hasattr(self, '_content_tooltip'):
                            self._content_tooltip.destroy()
                        
                        # Crear nuevo tooltip
                        self._content_tooltip = tk.Toplevel(self)
                        self._content_tooltip.wm_overrideredirect(True)
                        self._content_tooltip.wm_geometry(f"+{x+15}+{y+15}")
                        
                        # Configurar tooltip
                        text = tk.Text(self._content_tooltip, 
                                     height=4, width=40,
                                     wrap="word",
                                     font=("Segoe UI", 9),
                                     relief="solid",
                                     borderwidth=1)
                        text.insert("1.0", str(value))
                        text.config(state="disabled")
                        text.pack()
                        
                        # Auto-ocultar
                        self.after(5000, self.hide_content_tooltip)
    
    def hide_content_tooltip(self, event=None):
        """Ocultar tooltip de contenido"""
        if hasattr(self, '_content_tooltip'):
            self._content_tooltip.destroy()
            delattr(self, '_content_tooltip')
    
    def hide_tooltip(self, column):
        """Ocultar tooltip específico"""
        if column in self.tooltips:
            self.tooltips[column].destroy()
            del self.tooltips[column]
    
    def auto_adjust_columns(self):
        """Autoajustar columnas basado en contenido y espacio disponible"""
        if not self.get_children():
            return
        
        # Calcular espacio disponible
        available_width = self.winfo_width() - 25  # Dejar espacio para scrollbar
        
        # Obtener todas las columnas
        columns = self["columns"]
        if not columns:
            return
        
        # Calcular pesos basados en prioridad o tipo de dato
        column_weights = self.calculate_column_weights(columns, available_width)
        
        # Ajustar cada columna
        for i, col in enumerate(columns):
            # Obtener configuración de la columna
            col_config = self._columns_config.get(col, {}) if hasattr(self, '_columns_config') else {}
            
            # Calcular ancho basado en contenido
            content_width = self.calculate_content_width(col)
            header_width = self.calculate_header_width(col)
            
            # Usar el mayor entre contenido y encabezado
            min_needed = max(content_width, header_width, col_config.get("min_width", 50))
            max_allowed = min(available_width * 0.8, col_config.get("max_width", 300))
            
            # Asignar ancho basado en peso
            weight = column_weights.get(col, 1)
            assigned_width = min(max(min_needed, weight), max_allowed)
            
            # Aplicar ancho
            self.column(col, width=int(assigned_width))
    
    def calculate_column_weights(self, columns, available_width):
        """Calcular pesos para distribución proporcional"""
        weights = {}
        total_weight = 0
        
        for col in columns:
            col_config = self._columns_config.get(col, {}) if hasattr(self, '_columns_config') else {}
            
            # Determinar peso basado en prioridad
            priority = col_config.get("priority", 2)
            if priority == 1:  # Alta prioridad
                weight = 3
            elif priority == 2:  # Media prioridad
                weight = 2
            else:  # Baja prioridad
                weight = 1
            
            weights[col] = weight
            total_weight += weight
        
        # Convertir pesos a anchos proporcionales
        if total_weight > 0:
            for col in weights:
                weights[col] = (weights[col] / total_weight) * available_width
        
        return weights
    
    def calculate_content_width(self, column):
        """Calcular ancho máximo del contenido en una columna"""
        font = tkfont.Font(font="TkDefaultFont")
        max_width = 0
        
        # Ver contenido de cada fila
        for item in self.get_children():
            value = self.set(item, column)
            if value:
                # Medir ancho del texto
                text_width = font.measure(str(value))
                
                # Agregar padding y espacio para iconos
                cell_width = text_width + 30
                
                if cell_width > max_width:
                    max_width = cell_width
        
        return max_width
    
    def calculate_header_width(self, column):
        """Calcular ancho necesario para el encabezado"""
        font = tkfont.Font(font="TkDefaultFont")
        header_text = self.heading(column)["text"]
        
        # Medir texto y agregar espacio para icono de ordenamiento
        header_width = font.measure(header_text) + 40
        
        return header_width
    
    def on_resize(self, event):
        """Reajustar columnas cuando se redimensiona"""
        if event.widget == self and self.winfo_width() > 50:
            self.after(150, self.auto_adjust_columns)
    
    def on_visibility(self, event):
        """Ajustar columnas cuando se hace visible"""
        self.after(200, self.auto_adjust_columns)
    
    def update_row_tags(self, event=None):
        """Actualizar tags para colores alternados"""
        children = self.get_children()
        for i, child in enumerate(children):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.item(child, tags=(tag,))
    
    def setup_context_menu(self):
        """Configurar menú contextual para personalización"""
        self.context_menu = tk.Menu(self, tearoff=0)
        
        # Opciones principales
        self.context_menu.add_command(
            label="📏 Autoajustar columnas",
            command=self.auto_adjust_columns
        )
        self.context_menu.add_separator()
        
        # Submenú para mostrar/ocultar columnas
        self.columns_menu = tk.Menu(self.context_menu, tearoff=0)
        self.context_menu.add_cascade(label="👁️ Mostrar/Ocultar columnas", menu=self.columns_menu)
        
        # Opción para restaurar configuración
        self.context_menu.add_command(
            label="🔄 Restaurar configuración por defecto",
            command=self.restore_default_columns
        )
        self.context_menu.add_separator()
        
        # Opción para copiar datos
        self.context_menu.add_command(
            label="📋 Copiar datos seleccionados",
            command=self.copy_selected_data
        )
        
        # Vincular menú contextual
        self.bind("<Button-3>", self.show_context_menu)
        
        # También para encabezados
        self.bind_all("Treeview.Heading <Button-3>", self.show_header_context_menu, add='+')
    
    def show_context_menu(self, event):
        """Mostrar menú contextual en el cuerpo del Treeview"""
        # Actualizar menú de columnas
        self.update_columns_menu()
        
        # Mostrar menú
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def show_header_context_menu(self, event):
        """Mostrar menú contextual especial para encabezados"""
        # Identificar la columna clickeada
        col_id = self.identify_column(event.x)
        if col_id:
            col_index = int(col_id.replace('#', '')) - 1
            columns = self["columns"]
            
            if 0 <= col_index < len(columns):
                col_name = columns[col_index]
                self.show_column_menu(event, col_name)
    
    def show_column_menu(self, event, column):
        """Mostrar menú específico para una columna"""
        menu = tk.Menu(self, tearoff=0)
        
        # Información de la columna
        display_name = self.heading(column)["text"]
        current_width = self.column(column)["width"]
        
        menu.add_command(
            label=f"Columna: {display_name}",
            state="disabled"
        )
        menu.add_command(
            label=f"Ancho actual: {current_width}px",
            state="disabled"
        )
        menu.add_separator()
        
        # Opciones de ancho
        width_submenu = tk.Menu(menu, tearoff=0)
        for width in [60, 80, 100, 120, 150, 180, 200, 250, 300]:
            width_submenu.add_command(
                label=f"{width}px",
                command=lambda w=width, c=column: self.column(c, width=w)
            )
        menu.add_cascade(label="📐 Establecer ancho", menu=width_submenu)
        
        menu.add_command(
            label="📏 Autoajustar esta columna",
            command=lambda c=column: self.auto_adjust_single_column(c)
        )
        menu.add_separator()
        
        # Opciones de alineación
        align_submenu = tk.Menu(menu, tearoff=0)
        align_submenu.add_command(
            label="Izquierda",
            command=lambda c=column: self.heading(c, anchor="w")
        )
        align_submenu.add_command(
            label="Centro",
            command=lambda c=column: self.heading(c, anchor="center")
        )
        align_submenu.add_command(
            label="Derecha",
            command=lambda c=column: self.heading(c, anchor="e")
        )
        menu.add_cascade(label="↔️ Alineación", menu=align_submenu)
        
        menu.add_separator()
        menu.add_command(
            label="❌ Ocultar columna",
            command=lambda c=column: self.hide_column(c)
        )
        
        # Mostrar menú
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def update_columns_menu(self):
        """Actualizar el submenú de columnas"""
        # Limpiar menú actual
        self.columns_menu.delete(0, tk.END)
        
        # Agregar opción para cada columna
        for col in self["columns"]:
            display_name = self.heading(col)["text"]
            var = tk.BooleanVar(value=True)
            
            self.columns_menu.add_checkbutton(
                label=display_name,
                variable=var,
                command=lambda c=col, v=var: self.toggle_column_visibility(c, v)
            )
    
    def toggle_column_visibility(self, column, var):
        """Mostrar u ocultar una columna"""
        if var.get():
            self.column(column, width=100)  # Restaurar con ancho por defecto
        else:
            self.column(column, width=0)  # Ocultar
    
    def auto_adjust_single_column(self, column):
        """Autoajustar una sola columna"""
        content_width = self.calculate_content_width(column)
        header_width = self.calculate_header_width(column)
        
        new_width = max(content_width, header_width, 50)
        new_width = min(new_width, 400)  # Límite máximo
        
        self.column(column, width=int(new_width))
    
    def hide_column(self, column):
        """Ocultar una columna"""
        self.column(column, width=0)
    
    def restore_default_columns(self):
        """Restaurar configuración por defecto de columnas"""
        if hasattr(self, '_columns_config'):
            for col, config in self._columns_config.items():
                width = config.get("width", 100)
                anchor = config.get("anchor", "w")
                
                self.column(col, width=width)
                self.heading(col, anchor=anchor)
    
    def copy_selected_data(self):
        """Copiar datos seleccionados al portapapeles"""
        selection = self.selection()
        if not selection:
            return
        
        copied_data = []
        
        # Obtener encabezados visibles
        headers = []
        for col in self["columns"]:
            if self.column(col)["width"] > 0:  # Solo columnas visibles
                headers.append(self.heading(col)["text"])
        
        copied_data.append("\t".join(headers))
        
        # Obtener datos de las filas seleccionadas
        for item in selection:
            row_data = []
            for col in self["columns"]:
                if self.column(col)["width"] > 0:  # Solo columnas visibles
                    row_data.append(str(self.set(item, col) or ""))
            
            copied_data.append("\t".join(row_data))
        
        # Copiar al portapapeles
        self.clipboard_clear()
        self.clipboard_append("\n".join(copied_data))
    
    def sort_column(self, column, reverse=False):
        """Ordenar columna al hacer clic en el encabezado"""
        # Obtener datos
        data = [(self.set(item, column), item) for item in self.get_children()]
        
        # Intentar ordenar numéricamente si es posible
        try:
            data.sort(key=lambda t: float(t[0].replace('$', '').replace(',', '')) 
                     if t[0] else 0, reverse=reverse)
        except (ValueError, AttributeError):
            # Ordenar alfabéticamente
            data.sort(reverse=reverse)
        
        # Reorganizar items
        for index, (_, item) in enumerate(data):
            self.move(item, '', index)
        
        # Cambiar dirección para el próximo clic
        self.heading(column, command=lambda: self.sort_column(column, not reverse))
        
        # Actualizar tags de filas
        self.update_row_tags()


# Función de conveniencia para crear configuraciones de columnas
def create_columns_config(config_type="default"):
    """Crear configuraciones predefinidas de columnas"""
    
    configs = {
        "advances": [
            {"id": "id", "display": "ID", "width": 60, "min_width": 40, "max_width": 80, "anchor": "center", "priority": 3},
            {"id": "empleado", "display": "Empleado", "width": 180, "min_width": 100, "max_width": 250, "priority": 1},
            {"id": "departamento", "display": "Departamento", "width": 120, "min_width": 80, "max_width": 150, "priority": 2},
            {"id": "fecha", "display": "Fecha", "width": 100, "min_width": 80, "max_width": 120, "anchor": "center", "priority": 2},
            {"id": "monto", "display": "Monto ($)", "width": 100, "min_width": 80, "max_width": 150, "anchor": "e", "priority": 1},
            {"id": "estado", "display": "Estado", "width": 90, "min_width": 70, "max_width": 120, "anchor": "center", "priority": 2},
            {"id": "destino", "display": "Destino", "width": 140, "min_width": 100, "max_width": 200, "priority": 3},
        ],
        "liquidations": [
            {"id": "id", "display": "ID", "width": 60, "min_width": 40, "max_width": 80, "anchor": "center", "priority": 3},
            {"id": "empleado", "display": "Empleado", "width": 160, "min_width": 100, "max_width": 220, "priority": 1},
            {"id": "periodo", "display": "Período", "width": 100, "min_width": 80, "max_width": 120, "anchor": "center", "priority": 1},
            {"id": "dias", "display": "Días", "width": 60, "min_width": 40, "max_width": 80, "anchor": "center", "priority": 3},
            {"id": "total", "display": "Total ($)", "width": 100, "min_width": 80, "max_width": 150, "anchor": "e", "priority": 1},
            {"id": "anticipo", "display": "Anticipo ($)", "width": 110, "min_width": 90, "max_width": 160, "anchor": "e", "priority": 2},
            {"id": "saldo", "display": "Saldo ($)", "width": 100, "min_width": 80, "max_width": 150, "anchor": "e", "priority": 1},
            {"id": "fecha_liq", "display": "Fecha Liq.", "width": 100, "min_width": 80, "max_width": 120, "anchor": "center", "priority": 2},
        ],
        "all": [
            {"id": "id", "display": "ID", "width": 60, "min_width": 40, "max_width": 80, "anchor": "center", "priority": 3},
            {"id": "empleado", "display": "Empleado", "width": 160, "min_width": 100, "max_width": 220, "priority": 1},
            {"id": "departamento", "display": "Depto.", "width": 100, "min_width": 70, "max_width": 130, "priority": 2},
            {"id": "fecha", "display": "Fecha", "width": 90, "min_width": 70, "max_width": 110, "anchor": "center", "priority": 2},
            {"id": "tipo", "display": "Tipo", "width": 90, "min_width": 70, "max_width": 120, "anchor": "center", "priority": 2},
            {"id": "monto", "display": "Monto", "width": 100, "min_width": 80, "max_width": 150, "anchor": "e", "priority": 1},
            {"id": "estado", "display": "Estado", "width": 90, "min_width": 70, "max_width": 120, "anchor": "center", "priority": 2},
            {"id": "observaciones", "display": "Observaciones", "width": 150, "min_width": 100, "max_width": 250, "priority": 3},
        ]
    }
    
    return configs.get(config_type, configs["advances"])
import tkinter as tk
from tkinter import ttk

class RequestUserList(ttk.Frame):
    """Componente de lista de usuarios solicitantes con selección"""
    
    def __init__(self, parent, select_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.select_callback = select_callback
        
        self._create_widgets()

    def _create_widgets(self):
        """Crea la lista de usuarios solicitantes"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Crear Treeview con scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ('Username', 'Nombre Completo', 'Email', 'CI', 'Departamento')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        column_widths = [120, 200, 200, 100, 150]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Posicionar widgets
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind para selección
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _on_select(self, event):
        """Maneja la selección de usuarios en la tabla"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            user_id = self.tree.item(item)['tags'][0] if self.tree.item(item)['tags'] else None
            self.select_callback(user_id)
        else:
            self.select_callback(None)

    def load_users(self, users):
        """Carga los usuarios en la tabla - ID OCULTO"""
        # Limpiar tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar nuevos usuarios - ID guardado en tags
        for user in users:
            item_id = self.tree.insert('', tk.END, values=(
                user.username,
                user.fullname,
                user.email,
                user.ci,
                user.department_name  # Asumiendo que el servicio incluye el nombre del departamento
            ))
            # Guardar ID como tag para poder recuperarlo luego
            self.tree.item(item_id, tags=(user.id,))

    def get_selected_id(self):
        """Obtiene el ID del usuario seleccionado desde los tags"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item)['tags']
            return tags[0] if tags else None
        return None
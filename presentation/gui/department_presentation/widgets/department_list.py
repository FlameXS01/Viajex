import tkinter as tk
from tkinter import ttk

class DepartmentList(ttk.Frame):
    """Componente de lista de departamentos con selección"""
    
    def __init__(self, parent, select_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.select_callback = select_callback
        
        self._create_widgets()

    def _create_widgets(self):
        """Crea la lista de departamentos"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Crear Treeview con scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ('Nombre')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        self.tree.heading('Nombre', text='Nombre de departamento')
        self.tree.column('Nombre', width=300, minwidth=200, stretch=True)
        
        # Scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Posicionar widgets
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind para selección
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _on_select(self, event):
        """Maneja la selección de departamentos en la tabla"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            department_id = self.tree.item(item)['tags'][0] if self.tree.item(item)['tags'] else None
            self.select_callback(department_id)
        else:
            self.select_callback(None)

    def load_departments(self, departments):
        """Carga los departamentos en la tabla"""
        # Limpiar tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar nuevos departamentos
        for department in departments:
            item_id = self.tree.insert('', tk.END, values=(department.name,))
            self.tree.item(item_id, tags=(department.id,))

    def get_selected_id(self):
        """Obtiene el ID del departamento seleccionado desde los tags"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item)['tags']
            return tags[0] if tags else None
        return None
import tkinter as tk
from tkinter import ttk, messagebox
from application.services.department_service import DepartmentService
from presentation.gui.utils.windows_utils import WindowUtils

class DepartmentMainWindow:
    def __init__(self, department_service: DepartmentService, parent=None):
        self.department_service = department_service
        self.selected_department_id = None
        
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Gestión de Departamentos")
        self.root.geometry("800x600")
        
        if parent:
            WindowUtils.center_window(self.root, parent)
        else:
            WindowUtils.center_window(self.root)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self._create_widgets()
        self._load_departments()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="Gestión de Departamentos", 
                 font=('Arial', 18, 'bold')).grid(row=0, column=0, sticky='w')
        
        ttk.Button(header_frame, text="➕ Crear Departamento", 
                  command=self._create_department).grid(row=0, column=1, sticky='e')
        
        # Lista de departamentos
        list_frame = ttk.LabelFrame(main_frame, text="Departamentos Existentes", padding="15")
        list_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview para departamentos
        columns = ('ID', 'Nombre')
        self.department_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.department_tree.heading(col, text=col)
            self.department_tree.column(col, width=100, minwidth=50)
        
        self.department_tree.column('Nombre', width=300)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.department_tree.yview)
        self.department_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.department_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Bind selección
        self.department_tree.bind('<<TreeviewSelect>>', self._on_department_select)
        
        # Acciones
        actions_frame = ttk.LabelFrame(main_frame, text="Acciones", padding="15")
        actions_frame.grid(row=2, column=0, sticky='ew')
        
        self.edit_btn = ttk.Button(actions_frame, text="Editar Departamento", 
                                 command=self._edit_department, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(actions_frame, text="Eliminar Departamento", 
                                   command=self._delete_department, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

    def _on_department_select(self, event):
        selection = self.department_tree.selection()
        if selection:
            self.selected_department_id = self.department_tree.item(selection[0])['values'][0]
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.selected_department_id = None
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

    def _create_department(self):
        # Aquí integrarás el DepartmentDialog después
        name = tk.simpledialog.askstring("Crear Departamento", "Nombre del departamento:")
        if name:
            try:
                result = self.department_service.create_department_f(name)
                messagebox.showinfo("Éxito", f"Departamento '{result.name}' creado")
                self._load_departments()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear: {str(e)}")

    def _edit_department(self):
        if not self.selected_department_id:
            return
            
        department = self.department_service.get_department_by_id(self.selected_department_id)
        if department:
            new_name = tk.simpledialog.askstring("Editar Departamento", "Nuevo nombre:", 
                                               initialvalue=department.name)
            if new_name:
                try:
                    result = self.department_service.update_department_f(self.selected_department_id, new_name)
                    messagebox.showinfo("Éxito", "Departamento actualizado")
                    self._load_departments()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")

    def _delete_department(self):
        if not self.selected_department_id:
            return
            
        department = self.department_service.get_department_by_id(self.selected_department_id)
        if department and messagebox.askyesno("Confirmar", f"¿Eliminar departamento '{department.name}'?"):
            try:
                success = self.department_service.delete_department_f(self.selected_department_id)
                if success:
                    messagebox.showinfo("Éxito", "Departamento eliminado")
                    self.selected_department_id = None
                    self._load_departments()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def _load_departments(self):
        for item in self.department_tree.get_children():
            self.department_tree.delete(item)
            
        try:
            departments = self.department_service.get_all_departments()
            for dept in departments:
                self.department_tree.insert('', tk.END, values=(dept.id, dept.name))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los departamentos: {str(e)}")

    def run(self):
        self.root.mainloop()
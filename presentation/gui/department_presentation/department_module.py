import tkinter as tk
from tkinter import ttk, messagebox
from application.services.department_service import DepartmentService

# Importar componentes modulares
from presentation.gui.department_presentation.widgets.department_form import DepartmentForm
from presentation.gui.department_presentation.widgets.department_list import DepartmentList
from presentation.gui.department_presentation.widgets.department_actions import DepartmentActions
from presentation.gui.department_presentation.dialogs.department_dialog import DepartmentDialog
from presentation.gui.user_presentation.dialogs.confirm_dialog import ConfirmDialog

class DepartmentModule(ttk.Frame):
    """Módulo de gestión de departamentos - Versión modularizada"""
    
    def __init__(self, parent, department_service: DepartmentService):
        super().__init__(parent, style='Content.TFrame')
        self.department_service = department_service
        self.selected_department_id = None
        
        self._create_widgets()
        self._load_departments()

    def _create_widgets(self):
        """Crea los widgets principales usando componentes modulares"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self, style='Content.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="Gestión de Departamentos", 
                 font=('Arial', 18, 'bold'), style='Content.TLabel').grid(row=0, column=0, sticky='w')
        
        ttk.Button(header_frame, text="➕ Crear Departamento", 
                  command=self._create_department).grid(row=0, column=1, sticky='e')
        
        # Lista de departamentos (componente modular)
        list_frame = ttk.LabelFrame(self, text="Departamentos Existentes", padding="15")
        list_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.department_list = DepartmentList(list_frame, self._on_department_select)
        self.department_list.grid(row=0, column=0, sticky='nsew')
        
        # Acciones de departamento (componente modular)
        actions_frame = ttk.LabelFrame(self, text="Acciones", padding="15")
        actions_frame.grid(row=2, column=0, sticky='ew')
        
        self.department_actions = DepartmentActions(actions_frame, {
            'edit': self._edit_department,
            'delete': self._delete_department
        })
        self.department_actions.grid(row=0, column=0, sticky='ew')

    def _on_department_select(self, department_id):
        """Maneja la selección de departamentos"""
        self.selected_department_id = department_id
        if department_id:
            self.department_actions.set_buttons_state(tk.NORMAL)
        else:
            self.department_actions.set_buttons_state(tk.DISABLED)

    def _create_department(self):
        """Abre diálogo para crear nuevo departamento"""
        dialog = DepartmentDialog(self.winfo_toplevel(), self.department_service)
        result = dialog.show()
        if result:
            self._load_departments()

    def _edit_department(self):
        """Abre diálogo para editar departamento existente"""
        if not self.selected_department_id:
            return
            
        department = self.department_service.get_department_by_id(self.selected_department_id)
        if department:
            dialog = DepartmentDialog(self.winfo_toplevel(), self.department_service, department)
            result = dialog.show()
            if result:
                self._load_departments()

    def _delete_department(self):
        """Elimina el departamento seleccionado"""
        if not self.selected_department_id:
            return
            
        department = self.department_service.get_department_by_id(self.selected_department_id)
        if not department:
            messagebox.showerror("Error", "Departamento no encontrado")
            return
            
        def confirm_delete():
            try:
                success = self.department_service.delete_department_f(self.selected_department_id)
                if success:
                    messagebox.showinfo("Éxito", "Departamento eliminado correctamente")
                    self.selected_department_id = None
                    self._load_departments()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el departamento")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el departamento: {str(e)}")

        ConfirmDialog(
            self.winfo_toplevel(),
            "Confirmar Eliminación",
            f"¿Estás seguro de que quieres eliminar el departamento '{department.name}'?\nEsta acción no se puede deshacer.",
            confirm_delete
        )

    def _load_departments(self):
        """Carga los departamentos en la lista"""
        try:
            departments = self.department_service.get_all_departments()
            self.department_list.load_departments(departments)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los departamentos: {str(e)}")
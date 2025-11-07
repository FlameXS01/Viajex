import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.utils.windows_utils import WindowUtils

class DepartmentDialog:
    """Diálogo para crear/editar departamentos"""
    
    def __init__(self, parent, department_service, department_data=None):
        self.department_service = department_service
        self.department_data = department_data
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Departamento" if department_data else "Crear Departamento")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        WindowUtils.center_window(self.dialog, parent)
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # Campo de nombre
        ttk.Label(main_frame, text="Nombre del Departamento:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=10)
        self.name_entry.focus()

        # Si estamos en modo edición, cargar los datos existentes
        if self.department_data:
            self.name_entry.insert(0, self.department_data.name)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Guardar", command=self._save).grid(row=0, column=1, padx=5)

    def _save(self):
        """Guarda los datos del departamento"""
        name = self.name_entry.get()

        if not name:
            messagebox.showwarning("Advertencia", "El nombre del departamento es obligatorio")
            return

        try:
            if self.department_data:
                # Actualizar departamento existente
                department = self.department_service.update_department_f(self.department_data.id, name)
                self.result = department
                messagebox.showinfo("Éxito", "Departamento actualizado correctamente")
            else:
                # Crear nuevo departamento
                department = self.department_service.create_department_f(name)
                self.result = department
                messagebox.showinfo("Éxito", "Departamento creado correctamente")
            
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el departamento: {str(e)}")

    def show(self):
        """Muestra el diálogo y retorna el resultado"""
        self.dialog.wait_window()
        return self.result
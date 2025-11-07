import tkinter as tk
from tkinter import ttk, messagebox
from application.dtos.diet_dtos import DietMemberCreateDTO

class DietMemberDialog(tk.Toplevel):
    """
    Diálogo para gestionar miembros de dieta grupal
    """
    
    def __init__(self, parent, diet_controller, diet):
        super().__init__(parent)
        self.diet_controller = diet_controller
        self.diet = diet
        self.result = False
        
        self.title(f"Miembros - Dieta #{diet.advance_number}")
        self.geometry("600x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
        self.load_members()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para agregar nuevo miembro
        add_frame = ttk.LabelFrame(main_frame, text="Agregar Miembro", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_frame, text="Solicitante:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.request_user_combo = ttk.Combobox(add_frame, state="readonly", width=30)
        self.request_user_combo.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0), pady=5)
        
        ttk.Button(add_frame, text="Agregar", command=self.on_add_member).grid(row=0, column=2, padx=(5, 0))
        
        add_frame.columnconfigure(1, weight=1)
        
        # Frame para lista de miembros
        list_frame = ttk.LabelFrame(main_frame, text="Miembros Actuales", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para miembros
        columns = ["id", "nombre", "ci", "departamento"]
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("ci", text="CI")
        self.tree.heading("departamento", text="Departamento")
        
        self.tree.column("id", width=50)
        self.tree.column("nombre", width=200)
        self.tree.column("ci", width=100)
        self.tree.column("departamento", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón eliminar
        ttk.Button(list_frame, text="Eliminar Seleccionado", 
                  command=self.on_remove_member).pack(pady=(5, 0))
        
        # Botones principales
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Cerrar", command=self.destroy).pack(side=tk.RIGHT)
    
    def center_on_parent(self, parent):
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def load_members(self):
        # Cargar miembros actuales
        try:
            members = self.diet_controller.list_diet_members(self.diet.id)
            for member in members:
                self.tree.insert("", "end", values=(
                    member.id,
                    member.request_user_name,
                    member.request_user_ci,
                    "Departamento"  # Esto debería venir del DTO
                ))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los miembros: {str(e)}")
    
    def on_add_member(self):
        selected_user = self.request_user_combo.get()
        if not selected_user:
            messagebox.showwarning("Advertencia", "Seleccione un solicitante")
            return
        
        try:
            # Obtener ID del usuario seleccionado (esto es un ejemplo)
            # En implementación real, necesitarías mapear el combobox a IDs
            user_id = 1  # Esto debería venir del combobox
            
            create_dto = DietMemberCreateDTO(
                diet_id=self.diet.id,
                request_user_id=user_id
            )
            
            result = self.diet_controller.add_diet_member(create_dto)
            if result:
                self.load_members()  # Recargar lista
                self.result = True
                messagebox.showinfo("Éxito", "Miembro agregado correctamente")
            else:
                messagebox.showerror("Error", "No se pudo agregar el miembro")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar miembro: {str(e)}")
    
    def on_remove_member(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un miembro para eliminar")
            return
        
        member_id = self.tree.item(selected[0])["values"][0]
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este miembro?"):
            try:
                success = self.diet_controller.remove_diet_member(member_id)
                if success:
                    self.tree.delete(selected[0])
                    self.result = True
                    messagebox.showinfo("Éxito", "Miembro eliminado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el miembro")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
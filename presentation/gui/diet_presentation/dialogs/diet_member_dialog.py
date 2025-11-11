import tkinter as tk
from tkinter import ttk, messagebox
from application.dtos.diet_dtos import DietMemberCreateDTO

class DietMemberDialog(tk.Toplevel):
    """
    Diálogo para gestionar miembros de dieta grupal - MEJORADO
    """
    
    def __init__(self, parent, diet_controller, diet):
        super().__init__(parent)
        self.diet_controller = diet_controller
        self.diet = diet
        self.result = False
        
        self.title(f"👥 Miembros - Dieta #{diet.advance_number}")
        self.geometry("700x500")  # Aumentado para mejor visualización
        self.resizable(True, True)  # Permitir redimensionar
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
        self.load_members()
        self.load_available_users()
    
    def create_widgets(self):
        """Crea los widgets del diálogo con mejor distribución"""
        # Frame principal con padding
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para agregar nuevo miembro - MEJORADO
        add_frame = ttk.LabelFrame(main_frame, text="➕ Agregar Nuevo Miembro", padding=12)
        add_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(add_frame, text="Seleccionar Usuario:", 
                 font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=8)
        
        # Combobox más ancho y con mejor estilo
        self.request_user_combo = ttk.Combobox(
            add_frame, 
            state="readonly", 
            width=45,
            font=('Arial', 9),
            height=15  # Más items visibles
        )
        self.request_user_combo.grid(row=0, column=1, sticky=tk.EW, padx=(10, 15), pady=8)
        
        # Botón con mejor estilo
        ttk.Button(
            add_frame, 
            text="Agregar Miembro", 
            command=self.on_add_member,
            width=15
        ).grid(row=0, column=2, padx=(5, 0), pady=8)
        
        add_frame.columnconfigure(1, weight=1)  # Hacer el combobox expansivo
        
        # Frame para lista de miembros - MEJORADO
        list_frame = ttk.LabelFrame(main_frame, text="📋 Miembros Actuales", padding=12)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview para miembros - SIN COLUMNA ID VISIBLE
        columns = ["nombre", "ci", "departamento"]
        self.tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings", 
            height=12,  # Más filas visibles
            selectmode="browse"  # Solo selección simple
        )
        
        # Configurar columnas (SIN ID)
        self.tree.heading("nombre", text="👤 Nombre Completo")
        self.tree.heading("ci", text="📄 Cédula")
        self.tree.heading("departamento", text="🏢 Departamento")
        
        # Ajustar anchos de columnas
        self.tree.column("nombre", width=250, minwidth=200)
        self.tree.column("ci", width=120, minwidth=100)
        self.tree.column("departamento", width=200, minwidth=150)
        
        # Scrollbar mejorada
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar treeview y scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botones de acción - MEJORADO
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            action_frame, 
            text="🗑️ Eliminar Miembro Seleccionado", 
            command=self.on_remove_member,
            width=25
        ).pack(pady=5)
        
        # Botones principales - MEJORADOS
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            buttons_frame, 
            text="✅ Cerrar", 
            command=self.destroy,
            width=15
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            buttons_frame, 
            text="🔄 Actualizar Lista", 
            command=self.load_members,
            width=15
        ).pack(side=tk.RIGHT)

    def center_on_parent(self, parent):
        """Centra el diálogo en la ventana padre"""
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = 700  # Tamaño fijo para centrado
        height = 500
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def load_available_users(self):
        """Carga los usuarios disponibles en el combobox"""
        try:
            # Obtener usuarios disponibles (debes implementar este método)
            available_users = self.diet_controller.get_available_users(self.diet.id)
            
            # Ordenar alfabéticamente por nombre
            sorted_users = sorted(
                available_users, 
                key=lambda user: user.fullname.lower()
            )
            
            user_display = [f"{user.fullname} ({user.ci})" for user in sorted_users]
            self.request_user_combo['values'] = user_display
            
            if user_display:
                self.request_user_combo.set(user_display[0])
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los usuarios: {str(e)}")
    
    def load_members(self):
        """Carga los miembros actuales de la dieta"""
        try:
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Cargar miembros actuales
            members = self.diet_controller.list_diet_members(self.diet.id)
            
            # Ordenar miembros alfabéticamente
            sorted_members = sorted(
                members, 
                key=lambda member: member.request_user_name.lower()
            )
            
            for member in sorted_members:
                self.tree.insert("", "end", 
                    values=(
                        member.request_user_name,
                        member.request_user_ci,
                        getattr(member, 'department', 'N/A')  # Manejar atributo opcional
                    ),
                    tags=(member.id,)  # Guardar ID como tag para referencia
                )
                
            # Actualizar contador
            member_count = len(sorted_members)
            list_frame_text = f"📋 Miembros Actuales ({member_count} miembros)"
            self.nametowidget(list_frame).configure(text=list_frame_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los miembros: {str(e)}")
    
    def on_add_member(self):
        """Agrega un nuevo miembro a la dieta"""
        selected_display = self.request_user_combo.get()
        if not selected_display:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para agregar")
            return
        
        try:
            # Extraer ID del usuario seleccionado
            user_id = self._get_user_id_from_display(selected_display)
            if not user_id:
                messagebox.showerror("Error", "No se pudo identificar el usuario seleccionado")
                return
            
            create_dto = DietMemberCreateDTO(
                diet_id=self.diet.id,
                request_user_id=user_id
            )
            
            result = self.diet_controller.add_diet_member(create_dto)
            if result:
                self.load_members()  # Recargar lista
                self.load_available_users()  # Actualizar combobox
                self.result = True
                messagebox.showinfo("Éxito", "✅ Miembro agregado correctamente")
            else:
                messagebox.showerror("Error", "❌ No se pudo agregar el miembro")
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al agregar miembro: {str(e)}")
    
    def on_remove_member(self):
        """Elimina el miembro seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un miembro para eliminar")
            return
        
        # Obtener datos del miembro seleccionado
        member_name = self.tree.item(selected[0])["values"][0]
        member_id = self.tree.item(selected[0])["tags"][0]  # ID guardado como tag
        
        if messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Está seguro de eliminar al miembro:\n\"{member_name}\"?"
        ):
            try:
                success = self.diet_controller.remove_diet_member(member_id)
                if success:
                    self.tree.delete(selected[0])
                    self.load_available_users()  # Actualizar combobox
                    self.result = True
                    messagebox.showinfo("Éxito", "✅ Miembro eliminado correctamente")
                else:
                    messagebox.showerror("Error", "❌ No se pudo eliminar el miembro")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Error al eliminar: {str(e)}")
    
    def _get_user_id_from_display(self, display_text):
        """Obtiene el ID de usuario desde el texto mostrado en el combobox"""
        try:
            # El formato es "Nombre Completo (CI)"
            # Buscar en la lista de usuarios disponibles
            available_users = self.diet_controller.get_available_users(self.diet.id)
            
            for user in available_users:
                user_display = f"{user.fullname} ({user.ci})"
                if user_display == display_text:
                    return user.id
                    
            return None
        except Exception:
            return None
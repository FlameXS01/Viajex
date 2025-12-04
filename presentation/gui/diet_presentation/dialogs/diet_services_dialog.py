import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from application.dtos.diet_dtos import DietServiceResponseDTO
from application.services.diet_service import DietAppService

class DietServicesDialog(tk.Toplevel):
    """Diálogo para gestionar servicios de dieta"""
    
    def __init__(self, parent, diet_service: DietAppService):
        super().__init__(parent)
        self.diet_service = diet_service
        self.selected_service: Optional[DietServiceResponseDTO] = None
        self.result = False
        
        self._setup_dialog()
        self._create_widgets()
        self._load_services()
        
    def _setup_dialog(self):
        """Configura el diálogo"""
        self.title("Gestión de Servicios de Dieta")
        self.geometry("800x500")
        self.resizable(True, True)
        self.transient(self.master)
        self.grab_set()
        
        # Centrar en la pantalla
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Crea los widgets del diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Servicios de Dieta", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Frame de botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones de acciones
        ttk.Button(buttons_frame, text="➕ Agregar Servicio", 
                  command=self._add_service).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="✏️ Editar Servicio", 
                  command=self._edit_service).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="🗑️ Eliminar Servicio", 
                  command=self._delete_service).pack(side=tk.LEFT, padx=(0, 5))
        
        # Lista de servicios
        list_frame = ttk.LabelFrame(main_frame, text="Servicios Registrados", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar servicios
        columns = ("tipo", "desayuno", "almuerzo", "comida", "aloj_efectivo", "aloj_tarjeta")
        self.treeview = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configurar columnas
        #self.treeview.heading("id", text="ID")
        self.treeview.heading("tipo", text="Tipo")
        self.treeview.heading("desayuno", text="Desayuno ($)")
        self.treeview.heading("almuerzo", text="Almuerzo ($)")
        self.treeview.heading("comida", text="Comida ($)")
        self.treeview.heading("aloj_efectivo", text="Aloj. Efectivo ($)")
        self.treeview.heading("aloj_tarjeta", text="Aloj. Tarjeta ($)")
        
        #self.treeview.column("id", width=50)
        self.treeview.column("tipo", width=100)
        self.treeview.column("desayuno", width=100)
        self.treeview.column("almuerzo", width=100)
        self.treeview.column("comida", width=100)
        self.treeview.column("aloj_efectivo", width=120)
        self.treeview.column("aloj_tarjeta", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.treeview.bind("<<TreeviewSelect>>", self._on_service_select)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                    command=self.destroy).pack(side=tk.RIGHT, pady=(10, 0))
    
    def _load_services(self):
        """Carga los servicios en la lista"""
        try:
            services = self.diet_service.list_all_diet_services()
            self._update_treeview(services)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los servicios: {str(e)}")
    
    def _update_treeview(self, services: List[DietServiceResponseDTO]):
        """Actualiza el treeview con los servicios"""
        # Limpiar lista
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Agregar servicios
        for service in services:
            tipo = "Local" if service.is_local else "Fuera de provincia"
            self.treeview.insert("", "end", values=(
                tipo,
                f"${service.breakfast_price:.2f}",
                f"${service.lunch_price:.2f}",
                f"${service.dinner_price:.2f}",
                f"${service.accommodation_cash_price:.2f}",
                f"${service.accommodation_card_price:.2f}"
            ))
    
    def _get_local(self, place: str):
        if place == 'Fuera de provincia':
            return True
        return False

    def _on_service_select(self, event):
        """Maneja la selección de un servicio"""
        selection = self.treeview.selection()
        if selection:
            item = self.treeview.item(selection[0])
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>', item['values'][1])
            is_local = self._get_local(item['values'][1])
            
            
            # Buscar el servicio completo
            services = self.diet_service.list_all_diet_services()
            self.selected_service = next(
                (s for s in services if s.is_local == is_local), 
                None
            )
        else:
            self.selected_service = None
    
    def _add_service(self):
        """Abre diálogo para agregar nuevo servicio"""
        from .diet_service_form_dialog import DietServiceFormDialog
        
        dialog = DietServiceFormDialog(self, self.diet_service)
        self.wait_window(dialog)
        
        if dialog.result:
            self._load_services()
            messagebox.showinfo("Éxito", "Servicio agregado correctamente")
    
    def _edit_service(self):
        """Abre diálogo para editar servicio seleccionado"""
        if not self.selected_service:
            messagebox.showwarning("Advertencia", "Seleccione un servicio para editar")
            return
        
        from .diet_service_form_dialog import DietServiceFormDialog
        
        dialog = DietServiceFormDialog(self, self.diet_service, self.selected_service)
        self.wait_window(dialog)
        
        if dialog.result:
            self._load_services()
            self.selected_service = None
            messagebox.showinfo("Éxito", "Servicio actualizado correctamente")
    
    def _delete_service(self):
        """Elimina el servicio seleccionado"""
        if not self.selected_service:
            messagebox.showwarning("Advertencia", "Seleccione un servicio para eliminar")
            return
        
        tipo = "Local" if self.selected_service.is_local else "Fuera de provincia"
        
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el servicio {tipo}?\n\n"
            f"Desayuno: ${self.selected_service.breakfast_price:.2f}\n"
            f"Almuerzo: ${self.selected_service.lunch_price:.2f}\n"
            f"Comida: ${self.selected_service.dinner_price:.2f}"
        ):
            try:
                success = self.diet_service.delete_diet_service(self.selected_service.id)
                if success:
                    self._load_services()
                    self.selected_service = None
                    messagebox.showinfo("Éxito", "Servicio eliminado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el servicio")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
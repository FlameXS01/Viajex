import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from application.controller.diet_controller import DietController
from application.dtos.diet_dtos import DietResponseDTO, DietLiquidationResponseDTO
from .widgets.diet_list import DietList
from .widgets.diet_actions import DietActions
from .dialogs.diet_dialog import DietDialog
from .dialogs.diet_liquidation_dialog import DietLiquidationDialog
from .dialogs.diet_member_dialog import DietMemberDialog

class DietModule(ttk.Frame):
    """
    Módulo principal de gestión de dietas
    """
    
    def __init__(self, parent, diet_controller: DietController, **kwargs):
        super().__init__(parent, **kwargs)
        self.diet_controller = diet_controller
        self.current_diet: Optional[DietResponseDTO] = None
        
        self.create_widgets()
        self.refresh_diets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="Gestión de Dietas", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones principales
        self.actions_widget = DietActions(controls_frame, self)
        self.actions_widget.pack(fill=tk.X)
        
        # Frame de contenido
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de anticipos
        self.advances_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advances_frame, text="Anticipos")
        
        # Pestaña de liquidaciones
        self.liquidations_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.liquidations_frame, text="Liquidaciones")
        
        # Lista de anticipos
        self.advances_list = DietList(self.advances_frame, "advances")
        self.advances_list.pack(fill=tk.BOTH, expand=True)
        self.advances_list.bind_selection(self.on_diet_selected)
        
        # Lista de liquidaciones
        self.liquidations_list = DietList(self.liquidations_frame, "liquidations")
        self.liquidations_list.pack(fill=tk.BOTH, expand=True)
        self.liquidations_list.bind_selection(self.on_liquidation_selected)
    
    def refresh_diets(self):
        """Actualiza las listas de dietas y liquidaciones"""
        try:
            # Obtener anticipos
            diets = self.diet_controller.list_diets()
            self.advances_list.update_data(diets)
            
            # Obtener liquidaciones
            liquidations = self.diet_controller.list_liquidations_by_date_range(
                start_date=None, end_date=None  # Últimos 30 días
            )
            self.liquidations_list.update_data(liquidations)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(e)}")
    
    def on_diet_selected(self, diet: DietResponseDTO):
        """Maneja la selección de una dieta"""
        self.current_diet = diet
        self.actions_widget.update_buttons_state(diet)
    
    def on_liquidation_selected(self, liquidation: DietLiquidationResponseDTO):
        """Maneja la selección de una liquidación"""
        self.current_diet = None
        self.actions_widget.update_buttons_state(None)
    
    def create_diet(self):
        """Abre diálogo para crear nueva dieta"""
        dialog = DietDialog(self, self.diet_controller)
        if dialog.result:
            self.refresh_diets()
    
    def edit_diet(self):
        """Abre diálogo para editar dieta seleccionada"""
        if not self.current_diet:
            messagebox.showwarning("Advertencia", "Seleccione una dieta para editar")
            return
        
        dialog = DietDialog(self, self.diet_controller, self.current_diet)
        if dialog.result:
            self.refresh_diets()
    
    def delete_diet(self):
        """Elimina la dieta seleccionada"""
        if not self.current_diet:
            messagebox.showwarning("Advertencia", "Seleccione una dieta para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta dieta?"):
            try:
                success = self.diet_controller.delete_diet(self.current_diet.id)
                if success:
                    messagebox.showinfo("Éxito", "Dieta eliminada correctamente")
                    self.refresh_diets()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la dieta")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def liquidate_diet(self):
        """Abre diálogo para liquidar dieta seleccionada"""
        if not self.current_diet:
            messagebox.showwarning("Advertencia", "Seleccione una dieta para liquidar")
            return
        
        dialog = DietLiquidationDialog(self, self.diet_controller, self.current_diet)
        if dialog.result:
            self.refresh_diets()
    
    def manage_members(self):
        """Abre diálogo para gestionar miembros de dieta grupal"""
        if not self.current_diet or not self.current_diet.is_group:
            messagebox.showwarning("Advertencia", "Seleccione una dieta grupal")
            return
        
        dialog = DietMemberDialog(self, self.diet_controller, self.current_diet)
        if dialog.result:
            self.refresh_diets()
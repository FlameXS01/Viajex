import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from application.dtos.diet_dtos import DietResponseDTO, DietLiquidationResponseDTO
from application.services.card_service import CardService
from application.services.diet_service import DietAppService
from core.entities.enums import DietStatus
from .widgets.diet_list import DietList
from .widgets.diet_actions import DietActions
from .dialogs.diet_dialog import DietDialog
from .dialogs.diet_liquidation_dialog import DietLiquidationDialog


class DietModule(ttk.Frame):
    """
    Módulo principal de gestión de dietas
    """
    
    def __init__(self, parent, diet_service: DietAppService, request_user_service, card_service: CardService, **kwargs):
        super().__init__(parent, **kwargs)
        self.diet_service = diet_service
        self.current_item: Optional[DietResponseDTO | DietLiquidationResponseDTO] = None
        self.request_user_service = request_user_service
        self.card_service = card_service
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
        """
        # AGREGAR BOTÓN GESTIONAR SERVICIOS aquí
        services_button = ttk.Button(controls_frame, text="⚙️ Gestionar Servicios", command=self._manage_services, width=18)
        services_button.pack(side=tk.RIGHT, padx=(10, 0))
        """
        
        # Frame de contenido
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de all
        self.all_diets_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.all_diets_frame, text="Todas")

        # Pestaña de anticipos
        self.advances_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advances_frame, text="Anticipos")
        
        # Pestaña de liquidaciones
        self.liquidations_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.liquidations_frame, text="Liquidaciones")
        
        # Lista de anticipos
        self.advances_list = DietList(self.advances_frame, "advances", self.request_user_service, self.diet_service)
        self.advances_list.pack(fill=tk.BOTH, expand=True)
        self.advances_list.bind_selection(self.on_diet_selected)
        
        # Lista de liquidaciones
        self.liquidations_list = DietList(self.liquidations_frame, "liquidations", self.request_user_service, self.diet_service)
        self.liquidations_list.pack(fill=tk.BOTH, expand=True)
        self.liquidations_list.bind_selection(self.on_liquidation_selected)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.advances_list.tree.bind("<Double-1>", lambda e: self.on_double_click())
        self.liquidations_list.tree.bind("<Double-1>", lambda e: self.on_double_click())
        if hasattr(self, 'all_list'):
            self.all_list.tree.bind("<Double-1>", lambda e: self.on_double_click())
       
        try:
            # Lista de liquidaciones
            self.all_list = DietList(self.all_diets_frame, "all", self.request_user_service, self.diet_service)
            self.all_list.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            import traceback
            traceback.print_exc()

    def on_double_click(self):
        """Maneja el doble clic en cualquier lista"""
        self.show_selected_details()

    def on_tab_changed(self, event=None):
        """Se ejecuta cuando el usuario cambia de pestaña """
        self.current_item = None
        self.actions_widget.update_buttons_state(None)
        
        # Limpiar selecciones visuales en todas las listas
        self.advances_list.clear_selection()
        self.liquidations_list.clear_selection()
        if hasattr(self, 'all_list'):
            self.all_list.clear_selection()

    def show_selected_details(self):
        """Muestra los detalles del elemento seleccionado en la pestaña activa"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Pestaña "Todas"
            selected_item = self.all_list.get_selected_item()
        elif current_tab == 1:  # Pestaña "Anticipos"  
            selected_item = self.advances_list.get_selected_item()
        elif current_tab == 2:  # Pestaña "Liquidaciones"
            selected_item = self.liquidations_list.get_selected_item()
        else:
            selected_item = None
        
        if selected_item:
            self.show_item_details(selected_item)
        else:
            messagebox.showinfo("Información", "Seleccione un elemento para ver los detalles")

    def show_item_details(self, item):
        """Muestra los detalles de un item (dieta o liquidación)"""
        # Detectar si es dieta o liquidación
        if hasattr(item, 'liquidation_number'):
            # Es una liquidación
            from .dialogs.liquidation_info_dialog import LiquidationInfoDialog
            dialog = LiquidationInfoDialog(self, self.diet_service, self.request_user_service, self.card_service, item)
        else:
            # Es una dieta
            from .dialogs.diet_info_dialog import DietInfoDialog
            dialog = DietInfoDialog(self, self.diet_service, self.request_user_service, self.card_service, item)
        
        self.wait_window(dialog)
        
    def refresh_diets(self):
        """Actualiza las listas de dietas y liquidaciones"""
        try:
            # Obtener todas
            diets = self.diet_service.get_all()                                                        # type: ignore
            self.all_list.update_data(diets, type=0)
            
            # Obtener anticipos
            diets = self.diet_service.list_diets(status=DietStatus.REQUESTED)                          # type: ignore
            self.advances_list.update_data(diets, type=1)
            
            # Obtener liquidaciones
            liquidations = self.diet_service.list_all_liquidations()                  
            self.liquidations_list.update_data(liquidations,  type=2)

            self.actions_widget.refresh_counters()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_diet_selected(self, diet: DietResponseDTO):
        """Maneja la selección de una dieta"""
        self.current_item = diet
        self.actions_widget.update_buttons_state(diet)
    
    def on_liquidation_selected(self, liquidation: DietLiquidationResponseDTO):     
        """Maneja la selección de una liquidación"""
        self.current_item = liquidation
        self.actions_widget.update_buttons_state(liquidation)
    
    def create_diet(self):
        """Abre diálogo para crear nueva dieta"""
        dialog = DietDialog(self, self.diet_service, self.request_user_service, self.card_service)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_diets()
    
    def edit_item(self):
        """Abre diálogo para editar seleccionada"""
        if not self.current_item:
            messagebox.showwarning("Advertencia", "Seleccione una dieta para editar")
            return
        
        if hasattr(self.current_item, 'liquidation_number'):
            self.edit_liquidation()
        else:
            self.edit_diet()
    
    def edit_diet(self):
        """Abre diálogo para editar dieta seleccionada"""
        if not self.current_item or hasattr(self.current_item, 'liquidation_number'):
            messagebox.showwarning("Advertencia", "Seleccione una dieta para editar")
            return
        
        dialog = DietDialog(self, self.diet_service, self.request_user_service, self.card_service, self.current_item)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_diets()
            self.current_item = None
            self.actions_widget.update_buttons_state(None)
            self.advances_list.clear_selection()

    def edit_liquidation(self):
        """Abre diálogo para editar liquidación seleccionada"""
        if not self.current_item or not hasattr(self.current_item, 'liquidation_number'):
            messagebox.showwarning("Advertencia", "Seleccione una liquidación para editar")
            return
        
        # Obtener la dieta original asociada a la liquidación
        try:
            diet = self.diet_service.get_diet(self.current_item.id)  
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener la dieta asociada: {str(e)}")
            return
        
        dialog = DietLiquidationDialog(
            self, 
            self.diet_service, 
            diet,
            self.card_service, 
            self.diet_service,
            liquidation=self.current_item  
        )
        self.wait_window(dialog)
        
        if dialog.result:
            self.refresh_diets()
            self.current_item = None
            self.actions_widget.update_buttons_state(None)
            self.liquidations_list.clear_selection()

    def _manage_services(self):
        """Abre la gestión de servicios de dieta"""
        try:
            from presentation.gui.diet_presentation.dialogs.diet_services_dialog import DietServicesDialog
            
            dialog = DietServicesDialog(self.winfo_toplevel(), self.diet_service)
            self.wait_window(dialog)
            
            if hasattr(dialog, 'result') and dialog.result:
                self.refresh_diets()
                
        except ImportError as e:
            messagebox.showerror("Error", f"No se encontró el módulo de servicios: {str(e)}")
            messagebox.showinfo("Información", "Funcionalidad de Gestión de Servicios en desarrollo")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la gestión de servicios: {str(e)}")

    def delete_item(self):
        """Elimina el elemento seleccionado (dieta o liquidación)"""
        if not self.current_item:
            messagebox.showwarning("Advertencia", "Seleccione un elemento para eliminar")
            return
        
        if hasattr(self.current_item, 'liquidation_number'):
            self.delete_liquidation()
        else:
            self.delete_diet()
    
    def delete_diet(self):
        """Elimina la dieta seleccionada"""
        if not self.current_item or hasattr(self.current_item, 'liquidation_number'):
            messagebox.showwarning("Advertencia", "Seleccione una dieta para eliminar")
            return
        
        # Confirmar eliminación
        confirmation = messagebox.askyesno(
            "Confirmar eliminación", 
            "¿Está seguro de que desea eliminar esta dieta?\n\n"
            "Esta acción no se puede deshacer."
        )
        
        if not confirmation:
            return
        
        try:
            success = self.diet_service.delete_diet(self.current_item.id)
            if success:
                messagebox.showinfo("Éxito", "Dieta eliminada correctamente")
                self.refresh_diets()
                self.current_item = None
                self.actions_widget.update_buttons_state(None)
                # Limpiar selección en la lista correspondiente
                self.advances_list.clear_selection()
                if hasattr(self, 'all_list'):
                    self.all_list.clear_selection()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la dieta")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar la dieta: {str(e)}")

    def delete_liquidation(self):
        """Elimina la liquidación seleccionada"""
        if not self.current_item or not hasattr(self.current_item, 'liquidation_number'):
            messagebox.showwarning("Advertencia", "Seleccione una liquidación para eliminar")
            return
        
        # Confirmar eliminación (puedes personalizar el mensaje para liquidaciones)
        confirmation = messagebox.askyesno(
            "Confirmar eliminación", 
            "¿Está seguro de que desea eliminar esta liquidación?\n\n"
            "Esta acción eliminará todos los registros de liquidación asociados.\n"
            "Esta acción no se puede deshacer."
        )
        
        if not confirmation:
            return
        
        try:
            # Asumiendo que el servicio tiene un método delete_liquidation
            success = self.diet_service.delete_diet_liquidation(self.current_item.id)
            if success:
                # if self.current_item.accommodation_payment_method=='card': 
                #     self.card_service.recharge_card(,)
                    
                messagebox.showinfo("Éxito", "Liquidación eliminada correctamente")
                self.refresh_diets()
                self.current_item = None
                self.actions_widget.update_buttons_state(None)
                # Limpiar selección en la lista correspondiente
                self.liquidations_list.clear_selection()
                if hasattr(self, 'all_list'):
                    self.all_list.clear_selection()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la liquidación")
        except AttributeError:
            # Si el servicio no tiene método específico para liquidaciones
            try:
                # Alternativa: usar un método genérico o eliminar la dieta asociada
                success = self.diet_service.delete_diet(self.current_item.id)
                if success:
                    messagebox.showinfo("Éxito", "Liquidación eliminada correctamente")
                    self.refresh_diets()
                    self.current_item = None
                    self.actions_widget.update_buttons_state(None)
                    self.liquidations_list.clear_selection()
                    if hasattr(self, 'all_list'):
                        self.all_list.clear_selection()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la liquidación")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar la liquidación: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar la liquidación: {str(e)}")
    
    def liquidate_diet(self):
        """Abre diálogo para liquidar dieta seleccionada"""
        if not self.current_item:
            messagebox.showwarning("Advertencia", "Seleccione una dieta para liquidar")
            return
        
        dialog = DietLiquidationDialog(self, self.diet_service, self.current_item, self.card_service, self.diet_service)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_diets()
            self.current_diet = None
            self.actions_widget.update_buttons_state(None)
            self.advances_list.clear_selection()
    
    def get_counters_info(self):
        """Obtiene información de contadores para el widget de acciones"""
        try:
            advances_count = len(self.diet_service.list_diets(status=DietStatus.REQUESTED) or [])
            liquidations_count = len(self.diet_service.list_diets(status=DietStatus.LIQUIDATED) or [])
            
            return type('Counters', (), {
                'total_advance_number': advances_count,
                'total_liquidation_number': liquidations_count
            })()
        except Exception as e:
            print(f"Error obteniendo contadores: {e}")
            return type('Counters', (), {
                'total_advance_number': 0,
                'total_liquidation_number': 0
            })()
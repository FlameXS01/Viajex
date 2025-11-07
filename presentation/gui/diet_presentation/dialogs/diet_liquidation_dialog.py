import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from application.dtos.diet_dtos import DietLiquidationCreateDTO

class DietLiquidationDialog(tk.Toplevel):
    """
    Diálogo para liquidar una dieta
    """
    
    def __init__(self, parent, diet_controller, diet):
        super().__init__(parent)
        self.diet_controller = diet_controller
        self.diet = diet
        self.result = False
        
        self.title(f"Liquidar Dieta #{diet.advance_number}")
        self.geometry("500x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información del anticipo
        info_frame = ttk.LabelFrame(main_frame, text="Información del Anticipo", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Descripción: {self.diet.description}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Fechas: {self.diet.start_date} a {self.diet.end_date}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Monto anticipado: ${self.diet.total_amount:.2f}").pack(anchor=tk.W)
        
        # Servicios a liquidar
        services_frame = ttk.LabelFrame(main_frame, text="Servicios a Liquidar", padding=10)
        services_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Crear tabla comparativa
        columns = ["Servicio", "Solicitado", "Liquidar"]
        tree = ttk.Treeview(services_frame, columns=columns, show="headings", height=4)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Datos de servicios
        services_data = [
            ("Desayunos", self.diet.breakfast_count),
            ("Almuerzos", self.diet.lunch_count),
            ("Comidas", self.diet.dinner_count),
            ("Alojamientos", self.diet.accommodation_count)
        ]
        
        self.liquidation_vars = {}
        for i, (service, requested) in enumerate(services_data):
            var = tk.IntVar(value=requested)
            tree.insert("", "end", values=(service, requested, requested))
            self.liquidation_vars[service.lower()] = var
        
        tree.pack(fill=tk.X)
        
        # Frame para editar cantidades
        edit_frame = ttk.Frame(services_frame)
        edit_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(edit_frame, text="Desayunos:").grid(row=0, column=0, padx=(0, 5))
        breakfast_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.breakfast_count, 
                                   textvariable=self.liquidation_vars["desayunos"], width=10)
        breakfast_spin.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(edit_frame, text="Almuerzos:").grid(row=0, column=2, padx=(0, 5))
        lunch_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.lunch_count,
                               textvariable=self.liquidation_vars["almuerzos"], width=10)
        lunch_spin.grid(row=0, column=3, padx=(0, 15))
        
        ttk.Label(edit_frame, text="Comidas:").grid(row=1, column=0, padx=(0, 5))
        dinner_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.dinner_count,
                                textvariable=self.liquidation_vars["comidas"], width=10)
        dinner_spin.grid(row=1, column=1, padx=(0, 15))
        
        ttk.Label(edit_frame, text="Alojamientos:").grid(row=1, column=2, padx=(0, 5))
        accommodation_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.accommodation_count,
                                       textvariable=self.liquidation_vars["alojamientos"], width=10)
        accommodation_spin.grid(row=1, column=3, padx=(0, 15))
        
        # Método de pago
        payment_frame = ttk.LabelFrame(main_frame, text="Método de Pago Alojamiento", padding=10)
        payment_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.payment_method_var = tk.StringVar(value=self.diet.accommodation_payment_method)
        ttk.Radiobutton(payment_frame, text="Efectivo", 
                       variable=self.payment_method_var, value="CASH").pack(anchor=tk.W)
        ttk.Radiobutton(payment_frame, text="Tarjeta", 
                       variable=self.payment_method_var, value="CARD").pack(anchor=tk.W)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Liquidar", command=self.on_liquidate).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)
    
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
    
    def on_liquidate(self):
        try:
            # Validar que no se excedan las cantidades solicitadas
            if (self.liquidation_vars["desayunos"].get() > self.diet.breakfast_count or
                self.liquidation_vars["almuerzos"].get() > self.diet.lunch_count or
                self.liquidation_vars["comidas"].get() > self.diet.dinner_count or
                self.liquidation_vars["alojamientos"].get() > self.diet.accommodation_count):
                messagebox.showwarning("Validación", "Las cantidades liquidadas no pueden exceder las solicitadas")
                return
            
            create_dto = DietLiquidationCreateDTO(
                diet_id=self.diet.id,
                liquidation_date=datetime.now(),
                breakfast_count_liquidated=self.liquidation_vars["desayunos"].get(),
                lunch_count_liquidated=self.liquidation_vars["almuerzos"].get(),
                dinner_count_liquidated=self.liquidation_vars["comidas"].get(),
                accommodation_count_liquidated=self.liquidation_vars["alojamientos"].get(),
                accommodation_payment_method=self.payment_method_var.get(),
                diet_service_id=self.diet.diet_service_id,
                accommodation_card_id=self.diet.accommodation_card_id
            )
            
            result = self.diet_controller.create_diet_liquidation(create_dto)
            if result:
                self.result = True
                messagebox.showinfo("Éxito", "Dieta liquidada correctamente")
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo liquidar la dieta")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al liquidar: {str(e)}")
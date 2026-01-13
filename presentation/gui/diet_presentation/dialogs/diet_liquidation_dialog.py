import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from application.dtos.diet_dtos import DietLiquidationCreateDTO, DietLiquidationUpdateDTO
from application.services.card_service import CardService
from application.services.diet_service import DietAppService

class DietLiquidationDialog(tk.Toplevel):

    def __init__(self, parent, diet_controller, diet, card_service: CardService, 
                 diet_service: DietAppService, liquidation=None):
        super().__init__(parent)
        self.diet_controller = diet_controller
        self.liquidation = liquidation  
        self.result = False
        self.card_service = card_service
        self.diet_service = diet_service
        self.diet = diet if diet else self.diet_service.get_diet(liquidation.diet_id)
        self.mode = "edit" if liquidation else "create"
        
        self.liquidation_date_var = tk.StringVar()
        # Obtener el servicio de dieta
        self.diet_service_obj = self.diet_service.get_diet_service_by_local(self.diet.is_local)
        
        # Precio original de alojamiento
        self.original_accommodation_price = self._get_accommodation_unit_price()
        
        # Determinar si se usó precio manual en la liquidación anterior
        self.manual_price_used = False
        self.previous_accommodation_unit_price = self.original_accommodation_price
        
        if self.mode == "edit" and liquidation:
            if liquidation.accommodation_count_liquidated > 0:
                # Calcular el precio unitario que se usó anteriormente
                self.previous_accommodation_unit_price = liquidation.total_pay / liquidation.accommodation_count_liquidated
                
                # Verificar si difiere del precio original (indica precio manual)
                if abs(self.previous_accommodation_unit_price - self.original_accommodation_price) > 0.01:
                    self.manual_price_used = True

        if self.mode == "edit":
            self.title(f"Editar Liquidación #{liquidation.liquidation_number}")
        else:
            self.title(f"Liquidar Dieta #{diet.advance_number}")
            
        self.geometry("500x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
    
    def _get_accommodation_unit_price(self):
        """Obtiene el precio unitario de alojamiento según configuración"""
        if not self.diet_service_obj:
            return 0.0
        
        if self.diet.accommodation_payment_method == "card":
            return self.diet_service_obj.accommodation_card_price
        else:
            return self.diet_service_obj.accommodation_cash_price
    
    def calculate_accommodation_total(self, accommodation_count):
        """Calcula el total de alojamiento (esto es lo que se guarda en total_pay)"""
        if self.use_manual_price_var.get() and self.diet.accommodation_payment_method == "card":
            # Usar precio manual
            unit_price = self.manual_price_var.get()
        else:
            # Usar precio automático
            unit_price = self._get_accommodation_unit_price()
        
        return accommodation_count * unit_price
    
    def calculate_total(self, breakfast_count, lunch_count, dinner_count, accommodation_count):
        """Calcula el total general (todos los servicios) para mostrar al usuario"""
        try:
            if not self.diet_service_obj:
                return 0.0
            
            # Calcular total de comidas
            breakfast_total = breakfast_count * self.diet_service_obj.breakfast_price
            lunch_total = lunch_count * self.diet_service_obj.lunch_price
            dinner_total = dinner_count * self.diet_service_obj.dinner_price
            
            # Calcular total de alojamiento
            accommodation_total = self.calculate_accommodation_total(accommodation_count)
            
            # Total general = comidas + alojamiento
            total = breakfast_total + lunch_total + dinner_total + accommodation_total
            
            return total
            
        except Exception as e:
            return 0.0

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información del anticipo
        info_frame = ttk.LabelFrame(main_frame, text="Información del Anticipo", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text=f"Descripción: {self.diet.description}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Inicio: {self.diet.start_date} Fin: {self.diet.end_date}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Solicitado: {self.diet.created_at}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Método pago alojamiento: {self.diet.accommodation_payment_method}").pack(anchor=tk.W)
        
        liquidation_date_frame = ttk.Frame(info_frame)
        liquidation_date_frame.pack(anchor=tk.W, pady=(5, 0))
        
        ttk.Label(liquidation_date_frame, text="Fecha liquidación:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

        if self.mode == "edit" and self.liquidation:
            liquidation_date_str = self.liquidation.liquidation_date.strftime("%d/%m/%Y")
        else:
            liquidation_date_str = datetime.now().strftime("%d/%m/%Y")
        
        self.liquidation_date_var.set(liquidation_date_str)
        
        self.liquidation_date_entry = ttk.Entry(
            liquidation_date_frame,
            textvariable=self.liquidation_date_var,
            width=12,
            font=('Arial', 9)
        )
        self.liquidation_date_entry.grid(row=0, column=1, sticky=tk.W)

        # Determinar valores iniciales
        if self.mode == "edit" :
            breakfast_init = self.liquidation.breakfast_count_liquidated
            lunch_init = self.liquidation.lunch_count_liquidated
            dinner_init = self.liquidation.dinner_count_liquidated
            accommodation_init = self.liquidation.accommodation_count_liquidated
        else:
            breakfast_init = self.diet.breakfast_count
            lunch_init = self.diet.lunch_count
            dinner_init = self.diet.dinner_count
            accommodation_init = self.diet.accommodation_count
        
        # Calcular monto total inicial
        initial_total = self.calculate_total(
            breakfast_init,
            lunch_init,
            dinner_init,
            accommodation_init
        )
        
        # Variable para el monto total
        self.total_var = tk.StringVar(value=f"Monto total a liquidar: ${initial_total:.2f}")
        total_label = ttk.Label(info_frame, textvariable=self.total_var, font=('Arial', 10, 'bold'))
        total_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Servicios a liquidar
        services_frame = ttk.LabelFrame(main_frame, text="Servicios a Liquidar", padding=10)
        services_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Variables para los Spinbox
        self.liquidation_vars = {
            "desayunos": tk.IntVar(value=breakfast_init),
            "almuerzos": tk.IntVar(value=lunch_init),
            "comidas": tk.IntVar(value=dinner_init),
            "alojamientos": tk.IntVar(value=accommodation_init)
        }
        
        # Configurar trace para actualizar total
        for var in self.liquidation_vars.values():
            var.trace_add("write", self.update_total)
        
        # Frame para editar cantidades
        edit_frame = ttk.Frame(services_frame)
        edit_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Desayunos
        ttk.Label(edit_frame, text="Desayunos:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        breakfast_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.breakfast_count, 
                                   textvariable=self.liquidation_vars["desayunos"], width=10,
                                   command=self.update_total)
        breakfast_spin.grid(row=0, column=1, padx=(0, 15), pady=5)
        
        # Almuerzos
        ttk.Label(edit_frame, text="Almuerzos:").grid(row=0, column=2, padx=(0, 5), pady=5, sticky=tk.W)
        lunch_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.lunch_count,
                               textvariable=self.liquidation_vars["almuerzos"], width=10,
                               command=self.update_total)
        lunch_spin.grid(row=0, column=3, padx=(0, 15), pady=5)
        
        # Comidas
        ttk.Label(edit_frame, text="Comidas:").grid(row=1, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        dinner_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.dinner_count,
                                textvariable=self.liquidation_vars["comidas"], width=10,
                                command=self.update_total)
        dinner_spin.grid(row=1, column=1, padx=(0, 15), pady=5)
        
        # Alojamientos
        ttk.Label(edit_frame, text="Alojamientos:").grid(row=1, column=2, padx=(0, 5), pady=5, sticky=tk.W)
        accommodation_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.accommodation_count,
                                       textvariable=self.liquidation_vars["alojamientos"], width=10,
                                       command=self.update_total)
        accommodation_spin.grid(row=1, column=3, padx=(0, 15), pady=5)
        
        # Frame para precio manual de alojamiento
        price_frame = ttk.Frame(services_frame)
        price_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Variable para controlar si se usa precio manual
        self.use_manual_price_var = tk.BooleanVar(value=False)
        
        # Determinar estado inicial del precio manual
        can_use_manual = (self.diet.accommodation_payment_method == "card")
        
        # RadioButton para activar/desactivar precio manual
        manual_price_radio = ttk.Radiobutton(
            price_frame, 
            variable=self.use_manual_price_var, 
            value=True,
            command=self.toggle_manual_price,
            state="normal" if can_use_manual else "disabled"
        )
        manual_price_radio.grid(row=0, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        
        # Label para precio manual
        manual_label = ttk.Label(price_frame, text="Precio manual/alojamiento:")
        manual_label.grid(row=0, column=1, padx=(0, 5), pady=5, sticky=tk.W)
        
        # Variable para el precio manual
        self.manual_price_var = tk.DoubleVar(value=0.0)
        
        # Entry para precio manual (inicialmente deshabilitado)
        self.manual_price_entry = ttk.Entry(
            price_frame, 
            textvariable=self.manual_price_var, 
            width=10,
            state="disabled"
        )
        self.manual_price_entry.grid(row=0, column=2, padx=(0, 5), pady=5, sticky=tk.W)
        
        # Configurar trace para actualizar total cuando cambie el precio manual
        self.manual_price_var.trace_add("write", self.update_total)
        
        # Label para mostrar el precio original (referencia)
        price_ref_label = ttk.Label(price_frame, 
                 text=f"(Precio original: ${self.original_accommodation_price:.2f})",
                 font=('Arial', 8),
                 foreground='gray')
        price_ref_label.grid(row=0, column=3, padx=(5, 0), pady=5, sticky=tk.W)
        
        # Deshabilitar elementos si no se puede usar precio manual
        if not can_use_manual:
            manual_label.config(state="disabled")
            price_ref_label.config(state="disabled")
        
        # Información de límites
        limits_frame = ttk.Frame(services_frame)
        limits_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(limits_frame, text=f"Límites: Desayunos({self.diet.breakfast_count}), "
                                   f"Almuerzos({self.diet.lunch_count}), "
                                   f"Comidas({self.diet.dinner_count}), "
                                   f"Alojamientos({self.diet.accommodation_count})",
                font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        if self.mode == "edit":
            ttk.Button(buttons_frame, text="Actualizar", command=self.on_update).pack(side=tk.RIGHT, padx=(5, 0))
        else:
            ttk.Button(buttons_frame, text="Liquidar", command=self.on_liquidate).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(buttons_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)
        
        # Si estamos en modo edición y se usó precio manual anteriormente, activarlo
        if self.mode == "edit" and self.manual_price_used:
            self.use_manual_price_var.set(True)
            self.toggle_manual_price()
            # Establecer el precio manual que se usó
            self.manual_price_var.set(round(self.previous_accommodation_unit_price, 2))
                
    def toggle_manual_price(self):
        """Habilita o deshabilita el campo de precio manual"""
        if self.use_manual_price_var.get():
            # Validar que se puede usar precio manual
            if self.diet.accommodation_payment_method != "card":
                messagebox.showwarning(
                    "Precio Manual No Disponible",
                    "El precio manual solo está disponible cuando el método de pago es TARJETA."
                )
                self.use_manual_price_var.set(False)
                return
            
            self.manual_price_entry.config(state="normal")
            # Establecer el precio original como valor inicial si no hay valor
            if self.manual_price_var.get() == 0.0:
                self.manual_price_var.set(self.original_accommodation_price)
        else:
            self.manual_price_entry.config(state="disabled")
            self.manual_price_var.set(0.0)
        
        # Actualizar el total
        self.update_total()
    
    def validate_manual_price(self):
        """Valida que el precio manual sea válido"""
        if self.use_manual_price_var.get():
            if self.diet.accommodation_payment_method != "card":
                messagebox.showwarning(
                    "Validación Fallida",
                    "El precio manual solo se puede usar cuando el método de pago es TARJETA."
                )
                return False
            
            manual_price = self.manual_price_var.get()
            if manual_price > self.original_accommodation_price:
                messagebox.showwarning(
                    "Validación Fallida",
                    f"El precio manual (${manual_price:.2f}) no puede exceder "
                    f"el precio original (${self.original_accommodation_price:.2f})."
                )
                return False
            
            if manual_price <= 0:
                messagebox.showwarning(
                    "Validación Fallida",
                    "El precio manual debe ser mayor que cero."
                )
                return False
        
        return True
    
    def on_liquidate(self):
        """Crear nueva liquidación"""
        try:
            # Validar cantidades
            if (self.liquidation_vars["desayunos"].get() > self.diet.breakfast_count or
                self.liquidation_vars["almuerzos"].get() > self.diet.lunch_count or
                self.liquidation_vars["comidas"].get() > self.diet.dinner_count or
                self.liquidation_vars["alojamientos"].get() > self.diet.accommodation_count):
                messagebox.showwarning("Validación", "Las cantidades liquidadas no pueden exceder las solicitadas")
                return
            
            # Validar precio manual
            if not self.validate_manual_price():
                return
            
            liquidation_date_str = self.liquidation_date_var.get()
            try:
                liquidation_date = datetime.strptime(liquidation_date_str, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/AAAA")
            
            # Calcular total de alojamiento (esto es lo que se guarda en total_pay)
            accommodation_total = self.calculate_accommodation_total(
                self.liquidation_vars["alojamientos"].get()
            )
            

            # Crear DTO - IMPORTANTE: total_pay es solo el total de alojamiento
            create_dto = DietLiquidationCreateDTO(
                diet_id=self.diet.id,
                liquidation_date=liquidation_date,
                breakfast_count_liquidated=self.liquidation_vars["desayunos"].get(),
                lunch_count_liquidated=self.liquidation_vars["almuerzos"].get(),
                dinner_count_liquidated=self.liquidation_vars["comidas"].get(),
                accommodation_count_liquidated=self.liquidation_vars["alojamientos"].get(),
                accommodation_payment_method=self.diet.accommodation_payment_method,
                diet_service_id=self.diet.diet_service_id,
                accommodation_card_id=self.diet.accommodation_card_id,
                total_pay=accommodation_total 
            )
            
            # Crear liquidación
            result = self.diet_controller.create_diet_liquidation(create_dto)
            if not result:
                messagebox.showerror("Error", "No se pudo liquidar la dieta")
                return
            
            # Aplicar descuento si es con tarjeta
            if self.diet.accommodation_payment_method.upper() == 'CARD' and self.diet.accommodation_card_id:
                self.card_service.discount_card(self.diet.accommodation_card_id, accommodation_total)
                
                # Verificar si la tarjeta sigue en viaje
                if not self.diet_service.card_on_the_road(self.diet.accommodation_card_id):
                    self.card_service.toggle_card_active(self.diet.accommodation_card_id)
            
            self.result = True
            messagebox.showinfo("Éxito", "Dieta liquidada correctamente")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al liquidar: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_update(self):
        """Actualizar liquidación existente"""

        try:
            # Validar cantidades
            if (self.liquidation_vars["desayunos"].get() > self.liquidation.breakfast_count_liquidated or
                self.liquidation_vars["almuerzos"].get() > self.liquidation.lunch_count_liquidated or
                self.liquidation_vars["comidas"].get() > self.liquidation.dinner_count_liquidated or
                self.liquidation_vars["alojamientos"].get() > self.liquidation.accommodation_count_liquidated):
                messagebox.showwarning("Validación", "Las cantidades liquidadas no pueden exceder las solicitadas ")
                return
            
            # Validar precio manual
            if not self.validate_manual_price():
                return
            
            liquidation_date_str = self.liquidation_date_var.get()
            try:
                liquidation_date = datetime.strptime(liquidation_date_str, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/AAAA")

            # Calcular nuevo total de alojamiento
            new_accommodation_total = self.calculate_accommodation_total(
                self.liquidation_vars["alojamientos"].get()
            )
            
            # Calcular diferencia para reembolso si es con tarjeta
            if (self.diet.accommodation_payment_method.upper() == 'CARD' and 
                self.diet.accommodation_card_id and
                self.liquidation):
                
                # Obtener precio unitario actual
                if self.use_manual_price_var.get():
                    current_unit_price = self.manual_price_var.get()
                else:
                    current_unit_price = self._get_accommodation_unit_price()
                
                # Calcular diferencia total
                # Diferencia = (nuevo_total_alojamiento) - (anterior_total_alojamiento)
                previous_accommodation_total = self.liquidation.total_pay  
                difference = new_accommodation_total - previous_accommodation_total
                
                
                if difference < 0:
                    # Reembolsar la diferencia (se redujo el gasto)
                    self.card_service.recharge_card(
                        self.diet.accommodation_card_id, 
                        abs(difference), 
                        is_refound=True
                    )
                elif difference > 0:
                    # Descontar la diferencia (se aumentó el gasto)
                    self.card_service.discount_card(
                        self.diet.accommodation_card_id, 
                        difference
                    )
                # Si difference == 0, no hacer nada
            
            # Crear DTO de actualización
            update_dto = DietLiquidationUpdateDTO(
                breakfast_count_liquidated=self.liquidation_vars["desayunos"].get(),
                lunch_count_liquidated=self.liquidation_vars["almuerzos"].get(),
                dinner_count_liquidated=self.liquidation_vars["comidas"].get(),
                accommodation_count_liquidated=self.liquidation_vars["alojamientos"].get(),
                accommodation_payment_method=self.diet.accommodation_payment_method.upper(),
                accommodation_card_id=self.diet.accommodation_card_id,
                liquidation_date=liquidation_date,
                total_pay=new_accommodation_total  # SOLO el nuevo total de alojamiento
            )
            
            # Actualizar liquidación
            result = self.diet_service.update_diet_liquidation(
                self.liquidation.liquidation_number,
                update_dto
            )
            
            if result:
                self.result = True
                messagebox.showinfo("Éxito", "Liquidación actualizada correctamente")
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la liquidación")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar liquidación: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def update_total(self, *args):
        """Actualiza el monto total cuando cambian las cantidades o precio manual"""
        try:
            breakfast_count = self.liquidation_vars["desayunos"].get()
            lunch_count = self.liquidation_vars["almuerzos"].get()
            dinner_count = self.liquidation_vars["comidas"].get()
            accommodation_count = self.liquidation_vars["alojamientos"].get()
            
            new_total = self.calculate_total(
                breakfast_count,
                lunch_count,
                dinner_count,
                accommodation_count
            )
            
            self.total_var.set(f"Monto total a liquidar: ${new_total:.2f}")
            
        except Exception as e:
            print(f"Error actualizando total: {e}")
    
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
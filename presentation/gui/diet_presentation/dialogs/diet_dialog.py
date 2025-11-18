import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from application.dtos.diet_dtos import DietCreateDTO, DietMemberCreateDTO, DietUpdateDTO
from application.services.diet_service import DietAppService
from ..widgets.diet_form import DietForm

class DietDialog(tk.Toplevel):
    def __init__(self, parent, diet_service: DietAppService, request_user_service, card_service, diet=None):
        super().__init__(parent)
        self.diet_service = diet_service
        self.diet = diet
        self.request_user_service = request_user_service
        self.card_service = card_service
        self.result = False
        
        title = "Editar Dieta" if diet else "Crear Dieta"
        self.title(title)
        
        # Configurar dimensiones fijas adecuadas
        self.geometry("900x875")  
        self.minsize(900, 875)   
        self.resizable(True, True)
        
        

        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
        
        # Asegurar que todos los elementos se muestren correctamente
        self.update_idletasks()
        
    def create_widgets(self):
        # Frame principal con scrollbar
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid para expansión
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        title_text = f"Editando Dieta #{self.diet.advance_number}" if self.diet else "Nueva Dieta"
        title_label = ttk.Label(main_frame, text=title_text, font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Frame para el formulario con tamaño fijo
        form_container = ttk.Frame(main_frame)
        form_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        form_container.columnconfigure(0, weight=1)
        form_container.rowconfigure(0, weight=1)
        
        self.form = DietForm(
            form_container, 
            self.request_user_service, 
            self.card_service,   
            self.diet_service,
            self.diet
        )
        self.form.pack(fill=tk.BOTH, expand=True)
        
        # Frame de precios
        prices_frame = ttk.LabelFrame(main_frame, text="Precios de Referencia", padding=10)
        prices_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        prices_frame.columnconfigure(0, weight=1)
        
        self.prices_label = ttk.Label(prices_frame, text="Seleccione 'Local' para ver precios")
        self.prices_label.pack(anchor=tk.W)
        
        # Frame del total
        total_frame = ttk.Frame(main_frame)
        total_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(total_frame, text="Total estimado:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="$0.00", font=("Arial", 10, "bold"))
        self.total_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame de botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, sticky=tk.E, pady=(10, 0))
        
        if self.diet:
            ttk.Button(buttons_frame, text="Guardar Cambios", command=self.on_save).pack(side=tk.RIGHT, padx=(5, 0))
        else:
            ttk.Button(buttons_frame, text="Crear Dieta", command=self.on_create).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(buttons_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)
        
        self.setup_calculation_events()
    
    def setup_calculation_events(self):
        for var in self.form.service_vars.values():
            var.trace_add("write", self.calculate_total)
        
        self.form.is_local_var.trace_add("write", self.on_local_changed)
        
        self.on_local_changed()
        self.calculate_total()

    def on_local_changed(self, *args):
        is_local = self.form.is_local_var.get()
        try:
            service = self.diet_service.get_diet_service_by_local(is_local)
            if service:
                self.prices_label.config(
                    text=f"Des: ${service.breakfast_price} | Alm: ${service.lunch_price} | "
                         f"Com: ${service.dinner_price} | Aloj: ${service.accommodation_cash_price} (Efectivo)"
                )
            else:
                self.prices_label.config(text="No hay precios configurados para esta localidad")
        except Exception as e:
            self.prices_label.config(text=f"Error al cargar precios: {str(e)}")

    def calculate_total(self, *args):
        try:
            is_local = self.form.is_local_var.get()
            service = self.diet_service.get_diet_service_by_local(is_local)
            
            if not service:
                self.total_label.config(text="$0.00")
                return
            
            form_data = self.form.get_form_data()
            breakfast_count = form_data["breakfast_count"]
            lunch_count = form_data["lunch_count"]
            dinner_count = form_data["dinner_count"]
            accommodation_count = form_data["accommodation_count"]
            
            total = (
                breakfast_count * service.breakfast_price +
                lunch_count * service.lunch_price +
                dinner_count * service.dinner_price +
                accommodation_count * service.accommodation_cash_price  
            )
            
            self.total_label.config(text=f"${total:.2f}")
            
        except Exception as e:
            self.total_label.config(text="$0.00")

    def center_on_parent(self, parent):
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2 - 70
        
        self.geometry(f"+{x}+{y}")

    def validate_form(self):
        try:
            data = self.form.get_form_data()
            
            if not data["description"].strip():
                messagebox.showwarning("Validación", "La descripción es obligatoria")
                return False
            
            try:
                start_date = datetime.strptime(data["start_date"], "%d/%m/%Y").date()
                end_date = datetime.strptime(data["end_date"], "%d/%m/%Y").date()
                
                if start_date > end_date:
                    messagebox.showwarning("Validación", "La fecha de inicio no puede ser posterior a la fecha fin")
                    return False
            except ValueError:
                messagebox.showwarning("Validación", "Formato de fecha inválido. Use DD/MM/AAAA")
                return False
            
            if (data["breakfast_count"] == 0 and data["lunch_count"] == 0 and 
                data["dinner_count"] == 0 and data["accommodation_count"] == 0):
                messagebox.showwarning("Validación", "Debe solicitar al menos un servicio")
                return False
            
            if not data.get("user_ids"):
                messagebox.showwarning("Validación", "Debe seleccionar al menos un usuario")
                return False
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error en validación: {str(e)}")
            return False

    def on_create(self):
        if not self.validate_form():
            return
        
        try:
            form_data = self.form.get_form_data()
            
            # Validar usuarios
            user_ids = form_data.get("user_ids", [])
            if not user_ids:
                messagebox.showwarning("Validación", "Debe seleccionar al menos un usuario")
                return
            
            diet_service_obj = self.diet_service.get_diet_service_by_local(form_data["is_local"])
            if not diet_service_obj:
                messagebox.showerror("Error", "No se encontró servicio de dieta para la localidad seleccionada")
                return
            
            # Usar el primer usuario como request_user_id
            request_user_id = user_ids[0]
            
            create_dto = DietCreateDTO(
                is_local=form_data["is_local"],
                start_date=datetime.strptime(form_data["start_date"], "%d/%m/%Y").date(),
                end_date=datetime.strptime(form_data["end_date"], "%d/%m/%Y").date(),
                description=form_data["description"],
                is_group=form_data["is_group"],
                request_user_id=request_user_id,
                diet_service_id=diet_service_obj.id,
                breakfast_count=form_data["breakfast_count"],
                lunch_count=form_data["lunch_count"],
                dinner_count=form_data["dinner_count"],
                accommodation_count=form_data["accommodation_count"],
                accommodation_payment_method=form_data["accommodation_payment_method"],
                accommodation_card_id=form_data["accommodation_card_id"]
            )
            
            # CREAR LA DIETA PRIMERO
            diet_id = self.diet_service.create_diet(create_dto).id
            
            if diet_id:
                if form_data["is_group"]:
                    for user_id in user_ids:
                        member_dto = DietMemberCreateDTO(
                            diet_id=diet_id,
                            request_user_id=user_id
                        )
                        self.diet_service.add_diet_member(member_dto)
                else:
                    member_dto = DietMemberCreateDTO(
                        diet_id=diet_id,
                        request_user_id=request_user_id
                    )
                    self.diet_service.add_diet_member(member_dto)
                
                self.result = True
                messagebox.showinfo("Éxito", "Dieta creada correctamente")
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear la dieta")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear dieta: {str(e)}")

    def on_save(self):
        if not self.validate_form():
            return
        
        try:
            form_data = self.form.get_form_data()
            
            # Validar usuarios
            user_ids = form_data.get("user_ids", [])
            if not user_ids:
                messagebox.showwarning("Validación", "Debe seleccionar al menos un usuario")
                return
            
            update_dto = DietUpdateDTO(
                start_date=datetime.strptime(form_data["start_date"], "%d/%m/%Y").date(),
                end_date=datetime.strptime(form_data["end_date"], "%d/%m/%Y").date(),
                description=form_data["description"],
                breakfast_count=form_data["breakfast_count"],
                lunch_count=form_data["lunch_count"],
                dinner_count=form_data["dinner_count"],
                accommodation_count=form_data["accommodation_count"],
                accommodation_payment_method=form_data["accommodation_payment_method"],
                accommodation_card_id=form_data["accommodation_card_id"]
            )
            
            # ACTUALIZAR LA DIETA
            result = self.diet_service.update_diet(self.diet.id, update_dto)    # type: ignore
            if result:
                messagebox.showinfo("Editado", f"Se editó la dieta satisfactoriamente")
                self.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar dieta: {str(e)}")
            import traceback
            traceback.print_exc()

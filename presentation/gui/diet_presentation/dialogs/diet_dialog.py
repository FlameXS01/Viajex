import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from application.dtos.diet_dtos import DietCreateDTO, DietUpdateDTO
from ..widgets.diet_form import DietForm

class DietDialog(tk.Toplevel):
    """
    Diálogo para crear/editar dietas
    """
    
    def __init__(self, parent, diet_controller, diet=None):
        super().__init__(parent)
        self.diet_controller = diet_controller
        self.diet = diet
        self.result = False
        
        title = "Editar Dieta" if diet else "Crear Dieta"
        self.title(title)
        self.geometry("600x600")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_text = f"Editando Dieta #{self.diet.advance_number}" if self.diet else "Nueva Dieta"
        title_label = ttk.Label(main_frame, text=title_text, font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        self.form = DietForm(form_frame, self.diet_controller, self.diet)
        self.form.pack(fill=tk.BOTH, expand=True)
        
        # Información de precios
        prices_frame = ttk.LabelFrame(main_frame, text="Precios de Referencia", padding=10)
        prices_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.prices_label = ttk.Label(prices_frame, text="Seleccione 'Local' para ver precios")
        self.prices_label.pack()
        
        # Total calculado
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(total_frame, text="Total estimado:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="$0.00", font=("Arial", 10, "bold"))
        self.total_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        if self.diet:
            ttk.Button(buttons_frame, text="Guardar Cambios", command=self.on_save).pack(side=tk.RIGHT, padx=(5, 0))
        else:
            ttk.Button(buttons_frame, text="Crear Dieta", command=self.on_create).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(buttons_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)
        
        # Configurar eventos para cálculo automático
        self.setup_calculation_events()
    
    def setup_calculation_events(self):
        """Configura eventos para calcular total automáticamente"""
        # Conectar eventos de cambio en los campos de cantidad
        for var in self.form.service_vars.values():
            var.trace_add("write", self.calculate_total)
        
        # Conectar evento de cambio en localidad
        self.form.is_local_var.trace_add("write", self.on_local_changed)
        
        # Calcular inicialmente
        self.on_local_changed()
        self.calculate_total()
    
    def on_local_changed(self, *args):
        """Cuando cambia la localidad, actualizar precios de referencia"""
        is_local = self.form.is_local_var.get()
        try:
            service = self.diet_controller.get_diet_service_by_local(is_local)
            if service:
                self.prices_label.config(
                    text=f"Des: ${service.breakfast_price} | Alm: ${service.lunch_price} | "
                         f"Com: ${service.dinner_price} | Aloj: ${service.accommodation_cash_price} (Efectivo)"
                )
            else:
                self.prices_label.config(text="No hay precios configurados para esta localidad")
        except Exception:
            self.prices_label.config(text="Error al cargar precios")
    
    def calculate_total(self, *args):
        """Calcula el total estimado basado en cantidades y precios"""
        try:
            is_local = self.form.is_local_var.get()
            service = self.diet_controller.get_diet_service_by_local(is_local)
            
            if not service:
                self.total_label.config(text="$0.00")
                return
            
            # Obtener cantidades
            breakfast_count = self.form.service_vars["breakfast_count"].get()
            lunch_count = self.form.service_vars["lunch_count"].get()
            dinner_count = self.form.service_vars["dinner_count"].get()
            accommodation_count = self.form.service_vars["accommodation_count"].get()
            
            # Calcular total
            total = (
                breakfast_count * service.breakfast_price +
                lunch_count * service.lunch_price +
                dinner_count * service.dinner_price +
                accommodation_count * service.accommodation_cash_price  # Por defecto efectivo
            )
            
            self.total_label.config(text=f"${total:.2f}")
            
        except Exception:
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
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def validate_form(self) -> bool:
        """Valida los datos del formulario"""
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
        
        # Validar que al menos un servicio tenga cantidad > 0
        if (data["breakfast_count"] == 0 and data["lunch_count"] == 0 and 
            data["dinner_count"] == 0 and data["accommodation_count"] == 0):
            messagebox.showwarning("Validación", "Debe solicitar al menos un servicio")
            return False
        
        return True
    
    def on_create(self):
        if not self.validate_form():
            return
        
        try:
            form_data = self.form.get_form_data()
            
            # Obtener el servicio de dieta según localidad
            diet_service = self.diet_controller.get_diet_service_by_local(form_data["is_local"])
            if not diet_service:
                messagebox.showerror("Error", "No se encontró servicio de dieta para la localidad seleccionada")
                return
            
            create_dto = DietCreateDTO(
                is_local=form_data["is_local"],
                start_date=datetime.strptime(form_data["start_date"], "%d/%m/%Y").date(),
                end_date=datetime.strptime(form_data["end_date"], "%d/%m/%Y").date(),
                description=form_data["description"],
                is_group=form_data["is_group"],
                request_user_id=1,  # Esto debería venir de un combobox de solicitantes
                diet_service_id=diet_service.id,
                breakfast_count=form_data["breakfast_count"],
                lunch_count=form_data["lunch_count"],
                dinner_count=form_data["dinner_count"],
                accommodation_count=form_data["accommodation_count"],
                accommodation_payment_method=form_data["accommodation_payment_method"],
                accommodation_card_id=form_data["accommodation_card_id"]
            )
            
            result = self.diet_controller.create_diet(create_dto)
            if result:
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
            
            result = self.diet_controller.update_diet(self.diet.id, update_dto)
            if result:
                self.result = True
                messagebox.showinfo("Éxito", "Dieta actualizada correctamente")
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la dieta")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar dieta: {str(e)}")
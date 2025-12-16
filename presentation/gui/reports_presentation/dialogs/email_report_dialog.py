"""
email_report_dialog.py
Diálogo para configurar el envío de reportes por correo electrónico.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from .base_report_dialog import BaseReportDialog


class EmailReportDialog(BaseReportDialog):
    """Diálogo para configurar envío de reportes por email"""
    
    def __init__(self, parent, 
                 report_name: str = "Reporte",
                 report_filepath: Optional[str] = None,
                 default_recipients: Optional[List[str]] = None,
                 email_templates: Optional[List[str]] = None):
        """
        Inicializa el diálogo para envío de reportes por email.
        
        Args:
            parent: Ventana padre
            report_name: Nombre del reporte a enviar
            report_filepath: Ruta del archivo del reporte
            default_recipients: Lista de destinatarios por defecto
            email_templates: Lista de plantillas de email disponibles
        """
        self.report_name = report_name
        self.report_filepath = report_filepath or f"{report_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Destinatarios de ejemplo del PDF
        self.default_recipients = default_recipients or [
            "jailerpc@cimex.com.cu",
            "kareng@cimex.com.cu",
            "daniel.lorenzo@cimex.com.cu"
        ]
        
        self.email_templates = email_templates or [
            "Estándar CIMEX",
            "Resumen ejecutivo",
            "Detallado con adjuntos",
            "Urgente - Revisión inmediata",
            "Informe mensual",
            "Personalizado"
        ]
        
        super().__init__(parent, f"Enviar {report_name} por Email", width=700, height=700)
    
    def _create_widgets(self) -> None:
        """Crea los widgets del diálogo."""
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar expansión
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título descriptivo
        ttk.Label(
            main_frame,
            text=f"Configurar Envío por Email: {self.report_name}",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Información del reporte
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        ttk.Label(
            info_frame,
            text="📧 Envíe este reporte por correo electrónico a los destinatarios seleccionados.",
            font=('Arial', 9)
        ).pack(anchor='w')
        
        ttk.Label(
            info_frame,
            text=f"Archivo: {self.report_filepath}",
            font=('Arial', 9, 'italic'),
            foreground='darkblue'
        ).pack(anchor='w', pady=(2, 0))
        
        # Sección de destinatarios
        recipients_frame = self._create_section(main_frame, "Destinatarios", 2)
        
        # Para (To)
        ttk.Label(recipients_frame, text="Para:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.to_var = tk.StringVar(value=", ".join(self.default_recipients[:2]))
        to_entry = ttk.Entry(
            recipients_frame,
            textvariable=self.to_var,
            width=50
        )
        to_entry.grid(row=0, column=1, sticky="w", pady=10)
        
        # Botón para seleccionar destinatarios
        ttk.Button(
            recipients_frame,
            text="📋 Seleccionar",
            command=self._select_recipients,
            width=12
        ).grid(row=0, column=2, padx=(10, 0), pady=10)
        
        # Copia (CC)
        ttk.Label(recipients_frame, text="Copia (CC):").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.cc_var = tk.StringVar()
        cc_entry = ttk.Entry(
            recipients_frame,
            textvariable=self.cc_var,
            width=50
        )
        cc_entry.grid(row=1, column=1, sticky="w", pady=10)
        
        # Copia oculta (BCC)
        ttk.Label(recipients_frame, text="Copia oculta (BCC):").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.bcc_var = tk.StringVar()
        bcc_entry = ttk.Entry(
            recipients_frame,
            textvariable=self.bcc_var,
            width=50
        )
        bcc_entry.grid(row=2, column=1, sticky="w", pady=10)
        
        # Lista de contactos frecuentes
        ttk.Label(recipients_frame, text="Contactos frecuentes:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        contacts_frame = ttk.Frame(recipients_frame)
        contacts_frame.grid(row=3, column=1, sticky="w", pady=10)
        
        # Checkboxes para contactos frecuentes
        self.contact_vars = {}
        for i, contact in enumerate(self.default_recipients):
            var = tk.BooleanVar(value=i < 2)  # Primeros 2 seleccionados por defecto
            self.contact_vars[contact] = var
            
            ttk.Checkbutton(
                contacts_frame,
                text=contact,
                variable=var,
                command=self._update_recipients_from_contacts
            ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Sección de contenido del email
        content_frame = self._create_section(main_frame, "Contenido del Email", 3)
        
        # Asunto
        ttk.Label(content_frame, text="Asunto:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.subject_var = tk.StringVar(value=f"Reporte: {self.report_name} - {datetime.now().strftime('%d/%m/%Y')}")
        subject_entry = ttk.Entry(
            content_frame,
            textvariable=self.subject_var,
            width=50
        )
        subject_entry.grid(row=0, column=1, sticky="w", pady=10)
        
        # Plantilla de email
        ttk.Label(content_frame, text="Plantilla:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.template_var = tk.StringVar(value=self.email_templates[0])
        template_combo = ttk.Combobox(
            content_frame,
            textvariable=self.template_var,
            values=self.email_templates,
            state='readonly',
            width=30
        )
        template_combo.grid(row=1, column=1, sticky="w", pady=10)
        template_combo.bind('<<ComboboxSelected>>', self._on_template_change)
        
        # Cuerpo del mensaje
        ttk.Label(content_frame, text="Cuerpo del mensaje:").grid(
            row=2, column=0, sticky="nw", padx=(0, 10), pady=10
        )
        
        # Área de texto con scroll para el cuerpo del email
        self.body_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            width=50,
            height=8,
            font=('Arial', 10)
        )
        self.body_text.grid(row=2, column=1, sticky="nsew", pady=10)
        
        # Cargar plantilla por defecto
        self._load_template()
        
        # Sección de adjuntos y opciones
        options_frame = self._create_section(main_frame, "Adjuntos y Opciones", 4)
        
        # Archivos adjuntos
        ttk.Label(options_frame, text="Archivos adjuntos:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        attachments_frame = ttk.Frame(options_frame)
        attachments_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        # Lista de archivos adjuntos
        self.attachments_listbox = tk.Listbox(
            attachments_frame,
            height=3,
            width=40
        )
        self.attachments_listbox.pack(side=tk.LEFT)
        
        # Agregar el reporte principal
        self.attachments_listbox.insert(0, f"📎 {self.report_filepath} (principal)")
        
        # Botones para adjuntos
        attach_btn_frame = ttk.Frame(attachments_frame)
        attach_btn_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(
            attach_btn_frame,
            text="Agregar",
            command=self._add_attachment,
            width=10
        ).pack(pady=(0, 5))
        
        ttk.Button(
            attach_btn_frame,
            text="Quitar",
            command=self._remove_attachment,
            width=10
        ).pack()
        
        # Opciones de envío
        ttk.Label(options_frame, text="Opciones de envío:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        options_checks_frame = ttk.Frame(options_frame)
        options_checks_frame.grid(row=1, column=1, sticky="w", pady=10)
        
        self.confirm_read_var = tk.BooleanVar(value=False)
        self.high_priority_var = tk.BooleanVar(value=False)
        self.save_copy_var = tk.BooleanVar(value=True)
        self.schedule_send_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(
            options_checks_frame,
            text="Solicitar confirmación de lectura",
            variable=self.confirm_read_var
        ).pack(anchor='w')
        
        ttk.Checkbutton(
            options_checks_frame,
            text="Alta prioridad",
            variable=self.high_priority_var
        ).pack(anchor='w')
        
        ttk.Checkbutton(
            options_checks_frame,
            text="Guardar copia en 'Enviados'",
            variable=self.save_copy_var
        ).pack(anchor='w')
        
        ttk.Checkbutton(
            options_checks_frame,
            text="Programar envío",
            variable=self.schedule_send_var,
            command=self._toggle_schedule_options
        ).pack(anchor='w')
        
        # Frame para programar envío
        self.schedule_frame = ttk.Frame(options_frame)
        self.schedule_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        ttk.Label(self.schedule_frame, text="Programar para:").pack(side=tk.LEFT)
        
        self.schedule_date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        ttk.Entry(
            self.schedule_frame,
            textvariable=self.schedule_date_var,
            width=12,
            state='readonly'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(
            self.schedule_frame,
            text="📅",
            command=self._select_schedule_date,
            width=3
        ).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(self.schedule_frame, text="a las").pack(side=tk.LEFT)
        
        self.schedule_hour_var = tk.StringVar(value="09")
        hour_combo = ttk.Combobox(
            self.schedule_frame,
            textvariable=self.schedule_hour_var,
            values=[f"{i:02d}" for i in range(24)],
            width=3,
            state='readonly'
        )
        hour_combo.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(self.schedule_frame, text=":").pack(side=tk.LEFT)
        
        self.schedule_minute_var = tk.StringVar(value="00")
        minute_combo = ttk.Combobox(
            self.schedule_frame,
            textvariable=self.schedule_minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 5)],
            width=3,
            state='readonly'
        )
        minute_combo.pack(side=tk.LEFT)
        
        # Ocultar frame de programación inicialmente
        self.schedule_frame.grid_remove()
        
        # Sección de vista previa
        preview_frame = self._create_section(main_frame, "Vista Previa del Email", 5)
        
        # Botón para vista previa
        ttk.Button(
            preview_frame,
            text="Ver Vista Previa Completa",
            command=self._show_email_preview,
            width=25
        ).pack(pady=10)
        
        # Información de resumen
        self.summary_var = tk.StringVar()
        ttk.Label(
            preview_frame,
            textvariable=self.summary_var,
            font=('Arial', 9),
            foreground='green'
        ).pack(pady=(0, 10))
        
        # Actualizar resumen inicial
        self._update_summary()
        
        # Frame para botones de acción
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            action_frame,
            text="Guardar como Borrador",
            command=self._save_as_draft,
            width=18
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_frame,
            text="Enviar Prueba",
            command=self._send_test,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_frame,
            text="Validar Destinatarios",
            command=self._validate_recipients,
            width=18
        ).pack(side=tk.LEFT)
        
        # Frame para botones principales
        self.button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        # Cambiar texto del botón Aceptar
        self.accept_button.config(text="Enviar Email")
        
        # Bind eventos para actualizar resumen
        self.to_var.trace_add('write', lambda *args: self._update_summary())
        self.subject_var.trace_add('write', lambda *args: self._update_summary())
        self.schedule_send_var.trace_add('write', lambda *args: self._update_summary())
    
    def _select_recipients(self) -> None:
        """Abre diálogo para seleccionar destinatarios."""
        # Crear ventana de selección
        select_window = tk.Toplevel(self)
        select_window.title("Seleccionar Destinatarios")
        select_window.transient(self)
        select_window.grab_set()
        
        # Configurar tamaño
        select_window.geometry("500x400")
        
        # Frame principal
        main_frame = ttk.Frame(select_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            main_frame,
            text="Seleccionar destinatarios del email",
            font=('Arial', 11, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        # Área de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=search_var, width=30).pack(side=tk.LEFT, padx=(5, 0))
        
        # Lista de contactos con checkboxes
        contacts_frame = ttk.Frame(main_frame)
        contacts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(contacts_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox para selección múltiple
        contacts_listbox = tk.Listbox(
            contacts_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            height=12
        )
        contacts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=contacts_listbox.yview)
        
        # Cargar contactos
        for contact in self.default_recipients:
            contacts_listbox.insert(tk.END, contact)
        
        # Seleccionar los que ya están en el campo "Para"
        current_to = self.to_var.get().split(", ")
        for i, contact in enumerate(self.default_recipients):
            if contact in current_to:
                contacts_listbox.selection_set(i)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def on_accept():
            # Obtener selección
            selected_indices = contacts_listbox.curselection()
            selected_contacts = [self.default_recipients[i] for i in selected_indices]
            
            # Actualizar campo "Para"
            self.to_var.set(", ".join(selected_contacts))
            
            # Actualizar checkboxes de contactos frecuentes
            for contact, var in self.contact_vars.items():
                var.set(contact in selected_contacts)
            
            select_window.destroy()
        
        ttk.Button(
            button_frame,
            text="Aceptar",
            command=on_accept,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=select_window.destroy,
            width=15
        ).pack(side=tk.LEFT)
        
        # Centrar ventana
        select_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (select_window.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (select_window.winfo_height() // 2)
        select_window.geometry(f"+{x}+{y}")
    
    def _update_recipients_from_contacts(self) -> None:
        """Actualiza el campo "Para" basado en los checkboxes de contactos."""
        selected_contacts = []
        for contact, var in self.contact_vars.items():
            if var.get():
                selected_contacts.append(contact)
        
        self.to_var.set(", ".join(selected_contacts))
    
    def _load_template(self) -> None:
        """Carga la plantilla de email seleccionada."""
        template = self.template_var.get()
        
        # Limpiar área de texto
        self.body_text.delete(1.0, tk.END)
        
        # Cargar plantilla según selección
        if template == "Estándar CIMEX":
            body = f"""Estimado/a destinatario/a,

Adjunto encontrará el reporte "{self.report_name}" generado el {datetime.now().strftime('%d/%m/%Y')}.

Este reporte contiene la información solicitada sobre tarjetas, anticipos y liquidaciones correspondientes al período indicado.

Para cualquier consulta o aclaración, no dude en contactarnos.

Saludos cordiales,

Departamento de Contabilidad
CIMEX - Gerencia Administrativa
Teléfono: 555-1234
Email: contabilidad@cimex.com.cu"""
        
        elif template == "Resumen ejecutivo":
            body = f"""Estimado/a ejecutivo/a,

Se adjunta el reporte ejecutivo "{self.report_name}" correspondiente al {datetime.now().strftime('%d/%m/%Y')}.

Este documento contiene un resumen de los principales indicadores y resultados del período, con análisis de tendencias y proyecciones.

Recomendamos revisar especialmente las secciones de:
- Resumen financiero
- Análisis de costos
- Proyecciones
- Recomendaciones

Quedamos a su disposición para ampliar cualquier información.

Atentamente,

Gerencia Administrativa
CIMEX"""
        
        elif template == "Urgente - Revisión inmediata":
            body = f"""URGENTE - REVISIÓN INMEDIATA

Asunto: Reporte "{self.report_name}"

Estimado/a,

Se requiere su revisión inmediata del reporte adjunto "{self.report_name}" generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}.

Este reporte contiene información crítica que requiere su atención y aprobación antes de continuar con el proceso.

Por favor, revise y responda a este email con sus comentarios o aprobación en las próximas 24 horas.

Gracias por su pronta atención.

Saludos,

Control y Seguimiento
CIMEX"""
        
        else:
            body = f"""Estimado/a,

Adjunto encontrará el reporte "{self.report_name}".

Saludos cordiales."""
        
        # Insertar texto en el área de texto
        self.body_text.insert(1.0, body)
    
    def _on_template_change(self, event=None) -> None:
        """Actualiza el cuerpo del email cuando cambia la plantilla."""
        self._load_template()
    
    def _add_attachment(self) -> None:
        """Abre diálogo para agregar archivo adjunto."""
        try:
            from tkinter import filedialog
            
            filepaths = filedialog.askopenfilenames(
                parent=self,
                title="Seleccionar archivos para adjuntar",
                filetypes=[
                    ("Todos los archivos", "*.*"),
                    ("Documentos PDF", "*.pdf"),
                    ("Documentos Excel", "*.xlsx;*.xls"),
                    ("Documentos Word", "*.docx;*.doc"),
                    ("Archivos CSV", "*.csv"),
                    ("Archivos de texto", "*.txt")
                ]
            )
            
            if filepaths:
                for filepath in filepaths:
                    import os
                    filename = os.path.basename(filepath)
                    self.attachments_listbox.insert(tk.END, f"📎 {filename}")
                
                self._update_summary()
                
        except ImportError:
            messagebox.showwarning(
                "No disponible",
                "El selector de archivos no está disponible en este entorno.",
                parent=self
            )
    
    def _remove_attachment(self) -> None:
        """Elimina el archivo adjunto seleccionado de la lista."""
        selection = self.attachments_listbox.curselection()
        if selection:
            # Eliminar el elemento seleccionado
            self.attachments_listbox.delete(selection[0])
            
            # Actualizar resumen
            self._update_summary()

    def _toggle_schedule_options(self) -> None:
        """Muestra u oculta las opciones de programación de envío."""
        if self.schedule_send_var.get():
            self.schedule_frame.grid()
        else:
            self.schedule_frame.grid_remove()
    
    def _select_schedule_date(self) -> None:
        """Abre un diálogo para seleccionar fecha de programación."""
        try:
            # Importar aquí para evitar dependencias circulares
            from tkcalendar import DateEntry
            
            date_window = tk.Toplevel(self)
            date_window.title("Seleccionar Fecha")
            date_window.transient(self)
            date_window.grab_set()
            
            # Configurar tamaño
            date_window.geometry("300x150")
            
            # Frame principal
            main_frame = ttk.Frame(date_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            ttk.Label(
                main_frame,
                text="Seleccione la fecha de envío:",
                font=('Arial', 10)
            ).pack(pady=(0, 10))
            
            # Calendario
            cal = DateEntry(
                main_frame,
                date_pattern='dd/mm/yyyy',
                locale='es_ES'
            )
            cal.pack(pady=10)
            
            # Botones
            button_frame = ttk.Frame(main_frame)
            button_frame.pack()
            
            def on_accept():
                self.schedule_date_var.set(cal.get())
                date_window.destroy()
            
            ttk.Button(
                button_frame,
                text="Aceptar",
                command=on_accept,
                width=10
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Button(
                button_frame,
                text="Cancelar",
                command=date_window.destroy,
                width=10
            ).pack(side=tk.LEFT)
            
            # Centrar ventana
            date_window.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() // 2) - (date_window.winfo_width() // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (date_window.winfo_height() // 2)
            date_window.geometry(f"+{x}+{y}")
            
        except ImportError:
            messagebox.showwarning(
                "Módulo no disponible",
                "El módulo 'tkcalendar' no está instalado. "
                "Use 'pip install tkcalendar' para habilitar el selector de fechas.",
                parent=self
            )
    
    def _show_email_preview(self) -> None:
        """Muestra una vista previa completa del email."""
        preview_text = f"""
        ==========================================
        VISTA PREVIA DEL EMAIL
        ==========================================
        
        De: contabilidad@cimex.com.cu
        Para: {self.to_var.get()}
        CC: {self.cc_var.get() if self.cc_var.get() else 'No'}
        BCC: {self.bcc_var.get() if self.bcc_var.get() else 'No'}
        
        Asunto: {self.subject_var.get()}
        
        Adjuntos: {self.attachments_listbox.size()} archivo(s)
        
        --------------------------------------------------
        CUERPO DEL MENSAJE:
        --------------------------------------------------
        
        {self.body_text.get(1.0, tk.END).strip()}
        
        ==========================================
        OPCIONES:
        ==========================================
        
        • Confirmación de lectura: {'Sí' if self.confirm_read_var.get() else 'No'}
        • Alta prioridad: {'Sí' if self.high_priority_var.get() else 'No'}
        • Guardar copia: {'Sí' if self.save_copy_var.get() else 'No'}
        • Programar envío: {'Sí' if self.schedule_send_var.get() else 'No'}
        
        {'• Fecha programada: ' + self.schedule_date_var.get() + ' ' + 
         self.schedule_hour_var.get() + ':' + self.schedule_minute_var.get() 
         if self.schedule_send_var.get() else ''}
        """
        
        # Crear ventana de vista previa
        preview_window = tk.Toplevel(self)
        preview_window.title(f"Vista Previa: {self.report_name}")
        preview_window.transient(self)
        preview_window.grab_set()
        
        # Configurar tamaño
        preview_window.geometry("600x700")
        
        # Frame principal
        main_frame = ttk.Frame(preview_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            main_frame,
            text="Vista Previa del Email",
            font=('Arial', 12, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        # Área de texto con scroll
        preview_text_widget = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=('Courier', 9),
            height=30
        )
        preview_text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        preview_text_widget.insert(1.0, preview_text)
        preview_text_widget.config(state='disabled')
        
        # Botón de cierre
        ttk.Button(
            main_frame,
            text="Cerrar Vista Previa",
            command=preview_window.destroy,
            width=20
        ).pack()
    
    def _save_as_draft(self) -> None:
        """Guarda la configuración del email como borrador."""
        # Por ahora, solo un mensaje informativo
        messagebox.showinfo(
            "Guardar Borrador",
            "La configuración del email se ha guardado como borrador.\n\n"
            "Nota: En una implementación completa, esto guardaría la "
            "configuración en una base de datos o archivo.",
            parent=self
        )
    
    def _send_test(self) -> None:
        """Envía un email de prueba."""
        # Obtener el email del usuario actual (simulado)
        test_email = "usuario@cimex.com.cu"  # En realidad debería venir del sistema
        
        # Mostrar diálogo de confirmación
        result = messagebox.askyesno(
            "Enviar Email de Prueba",
            f"Se enviará un email de prueba a:\n\n{test_email}\n\n"
            "¿Desea continuar?",
            parent=self
        )
        
        if result:
            # Simular envío de prueba
            messagebox.showinfo(
                "Prueba Enviada",
                f"Se ha enviado un email de prueba a:\n{test_email}\n\n"
                "Por favor, verifique su bandeja de entrada.",
                parent=self
            )
    
    def _validate_recipients(self) -> None:
        """Valida las direcciones de email de los destinatarios."""
        import re
        
        def is_valid_email(email: str) -> bool:
            """Valida si una cadena es un email válido."""
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email.strip()))
        
        # Obtener todos los destinatarios
        all_recipients = []
        if self.to_var.get():
            all_recipients.extend([e.strip() for e in self.to_var.get().split(',')])
        if self.cc_var.get():
            all_recipients.extend([e.strip() for e in self.cc_var.get().split(',')])
        if self.bcc_var.get():
            all_recipients.extend([e.strip() for e in self.bcc_var.get().split(',')])
        
        # Filtrar emails vacíos
        all_recipients = [e for e in all_recipients if e]
        
        if not all_recipients:
            messagebox.showwarning(
                "Validación de Destinatarios",
                "No hay destinatarios para validar.",
                parent=self
            )
            return
        
        # Validar cada email
        invalid_emails = []
        for email in all_recipients:
            if not is_valid_email(email):
                invalid_emails.append(email)
        
        if invalid_emails:
            messagebox.showwarning(
                "Validación de Destinatarios",
                f"Se encontraron {len(invalid_emails)} email(s) inválido(s):\n\n" +
                "\n".join(invalid_emails),
                parent=self
            )
        else:
            messagebox.showinfo(
                "Validación de Destinatarios",
                f"✓ Todos los {len(all_recipients)} destinatario(s) son válidos.",
                parent=self
            )
    
    def _update_summary(self) -> None:
        """Actualiza el resumen del email en la interfaz."""
        # Contar destinatarios
        to_count = len([e for e in self.to_var.get().split(',') if e.strip()])
        cc_count = len([e for e in self.cc_var.get().split(',') if e.strip()])
        bcc_count = len([e for e in self.bcc_var.get().split(',') if e.strip()])
        
        # Contar adjuntos
        attachments_count = self.attachments_listbox.size()
        
        # Construir resumen
        summary_parts = []
        
        if to_count > 0:
            summary_parts.append(f"Para: {to_count} destinatario(s)")
        if cc_count > 0:
            summary_parts.append(f"CC: {cc_count}")
        if bcc_count > 0:
            summary_parts.append(f"BCC: {bcc_count}")
        
        summary_parts.append(f"Adjuntos: {attachments_count}")
        
        if self.schedule_send_var.get():
            summary_parts.append(f"Programado: {self.schedule_date_var.get()} "
                               f"{self.schedule_hour_var.get()}:{self.schedule_minute_var.get()}")
        
        self.summary_var.set(" | ".join(summary_parts))
    
    def get_email_config(self) -> Dict[str, Any]:
        """
        Retorna la configuración del email.
        
        Returns:
            Diccionario con la configuración del email
        """
        return {
            'to': self.to_var.get(),
            'cc': self.cc_var.get(),
            'bcc': self.bcc_var.get(),
            'subject': self.subject_var.get(),
            'body': self.body_text.get(1.0, tk.END).strip(),
            'template': self.template_var.get(),
            'attachments': list(self.attachments_listbox.get(0, tk.END)),
            'confirm_read': self.confirm_read_var.get(),
            'high_priority': self.high_priority_var.get(),
            'save_copy': self.save_copy_var.get(),
            'schedule_send': self.schedule_send_var.get(),
            'schedule_date': self.schedule_date_var.get() if self.schedule_send_var.get() else None,
            'schedule_time': f"{self.schedule_hour_var.get()}:{self.schedule_minute_var.get()}" 
                           if self.schedule_send_var.get() else None,
            'report_name': self.report_name,
            'report_filepath': self.report_filepath
        }
    
    def show(self) -> Dict[str, Any]:
        """
        Muestra el diálogo y retorna la configuración.
        
        Returns:
            Diccionario con la configuración del email o diccionario vacío si se cancela
        """
        # Ejecutar el diálogo
        self.wait_window()
        
        # Retornar configuración si se aceptó
        if self.result:
            return self.get_email_config()
        return {}
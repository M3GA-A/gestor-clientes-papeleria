import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import calendar
from datetime import datetime
import re

# Establecemos el tema claro
ctk.set_appearance_mode("light")

# Colores extraídos del diseño
COLOR_FONDO_APP = "#F7F9FC"
COLOR_FONDO_PANEL = "#FFFFFF"
COLOR_BORDE = "#E2E8F0"
COLOR_TEXTO = "#1E293B"
COLOR_TEXTO_SEC = "#64748B"
COLOR_PRIMARIO = "#0F52BA"
COLOR_ESTADO_PEND = "#E2E8F0"
COLOR_ESTADO_COMP = "#DBEAFE"

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

ARCHIVO_JSON = "datos_papeleria.json"
ARCHIVO_CLIENTES = "clientes.json"

# Lista de productos
PRODUCTOS_PAPELERIA = {
    "Cuaderno A4": 4.00, "Bolígrafos azules": 2.50, "Folios A4 500 uds": 6.50,
    "Grapadora": 8.00, "Caja de clips": 1.20, "Tóner impresora": 45.00,
    "Lápices HB": 1.50, "Goma de borrar": 0.80, "Sacapuntas": 1.00,
    "Carpetas de cartón": 5.00, "Marcadores flúor": 3.20, "Calculadora básica": 12.00,
    "Agenda 2026": 15.00, "Notas adhesivas (Post-it)": 2.00, "Mochila escolar": 25.00,
    "Estuche": 6.00, "Regla 30cm": 1.20, "Pegamento en barra": 1.50,
    "Tijeras escolares": 1.80, "Cinta adhesiva": 1.50, "Corrector en cinta": 3.00
}

# ==========================================
# CLASE CALENDARIO POPUP
# ==========================================
class CalendarioPopup:
    def __init__(self, ventana_padre, entrada_fecha):
        self.entrada_fecha = entrada_fecha
        self.fecha_actual = datetime.today()
        self.ventana = ctk.CTkToplevel(ventana_padre)
        self.ventana.title("Seleccionar fecha")
        self.ventana.resizable(False, False)
        self.ventana.transient(ventana_padre)
        self.ventana.configure(fg_color=COLOR_FONDO_APP)
        self.ventana.grab_set()
        self.ventana.attributes("-topmost", True)
        
        self.contenedor = ctk.CTkFrame(self.ventana, fg_color="transparent")
        self.contenedor.pack(padx=15, pady=15)
        self.dibujar_calendario()

    def dibujar_calendario(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()
            
        encabezado = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        encabezado.grid(row=0, column=0, columnspan=7, pady=(0, 10))
        
        ctk.CTkButton(encabezado, text="<", width=30, fg_color=COLOR_PRIMARIO, command=self.mes_anterior).pack(side="left")
        ctk.CTkLabel(encabezado, text=f"{MESES[self.fecha_actual.month - 1]} {self.fecha_actual.year}", width=120, font=("Arial", 14, "bold"), text_color=COLOR_TEXTO).pack(side="left", padx=5)
        ctk.CTkButton(encabezado, text=">", width=30, fg_color=COLOR_PRIMARIO, command=self.mes_siguiente).pack(side="left")
        
        dias_semana = ["L", "M", "X", "J", "V", "S", "D"]
        for columna, dia in enumerate(dias_semana):
            ctk.CTkLabel(self.contenedor, text=dia, width=30, font=("Arial", 12, "bold"), text_color=COLOR_TEXTO_SEC).grid(row=1, column=columna, pady=(0, 5))
            
        calendario_mes = calendar.monthcalendar(self.fecha_actual.year, self.fecha_actual.month)
        for fila, semana in enumerate(calendario_mes, start=2):
            for columna, dia in enumerate(semana):
                if dia == 0:
                    ctk.CTkLabel(self.contenedor, text="", width=30).grid(row=fila, column=columna)
                else:
                    ctk.CTkButton(self.contenedor, text=str(dia), width=30, height=30, fg_color=COLOR_FONDO_PANEL, text_color=COLOR_TEXTO, border_width=1, border_color=COLOR_BORDE, hover_color=COLOR_ESTADO_COMP, command=lambda d=dia: self.seleccionar_fecha(d)).grid(row=fila, column=columna, padx=2, pady=2)

    def mes_anterior(self):
        mes = self.fecha_actual.month - 1
        anio = self.fecha_actual.year
        if mes == 0:
            mes, anio = 12, anio - 1
        self.fecha_actual = self.fecha_actual.replace(year=anio, month=mes, day=1)
        self.dibujar_calendario()

    def mes_siguiente(self):
        mes = self.fecha_actual.month + 1
        anio = self.fecha_actual.year
        if mes == 13:
            mes, anio = 1, anio + 1
        self.fecha_actual = self.fecha_actual.replace(year=anio, month=mes, day=1)
        self.dibujar_calendario()

    def seleccionar_fecha(self, dia):
        fecha = self.fecha_actual.replace(day=dia)
        self.entrada_fecha.delete(0, 'end')
        self.entrada_fecha.insert(0, fecha.strftime("%d/%m/%Y"))
        self.ventana.destroy()

# ==========================================
# CLASE API PARA MANEJO DE JSON
# ==========================================
class APIPapeleria:
    @staticmethod
    def leer_datos():
        try:
            with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def guardar_datos(datos):
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)

# ==========================================
# CLASE PRINCIPAL DE LA APP GUI
# ==========================================
class MiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AppVentas - Gestión de Papelería")
        self.geometry("1100x850")
        self.configure(fg_color=COLOR_FONDO_APP)

        self.datos = APIPapeleria.leer_datos()
        self.lista_clientes = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.armar_interfaz()
        self.cargar_datos_en_ui()

    def armar_interfaz(self):
        # ---------------------------------------------------------
        # MENU LATERAL (Sidebar)
        # ---------------------------------------------------------
        self.menu_lateral = ctk.CTkFrame(self, fg_color=COLOR_FONDO_PANEL, corner_radius=0, width=220, border_width=1, border_color=COLOR_BORDE)
        self.menu_lateral.grid(row=0, column=0, sticky="nsew")
        self.menu_lateral.grid_rowconfigure(6, weight=1) 
        self.menu_lateral.grid_propagate(False)

        ctk.CTkLabel(self.menu_lateral, text="📦 AppVentas", font=("Arial", 22, "bold"), text_color=COLOR_PRIMARIO).pack(pady=(30, 40))

        self.btn_dashboard = self.crear_boton_menu("Dashboard", activo=True, command=self.mostrar_dashboard)
        self.btn_clientes = self.crear_boton_menu("Clientes", command=self.mostrar_clientes)
        self.btn_ajustes = self.crear_boton_menu("Configuración", command=self.mostrar_configuracion)

        # Ocultos hasta login
        self.btn_clientes.pack_forget()
        self.btn_ajustes.pack_forget()

        ctk.CTkFrame(self.menu_lateral, fg_color="transparent").pack(fill="both", expand=True)
        self.btn_salir = self.crear_boton_menu("Salir", command=self.confirmar_salida)
        self.btn_salir.pack_configure(pady=(5, 30)) 

        # ---------------------------------------------------------
        # CONTENEDOR DE VISTAS
        # ---------------------------------------------------------
        self.contenedor_vistas = ctk.CTkFrame(self, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self.contenedor_vistas.grid(row=0, column=1, sticky="nsew")
        self.contenedor_vistas.grid_rowconfigure(0, weight=1)
        self.contenedor_vistas.grid_columnconfigure(0, weight=1)

        # Inicializar vistas
        self.vista_dashboard = self.crear_vista_dashboard()
        self.vista_clientes = self.crear_vista_clientes()
        self.vista_configuracion = self.crear_vista_configuracion()
        self.vista_login = self.crear_vista_login()
        self.vista_registro = self.crear_vista_registro()

        self.mostrar_dashboard()

    # ==========================================
    # VISTAS PRINCIPALES
    # ==========================================
    
    def crear_vista_clientes(self):
        frame_clientes = ctk.CTkFrame(self.contenedor_vistas, fg_color=COLOR_FONDO_APP, corner_radius=0)
        frame_clientes.grid_columnconfigure(0, weight=1)
        frame_clientes.grid_rowconfigure(1, weight=1)
        frame_clientes.grid_rowconfigure(2, weight=2, minsize=330)

        # CABECERA
        frame_cabecera = ctk.CTkFrame(frame_clientes, fg_color="transparent")
        frame_cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        frame_cabecera.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_cabecera, text="Gestión de Clientes", font=("Arial", 26, "bold"), text_color=COLOR_TEXTO).grid(row=0, column=0, sticky="w")
        
        self.buscador_clientes = ctk.CTkEntry(frame_cabecera, placeholder_text="🔍 Buscar cliente...", width=300, fg_color=COLOR_FONDO_PANEL, border_color=COLOR_BORDE, corner_radius=20, height=35)
        self.buscador_clientes.grid(row=0, column=1, sticky="e")
        self.buscador_clientes.bind("<KeyRelease>", self.filtrar_clientes)

        # --- PARTE ARRIBA (LISTA) ---
        self.scroll_clientes = ctk.CTkScrollableFrame(frame_clientes, fg_color=COLOR_FONDO_PANEL, border_color=COLOR_BORDE, border_width=1, corner_radius=12)
        self.scroll_clientes.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        frame_header = ctk.CTkFrame(self.scroll_clientes, fg_color="#F8FAFC", corner_radius=8)
        frame_header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(frame_header, text="Nombre y Apellido", font=("Arial", 13, "bold"), text_color=COLOR_TEXTO_SEC, width=220, anchor="w").pack(side="left", padx=15, pady=12)
        ctk.CTkLabel(frame_header, text="Fecha Pedido", font=("Arial", 13, "bold"), text_color=COLOR_TEXTO_SEC, width=120, anchor="w").pack(side="left", padx=10, pady=12)
        ctk.CTkLabel(frame_header, text="Total", font=("Arial", 13, "bold"), text_color=COLOR_TEXTO_SEC, width=100, anchor="w").pack(side="left", padx=10, pady=12)
        ctk.CTkLabel(frame_header, text="Estado", font=("Arial", 13, "bold"), text_color=COLOR_TEXTO_SEC, width=150, anchor="w").pack(side="left", padx=10, pady=12)

        self.frame_filas_clientes = ctk.CTkFrame(self.scroll_clientes, fg_color="transparent")
        self.frame_filas_clientes.pack(fill="both", expand=True)

        # --- PARTE ABAJO (FORMULARIO) AJUSTADO ---
        self.frame_formulario = ctk.CTkFrame(frame_clientes, fg_color=COLOR_FONDO_PANEL, corner_radius=12, border_width=1, border_color=COLOR_BORDE)
        self.frame_formulario.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        
        frame_top_form = ctk.CTkFrame(self.frame_formulario, fg_color="#F8FAFC", corner_radius=8)
        frame_top_form.pack(fill="x", padx=5, pady=5)
        
        self.lbl_titulo_form = ctk.CTkLabel(frame_top_form, text="Añadir Nuevo Cliente", font=("Arial", 14, "bold"), text_color=COLOR_TEXTO)
        self.lbl_titulo_form.pack(side="left", padx=15, pady=12)
        
        ctk.CTkButton(frame_top_form, text="+ Nuevo", fg_color=COLOR_PRIMARIO, text_color="white", width=90, height=30, command=self.guardar_nuevo_cliente).pack(side="right", padx=(5, 10))
        ctk.CTkButton(frame_top_form, text="Limpiar", fg_color=COLOR_TEXTO_SEC, hover_color="#475569", text_color="white", width=80, height=30, command=self.limpiar_formulario_confirmacion).pack(side="right", padx=5)

        self.btn_eliminar_cliente = ctk.CTkButton(frame_top_form, text="Eliminar Cliente", fg_color="#EF4444", hover_color="#DC2626", text_color="white", width=120, height=30, font=("Arial", 12, "bold"), command=self.eliminar_cliente)
        self.btn_eliminar_cliente.pack(side="right", padx=5)

        self.btn_guardar_cliente = ctk.CTkButton(frame_top_form, text="Guardar/Actualizar", fg_color="#10B981", hover_color="#059669", text_color="white", width=120, height=30, font=("Arial", 12, "bold"), command=self.guardar_cliente)
        self.btn_guardar_cliente.pack(side="right", padx=5)

        contenido_form = ctk.CTkFrame(self.frame_formulario, fg_color="transparent")
        contenido_form.pack(fill="x", expand=False, padx=16, pady=(6, 0))
        
        # Fila 1: Campos
        frame_campos = ctk.CTkFrame(contenido_form, fg_color="transparent")
        frame_campos.pack(fill="x", pady=(0, 8))
        # Ajuste clave: Usamos uniform para obligar a mantener proporciones exactas
        frame_campos.grid_columnconfigure(0, weight=2, uniform="campos") 
        frame_campos.grid_columnconfigure(1, weight=1, uniform="campos")
        frame_campos.grid_columnconfigure(2, weight=1, uniform="campos")
        
        # Nombre
        f_nom = ctk.CTkFrame(frame_campos, fg_color="transparent")
        f_nom.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_nom, text="Nombre Completo:", text_color=COLOR_TEXTO_SEC, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.ent_nombre_cliente = ctk.CTkEntry(f_nom, height=35)
        self.ent_nombre_cliente.pack(fill="x")
        
        # Fecha
        f_fec = ctk.CTkFrame(frame_campos, fg_color="transparent")
        f_fec.grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(f_fec, text="Fecha (DD/MM/AAAA):", text_color=COLOR_TEXTO_SEC, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        sub_fec = ctk.CTkFrame(f_fec, fg_color="transparent")
        sub_fec.pack(fill="x")
        vcmd_fecha = (self.register(self.validar_fecha_pedido), "%P")
        self.ent_fecha_cliente = ctk.CTkEntry(sub_fec, validate="key", validatecommand=vcmd_fecha, height=35)
        self.ent_fecha_cliente.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(sub_fec, text="📅", width=40, height=35, fg_color=COLOR_PRIMARIO, command=lambda: CalendarioPopup(self, self.ent_fecha_cliente)).pack(side="right", padx=(5, 0))

        # Estado
        f_est = ctk.CTkFrame(frame_campos, fg_color="transparent")
        f_est.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(f_est, text="Estado del Pedido:", text_color=COLOR_TEXTO_SEC, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.var_estado_cliente = ctk.StringVar(value="PENDIENTE")
        self.opt_estado_cliente = ctk.CTkOptionMenu(f_est, values=["PENDIENTE", "COMPLETADO", "ENVIADO", "CANCELADO"], variable=self.var_estado_cliente, height=35, fg_color=COLOR_FONDO_PANEL, text_color=COLOR_TEXTO, button_color=COLOR_BORDE, button_hover_color=COLOR_TEXTO_SEC)
        self.opt_estado_cliente.pack(fill="x")

        # Fila 2: Productos y Resumen
        frame_prods = ctk.CTkFrame(contenido_form, fg_color="transparent")
        frame_prods.pack(fill="x", expand=False)
        # Ajuste: Lista y formulario 50%/50%
        frame_prods.grid_columnconfigure(0, weight=1, uniform="prods")
        frame_prods.grid_columnconfigure(1, weight=1, uniform="prods")

        # Columna Izquierda: Buscador de productos
        f_izq = ctk.CTkFrame(frame_prods, fg_color="transparent")
        f_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        ctk.CTkLabel(f_izq, text="Añadir Artículo al Pedido:", text_color=COLOR_TEXTO_SEC, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.frame_add_prod = ctk.CTkFrame(f_izq, fg_color="transparent")
        self.frame_add_prod.pack(fill="x")
        self.ent_producto = ctk.CTkEntry(self.frame_add_prod, height=35)
        self.ent_producto.pack(side="left", fill="x", expand=True)
        self.ent_producto.bind("<KeyRelease>", self.mostrar_sugerencias_productos)
        ctk.CTkButton(self.frame_add_prod, text="Agregar", width=80, height=35, fg_color=COLOR_PRIMARIO, command=self.agregar_producto_lista).pack(side="right", padx=(5, 0))
        
        self.frame_sugerencias = ctk.CTkFrame(f_izq, fg_color=COLOR_FONDO_PANEL, border_color=COLOR_BORDE, border_width=1, corner_radius=6)

        # Columna Derecha: Lista de productos, Totales y Botones de Acción
        f_der = ctk.CTkFrame(frame_prods, fg_color="transparent")
        f_der.grid(row=0, column=1, sticky="nsew")
        
        self.frame_lista_prods = ctk.CTkScrollableFrame(f_der, height=60, fg_color=COLOR_FONDO_APP, border_width=1, border_color=COLOR_BORDE, corner_radius=6)
        self.frame_lista_prods.pack(fill="x", expand=False, pady=(0, 10))

        resumen_box = ctk.CTkFrame(f_der, fg_color=COLOR_FONDO_APP, border_width=1, border_color=COLOR_BORDE, corner_radius=6)
        resumen_box.pack(fill="x", pady=(0, 4))
        resumen_box.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.lbl_subtotal = ctk.CTkLabel(resumen_box, text="Subtotal: €0.00", font=("Arial", 12), text_color=COLOR_TEXTO_SEC)
        self.lbl_subtotal.grid(row=0, column=0, sticky="w", padx=(12, 6), pady=10)
        self.lbl_iva = ctk.CTkLabel(resumen_box, text="IVA (21%): €0.00", font=("Arial", 12), text_color=COLOR_TEXTO_SEC)
        self.lbl_iva.grid(row=0, column=1, sticky="ew", padx=6, pady=10)
        self.lbl_suma_total = ctk.CTkLabel(resumen_box, text="Total: €0.00", font=("Arial", 14, "bold"), text_color=COLOR_PRIMARIO)
        self.lbl_suma_total.grid(row=0, column=2, sticky="e", padx=(6, 12), pady=10)

        self.preparar_nuevo_cliente()
        return frame_clientes

    def crear_vista_configuracion(self):
        # Vista de Configuración
        frame = ctk.CTkFrame(self.contenedor_vistas, fg_color=COLOR_FONDO_APP, corner_radius=0)
        
        ctk.CTkLabel(frame, text="Configuración del Sistema", font=("Arial", 26, "bold"), text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=(30, 20))

        # Panel de Apariencia
        panel_apariencia = ctk.CTkFrame(frame, fg_color=COLOR_FONDO_PANEL, corner_radius=12, border_width=1, border_color=COLOR_BORDE)
        panel_apariencia.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(panel_apariencia, text="Apariencia", font=("Arial", 16, "bold"), text_color=COLOR_TEXTO).pack(anchor="w", padx=20, pady=(20, 10))
        
        self.sw_tema = ctk.CTkSwitch(panel_apariencia, text="Activar Modo Oscuro", font=("Arial", 14), text_color=COLOR_TEXTO, progress_color=COLOR_PRIMARIO, command=self.cambiar_tema)
        self.sw_tema.pack(anchor="w", padx=20, pady=(0, 20))

        # Panel de Datos
        panel_datos = ctk.CTkFrame(frame, fg_color=COLOR_FONDO_PANEL, corner_radius=12, border_width=1, border_color=COLOR_BORDE)
        panel_datos.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(panel_datos, text="Gestión de Datos", font=("Arial", 16, "bold"), text_color=COLOR_TEXTO).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(panel_datos, text="Advertencia: Estas acciones son irreversibles.", font=("Arial", 12), text_color="red").pack(anchor="w", padx=20, pady=(0, 10))
        
        ctk.CTkButton(panel_datos, text="Borrar todos los clientes y pedidos", fg_color="#EF4444", hover_color="#DC2626", command=self.borrar_todos_datos).pack(anchor="w", padx=20, pady=(0, 20))

        return frame

    def cambiar_tema(self):
        if self.sw_tema.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def borrar_todos_datos(self):
        if messagebox.askyesno("Peligro", "¿Estás completamente seguro de borrar todos los registros?"):
            self.lista_clientes = []
            with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
                json.dump(self.lista_clientes, f)
            self.actualizar_lista_clientes()
            messagebox.showinfo("Limpieza", "Datos borrados exitosamente.")

    def crear_vista_dashboard(self):
        frame_dashboard = ctk.CTkFrame(self.contenedor_vistas, fg_color=COLOR_FONDO_APP, corner_radius=0)
        frame_dashboard.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_dashboard, text="Panel Principal (Dashboard)", font=("Arial", 28, "bold"), text_color=COLOR_TEXTO).grid(row=0, column=0, sticky="w", padx=30, pady=(40, 10))
        ctk.CTkLabel(frame_dashboard, text="Bienvenido al sistema. Aquí tienes un resumen de la actividad reciente.", font=("Arial", 14), text_color=COLOR_TEXTO_SEC).grid(row=1, column=0, sticky="w", padx=30, pady=(0, 30))

        frame_stats = ctk.CTkFrame(frame_dashboard, fg_color="transparent")
        frame_stats.grid(row=2, column=0, sticky="ew", padx=30, pady=10)
        frame_stats.grid_columnconfigure((0, 1, 2), weight=1)

        card1 = ctk.CTkFrame(frame_stats, fg_color=COLOR_FONDO_PANEL, border_color=COLOR_BORDE, border_width=1, corner_radius=12)
        card1.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(card1, text="Clientes Registrados", font=("Arial", 14), text_color=COLOR_TEXTO_SEC).pack(pady=(20, 5))
        self.lbl_stat_clientes = ctk.CTkLabel(card1, text="0", font=("Arial", 28, "bold"), text_color=COLOR_PRIMARIO)
        self.lbl_stat_clientes.pack(pady=(0, 20))

        card2 = ctk.CTkFrame(frame_stats, fg_color=COLOR_FONDO_PANEL, border_color=COLOR_BORDE, border_width=1, corner_radius=12)
        card2.grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(card2, text="Pedidos Totales", font=("Arial", 14), text_color=COLOR_TEXTO_SEC).pack(pady=(20, 5))
        self.lbl_stat_pedidos = ctk.CTkLabel(card2, text="0", font=("Arial", 28, "bold"), text_color=COLOR_PRIMARIO)
        self.lbl_stat_pedidos.pack(pady=(0, 20))

        card3 = ctk.CTkFrame(frame_stats, fg_color=COLOR_FONDO_PANEL, border_color=COLOR_BORDE, border_width=1, corner_radius=12)
        card3.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(card3, text="Ingresos Acumulados", font=("Arial", 14), text_color=COLOR_TEXTO_SEC).pack(pady=(20, 5))
        self.lbl_stat_ingresos = ctk.CTkLabel(card3, text="€0.00", font=("Arial", 28, "bold"), text_color=COLOR_PRIMARIO)
        self.lbl_stat_ingresos.pack(pady=(0, 20))

        # Sección de Autenticación
        self.frame_auth = ctk.CTkFrame(frame_dashboard, fg_color=COLOR_FONDO_PANEL, border_color=COLOR_BORDE, border_width=1, corner_radius=12)
        self.frame_auth.grid(row=3, column=0, sticky="ew", padx=30, pady=40)
        
        ctk.CTkLabel(self.frame_auth, text="Acceso al Sistema", font=("Arial", 18, "bold"), text_color=COLOR_TEXTO).pack(pady=(30, 10))
        ctk.CTkLabel(self.frame_auth, text="Inicia sesión para gestionar tus datos o regístrate si eres un nuevo usuario.", font=("Arial", 14), text_color=COLOR_TEXTO_SEC).pack(pady=(0, 20))
        
        frame_botones = ctk.CTkFrame(self.frame_auth, fg_color="transparent")
        frame_botones.pack(pady=(0, 30))
        
        ctk.CTkButton(frame_botones, text="Iniciar Sesión", fg_color=COLOR_PRIMARIO, text_color="white", font=("Arial", 14, "bold"), command=self.mostrar_login).pack(side="left", padx=15)
        ctk.CTkButton(frame_botones, text="Registrarse", fg_color="transparent", border_width=2, border_color=COLOR_PRIMARIO, text_color=COLOR_PRIMARIO, font=("Arial", 14, "bold"), hover_color=COLOR_ESTADO_COMP, command=self.mostrar_registro).pack(side="left", padx=15)

        return frame_dashboard

    def actualizar_stats_dashboard(self):
        total_clientes = len(self.lista_clientes)
        ingresos = sum(c.get("suma_pedido", 0) for c in self.lista_clientes if c.get("estado") != "CANCELADO")
        
        self.lbl_stat_clientes.configure(text=str(total_clientes))
        self.lbl_stat_pedidos.configure(text=str(total_clientes))
        self.lbl_stat_ingresos.configure(text=f"€{ingresos:,.2f}")

    # --- NAVEGACIÓN Y MENÚS ---
    def crear_boton_menu(self, texto, activo=False, command=None):
        color_fondo = COLOR_PRIMARIO if activo else "transparent"
        color_texto = "white" if activo else COLOR_TEXTO_SEC
        
        btn = ctk.CTkButton(self.menu_lateral, text=texto, fg_color=color_fondo, text_color=color_texto, anchor="w", font=("Arial", 14, "bold" if activo else "normal"), corner_radius=8, hover_color=COLOR_BORDE, command=command)
        btn.pack(fill="x", padx=15, pady=5)
        return btn

    def esconder_vistas(self):
        self.vista_dashboard.grid_forget()
        self.vista_clientes.grid_forget()
        self.vista_configuracion.grid_forget()
        self.vista_login.grid_forget()
        self.vista_registro.grid_forget()

    def mostrar_menu_completo(self):
        self.btn_clientes.pack(fill="x", padx=15, pady=5, after=self.btn_dashboard)
        self.btn_ajustes.pack(fill="x", padx=15, pady=5, after=self.btn_clientes)
        self.frame_auth.grid_forget() 

    def mostrar_dashboard(self):
        self.esconder_vistas()
        self.vista_dashboard.grid(row=0, column=0, sticky="nsew")
        self.actualizar_stats_dashboard()
        self.actualizar_botones_menu(self.btn_dashboard)

    def mostrar_clientes(self):
        self.esconder_vistas()
        self.vista_clientes.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        self.actualizar_botones_menu(self.btn_clientes)

    def mostrar_configuracion(self):
        self.esconder_vistas()
        self.vista_configuracion.grid(row=0, column=0, sticky="nsew")
        self.actualizar_botones_menu(self.btn_ajustes)

    def mostrar_login(self):
        self.esconder_vistas()
        self.vista_login.grid(row=0, column=0, sticky="nsew")
        self.actualizar_botones_menu(None)

    def mostrar_registro(self):
        self.esconder_vistas()
        self.vista_registro.grid(row=0, column=0, sticky="nsew")
        self.actualizar_botones_menu(None)

    def actualizar_botones_menu(self, boton_activo):
        botones = [self.btn_dashboard, self.btn_clientes, self.btn_ajustes]
        for btn in botones:
            if btn == boton_activo:
                btn.configure(fg_color=COLOR_PRIMARIO, text_color="white", font=("Arial", 14, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXTO_SEC, font=("Arial", 14, "normal"))

    # --- VISTAS AUTENTICACIÓN ---
    def crear_vista_login(self):
        frame_login = ctk.CTkFrame(self.contenedor_vistas, fg_color=COLOR_FONDO_APP, corner_radius=0)
        frame_centro = ctk.CTkFrame(frame_login, fg_color=COLOR_FONDO_PANEL, border_color=COLOR_BORDE, border_width=1, corner_radius=12)
        frame_centro.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame_centro, text="Iniciar Sesión", font=("Arial", 24, "bold"), text_color=COLOR_TEXTO).pack(pady=(30, 20), padx=50)

        ctk.CTkLabel(frame_centro, text="Correo Electrónico:", text_color=COLOR_TEXTO_SEC, anchor="w").pack(pady=(10, 0), padx=50, fill="x")
        login_mail = ctk.CTkEntry(frame_centro, placeholder_text="ejemplo@correo.com", border_color=COLOR_BORDE, fg_color=COLOR_FONDO_APP, text_color=COLOR_TEXTO, width=300, height=35)
        login_mail.pack(pady=(0, 10), padx=50, fill="x")

        ctk.CTkLabel(frame_centro, text="Contraseña:", text_color=COLOR_TEXTO_SEC, anchor="w").pack(pady=(10, 0), padx=50, fill="x")
        login_pass = ctk.CTkEntry(frame_centro, placeholder_text="Tu contraseña", show="*", border_color=COLOR_BORDE, fg_color=COLOR_FONDO_APP, text_color=COLOR_TEXTO, width=300, height=35)
        login_pass.pack(pady=(0, 10), padx=50, fill="x")

        def toggle_login_pass():
            if chk_show_login.get() == 1:
                login_pass.configure(show="")
            else:
                login_pass.configure(show="*")

        chk_show_login = ctk.CTkCheckBox(frame_centro, text="Mostrar contraseña", text_color=COLOR_TEXTO_SEC, fg_color=COLOR_PRIMARIO, command=toggle_login_pass)
        chk_show_login.pack(pady=(0, 10), padx=50, anchor="w")

        lbl_error_login = ctk.CTkLabel(frame_centro, text="", text_color="red")
        lbl_error_login.pack()

        def validar_login(event=None):
            correo = login_mail.get()
            password = login_pass.get()
            
            self.datos = APIPapeleria.leer_datos()
            usuarios = self.datos.get("usuarios", {})

            if not correo or not password:
                lbl_error_login.configure(text="Todos los campos son obligatorios.", text_color="red")
            elif correo not in usuarios or usuarios[correo] != password:
                lbl_error_login.configure(text="Correo o contraseña incorrectos.", text_color="red")
            else:
                lbl_error_login.configure(text="Inicio de sesión exitoso.", text_color="green")
                self.update_idletasks() # Actualizar UI para mostrar el mensaje de éxito
                self.actualizar_lista_clientes() # Generar los cientos de widgets ahora
                self.after(500, lambda: [self.mostrar_menu_completo(), self.mostrar_dashboard(), lbl_error_login.configure(text=""), login_mail.delete(0, 'end'), login_pass.delete(0, 'end')])

        ctk.CTkButton(frame_centro, text="Entrar", fg_color=COLOR_PRIMARIO, hover_color="#0D47A1", height=40, font=("Arial", 14, "bold"), command=validar_login).pack(pady=30, padx=50, fill="x")
        login_mail.bind('<Return>', validar_login)
        login_pass.bind('<Return>', validar_login)
        
        return frame_login

    def crear_vista_registro(self):
        frame_registro = ctk.CTkFrame(self.contenedor_vistas, fg_color=COLOR_FONDO_APP, corner_radius=0)
        frame_centro = ctk.CTkFrame(frame_registro, fg_color=COLOR_FONDO_PANEL, border_color=COLOR_BORDE, border_width=1, corner_radius=12)
        frame_centro.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame_centro, text="Registrarse", font=("Arial", 24, "bold"), text_color=COLOR_TEXTO).pack(pady=(30, 20), padx=50)

        ctk.CTkLabel(frame_centro, text="Correo Electrónico:", text_color=COLOR_TEXTO_SEC, anchor="w").pack(pady=(10, 0), padx=50, fill="x")
        sign_mail = ctk.CTkEntry(frame_centro, border_color=COLOR_BORDE, fg_color=COLOR_FONDO_APP, width=300, height=35)
        sign_mail.pack(pady=(0, 10), padx=50, fill="x")

        ctk.CTkLabel(frame_centro, text="Contraseña:", text_color=COLOR_TEXTO_SEC, anchor="w").pack(pady=(5, 0), padx=50, fill="x")
        sign_pass = ctk.CTkEntry(frame_centro, show="*", border_color=COLOR_BORDE, fg_color=COLOR_FONDO_APP, width=300, height=35)
        sign_pass.pack(pady=(0, 10), padx=50, fill="x")
        
        # Hint (pista) indicando los requisitos de la contraseña
        ctk.CTkLabel(frame_centro, text="* Mínimo 6 caracteres y al menos 1 letra", text_color="gray", font=("Arial", 11), width=250, anchor="w").pack(pady=(2, 10))



        ctk.CTkLabel(frame_centro, text="Confirmar Contraseña:", text_color=COLOR_TEXTO_SEC, anchor="w").pack(pady=(5, 0), padx=50, fill="x")
        sign_pass2 = ctk.CTkEntry(frame_centro, show="*", border_color=COLOR_BORDE, fg_color=COLOR_FONDO_APP, width=300, height=35)
        sign_pass2.pack(pady=(0, 10), padx=50, fill="x")
        
        def toggle_sign_pass():
            if chk_show_sign.get() == 1:
                sign_pass.configure(show="")
                sign_pass2.configure(show="")
            else:
                sign_pass.configure(show="*")
                sign_pass2.configure(show="*")

        chk_show_sign = ctk.CTkCheckBox(frame_centro, text="Mostrar contraseñas", text_color=COLOR_TEXTO_SEC, fg_color=COLOR_PRIMARIO, hover_color="#882056", command=toggle_sign_pass)
        chk_show_sign.pack(pady=(0, 10))

        lbl_error_sign = ctk.CTkLabel(frame_centro, text="", text_color="red")
        lbl_error_sign.pack()

        def validar_signup(event=None):
            correo = sign_mail.get()
            password = sign_pass.get()
            confirmar = sign_pass2.get()
            
            self.datos = APIPapeleria.leer_datos()
            usuarios = self.datos.setdefault("usuarios", {})

            if not correo or not password:
                lbl_error_sign.configure(text="Faltan datos.", text_color="red")
            elif password != confirmar:
                lbl_error_sign.configure(text="Contraseñas no coinciden.", text_color="red")
            elif correo in usuarios:
                lbl_error_sign.configure(text="El correo ya existe.", text_color="red")
            else:
                usuarios[correo] = password
                APIPapeleria.guardar_datos(self.datos)
                lbl_error_sign.configure(text="Registro exitoso.", text_color="green")
                self.update_idletasks() # Actualizar UI para mostrar el mensaje de éxito
                self.actualizar_lista_clientes() # Generar los cientos de widgets ahora
                self.after(500, lambda: [self.mostrar_menu_completo(), self.mostrar_dashboard(), lbl_error_sign.configure(text=""), sign_mail.delete(0, 'end'), sign_pass.delete(0, 'end'), sign_pass2.delete(0, 'end')])

        ctk.CTkButton(frame_centro, text="Crear Cuenta", fg_color=COLOR_PRIMARIO, height=40, font=("Arial", 14, "bold"), command=validar_signup).pack(pady=30, padx=50, fill="x")
        return frame_registro

    # --- LÓGICA DE DATOS ---
    def validar_fecha_pedido(self, P):
        if len(P) > 10: return False
        for i, char in enumerate(P):
            if i in [2, 5]:
                if char != "/": return False
            elif not char.isdigit(): return False
        return True

    def cargar_datos_en_ui(self):
        try:
            with open(ARCHIVO_CLIENTES, "r", encoding="utf-8") as f:
                self.lista_clientes = json.load(f)
                for i, c in enumerate(self.lista_clientes):
                    if "id" not in c:
                        c["id"] = i + 1
        except (FileNotFoundError, json.JSONDecodeError):
            self.lista_clientes = []
            
        # Actualizamos solo las estadísticas numéricas para que el Dashboard arranque rápido
        # NO renderizamos las listas gráficamente aquí
        self.actualizar_stats_dashboard()

    def filtrar_clientes(self, event=None):
        if hasattr(self, '_filtro_timer'):
            self.after_cancel(self._filtro_timer)
        self._filtro_timer = self.after(300, self._aplicar_filtro)

    def _aplicar_filtro(self):
        texto = self.buscador_clientes.get().lower()
        if not texto:
            self.actualizar_lista_clientes()
        else:
            filtrados = [c for c in self.lista_clientes if texto in f"{c.get('nombre', '')} {c.get('apellido', '')}".lower()]
            self.actualizar_lista_clientes(filtrados)

    def actualizar_lista_clientes(self, lista_mostrar=None):
        if lista_mostrar is None:
            lista_mostrar = self.lista_clientes
            
        for widget in self.frame_filas_clientes.winfo_children():
            widget.destroy()
            
        for cliente in lista_mostrar:
            row_frame = ctk.CTkFrame(self.frame_filas_clientes, fg_color="transparent", cursor="hand2")
            row_frame.pack(fill="x", pady=2, padx=5)
            
            nombre_completo = f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}".strip()
            
            lbl_nom = ctk.CTkLabel(row_frame, text=nombre_completo, font=("Arial", 14), text_color=COLOR_TEXTO, width=220, anchor="w", cursor="hand2")
            lbl_nom.pack(side="left", padx=15, pady=12)
            
            lbl_fec = ctk.CTkLabel(row_frame, text=cliente.get("fecha_pedido", ""), font=("Arial", 13), text_color=COLOR_TEXTO_SEC, width=120, anchor="w", cursor="hand2")
            lbl_fec.pack(side="left", padx=10, pady=12)
            
            lbl_sum = ctk.CTkLabel(row_frame, text=f"€{cliente.get('suma_pedido', 0):.2f}", font=("Arial", 14, "bold"), text_color=COLOR_TEXTO, width=100, anchor="w", cursor="hand2")
            lbl_sum.pack(side="left", padx=10, pady=12)
            
            estado_var = ctk.StringVar(value=cliente.get("estado", "PENDIENTE"))
            combo = ctk.CTkOptionMenu(
                row_frame, values=["PENDIENTE", "COMPLETADO", "ENVIADO", "CANCELADO"], 
                variable=estado_var, width=140, fg_color=COLOR_FONDO_PANEL, text_color=COLOR_TEXTO, button_color=COLOR_BORDE,
                command=lambda v, cid=cliente.get("id"): self.cambiar_estado(cid, v)
            )
            combo.pack(side="left", padx=10, pady=8)
            
            ctk.CTkFrame(self.frame_filas_clientes, height=1, fg_color=COLOR_BORDE).pack(fill="x", padx=15)
            
            click_handler = lambda e, c=cliente: self.cargar_cliente_formulario(c)
            row_frame.bind("<Button-1>", click_handler)
            lbl_nom.bind("<Button-1>", click_handler)
            lbl_fec.bind("<Button-1>", click_handler)
            lbl_sum.bind("<Button-1>", click_handler)

    def preparar_nuevo_cliente(self):
        self.cliente_actual_id = None
        self.lbl_titulo_form.configure(text="Añadir Nuevo Cliente")
        self.btn_guardar_cliente.configure(text="Guardar/Actualizar")
        self.btn_eliminar_cliente.configure(state="disabled")
        
        self.ent_nombre_cliente.delete(0, 'end')
        self.ent_fecha_cliente.delete(0, 'end')
        self.var_estado_cliente.set("PENDIENTE")
        self.ent_producto.delete(0, 'end')
        
        self.productos_actuales = []
        self.suma_actual = 0.0
        self.actualizar_ui_productos()
        
        for w in self.frame_sugerencias.winfo_children(): w.destroy()
        self.frame_sugerencias.pack_forget()

    def limpiar_formulario_confirmacion(self):
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres limpiar el formulario sin guardar?"):
            self.preparar_nuevo_cliente()

    def cargar_cliente_formulario(self, cliente):
        self.cliente_actual_id = cliente.get("id")
        nombre_completo = f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}".strip()
        self.lbl_titulo_form.configure(text=f"Editando: {nombre_completo}")
        self.btn_guardar_cliente.configure(text="Guardar Cambios")
        self.btn_eliminar_cliente.configure(state="normal")
        
        self.ent_nombre_cliente.delete(0, 'end')
        self.ent_nombre_cliente.insert(0, nombre_completo)
        
        self.ent_fecha_cliente.delete(0, 'end')
        self.ent_fecha_cliente.insert(0, cliente.get("fecha_pedido", ""))
        
        self.var_estado_cliente.set(cliente.get("estado", "PENDIENTE"))
        self.ent_producto.delete(0, 'end')
        
        self.productos_actuales = list(cliente.get("productos", []))
        self.suma_actual = sum(p.get("precio", 0) for p in self.productos_actuales)
        self.actualizar_ui_productos()
        for w in self.frame_sugerencias.winfo_children(): w.destroy()
        self.frame_sugerencias.pack_forget()

    def actualizar_ui_productos(self):
        for w in self.frame_lista_prods.winfo_children():
            w.destroy()
            
        for i, prod in enumerate(self.productos_actuales):
            frame_prod = ctk.CTkFrame(self.frame_lista_prods, fg_color="transparent")
            frame_prod.pack(fill="x", pady=2)
            ctk.CTkLabel(frame_prod, text=f"• {prod['articulo']}", anchor="w", text_color=COLOR_TEXTO).pack(side="left", padx=5)
            ctk.CTkLabel(frame_prod, text=f"€{prod['precio']:.2f}", text_color=COLOR_TEXTO_SEC).pack(side="left", padx=5)
            btn_del = ctk.CTkButton(frame_prod, text="X", width=25, height=20, fg_color="#EF4444", hover_color="#DC2626", command=lambda idx=i: self.eliminar_producto_lista(idx))
            btn_del.pack(side="right", padx=5)
            
        subtotal = self.suma_actual
        iva = subtotal * 0.21
        total = subtotal + iva
        
        self.lbl_subtotal.configure(text=f"Subtotal: €{subtotal:.2f}")
        self.lbl_iva.configure(text=f"IVA (21%): €{iva:.2f}")
        self.lbl_suma_total.configure(text=f"Total: €{total:.2f}")

    def eliminar_producto_lista(self, idx):
        if 0 <= idx < len(self.productos_actuales):
            prod = self.productos_actuales.pop(idx)
            self.suma_actual -= prod.get("precio", 0)
            self.actualizar_ui_productos()

    def mostrar_sugerencias_productos(self, event):
        texto = self.ent_producto.get().lower()
        for w in self.frame_sugerencias.winfo_children(): w.destroy()
        
        if not texto: 
            self.frame_sugerencias.pack_forget()
            return
            
        coincidencias = [p for p in PRODUCTOS_PAPELERIA.keys() if texto in p.lower()][:3]
        if not coincidencias:
            self.frame_sugerencias.pack_forget()
            return
            
        for p in coincidencias:
            btn = ctk.CTkButton(self.frame_sugerencias, text=p, fg_color="transparent", hover_color=COLOR_ESTADO_PEND, text_color=COLOR_TEXTO, anchor="w", height=30, command=lambda prod=p: self.seleccionar_sugerencia(prod))
            btn.pack(fill="x", pady=1, padx=2)
            
        self.frame_sugerencias.pack(fill="x", padx=(0, 85), pady=(2, 0))

    def seleccionar_sugerencia(self, prod_name):
        self.ent_producto.delete(0, 'end')
        self.ent_producto.insert(0, prod_name)
        for w in self.frame_sugerencias.winfo_children(): w.destroy()
        self.frame_sugerencias.pack_forget()
            
    def agregar_producto_lista(self):
        prod_name = self.ent_producto.get()
        if prod_name in PRODUCTOS_PAPELERIA:
            precio = PRODUCTOS_PAPELERIA[prod_name]
            self.productos_actuales.append({"articulo": prod_name, "precio": precio})
            self.suma_actual += precio
            self.ent_producto.delete(0, 'end')
            self.actualizar_ui_productos()
        else:
            messagebox.showwarning("No encontrado", "Selecciona un producto válido de las sugerencias.")

    def guardar_nuevo_cliente(self):
        self.cliente_actual_id = None
        self.guardar_cliente()

    def guardar_cliente(self):
        nombre_input = self.ent_nombre_cliente.get().strip()
        fecha = self.ent_fecha_cliente.get()
        estado = self.var_estado_cliente.get()
        
        if not nombre_input or not fecha:
            messagebox.showwarning("Faltan datos", "Nombre y Fecha son obligatorios.")
            return
            
        partes = nombre_input.split(" ", 1)
        nombre = partes[0]
        apellido = partes[1] if len(partes) > 1 else ""
        
        if self.cliente_actual_id is None:
            nuevo_id = max([c.get("id", 0) for c in self.lista_clientes] + [0]) + 1
            nuevo_cliente = {
                "id": nuevo_id, "nombre": nombre, "apellido": apellido, "fecha_pedido": fecha,
                "subtotal": self.suma_actual, "iva": self.suma_actual * 0.21,
                "suma_pedido": self.suma_actual * 1.21, "productos": self.productos_actuales, "estado": estado
            }
            self.lista_clientes.append(nuevo_cliente)
        else:
            for c in self.lista_clientes:
                if c.get("id") == self.cliente_actual_id:
                    c.update({"nombre": nombre, "apellido": apellido, "fecha_pedido": fecha, "estado": estado, "productos": self.productos_actuales, "subtotal": self.suma_actual, "iva": self.suma_actual * 0.21, "suma_pedido": self.suma_actual * 1.21})
                    break
            
        with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
            json.dump(self.lista_clientes, f, indent=4)
            
        self.actualizar_lista_clientes()
        self.preparar_nuevo_cliente()
        messagebox.showinfo("Éxito", "Operación realizada correctamente.")

    def eliminar_cliente(self):
        if self.cliente_actual_id is not None and messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este cliente?"):
            self.lista_clientes = [c for c in self.lista_clientes if c.get("id") != self.cliente_actual_id]
            with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
                json.dump(self.lista_clientes, f, indent=4)
            self.actualizar_lista_clientes()
            self.preparar_nuevo_cliente()

    def cambiar_estado(self, cliente_id, nuevo_estado):
        for c in self.lista_clientes:
            if c.get("id") == cliente_id:
                c["estado"] = nuevo_estado
                break
        with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
            json.dump(self.lista_clientes, f, indent=4)

    def confirmar_salida(self):
        self.btn_salir.configure(state="disabled")
        ventana = ctk.CTkToplevel(self)
        ventana.title("Saliendo...")
        ventana.geometry(f"350x120+{int(self.winfo_x() + (self.winfo_width()/2) - 175)}+{int(self.winfo_y() + (self.winfo_height()/2) - 60)}")
        ventana.configure(fg_color=COLOR_FONDO_APP)
        ventana.attributes("-topmost", True)
        ctk.CTkLabel(ventana, text="Se cierra el programa en 3 segundos...💣​ ", font=("Arial", 16, "bold"), text_color=COLOR_TEXTO).pack(expand=True)
        self.after(3000, self.destroy)

if __name__ == "__main__":
    app = MiApp()
    app.mainloop()
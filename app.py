import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime
from PIL import Image

# CONFIGURACIÓN VISUAL
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==========================================
# PARTE 1: BACKEND (DB + LÓGICA FINANCIERA) - VERSIÓN ANTI-LOCK
# ==========================================
def iniciar_db():
    # timeout=10 hace que espere 10 segundos antes de dar error de bloqueo
    conn = sqlite3.connect("negocio.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            tipo TEXT, 
            nombre TEXT, 
            genero TEXT, 
            cantidad INTEGER, 
            precio REAL,
            UNIQUE(nombre, tipo, genero))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            ticket_id TEXT,
            producto_id INTEGER, 
            producto_nombre TEXT, 
            tipo_movimiento TEXT, 
            cantidad INTEGER, 
            precio_unitario REAL,
            total_renglon REAL,
            fecha TEXT)''')
    conn.commit()
    conn.close()

def db_consultar(query, params=()):
    try:
        # Usamos 'with' para que la conexión se cierre AUTOMÁTICAMENTE al terminar
        with sqlite3.connect("negocio.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            datos = cursor.fetchall()
            return datos
    except Exception as e:
        print(f"Error Lectura DB: {e}")
        return []

def db_ejecutar(query, params=()):
    try:
        with sqlite3.connect("negocio.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return "OK", cursor.lastrowid
    except Exception as e:
        return str(e), 0

# --- FUNCIONES ESPECÍFICAS (Wrappers) ---

def db_listar_productos(filtro=""):
    q = "SELECT id, tipo, nombre, genero, cantidad, precio FROM productos"
    if filtro: q += f" WHERE nombre LIKE '%{filtro}%' OR tipo LIKE '%{filtro}%' ORDER BY nombre"
    else: q += " ORDER BY nombre"
    return db_consultar(q)

def db_actualizar_producto(pid, t, n, g, c, p):
    res, _ = db_ejecutar("UPDATE productos SET tipo=?, nombre=?, genero=?, cantidad=?, precio=? WHERE id=?", (t, n, g, c, p, pid))
    return res

def db_obtener_precio(pid):
    res = db_consultar("SELECT precio FROM productos WHERE id=?", (pid,))
    return res[0][0] if res else 0.0

def db_procesar_venta(carrito):
    # En transacciones complejas (varios pasos), controlamos la conexión manualmente
    conn = sqlite3.connect("negocio.db", timeout=10)
    cursor = conn.cursor()
    
    ticket_id = f"T-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        for item in carrito:
            # 1. Verificar Stock
            cursor.execute("SELECT cantidad FROM productos WHERE id=?", (item['id'],))
            stock_actual = cursor.fetchone()[0]
            if stock_actual < item['cantidad']:
                conn.close(); return f"Error: Stock insuficiente para {item['nombre']}"
            
            # 2. Descontar
            cursor.execute("UPDATE productos SET cantidad=? WHERE id=?", (stock_actual - item['cantidad'], item['id']))
            
            # 3. Historial
            total_linea = item['cantidad'] * item['precio']
            cursor.execute("""
                INSERT INTO historial (ticket_id, producto_id, producto_nombre, tipo_movimiento, cantidad, precio_unitario, total_renglon, fecha)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticket_id, item['id'], item['nombre'], "VENTA", item['cantidad'], item['precio'], total_linea, fecha))
            
        conn.commit()
        return "OK"
    except Exception as e: 
        conn.rollback() # Si falla, deshacer cambios
        return str(e)
    finally:
        conn.close() # ESTO GARANTIZA QUE SIEMPRE SE CIERRE

def db_procesar_compra(carrito):
    conn = sqlite3.connect("negocio.db", timeout=10)
    cursor = conn.cursor()
    ticket_id = f"C-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        for item in carrito:
            pid, nom = 0, item['nombre']
            if item['nuevo']:
                cursor.execute("INSERT INTO productos (tipo, nombre, genero, cantidad, precio) VALUES (?,?,?,?,?)", 
                              (item['tipo'], item['nombre'], item['genero'], item['cantidad'], item['precio']))
                pid = cursor.lastrowid
            else:
                pid = item['id']
                cursor.execute("UPDATE productos SET cantidad=cantidad+?, precio=? WHERE id=?", (item['cantidad'], item['precio'], pid))
                if 'nombre_real' in item: nom = item['nombre_real']
            
            total_linea = item['cantidad'] * item['precio']
            cursor.execute("INSERT INTO historial VALUES (NULL,?,?,?,?,?,?,?,?)", 
                           (ticket_id, pid, nom, "COMPRA", item['cantidad'], item['precio'], total_linea, fecha))
        conn.commit()
        return "OK"
    except Exception as e: 
        conn.rollback()
        return str(e)
    finally:
        conn.close()

# ==========================================
# PARTE 2: WIDGETS PROPIOS
# ==========================================
class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = []; self._hits = []; self.mapa_ids = {} 
        self.bind('<KeyRelease>', self.handle_keyrelease)
    def set_completion_list(self, l, m): self._completion_list = sorted(l); self.mapa_ids = m; self['values'] = self._completion_list
    def handle_keyrelease(self, event):
        if event.keysym in ('BackSpace', 'Left', 'Right', 'Up', 'Down', 'Return', 'Tab'): return
        val = self.get()
        if val == '': self['values'] = self._completion_list
        else: self['values'] = [x for x in self._completion_list if val.lower() in x.lower()]
    def get_selected_id(self): return self.mapa_ids.get(self.get(), None)

def ordenar_treeview(tree, col, reverse):
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    try: l.sort(key=lambda t: float(t[0].replace("$","")), reverse=reverse)
    except: l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l): tree.move(k, '', index)
    tree.heading(col, command=lambda: ordenar_treeview(tree, col, not reverse))

# ==========================================
# PARTE 3: INTERFAZ
# ==========================================

class Aplicacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión Comercial v9.0 (Financiero)")
        self.geometry("1150x750")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # MENÚ LATERAL
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="MI NEGOCIO", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.botones_menu = {}
        items = [("🏠 Inicio", "inicio"), ("📦 Inventario", "inventario"), ("💰 Nueva Venta", "venta"), ("🚚 Nueva Compra", "compra"), ("📅 Registro", "historial")]
        for i, (txt, key) in enumerate(items):
            btn = ctk.CTkButton(self.sidebar, text=txt, command=lambda k=key: self.mostrar_frame(k), fg_color="transparent", anchor="w", height=40)
            btn.grid(row=i+1, column=0, sticky="ew", padx=10, pady=5)
            self.botones_menu[key] = btn

        # ÁREA CONTENIDO
        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.frames = {}
        self.crear_frames()
        
        # Variables y Estilos
        self.carrito_ventas = []
        self.carrito_compras = []
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=30, borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#333333", foreground="white", relief="flat")
        
        iniciar_db()
        self.refrescar_datos_globales()
        self.mostrar_frame("inicio")

    def crear_frames(self):
        for k in ["inicio", "inventario", "venta", "compra", "historial"]:
            f = ctk.CTkFrame(self.main, fg_color="transparent")
            self.frames[k] = f
            getattr(self, f"setup_{k}")(f)

    def mostrar_frame(self, key):
        for k, f in self.frames.items(): f.pack_forget()
        for k, b in self.botones_menu.items(): b.configure(fg_color=("gray75", "gray25") if k == key else "transparent")
        self.frames[key].pack(fill="both", expand=True)
        if key == "inicio": self.actualizar_dashboard()

    # --- INICIO ---
    def setup_inicio(self, f):
        ctk.CTkLabel(f, text="Panel de Control", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        self.stats = ctk.CTkFrame(f); self.stats.pack(fill="x", pady=20)
        self.lbl_tot = ctk.CTkLabel(self.stats, text="...", font=ctk.CTkFont(size=18)); self.lbl_tot.pack(side="left", padx=20, pady=20)
        self.lbl_caja = ctk.CTkLabel(self.stats, text="...", font=ctk.CTkFont(size=18), text_color="#2ECC71"); self.lbl_caja.pack(side="right", padx=20, pady=20)
        
        btns = ctk.CTkFrame(f, fg_color="transparent"); btns.pack()
        ctk.CTkButton(btns, text="VENDER", width=200, height=80, fg_color="#2ECC71", command=lambda: self.mostrar_frame("venta")).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btns, text="COMPRAR", width=200, height=80, fg_color="#E67E22", command=lambda: self.mostrar_frame("compra")).grid(row=0, column=1, padx=10)

    def actualizar_dashboard(self):
        try:
            tot = db_consultar("SELECT count(*) FROM productos")[0][0]
            # Calculamos ventas totales de la historia
            caja = db_consultar("SELECT sum(total_renglon) FROM historial WHERE tipo_movimiento='VENTA'")[0][0] or 0
            self.lbl_tot.configure(text=f"Productos en Catálogo: {tot}")
            self.lbl_caja.configure(text=f"Ventas Históricas: ${caja:,.2f}")
        except: pass

    # --- INVENTARIO ---
    def setup_inventario(self, f):
        # Frame superior para Título, Botón y Búsqueda
        top = ctk.CTkFrame(f, fg_color="transparent")
        top.pack(fill="x", pady=10)
        
        # Título
        ctk.CTkLabel(top, text="Inventario", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        
        # NUEVO BOTÓN: Agregar Producto
        ctk.CTkButton(top, text="➕ Nuevo Producto", command=self.ventana_nuevo_producto, fg_color="#2ECC71", hover_color="#27AE60", width=120).pack(side="left", padx=20)
        
        # Buscador (Corregido el error del width)
        self.entry_inv = ctk.CTkEntry(top, placeholder_text="🔍 Buscar por nombre...", width=250)
        self.entry_inv.pack(side="right")
        self.entry_inv.bind("<KeyRelease>", lambda e: self.llenar_tree(self.tree_inv, db_listar_productos(self.entry_inv.get())))

        # Tabla
        cols = ("ID", "Tipo", "Nombre", "Genero", "Cant", "Precio")
        self.tree_inv = ttk.Treeview(f, columns=cols, show='headings')
        for c in cols: self.tree_inv.heading(c, text=c, command=lambda x=c: ordenar_treeview(self.tree_inv, x, False))
        
        self.tree_inv.column("ID", width=40)
        self.tree_inv.column("Precio", width=80)
        self.tree_inv.column("Cant", width=60)
        
        self.tree_inv.pack(fill="both", expand=True, pady=10)
        
        # Evento Doble Click para editar
        self.tree_inv.bind("<Double-1>", self.editar_producto)

    # --- VENTAS ---
    def setup_venta(self, f):
        ctk.CTkLabel(f, text="Nueva Venta", font=ctk.CTkFont(size=20)).pack(anchor="w")
        
        top = ctk.CTkFrame(f); top.pack(fill="x", pady=5)
        self.combo_v = AutocompleteCombobox(top, width=40); self.combo_v.pack(side="left", padx=5)
        self.entry_v_c = ctk.CTkEntry(top, placeholder_text="Cant", width=60); self.entry_v_c.pack(side="left", padx=5)
        
        # Campo de Precio (Auto-rellenable pero editable)
        self.entry_v_p = ctk.CTkEntry(top, placeholder_text="Precio", width=80); self.entry_v_p.pack(side="left", padx=5)
        
        # Evento: Al seleccionar producto, rellenar precio automáticamente
        self.combo_v.bind("<<ComboboxSelected>>", self.al_seleccionar_producto_venta)

        ctk.CTkButton(top, text="➕ Agregar", width=80, command=self.add_venta).pack(side="left", padx=10)

        self.tree_v = ttk.Treeview(f, columns=("Prod", "Cant", "Precio", "Subtotal"), show="headings", height=8)
        self.tree_v.heading("Prod", text="Producto"); self.tree_v.heading("Cant", text="Cant")
        self.tree_v.heading("Precio", text="Precio Unit."); self.tree_v.heading("Subtotal", text="Subtotal")
        self.tree_v.pack(fill="both", expand=True, pady=10)
        
        self.lbl_total_v = ctk.CTkLabel(f, text="TOTAL: $0.00", font=ctk.CTkFont(size=20, weight="bold"), text_color="#2ECC71")
        self.lbl_total_v.pack(pady=5)
        
        ctk.CTkButton(f, text="✅ FINALIZAR VENTA", height=50, fg_color="#2ECC71", command=self.fin_venta).pack(fill="x")

    def al_seleccionar_producto_venta(self, event):
        pid = self.combo_v.get_selected_id()
        if pid:
            precio = db_obtener_precio(pid)
            self.entry_v_p.delete(0, 'end')
            self.entry_v_p.insert(0, str(precio))

    # --- COMPRAS ---
    def setup_compra(self, f):
        ctk.CTkLabel(f, text="Ingreso de Stock (Compra)", font=ctk.CTkFont(size=20)).pack(anchor="w")
        self.var_new = ctk.BooleanVar()
        ctk.CTkSwitch(f, text="Producto Nuevo", variable=self.var_new, command=self.toggle_compra_ui).pack(anchor="w")
        
        self.fr_exist = ctk.CTkFrame(f, fg_color="transparent"); self.fr_exist.pack(fill="x")
        self.combo_c = AutocompleteCombobox(self.fr_exist, width=50); self.combo_c.pack(fill="x")
        self.combo_c.bind("<<ComboboxSelected>>", self.al_seleccionar_producto_compra)

        self.fr_new = ctk.CTkFrame(f, fg_color="transparent")
        self.ec_n = ctk.CTkEntry(self.fr_new, placeholder_text="Nombre"); self.ec_n.pack(side="left", fill="x", expand=True)
        self.ec_t = ctk.CTkEntry(self.fr_new, placeholder_text="Tipo"); self.ec_t.pack(side="left", padx=2)
        self.ec_g = ctk.CTkEntry(self.fr_new, placeholder_text="Gen"); self.ec_g.pack(side="left", padx=2)
        
        mid = ctk.CTkFrame(f, fg_color="transparent"); mid.pack(fill="x", pady=5)
        self.ec_c = ctk.CTkEntry(mid, placeholder_text="Cant", width=80); self.ec_c.pack(side="left")
        self.ec_p = ctk.CTkEntry(mid, placeholder_text="Costo Unit.", width=80); self.ec_p.pack(side="left", padx=5)
        
        ctk.CTkButton(mid, text="Agregar Lote", command=self.add_compra).pack(side="left", padx=10)

        self.tree_c = ttk.Treeview(f, columns=("Det", "Cant", "Costo", "Subtotal"), show="headings")
        self.tree_c.heading("Det", text="Detalle"); self.tree_c.heading("Cant", text="Cant")
        self.tree_c.heading("Costo", text="Costo"); self.tree_c.heading("Subtotal", text="Subtotal")
        self.tree_c.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkButton(f, text="🚚 REGISTRAR INGRESO", height=50, fg_color="#E67E22", command=self.fin_compra).pack(fill="x")
        self.toggle_compra_ui()

    def al_seleccionar_producto_compra(self, event):
        pid = self.combo_c.get_selected_id()
        if pid:
            p = db_obtener_precio(pid)
            self.ec_p.delete(0, 'end'); self.ec_p.insert(0, str(p))

    def toggle_compra_ui(self):
        if self.var_new.get(): self.fr_exist.pack_forget(); self.fr_new.pack(fill="x")
        else: self.fr_new.pack_forget(); self.fr_exist.pack(fill="x")

    # --- HISTORIAL ---
    def setup_historial(self, f):
        ctk.CTkLabel(f, text="Registro Detallado", font=ctk.CTkFont(size=20)).pack(anchor="w")
        cols = ("Ticket", "Fecha", "Mov", "Producto", "Cant", "Precio Unit", "Total")
        self.tree_h = ttk.Treeview(f, columns=cols, show='headings')
        for c in cols: self.tree_h.heading(c, text=c)
        self.tree_h.column("Ticket", width=120); self.tree_h.column("Precio Unit", width=80); self.tree_h.column("Total", width=80)
        self.tree_h.pack(fill="both", expand=True)

    # --- LÓGICA ---
    def refrescar_datos_globales(self):
        prods = db_listar_productos()
        self.llenar_tree(self.tree_inv, prods)
        self.llenar_tree(self.tree_h, db_consultar("SELECT ticket_id, fecha, tipo_movimiento, producto_nombre, cantidad, precio_unitario, total_renglon FROM historial ORDER BY id DESC"))
        
        lv, mv, lc, mc = [], {}, [], {}
        for pid, t, n, g, c, p in prods:
            txt = f"{n} - {t} ({g})"
            if c > 0: lv.append(f"{txt} | ${p} | Stock: {c}"); mv[f"{txt} | ${p} | Stock: {c}"] = pid
            lc.append(txt); mc[txt] = pid
        self.combo_v.set_completion_list(lv, mv)
        self.combo_c.set_completion_list(lc, mc)

    def llenar_tree(self, tree, datos):
        for i in tree.get_children(): tree.delete(i)
        for d in datos: tree.insert("", "end", values=d)

    # Ventas
    def add_venta(self):
        pid = self.combo_v.get_selected_id()
        c = self.entry_v_c.get()
        p = self.entry_v_p.get()
        if pid and c and p:
            sub = int(c) * float(p)
            self.carrito_ventas.append({'id':pid, 'cantidad':int(c), 'precio':float(p), 'nombre': self.combo_v.get().split('|')[0]})
            self.tree_v.insert("", "end", values=(self.combo_v.get(), c, f"${p}", f"${sub}"))
            self.entry_v_c.delete(0,'end'); self.entry_v_p.delete(0,'end'); self.combo_v.set("")
            self.calc_total_venta()
    
    def calc_total_venta(self):
        tot = sum(item['cantidad'] * item['precio'] for item in self.carrito_ventas)
        self.lbl_total_v.configure(text=f"TOTAL: ${tot:,.2f}")

    def fin_venta(self):
        if self.carrito_ventas and db_procesar_venta(self.carrito_ventas) == "OK":
            messagebox.showinfo("OK", "Venta Guardada"); self.carrito_ventas=[]
            for i in self.tree_v.get_children(): self.tree_v.delete(i)
            self.lbl_total_v.configure(text="TOTAL: $0.00")
            self.refrescar_datos_globales()

    # Compras
    def add_compra(self):
        c = self.ec_c.get()
        p = self.ec_p.get()
        if not c or not p: return
        
        if self.var_new.get():
            item = {'nuevo':True, 'nombre':self.ec_n.get().upper(), 'tipo':self.ec_t.get(), 'genero':self.ec_g.get(), 'cantidad':int(c), 'precio':float(p)}
            txt = f"NUEVO: {item['nombre']}"
        else:
            pid = self.combo_c.get_selected_id()
            if not pid: return
            item = {'nuevo':False, 'id':pid, 'cantidad':int(c), 'precio':float(p), 'nombre_real': self.combo_c.get().split(' - ')[0]}
            txt = self.combo_c.get()
        
        sub = int(c) * float(p)
        self.carrito_compras.append(item)
        self.tree_c.insert("", "end", values=(txt, c, f"${p}", f"${sub}"))
        self.ec_c.delete(0,'end'); self.ec_p.delete(0,'end')
        if self.var_new.get(): self.ec_n.delete(0,'end'); self.ec_t.delete(0,'end'); self.ec_g.delete(0,'end')
        else: self.combo_c.set("")

    def fin_compra(self):
        if self.carrito_compras and db_procesar_compra(self.carrito_compras) == "OK":
            messagebox.showinfo("OK", "Ingreso Guardado"); self.carrito_compras=[]
            for i in self.tree_c.get_children(): self.tree_c.delete(i)
            self.refrescar_datos_globales()

    def ventana_nuevo_producto(self):
        # Crear ventana flotante
        win = ctk.CTkToplevel(self)
        win.title("Nuevo Producto")
        win.geometry("350x500")
        win.attributes("-topmost", True) # Que se mantenga siempre encima
        
        ctk.CTkLabel(win, text="Datos del Nuevo Producto", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Campos de entrada
        ctk.CTkLabel(win, text="Nombre:").pack(pady=(5,0))
        en = ctk.CTkEntry(win, placeholder_text="Ej: Remera Nike"); en.pack()
        
        ctk.CTkLabel(win, text="Tipo:").pack(pady=(5,0))
        et = ctk.CTkEntry(win, placeholder_text="Ej: Remera"); et.pack()
        
        ctk.CTkLabel(win, text="Género:").pack(pady=(5,0))
        eg = ctk.CTkEntry(win, placeholder_text="Ej: Hombre/Mujer/Uni"); eg.pack()
        
        ctk.CTkLabel(win, text="Precio Base ($):").pack(pady=(5,0))
        ep = ctk.CTkEntry(win, placeholder_text="0.0"); ep.pack()
        
        ctk.CTkLabel(win, text="Stock Inicial:").pack(pady=(5,0))
        ec = ctk.CTkEntry(win, placeholder_text="0"); ec.pack()

        def guardar_nuevo():
            nom = en.get().strip().upper()
            tip = et.get().strip().capitalize()
            gen = eg.get().strip().capitalize()
            pre = ep.get().strip()
            can = ec.get().strip()

            if not nom or not tip or not gen or not pre or not can:
                messagebox.showwarning("Faltan datos", "Por favor completa todos los campos")
                return
            
            try:
                # Insertamos directo en la base de datos
                conn = sqlite3.connect("negocio.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO productos (tipo, nombre, genero, cantidad, precio) VALUES (?,?,?,?,?)", 
                              (tip, nom, gen, int(can), float(pre)))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Éxito", "Producto creado correctamente")
                win.destroy()
                self.refrescar_datos_globales() # Actualizar la tabla de atrás
                
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Ya existe un producto con ese Nombre, Tipo y Género.")
            except ValueError:
                messagebox.showerror("Error", "Precio y Cantidad deben ser números.")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {e}")

        ctk.CTkButton(win, text="Guardar Producto", command=guardar_nuevo, fg_color="#2ECC71", hover_color="#27AE60").pack(pady=20)

    # Editar
    def editar_producto(self, event):
        item = self.tree_inv.focus(); 
        if not item: return
        vals = self.tree_inv.item(item)['values']
        win = ctk.CTkToplevel(self); win.title("Editar"); win.geometry("300x350"); win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="Tipo:").pack(); et=ctk.CTkEntry(win); et.insert(0,vals[1]); et.pack()
        ctk.CTkLabel(win, text="Nombre:").pack(); en=ctk.CTkEntry(win); en.insert(0,vals[2]); en.pack()
        ctk.CTkLabel(win, text="Género:").pack(); eg=ctk.CTkEntry(win); eg.insert(0,vals[3]); eg.pack()
        ctk.CTkLabel(win, text="Stock:").pack(); ec=ctk.CTkEntry(win); ec.insert(0,vals[4]); ec.pack()
        ctk.CTkLabel(win, text="Precio:").pack(); ep=ctk.CTkEntry(win); ep.insert(0,vals[5]); ep.pack()
        def save():
            if db_actualizar_producto(vals[0], et.get(), en.get(), eg.get(), int(ec.get()), float(ep.get())) == "OK":
                win.destroy(); self.refrescar_datos_globales()
        ctk.CTkButton(win, text="Guardar", command=save).pack(pady=20)

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
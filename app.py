# =============================================================================
# DOMINAN PRO - Versión SQLite + Mobile First
# =============================================================================

import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
st.set_page_config(
    page_title="DomiNan Pro",
    page_icon="🏍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stButton > button { width: 100%; padding: 0.75rem; font-size: 1rem; }
    .stForm > .stButton > button { width: 100%; }
    h1 { font-size: 1.8rem; }
    h2 { font-size: 1.4rem; }
    h3 { font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# BASE DE DATOS
# =============================================================================
DB_PATH = "dominan.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS zonas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        precio_base INTEGER NOT NULL DEFAULT 7000
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS lugares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        zona_id INTEGER,
        visitas INTEGER DEFAULT 0,
        ultima_visita TEXT,
        FOREIGN KEY (zona_id) REFERENCES zonas(id) ON DELETE SET NULL
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS direcciones_lugares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lugar_id INTEGER NOT NULL,
        direccion TEXT NOT NULL,
        FOREIGN KEY (lugar_id) REFERENCES lugares(id) ON DELETE CASCADE
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS domicilios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lugar_id INTEGER,
        direccion TEXT NOT NULL,
        zona_id INTEGER,
        valor INTEGER NOT NULL DEFAULT 0,
        propina INTEGER NOT NULL DEFAULT 0,
        fecha TEXT NOT NULL,
        FOREIGN KEY (lugar_id) REFERENCES lugares(id) ON DELETE SET NULL,
        FOREIGN KEY (zona_id) REFERENCES zonas(id) ON DELETE SET NULL
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concepto TEXT NOT NULL,
        valor INTEGER NOT NULL DEFAULT 0,
        fecha TEXT NOT NULL
    )""")
    
    c.execute("SELECT COUNT(*) as count FROM zonas")
    if c.fetchone()["count"] == 0:
        c.executemany("INSERT INTO zonas (nombre, precio_base) VALUES (?, ?)",
            [("Zona Norte", 7000), ("Zona Sur", 7500), ("Zona Centro", 6000)])
    
    conn.commit()
    conn.close()

init_db()

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def formatear_moneda(valor):
    return f"${int(valor):,}"

def obtener_fecha_hoy():
    return datetime.now().strftime("%Y-%m-%d")

def obtener_hora_actual():
    return datetime.now().strftime("%H:%M")

def obtener_fecha_hora():
    return f"{obtener_fecha_hoy()} {obtener_hora_actual()}"

# =============================================================================
# FUNCIONES DE BASE DE DATOS
# =============================================================================
def get_zonas():
    conn = get_db()
    zonas = conn.execute("SELECT * FROM zonas ORDER BY nombre").fetchall()
    conn.close()
    return zonas

def get_lugares(busqueda=""):
    conn = get_db()
    if busqueda:
        query = """SELECT l.*, z.nombre as zona_nombre, z.precio_base
            FROM lugares l LEFT JOIN zonas z ON l.zona_id = z.id
            WHERE l.nombre LIKE ? ORDER BY l.visitas DESC"""
        lugares = conn.execute(query, (f"%{busqueda}%",)).fetchall()
    else:
        query = """SELECT l.*, z.nombre as zona_nombre, z.precio_base
            FROM lugares l LEFT JOIN zonas z ON l.zona_id = z.id
            ORDER BY l.visitas DESC"""
        lugares = conn.execute(query).fetchall()
    conn.close()
    return lugares

def get_direcciones_lugar(lugar_id):
    conn = get_db()
    dirs = conn.execute("SELECT * FROM direcciones_lugares WHERE lugar_id = ?", (lugar_id,)).fetchall()
    conn.close()
    return dirs

def get_domicilios_filtrados(busqueda="", fecha_inicio=None, fecha_fin=None):
    conn = get_db()
    query = """SELECT d.*, l.nombre as lugar_nombre, z.nombre as zona_nombre
        FROM domicilios d
        LEFT JOIN lugares l ON d.lugar_id = l.id
        LEFT JOIN zonas z ON d.zona_id = z.id WHERE 1=1"""
    params = []
    if busqueda:
        query += " AND (l.nombre LIKE ? OR d.direccion LIKE ?)"
        params.extend([f"%{busqueda}%", f"%{busqueda}%"])
    if fecha_inicio:
        query += " AND d.fecha >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND d.fecha <= ?"
        params.append(fecha_fin + " 23:59:59")
    query += " ORDER BY d.id DESC"
    domicilios = conn.execute(query, params).fetchall()
    conn.close()
    return domicilios

def get_gastos_filtrados(busqueda="", fecha_inicio=None, fecha_fin=None):
    conn = get_db()
    query = "SELECT * FROM gastos WHERE 1=1"
    params = []
    if busqueda:
        query += " AND concepto LIKE ?"
        params.append(f"%{busqueda}%")
    if fecha_inicio:
        query += " AND fecha >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND fecha <= ?"
        params.append(fecha_fin + " 23:59:59")
    query += " ORDER BY id DESC"
    gastos = conn.execute(query, params).fetchall()
    conn.close()
    return gastos

def get_domicilios_hoy():
    hoy = obtener_fecha_hoy()
    conn = get_db()
    doms = conn.execute("SELECT * FROM domicilios WHERE fecha LIKE ?", (f"{hoy}%",)).fetchall()
    conn.close()
    return doms

def get_gastos_hoy():
    hoy = obtener_fecha_hoy()
    conn = get_db()
    gastos = conn.execute("SELECT * FROM gastos WHERE fecha LIKE ?", (f"{hoy}%",)).fetchall()
    conn.close()
    return gastos

def insertar_zona(nombre, precio):
    conn = get_db()
    try:
        conn.execute("INSERT INTO zonas (nombre, precio_base) VALUES (?, ?)", (nombre, precio))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def eliminar_zona(zona_id):
    conn = get_db()
    conn.execute("DELETE FROM zonas WHERE id = ?", (zona_id,))
    conn.commit()
    conn.close()

def actualizar_precio_zona(zona_id, nuevo_precio):
    conn = get_db()
    conn.execute("UPDATE zonas SET precio_base = ? WHERE id = ?", (nuevo_precio, zona_id))
    conn.commit()
    conn.close()

def insertar_lugar(nombre, zona_id, direccion):
    conn = get_db()
    try:
        cursor = conn.execute("INSERT INTO lugares (nombre, zona_id) VALUES (?, ?)", (nombre, zona_id))
        lugar_id = cursor.lastrowid
        conn.execute("INSERT INTO direcciones_lugares (lugar_id, direccion) VALUES (?, ?)", (lugar_id, direccion))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def agregar_direccion_lugar(lugar_id, direccion):
    conn = get_db()
    conn.execute("INSERT INTO direcciones_lugares (lugar_id, direccion) VALUES (?, ?)", (lugar_id, direccion))
    conn.commit()
    conn.close()

def eliminar_direccion_lugar(dir_id):
    conn = get_db()
    conn.execute("DELETE FROM direcciones_lugares WHERE id = ?", (dir_id,))
    conn.commit()
    conn.close()

def eliminar_lugar(lugar_id):
    conn = get_db()
    conn.execute("DELETE FROM lugares WHERE id = ?", (lugar_id,))
    conn.commit()
    conn.close()

def actualizar_zona_lugar(lugar_id, zona_id):
    conn = get_db()
    conn.execute("UPDATE lugares SET zona_id = ? WHERE id = ?", (zona_id, lugar_id))
    conn.commit()
    conn.close()

def registrar_domicilio(lugar_id, direccion, zona_id, valor, propina):
    conn = get_db()
    fecha = obtener_fecha_hora()
    conn.execute("""INSERT INTO domicilios (lugar_id, direccion, zona_id, valor, propina, fecha) 
        VALUES (?, ?, ?, ?, ?, ?)""", (lugar_id, direccion, zona_id, valor, propina, fecha))
    if lugar_id:
        conn.execute("""UPDATE lugares SET visitas = visitas + 1, ultima_visita = ? WHERE id = ?""",
            (fecha, lugar_id))
    conn.commit()
    conn.close()

def eliminar_domicilio(dom_id):
    conn = get_db()
    conn.execute("DELETE FROM domicilios WHERE id = ?", (dom_id,))
    conn.commit()
    conn.close()

def registrar_gasto(concepto, valor):
    conn = get_db()
    fecha = obtener_fecha_hora()
    conn.execute("INSERT INTO gastos (concepto, valor, fecha) VALUES (?, ?, ?)", (concepto, valor, fecha))
    conn.commit()
    conn.close()

def eliminar_gasto(gasto_id):
    conn = get_db()
    conn.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
    conn.commit()
    conn.close()

def get_top_lugares(limit=10):
    conn = get_db()
    lugares = conn.execute("""SELECT l.*, z.nombre as zona_nombre 
        FROM lugares l LEFT JOIN zonas z ON l.zona_id = z.id 
        ORDER BY l.visitas DESC LIMIT ?""", (limit,)).fetchall()
    conn.close()
    return lugares

# =============================================================================
# NAVEGACIÓN PRINCIPAL
# =============================================================================
st.title("🏍️ DomiNan Pro")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    btn_domicilio = st.button("📝\nNuevo", use_container_width=True, type="primary")
with nav_col2:
    btn_historial = st.button("📋\nHistorial", use_container_width=True)
with nav_col3:
    btn_gastos = st.button("💸\nGastos", use_container_width=True)
with nav_col4:
    btn_mas = st.button("⚙️\nMás", use_container_width=True)

st.markdown("---")

# =============================================================================
# VISTA: NUEVO DOMICILIO
# =============================================================================
if btn_domicilio or not any([btn_historial, btn_gastos, btn_mas]):
    doms_hoy = get_domicilios_hoy()
    gastos_hoy_list = get_gastos_hoy()
    total_ingresos = sum(d["valor"] + d["propina"] for d in doms_hoy)
    total_gastos = sum(g["valor"] for g in gastos_hoy_list)
    balance = total_ingresos - total_gastos
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("📦 Hoy", len(doms_hoy))
    with col_m2:
        st.metric("💰 Ingresos", formatear_moneda(total_ingresos))
    with col_m3:
        st.metric("📊 Balance", formatear_moneda(balance))
    
    st.markdown("---")
    st.subheader("📝 Registrar Nuevo Domicilio")
    
    if "propina_calc" not in st.session_state:
        st.session_state.propina_calc = 0
    
    busqueda = st.text_input("🔍 Buscar lugar:", placeholder="Escribe el nombre del lugar...", key="buscador_domicilio")
    lugares = get_lugares(busqueda)
    
    with st.form("form_domicilio", clear_on_submit=True):
        opciones_lugar = ["➕ Crear nuevo lugar"] + [l["nombre"] for l in lugares]
        lugar_seleccionado = st.selectbox("📍 Selecciona el lugar:", options=opciones_lugar)
        
        if lugar_seleccionado == "➕ Crear nuevo lugar":
            nombre_nuevo = st.text_input("Nombre del lugar:")
            zonas = get_zonas()
            zona_nueva = st.selectbox("Zona:", options=[z["nombre"] for z in zonas])
            direccion_nueva = st.text_input("Dirección:")
            lugar_final_id = None
            zona_final_id = next((z["id"] for z in zonas if z["nombre"] == zona_nueva), None)
            direccion_final = direccion_nueva
            precio_sugerido = next((z["precio_base"] for z in zonas if z["nombre"] == zona_nueva), 7000)
        else:
            lugar_obj = next((l for l in lugares if l["nombre"] == lugar_seleccionado), None)
            lugar_final_id = lugar_obj["id"] if lugar_obj else None
            zona_final_id = lugar_obj["zona_id"] if lugar_obj else None
            precio_sugerido = lugar_obj["precio_base"] if lugar_obj and lugar_obj["precio_base"] else 7000
            
            direcciones = get_direcciones_lugar(lugar_final_id)
            if direcciones:
                opciones_dir = [d["direccion"] for d in direcciones] + ["➕ Escribir nueva dirección"]
                opcion_direccion = st.selectbox("📍 Dirección:", options=opciones_dir)
                if opcion_direccion == "➕ Escribir nueva dirección":
                    direccion_final = st.text_input("Nueva dirección:")
                else:
                    direccion_final = opcion_direccion
            else:
                direccion_final = st.text_input("📍 Dirección:")
            
            zonas = get_zonas()
            zona_nombre_actual = lugar_obj["zona_nombre"] if lugar_obj else None
            index_zona = 0
            if zona_nombre_actual:
                nombres_zonas = [z["nombre"] for z in zonas]
                if zona_nombre_actual in nombres_zonas:
                    index_zona = nombres_zonas.index(zona_nombre_actual)
            
            zona_seleccionada_nombre = st.selectbox("🗺️ Zona:", options=[z["nombre"] for z in zonas], index=index_zona)
            zona_final_id = next((z["id"] for z in zonas if z["nombre"] == zona_seleccionada_nombre), zona_final_id)
            precio_sugerido = next((z["precio_base"] for z in zonas if z["nombre"] == zona_seleccionada_nombre), precio_sugerido)
        
        st.info(f"📅 **{obtener_fecha_hoy()}** | 🕒 **{obtener_hora_actual()}**")
        
        valor_final = st.number_input("💵 Valor del domicilio:", min_value=0, step=500, value=precio_sugerido)
        
        st.markdown("🎁 **Propina:**")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            if st.form_submit_button("10%", use_container_width=True):
                st.session_state.propina_calc = int(valor_final * 0.10)
        with col_p2:
            if st.form_submit_button("15%", use_container_width=True):
                st.session_state.propina_calc = int(valor_final * 0.15)
        with col_p3:
            if st.form_submit_button("20%", use_container_width=True):
                st.session_state.propina_calc = int(valor_final * 0.20)
        with col_p4:
            if st.form_submit_button("0%", use_container_width=True):
                st.session_state.propina_calc = 0
        
        propina = st.number_input("💵 Valor de propina:", min_value=0, step=500, value=st.session_state.propina_calc)
        total = valor_final + propina
        st.success(f"**💰 Total: {formatear_moneda(total)}**")
        
        guardar = st.form_submit_button("💾 GUARDAR DOMICILIO", type="primary", use_container_width=True)
    
    if guardar:
        if lugar_seleccionado == "➕ Crear nuevo lugar":
            if not nombre_nuevo.strip() or not direccion_nueva.strip():
                st.error("⚠️ Completa el nombre y dirección.")
            else:
                if insertar_lugar(nombre_nuevo, zona_final_id, direccion_nueva):
                    conn = get_db()
                    lugar_creado = conn.execute("SELECT id FROM lugares WHERE nombre = ?", (nombre_nuevo,)).fetchone()
                    conn.close()
                    lugar_final_id = lugar_creado["id"]
                    registrar_domicilio(lugar_final_id, direccion_nueva, zona_final_id, int(valor_final), int(propina))
                    st.session_state.propina_calc = 0
                    st.success(f"✅ ¡Registrado! Total: {formatear_moneda(total)}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ Ese lugar ya existe.")
        else:
            if not direccion_final.strip():
                st.error("⚠️ Ingresa la dirección.")
            else:
                direcciones_existentes = [d["direccion"] for d in get_direcciones_lugar(lugar_final_id)]
                if direccion_final not in direcciones_existentes:
                    agregar_direccion_lugar(lugar_final_id, direccion_final)
                registrar_domicilio(lugar_final_id, direccion_final, zona_final_id, int(valor_final), int(propina))
                st.session_state.propina_calc = 0
                st.success(f"✅ ¡Registrado! Total: {formatear_moneda(total)}")
                st.balloons()
                st.rerun()

# =============================================================================
# VISTA: HISTORIAL
# =============================================================================
elif btn_historial:
    st.subheader("📋 Historial de Domicilios")
    busqueda_hist = st.text_input("🔍 Buscar:", placeholder="Lugar o dirección...", key="busqueda_hist")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_inicio = st.date_input("📅 Desde:", value=datetime.now() - timedelta(days=30), key="fecha_ini_hist")
    with col_f2:
        fecha_fin = st.date_input("📅 Hasta:", value=datetime.now(), key="fecha_fin_hist")
    
    domicilios = get_domicilios_filtrados(busqueda_hist, fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"))
    total_filtrado = sum(d["valor"] + d["propina"] for d in domicilios)
    st.info(f"📊 **{len(domicilios)}** domicilios | 💰 Total: **{formatear_moneda(total_filtrado)}**")
    
    if not domicilios:
        st.warning("No hay domicilios.")
    else:
        for dom in domicilios[:30]:
            with st.container(border=True):
                st.markdown(f"**📍 {dom['lugar_nombre'] or 'Sin lugar'}**")
                st.caption(f"📌 {dom['direccion']}")
                st.caption(f"🗺️ {dom['zona_nombre'] or 'Sin zona'} | 🕒 {dom['fecha']}")
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d1:
                    st.metric("Valor", formatear_moneda(dom["valor"]))
                with col_d2:
                    st.metric("Propina", formatear_moneda(dom["propina"]))
                with col_d3:
                    st.metric("Total", formatear_moneda(dom["valor"] + dom["propina"]))
                if st.button("🗑️ Eliminar", key=f"del_dom_{dom['id']}", use_container_width=True):
                    eliminar_domicilio(dom["id"])
                    st.rerun()
            st.markdown("---")

# =============================================================================
# VISTA: GASTOS
# =============================================================================
elif btn_gastos:
    st.subheader("💸 Registrar Gasto")
    
    GASTOS_FRECUENTES = {
        "Gasolina": 15000, "Almuerzo": 12000, "Cena": 10000,
        "Mantenimiento moto": 25000, "Carga celular": 3000,
        "Agua/Refresco": 2000, "Parqueadero": 3000, "Peaje": 5000, "Otro": 0
    }
    
    with st.form("form_gasto", clear_on_submit=True):
        concepto = st.selectbox("📋 Concepto:", options=list(GASTOS_FRECUENTES.keys()))
        if concepto == "Otro":
            concepto_final = st.text_input("Describe el gasto:")
        else:
            concepto_final = concepto
        
        valor_sugerido = GASTOS_FRECUENTES[concepto]
        valor_gasto = st.number_input("💵 Valor:", min_value=0, step=500, value=valor_sugerido if valor_sugerido > 0 else 0)
        st.info(f"📅 **{obtener_fecha_hoy()}** | 🕒 **{obtener_hora_actual()}**")
        guardar_gasto = st.form_submit_button("💾 GUARDAR GASTO", type="primary", use_container_width=True)
    
    if guardar_gasto:
        if not concepto_final.strip():
            st.error("⚠️ Ingresa un concepto.")
        elif valor_gasto == 0:
            st.error("⚠️ El valor no puede ser cero.")
        else:
            registrar_gasto(concepto_final, int(valor_gasto))
            st.success(f"✅ Registrado: {concepto_final} - {formatear_moneda(valor_gasto)}")
            st.rerun()
    
    st.markdown("---")
    st.subheader("📋 Gastos Recientes")
    gastos = get_gastos_filtrados()[:15]
    for gasto in gastos:
        with st.container(border=True):
            st.markdown(f"**💸 {gasto['concepto']}**")
            st.caption(f"🕒 {gasto['fecha']}")
            st.metric("Valor", formatear_moneda(gasto["valor"]))
            if st.button("🗑️", key=f"del_gas_{gasto['id']}", use_container_width=True):
                eliminar_gasto(gasto["id"])
                st.rerun()

# =============================================================================
# VISTA: MÁS (con session_state para recordar la selección)
# =============================================================================
elif btn_mas:
    st.subheader("⚙️ Más Opciones")
    
    if "vista_mas" not in st.session_state:
        st.session_state.vista_mas = "menu"
    
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("🗺️ Zonas", use_container_width=True):
            st.session_state.vista_mas = "zonas"
            st.rerun()
    with col_nav2:
        if st.button("📍 Lugares", use_container_width=True):
            st.session_state.vista_mas = "lugares"
            st.rerun()
    with col_nav3:
        if st.button("🏆 Top", use_container_width=True):
            st.session_state.vista_mas = "top"
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.vista_mas != "menu":
        if st.button("⬅️ Volver al menú", use_container_width=True):
            st.session_state.vista_mas = "menu"
            st.rerun()
        st.markdown("---")
    
    # --- ZONAS ---
    if st.session_state.vista_mas == "zonas":
        st.markdown("### 🗺️ Zonas y Tarifas")
        with st.form("form_nueva_zona"):
            col_z1, col_z2 = st.columns(2)
            with col_z1:
                nombre_zona = st.text_input("Nombre:")
            with col_z2:
                precio_zona = st.number_input("Precio:", min_value=0, step=500, value=7000)
            if st.form_submit_button("➕ Agregar Zona", use_container_width=True):
                if nombre_zona.strip():
                    if insertar_zona(nombre_zona.strip(), int(precio_zona)):
                        st.success(f"✅ Zona '{nombre_zona}' agregada.")
                        st.rerun()
                    else:
                        st.error("⚠️ Esa zona ya existe.")
        
        st.markdown("---")
        st.markdown("**Zonas registradas:**")
        zonas = get_zonas()
        if not zonas:
            st.info("No hay zonas registradas.")
        else:
            for zona in zonas:
                with st.container(border=True):
                    col_z1, col_z2, col_z3 = st.columns([3, 1, 1])
                    col_z1.markdown(f"**{zona['nombre']}** - {formatear_moneda(zona['precio_base'])}")
                    nuevo_precio = col_z2.number_input("Precio:", value=zona["precio_base"], min_value=0, step=500, key=f"precio_zona_{zona['id']}")
                    if col_z3.button("💾", key=f"guardar_zona_{zona['id']}"):
                        actualizar_precio_zona(zona["id"], int(nuevo_precio))
                        st.success("Precio actualizado.")
                        st.rerun()
                    if st.button("🗑️", key=f"del_zona_{zona['id']}"):
                        eliminar_zona(zona["id"])
                        st.rerun()
    
    # --- LUGARES ---
    elif st.session_state.vista_mas == "lugares":
        st.markdown("### 📍 Lugares de Entrega")
        zonas = get_zonas()
        
        with st.form("form_nuevo_lugar"):
            nombre_lugar = st.text_input("Nombre del lugar:")
            zona_lugar = st.selectbox("Zona:", options=[z["nombre"] for z in zonas])
            direccion_lugar = st.text_input("Dirección inicial:")
            if st.form_submit_button("➕ Agregar Lugar", use_container_width=True):
                if nombre_lugar.strip() and direccion_lugar.strip():
                    zona_id = next((z["id"] for z in zonas if z["nombre"] == zona_lugar), None)
                    if insertar_lugar(nombre_lugar, zona_id, direccion_lugar):
                        st.success(f"✅ Lugar '{nombre_lugar}' agregado.")
                        st.rerun()
                    else:
                        st.error("⚠️ Ese lugar ya existe.")
        
        st.markdown("---")
        st.markdown("**Lugares registrados:**")
        lugares = get_lugares()
        if not lugares:
            st.info("No hay lugares registrados.")
        else:
            for lugar in lugares:
                with st.container(border=True):
                    st.markdown(f"**{lugar['nombre']}**")
                    st.caption(f"🗺️ {lugar['zona_nombre'] or 'Sin zona'} | 🔄 {lugar['visitas']} visitas")
                    st.markdown("**Direcciones:**")
                    direcciones = get_direcciones_lugar(lugar["id"])
                    for dir_obj in direcciones:
                        col_dir1, col_dir2 = st.columns([4, 1])
                        col_dir1.write(f"  - {dir_obj['direccion']}")
                        if col_dir2.button("🗑️", key=f"del_dir_{dir_obj['id']}"):
                            eliminar_direccion_lugar(dir_obj["id"])
                            st.rerun()
                    
                    nueva_dir = st.text_input("Nueva dirección", key=f"add_dir_{lugar['id']}", placeholder="Ej: Carrera 10 #5-20")
                    if st.button("➕ Agregar dirección", key=f"btn_add_{lugar['id']}", use_container_width=True):
                        if nueva_dir.strip():
                            agregar_direccion_lugar(lugar["id"], nueva_dir)
                            st.success("Dirección agregada.")
                            st.rerun()
                    
                    zonas_list = [z["nombre"] for z in zonas]
                    index_zona_actual = 0
                    if lugar["zona_nombre"] and lugar["zona_nombre"] in zonas_list:
                        index_zona_actual = zonas_list.index(lugar["zona_nombre"])
                    nueva_zona = st.selectbox("Cambiar zona:", options=zonas_list, index=index_zona_actual, key=f"cambiar_zona_{lugar['id']}")
                    if st.button("💾 Actualizar zona", key=f"btn_zona_{lugar['id']}", use_container_width=True):
                        zona_id = next((z["id"] for z in zonas if z["nombre"] == nueva_zona), None)
                        actualizar_zona_lugar(lugar["id"], zona_id)
                        st.success("Zona actualizada.")
                        st.rerun()
                    
                    if st.button("🗑️ Eliminar lugar", key=f"del_lugar_{lugar['id']}", use_container_width=True):
                        eliminar_lugar(lugar["id"])
                        st.rerun()
    
    # --- TOP ---
    elif st.session_state.vista_mas == "top":
        st.markdown("### 🏆 Lugares Más Frecuentes")
        top_lugares = get_top_lugares(10)
        if not top_lugares:
            st.info("No hay lugares registrados.")
        else:
            for idx, lugar in enumerate(top_lugares):
                with st.container(border=True):
                    st.markdown(f"**#{idx + 1} {lugar['nombre']}**")
                    st.caption(f"🗺️ {lugar['zona_nombre'] or 'Sin zona'}")
                    st.metric("Visitas", lugar["visitas"])
                    st.caption(f"Última: {lugar['ultima_visita'] or 'N/A'}")
    
    # --- MENÚ ---
    else:
        st.info("👆 Selecciona una opción arriba para gestionar.")
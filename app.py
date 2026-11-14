import streamlit as st
import json
from datetime import datetime

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
st.set_page_config(page_title="DomiVillavo", page_icon="🏍️", layout="centered")

ARCHIVO = "domivillavo.json"

# =============================================================================
# ESTILO BÁSICO PARA MÓVIL
# =============================================================================
st.markdown("""
<style>
    .stButton>button { width: 100%; }
    .metric-card { background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 5px 0; }
    h1 { font-size: 1.5em; }
    h2 { font-size: 1.2em; }
    h3 { font-size: 1em; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# ZONAS BASE (editables desde la app)
# =============================================================================
ZONAS_BASE = {
    "Comuna 1 - Norte": {
        "Nueva Granada": 9000, "Galán": 9500, "Los Cerezos": 9000,
        "Cataluña": 9500, "Los Andes": 9000,
    },
    "Comuna 2 - Centro": {
        "Centro": 8000, "La Salle": 8000, "Nueva Andalucía": 8500,
        "San Antonio": 8000,
    },
    "Comuna 3 - Sur (Amarilo)": {
        "Hacienda Rosablanca": 5000, "Prado Verde": 5000,
        "Llano Alto": 5500, "Caracolí": 5500,
        "Amarilo Zainos": 6000, "Amarilo Mapire": 6000,
        "Villa España": 7000, "Maracos": 7500, "El Barzal": 8000,
    },
    "Comuna 4 - Occidente": {
        "El Recreo": 11000, "Cedritos": 12000, "Villa Fabiola": 12000,
    },
    "Comuna 5 - Noroccidente": {
        "Acapulco": 12500, "Almendros": 12500, "El Remanso": 12000,
    },
    "Comuna 6 - Suroriental": {
        "Pastrana": 13000, "Macarena": 13000, "Amaral": 13000,
    },
    "Comuna 7 - Oriente": {
        "Alto Pompeya": 14000, "Los Arrayanes": 14000, "San Cristóbal": 14000,
    },
    "Comuna 8 - Suroccidente": {
        "La Grama": 10500, "Evaristo Sourdis": 11000,
    },
    "Municipios": {
        "Acacías": 18000, "Restrepo": 20000, "Cumaral": 22000,
    },
    "Personalizado": {"Otro": 0},
}

# =============================================================================
# PERSISTENCIA
# =============================================================================
def cargar():
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            d = json.load(f)
            for k in ["ingresos", "gastos", "clientes", "zonas"]:
                if k not in d:
                    d[k] = ZONAS_BASE if k == "zonas" else []
            return d
    except:
        return {
            "ingresos": [], "gastos": [], "clientes": [],
            "zonas": ZONAS_BASE
        }

def guardar(d):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

# =============================================================================
# CARGAR DATOS
# =============================================================================
datos = cargar()

# =============================================================================
# CABECERA
# =============================================================================
st.title("🏍️ DomiVillavo")
st.caption(f"{datetime.now().strftime('%d/%m/%Y - %H:%M')}")
st.markdown("---")

# =============================================================================
# NAVEGACIÓN
# =============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "➕ Nuevo", "📇 Clientes", "📊 Resumen", "📜 Historial", "⚙️ Zonas"
])

# =============================================================================
# TAB 1: NUEVO REGISTRO
# =============================================================================
with tab1:
    st.subheader("Nuevo Registro")
    
    tipo = st.radio("Tipo:", ["💰 Ingreso (Entrega)", "💸 Gasto"], horizontal=True)
    
    if tipo == "💰 Ingreso (Entrega)":
        # Buscador de cliente
        busqueda = st.text_input("🔍 Buscar cliente:", placeholder="Nombre, teléfono o barrio...")
        clientes = datos.get("clientes", [])
        cliente_sel = None
        
        if busqueda.strip():
            t = busqueda.lower()
            resultados = [c for c in clientes if t in c.get("nombre","").lower()
                         or t in c.get("telefono","").lower()
                         or t in c.get("direccion","").lower()]
        else:
            resultados = sorted(clientes, key=lambda x: x.get("visitas",0), reverse=True)
        
        if resultados:
            for c in resultados[:4]:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    fav = "⭐" if c.get("favorito") else ""
                    st.write(f"{fav} **{c['nombre']}**")
                    st.caption(f"📱 {c.get('telefono','')} | 📍 {c.get('direccion','')}")
                with col_b:
                    if st.button("Usar", key=f"u_{c.get('nombre','')}"):
                        cliente_sel = c
                        st.rerun()
        
        # Formulario
        if cliente_sel:
            nombre = st.text_input("Cliente:", value=cliente_sel["nombre"])
            telefono = st.text_input("Teléfono:", value=cliente_sel.get("telefono",""))
            direccion = st.text_input("Dirección:", value=cliente_sel.get("direccion",""))
            barrio_def = cliente_sel.get("barrio","")
            anillo_def = cliente_sel.get("anillo","")
        else:
            nombre = st.text_input("Cliente:")
            telefono = st.text_input("Teléfono:")
            direccion = st.text_input("Dirección:")
            barrio_def = ""
            anillo_def = ""
        
        zonas = datos.get("zonas", ZONAS_BASE)
        idx_a = list(zonas.keys()).index(anillo_def) if anillo_def in zonas else 0
        anillo = st.selectbox("Zona:", list(zonas.keys()), index=idx_a)
        barrios = list(zonas[anillo].keys())
        idx_b = barrios.index(barrio_def) if barrio_def in barrios else 0
        barrio = st.selectbox("Barrio:", barrios, index=idx_b)
        
        tarifa = zonas[anillo][barrio]
        if tarifa == 0:
            monto = st.number_input("Monto ($):", min_value=0, value=0, step=500)
        else:
            st.info(f"Tarifa sugerida: ${tarifa:,}")
            monto = st.number_input("Monto ($):", min_value=0, value=tarifa, step=500)
        
        favorito = st.checkbox("⭐ Cliente frecuente", value=cliente_sel.get("favorito", False) if cliente_sel else False)
        
        if st.button("✅ Registrar Ingreso", type="primary"):
            if not nombre.strip() or not direccion.strip():
                st.error("Nombre y dirección son obligatorios")
            elif monto == 0:
                st.error("El monto no puede ser cero")
            else:
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ingreso = {
                    "cliente": nombre, "telefono": telefono, "direccion": direccion,
                    "anillo": anillo, "barrio": barrio, "monto": int(monto),
                    "fecha": ahora,
                }
                datos["ingresos"].append(ingreso)
                
                # Actualizar cliente
                existe = None
                for c in datos["clientes"]:
                    if c.get("telefono") == telefono and telefono:
                        existe = c; break
                    elif c.get("nombre") == nombre and c.get("direccion") == direccion:
                        existe = c; break
                
                if existe:
                    existe["visitas"] = existe.get("visitas",0) + 1
                    existe["ultima_visita"] = ahora
                    existe["direccion"] = direccion
                    existe["barrio"] = barrio
                    existe["anillo"] = anillo
                    existe["favorito"] = favorito
                else:
                    datos["clientes"].append({
                        "nombre": nombre, "telefono": telefono, "direccion": direccion,
                        "barrio": barrio, "anillo": anillo, "visitas": 1,
                        "ultima_visita": ahora, "favorito": favorito,
                    })
                
                guardar(datos)
                st.success(f"✅ Ingreso registrado: ${monto:,}")
                st.rerun()
    
    else:
        # Formulario de gasto
        concepto = st.selectbox("Concepto:", [
            "⛽ Gasolina", "🍲 Almuerzo", "🌙 Cena", "🔧 Mantenimiento moto",
            "🔋 Carga celular", "💧 Agua", "🅿️ Parqueadero", "🛞 Llanta",
            "🏥 Farmacia", "📱 Datos", "📝 Otro"
        ])
        detalle = st.text_input("Detalle (opcional):")
        monto = st.number_input("Monto ($):", min_value=0, value=0, step=500)
        
        if st.button("✅ Registrar Gasto", type="primary"):
            if not concepto or monto == 0:
                st.error("Concepto y monto son obligatorios")
            else:
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                datos["gastos"].append({
                    "concepto": concepto, "detalle": detalle, "monto": int(monto),
                    "fecha": ahora,
                })
                guardar(datos)
                st.success(f"✅ Gasto registrado: ${monto:,}")
                st.rerun()

# =============================================================================
# TAB 2: CLIENTES
# =============================================================================
with tab2:
    st.subheader("Clientes")
    clientes = datos.get("clientes", [])
    
    if not clientes:
        st.info("Sin clientes registrados")
    else:
        busq = st.text_input("🔍 Buscar:", placeholder="Nombre, teléfono, barrio...")
        
        if busq.strip():
            t = busq.lower()
            lista = [c for c in clientes if t in c.get("nombre","").lower()
                    or t in c.get("telefono","").lower()
                    or t in c.get("barrio","").lower()]
        else:
            favs = [c for c in clientes if c.get("favorito")]
            otros = [c for c in clientes if not c.get("favorito")]
            lista = favs + otros
        
        st.caption(f"{len(lista)} clientes")
        
        for c in lista:
            with st.expander(f"{'⭐' if c.get('favorito') else '👤'} {c['nombre']}"):
                st.write(f"📱 {c.get('telefono','')}")
                st.write(f"📍 {c.get('direccion','')}")
                st.write(f"🗺️ {c.get('barrio','')} - {c.get('anillo','')}")
                st.write(f"🔁 {c.get('visitas',0)} visitas")
                st.write(f"📅 Última: {c.get('ultima_visita','')}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"{'Quitar ⭐' if c.get('favorito') else 'Poner ⭐'}",
                                key=f"f_{c.get('nombre','')}"):
                        c["favorito"] = not c.get("favorito", False)
                        guardar(datos); st.rerun()
                with col_b:
                    if st.button("🗑️ Eliminar", key=f"d_{c.get('nombre','')}"):
                        datos["clientes"].remove(c)
                        guardar(datos); st.rerun()

# =============================================================================
# TAB 3: RESUMEN
# =============================================================================
with tab3:
    st.subheader("Resumen")
    
    ingresos = datos.get("ingresos", [])
    gastos = datos.get("gastos", [])
    
    hoy = datetime.now().strftime("%Y-%m-%d")
    ing_hoy = sum(i["monto"] for i in ingresos if i.get("fecha","").startswith(hoy))
    gas_hoy = sum(g["monto"] for g in gastos if g.get("fecha","").startswith(hoy))
    total_ing = sum(i["monto"] for i in ingresos)
    total_gas = sum(g["monto"] for g in gastos)
    
    col1, col2 = st.columns(2)
    col1.metric("Ingresos hoy", f"${ing_hoy:,}")
    col2.metric("Gastos hoy", f"${gas_hoy:,}")
    
    col3, col4 = st.columns(2)
    col3.metric("Ingresos total", f"${total_ing:,}")
    col4.metric("Gastos total", f"${total_gas:,}")
    
    balance = total_ing - total_gas
    st.metric("💰 Balance neto", f"${balance:,}")
    
    st.markdown("---")
    st.subheader("Top 5 barrios")
    from collections import Counter
    contador = Counter(i.get("barrio","?") for i in ingresos)
    for barrio, cant in contador.most_common(5):
        st.write(f"**{barrio}**: {cant} entregas")
    
    st.markdown("---")
    st.subheader("Top 5 gastos")
    contador_g = Counter(g.get("concepto","?") for g in gastos)
    for conc, cant in contador_g.most_common(5):
        st.write(f"**{conc}**: {cant} registros")

# =============================================================================
# TAB 4: HISTORIAL
# =============================================================================
with tab4:
    st.subheader("Historial")
    
    filtro = st.radio("Ver:", ["Todo", "Ingresos", "Gastos"], horizontal=True)
    
    ingresos = datos.get("ingresos", [])
    gastos = datos.get("gastos", [])
    
    if filtro == "Ingresos":
        lista = [("ingreso", i) for i in ingresos]
    elif filtro == "Gastos":
        lista = [("gasto", g) for g in gastos]
    else:
        lista = [("ingreso", i) for i in ingresos] + [("gasto", g) for g in gastos]
    
    lista.sort(key=lambda x: x[1].get("fecha",""), reverse=True)
    
    st.caption(f"{len(lista)} registros")
    
    for tipo, item in lista[:50]:
        if tipo == "ingreso":
            icono = "📥"
            titulo = f"{item.get('cliente','')} - ${item.get('monto',0):,}"
            detalle = f"{item.get('barrio','')} | {item.get('direccion','')}"
        else:
            icono = "📤"
            titulo = f"{item.get('concepto','')} - ${item.get('monto',0):,}"
            detalle = item.get("detalle","")
        
        with st.expander(f"{icono} {item.get('fecha','')} - {titulo}"):
            st.write(detalle)
            if tipo == "ingreso":
                st.write(f"📱 {item.get('telefono','')}")

# =============================================================================
# TAB 5: ZONAS
# =============================================================================
with tab5:
    st.subheader("Gestionar Zonas")
    
    st.markdown("### Agregar barrio")
    with st.form("add"):
        opc = st.selectbox("Zona:", list(datos["zonas"].keys()) + ["➕ Nueva zona"])
        if opc == "➕ Nueva zona":
            nz = st.text_input("Nombre de la nueva zona:")
        else:
            nz = opc
        nb = st.text_input("Nombre del barrio:")
        nt = st.number_input("Tarifa ($):", min_value=0, value=5000, step=500)
        if st.form_submit_button("Agregar"):
            if nb.strip():
                if opc == "➕ Nueva zona" and nz.strip():
                    if nz not in datos["zonas"]:
                        datos["zonas"][nz] = {}
                if nz in datos["zonas"]:
                    datos["zonas"][nz][nb] = int(nt)
                    guardar(datos)
                    st.success("✅ Agregado")
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### Editar zonas")
    ze = st.selectbox("Selecciona zona:", list(datos["zonas"].keys()))
    if ze:
        for b, t in datos["zonas"][ze].items():
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"**{b}**")
            col2.write(f"${t:,}")
            if col3.button("🗑️", key=f"z_{ze}_{b}"):
                del datos["zonas"][ze][b]
                guardar(datos)
                st.rerun()

# =============================================================================
# PIE
# =============================================================================
st.markdown("---")
st.caption(f"DomiVillavo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
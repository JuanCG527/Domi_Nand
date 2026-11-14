import streamlit as st
import json
from datetime import datetime

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
st.set_page_config(page_title="Domicilios Villavicencio", page_icon="🏍️", layout="wide")

ARCHIVO = "datos_app.json"

# =============================================================================
# ZONAS BASE (puedes editarlas desde la app)
# =============================================================================
ZONAS_BASE = {
    "🟢 Comuna 3 - Sur (Amarilo)": {
        "Hacienda Rosablanca (Amarilo)": 5000,
        "Prado Verde": 5000,
        "Llano Alto": 5500,
        "Caracolí": 5500,
        "Amarilo Zainos": 6000,
        "Amarilo Mapire": 6000,
        "Villa España": 7000,
        "Catama": 7000,
        "Maracos": 7500,
        "El Barzal": 8000,
    },
    "🟡 Comuna 2 - Centro": {
        "Centro": 8000,
        "La Salle": 8000,
        "Nueva Andalucía": 8500,
        "San Antonio": 8000,
    },
    "🟠 Comuna 1 - Norte": {
        "Nueva Granada": 9000,
        "Galán": 9500,
        "Los Cerezos": 9000,
        "Cataluña": 9500,
    },
    "🔴 Comunas Lejanas": {
        "La Grama": 10500,
        "Acapulco": 12500,
        "Pastrana": 13000,
        "Alto Pompeya": 14000,
    },
    "🏘️ Municipios": {
        "Acacías": 18000,
        "Restrepo": 20000,
        "Cumaral": 22000,
    },
    "🤝 Personalizado": {
        "A negociar": 0,
    },
}

# =============================================================================
# PERSISTENCIA
# =============================================================================
def cargar():
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            d = json.load(f)
            for k in ["domicilios", "clientes", "zonas"]:
                if k not in d:
                    d[k] = ZONAS_BASE if k == "zonas" else []
            return d
    except:
        return {"domicilios": [], "clientes": [], "zonas": ZONAS_BASE}

def guardar(d):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

# =============================================================================
# DATOS
# =============================================================================
datos = cargar()

# =============================================================================
# CABECERA
# =============================================================================
st.title("🏍️ Domicilios Villavicencio")
st.caption("📍 Punto base: Amarilo - Meta")
st.markdown("---")

# =============================================================================
# PESTAÑAS
# =============================================================================
tab_entrega, tab_clientes, tab_historial, tab_zonas = st.tabs([
    "📦 Nueva Entrega",
    "📇 Clientes",
    "🗂️ Historial",
    "⚙️ Zonas"
])

# =============================================================================
# TAB 1: NUEVA ENTREGA (flujo único)
# =============================================================================
with tab_entrega:
    st.subheader("📦 Registrar Entrega")
    
    # PASO 1: Buscar o crear cliente
    st.markdown("### Paso 1: Cliente")
    busqueda = st.text_input("🔍 Buscar cliente (nombre, teléfono o barrio):", placeholder="Escribe para buscar...")
    
    clientes = datos.get("clientes", [])
    
    if busqueda.strip():
        t = busqueda.lower()
        resultados = [
            c for c in clientes
            if t in c.get("nombre", "").lower()
            or t in c.get("telefono", "").lower()
            or t in c.get("barrio", "").lower()
        ]
    else:
        # Favoritos primero, luego por visitas
        favs = sorted([c for c in clientes if c.get("favorito")], key=lambda x: x.get("visitas", 0), reverse=True)
        otros = sorted([c for c in clientes if not c.get("favorito")], key=lambda x: x.get("visitas", 0), reverse=True)
        resultados = favs + otros
    
    cliente_sel = None
    
    if not resultados:
        st.info("No hay clientes. Crea uno nuevo abajo.")
    else:
        st.caption(f"{len(resultados)} cliente(s)")
        for c in resultados[:6]:
            col_a, col_b = st.columns([4, 1])
            with col_a:
                fav = "⭐" if c.get("favorito") else ""
                st.write(f"{fav} **{c['nombre']}** - {c.get('telefono', '')}")
                st.caption(f"📍 {c.get('direccion', '')} | 🗺️ {c.get('barrio', '')} | 🔁 {c.get('visitas', 0)}")
            with col_b:
                if st.button("Elegir", key=f"e_{c.get('nombre','')}_{c.get('telefono','')}"):
                    cliente_sel = c
                    st.rerun()
    
    # Si no se eligió cliente, mostrar formulario de nuevo cliente
    if not cliente_sel:
        st.markdown("---")
        st.markdown("**O crear cliente nuevo:**")
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            nombre = st.text_input("👤 Nombre:")
            telefono = st.text_input("📱 Teléfono:")
        with col_n2:
            direccion = st.text_input("🏠 Dirección:")
            barrio_manual = st.text_input("🗺️ Barrio (opcional):")
    else:
        nombre = cliente_sel["nombre"]
        telefono = cliente_sel.get("telefono", "")
        direccion = st.text_input("🏠 Dirección:", value=cliente_sel.get("direccion", ""))
        barrio_manual = cliente_sel.get("barrio", "")
        st.success(f"✅ Cliente: {nombre}")
    
    # PASO 2: Zona y valor
    st.markdown("---")
    st.markdown("### Paso 2: Entrega")
    
    zonas = datos.get("zonas", ZONAS_BASE)
    anillo = st.selectbox("🗺️ Zona/Comuna:", list(zonas.keys()))
    barrios = list(zonas[anillo].keys())
    barrio = st.selectbox("📍 Barrio:", barrios)
    
    tarifa = zonas[anillo][barrio]
    
    if tarifa == 0:
        valor = st.number_input("💵 Valor a cobrar:", min_value=0, value=0, step=500)
    else:
        st.info(f"Tarifa sugerida: **${tarifa:,}**")
        valor = st.number_input("💵 Valor:", min_value=0, value=tarifa, step=500)
    
    propina = st.number_input("🎁 Propina:", min_value=0, value=0, step=500)
    
    total = valor + propina
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Valor", f"${valor:,}")
    col_r2.metric("Propina", f"${propina:,}")
    col_r3.metric("TOTAL", f"${total:,}")
    
    guardar_cliente = st.checkbox("💾 Guardar/actualizar cliente", value=True)
    favorito = st.checkbox("⭐ Marcar como favorito", value=cliente_sel.get("favorito", False) if cliente_sel else False)
    
    if st.button("✅ Registrar Entrega", use_container_width=True, type="primary"):
        if not nombre.strip() or not direccion.strip():
            st.error("⚠️ Nombre y dirección son obligatorios")
        elif valor == 0:
            st.error("⚠️ El valor no puede ser cero")
        else:
            # Guardar domicilio
            dom = {
                "cliente": nombre,
                "telefono": telefono,
                "direccion": direccion,
                "anillo": anillo,
                "barrio": barrio,
                "valor": int(valor),
                "propina": int(propina),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            datos["domicilios"].append(dom)
            
            # Actualizar o crear cliente
            if guardar_cliente:
                existe = None
                for c in datos["clientes"]:
                    if c.get("telefono") == telefono and telefono:
                        existe = c
                        break
                    elif c.get("nombre") == nombre and c.get("direccion") == direccion:
                        existe = c
                        break
                
                if existe:
                    existe["visitas"] = existe.get("visitas", 0) + 1
                    existe["ultima_visita"] = dom["fecha"]
                    existe["direccion"] = direccion
                    existe["barrio"] = barrio
                    existe["anillo"] = anillo
                    existe["favorito"] = favorito
                else:
                    datos["clientes"].append({
                        "nombre": nombre,
                        "telefono": telefono,
                        "direccion": direccion,
                        "barrio": barrio,
                        "anillo": anillo,
                        "visitas": 1,
                        "ultima_visita": dom["fecha"],
                        "favorito": favorito,
                    })
            
            guardar(datos)
            st.success(f"✅ Entrega registrada: {nombre} en {barrio} - ${total:,}")
            st.balloons()
            st.rerun()

# =============================================================================
# TAB 2: CLIENTES
# =============================================================================
with tab_clientes:
    st.subheader("📇 Clientes Frecuentes")
    clientes = datos.get("clientes", [])
    
    if not clientes:
        st.info("Aún no hay clientes")
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
            with st.expander(f"{'⭐' if c.get('favorito') else '👤'} {c['nombre']} - {c.get('telefono','')}"):
                st.write(f"📍 {c.get('direccion', '')}")
                st.write(f"🗺️ {c.get('barrio', '')} | {c.get('anillo', '')}")
                st.write(f"🔁 Visitas: {c.get('visitas', 0)}")
                st.write(f"📅 Última: {c.get('ultima_visita', '')}")
                
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if st.button(f"{'Quitar ⭐' if c.get('favorito') else 'Poner ⭐'}", key=f"fav_{c.get('nombre','')}_{c.get('telefono','')}"):
                        c["favorito"] = not c.get("favorito", False)
                        guardar(datos)
                        st.rerun()
                with col_a2:
                    if st.button("🗑️ Eliminar", key=f"del_{c.get('nombre','')}_{c.get('telefono','')}"):
                        datos["clientes"].remove(c)
                        guardar(datos)
                        st.rerun()

# =============================================================================
# TAB 3: HISTORIAL
# =============================================================================
with tab_historial:
    st.subheader("🗂️ Historial de Entregas")
    doms = datos.get("domicilios", [])
    
    if not doms:
        st.info("Sin registros")
    else:
        st.caption(f"{len(doms)} entregas totales")
        for d in reversed(doms[-30:]):
            with st.expander(f"{d.get('fecha','')} - {d.get('cliente','')} - ${d.get('valor',0)+d.get('propina',0):,}"):
                st.write(f"📱 {d.get('telefono', '')}")
                st.write(f"📍 {d.get('direccion', '')}")
                st.write(f"🗺️ {d.get('barrio', '')} - {d.get('anillo', '')}")
                st.write(f"💵 ${d.get('valor',0):,} + 🎁 ${d.get('propina',0):,}")

# =============================================================================
# TAB 4: ZONAS
# =============================================================================
with tab_zonas:
    st.subheader("⚙️ Gestionar Zonas")
    
    st.markdown("### ➕ Agregar barrio")
    with st.form("add"):
        opc = st.selectbox("Zona:", list(datos["zonas"].keys()) + ["➕ Nueva zona"])
        if opc == "➕ Nueva zona":
            nz = st.text_input("Nombre de la nueva zona:")
        else:
            nz = opc
        nb = st.text_input("Nombre del barrio:")
        nt = st.number_input("Tarifa:", min_value=0, value=5000, step=500)
        if st.form_submit_button("Agregar"):
            if nb.strip():
                if opc == "➕ Nueva zona" and nz.strip() and nz not in datos["zonas"]:
                    datos["zonas"][nz] = {}
                if nz in datos["zonas"]:
                    datos["zonas"][nz][nb] = int(nt)
                    guardar(datos)
                    st.success("✅ Agregado")
                    st.rerun()
    
    st.markdown("---")
    ze = st.selectbox("Editar zona:", list(datos["zonas"].keys()))
    if ze:
        for b, t in datos["zonas"][ze].items():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{b}**")
            with col2:
                st.write(f"${t:,}")
            with col3:
                if st.button("🗑️", key=f"z_{ze}_{b}"):
                    del datos["zonas"][ze][b]
                    guardar(datos)
                    st.rerun()

# =============================================================================
# PIE
# =============================================================================
st.markdown("---")
st.caption(f"v1.0 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
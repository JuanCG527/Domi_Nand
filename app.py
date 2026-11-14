import streamlit as st
import json
from datetime import datetime
from collections import Counter

# =============================================================================
# CONFIGURACIÓN MÓVIL
# =============================================================================
st.set_page_config(page_title="DomiVillavo", page_icon="🏍️", layout="centered")

ARCHIVO = "domivillavo.json"

# =============================================================================
# ZONAS BASE POR COMUNAS (Villavicencio - Meta)
# Fuente: datos.gov.co - Barrios oficiales. Lista parcial, editable desde la app.
# =============================================================================
ZONAS_BASE = {
    "Comuna 1 - Norte": {
        "Nueva Granada": 9000, "Rondinela": 9000, "Galán": 9500,
        "Chapinerito": 9500, "Los Cerezos": 9000, "La Campiña": 9000,
        "Cataluña": 9500, "Caudal Norte": 9500, "Los Andes": 9000,
        "Alcázares": 9000, "La Esperanza": 9000, "Caño Fistol": 9000,
    },
    "Comuna 2 - Centro": {
        "Centro": 8000, "La Salle": 8000, "Nueva Andalucía": 8500,
        "Obrero": 8000, "Sinaí": 8000, "Villa del Prado": 8500,
        "El Progreso": 8000, "San Antonio": 8000, "La Libertad": 8000,
        "San José": 8000, "El Rocío": 8000,
    },
    "Comuna 3 - Sur (Amarilo)": {
        "Hacienda Rosablanca (Amarilo)": 5000, "Prado Verde": 5000,
        "Llano Alto 1": 5500, "Llano Alto 2": 5500, "Llano Alto 3": 5500,
        "Llano Alto 4": 5500, "Caracolí": 5500, "Amarilo Zainos": 6000,
        "Amarilo Mapire": 6000, "Amarilo Confort": 6000, "Amarilo Arauco": 6000,
        "Villa España": 7000, "Catama": 7000, "Maracos": 7500,
        "Santa María del Llano": 7500, "El Barzal": 8000,
    },
    "Comuna 4 - Occidente": {
        "El Recreo": 11000, "Prados de Ciberia": 11500, "Cedritos": 12000,
        "Villa Fabiola": 12000, "Luis Carlos Galán": 11000, "Calamar": 11500,
        "El Cedral": 12000, "Covisán": 11500, "La Desmotadora": 11500,
    },
    "Comuna 5 - Noroccidente": {
        "Acapulco": 12500, "Almendros": 12500, "El Remanso": 12000,
        "Villa Ortiz": 12000, "Brisas del Ocoa": 12000, "Cambulos": 12500,
        "Bosques de Rosa Blanca": 12000, "Brisas de la Esperanza": 12000,
    },
    "Comuna 6 - Suroriental": {
        "Pastrana": 13000, "Caney": 13000, "Simón Bolívar": 13000,
        "Macarena": 13000, "Retiro": 13000, "Amaral": 13000,
        "Canaima": 13500, "Nuevo Maizaro": 13500, "Policía": 13000,
    },
    "Comuna 7 - Oriente": {
        "Alto Pompeya": 14000, "Rincón de Pompeya": 14000, "Quenane": 14000,
        "Los Arrayanes": 14000, "Puerto Colombia": 14500,
        "Santa María Baja": 14000, "Santa María Alta": 14500,
        "San Cristóbal": 14000, "Quebrada Honda": 14500, "Palmichal": 14000,
    },
    "Comuna 8 - Suroccidente": {
        "La Grama": 10500, "Evaristo Sourdis": 11000, "Carulu": 11000,
        "Altagracia": 10500, "Alborada": 10500,
    },
    "Comuna 9 - Sur": {
        "Comuna 9 Centro": 10000, "La Esperanza Sur": 10500,
    },
    "Comuna 10 - Industrial": {
        "Zona Industrial": 12000, "Sabaneta": 11000,
    },
    "Municipios Cercanos": {
        "Acacías": 18000, "Restrepo": 20000, "Cumaral": 22000,
        "El Castillo": 25000, "San Martín": 28000, "Granada": 30000,
        "Fuente de Oro": 32000, "Castilla la Nueva": 35000,
    },
    "🤝 Personalizado": {"A negociar": 0},
}

# =============================================================================
# PERSISTENCIA
# =============================================================================
def cargar():
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            d = json.load(f)
            for k in ["domicilios", "clientes", "zonas", "movimientos"]:
                if k not in d:
                    d[k] = ZONAS_BASE if k == "zonas" else []
            return d
    except:
        return {"domicilios": [], "clientes": [], "zonas": ZONAS_BASE, "movimientos": []}

def guardar(d):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

# =============================================================================
# ESTADO
# =============================================================================
datos = cargar()

# =============================================================================
# CABECERA
# =============================================================================
st.title("🏍️ DomiVillavo")
st.caption(f"📍 Amarilo - Meta | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("---")

# =============================================================================
# NAVEGACIÓN
# =============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Entrega", "📇 Clientes", "📊 Análisis", "🗂️ Historial", "⚙️ Zonas"
])

# =============================================================================
# TAB 1: ENTREGA (flujo único optimizado para móvil)
# =============================================================================
with tab1:
    st.subheader("📦 Nueva Entrega")
    
    # --- BUSCADOR DE CLIENTE ---
    st.markdown("**🔍 Buscar cliente existente:**")
    busqueda = st.text_input("", placeholder="Nombre, teléfono o dirección...", key="busq_entrega")
    
    clientes = datos.get("clientes", [])
    cliente_sel = None
    
    if busqueda.strip():
        t = busqueda.lower()
        resultados = [c for c in clientes if t in c.get("nombre","").lower() 
                      or t in c.get("telefono","").lower()
                      or t in c.get("direccion","").lower()
                      or t in c.get("barrio","").lower()]
    else:
        favs = sorted([c for c in clientes if c.get("favorito")], key=lambda x: x.get("visitas",0), reverse=True)
        otros = sorted([c for c in clientes if not c.get("favorito")], key=lambda x: x.get("visitas",0), reverse=True)
        resultados = favs + otros
    
    if resultados:
        st.caption(f"{len(resultados)} encontrado(s)")
        for c in resultados[:5]:
            col_a, col_b = st.columns([4, 1])
            with col_a:
                fav = "⭐" if c.get("favorito") else ""
                st.write(f"{fav} **{c['nombre']}**")
                st.caption(f"📱 {c.get('telefono','')} | 📍 {c.get('direccion','')}")
                st.caption(f"🗺️ {c.get('barrio','')} | 🔁 {c.get('visitas',0)}")
            with col_b:
                if st.button("Usar", key=f"u_{c.get('nombre','')}_{c.get('telefono','')}"):
                    cliente_sel = c
                    st.rerun()
    
    # --- DATOS DE LA ENTREGA ---
    st.markdown("---")
    st.markdown("**📝 Datos de la entrega:**")
    
    if cliente_sel:
        nombre = st.text_input("👤 Cliente:", value=cliente_sel["nombre"])
        telefono = st.text_input("📱 Teléfono:", value=cliente_sel.get("telefono",""))
        direccion = st.text_input("📍 Dirección:", value=cliente_sel.get("direccion",""))
        barrio_def = cliente_sel.get("barrio","")
        anillo_def = cliente_sel.get("anillo","")
        st.success(f"✅ {cliente_sel['nombre']} (visita #{cliente_sel.get('visitas',0)+1})")
    else:
        nombre = st.text_input("👤 Cliente:")
        telefono = st.text_input("📱 Teléfono:")
        direccion = st.text_input("📍 Dirección:")
        barrio_def = ""
        anillo_def = ""
    
    # Zona y barrio
    zonas = datos.get("zonas", ZONAS_BASE)
    idx_anillo = list(zonas.keys()).index(anillo_def) if anillo_def in zonas else 0
    anillo = st.selectbox("🗺️ Comuna/Zona:", list(zonas.keys()), index=idx_anillo)
    barrios = list(zonas[anillo].keys())
    idx_barrio = barrios.index(barrio_def) if barrio_def in barrios else 0
    barrio = st.selectbox("📍 Barrio:", barrios, index=idx_barrio)
    
    # Tipo de movimiento
    tipo_mov = st.radio("💰 Tipo:", ["📥 Ingreso (Entrega)", "📤 Gasto"], horizontal=True)
    
    if tipo_mov == "📥 Ingreso (Entrega)":
        tarifa = zonas[anillo][barrio]
        if tarifa == 0:
            monto = st.number_input("💵 Monto:", min_value=0, value=0, step=500)
        else:
            st.info(f"Tarifa: **${tarifa:,}**")
            monto = st.number_input("💵 Monto:", min_value=0, value=tarifa, step=500)
    else:
        concepto_gasto = st.selectbox("Concepto:", [
            "⛽ Gasolina", "🍲 Almuerzo", "🌙 Cena", "🔧 Mantenimiento",
            "🔋 Carga celular", "💧 Agua", "🅿️ Parqueadero", "🛞 Llanta",
            "🏥 Farmacia", "📱 Datos", "📝 Otro"
        ])
        monto = st.number_input("💸 Valor del gasto:", min_value=0, value=0, step=500)
    
    # Favorito
    es_favorito = st.checkbox("⭐ Marcar como cliente frecuente", value=cliente_sel.get("favorito", False) if cliente_sel else False)
    
    # Resumen
    col1, col2 = st.columns(2)
    col1.metric("Tipo", tipo_mov.split(" ")[0])
    col2.metric("Monto", f"${monto:,}")
    
    if st.button("✅ Registrar", use_container_width=True, type="primary"):
        if not nombre.strip() or not direccion.strip():
            st.error("⚠️ Nombre y dirección obligatorios")
        elif monto == 0:
            st.error("⚠️ El monto no puede ser cero")
        else:
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if tipo_mov == "📥 Ingreso (Entrega)":
                # Guardar domicilio
                dom = {
                    "cliente": nombre, "telefono": telefono, "direccion": direccion,
                    "anillo": anillo, "barrio": barrio, "monto": int(monto),
                    "tipo": "ingreso", "fecha": ahora,
                }
                datos["domicilios"].append(dom)
                datos["movimientos"].append(dom)
                
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
                    existe["favorito"] = es_favorito
                else:
                    datos["clientes"].append({
                        "nombre": nombre, "telefono": telefono, "direccion": direccion,
                        "barrio": barrio, "anillo": anillo, "visitas": 1,
                        "ultima_visita": ahora, "favorito": es_favorito,
                    })
                st.success(f"✅ Entrega registrada: ${monto:,}")
            else:
                mov = {
                    "concepto": concepto_gasto, "monto": int(monto),
                    "tipo": "gasto", "fecha": ahora,
                }
                datos["movimientos"].append(mov)
                st.success(f"✅ Gasto registrado: {concepto_gasto} ${monto:,}")
            
            guardar(datos)
            st.balloons()
            st.rerun()

# =============================================================================
# TAB 2: CLIENTES
# =============================================================================
with tab2:
    st.subheader("📇 Clientes Frecuentes")
    clientes = datos.get("clientes", [])
    
    if not clientes:
        st.info("Sin clientes aún")
    else:
        busq = st.text_input("🔍 Buscar:", placeholder="Nombre, tel, barrio...", key="busq_cli")
        
        if busq.strip():
            t = busq.lower()
            lista = [c for c in clientes if t in c.get("nombre","").lower() 
                    or t in c.get("telefono","").lower() or t in c.get("barrio","").lower()]
        else:
            favs = [c for c in clientes if c.get("favorito")]
            otros = [c for c in clientes if not c.get("favorito")]
            lista = favs + otros
        
        st.caption(f"{len(lista)} de {len(clientes)}")
        
        for c in lista:
            with st.expander(f"{'⭐' if c.get('favorito') else '👤'} {c['nombre']}"):
                st.write(f"📱 {c.get('telefono','')}")
                st.write(f"📍 {c.get('direccion','')}")
                st.write(f"🗺️ {c.get('barrio','')} - {c.get('anillo','')}")
                st.write(f"🔁 {c.get('visitas',0)} visitas | 📅 {c.get('ultima_visita','')}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"{'Quitar ⭐' if c.get('favorito') else 'Poner ⭐'}", key=f"f_{c.get('nombre','')}_{c.get('telefono','')}"):
                        c["favorito"] = not c.get("favorito", False)
                        guardar(datos); st.rerun()
                with col_b:
                    if st.button("🗑️", key=f"d_{c.get('nombre','')}_{c.get('telefono','')}"):
                        datos["clientes"].remove(c); guardar(datos); st.rerun()

# =============================================================================
# TAB 3: ANÁLISIS CON GRÁFICOS DE BARRAS
# =============================================================================
with tab3:
    st.subheader("📊 Análisis")
    
    movs = datos.get("movimientos", [])
    if not movs:
        st.info("Sin datos")
    else:
        # Totales
        ingresos = sum(m["monto"] for m in movs if m.get("tipo")=="ingreso")
        gastos = sum(m["monto"] for m in movs if m.get("tipo")=="gasto")
        balance = ingresos - gastos
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Ingresos", f"${ingresos:,}")
        c2.metric("💸 Gastos", f"${gastos:,}")
        c3.metric("📊 Balance", f"${balance:,}")
        
        st.markdown("---")
        st.markdown("**📊 Ingresos vs Gastos:**")
        df_barras = {"Concepto": ["Ingresos", "Gastos"], "Monto": [ingresos, gastos]}
        st.bar_chart(df_barras, x="Concepto", y="Monto", color=["#2ecc71", "#e74c3c"])
        
        st.markdown("---")
        st.markdown("**🗺️ Ingresos por Comuna:**")
        contador_zonas = Counter()
        for m in movs:
            if m.get("tipo") == "ingreso":
                contador_zonas[m.get("anillo","Otro")] += m.get("monto",0)
        
        if contador_zonas:
            df_zonas = {"Zona": list(contador_zonas.keys()), "Monto": list(contador_zonas.values())}
            st.bar_chart(df_zonas, x="Zona", y="Monto")
        
        st.markdown("---")
        st.markdown("**📦 Top 5 Barrios:**")
        contador_barrios = Counter()
        for m in movs:
            if m.get("tipo") == "ingreso":
                contador_barrios[m.get("barrio","?")] += 1
        
        if contador_barrios:
            top = contador_barrios.most_common(5)
            for barrio, cant in top:
                st.write(f"**{barrio}**: {cant} entregas")
        
        st.markdown("---")
        st.markdown("**💸 Top 5 Gastos:**")
        contador_gastos = Counter()
        for m in movs:
            if m.get("tipo") == "gasto":
                contador_gastos[m.get("concepto","?")] += m.get("monto",0)
        
        if contador_gastos:
            top_g = contador_gastos.most_common(5)
            for conc, val in top_g:
                st.write(f"**{conc}**: ${val:,}")

# =============================================================================
# TAB 4: HISTORIAL
# =============================================================================
with tab4:
    st.subheader("🗂️ Historial")
    movs = datos.get("movimientos", [])
    
    if not movs:
        st.info("Sin registros")
    else:
        filtro = st.radio("Ver:", ["Todos", "📥 Ingresos", "📤 Gastos"], horizontal=True)
        
        if filtro == "📥 Ingresos":
            lista = [m for m in movs if m.get("tipo")=="ingreso"]
        elif filtro == "📤 Gastos":
            lista = [m for m in movs if m.get("tipo")=="gasto"]
        else:
            lista = movs
        
        st.caption(f"{len(lista)} registros")
        
        for m in reversed(lista[-50:]):
            if m.get("tipo") == "ingreso":
                icono = "📥"
                desc = f"{m.get('cliente','')} → {m.get('barrio','')}"
            else:
                icono = "📤"
                desc = m.get("concepto","")
            
            with st.expander(f"{icono} {m.get('fecha','')} - ${m.get('monto',0):,}"):
                st.write(desc)
                if m.get("tipo") == "ingreso":
                    st.write(f"📱 {m.get('telefono','')}")
                    st.write(f"📍 {m.get('direccion','')}")
                    st.write(f"🗺️ {m.get('anillo','')}")

# =============================================================================
# TAB 5: ZONAS
# =============================================================================
with tab5:
    st.subheader("⚙️ Gestionar Zonas")
    
    st.markdown("### ➕ Agregar barrio")
    with st.form("add"):
        opc = st.selectbox("Zona:", list(datos["zonas"].keys()) + ["➕ Nueva"])
        if opc == "➕ Nueva":
            nz = st.text_input("Nombre nueva zona:")
        else:
            nz = opc
        nb = st.text_input("Barrio:")
        nt = st.number_input("Tarifa:", min_value=0, value=5000, step=500)
        if st.form_submit_button("Agregar"):
            if nb.strip():
                if opc == "➕ Nueva" and nz.strip() and nz not in datos["zonas"]:
                    datos["zonas"][nz] = {}
                if nz in datos["zonas"]:
                    datos["zonas"][nz][nb] = int(nt)
                    guardar(datos); st.success("✅"); st.rerun()
    
    st.markdown("---")
    ze = st.selectbox("Editar:", list(datos["zonas"].keys()))
    if ze:
        for b, t in datos["zonas"][ze].items():
            col1, col2, col3 = st.columns([3,1,1])
            col1.write(f"**{b}**")
            col2.write(f"${t:,}")
            if col3.button("🗑️", key=f"z_{ze}_{b}"):
                del datos["zonas"][ze][b]; guardar(datos); st.rerun()

# =============================================================================
# PIE
# =============================================================================
st.markdown("---")
st.caption(f"DomiVillavo v1.0 | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
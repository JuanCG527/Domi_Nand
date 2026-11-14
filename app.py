import streamlit as st
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from io import StringIO

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
st.set_page_config(
    page_title="DomiVillavo Pro",
    page_icon="🏍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ARCHIVO = "domivillavo_pro.json"

# =============================================================================
# ESTILO PROFESIONAL (CSS)
# =============================================================================
st.markdown("""
<style>
    /* Fondo y tipografía */
    .stApp { background: #0f172a; color: #e2e8f0; }
    
    /* Títulos */
    h1 { color: #38bdf8; font-size: 1.8em; font-weight: 700; }
    h2 { color: #7dd3fc; font-size: 1.3em; }
    h3 { color: #bae6fd; font-size: 1.1em; }
    
    /* Botones principales */
    .stButton>button {
        background: linear-gradient(135deg, #0ea5e9, #0284c7);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-weight: 600;
        font-size: 1em;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0284c7, #0369a1);
        transform: translateY(-1px);
    }
    
    /* Botones secundarios */
    .stButton>button[kind="secondary"] {
        background: #334155;
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        background: #1e293b;
        color: #e2e8f0;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    /* Métricas */
    div[data-testid="stMetric"] {
        background: #1e293b;
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #0ea5e9;
    }
    
    /* Expander */
    .stExpander {
        background: #1e293b;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    
    /* Tabs */
    button[data-baseweb="tab"] {
        background: #1e293b;
        color: #94a3b8;
        border-radius: 8px 8px 0 0;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: #0ea5e9;
        color: white;
    }
    
    /* Ocultar menú y footer de Streamlit */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Alertas */
    .stSuccess { background: #064e3b; border-radius: 8px; }
    .stError { background: #7f1d1d; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# ZONAS BASE (Villavicencio - Meta)
# =============================================================================
ZONAS_BASE = {
    "Comuna 1 - Norte": {
        "Nueva Granada": 9000, "Galán": 9500, "Los Cerezos": 9000,
        "Cataluña": 9500, "Los Andes": 9000, "Rondinela": 9000,
    },
    "Comuna 2 - Centro": {
        "Centro": 8000, "La Salle": 8000, "Nueva Andalucía": 8500,
        "San Antonio": 8000, "Obrero": 8000,
    },
    "Comuna 3 - Sur (Amarilo)": {
        "Hacienda Rosablanca": 5000, "Prado Verde": 5000,
        "Llano Alto": 5500, "Caracolí": 5500,
        "Amarilo Zainos": 6000, "Amarilo Mapire": 6000,
        "Villa España": 7000, "Maracos": 7500, "El Barzal": 8000,
    },
    "Comuna 4 - Occidente": {
        "El Recreo": 11000, "Cedritos": 12000, "Villa Fabiola": 12000,
        "Prados de Ciberia": 11500,
    },
    "Comuna 5 - Noroccidente": {
        "Acapulco": 12500, "Almendros": 12500, "El Remanso": 12000,
    },
    "Comuna 6 - Suroriental": {
        "Pastrana": 13000, "Macarena": 13000, "Amaral": 13000, "Caney": 13000,
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

CATEGORIAS_GASTO = [
    "⛽ Gasolina", "🍲 Alimentación", "🔧 Mantenimiento",
    "🔋 Carga celular", "💧 Bebidas", "🅿️ Parqueadero",
    "🛞 Llantas/Repuestos", "🏥 Salud", "📱 Datos/Internet",
    "🧴 Aseo personal", "👕 Ropa", "📝 Otro"
]

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
# UTILIDADES
# =============================================================================
def fmt_pesos(n):
    """Formatea número como pesos colombianos."""
    return f"${int(n):,}".replace(",", ".")

def fecha_hoy():
    return datetime.now().strftime("%Y-%m-%d")

def hace_n_dias(n):
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")

def filtrar_por_fecha(lista, campo, desde, hasta):
    """Filtra registros entre dos fechas (inclusive)."""
    resultado = []
    for item in lista:
        f = item.get(campo, "")
        if not f:
            continue
        fecha_solo = f.split(" ")[0]
        if desde <= fecha_solo <= hasta:
            resultado.append(item)
    return resultado

def exportar_csv(datos):
    """Genera CSV con todos los datos para backup."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["TIPO", "FECHA", "CLIENTE", "TELEFONO", "DIRECCION",
                     "BARRIO", "ZONA", "CONCEPTO", "MONTO"])
    for i in datos.get("ingresos", []):
        writer.writerow(["INGRESO", i.get("fecha",""), i.get("cliente",""),
                        i.get("telefono",""), i.get("direccion",""),
                        i.get("barrio",""), i.get("anillo",""), "", i.get("monto",0)])
    for g in datos.get("gastos", []):
        writer.writerow(["GASTO", g.get("fecha",""), "", "", "", "", "",
                        g.get("concepto",""), g.get("monto",0)])
    return output.getvalue()

# =============================================================================
# CARGAR DATOS
# =============================================================================
datos = cargar()

# =============================================================================
# CABECERA
# =============================================================================
st.title("🏍️ DomiVillavo Pro")
st.caption(f"📍 Villavicencio - Meta | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("---")

# =============================================================================
# NAVEGACIÓN
# =============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "➕ Nuevo", "📊 Panel", "📜 Historial",
    "📇 Clientes", "📈 Análisis", "⚙️ Ajustes"
])

# =============================================================================
# TAB 1: NUEVO REGISTRO
# =============================================================================
with tab1:
    st.subheader("Nuevo Registro")
    
    tipo = st.radio("Tipo de registro:", ["💰 Ingreso", "💸 Gasto"], horizontal=True)
    
    if tipo == "💰 Ingreso":
        # Buscador de cliente
        busqueda = st.text_input(
            "🔍 Buscar cliente:",
            placeholder="Escribe nombre, teléfono o barrio...",
            key="busq_ingreso"
        )
        
        clientes = datos.get("clientes", [])
        cliente_sel = None
        
        if busqueda.strip():
            t = busqueda.lower()
            resultados = [c for c in clientes
                         if t in c.get("nombre","").lower()
                         or t in c.get("telefono","").lower()
                         or t in c.get("direccion","").lower()
                         or t in c.get("barrio","").lower()]
        else:
            favs = sorted([c for c in clientes if c.get("favorito")],
                         key=lambda x: x.get("visitas",0), reverse=True)
            otros = sorted([c for c in clientes if not c.get("favorito")],
                          key=lambda x: x.get("visitas",0), reverse=True)
            resultados = favs + otros
        
        if resultados:
            st.caption(f"📋 {len(resultados)} cliente(s)")
            for c in resultados[:5]:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    fav = "⭐ " if c.get("favorito") else ""
                    st.write(f"{fav}**{c['nombre']}**")
                    st.caption(f"📱 {c.get('telefono','')} | 📍 {c.get('direccion','')}")
                    st.caption(f"🗺️ {c.get('barrio','')} | 🔁 {c.get('visitas',0)} visitas")
                with col_b:
                    if st.button("Usar", key=f"u_{c.get('nombre','')}_{c.get('telefono','')}"):
                        st.session_state.cliente_sel = c
                        st.rerun()
        
        # Formulario de ingreso
        st.markdown("---")
        if "cliente_sel" in st.session_state and st.session_state.cliente_sel:
            c = st.session_state.cliente_sel
            nombre = st.text_input("👤 Cliente:", value=c["nombre"])
            telefono = st.text_input("📱 Teléfono:", value=c.get("telefono",""))
            direccion = st.text_input("📍 Dirección:", value=c.get("direccion",""))
            barrio_def = c.get("barrio","")
            anillo_def = c.get("anillo","")
            st.success(f"✅ {c['nombre']} (visita #{c.get('visitas',0)+1})")
            if st.button("Limpiar selección"):
                del st.session_state.cliente_sel
                st.rerun()
        else:
            nombre = st.text_input("👤 Cliente:")
            telefono = st.text_input("📱 Teléfono:")
            direccion = st.text_input("📍 Dirección:")
            barrio_def = ""
            anillo_def = ""
        
        zonas = datos.get("zonas", ZONAS_BASE)
        idx_a = list(zonas.keys()).index(anillo_def) if anillo_def in zonas else 0
        anillo = st.selectbox("🗺️ Zona/Comuna:", list(zonas.keys()), index=idx_a)
        barrios = list(zonas[anillo].keys())
        idx_b = barrios.index(barrio_def) if barrio_def in barrios else 0
        barrio = st.selectbox("📍 Barrio:", barrios, index=idx_b)
        
        tarifa = zonas[anillo][barrio]
        if tarifa == 0:
            monto = st.number_input("💵 Monto ($):", min_value=0, value=0, step=500)
        else:
            st.info(f"💰 Tarifa sugerida: {fmt_pesos(tarifa)}")
            monto = st.number_input("💵 Monto ($):", min_value=0, value=tarifa, step=500)
        
        favorito = st.checkbox(
            "⭐ Marcar como cliente frecuente",
            value=st.session_state.get("cliente_sel", {}).get("favorito", False)
        )
        
        if st.button("✅ Registrar Ingreso", type="primary"):
            if not nombre.strip() or not direccion.strip():
                st.error("⚠️ Nombre y dirección son obligatorios")
            elif monto == 0:
                st.error("⚠️ El monto no puede ser cero")
            else:
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ingreso = {
                    "id": datetime.now().timestamp(),
                    "cliente": nombre, "telefono": telefono,
                    "direccion": direccion, "anillo": anillo,
                    "barrio": barrio, "monto": int(monto),
                    "fecha": ahora,
                }
                datos["ingresos"].append(ingreso)
                
                # Actualizar o crear cliente
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
                        "nombre": nombre, "telefono": telefono,
                        "direccion": direccion, "barrio": barrio,
                        "anillo": anillo, "visitas": 1,
                        "ultima_visita": ahora, "favorito": favorito,
                    })
                
                guardar(datos)
                st.toast(f"✅ Ingreso registrado: {fmt_pesos(monto)}", icon="🎉")
                if "cliente_sel" in st.session_state:
                    del st.session_state.cliente_sel
                st.rerun()
    
    else:
        # Formulario de gasto
        concepto = st.selectbox("📝 Concepto:", CATEGORIAS_GASTO)
        detalle = st.text_input("📎 Detalle (opcional):")
        monto = st.number_input("💸 Monto ($):", min_value=0, value=0, step=500)
        
        if st.button("✅ Registrar Gasto", type="primary"):
            if not concepto or monto == 0:
                st.error("⚠️ Concepto y monto son obligatorios")
            else:
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                datos["gastos"].append({
                    "id": datetime.now().timestamp(),
                    "concepto": concepto, "detalle": detalle,
                    "monto": int(monto), "fecha": ahora,
                })
                guardar(datos)
                st.toast(f"✅ Gasto registrado: {fmt_pesos(monto)}", icon="💸")
                st.rerun()

# =============================================================================
# TAB 2: PANEL DE CONTROL
# =============================================================================
with tab2:
    st.subheader("📊 Panel de Control")
    
    # Filtro de período
    periodo = st.radio("Período:", ["Hoy", "7 días", "30 días", "Todo"], horizontal=True)
    
    hoy = fecha_hoy()
    if periodo == "Hoy":
        desde, hasta = hoy, hoy
    elif periodo == "7 días":
        desde, hasta = hace_n_dias(6), hoy
    elif periodo == "30 días":
        desde, hasta = hace_n_dias(29), hoy
    else:
        desde, hasta = "2000-01-01", "2099-12-31"
    
    ingresos_f = filtrar_por_fecha(datos["ingresos"], "fecha", desde, hasta)
    gastos_f = filtrar_por_fecha(datos["gastos"], "fecha", desde, hasta)
    
    total_ing = sum(i["monto"] for i in ingresos_f)
    total_gas = sum(g["monto"] for g in gastos_f)
    balance = total_ing - total_gas
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("📥 Ingresos", fmt_pesos(total_ing))
    c2.metric("📤 Gastos", fmt_pesos(total_gas))
    c3.metric("💰 Balance", fmt_pesos(balance))
    
    c4, c5 = st.columns(2)
    c4.metric("📦 Entregas", len(ingresos_f))
    c5.metric("🎯 Promedio/entrega", fmt_pesos(total_ing/len(ingresos_f)) if ingresos_f else "$0")
    
    # Gráfico de barras últimos 7 días
    st.markdown("---")
    st.subheader("📈 Últimos 7 días")
    
    datos_graf = []
    for i in range(7):
        dia = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        ing_dia = sum(x["monto"] for x in datos["ingresos"] if x.get("fecha","").startswith(dia))
        gas_dia = sum(x["monto"] for x in datos["gastos"] if x.get("fecha","").startswith(dia))
        datos_graf.append({
            "Día": dia[5:],  # MM-DD
            "Ingresos": ing_dia,
            "Gastos": gas_dia
        })
    
    df_graf = pd.DataFrame(datos_graf).set_index("Día")
    st.bar_chart(df_graf)
    
    # Top barrios
    st.markdown("---")
    st.subheader("🏆 Top 5 barrios")
    contador = Counter(i.get("barrio","?") for i in ingresos_f)
    for barrio, cant in contador.most_common(5):
        st.write(f"**{barrio}**: {cant} entregas")

# =============================================================================
# TAB 3: HISTORIAL
# =============================================================================
with tab3:
    st.subheader("📜 Historial")
    
    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_tipo = st.radio("Tipo:", ["Todo", "Ingresos", "Gastos"], horizontal=True)
    with col_f2:
        filtro_fecha = st.radio("Fecha:", ["Hoy", "7d", "30d", "Todo"], horizontal=True)
    
    busqueda = st.text_input("🔍 Buscar:", placeholder="Cliente, barrio, concepto...")
    
    # Aplicar filtros
    if filtro_fecha == "Hoy":
        desde, hasta = hoy, hoy
    elif filtro_fecha == "7d":
        desde, hasta = hace_n_dias(6), hoy
    elif filtro_fecha == "30d":
        desde, hasta = hace_n_dias(29), hoy
    else:
        desde, hasta = "2000-01-01", "2099-12-31"
    
    ingresos_hist = filtrar_por_fecha(datos["ingresos"], "fecha", desde, hasta)
    gastos_hist = filtrar_por_fecha(datos["gastos"], "fecha", desde, hasta)
    
    if busqueda.strip():
        t = busqueda.lower()
        ingresos_hist = [i for i in ingresos_hist
                        if t in i.get("cliente","").lower()
                        or t in i.get("barrio","").lower()
                        or t in i.get("direccion","").lower()]
        gastos_hist = [g for g in gastos_hist
                      if t in g.get("concepto","").lower()
                      or t in g.get("detalle","").lower()]
    
    # Construir lista unificada
    lista = []
    if filtro_tipo in ["Todo", "Ingresos"]:
        for i in ingresos_hist:
            lista.append(("ingreso", i))
    if filtro_tipo in ["Todo", "Gastos"]:
        for g in gastos_hist:
            lista.append(("gasto", g))
    
    lista.sort(key=lambda x: x[1].get("fecha",""), reverse=True)
    
    st.caption(f"📋 {len(lista)} registros")
    
    # Totales del filtro
    ing_f = sum(x[1]["monto"] for x in lista if x[0]=="ingreso")
    gas_f = sum(x[1]["monto"] for x in lista if x[0]=="gasto")
    st.info(f"💰 Ingresos: {fmt_pesos(ing_f)} | 💸 Gastos: {fmt_pesos(gas_f)} | 📊 Balance: {fmt_pesos(ing_f-gas_f)}")
    
    # Listar
    for tipo, item in lista[:100]:
        if tipo == "ingreso":
            icono = "📥"
            titulo = f"{item.get('cliente','?')} → {item.get('barrio','?')}"
            sub = f"📱 {item.get('telefono','')} | 📍 {item.get('direccion','')}"
        else:
            icono = "📤"
            titulo = item.get("concepto","?")
            sub = item.get("detalle","")
        
        with st.expander(f"{icono} {item.get('fecha','')[:16]} - {titulo} - {fmt_pesos(item.get('monto',0))}"):
            st.write(sub)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✏️ Editar", key=f"e_{item.get('id',0)}"):
                    st.session_state.editando = item
                    st.session_state.edit_tipo = tipo
                    st.rerun()
            with col_b:
                if st.button("🗑️ Eliminar", key=f"d_{item.get('id',0)}"):
                    if tipo == "ingreso":
                        datos["ingresos"] = [x for x in datos["ingresos"] if x.get("id") != item.get("id")]
                    else:
                        datos["gastos"] = [x for x in datos["gastos"] if x.get("id") != item.get("id")]
                    guardar(datos)
                    st.toast("🗑️ Eliminado", icon="🗑️")
                    st.rerun()
    
    # Modal de edición
    if "editando" in st.session_state:
        st.markdown("---")
        st.subheader("✏️ Editar registro")
        item = st.session_state.editando
        tipo_ed = st.session_state.edit_tipo
        
        if tipo_ed == "ingreso":
            nombre_ed = st.text_input("Cliente:", value=item.get("cliente",""))
            telefono_ed = st.text_input("Teléfono:", value=item.get("telefono",""))
            direccion_ed = st.text_input("Dirección:", value=item.get("direccion",""))
            monto_ed = st.number_input("Monto:", value=item.get("monto",0))
            
            if st.button("💾 Guardar cambios"):
                item["cliente"] = nombre_ed
                item["telefono"] = telefono_ed
                item["direccion"] = direccion_ed
                item["monto"] = int(monto_ed)
                guardar(datos)
                del st.session_state.editando
                st.toast("✅ Actualizado", icon="✅")
                st.rerun()
            if st.button("❌ Cancelar"):
                del st.session_state.editando
                st.rerun()

# =============================================================================
# TAB 4: CLIENTES
# =============================================================================
with tab4:
    st.subheader("📇 Clientes Frecuentes")
    clientes = datos.get("clientes", [])
    
    if not clientes:
        st.info("📭 Aún no hay clientes registrados")
    else:
        busq = st.text_input("🔍 Buscar:", placeholder="Nombre, teléfono, barrio...")
        
        if busq.strip():
            t = busq.lower()
            lista = [c for c in clientes
                    if t in c.get("nombre","").lower()
                    or t in c.get("telefono","").lower()
                    or t in c.get("barrio","").lower()]
        else:
            favs = [c for c in clientes if c.get("favorito")]
            otros = [c for c in clientes if not c.get("favorito")]
            lista = favs + otros
        
        st.caption(f"📋 {len(lista)} de {len(clientes)} clientes")
        
        for c in lista:
            with st.expander(f"{'⭐' if c.get('favorito') else '👤'} **{c['nombre']}**"):
                st.write(f"📱 {c.get('telefono','N/A')}")
                st.write(f"📍 {c.get('direccion','N/A')}")
                st.write(f"🗺️ {c.get('barrio','N/A')} - {c.get('anillo','N/A')}")
                st.write(f"🔁 {c.get('visitas',0)} visitas")
                st.write(f"📅 Última: {c.get('ultima_visita','N/A')[:16]}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"{'Quitar ⭐' if c.get('favorito') else 'Poner ⭐'}",
                                key=f"f_{c.get('nombre','')}_{c.get('telefono','')}"):
                        c["favorito"] = not c.get("favorito", False)
                        guardar(datos); st.rerun()
                with col_b:
                    if st.button("🗑️ Eliminar", key=f"dc_{c.get('nombre','')}_{c.get('telefono','')}"):
                        datos["clientes"].remove(c)
                        guardar(datos); st.rerun()

# =============================================================================
# TAB 5: ANÁLISIS
# =============================================================================
with tab5:
    st.subheader("📈 Análisis Detallado")
    
    ingresos = datos.get("ingresos", [])
    gastos = datos.get("gastos", [])
    
    if not ingresos and not gastos:
        st.info("📭 Sin datos para analizar")
    else:
        # Resumen general
        total_ing = sum(i["monto"] for i in ingresos)
        total_gas = sum(g["monto"] for g in gastos)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total ingresos", fmt_pesos(total_ing))
        c2.metric("💸 Total gastos", fmt_pesos(total_gas))
        c3.metric("📊 Balance", fmt_pesos(total_ing - total_gas))
        
        # Gráfico de gastos por categoría
        st.markdown("---")
        st.subheader("💸 Gastos por categoría")
        contador_g = Counter(g.get("concepto","?") for g in gastos)
        if contador_g:
            df_g = pd.DataFrame([
                {"Categoría": k, "Monto": v}
                for k, v in contador_g.most_common(10)
            ]).set_index("Categoría")
            st.bar_chart(df_g)
        
        # Top barrios
        st.markdown("---")
        st.subheader("🏆 Top 10 barrios")
        contador_b = Counter(i.get("barrio","?") for i in ingresos)
        for barrio, cant in contador_b.most_common(10):
            st.write(f"**{barrio}**: {cant} entregas")
        
        # Top clientes
        st.markdown("---")
        st.subheader("👥 Top 10 clientes")
        contador_c = Counter(i.get("cliente","?") for i in ingresos)
        for cliente, cant in contador_c.most_common(10):
            st.write(f"**{cliente}**: {cant} entregas")

# =============================================================================
# TAB 6: AJUSTES (Zonas + Backup)
# =============================================================================
with tab6:
    st.subheader("⚙️ Ajustes")
    
    # Gestión de zonas
    st.markdown("### 🗺️ Gestionar Zonas y Barrios")
    
    st.markdown("**➕ Agregar barrio:**")
    with st.form("add_barrio"):
        opc = st.selectbox("Zona:", list(datos["zonas"].keys()) + ["➕ Nueva zona"])
        if opc == "➕ Nueva zona":
            nz = st.text_input("Nombre de la nueva zona:")
        else:
            nz = opc
        nb = st.text_input("Nombre del barrio:")
        nt = st.number_input("Tarifa ($):", min_value=0, value=5000, step=500)
        if st.form_submit_button("Agregar barrio"):
            if nb.strip():
                if opc == "➕ Nueva zona" and nz.strip():
                    if nz not in datos["zonas"]:
                        datos["zonas"][nz] = {}
                if nz in datos["zonas"]:
                    datos["zonas"][nz][nb] = int(nt)
                    guardar(datos)
                    st.toast("✅ Barrio agregado", icon="✅")
                    st.rerun()
    
    st.markdown("---")
    st.markdown("**📋 Editar zonas existentes:**")
    ze = st.selectbox("Selecciona zona:", list(datos["zonas"].keys()))
    if ze:
        for b, t in datos["zonas"][ze].items():
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"**{b}**")
            col2.write(fmt_pesos(t))
            if col3.button("🗑️", key=f"z_{ze}_{b}"):
                del datos["zonas"][ze][b]
                guardar(datos)
                st.rerun()
    
    # Backup y restauración
    st.markdown("---")
    st.markdown("### 💾 Backup de datos")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("**📤 Exportar:**")
        csv_data = exportar_csv(datos)
        st.download_button(
            "⬇️ Descargar CSV",
            data=csv_data,
            file_name=f"domivillavo_backup_{fecha_hoy()}.csv",
            mime="text/csv"
        )
    
    with col_b2:
        st.markdown("**📥 Importar:**")
        archivo = st.file_uploader("Subir CSV", type=["csv"])
        if archivo:
            st.warning("⚠️ Esto REEMPLAZARÁ todos los datos actuales")
            if st.button("⚠️ Confirmar importación"):
                st.info("Función en desarrollo - usa el JSON directamente")
    
    # Reset total
    st.markdown("---")
    st.markdown("### ⚠️ Zona peligrosa")
    if st.button("🗑️ BORRAR TODOS LOS DATOS", type="secondary"):
        st.error("⚠️ Esta acción no se puede deshacer")
        if st.checkbox("Sí, estoy seguro"):
            datos["ingresos"] = []
            datos["gastos"] = []
            datos["clientes"] = []
            guardar(datos)
            st.toast("🗑️ Datos borrados", icon="🗑️")
            st.rerun()

# =============================================================================
# PIE
# =============================================================================
st.markdown("---")
st.caption(f"DomiVillavo Pro | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
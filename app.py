# =============================================================================
# BLOQUE 1: IMPORTACIONES Y CONFIGURACIÓN
# =============================================================================
import streamlit as st
import json
from datetime import datetime, timedelta

# Configuración de la página (siempre va PRIMERO)
st.set_page_config(
    page_title="Domicilios Villavicencio",
    page_icon="🏍️",
    layout="wide"
)

# =============================================================================
# BLOQUE 2: CATÁLOGO DE ZONAS REALES DE VILLAVICENCIO (CENTRADO EN AMARILO)
# =============================================================================
# Estructura jerárquica: Anillo -> Barrio -> Tarifa
# Punto base: Amarilo (Hacienda Rosablanca), Villavicencio - Meta

ZONAS_Y_TARIFAS = {
    # 🟢 ANILLO 1: Mi Vecindario (0-3 km)
    "🟢 Anillo 1 - Vecindario (0-3km)": {
        "Amarilo - Hacienda Rosablanca (C3)": 5000,
        "Prado Verde (C3)": 5000,
        "Llano Alto 1-4 (C3)": 5500,
        "Condominio Caracolí (C3)": 5500,
        "Amarilo Zainos (C3)": 6000,
        "Amarilo Mapire (C3)": 6000,
        "Amarilo Confort (C3)": 6000,
        "Amarilo Arauco Home (C3)": 6000,
    },
    # 🟡 ANILLO 2: Cercano (3-7 km)
    "🟡 Anillo 2 - Cercano (3-7km)": {
        "Villa España (C3)": 7000,
        "Catama (C3)": 7000,
        "Maracos (C3)": 7500,
        "Santa María del Llano (C3)": 7500,
        "El Barzal (C3)": 8000,
        "Centro Villavicencio (C2)": 8500,
        "La Salle (C2)": 8500,
        "Nueva Andalucía (C2)": 9000,
    },
    # 🟠 ANILLO 3: Medio (7-15 km)
    "🟠 Anillo 3 - Medio (7-15km)": {
        "Comuna 1 (Nueva Granada, Galán)": 10000,
        "La Grama (C1)": 10500,
        "Evaristo Sourdis (C1)": 11000,
        "El Recreo (C4)": 11000,
        "Prados de Ciberia (C4)": 11500,
        "Cedritos (C4)": 12000,
        "Villa Fabiola (C4)": 12000,
        "Comuna 5 (Acapulco, Almendros)": 12500,
        "Comuna 6 (Pastrana, Macarena)": 13000,
    },
    # 🔴 ANILLO 4: Lejano (15+ km)
    "🔴 Anillo 4 - Lejano (15+km)": {
        "Comuna 7": 15000,
        "Comuna 8": 16000,
        "Acacías (Municipio)": 18000,
        "Restrepo": 20000,
        "Cumaral": 22000,
        "Veredas/Rural": 25000,
        "🤝 Personalizado (negociar)": 0,
    },
}

# Gastos frecuentes ajustados a la realidad de Villavicencio
GASTOS_FRECUENTES = {
    "⛽ Gasolina (Galón)": 17000,
    "🍲 Almuerzo": 12000,
    "🌙 Cena": 10000,
    "🔧 Mantenimiento moto": 25000,
    "🔋 Carga celular": 3000,
    "💧 Agua/Refresco": 2000,
    "🅿️ Parqueadero Centro": 3000,
    "🛞 Llanta/Reparación": 15000,
    "🏥 Salud/Farmacia": 8000,
    "📱 Datos móviles": 10000,
    "📝 Otro gasto": 0,
}

# =============================================================================
# BLOQUE 3: FUNCIONES AUXILIARES
# =============================================================================
def cargar_datos_web():
    """Lee el JSON. Si no existe, devuelve estructura vacía."""
    try:
        with open("datos_app.json", "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"domicilios": [], "gastos": [], "turnos": []}


def guardar_datos_web(datos):
    """Escribe los datos en JSON con formato legible."""
    with open("datos_app.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def filtrar_por_rango(lista, campo_fecha, inicio, fin):
    """Filtra una lista de registros por rango de fechas."""
    resultado = []
    for item in lista:
        fecha_str = item.get(campo_fecha, "")
        if not fecha_str:
            continue
        fecha_solo = fecha_str.split(" ")[0] if " " in fecha_str else fecha_str
        if inicio <= fecha_solo <= fin:
            resultado.append(item)
    return resultado


def calcular_estadisticas(domicilios, gastos):
    """Calcula ingresos, gastos y balance de listas filtradas."""
    ingresos = sum(d["valor"] + d.get("propina", 0) for d in domicilios)
    gastos_total = sum(g["valor"] for g in gastos)
    balance = ingresos - gastos_total
    return ingresos, gastos_total, balance

# =============================================================================
# BLOQUE 4: INICIALIZACIÓN DE SESIÓN (Para el Modo Turno)
# =============================================================================
if "turno_activo" not in st.session_state:
    st.session_state.turno_activo = False
if "turno_inicio" not in st.session_state:
    st.session_state.turno_inicio = None
if "turno_domicilios" not in st.session_state:
    st.session_state.turno_domicilios = []
if "turno_gastos" not in st.session_state:
    st.session_state.turno_gastos = []

# =============================================================================
# BLOQUE 5: CABECERA
# =============================================================================
st.title("🏍️ Domicilios Villavicencio")
st.caption("📍 Punto base: Amarilo, Hacienda Rosablanca - Meta")

# Indicador de turno activo
if st.session_state.turno_activo:
    horas_activa = (datetime.now() - st.session_state.turno_inicio).total_seconds() / 3600
    st.success(f"⏱️ **TURNO ACTIVO** desde {st.session_state.turno_inicio.strftime('%H:%M')} ({horas_activa:.1f}h transcurridas)")
else:
    st.info("🔴 No hay turno activo. Ve a la pestaña '⏱️ Turno' para iniciar.")

st.markdown("---")

# =============================================================================
# BLOQUE 6: NAVEGACIÓN POR TABS
# =============================================================================
tab_dashboard, tab_domicilios, tab_gastos, tab_historial, tab_analisis, tab_turno = st.tabs([
    "📊 Dashboard",
    "📦 Domicilio",
    "💸 Gasto",
    "🗂️ Historial",
    "📈 Análisis",
    "⏱️ Turno"
])

# =============================================================================
# TAB 1: DASHBOARD CON FILTROS DE FECHA
# =============================================================================
with tab_dashboard:
    st.subheader("📊 Panel de Control")
    
    # Filtro de Fecha
    st.markdown("### 📅 Período a analizar")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        periodo = st.selectbox(
            "Selecciona período:",
            options=["Hoy", "Ayer", "Últimos 7 días", "Este mes", "Personalizado"],
            index=0
        )
    
    hoy = datetime.now().date()
    
    if periodo == "Hoy":
        fecha_inicio = hoy
        fecha_fin = hoy
    elif periodo == "Ayer":
        fecha_inicio = hoy - timedelta(days=1)
        fecha_fin = hoy - timedelta(days=1)
    elif periodo == "Últimos 7 días":
        fecha_inicio = hoy - timedelta(days=6)
        fecha_fin = hoy
    elif periodo == "Este mes":
        fecha_inicio = hoy.replace(day=1)
        fecha_fin = hoy
    else:
        with col_f2:
            fecha_inicio = st.date_input("Desde:", value=hoy - timedelta(days=7))
        with col_f3:
            fecha_fin = st.date_input("Hasta:", value=hoy)
    
    inicio_str = fecha_inicio.strftime("%Y-%m-%d")
    fin_str = fecha_fin.strftime("%Y-%m-%d")
    
    st.markdown(f"**Mostrando datos del {inicio_str} al {fin_str}**")
    st.markdown("---")
    
    # Cargar y Filtrar Datos
    datos = cargar_datos_web()
    domicilios_filtrados = filtrar_por_rango(datos.get("domicilios", []), "fecha", inicio_str, fin_str)
    gastos_filtrados = filtrar_por_rango(datos.get("gastos", []), "fecha", inicio_str, fin_str)
    
    ingresos, gastos_total, balance = calcular_estadisticas(domicilios_filtrados, gastos_filtrados)
    promedio = ingresos / len(domicilios_filtrados) if domicilios_filtrados else 0
    
    # Métricas en 5 columnas
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📦 Domicilios", len(domicilios_filtrados))
    with col2:
        st.metric("💰 Ingresos", f"${ingresos:,}")
    with col3:
        st.metric("💸 Gastos", f"${gastos_total:,}")
    with col4:
        st.metric("📊 Balance", f"${balance:,}")
    with col5:
        st.metric("🎯 Promedio/domicilio", f"${int(promedio):,}")
    
    # Mensaje de Estado
    st.markdown("---")
    if balance > 0:
        st.success(f"🟢 ¡Excelente! Ganancia de **${balance:,}** en este período.")
    elif balance < 0:
        st.error(f"🔴 Atención: Pérdida de **${abs(balance):,}** en este período.")
    else:
        st.info("⚪ Balance en cero. No hay movimientos en este período.")
    
    # Gráfico Simple de Barras
    st.markdown("### 📈 Distribución Visual")
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.markdown(f"**Ingresos:**")
        st.progress(min(ingresos / max(ingresos + gastos_total, 1), 1.0))
        st.caption(f"${ingresos:,}")
    with col_graf2:
        st.markdown(f"**Gastos:**")
        st.progress(min(gastos_total / max(ingresos + gastos_total, 1), 1.0))
        st.caption(f"${gastos_total:,}")

# =============================================================================
# TAB 2: REGISTRAR DOMICILIO (Con Anillos Reales de Villavicencio)
# =============================================================================
with tab_domicilios:
    st.subheader("📦 Registrar Nuevo Domicilio")
    st.caption("📍 Punto base: Amarilo, Villavicencio - Meta")
    
    with st.form("registro_domicilio"):
        
        # NIVEL 1: Seleccionar Anillo
        anillo_seleccionado = st.selectbox(
            "🗺️ Anillo de distancia:",
            options=list(ZONAS_Y_TARIFAS.keys()),
            index=0
        )
        
        # NIVEL 2: Seleccionar Barrio específico del anillo
        lista_barrios = list(ZONAS_Y_TARIFAS[anillo_seleccionado].keys())
        barrio_seleccionado = st.selectbox(
            "📍 Barrio específico:",
            options=lista_barrios,
            index=0
        )
        
        # Dirección exacta
        direccion_detalle = st.text_input(
            "🏠 Dirección específica (calle, número, edificio):",
            placeholder="Ej: Calle 40 #15-20, Apt 302"
        )
        
        # Calcular valor según el barrio
        valor_base = ZONAS_Y_TARIFAS[anillo_seleccionado][barrio_seleccionado]
        
        # Si es zona negociada, permitir editar
        if "Personalizado" in barrio_seleccionado:
            valor_final = st.number_input(
                "💵 Valor acordado con el cliente:",
                min_value=0, step=500, value=0
            )
        else:
            st.info(f"💰 Tarifa sugerida para **{barrio_seleccionado}**: **${valor_base:,}**")
            valor_final = valor_base
        
        # Propina inteligente
        tipo_propina = st.radio(
            "🎁 Propina:",
            options=["Sin propina", "10%", "15%", "20%", "Personalizada"],
            horizontal=True
        )
        
        if tipo_propina == "Sin propina":
            propina = 0
        elif tipo_propina == "10%":
            propina = int(valor_final * 0.10)
        elif tipo_propina == "15%":
            propina = int(valor_final * 0.15)
        elif tipo_propina == "20%":
            propina = int(valor_final * 0.20)
        else:
            porcentaje = st.slider("Porcentaje:", 0, 50, 10, 1)
            propina = int(valor_final * (porcentaje / 100))
        
        # Resumen visual antes de guardar
        total = valor_final + propina
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("💵 Valor", f"${valor_final:,}")
        with col_res2:
            st.metric("🎁 Propina", f"${propina:,}")
        with col_res3:
            st.metric("💰 TOTAL", f"${total:,}")
        
        boton_dom = st.form_submit_button(
            "💾 Guardar Domicilio", 
            use_container_width=True, 
            type="primary"
        )
    
    # Lógica de guardado
    if boton_dom:
        if direccion_detalle.strip() == "":
            st.error("⚠️ Ingresa la dirección específica.")
        elif valor_final == 0:
            st.error("⚠️ El valor no puede ser cero.")
        else:
            datos = cargar_datos_web()
            nuevo = {
                "anillo": anillo_seleccionado,
                "barrio": barrio_seleccionado,
                "zona": anillo_seleccionado,
                "direccion": direccion_detalle,
                "valor": int(valor_final),
                "propina": int(propina),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            datos["domicilios"].append(nuevo)
            guardar_datos_web(datos)
            
            if st.session_state.turno_activo:
                st.session_state.turno_domicilios.append(nuevo)
            
            st.success(f"✅ Domicilio registrado en {barrio_seleccionado}")
            st.balloons()

# =============================================================================
# TAB 3: REGISTRAR GASTO
# =============================================================================
with tab_gastos:
    st.subheader("💸 Registrar Gasto Rápido")
    
    with st.form("registro_gasto"):
        col_g, col_v = st.columns([2, 1])
        with col_g:
            gasto_sel = st.selectbox("¿Qué gasto?", options=list(GASTOS_FRECUENTES.keys()), index=0)
        
        valor_sug = GASTOS_FRECUENTES[gasto_sel]
        
        if gasto_sel == "📝 Otro gasto":
            concepto = st.text_input("📝 Describe el gasto:", placeholder="Ej: Repuesto")
            valor_ini = 0
        else:
            concepto = gasto_sel
            valor_ini = valor_sug
        
        with col_v:
            valor_gasto = st.number_input("💵 Valor:", min_value=0, step=500, value=valor_ini)
        
        if valor_sug > 0 and gasto_sel != "📝 Otro gasto":
            st.caption(f"💡 Valor típico: ${valor_sug:,}")
        
        boton_gas = st.form_submit_button("💾 Guardar Gasto", use_container_width=True)
    
    if boton_gas:
        if concepto.strip() == "":
            st.error("⚠️ Ingresa un concepto.")
        elif valor_gasto == 0:
            st.error("⚠️ El valor no puede ser cero.")
        else:
            datos = cargar_datos_web()
            nuevo = {
                "concepto": concepto,
                "valor": int(valor_gasto),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            datos["gastos"].append(nuevo)
            guardar_datos_web(datos)
            
            if st.session_state.turno_activo:
                st.session_state.turno_gastos.append(nuevo)
            
            st.success(f"✅ Gasto registrado: {concepto} - ${valor_gasto:,}")
            st.balloons()

# =============================================================================
# TAB 4: HISTORIAL CON FILTROS
# =============================================================================
with tab_historial:
    st.subheader("🗂️ Historial Completo")
    
    # Filtros del historial
    col_fh1, col_fh2 = st.columns(2)
    with col_fh1:
        filtro_tipo = st.radio("Mostrar:", ["Domicilios", "Gastos", "Ambos"], horizontal=True)
    with col_fh2:
        filtro_busqueda = st.text_input("🔍 Buscar por texto:", placeholder="Ej: Amarilo, Gasolina...")
    
    datos = cargar_datos_web()
    lista_dom = datos.get("domicilios", [])
    lista_gas = datos.get("gastos", [])
    
    # Aplicar filtro de búsqueda
    if filtro_busqueda.strip():
        texto = filtro_busqueda.lower()
        lista_dom = [d for d in lista_dom if texto in d.get("direccion", "").lower() or texto in d.get("barrio", "").lower()]
        lista_gas = [g for g in lista_gas if texto in g.get("concepto", "").lower()]
    
    sub_dom, sub_gas = st.tabs(["📦 Domicilios", "💸 Gastos"])
    
    with sub_dom:
        if filtro_tipo == "Gastos":
            st.info("Filtro activo: mostrando solo gastos. Cambia a 'Domicilios' o 'Ambos'.")
        elif not lista_dom:
            st.info("📭 No hay domicilios.")
        else:
            st.caption(f"Total: {len(lista_dom)} registros")
            for i, dom in enumerate(reversed(lista_dom), 1):
                total = dom["valor"] + dom.get("propina", 0)
                with st.expander(f"📦 #{len(lista_dom) - i + 1} | {dom.get('barrio', '?')} | ${total:,} | {dom.get('fecha', 'N/A')}"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        st.write(f"**Dirección:** {dom['direccion']}")
                        st.write(f"**Barrio:** {dom.get('barrio', 'N/A')}")
                        st.write(f"**Anillo:** {dom.get('anillo', 'N/A')}")
                    with col_e2:
                        st.write(f"**Valor:** ${dom['valor']:,}")
                        st.write(f"**Propina:** ${dom.get('propina', 0):,}")
                    st.write(f"**Fecha:** {dom.get('fecha', 'N/A')}")
    
    with sub_gas:
        if filtro_tipo == "Domicilios":
            st.info("Filtro activo: mostrando solo domicilios.")
        elif not lista_gas:
            st.info("📭 No hay gastos.")
        else:
            st.caption(f"Total: {len(lista_gas)} registros")
            for i, gas in enumerate(reversed(lista_gas), 1):
                with st.expander(f"💸 #{len(lista_gas) - i + 1} | {gas['concepto']} | ${gas['valor']:,} | {gas.get('fecha', 'N/A')}"):
                    st.write(f"**Concepto:** {gas['concepto']}")
                    st.write(f"**Valor:** ${gas['valor']:,}")
                    st.write(f"**Fecha:** {gas.get('fecha', 'N/A')}")

# =============================================================================
# TAB 5: ANÁLISIS POR ANILLO (NUEVO)
# =============================================================================
with tab_analisis:
    st.subheader("📊 Análisis por Anillo de Distancia")
    st.caption("¿Qué tan rentable es cada zona?")
    
    datos = cargar_datos_web()
    lista_dom = datos.get("domicilios", [])
    
    if not lista_dom:
        st.info("📭 Aún no hay domicilios registrados para analizar.")
    else:
        # Calcular estadísticas por anillo
        estadisticas_anillos = {}
        
        for anillo in ZONAS_Y_TARIFAS.keys():
            # Filtrar domicilios de este anillo
            domicilios_anillo = [d for d in lista_dom if d.get("anillo") == anillo]
            
            if domicilios_anillo:
                ingresos_anillo = sum(d["valor"] + d.get("propina", 0) for d in domicilios_anillo)
                cantidad = len(domicilios_anillo)
                promedio_anillo = ingresos_anillo / cantidad
            else:
                ingresos_anillo = 0
                cantidad = 0
                promedio_anillo = 0
            
            estadisticas_anillos[anillo] = {
                "cantidad": cantidad,
                "ingresos": ingresos_anillo,
                "promedio": promedio_anillo
            }
        
        # Mostrar en tabla
        st.markdown("### 📋 Resumen por Anillo")
        
        for anillo, stats in estadisticas_anillos.items():
            if stats["cantidad"] > 0:
                with st.expander(f"{anillo} - {stats['cantidad']} domicilios"):
                    col_a1, col_a2, col_a3 = st.columns(3)
                    with col_a1:
                        st.metric("📦 Cantidad", stats["cantidad"])
                    with col_a2:
                        st.metric("💰 Ingresos", f"${stats['ingresos']:,}")
                    with col_a3:
                        st.metric("🎯 Promedio", f"${int(stats['promedio']):,}")
            else:
                st.caption(f"{anillo}: Sin domicilios registrados")
        
        # Gráfico de barras simple
        st.markdown("---")
        st.markdown("### 📈 Ingresos por Anillo")
        
        anillos_con_datos = {k: v for k, v in estadisticas_anillos.items() if v["ingresos"] > 0}
        
        if anillos_con_datos:
            max_ingresos = max(v["ingresos"] for v in anillos_con_datos.values())
            
            for anillo, stats in anillos_con_datos.items():
                porcentaje = (stats["ingresos"] / max_ingresos) * 100
                st.markdown(f"**{anillo}**")
                st.progress(porcentaje / 100)
                st.caption(f"${stats['ingresos']:,} ({stats['cantidad']} domicilios)")
        else:
            st.info("No hay datos para mostrar")

# =============================================================================
# TAB 6: MODO TURNO DE TRABAJO
# =============================================================================
with tab_turno:
    st.subheader("⏱️ Control de Turno")
    st.markdown("Registra el inicio y cierre de tu jornada laboral para ver tu rendimiento real.")
    
    if not st.session_state.turno_activo:
        # ESTADO: SIN TURNO ACTIVO
        st.warning("🔴 No hay turno activo.")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("▶️ INICIAR TURNO", use_container_width=True, type="primary"):
                st.session_state.turno_activo = True
                st.session_state.turno_inicio = datetime.now()
                st.session_state.turno_domicilios = []
                st.session_state.turno_gastos = []
                st.rerun()
        
        with col_t2:
            st.info("💡 Al iniciar un turno, todos los domicilios y gastos que registres se asociarán automáticamente a esta jornada.")
    
    else:
        # ESTADO: TURNO ACTIVO
        tiempo_transcurrido = datetime.now() - st.session_state.turno_inicio
        horas = int(tiempo_transcurrido.total_seconds() // 3600)
        minutos = int((tiempo_transcurrido.total_seconds() % 3600) // 60)
        
        st.success(f"🟢 **Turno activo** desde {st.session_state.turno_inicio.strftime('%H:%M:%S')}")
        st.metric("⏱️ Tiempo transcurrido", f"{horas}h {minutos}m")
        
        # Estadísticas del turno en tiempo real
        ing_turno = sum(d["valor"] + d.get("propina", 0) for d in st.session_state.turno_domicilios)
        gas_turno = sum(g["valor"] for g in st.session_state.turno_gastos)
        bal_turno = ing_turno - gas_turno
        
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.metric("📦 Domicilios", len(st.session_state.turno_domicilios))
        with col_t2:
            st.metric("💰 Ingresos", f"${ing_turno:,}")
        with col_t3:
            st.metric("💸 Gastos", f"${gas_turno:,}")
        with col_t4:
            st.metric("📊 Balance", f"${bal_turno:,}")
        
        st.markdown("---")
        
        # Botón de cierre de turno
        if st.button("⏹️ CERRAR TURNO Y GENERAR REPORTE", use_container_width=True, type="primary"):
            tiempo_final = datetime.now()
            duracion = tiempo_final - st.session_state.turno_inicio
            
            registro_turno = {
                "inicio": st.session_state.turno_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                "fin": tiempo_final.strftime("%Y-%m-%d %H:%M:%S"),
                "duracion_minutos": int(duracion.total_seconds() / 60),
                "domicilios": len(st.session_state.turno_domicilios),
                "ingresos": ing_turno,
                "gastos": gas_turno,
                "balance": bal_turno,
                "fecha": tiempo_final.strftime("%Y-%m-%d")
            }
            
            datos = cargar_datos_web()
            if "turnos" not in datos:
                datos["turnos"] = []
            datos["turnos"].append(registro_turno)
            guardar_datos_web(datos)
            
            st.markdown("## 📋 REPORTE DE TURNO")
            st.markdown("---")
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.write(f"**🕐 Inicio:** {registro_turno['inicio']}")
                st.write(f"**🕐 Fin:** {registro_turno['fin']}")
                st.write(f"**⏱️ Duración:** {registro_turno['duracion_minutos']} minutos")
            with col_r2:
                st.write(f"**📦 Domicilios:** {registro_turno['domicilios']}")
                st.write(f"**💰 Ingresos:** ${registro_turno['ingresos']:,}")
                st.write(f"**💸 Gastos:** ${registro_turno['gastos']:,}")
            
            st.markdown("---")
            if bal_turno > 0:
                st.success(f"### 🟢 GANANCIA NETA: ${bal_turno:,}")
                st.write(f"**Ganancia por hora:** ${bal_turno / max(duracion.total_seconds() / 3600, 0.01):,.0f}")
            else:
                st.error(f"### 🔴 PÉRDIDA NETA: ${abs(bal_turno):,}")
            
            st.balloons()
            
            st.session_state.turno_activo = False
            st.session_state.turno_inicio = None
            st.session_state.turno_domicilios = []
            st.session_state.turno_gastos = []
            
            st.info("✅ Turno cerrado y guardado. Puedes iniciar uno nuevo cuando quieras.")

# =============================================================================
# PIE DE PÁGINA
# =============================================================================
st.markdown("---")
st.caption(f"🏍️ Domicilios Villavicencio v5.0 | Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
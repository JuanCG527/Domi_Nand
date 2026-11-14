# =============================================================================
# BLOQUE 1: IMPORTACIONES Y CONFIGURACIÓN
# =============================================================================
import streamlit as st
import json
from datetime import datetime

# Configuración de la página (debe ser lo PRIMERO que se ejecute)
st.set_page_config(
    page_title="Mi App de Domicilios",
    page_icon="🏍️",
    layout="wide"  # 'wide' aprovecha todo el ancho de la pantalla
)

# =============================================================================
# BLOQUE 2: CATÁLOGOS (DATOS QUE NO CAMBIAN FRECUENTEMENTE)
# =============================================================================
# Zonas y sus tarifas base. Si cambias un precio, solo editas aquí.
ZONAS_Y_TARIFAS = {
    "Zona Norte - Cercana": 7000,
    "Zona Norte - Lejana": 9000,
    "Zona Sur - Cercana": 7500,
    "Zona Sur - Lejana": 9500,
    "Zona Centro": 6000,
    "Zona Occidente": 8000,
    "Zona Oriental": 8500,
    "Zona Especial (negociar)": 0,
}

# Gastos frecuentes con sus valores típicos.
GASTOS_FRECUENTES = {
    "Gasolina": 15000,
    "Almuerzo": 12000,
    "Cena": 10000,
    "Mantenimiento moto": 25000,
    "Carga celular": 3000,
    "Agua/Refresco": 2000,
    "Parqueadero": 3000,
    "Otro gasto": 0,
}

# =============================================================================
# BLOQUE 3: FUNCIONES AUXILIARES (PERSISTENCIA)
# =============================================================================
def cargar_datos_web():
    """Lee el archivo JSON. Si no existe o está corrupto, devuelve estructura vacía."""
    try:
        with open("datos_app.json", "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"domicilios": [], "gastos": []}


def guardar_datos_web(datos):
    """Escribe los datos en JSON con formato legible (indent=4)."""
    with open("datos_app.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

# =============================================================================
# BLOQUE 4: CABECERA DE LA APP
# =============================================================================
st.title("🏍️ Sistema de Domicilios")
st.caption("Registra, controla y analiza tu trabajo diario")
st.markdown("---")

# =============================================================================
# BLOQUE 5: NAVEGACIÓN POR TABS (La mejora visual clave)
# =============================================================================
# st.tabs crea pestañas interactivas. Cada variable es una pestaña.
tab_dashboard, tab_domicilios, tab_gastos, tab_historial = st.tabs([
    "📊 Dashboard",
    "📦 Registrar Domicilio",
    "💸 Registrar Gasto",
    "🗂️ Historial"
])

# =============================================================================
# TAB 1: DASHBOARD (Resumen visual del día)
# =============================================================================
with tab_dashboard:
    st.subheader("📊 Resumen del Día")
    
    # Cargar datos una sola vez
    datos_actuales = cargar_datos_web()
    lista_domicilios = datos_actuales.get("domicilios", [])
    lista_gastos = datos_actuales.get("gastos", [])
    
    # Fecha de hoy en formato "YYYY-MM-DD"
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    # Filtrar solo lo de hoy (List Comprehension con condición)
    domicilios_hoy = [d for d in lista_domicilios if d.get("fecha", "").startswith(hoy)]
    gastos_hoy = [g for g in lista_gastos if g.get("fecha", "").startswith(hoy)]
    
    # Calcular totales del día
    ingresos_hoy = sum(d["valor"] + d["propina"] for d in domicilios_hoy)
    gastos_hoy_total = sum(g["valor"] for g in gastos_hoy)
    balance_hoy = ingresos_hoy - gastos_hoy_total
    
    # Calcular promedio por domicilio (con protección contra división por cero)
    promedio_hoy = ingresos_hoy / len(domicilios_hoy) if domicilios_hoy else 0
    
    # Mostrar métricas en 5 columnas
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📦 Domicilios", len(domicilios_hoy))
    with col2:
        st.metric("💰 Ingresos", f"${ingresos_hoy:,}")
    with col3:
        st.metric("💸 Gastos", f"${gastos_hoy_total:,}")
    with col4:
        st.metric("📊 Balance", f"${balance_hoy:,}")
    with col5:
        st.metric("🎯 Promedio", f"${int(promedio_hoy):,}")
    
    # Estado de ánimo del día (lógica condicional simple)
    st.markdown("---")
    if balance_hoy > 0:
        st.success(f"🟢 ¡Buen día! Ganaste ${balance_hoy:,} hoy.")
    elif balance_hoy < 0:
        st.error(f"🔴 Cuidado: Perdiste ${abs(balance_hoy):,} hoy.")
    else:
        st.info("⚪ Aún no hay movimientos hoy. ¡Empieza a registrar!")

# =============================================================================
# TAB 2: REGISTRAR DOMICILIO (Con zonas y propinas inteligentes)
# =============================================================================
with tab_domicilios:
    st.subheader("📦 Registrar Nuevo Domicilio")
    
    with st.form("registro_domicilio"):
        # Fila 1: Zona y dirección
        col_zona, col_direccion = st.columns([1, 2])
        with col_zona:
            zona_seleccionada = st.selectbox(
                "🗺️ Zona",
                options=list(ZONAS_Y_TARIFAS.keys()),
                index=0
            )
        with col_direccion:
            direccion_detalle = st.text_input(
                "📍 Dirección específica",
                placeholder="Ej: Calle 45 #12-30"
            )
        
        # Fila 2: Valor base (solo lectura)
        valor_base = ZONAS_Y_TARIFAS[zona_seleccionada]
        
        if zona_seleccionada == "Zona Especial (negociar)":
            valor_final = st.number_input(
                "💵 Valor a cobrar:",
                min_value=0, step=500, value=0
            )
        else:
            st.info(f"💰 Valor base de la zona: **${valor_base:,}**")
            valor_final = valor_base
        
        # Fila 3: Propina inteligente con radio buttons
        # (Los radio buttons SÍ funcionan dentro de forms, a diferencia de st.button)
        tipo_propina = st.radio(
            "🎁 Propina sugerida:",
            options=["Sin propina", "10%", "15%", "20%", "Personalizada"],
            horizontal=True  # Los botones aparecen en fila, no en columna
        )
        
        # Calcular propina según lo elegido
        if tipo_propina == "Sin propina":
            propina = 0
        elif tipo_propina == "10%":
            propina = int(valor_final * 0.10)
        elif tipo_propina == "15%":
            propina = int(valor_final * 0.15)
        elif tipo_propina == "20%":
            propina = int(valor_final * 0.20)
        else:  # Personalizada
            porcentaje = st.slider(
                "Ajusta el porcentaje:",
                min_value=0, max_value=50, value=10, step=1
            )
            propina = int(valor_final * (porcentaje / 100))
        
        st.caption(f"🎯 Propina calculada: **${propina:,}**")
        
        # Fila 4: Total y botón
        total = valor_final + propina
        st.markdown(f"### 💰 Total a cobrar: ${total:,}")
        
        boton_guardar = st.form_submit_button("💾 Guardar Domicilio", use_container_width=True)
    
    # Lógica de guardado (fuera del form)
    if boton_guardar:
        if direccion_detalle.strip() == "":
            st.error("⚠️ Debes ingresar la dirección específica.")
        elif valor_final == 0:
            st.error("⚠️ El valor del domicilio no puede ser cero.")
        else:
            datos = cargar_datos_web()
            nuevo_domicilio = {
                "zona": zona_seleccionada,
                "direccion": direccion_detalle,
                "valor": int(valor_final),
                "propina": int(propina),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            datos["domicilios"].append(nuevo_domicilio)
            guardar_datos_web(datos)
            st.success(f"✅ Domicilio registrado en {zona_seleccionada}")
            st.balloons()

# =============================================================================
# TAB 3: REGISTRAR GASTO (Con catálogo de gastos frecuentes)
# =============================================================================
with tab_gastos:
    st.subheader("💸 Registrar Gasto Rápido")
    
    with st.form("registro_gasto"):
        col_gasto, col_valor = st.columns([2, 1])
        
        with col_gasto:
            gasto_seleccionado = st.selectbox(
                "¿Qué gasto registras?",
                options=list(GASTOS_FRECUENTES.keys()),
                index=0
            )
        
        valor_sugerido = GASTOS_FRECUENTES[gasto_seleccionado]
        
        # Si es "Otro gasto", pedir concepto personalizado
        if gasto_seleccionado == "Otro gasto":
            concepto_final = st.text_input(
                "📝 Describe el gasto:",
                placeholder="Ej: Repuesto, Multa, etc."
            )
            valor_inicial = 0
        else:
            concepto_final = gasto_seleccionado
            valor_inicial = valor_sugerido
        
        with col_valor:
            valor_gasto = st.number_input(
                "💵 Valor del gasto:",
                min_value=0, step=500, value=valor_inicial
            )
        
        # Mostrar valor típico como referencia
        if valor_sugerido > 0:
            st.caption(f"💡 Valor típico de '{gasto_seleccionado}': ${valor_sugerido:,}")
        
        boton_guardar_gasto = st.form_submit_button("💾 Guardar Gasto", use_container_width=True)
    
    if boton_guardar_gasto:
        if concepto_final.strip() == "":
            st.error("⚠️ Debes ingresar un concepto para el gasto.")
        elif valor_gasto == 0:
            st.error("⚠️ El valor del gasto no puede ser cero.")
        else:
            datos = cargar_datos_web()
            nuevo_gasto = {
                "concepto": concepto_final,
                "valor": int(valor_gasto),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            datos["gastos"].append(nuevo_gasto)
            guardar_datos_web(datos)
            st.success(f"✅ Gasto registrado: {concepto_final} - ${valor_gasto:,}")
            st.balloons()

# =============================================================================
# TAB 4: HISTORIAL (Ver todos los registros)
# =============================================================================
with tab_historial:
    st.subheader("🗂️ Historial Completo")
    
    datos = cargar_datos_web()
    lista_domicilios = datos.get("domicilios", [])
    lista_gastos = datos.get("gastos", [])
    
    # Sub-tabs dentro del historial
    sub_domi, sub_gastos = st.tabs(["📦 Domicilios", "💸 Gastos"])
    
    with sub_domi:
        if not lista_domicilios:
            st.info("📭 Aún no hay domicilios registrados.")
        else:
            # Mostrar en orden inverso (más reciente primero)
            for i, dom in enumerate(reversed(lista_domicilios), 1):
                total = dom["valor"] + dom["propina"]
                with st.expander(f"📦 #{len(lista_domicilios) - i + 1} - {dom.get('zona', 'Sin zona')} - ${total:,}"):
                    st.write(f"**Dirección:** {dom['direccion']}")
                    st.write(f"**Valor:** ${dom['valor']:,}")
                    st.write(f"**Propina:** ${dom['propina']:,}")
                    st.write(f"**Fecha:** {dom.get('fecha', 'N/A')}")
    
    with sub_gastos:
        if not lista_gastos:
            st.info("📭 Aún no hay gastos registrados.")
        else:
            for i, gas in enumerate(reversed(lista_gastos), 1):
                with st.expander(f"💸 #{len(lista_gastos) - i + 1} - {gas['concepto']} - ${gas['valor']:,}"):
                    st.write(f"**Concepto:** {gas['concepto']}")
                    st.write(f"**Valor:** ${gas['valor']:,}")
                    st.write(f"**Fecha:** {gas.get('fecha', 'N/A')}")
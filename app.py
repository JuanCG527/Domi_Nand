# =============================================================================
# IMPORTACIONES
# =============================================================================
import streamlit as st
import json
from datetime import datetime

# =============================================================================
# CATÁLOGO DE ZONAS Y TARIFAS
# =============================================================================
# Aquí defines tus zonas y precios. Si cambias un precio, solo editas esto.

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

# =============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# =============================================================================
st.set_page_config(page_title="Mi App de Domicilios", page_icon="🏍️", layout="wide")

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def cargar_datos_web():
    """Carga los datos del archivo JSON. Si no existe, devuelve listas vacías."""
    try:
        with open("datos_app.json", "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"domicilios": [], "gastos": []}


def guardar_datos_web(datos):
    """Guarda los datos en el archivo JSON con formato legible."""
    with open("datos_app.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

# =============================================================================
# TÍTULO PRINCIPAL
# =============================================================================
st.title("🏍️ Sistema de Domicilios")
# =============================================================================
# DASHBOARD: RESUMEN DEL DÍA
# =============================================================================
# Cargamos los datos para mostrar estadísticas en tiempo real
datos_actuales = cargar_datos_web()
lista_domicilios = datos_actuales.get("domicilios", [])
lista_gastos = datos_actuales.get("gastos", [])

# Obtener la fecha de hoy en el mismo formato que guardamos
hoy = datetime.now().strftime("%Y-%m-%d")

# FILTRAR: Solo domicilios de hoy
# (Agrupación: de todos los domicilios, sacamos solo los de hoy)
domicilios_hoy = [
    d for d in lista_domicilios 
    if d.get("fecha", "").startswith(hoy)
]

# FILTRAR: Solo gastos de hoy
gastos_hoy = [
    g for g in lista_gastos 
    if g.get("fecha", "").startswith(hoy)
]

# CALCULAR totales del día
total_ingresos_hoy = sum(d["valor"] + d["propina"] for d in domicilios_hoy)
total_gastos_hoy = sum(g["valor"] for g in gastos_hoy)
balance_hoy = total_ingresos_hoy - total_gastos_hoy

# CALCULAR totales generales (toda la historia)
total_ingresos_general = sum(d["valor"] + d["propina"] for d in lista_domicilios)
total_gastos_general = sum(g["valor"] for g in lista_gastos)
balance_general = total_ingresos_general - total_gastos_general

# =============================================================================
# MOSTRAR EL DASHBOARD EN PANTALLA
# =============================================================================
# st.columns divide la pantalla en columnas (como una tabla)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📦 Domicilios Hoy",
        value=len(domicilios_hoy),
        delta=None
    )

with col2:
    st.metric(
        label="💰 Ingresos Hoy",
        value=f"${total_ingresos_hoy:,}",
        delta=None
    )

with col3:
    st.metric(
        label="💸 Gastos Hoy",
        value=f"${total_gastos_hoy:,}",
        delta=None
    )

with col4:
    # El delta muestra si ganaste (+) o perdiste (-) con color automático
    st.metric(
        label="📊 Balance Hoy",
        value=f"${balance_hoy:,}",
        delta=f"${balance_hoy:,}" if balance_hoy != 0 else None
    )

# Separador visual
st.markdown("---")

# Resumen general (toda la historia)
with st.expander("📈 Ver resumen histórico completo"):
    col_hist1, col_hist2, col_hist3 = st.columns(3)
    with col_hist1:
        st.info(f"**Total histórico de ingresos:**\n${total_ingresos_general:,}")
    with col_hist2:
        st.warning(f"**Total histórico de gastos:**\n${total_gastos_general:,}")
    with col_hist3:
        if balance_general > 0:
            st.success(f"**Ganancia neta total:**\n${balance_general:,}")
        elif balance_general < 0:
            st.error(f"**Pérdida neta total:**\n${abs(balance_general):,}")
        else:
            st.info("**Balance en cero**")
st.markdown("---")

# =============================================================================
# FORMULARIO DE REGISTRO DE DOMICILIO
# =============================================================================
with st.form("registro_domicilio"):
    st.subheader("📝 Registrar Nuevo Domicilio")
    
    # Selector de zona
    zona_seleccionada = st.selectbox(
        "🗺️ Selecciona la zona:",
        options=list(ZONAS_Y_TARIFAS.keys()),
        index=0
    )
    
    # Dirección específica
    direccion_detalle = st.text_input(
        "📍 Dirección específica (calle, número, barrio):",
        placeholder="Ej: Calle 45 #12-30, Barrio La Esperanza"
    )
    
    # Calcular valor base según la zona
    valor_base = ZONAS_Y_TARIFAS[zona_seleccionada]
    
    # Mostrar el precio automáticamente
    st.info(f"💰 Valor base de la zona: **${valor_base:,}**")
    
    # Si es zona especial, permitir editar el valor
    if zona_seleccionada == "Zona Especial (negociar)":
        valor_final = st.number_input(
            "💵 Ingresa el valor acordado:",
            min_value=0,
            step=500,
            value=0
        )
    else:
        valor_final = valor_base
    
    # Propina
   # Propinas inteligentes con botones de porcentaje
st.markdown("🎁 **Propina sugerida:**")

# Crear 3 columnas para los botones de propina
col_prop1, col_prop2, col_prop3 = st.columns(3)

with col_prop1:
    if st.button("10%"):
        st.session_state.propina_calc = int(valor_final * 0.10)

with col_prop2:
    if st.button("15%"):
        st.session_state.propina_calc = int(valor_final * 0.15)

with col_prop3:
    if st.button("20%"):
        st.session_state.propina_calc = int(valor_final * 0.20)

# Si no se ha calculado propina, iniciar en 0
if "propina_calc" not in st.session_state:
    st.session_state.propina_calc = 0

# Mostrar la propina calculada y permitir editarla
propina = st.number_input(
    "💵 Valor de propina (puedes editar):",
    min_value=0,
    step=500,
    value=st.session_state.propina_calc
)

# Resetear después de usar
if boton_guardar:
    st.session_state.propina_calc = 0
    
    
    # Botón de guardar (IMPORTANTE: debe estar DENTRO del form)
    boton_guardar = st.form_submit_button("💾 Guardar Domicilio")
# =============================================================================
# FORMULARIO DE GASTOS RÁPIDOS
# =============================================================================
st.markdown("---")
st.subheader("💸 Registrar Gasto Rápido")

# Catálogo de gastos frecuentes
GASTOS_FRECUENTES = {
    "Gasolina": 15000,
    "Almuerzo": 12000,
    "Cena": 10000,
    "Mantenimiento moto": 25000,
    "Carga celular": 3000,
    "Agua/Refresco": 2000,
    "Parqueadero": 3000,
    "Otro gasto": 0
}

with st.form("registro_gasto_rapido"):
    # Selector de gasto frecuente
    gasto_seleccionado = st.selectbox(
        "¿Qué gasto registras?",
        options=list(GASTOS_FRECUENTES.keys()),
        index=0
    )
    
    # Mostrar valor sugerido
    valor_sugerido = GASTOS_FRECUENTES[gasto_seleccionado]
    st.caption(f"💡 Valor típico: ${valor_sugerido:,}")
    
    # Si es "Otro gasto", permitir escribir el concepto
    if gasto_seleccionado == "Otro gasto":
        concepto_personalizado = st.text_input(
            "Describe el gasto:",
            placeholder="Ej: Repuesto, Multa, etc."
        )
        concepto_final = concepto_personalizado
    else:
        concepto_final = gasto_seleccionado
    
    # Valor del gasto (editable si es necesario)
    valor_gasto = st.number_input(
        "Valor del gasto:",
        min_value=0,
        step=500,
        value=valor_sugerido if valor_sugerido > 0 else 0
    )
    
    # Botón de guardar gasto
    boton_guardar_gasto = st.form_submit_button("💾 Guardar Gasto")

# =============================================================================
# LÓGICA DE PROCESAMIENTO DE GASTOS
# =============================================================================
if boton_guardar_gasto:
    if concepto_final.strip() == "":
        st.error("️ Debes ingresar un concepto para el gasto.")
    elif valor_gasto == 0:
        st.error("⚠️ El valor del gasto no puede ser cero.")
    else:
        # Cargar datos existentes
        datos = cargar_datos_web()
        
        # Crear el nuevo gasto
        nuevo_gasto = {
            "concepto": concepto_final,
            "valor": int(valor_gasto),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # Agregarlo a la lista
        datos["gastos"].append(nuevo_gasto)
        
        # Guardar en el archivo
        guardar_datos_web(datos)
        
        # Mensaje de éxito
        st.success(f"✅ Gasto registrado: {concepto_final} - ${valor_gasto:,}")
        st.balloons()
# =============================================================================
# LÓGICA DE PROCESAMIENTO (FUERA del form, pero usa la variable)
# =============================================================================
if boton_guardar:
    if direccion_detalle.strip() == "":
        st.error("⚠️ Debes ingresar la dirección específica.")
    elif valor_final == 0 and zona_seleccionada == "Zona Especial (negociar)":
        st.error("⚠️ Debes ingresar un valor para zona especial.")
    else:
        # Cargar datos existentes
        datos = cargar_datos_web()
        
        # Crear el nuevo domicilio
        nuevo_domicilio = {
            "zona": zona_seleccionada,
            "direccion": direccion_detalle,
            "valor": int(valor_final),
            "propina": int(propina),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # Agregarlo a la lista
        datos["domicilios"].append(nuevo_domicilio)
        
        # Guardar en el archivo
        guardar_datos_web(datos)
        
        # Calcular total
        total = valor_final + propina
        
        # Mensaje de éxito
        st.success(f"""
            ✅ ¡Domicilio registrado exitosamente!
            - Zona: {zona_seleccionada}
            - Dirección: {direccion_detalle}
            - Valor: ${valor_final:,}
            - Propina: ${propina:,}
            - **Total: ${total:,}**
        """)
        st.balloons()
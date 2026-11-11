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
    propina = st.number_input(
        "🎁 Propina (opcional):",
        min_value=0,
        step=500,
        value=0
    )
    
    # Botón de guardar (IMPORTANTE: debe estar DENTRO del form)
    boton_guardar = st.form_submit_button("💾 Guardar Domicilio")

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
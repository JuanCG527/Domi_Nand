# Importamos la librería que convierte Python en Web App
import streamlit as st
import json
from datetime import datetime
# =============================================================================
# CATÁLOGO DE ZONAS Y TARIFAS
# =============================================================================
# Este diccionario define las zonas disponibles y sus precios base.
# Si necesitas cambiar un precio, solo modificas este diccionario.

ZONAS_Y_TARIFAS = {
    "Zona Norte - Cercana": 7000,
    "Zona Norte - Lejana": 9000,
    "Zona Sur - Cercana": 7500,
    "Zona Sur - Lejana": 9500,
    "Zona Centro": 6000,
    "Zona Occidente": 8000,
    "Zona Oriental": 8500,
    "Zona Especial (negociar)": 0,  # Precio manual
}

# Configuramos la página de la app
st.set_page_config(page_title="Mi App de Domicilios", page_icon="🏍️")

# Función para cargar datos existentes
def cargar_datos_web():
    try:
        with open("datos_app.json", "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"domicilios": [], "gastos": []}

# Función para guardar datos
def guardar_datos_web(datos):
    with open("datos_app.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

# TÍTULO PRINCIPAL
st.title("️ Sistema de Domicilios")

# SEPARADOR VISUAL
st.markdown("---")

# FORMULARIO DE REGISTRO
# FORMULARIO DE REGISTRO MEJORADO
with st.form("registro_domicilio"):
    st.subheader("📝 Registrar Nuevo Domicilio")
    
    # Selector de zona (reemplaza el text_input de dirección)
    zona_seleccionada = st.selectbox(
        "🗺️ Selecciona la zona:",
        options=list(ZONAS_Y_TARIFAS.keys()),
        index=0  # La primera zona aparece seleccionada por defecto
    )
    
    # Dirección específica (calle, número, barrio)
    direccion_detalle = st.text_input(
        "📍 Dirección específica (calle, número, barrio):",
        placeholder="Ej: Calle 45 #12-30, Barrio La Esperanza"
    )
    
    # El valor se calcula automáticamente según la zona
    valor_base = ZONAS_Y_TARIFAS[zona_seleccionada]
    
    # Mostrar el precio calculado (solo lectura, el usuario no lo edita)
    st.info(f"💰 Valor base de la zona: **${valor_base:,}**")
    
    # Si eligió "Zona Especial", permitir editar el valor manualmente
    if zona_seleccionada == "Zona Especial (negociar)":
        valor_final = st.number_input(
            "💵 Ingresa el valor acordado:",
            min_value=0,
            step=500,
            value=0
        )
    else:
        valor_final = valor_base
    
    # Propina (opcional)
    propina = st.number_input(
        "🎁 Propina (opcional):",
        min_value=0,
        step=500,
        value=0
    )
    
    # LÓGICA DE PROCESAMIENTO
if boton_guardar:
    # Validación: la dirección específica no puede estar vacía
    if direccion_detalle.strip() == "":
        st.error("⚠️ Debes ingresar la dirección específica.")
    elif valor_final == 0 and zona_seleccionada == "Zona Especial (negociar)":
        st.error("⚠️ Debes ingresar un valor para zona especial.")
    else:
        # 1. Cargar datos existentes
        datos = cargar_datos_web()
        
        # 2. Crear el nuevo domicilio con TODOS los datos
        nuevo_domicilio = {
            "zona": zona_seleccionada,           # NUEVO: guardamos la zona
            "direccion": direccion_detalle,       # Ahora es la dirección específica
            "valor": int(valor_final),            # Valor calculado o manual
            "propina": int(propina),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # 3. Agregarlo a la lista
        datos["domicilios"].append(nuevo_domicilio)
        
        # 4. Guardar en el archivo
        guardar_datos_web(datos)
        
        # 5. Calcular el total para mostrarlo
        total = valor_final + propina
        
        # 6. Mostrar mensaje de éxito detallado
        st.success(f"""
            ✅ ¡Domicilio registrado exitosamente!
            - Zona: {zona_seleccionada}
            - Dirección: {direccion_detalle}
            - Valor: ${valor_final:,}
            - Propina: ${propina:,}
            - **Total: ${total:,}**
        """)
        st.balloons()
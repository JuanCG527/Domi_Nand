# Importamos la librería que convierte Python en Web App
import streamlit as st
import json
from datetime import datetime

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
with st.form("registro_domicilio"):
    st.subheader("Registrar Nuevo Domicilio")
    
    # Campos del formulario
    direccion = st.text_input("📍 Dirección de entrega:")
    valor = st.number_input(" Valor del domicilio:", min_value=0, step=1000)
    propina = st.number_input("🎁 Propina:", min_value=0, step=500)
    
    # Botón de guardar
    boton_guardar = st.form_submit_button("Guardar Domicilio")

# LÓGICA DE PROCESAMIENTO (Se ejecuta SOLO si se presionó el botón)
if boton_guardar:
    if direccion == "":
        st.error("⚠️ La dirección no puede estar vacía.")
    else:
        # 1. Cargar datos existentes
        datos = cargar_datos_web()
        
        # 2. Crear el nuevo domicilio
        nuevo_domicilio = {
            "direccion": direccion,
            "valor": int(valor),
            "propina": int(propina),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # 3. Agregarlo a la lista
        datos["domicilios"].append(nuevo_domicilio)
        
        # 4. Guardar en el archivo
        guardar_datos_web(datos)
        
        # 5. Mostrar mensaje de éxito
        st.success(f"✅ ¡Domicilio en '{direccion}' registrado por ${valor + propina}!")
        st.balloons()
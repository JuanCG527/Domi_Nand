# =============================================================================
# BLOQUE 1: IMPORTACIONES Y CONFIGURACIÓN
# =============================================================================
import streamlit as st
import json
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Domicilios Villavicencio Pro",
    page_icon="🏍️",
    layout="wide"
)

# =============================================================================
# BLOQUE 2: CATÁLOGO DE ZONAS REALES DE VILLAVICENCIO
# =============================================================================
ZONAS_Y_TARIFAS = {
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

# Gastos frecuentes
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
    """Lee el JSON con estructura completa incluyendo clientes."""
    try:
        with open("datos_app.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            # Asegurar que existan todas las secciones
            if "clientes" not in datos:
                datos["clientes"] = []
            if "turnos" not in datos:
                datos["turnos"] = []
            return datos
    except (FileNotFoundError, json.JSONDecodeError):
        return {"domicilios": [], "gastos": [], "turnos": [], "clientes": []}


def guardar_datos_web(datos):
    """Escribe los datos en JSON."""
    with open("datos_app.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def filtrar_por_rango(lista, campo_fecha, inicio, fin):
    """Filtra registros por rango de fechas."""
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
    """Calcula ingresos, gastos y balance."""
    ingresos = sum(d["valor"] + d.get("propina", 0) for d in domicilios)
    gastos_total = sum(g["valor"] for g in gastos)
    balance = ingresos - gastos_total
    return ingresos, gastos_total, balance


def buscar_en_lista(lista, texto_busqueda, campos):
    """Busca texto en múltiples campos de una lista de diccionarios.
    Analogía: Es como Ctrl+F pero busca en varios campos a la vez."""
    if not texto_busqueda.strip():
        return lista
    
    texto = texto_busqueda.lower()
    resultado = []
    for item in lista:
        for campo in campos:
            valor = str(item.get(campo, "")).lower()
            if texto in valor:
                resultado.append(item)
                break  # Si encontró en un campo, no sigue buscando
    return resultado

# =============================================================================
# BLOQUE 4: INICIALIZACIÓN DE SESIÓN
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
st.title("🏍️ Domicilios Villavicencio Pro")
st.caption("📍 Punto base: Amarilo, Hacienda Rosablanca - Meta | CRM de Domicilios")

# Indicador de turno activo
if st.session_state.turno_activo:
    horas_activa = (datetime.now() - st.session_state.turno_inicio).total_seconds() / 3600
    st.success(f"⏱️ **TURNO ACTIVO** desde {st.session_state.turno_inicio.strftime('%H:%M')} ({horas_activa:.1f}h)")
else:
    st.info("🔴 No hay turno activo. Ve a '⏱️ Turno' para iniciar.")

st.markdown("---")

# =============================================================================
# BLOQUE 6: NAVEGACIÓN POR TABS
# =============================================================================
tab_dashboard, tab_domicilios, tab_clientes, tab_gastos, tab_historial, tab_analisis, tab_zonas, tab_turno = st.tabs([
    "📊 Dashboard",
    "📦 Domicilio",
    "📇 Clientes",
    "💸 Gasto",
    "🗂️ Historial",
    "📈 Análisis",
    "⚙️ Zonas",
    "⏱️ Turno"
])

# =============================================================================
# TAB 1: DASHBOARD
# =============================================================================
with tab_dashboard:
    st.subheader("📊 Panel de Control")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        periodo = st.selectbox(
            "Período:",
            options=["Hoy", "Ayer", "Últimos 7 días", "Este mes", "Personalizado"],
            index=0
        )
    
    hoy = datetime.now().date()
    
    if periodo == "Hoy":
        fecha_inicio = fecha_fin = hoy
    elif periodo == "Ayer":
        fecha_inicio = fecha_fin = hoy - timedelta(days=1)
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
    
    st.markdown(f"**📅 {inicio_str} al {fin_str}**")
    st.markdown("---")
    
    datos = cargar_datos_web()
    domicilios_filtrados = filtrar_por_rango(datos.get("domicilios", []), "fecha", inicio_str, fin_str)
    gastos_filtrados = filtrar_por_rango(datos.get("gastos", []), "fecha", inicio_str, fin_str)
    
    ingresos, gastos_total, balance = calcular_estadisticas(domicilios_filtrados, gastos_filtrados)
    promedio = ingresos / len(domicilios_filtrados) if domicilios_filtrados else 0
    
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
        st.metric("🎯 Promedio", f"${int(promedio):,}")
    
    st.markdown("---")
    if balance > 0:
        st.success(f"🟢 Ganancia: **${balance:,}**")
    elif balance < 0:
        st.error(f"🔴 Pérdida: **${abs(balance):,}**")
    else:
        st.info("⚪ Balance en cero")

# =============================================================================
# TAB 2: REGISTRAR DOMICILIO (Con Buscador Inteligente y Clientes)
# =============================================================================
with tab_domicilios:
    st.subheader("📦 Registrar Nuevo Domicilio")
    
    # MODO DE REGISTRO: Cliente existente o nuevo
    modo_registro = st.radio(
        "¿Cómo registrar?",
        options=["📇 Cliente frecuente", "🆕 Cliente nuevo"],
        horizontal=True
    )
    
    with st.form("registro_domicilio"):
        
        if modo_registro == "📇 Cliente frecuente":
            # BUSCADOR INTELIGENTE DE CLIENTES
            st.markdown("### 🔍 Buscar Cliente")
            
            datos = cargar_datos_web()
            lista_clientes = datos.get("clientes", [])
            
            if not lista_clientes:
                st.warning("No hay clientes guardados. Registra uno nuevo primero.")
                cliente_seleccionado = None
            else:
                # Campo de búsqueda con autocompletado
                busqueda_cliente = st.text_input(
                    "Escribe nombre, teléfono o dirección:",
                    placeholder="Ej: Juan, 310, Amarilo..."
                )
                
                # Filtrar clientes según búsqueda
                if busqueda_cliente.strip():
                    clientes_filtrados = buscar_en_lista(
                        lista_clientes, 
                        busqueda_cliente, 
                        ["nombre", "telefono", "direccion", "barrio"]
                    )
                else:
                    # Mostrar favoritos primero, luego todos
                    clientes_favoritos = [c for c in lista_clientes if c.get("favorito", False)]
                    clientes_normales = [c for c in lista_clientes if not c.get("favorito", False)]
                    clientes_filtrados = clientes_favoritos + clientes_normales
                
                # Mostrar resultados como botones seleccionables
                if clientes_filtrados:
                    st.caption(f"Se encontraron {len(clientes_filtrados)} cliente(s)")
                    
                    # Limitar a 10 resultados para no saturar
                    for cliente in clientes_filtrados[:10]:
                        col_c1, col_c2, col_c3 = st.columns([3, 1, 1])
                        with col_c1:
                            favorito = "⭐" if cliente.get("favorito") else "  "
                            st.write(f"{favorito} **{cliente['nombre']}** - {cliente.get('telefono', 'Sin tel.')}")
                            st.caption(f"📍 {cliente.get('direccion', '')} | {cliente.get('barrio', '')}")
                            st.caption(f"🔁 Visitas: {cliente.get('visitas', 0)}")
                        with col_c2:
                            if st.button(f"Seleccionar", key=f"sel_{cliente['nombre']}_{cliente.get('telefono', '')}"):
                                st.session_state.cliente_temp = cliente
                                st.rerun()
                        with col_c3:
                            pass
                    
                    # Si hay más de 10, mostrar mensaje
                    if len(clientes_filtrados) > 10:
                        st.info(f"Mostrando 10 de {len(clientes_filtrados)} resultados. Refina tu búsqueda.")
                else:
                    st.warning("No se encontraron clientes con ese texto.")
            
            # Si se seleccionó un cliente, mostrar sus datos
            if "cliente_temp" in st.session_state and st.session_state.cliente_temp:
                cliente = st.session_state.cliente_temp
                st.success(f"✅ Cliente seleccionado: {cliente['nombre']}")
                
                nombre_cliente = cliente["nombre"]
                telefono_cliente = cliente.get("telefono", "")
                direccion_detalle = cliente.get("direccion", "")
                barrio_seleccionado = cliente.get("barrio", "")
                anillo_seleccionado = cliente.get("anillo", list(ZONAS_Y_TARIFAS.keys())[0])
                
                # Actualizar dirección si es necesario
                direccion_detalle = st.text_input("🏠 Dirección (editable):", value=direccion_detalle)
                
            else:
                nombre_cliente = ""
                telefono_cliente = ""
                direccion_detalle = ""
                barrio_seleccionado = ""
                anillo_seleccionado = list(ZONAS_Y_TARIFAS.keys())[0]
        
        else:
            # REGISTRO DE CLIENTE NUEVO (Formulario tradicional)
            nombre_cliente = st.text_input("👤 Nombre del cliente:", placeholder="Ej: Juan Pérez")
            telefono_cliente = st.text_input("📱 Teléfono:", placeholder="Ej: 3101234567")
            
            # Selector de anillo y barrio
            anillo_seleccionado = st.selectbox(
                "🗺️ Anillo de distancia:",
                options=list(ZONAS_Y_TARIFAS.keys()),
                index=0
            )
            
            lista_barrios = list(ZONAS_Y_TARIFAS[anillo_seleccionado].keys())
            barrio_seleccionado = st.selectbox(
                "📍 Barrio específico:",
                options=lista_barrios,
                index=0
            )
            
            direccion_detalle = st.text_input(
                "🏠 Dirección específica:",
                placeholder="Ej: Calle 40 #15-20, Apt 302"
            )
        
        # Calcular valor
        valor_base = ZONAS_Y_TARIFAS.get(anillo_seleccionado, {}).get(barrio_seleccionado, 0)
        
        if "Personalizado" in barrio_seleccionado:
            valor_final = st.number_input("💵 Valor acordado:", min_value=0, step=500, value=0)
        else:
            st.info(f"💰 Tarifa para **{barrio_seleccionado}**: **${valor_base:,}**")
            valor_final = valor_base
        
        # Propina
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
        
        # Resumen
        total = valor_final + propina
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("💵 Valor", f"${valor_final:,}")
        with col_res2:
            st.metric("🎁 Propina", f"${propina:,}")
        with col_res3:
            st.metric("💰 TOTAL", f"${total:,}")
        
        # Checkbox para guardar como cliente frecuente
        guardar_cliente = st.checkbox("💾 Guardar este cliente para futuras entregas", value=True)
        marcar_favorito = st.checkbox("⭐ Marcar como favorito", value=False)
        
        boton_dom = st.form_submit_button("💾 Guardar Domicilio", use_container_width=True, type="primary")
    
    # Lógica de guardado
    if boton_dom:
        if not nombre_cliente.strip():
            st.error("⚠️ Ingresa el nombre del cliente.")
        elif direccion_detalle.strip() == "":
            st.error("⚠️ Ingresa la dirección.")
        elif valor_final == 0:
            st.error("⚠️ El valor no puede ser cero.")
        else:
            datos = cargar_datos_web()
            
            # Crear domicilio
            nuevo_dom = {
                "cliente": nombre_cliente,
                "telefono": telefono_cliente,
                "anillo": anillo_seleccionado,
                "barrio": barrio_seleccionado,
                "zona": anillo_seleccionado,
                "direccion": direccion_detalle,
                "valor": int(valor_final),
                "propina": int(propina),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            datos["domicilios"].append(nuevo_dom)
            
            # Actualizar o crear cliente frecuente
            if guardar_cliente:
                # Buscar si ya existe
                cliente_existente = None
                for c in datos.get("clientes", []):
                    if c.get("telefono") == telefono_cliente and telefono_cliente:
                        cliente_existente = c
                        break
                    elif c.get("nombre") == nombre_cliente and c.get("direccion") == direccion_detalle:
                        cliente_existente = c
                        break
                
                if cliente_existente:
                    # Actualizar visitas
                    cliente_existente["visitas"] = cliente_existente.get("visitas", 0) + 1
                    cliente_existente["ultima_visita"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    if marcar_favorito:
                        cliente_existente["favorito"] = True
                else:
                    # Crear nuevo cliente
                    nuevo_cliente = {
                        "nombre": nombre_cliente,
                        "telefono": telefono_cliente,
                        "direccion": direccion_detalle,
                        "barrio": barrio_seleccionado,
                        "anillo": anillo_seleccionado,
                        "visitas": 1,
                        "ultima_visita": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "favorito": marcar_favorito
                    }
                    datos["clientes"].append(nuevo_cliente)
            
            guardar_datos_web(datos)
            
            if st.session_state.turno_activo:
                st.session_state.turno_domicilios.append(nuevo_dom)
            
            st.success(f"✅ Domicilio registrado para {nombre_cliente} en {barrio_seleccionado}")
            st.balloons()
            
            # Limpiar sesión
            if "cliente_temp" in st.session_state:
                del st.session_state.cliente_temp

# =============================================================================
# TAB 3: GESTIÓN DE CLIENTES FRECUENTES
# =============================================================================
with tab_clientes:
    st.subheader("📇 Clientes Frecuentes")
    st.caption("Tus clientes guardados con historial de visitas")
    
    datos = cargar_datos_web()
    lista_clientes = datos.get("clientes", [])
    
    if not lista_clientes:
        st.info("📭 No hay clientes guardados aún. Registra un domicilio y marca 'Guardar cliente'.")
    else:
        # Filtros
        col_filt1, col_filt2 = st.columns(2)
        with col_filt1:
            mostrar = st.radio("Mostrar:", ["Todos", "⭐ Favoritos", "Más visitados"], horizontal=True)
        with col_filt2:
            busqueda = st.text_input("🔍 Buscar:", placeholder="Nombre, teléfono, barrio...")
        
        # Filtrar
        if busqueda.strip():
            lista_filtrada = buscar_en_lista(lista_clientes, busqueda, ["nombre", "telefono", "direccion", "barrio"])
        elif mostrar == "⭐ Favoritos":
            lista_filtrada = [c for c in lista_clientes if c.get("favorito", False)]
        elif mostrar == "Más visitados":
            lista_filtrada = sorted(lista_clientes, key=lambda x: x.get("visitas", 0), reverse=True)
        else:
            lista_filtrada = lista_clientes
        
        st.caption(f"Mostrando {len(lista_filtrada)} de {len(lista_clientes)} clientes")
        
        # Mostrar tarjetas de clientes
        for cliente in lista_filtrada:
            with st.expander(f"{'⭐' if cliente.get('favorito') else '👤'} {cliente['nombre']} - {cliente.get('telefono', 'Sin tel.')}"):
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.write(f"**📱 Teléfono:** {cliente.get('telefono', 'N/A')}")
                    st.write(f"**📍 Dirección:** {cliente.get('direccion', 'N/A')}")
                    st.write(f"**🗺️ Barrio:** {cliente.get('barrio', 'N/A')}")
                    st.write(f"**🔁 Visitas:** {cliente.get('visitas', 0)}")
                
                with col_info2:
                    st.write(f"**📅 Última visita:** {cliente.get('ultima_visita', 'N/A')}")
                    st.write(f"**⭐ Favorito:** {'Sí' if cliente.get('favorito') else 'No'}")
                
                # Botones de acción
                col_acc1, col_acc2 = st.columns(2)
                with col_acc1:
                    if st.button(f"{'Quitar ⭐' if cliente.get('favorito') else 'Poner ⭐'}", key=f"fav_{cliente['nombre']}"):
                        cliente["favorito"] = not cliente.get("favorito", False)
                        guardar_datos_web(datos)
                        st.rerun()
                with col_acc2:
                    if st.button("🗑️ Eliminar", key=f"del_{cliente['nombre']}"):
                        datos["clientes"].remove(cliente)
                        guardar_datos_web(datos)
                        st.rerun()

# =============================================================================
# TAB 4: REGISTRAR GASTO
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
# TAB 5: HISTORIAL
# =============================================================================
with tab_historial:
    st.subheader("🗂️ Historial Completo")
    
    col_fh1, col_fh2 = st.columns(2)
    with col_fh1:
        filtro_tipo = st.radio("Mostrar:", ["Domicilios", "Gastos", "Ambos"], horizontal=True)
    with col_fh2:
        filtro_busqueda = st.text_input("🔍 Buscar:", placeholder="Ej: Amarilo, Gasolina...")
    
    datos = cargar_datos_web()
    lista_dom = datos.get("domicilios", [])
    lista_gas = datos.get("gastos", [])
    
    if filtro_busqueda.strip():
        lista_dom = buscar_en_lista(lista_dom, filtro_busqueda, ["direccion", "barrio", "cliente", "telefono"])
        lista_gas = buscar_en_lista(lista_gas, filtro_busqueda, ["concepto"])
    
    sub_dom, sub_gas = st.tabs(["📦 Domicilios", "💸 Gastos"])
    
    with sub_dom:
        if filtro_tipo == "Gastos":
            st.info("Filtro: solo gastos")
        elif not lista_dom:
            st.info("📭 No hay domicilios.")
        else:
            st.caption(f"Total: {len(lista_dom)} registros")
            for i, dom in enumerate(reversed(lista_dom), 1):
                total = dom["valor"] + dom.get("propina", 0)
                with st.expander(f"📦 #{len(lista_dom) - i + 1} | {dom.get('cliente', 'N/A')} | ${total:,} | {dom.get('fecha', 'N/A')}"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        st.write(f"**Cliente:** {dom.get('cliente', 'N/A')}")
                        st.write(f"**Teléfono:** {dom.get('telefono', 'N/A')}")
                        st.write(f"**Dirección:** {dom['direccion']}")
                    with col_e2:
                        st.write(f"**Barrio:** {dom.get('barrio', 'N/A')}")
                        st.write(f"**Valor:** ${dom['valor']:,}")
                        st.write(f"**Propina:** ${dom.get('propina', 0):,}")
    
    with sub_gas:
        if filtro_tipo == "Domicilios":
            st.info("Filtro: solo domicilios")
        elif not lista_gas:
            st.info("📭 No hay gastos.")
        else:
            st.caption(f"Total: {len(lista_gas)} registros")
            for i, gas in enumerate(reversed(lista_gas), 1):
                with st.expander(f"💸 #{len(lista_gas) - i + 1} | {gas['concepto']} | ${gas['valor']:,} | {gas.get('fecha', 'N/A')}"):
                    st.write(f"**Concepto:** {gas['concepto']}")
                    st.write(f"**Valor:** ${gas['valor']:,}")

# =============================================================================
# TAB 6: ANÁLISIS CON CONTADOR DE VISITAS
# =============================================================================
with tab_analisis:
    st.subheader("📊 Análisis Detallado")
    
    datos = cargar_datos_web()
    lista_dom = datos.get("domicilios", [])
    lista_clientes = datos.get("clientes", [])
    
    col_an1, col_an2 = st.columns(2)
    
    with col_an1:
        st.markdown("### 📍 Lugares Más Visitados")
        if not lista_dom:
            st.info("Sin datos")
        else:
            # Contar visitas por dirección
            contador_lugares = {}
            for dom in lista_dom:
                key = f"{dom.get('direccion', 'N/A')} - {dom.get('barrio', 'N/A')}"
                if key not in contador_lugares:
                    contador_lugares[key] = {"visitas": 0, "ingresos": 0}
                contador_lugares[key]["visitas"] += 1
                contador_lugares[key]["ingresos"] += dom["valor"] + dom.get("propina", 0)
            
            # Ordenar por visitas
            lugares_ordenados = sorted(contador_lugares.items(), key=lambda x: x[1]["visitas"], reverse=True)
            
            # Mostrar top 10
            for lugar, stats in lugares_ordenados[:10]:
                st.write(f"**{lugar}**")
                st.caption(f"🔁 {stats['visitas']} visitas | 💰 ${stats['ingresos']:,}")
    
    with col_an2:
        st.markdown("### 📈 Ingresos por Anillo")
        if not lista_dom:
            st.info("Sin datos")
        else:
            for anillo in ZONAS_Y_TARIFAS.keys():
                domicilios_anillo = [d for d in lista_dom if d.get("anillo") == anillo]
                if domicilios_anillo:
                    ingresos_anillo = sum(d["valor"] + d.get("propina", 0) for d in domicilios_anillo)
                    st.write(f"**{anillo}**")
                    st.caption(f"{len(domicilios_anillo)} domicilios | ${ingresos_anillo:,}")
    
    # Análisis de clientes frecuentes
    st.markdown("---")
    st.markdown("### 📇 Top 10 Clientes Frecuentes")
    
    if not lista_clientes:
        st.info("No hay clientes guardados")
    else:
        clientes_ordenados = sorted(lista_clientes, key=lambda x: x.get("visitas", 0), reverse=True)
        
        for i, cliente in enumerate(clientes_ordenados[:10], 1):
            col_cli1, col_cli2, col_cli3 = st.columns([3, 1, 1])
            with col_cli1:
                st.write(f"**{i}. {cliente['nombre']}** {'⭐' if cliente.get('favorito') else ''}")
                st.caption(f"📱 {cliente.get('telefono', 'N/A')} | 📍 {cliente.get('direccion', 'N/A')}")
            with col_cli2:
                st.metric("Visitas", cliente.get("visitas", 0))
            with col_cli3:
                st.caption(f"Última: {cliente.get('ultima_visita', 'N/A')}")

# =============================================================================
# TAB 7: GESTIÓN DE ZONAS (Agregar/Editar/Eliminar)
# =============================================================================
with tab_zonas:
    st.subheader("⚙️ Gestión de Zonas y Barrios")
    st.caption("Personaliza tu mapa de trabajo")
    
    # Mostrar zonas actuales
    st.markdown("### 🗺️ Zonas Actuales")
    
    for anillo, barrios in ZONAS_Y_TARIFAS.items():
        with st.expander(f"{anillo} ({len(barrios)} barrios)"):
            for barrio, tarifa in barrios.items():
                col_z1, col_z2, col_z3 = st.columns([3, 1, 1])
                with col_z1:
                    st.write(f"**{barrio}**")
                with col_z2:
                    st.write(f"${tarifa:,}")
                with col_z3:
                    pass
    
    # Agregar nueva zona/barrio
    st.markdown("---")
    st.markdown("### ➕ Agregar Nuevo Barrio")
    
    with st.form("agregar_barrio"):
        anillo_nuevo = st.selectbox("Anillo:", options=list(ZONAS_Y_TARIFAS.keys()))
        barrio_nuevo = st.text_input("Nombre del barrio:", placeholder="Ej: Mi Barrio Nuevo (C3)")
        tarifa_nueva = st.number_input("Tarifa:", min_value=0, step=500, value=5000)
        
        boton_agregar = st.form_submit_button("➕ Agregar Barrio", use_container_width=True)
    
    if boton_agregar:
        if barrio_nuevo.strip():
            ZONAS_Y_TARIFAS[anillo_nuevo][barrio_nuevo] = int(tarifa_nueva)
            st.success(f"✅ {barrio_nuevo} agregado a {anillo_nuevo} con tarifa ${tarifa_nueva:,}")
        else:
            st.error("⚠️ Ingresa el nombre del barrio")

# =============================================================================
# TAB 8: MODO TURNO
# =============================================================================
with tab_turno:
    st.subheader("⏱️ Control de Turno")
    
    if not st.session_state.turno_activo:
        st.warning("🔴 No hay turno activo.")
        
        if st.button("▶️ INICIAR TURNO", use_container_width=True, type="primary"):
            st.session_state.turno_activo = True
            st.session_state.turno_inicio = datetime.now()
            st.session_state.turno_domicilios = []
            st.session_state.turno_gastos = []
            st.rerun()
    else:
        tiempo_transcurrido = datetime.now() - st.session_state.turno_inicio
        horas = int(tiempo_transcurrido.total_seconds() // 3600)
        minutos = int((tiempo_transcurrido.total_seconds() % 3600) // 60)
        
        st.success(f"🟢 **Turno activo** desde {st.session_state.turno_inicio.strftime('%H:%M:%S')}")
        st.metric("⏱️ Tiempo", f"{horas}h {minutos}m")
        
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
        
        if st.button("⏹️ CERRAR TURNO", use_container_width=True, type="primary"):
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
                st.write(f"**⏱️ Duración:** {registro_turno['duracion_minutos']} min")
            with col_r2:
                st.write(f"**📦 Domicilios:** {registro_turno['domicilios']}")
                st.write(f"**💰 Ingresos:** ${registro_turno['ingresos']:,}")
                st.write(f"**💸 Gastos:** ${registro_turno['gastos']:,}")
            
            st.markdown("---")
            if bal_turno > 0:
                st.success(f"### 🟢 GANANCIA: ${bal_turno:,}")
            else:
                st.error(f"### 🔴 PÉRDIDA: ${abs(bal_turno):,}")
            
            st.balloons()
            
            st.session_state.turno_activo = False
            st.session_state.turno_inicio = None
            st.session_state.turno_domicilios = []
            st.session_state.turno_gastos = []
            
            st.info("✅ Turno cerrado")

# =============================================================================
# PIE DE PÁGINA
# =============================================================================
st.markdown("---")
st.caption(f"🏍️ Domicilios Villavicencio Pro v6.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
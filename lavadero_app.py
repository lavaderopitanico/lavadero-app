import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuración de base de datos con campos de "Ficha"
conn = sqlite3.connect('lavadero_profesional.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS fichas 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              fecha TEXT,
              propietario TEXT, 
              telefono TEXT,
              email TEXT,
              matricula TEXT, 
              marca_modelo TEXT,
              color TEXT,
              tipo_trabajo TEXT, 
              precio REAL, 
              estado_pago TEXT,
              observaciones TEXT)''')
conn.commit()

st.set_page_config(page_title="Lavadero Pro - Fichas", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .css-1r6slb0 { background-color: #f0f2f6; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📑 Gestión de Fichas de Vehículos")

# --- MENÚ SUPERIOR ---
col1, col2, col3 = st.columns(3)
with col1:
    btn_nueva = st.button("➕ NUEVA FICHA / ENTRADA")
with col2:
    btn_ver = st.button("🔍 VER HISTORIAL / BUSCAR")
with col3:
    btn_caja = st.button("💰 CIERRE DE CAJA")

# Control de navegación
if btn_nueva: st.session_state.seccion = "nueva"
if btn_ver: st.session_state.seccion = "ver"
if btn_caja: st.session_state.seccion = "caja"

seccion = st.session_state.get("seccion", "nueva")

# --- SECCIÓN: NUEVA FICHA (RELLENAR DATOS) ---
if seccion == "nueva":
    st.subheader("📝 Rellenar Ficha de Entrada")
    with st.form("ficha_detallada", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("### 👤 Datos del Propietario")
            nombre = st.text_input("Nombre Completo")
            tel = st.text_input("Teléfono de Contacto")
            correo = st.text_input("Email")
            
        with col_b:
            st.markdown("### 🚗 Datos del Vehículo")
            mat = st.text_input("Matrícula")
            modelo = st.text_input("Marca y Modelo (ej: Seat Ibiza)")
            color = st.text_input("Color del vehículo")

        st.markdown("---")
        st.markdown("### 🛠️ Detalles del Servicio")
        c1, c2, c3 = st.columns(3)
        trabajo = c1.selectbox("Servicio", ["Lavado Exterior", "Lavado Completo", "Tapicería", "Motor", "Pulido", "Cerámico"])
        precio = c2.number_input("Precio Pactado (€)", min_value=0.0)
        pago = c3.selectbox("Estado inicial", ["Pendiente", "Pagado"])
        
        notas = st.text_area("Observaciones (Daños previos, objetos olvidados, etc.)")
        
        if st.form_submit_button("💾 GUARDAR FICHA Y GENERAR ENTRADA"):
            fecha_act = datetime.now().strftime("%d/%m/%Y %H:%M")
            c.execute('''INSERT INTO fichas (fecha, propietario, telefono, email, matricula, marca_modelo, color, tipo_trabajo, precio, estado_pago, observaciones) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                      (fecha_act, nombre, tel, correo, mat, modelo, color, trabajo, precio, pago, notas))
            conn.commit()
            st.success(f"Ficha de {mat} guardada correctamente.")

# --- SECCIÓN: VER HISTORIAL ---
elif seccion == "ver":
    st.subheader("🔍 Buscador de Fichas")
    busqueda = st.text_input("Buscar por Matrícula o Nombre")
    df = pd.read_sql_query("SELECT * FROM fichas", conn)
    
    if busqueda:
        df = df[df['matricula'].str.contains(busqueda, case=False) | df['propietario'].str.contains(busqueda, case=False)]
    
    st.dataframe(df, use_container_width=True)

# --- SECCIÓN: CAJA ---
elif seccion == "caja":
    st.subheader("💰 Resumen de Caja")
    df_caja = pd.read_sql_query("SELECT * FROM fichas WHERE estado_pago = 'Pagado'", conn)
    total = df_caja['precio'].sum()
    st.metric("Total Recaudado en Fichas Pagadas", f"{total} €")
    st.table(df_caja[['fecha', 'matricula', 'tipo_trabajo', 'precio']])
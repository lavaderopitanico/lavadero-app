import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import urllib.parse

# Conexión a base de datos
conn = sqlite3.connect('lavadero_mecanica.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS servicios 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, propietario TEXT, 
              telefono TEXT, matricula TEXT, marca_modelo TEXT, trabajo TEXT, 
              precio REAL, estado TEXT, tipo TEXT, observaciones TEXT)''')
conn.commit()

st.set_page_config(page_title="Lavadero & Mecánica Pro", layout="wide")

# --- NAVEGACIÓN ---
menu = st.sidebar.selectbox("Menú Principal", ["📅 Agenda de Citas", "🛠️ Taller y Lavadero (Hoy)", "📊 Historial y Caja"])

# --- SECCIÓN 1: AGENDA DE CITAS ---
if menu == "📅 Agenda de Citas":
    st.title("📅 Reserva de Citas")
    
    with st.expander("➕ Registrar Nueva Cita"):
        with st.form("nueva_cita"):
            col1, col2 = st.columns(2)
            f_cita = col1.date_input("Fecha")
            h_cita = col2.time_input("Hora")
            cliente = col1.text_input("Nombre del Cliente")
            tel = col1.text_input("WhatsApp (ej: 34600000000)")
            mat = col2.text_input("Matrícula")
            obs = st.text_area("Notas / Pedido especial")
            
            if st.form_submit_button("Reservar Cita"):
                fecha_full = f"{f_cita} {h_cita}"
                c.execute("INSERT INTO servicios (fecha, propietario, telefono, matricula, estado, tipo, observaciones) VALUES (?,?,?,?,?,?,?)",
                          (fecha_full, cliente, tel, mat, "Pendiente", "CITA", obs))
                conn.commit()
                st.success("Cita reservada")

    st.subheader("Próximas Citas")
    df_citas = pd.read_sql_query("SELECT * FROM servicios WHERE tipo='CITA' ORDER BY fecha ASC", conn)
    
    for i, r in df_citas.iterrows():
        col_c, col_b = st.columns([0.7, 0.3])
        col_c.write(f"📌 *{r['fecha']}* | {r['matricula']} - {r['propietario']}")
        
        # BOTÓN WHATSAPP RECORDATORIO
        msg = urllib.parse.quote(f"Hola {r['propietario']}, te recordamos tu cita para el día {r['fecha']} en nuestro centro. ¡Te esperamos!")
        col_b.markdown(f"[🔔 Avisar por WhatsApp](https://wa.me/{r['telefono']}?text={msg})")
        
        if col_b.button(f"Comenzar Trabajo - ID {r['id']}"):
            c.execute("UPDATE servicios SET tipo='TRABAJO' WHERE id=?", (r['id'],))
            conn.commit()
            st.rerun()

# --- SECCIÓN 2: TALLER Y LAVADERO ---
elif menu == "🛠️ Taller y Lavadero (Hoy)":
    st.title("🛠️ Servicios en Curso")
    
    with st.sidebar:
        st.header("Entrada Directa")
        with st.form("entrada_directa"):
            nombre = st.text_input("Cliente")
            matricula = st.text_input("Matrícula")
            tel = st.text_input("Teléfono")
            
            # LISTA DE SERVICIOS PEDIDOS
            trabajo = st.multiselect("Servicios a realizar", [
                "Lavado Básico", "Lavado Motor y Bajos", "Engrases", 
                "Cambio de Aceite", "Filtro de Aire", "Filtro de Gasoil", 
                "Filtro Aceite", "Filtro de Polen"
            ])
            
            precio = st.number_input("Precio Total (€)", min_value=0.0)
            if st.form_submit_button("Registrar Entrada"):
                c.execute("INSERT INTO servicios (fecha, propietario, telefono, matricula, trabajo, precio, estado, tipo) VALUES (?,?,?,?,?,?,?,?)",
                          (datetime.now().strftime("%Y-%m-%d %H:%M"), nombre, tel, matricula, ", ".join(trabajo), precio, "En Proceso", "TRABAJO"))
                conn.commit()
                st.rerun()

    df_h = pd.read_sql_query("SELECT * FROM servicios WHERE tipo='TRABAJO' AND estado='En Proceso'", conn)
    st.table(df_h[['fecha', 'matricula', 'propietario', 'trabajo', 'precio']])
    
    for i, r in df_h.iterrows():
        if st.button(f"✅ Finalizar y Cobrar: {r['matricula']}"):
            c.execute("UPDATE servicios SET estado='Pagado' WHERE id=?", (r['id'],))
            conn.commit()
            st.rerun()

# --- SECCIÓN 3: CAJA ---
elif menu == "📊 Historial y Caja":
    st.title("💰 Historial de Ventas")
    df_p = pd.read_sql_query("SELECT * FROM servicios WHERE estado='Pagado'", conn)
    st.dataframe(df_p)
    st.metric("Total Caja", f"{df_p['precio'].sum()} €")

import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configurar acceso a Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Leer credenciales desde el archivo de configuración
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPE
)
gc = gspread.authorize(credentials)
sheet = gc.open_by_url(st.secrets["sheet_url"])
worksheet = sheet.sheet1

@st.cache_data
def cargar_datos():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def registrar_glucosa(nivel, comentario):
    now = datetime.now()
    fila = [now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), nivel, comentario]
    worksheet.append_row(fila)

# INTERFAZ
st.title("Monitoreo de Glucosa - AnaLilia")

st.subheader("📥 Registrar nuevo nivel de glucosa")

nivel = st.number_input("Nivel de glucosa (mg/dL)", min_value=20, max_value=600)
comentario = st.text_input("Comentario (opcional)")

if st.button("Guardar"):
    registrar_glucosa(nivel, comentario)
    st.success("✅ Registro guardado correctamente")

st.subheader("📊 Historial de registros")

df = cargar_datos()

if df.empty:
    st.info("Aún no hay registros.")
else:
    st.dataframe(df)

    df["FechaHora"] = pd.to_datetime(df["Fecha"] + " " + df["Hora"])
    st.line_chart(df.set_index("FechaHora")["Nivel"])

    ultimo = df.iloc[-1]["Nivel"]
    promedio = df["Nivel"].tail(7).mean()

    st.metric("Último nivel", f"{ultimo} mg/dL")
    st.metric("Promedio últimos registros", f"{promedio:.1f} mg/dL")

    if ultimo < 70 or ultimo > 180:
        st.error("⚠️ Nivel fuera del rango saludable.")

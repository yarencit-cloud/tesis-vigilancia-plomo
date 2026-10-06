import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS DE INGENIERÍA BIOMÉDICA
# ==============================================================================
st.set_page_config(
    page_title="Vigilancia Infantil - Exposición a Plomo",
    page_icon="🩸",
    layout="wide"
)

# Estilos visuales para tarjetas de información y recomendaciones
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MÓDULO 2: BASE DE DATOS (SQLite Local)
# ==============================================================================
def conectar_bd():
    conn = sqlite3.connect("vigilancia_plomo.db")
    return conn

def inicializar_bd():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            codigo_paciente TEXT UNIQUE,
            edad INTEGER,
            bll REAL,
            hb REAL,
            residencia INTEGER,
            cercania INTEGER,
            antecedentes INTEGER,
            irn_porcentaje REAL,
            nivel_riesgo TEXT
        )
    ''')
    conn.commit()
    conn.close()

inicializar_bd()

# ==============================================================================
# MÓDULO 3 Y 4: PROCESAMIENTO Y CLASIFICACIÓN (Ecuación Ponderada IRN)
# ==============================================================================
def calcular_riesgo_ponderado(edad, bll, hb, residencia, cercania, antecedentes):
    """
    Ecuación de la Matriz Ponderada del Índice de Riesgo Neurocognitivo (IRN %)
    Pesos (w_i):
      - BLL: 30% (0.30)
      - Hemoglobina: 20% (0.20)
      - Tiempo de residencia: 15% (0.15)
      - Cercanía a fuente: 15% (0.15)
      - Antecedentes ambientales: 10% (0.10)
      - Edad (<=5 años): 10% (0.10)
    """
    # Escalamiento de sub-puntajes
    s_bll = 0 if bll < 3.5 else (1 if bll < 5.0 else (2 if bll < 10.0 else 3))
    s_edad = 1 if edad <= 5 else 0
    s_hb = 0 if hb >= 12.0 else (1 if hb >= 11.0 else 2)
    s_res = 1 if residencia >= 3 else 0
    s_cerc = 1 if cercania else 0
    s_antec = 1 if antecedentes else 0

    # Ecuación Ponderada (%)
    irn = (
        (s_bll / 3.0) * 0.30 +
        (s_hb / 2.0) * 0.20 +
        (s_res / 1.0) * 0.15 +
        (s_cerc / 1.0) * 0.15 +
        (s_antec / 1.0) * 0.10 +
        (s_edad / 1.0) * 0.10
    ) * 100

    # Clasificación por Rangos Porcentuales
    if irn < 35.0:
        clasificacion = "Riesgo Bajo"
        color = "green"
    elif irn < 65.0:
        clasificacion = "Riesgo Moderado"
        color = "orange"
    else:
        clasificacion = "Riesgo Alto"
        color = "red"

    return round(irn, 2), clasificacion, color

# ==============================================================================
# INTERFAZ WEB PRINCIPAL
# ==============================================================================
st.title("🛡️ Plataforma Digital de Vigilancia Comunitaria")
st.caption("Clasificación del Riesgo Cognitivo Asociado a Exposición a Plomo en Población Infantil — Torreón, Coahuila")
st.write("---")

# Menú lateral para navegación por módulos
menu = st.sidebar.radio(
    "Navegación / Módulos:",
    ["1. Captura y Evaluación de Casos", "2. Base de Datos Comunitarios", "3. Dashboard y Estadísticas"]
)

# ------------------------------------------------------------------------------
# MÓDULO 1: CAPTURA DE DATOS Y EVALUACIÓN
# ------------------------------------------------------------------------------
if menu == "1. Captura y Evaluación de Casos":
    st.subheader("📋 Módulo 1: Captura de Variables Clínicas y Epidemiológicas")
    st.info("Ingresa la información correspondiente al expediente del menor para calcular su clasificación preliminar de riesgo.")

    with st.form("formulario_captura", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 👤 Datos Demográficos y Clínicos")
            codigo = st.text_input("Código o Identificador Anónimo del Paciente:", placeholder="Ej. INF-2026-001")
            edad = st.number_input("Edad del Menor (Años):", min_value=1, max_value=17, value=5, help="La edad <= 5 años se considera de mayor vulnerabilidad neurológica.")
            bll = st.number_input("Nivel de Plomo en Sangre (BLL en µg/dL):", min_value=0.0, max_value=80.0, value=3.2, step=0.1, help="Valor de referencia epidemiológico del CDC: 3.5 µg/dL.")
            hb = st.number_input("Hemoglobina (Hb en g/dL):", min_value=3.0, max_value=20.0, value=12.5, step=0.1, help="Valores < 12.0 g/dL sugieren posible anemia o deficiencia de hierro.")

        with col2:
            st.markdown("##### 🏡 Factores Ambientales y de Residencia")
            residencia = st.number_input("Tiempo de Residencia en Zona de Riesgo (Años):", min_value=0, max_value=17, value=2)
            cercania = st.selectbox("¿Vive cerca de Fuentes Contaminantes / Zonas Industriales?", [False, True], format_func=lambda x: "Sí" if x else "No")
            antecedentes = st.selectbox("¿Tiene antecedentes de contacto con Polvo/Suelo o Cerámica Vidriada?", [False, True], format_func=lambda x: "Sí" if x else "No")

        bot_evaluar = st.form_submit_button("🧪 Procesar y Guardar Registro", use_container_width=True)

    if bot_evaluar:
        # Módulo de Validación de Entradas (Validación de campos, pág. 40)
        if not codigo.strip():
            st.error("⚠️ Error de Validación: Debe ingresar un Código o Identificador Anónimo válido.")
        else:
            # Procesamiento de la Ecuación Ponderada
            irn, riesgo, color = calcular_riesgo_ponderado(edad, bll, hb, residencia, cercania, antecedentes)

            # Guardado en SQLite
            try:
                conn = conectar_bd()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO registros (codigo_paciente, edad, bll, hb, residencia, cercania, antecedentes, irn_porcentaje, nivel_riesgo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (codigo, edad, bll, hb, residencia, int(cercania), int(antecedentes), irn, riesgo))
                conn.commit()
                conn.close()
                st.success(f"✅ Registro '{codigo}' guardado exitosamente en la Base de Datos Local.")
            except sqlite3.IntegrityError:
                st.warning(f"⚠️ El código '{codigo}' ya existe en la base de datos. Se muestra el cálculo del riesgo actual:")

            # MÓDULO 5: VISUALIZACIÓN DE RESULTADOS
            st.write("---")
            st.subheader("📊 Módulo 5: Resultado de la Clasificación Preliminar")
            
            res_col1, res_col2 = st.columns([1, 2])
            
            with res_col1:
                st.metric(label="Índice Ponderado de Riesgo (IRN)", value=f"{irn}%")
            
            with res_col2:
                if color == "green":
                    st.success(f"### Categoria: **{riesgo.upper()}**\n\n**Recomendación:** Mantener vigilancia rutinaria y promover hábitos de higiene comunitarios.")
                elif color == "orange":
                    st.warning(f"### Categoria: **{riesgo.upper()}**\n\n**Recomendación:** Se sugiere seguimiento comunitario, evaluación nutricional (hierro) y revaluación de BLL en 3-6 meses.")
                else:
                    st.error(f"### Categoria: **{riesgo.upper()}**\n\n**Recomendación:** Prioridad Alta. Canalización a valoración médica e intervención en la fuente de exposición ambiental.")

# ------------------------------------------------------------------------------
# MÓDULO 2: BASE DE DATOS Y REGISTROS
# ------------------------------------------------------------------------------
elif menu == "2. Base de Datos Comunitarios":
    st.subheader("🗄️ Módulo 2: Almacenamiento y Consulta de Expedientes")
    conn = conectar_bd()
    df = pd.read_sql_query("SELECT id, fecha, codigo_paciente, edad, bll, hb, residencia, cercania, antecedentes, irn_porcentaje, nivel_riesgo FROM registros ORDER BY id DESC", conn)
    conn.close()

    if df.empty:
        st.info("Aún no hay expedientes registrados en la base de datos.")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Descargar Base de Datos (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name="expedientes_vigilancia_plomo.csv", mime="text/csv")

# ------------------------------------------------------------------------------
# MÓDULO 3 Y 5: DASHBOARD Y ESTADÍSTICAS
# ------------------------------------------------------------------------------
elif menu == "3. Dashboard y Estadísticas":
    st.subheader("📈 Módulo 5: Visualización Epidemiológica y Resumen Comunitario")
    conn = conectar_bd()
    df = pd.read_sql_query("SELECT * FROM registros", conn)
    conn.close()

    if df.empty:
        st.info("Registre casos en el Módulo 1 para poder visualizar las estadísticas comunitarias.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Pacientes Evaluados", len(df))
        col2.metric("Promedio de BLL (µg/dL)", round(df['bll'].mean(), 2))
        col3.metric("Casos en Riesgo Alto", len(df[df['nivel_riesgo'] == 'Riesgo Alto']))

        st.write("---")
        
        # Gráfica de pastel de distribución del riesgo
        fig, ax = plt.subplots(figsize=(6, 3))
        conteo_riesgos = df['nivel_riesgo'].value_counts()
        colores = {'Riesgo Bajo': '#28a745', 'Riesgo Moderado': '#ffc107', 'Riesgo Alto': '#dc3545'}
        col_list = [colores.get(x, '#6c757d') for x in conteo_riesgos.index]
        
        ax.pie(conteo_riesgos, labels=conteo_riesgos.index, autopct='%1.1f%%', colors=col_list, startangle=140)
        ax.set_title("Distribución Poblacional según Nivel de Riesgo Neurocognitivo")
        
        st.pyplot(fig)
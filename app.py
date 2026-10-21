import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS DE INGENIERÍA BIOMÉDICA
# ==============================================================================
st.set_page_config(
    page_title="Sistema de Vigilancia de Exposición Infantil a Plomo",
    page_icon="🧪",
    layout="wide"
)

# ==============================================================================
# BASE DE DATOS LOCAL (SQLite) CON MIGRACIÓN AUTOMÁTICA
# ==============================================================================
def conectar_bd():
    return sqlite3.connect("vigilancia_plomo.db")

def inicializar_bd():
    conn = conectar_bd()
    cursor = conn.cursor()
    
    # 1. Crear tabla base si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            codigo_paciente TEXT UNIQUE,
            edad INTEGER,
            bll REAL,
            hb_medida REAL,
            hb_ajustada REAL,
            residencia INTEGER,
            cercania INTEGER,
            antecedentes INTEGER,
            indice_r_porcentaje REAL,
            nivel_riesgo TEXT
        )
    ''')
    
    # 2. Migración automática: Agregar columnas faltantes si la tabla es antigua
    cursor.execute("PRAGMA table_info(registros)")
    columnas_existentes = [columna[1] for columna in cursor.fetchall()]
    
    if "altitud_evaluacion" not in columnas_existentes:
        cursor.execute("ALTER TABLE registros ADD COLUMN altitud_evaluacion INTEGER DEFAULT 1120")
    if "es_torreon" not in columnas_existentes:
        cursor.execute("ALTER TABLE registros ADD COLUMN es_torreon INTEGER DEFAULT 1")
        
    conn.commit()
    conn.close()

inicializar_bd()

# ==============================================================================
# ALGORITMO PONDERADO Y CÁLCULO DE ALTITUD
# ==============================================================================
def calcular_ajuste_altitud(es_torreon, altitud_ingresada):
    """
    Cálculo de la corrección de hemoglobina según altitud geográfica (msnm).
    Torreón (~1,120 msnm) representa un ajuste de -0.2 g/dL.
    Fórmula estándar OMS para altitudes >= 1,000 msnm.
    """
    if es_torreon:
        return 0.2, 1120
    else:
        altitud = float(altitud_ingresada)
        if altitud < 1000:
            return 0.0, int(altitud)
        else:
            delta_hb = round(0.2 * (altitud / 1000.0), 2)
            return delta_hb, int(altitud)

def calcular_riesgo_ponderado_oficial(edad, bll, hb_medida, residencia, cercania, antecedentes, es_torreon, altitud_custom):
    """
    Algoritmo de ponderación normalizada (R = \sum W_i * S_i)
    Pesos Relativos (W_i):
      - W_BLL = 0.30 (30%)
      - W_Hb = 0.20 (20%)
      - W_edad = 0.15 (15%)
      - W_cerc = 0.15 (15%)
      - W_res = 0.10 (10%)
      - W_antec = 0.10 (10%)
    """
    # 1. Corrección por Altitud
    delta_hb, altitud_eval = calcular_ajuste_altitud(es_torreon, altitud_custom)
    hb_ajustada = hb_medida - delta_hb

    # 2. Asignación de Sub-puntajes y Normalización (S_i = P_i / P_max)
    # Variable 1: BLL (P_max = 3)
    if bll < 3.5:
        p_bll = 0
    elif bll < 5.0:
        p_bll = 1
    elif bll < 10.0:
        p_bll = 2
    else:
        p_bll = 3
    s_bll = p_bll / 3.0

    # Variable 2: Hemoglobina Ajustada (P_max = 2)
    if hb_ajustada >= 12.0:
        p_hb = 0
    elif hb_ajustada >= 11.0:
        p_hb = 1
    else:
        p_hb = 2
    s_hb = p_hb / 2.0

    # Variable 3: Edad (P_max = 1)
    s_edad = 1.0 if edad <= 5 else 0.0

    # Variable 4: Cercanía a fuente (P_max = 1)
    s_cerc = 1.0 if cercania else 0.0

    # Variable 5: Tiempo de residencia (P_max = 1)
    s_res = 1.0 if residencia >= 3 else 0.0

    # Variable 6: Antecedentes ambientales (P_max = 1)
    s_antec = 1.0 if antecedentes else 0.0

    # 3. Cálculo del Índice R Ponderado
    r_escalar = (
        0.30 * s_bll +
        0.20 * s_hb +
        0.15 * s_edad +
        0.15 * s_cerc +
        0.10 * s_res +
        0.10 * s_antec
    )
    
    r_porcentaje = round(r_escalar * 100.0, 1)

    # 4. Clasificación Criterial
    if r_porcentaje < 35.0:
        clasificacion = "Riesgo Bajo"
        color = "green"
    elif r_porcentaje < 65.0:
        clasificacion = "Riesgo Moderado"
        color = "orange"
    else:
        clasificacion = "Riesgo Alto"
        color = "red"

    return r_porcentaje, clasificacion, color, hb_ajustada, delta_hb, altitud_eval

# ==============================================================================
# INTERFAZ WEB PRINCIPAL
# ==============================================================================
st.title("Sistema de Vigilancia Comunitaria e Índice de Riesgo Neurocognitivo")
st.caption("Plataforma Digital de Evaluación Preliminar de Exposición Infantil a Plomo — Facultad de Ingeniería Mecánica y Eléctrica")
st.write("---")

menu = st.sidebar.radio(
    "Navegación / Módulos:",
    ["1. Captura y Evaluación Individual", "2. Base de Datos y Carga Epidemiológica", "3. Dashboard y Asociación Neurocognitiva"]
)

# ------------------------------------------------------------------------------
# MÓDULO 1: CAPTURA Y VALIDACIÓN DE DATOS
# ------------------------------------------------------------------------------
if menu == "1. Captura y Evaluación Individual":
    st.subheader("Módulo 1: Captura de Variables Clínicas y Epidemiológicas")
    st.info("Ingrese la información correspondiente al expediente del paciente para procesar la clasificación preliminar.")

    # Selección geográfica fuera del form para refresco dinámico instantáneo
    st.markdown("##### Ubicación Geográfica de la Evaluación")
    es_torreon = st.radio("¿El sitio de evaluación se ubica en Torreón, Coahuila (~1,120 msnm)?", ["Sí", "No"], key="radio_geo") == "Sí"
    
    if not es_torreon:
        altitud_custom = st.number_input("Ingrese la altitud geográfica del sitio de evaluación (msnm):", min_value=0, max_value=5000, value=1000, key="num_altitud")
    else:
        altitud_custom = 1120

    st.write("---")

    with st.form("form_captura", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Factores Clínicos y Demográficos")
            codigo = st.text_input("Código de Expediente (Anónimo):", placeholder="Ej. INF-2026-001")
            edad = st.number_input("Edad del Menor (Años):", min_value=1, max_value=17, value=4)
            bll = st.number_input("Nivel de Plomo en Sangre (BLL en µg/dL):", min_value=0.0, max_value=80.0, value=3.2, step=0.1)
            hb_medida = st.number_input("Hemoglobina de Laboratorio (g/dL):", min_value=3.0, max_value=20.0, value=12.2, step=0.1)

        with col2:
            st.markdown("##### Factores Ambientales y de Exposición")
            residencia = st.number_input("Tiempo de Residencia en Zona de Riesgo (Años):", min_value=0, max_value=17, value=2)
            cercania = st.selectbox("¿Reside a menos de 1 km de una Fuente Contaminante?", [False, True], format_func=lambda x: "Sí" if x else "No")
            antecedentes = st.selectbox("¿Antecedente de Loza Vidriada, Polvo o Trabajo Parental?", [False, True], format_func=lambda x: "Sí" if x else "No")

        bot_evaluar = st.form_submit_button("🧪 Procesar y Guardar Caso", use_container_width=True)

    if bot_evaluar:
        # Validación de Campos Obligatorios y Coherencia Biológica
        if not codigo.strip():
            st.error("Error de Validación: Debe ingresar un Código de Expediente válido.")
        elif residencia > edad:
            st.error(f"Error de Coherencia Biológica: El tiempo de residencia ({residencia} años) no puede ser mayor que la edad del niño ({edad} años).")
        else:
            # Procesamiento Matemático del Algoritmo
            r_porc, riesgo, color, hb_ajustada, delta_hb, altitud_eval = calcular_riesgo_ponderado_oficial(
                edad, bll, hb_medida, residencia, cercania, antecedentes, es_torreon, altitud_custom
            )

            # Persistencia en Base de Datos SQLite
            try:
                conn = conectar_bd()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO registros 
                    (codigo_paciente, edad, bll, hb_medida, hb_ajustada, altitud_evaluacion, es_torreon, residencia, cercania, antecedentes, indice_r_porcentaje, nivel_riesgo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (codigo, edad, bll, hb_medida, hb_ajustada, altitud_eval, int(es_torreon), residencia, int(cercania), int(antecedentes), r_porc, riesgo))
                conn.commit()
                conn.close()
                st.success(f"Registro '{codigo}' guardado correctamente en la Base de Datos.")
            except sqlite3.IntegrityError:
                st.warning(f"CUIDADO: El código '{codigo}' ya existe en la base de datos. Se muestra la evaluación del expediente actual:")

            # Módulo de Visualización de Resultados
            st.write("---")
            st.subheader("Resultado de la Clasificación de Riesgo Ponderado")
            
            res_col1, res_col2 = st.columns([1, 2])
            
            with res_col1:
                st.metric(label="Índice de Riesgo (R %)", value=f"{r_porc}%")
                st.caption(f"Ajuste por Altitud ({altitud_eval} msnm): **-{delta_hb:.2f} g/dL** | Hb Ajustada: **{hb_ajustada:.2f} g/dL**")

            with res_col2:
                if color == "green":
                    st.success(f"### Clasificación: **{riesgo.upper()}**")
                    st.markdown("""
                    **Recomendaciones Clínicas y Epidemiológicas:**
                    * **Monitoreo:** Mantener vigilancia comunitaria de rutina en campañas sanitarias.
                    * **Medidas Preventivas:** Promover hábitos comunitarios de higiene (lavado frecuente de manos mano-boca).
                    * **Nutrición:** Fomentar una dieta balanceada rica en calcio, hierro y vitamina C para mitigar la absorción de plomo.
                    """)
                elif color == "orange":
                    st.warning(f"### CUIDADO - Clasificación: **{riesgo.upper()}**")
                    st.markdown("""
                    **Recomendaciones Clínicas y Epidemiológicas:**
                    * **Seguimiento:** Monitoreo comunitario continuo y reprogramación de prueba de plomo en sangre (BLL) en 3 a 6 meses.
                    * **Evaluación Médica:** Canalizar a evaluación nutricional para descartar deficiencia de hierro/anemia.
                    * **Intervención Doméstica:** Identificar y eliminar la fuente de exposición en el hogar (inspección de loza vidriada o descascarillado de pintura).
                    """)
                else:
                    st.error(f"### CUIDADO - Clasificación: **{riesgo.upper()}**")
                    st.markdown("""
                    **Recomendaciones Clínicas y Epidemiológicas:**
                    * **Prioridad Alta:** Canalización prioritaria a valoración médica especializada (pediatría/toxicología) e intervención ambiental inmediata.
                    * **Evaluación del Neurodesarrollo:** Realizar tamizaje y seguimiento del desarrollo psicomotor y neurocognitivo.
                    * **Acción Sanitaria:** Notificación a las autoridades de salud pública para inspección ambiental en la vivienda y radio de 1 km.
                    """)

# ------------------------------------------------------------------------------
# MÓDULO 2: BASE DE DATOS Y CARGA MASIVA
# ------------------------------------------------------------------------------
elif menu == "2. Base de Datos y Carga Epidemiológica":
    st.subheader("Módulo 2: Consulta, Exportación y Carga Masiva de Expedientes")
    
    tab1, tab2 = st.tabs(["Consulta de Expedientes", "Carga Masiva para Epidemiología (CSV/Excel)"])
    
    with tab1:
        conn = conectar_bd()
        df = pd.read_sql_query("SELECT id, fecha, codigo_paciente, edad, bll, hb_medida, hb_ajustada, altitud_evaluacion, residencia, cercania, antecedentes, indice_r_porcentaje, nivel_riesgo FROM registros ORDER BY id DESC", conn)
        conn.close()

        if df.empty:
            st.info("No existen casos registrados en la base de datos comunitaria.")
        else:
            st.dataframe(df, use_container_width=True)
            st.download_button("Descargar Base de Datos (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name="expedientes_vigilancia_plomo.csv", mime="text/csv")

    with tab2:
        st.markdown("#### Carga Masiva de Datos para Análisis Epidemiológico")
        st.write("Sube un archivo de Excel o CSV con los registros recolectados en brigadas de campo.")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            es_torreon_masivo = st.radio("¿La base de datos corresponde a evaluaciones en Torreón, Coahuila (~1,120 msnm)?", ["Sí", "No"], key="radio_masivo") == "Sí"
        with col_c2:
            if not es_torreon_masivo:
                altitud_masiva = st.number_input("Altitud promedio del sitio de recolección (msnm):", min_value=0, max_value=5000, value=1000, key="alt_masivo")
            else:
                altitud_masiva = 1120

        st.markdown("**Columnas requeridas:** `codigo_paciente`, `edad`, `bll`, `hb_medida`, `residencia`, `cercania` (0 o 1), `antecedentes` (0 o 1)")
        
        archivo_subido = st.file_uploader("Seleccione un archivo (.csv o .xlsx):", type=["csv", "xlsx"])
        
        if archivo_subido is not None:
            try:
                if archivo_subido.name.endswith('.csv'):
                    df_cargado = pd.read_csv(archivo_subido)
                else:
                    df_cargado = pd.read_excel(archivo_subido)
                
                st.write("Vista previa de los datos cargados:")
                st.dataframe(df_cargado.head(), use_container_width=True)
                
                if st.button("Procesar y Guardar Lote Completo"):
                    registros_exitosos = 0
                    registros_omitidos = 0
                    
                    conn = conectar_bd()
                    cursor = conn.cursor()
                    
                    for _, fila in df_cargado.iterrows():
                        try:
                            cod = str(fila['codigo_paciente'])
                            ed = int(fila['edad'])
                            bll_val = float(fila['bll'])
                            hb_val = float(fila['hb_medida'])
                            res_val = int(fila['residencia'])
                            cerc_val = bool(int(fila['cercania']))
                            antec_val = bool(int(fila['antecedentes']))
                            
                            # Validación de coherencia biológica
                            if res_val <= ed:
                                r_porc, riesgo, _, hb_ajustada, _, alt_eval = calcular_riesgo_ponderado_oficial(
                                    ed, bll_val, hb_val, res_val, cerc_val, antec_val, es_torreon_masivo, altitud_masiva
                                )
                                cursor.execute('''
                                    INSERT INTO registros 
                                    (codigo_paciente, edad, bll, hb_medida, hb_ajustada, altitud_evaluacion, es_torreon, residencia, cercania, antecedentes, indice_r_porcentaje, nivel_riesgo)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (cod, ed, bll_val, hb_val, hb_ajustada, alt_eval, int(es_torreon_masivo), res_val, int(cerc_val), int(antec_val), r_porc, riesgo))
                                registros_exitosos += 1
                            else:
                                registros_omitidos += 1
                        except Exception:
                            registros_omitidos += 1
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Procesamiento completado: {registros_exitosos} registros ingresados correctamente.")
                    if registros_omitidos > 0:
                        st.warning(f"CUIDADO: {registros_omitidos} registros fueron omitidos por datos inválidos, duplicados o incoherencia biológica (Residencia > Edad).")
            except Exception as e:
                st.error(f"Error al leer el archivo. Asegúrese de que tenga el formato adecuado. Detalle: {e}")

# ------------------------------------------------------------------------------
# MÓDULO 3: DASHBOARD Y ASOCIACIÓN NEUROCOGNITIVA
# ------------------------------------------------------------------------------
elif menu == "3. Dashboard y Asociación Neurocognitiva":
    st.subheader("Módulo 3: Visualización Epidemiológica y Asociación Neurocognitiva")
    conn = conectar_bd()
    df = pd.read_sql_query("SELECT * FROM registros", conn)
    conn.close()

    if df.empty:
        st.info("Registre casos en el Módulo 1 o en la Carga Masiva para habilitar el análisis epidemiológico.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Pacientes Evaluados", len(df))
        col2.metric("Promedio BLL Poblacional", f"{df['bll'].mean():.2f} µg/dL")
        col3.metric("Casos en Riesgo Alto", len(df[df['nivel_riesgo'] == 'Riesgo Alto']))

        st.write("---")
        
        tab_g1, tab_g2 = st.tabs(["Distribución de Riesgo (Pastel)", "Asociación BLL vs Índice de Riesgo (Dispersión)"])
        
        with tab_g1:
            fig1, ax1 = plt.subplots(figsize=(6, 3))
            conteo_riesgos = df['nivel_riesgo'].value_counts()
            colores = {'Riesgo Bajo': '#28a745', 'Riesgo Moderado': '#ffc107', 'Riesgo Alto': '#dc3545'}
            col_list = [colores.get(x, '#6c757d') for x in conteo_riesgos.index]

            ax1.pie(conteo_riesgos, labels=conteo_riesgos.index, autopct='%1.1f%%', colors=col_list, startangle=140)
            ax1.set_title("Distribución Poblacional según Nivel de Riesgo Neurocognitivo")
            st.pyplot(fig1)

        with tab_g2:
            st.markdown("##### Gráfico de Asociación: Concentración de Plomo en Sangre (BLL) vs. Índice de Riesgo R (%)")
            st.caption("Muestra la tendencia y dispersión poblacional para evaluar el impacto acumulativo del metal en la escala de riesgo.")
            
            fig2, ax2 = plt.subplots(figsize=(7, 3.5))
            
            color_map = {'Riesgo Bajo': '#28a745', 'Riesgo Moderado': '#ffc107', 'Riesgo Alto': '#dc3545'}
            df_colors = df['nivel_riesgo'].map(color_map)
            
            ax2.scatter(df['bll'], df['indice_r_porcentaje'], c=df_colors, alpha=0.7, edgecolors='k', s=60)
            
            if len(df) > 1:
                z = np.polyfit(df['bll'], df['indice_r_porcentaje'], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(df['bll'].min(), df['bll'].max(), 100)
                ax2.plot(x_trend, p(x_trend), "k--", alpha=0.6, label="Tendencia Lineal")
            
            ax2.set_xlabel("Nivel de Plomo en Sangre (BLL en µg/dL)")
            ax2.set_ylabel("Índice de Riesgo Neurocognitivo (R %)")
            ax2.set_title("Análisis de Asociación Epidemiológica (BLL vs Risk %)")
            ax2.grid(True, linestyle=":", alpha=0.6)
            ax2.legend()
            
            st.pyplot(fig2)

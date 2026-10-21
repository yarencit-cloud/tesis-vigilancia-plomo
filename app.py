# ------------------------------------------------------------------------------
# MÓDULO 1: CAPTURA Y VALIDACIÓN DE DATOS (VERSIÓN CORREGIDA Y CON LIMPIEZA)
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

    # Usamos clear_on_submit=True para restablecer los widgets del formulario tras el envío
    with st.form("form_captura", clear_on_submit=True):
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

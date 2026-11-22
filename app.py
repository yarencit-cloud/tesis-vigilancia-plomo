            else:
                altitud_masiva = 1120
        st.markdown("**Columnas requeridas:** `codigo_paciente`, `edad`, `bll`, `hb_medida`, `residencia`, `cercania` (0 o 1), `antecedentes` (0 o 1)")
        archivo_subido = st.file_uploader("Seleccione un archivo (.csv o .xlsx):", type=["csv", "xlsx"])
        if archivo_subido is not None:
            try:
                if archivo_subido.name.lower().endswith(".csv"):
                    df_cargado = pd.read_csv(archivo_subido)
                else:
                    df_cargado = pd.read_excel(archivo_subido)
                st.write("Vista previa de los datos cargados:")
                st.dataframe(df_cargado.head(), use_container_width=True)
                if st.button("Procesar y Guardar Lote Completo"):
                    registros_exitosos = 0
                    registros_omitidos = 0
                    conn = None
                    try:
                        conn = conectar_bd()
                        with conn.cursor() as cursor:
                            for _, fila in df_cargado.iterrows():
                                try:
                                    cod = str(fila["codigo_paciente"]).strip()
                                    ed = int(fila["edad"])
                                    bll_val = float(fila["bll"])
                                    hb_val = float(fila["hb_medida"])
                                    res_val = int(fila["residencia"])
                                    cerc_num = int(fila["cercania"])
                                    antec_num = int(fila["antecedentes"])
                                    if (not cod or cod.lower() == "nan" or
                                        not (1 <= ed <= 17) or not (0 <= bll_val <= 80) or
                                        not (3 <= hb_val <= 20) or not (0 <= res_val <= ed) or
                                        cerc_num not in (0, 1) or antec_num not in (0, 1) or
                                        not np.isfinite(bll_val) or not np.isfinite(hb_val)):
                                        registros_omitidos += 1
                                        continue
                                    r_porc, riesgo, _, hb_ajustada, _, alt_eval = calcular_riesgo_ponderado_oficial(
                                        ed, bll_val, hb_val, res_val, bool(cerc_num), bool(antec_num),
                                        es_torreon_masivo, altitud_masiva
                                    )
                                    cursor.execute(SQL_INSERT, (
                                        cod, ed, bll_val, hb_val, hb_ajustada,
                                        alt_eval, int(es_torreon_masivo), res_val,
                                        cerc_num, antec_num, r_porc, riesgo
                                    ))
                                    if cursor.fetchone():
                                        registros_exitosos += 1
                                    else:
                                        registros_omitidos += 1
                                except (ValueError, TypeError, KeyError, OverflowError):
                                    registros_omitidos += 1
                        conn.commit()
                        st.success(f"Procesamiento completado: {registros_exitosos} registros ingresados correctamente.")
                        if registros_omitidos > 0:
                            st.warning(f"CUIDADO: {registros_omitidos} registros fueron omitidos por datos inválidos, duplicados o incoherencia biológica (Residencia > Edad).")
                    except psycopg2.Error:
                        if conn is not None:
                            conn.rollback()
                        st.error("No se pudo guardar el lote en Supabase. La operación se canceló; no se guardaron registros de este lote.")
                    finally:
                        if conn is not None:
                            conn.close()
            except (ValueError, KeyError, ImportError, OSError) as exc:
                st.error(f"Error al leer el archivo. Asegúrese de que tenga el formato adecuado. Detalle: {exc}")

# ------------------------------------------------------------------------------
# MÓDULO 3: DASHBOARD Y ASOCIACIÓN NEUROCOGNITIVA
# ------------------------------------------------------------------------------
elif menu == "3. Dashboard y Asociación Neurocognitiva":
    st.subheader("Módulo 3: Visualización Epidemiológica y Asociación Neurocognitiva")
    try:
        df = consultar_registros()
    except psycopg2.Error:
        st.error("No fue posible consultar los datos epidemiológicos en Supabase.")
        st.stop()

    if df.empty:
        st.info("Registre casos en el Módulo 1 o en la Carga Masiva para habilitar el análisis epidemiológico.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Pacientes Evaluados", len(df))
        col2.metric("Promedio BLL Poblacional", f"{df['bll'].mean():.2f} µg/dL")
        col3.metric("Casos en Riesgo Alto", len(df[df["nivel_riesgo"] == "Riesgo Alto"]))
        st.write("---")
        tab_g1, tab_g2 = st.tabs(["Distribución de Riesgo (Pastel)", "Asociación BLL vs Índice de Riesgo (Dispersión)"])
        with tab_g1:
            fig1, ax1 = plt.subplots(figsize=(6, 3))
            conteo_riesgos = df["nivel_riesgo"].value_counts()
            colores = {"Riesgo Bajo": "#28a745", "Riesgo Moderado": "#ffc107", "Riesgo Alto": "#dc3545"}
            col_list = [colores.get(x, "#6c757d") for x in conteo_riesgos.index]
            ax1.pie(conteo_riesgos, labels=conteo_riesgos.index, autopct="%1.1f%%", colors=col_list, startangle=140)
            ax1.set_title("Distribución Poblacional según Nivel de Riesgo Neurocognitivo")
            st.pyplot(fig1)
            plt.close(fig1)
        with tab_g2:
            st.markdown("##### Gráfico de Asociación: Concentración de Plomo en Sangre (BLL) vs. Índice de Riesgo R (%)")
            st.caption("Muestra la tendencia y dispersión del BLL respecto al índice calculado. Como el BLL forma parte de la fórmula del índice, esta gráfica no demuestra una asociación neurocognitiva independiente.")
            fig2, ax2 = plt.subplots(figsize=(7, 3.5))
            color_map = {"Riesgo Bajo": "#28a745", "Riesgo Moderado": "#ffc107", "Riesgo Alto": "#dc3545"}
            df_colors = df["nivel_riesgo"].map(color_map).fillna("#6c757d")
            ax2.scatter(df["bll"], df["indice_r_porcentaje"], c=df_colors, alpha=0.7, edgecolors="k", s=60)
            if len(df) > 1 and df["bll"].nunique() > 1:
                z = np.polyfit(df["bll"].astype(float), df["indice_r_porcentaje"].astype(float), 1)
                p = np.poly1d(z)
                x_trend = np.linspace(df["bll"].min(), df["bll"].max(), 100)
                ax2.plot(x_trend, p(x_trend), "k--", alpha=0.6, label="Tendencia Lineal")
                ax2.legend()
            ax2.set_xlabel("Nivel de Plomo en Sangre (BLL en µg/dL)")
            ax2.set_ylabel("Índice de Riesgo Neurocognitivo (R %)")
            ax2.set_title("Análisis descriptivo (BLL vs R %)")
            ax2.grid(True, linestyle=":", alpha=0.6)
            st.pyplot(fig2)
            plt.close(fig2)


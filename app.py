import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS DE INGENIERÍA BIOMÉDICA
# ==============================================================================
st.set_page_config(
    page_title="Sistema de Vigilancia de Exposición Infantil a Plomo",
    page_icon="🧪",
    layout="wide",
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
    cursor.execute("""
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
    """)

    # 2. Migración automática: Agregar columnas faltantes si la tabla es antigua
    cursor.execute("PRAGMA table_info(registros)")
    columnas_existentes = [columna[1] for columna in cursor.fetchall()]

    if "altitud_evaluacion" not in columnas_existentes:
        cursor.execute(
            "ALTER TABLE registros ADD COLUMN altitud_evaluacion INTEGER DEFAULT"
            " 1120"
        )
    if "es_torreon" not in columnas_existentes:
        cursor.execute(
            "ALTER TABLE registros ADD COLUMN es_torreon INTEGER DEFAULT 1"
        )

    conn.commit()
    conn.close()


inicializar_bd()


# ==============================================================================
# ALGORITMO PONDERADO Y CÁLCULO DE ALTITUD
# ==============================================================================
def calcular_ajuste_altitud(es_torreon, altitud_ingresada):
    """Cálculo de la corrección de hemoglobina según altitud geográfica (msnm).

    Torreón (~1,120 msnm) representa un ajuste de -0.2 g/dL. Fórmula estándar
    OMS para altitudes >= 1,000 msnm.
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


def calcular_riesgo_ponderado_oficial(
    edad,
    bll,
    hb_medida,
    residencia,
    cercania,
    antecedentes,
    es_torreon,
    altitud_custom,
):
    """Algoritmo de ponderación normalizada (R = \sum W_i * S_i) Pesos Relativos.

    (W_i):
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
        0.30 * s_bll
        + 0.20 * s_hb
        + 0.15 * s_edad
        + 0.15 * s_cerc
        + 0.10 * s_res
        + 0.10 * s_antec
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

    return (
        r_porcentaje,
        clasificacion,
        color,
        hb_ajustada,
        delta_hb,
        altitud_eval,
    )


# ==============================================================================
# INTERFAZ WEB PRINCIPAL
# ==============================================================================
st.title("Sistema de Vigilancia Comunitaria e Índice de Riesgo Neurocognitivo")
st.caption(
    "Plataforma Digital de Evaluación Preliminar de Exposición Infantil a Plomo"
    " — Facultad de Ingeniería Mecánica y Eléctrica"
)
st.write("---")

# DECLARACIÓN DEL MENÚ (Debe ir en el scope principal antes de los bloques IF)
menu = st.sidebar.radio(
    "Navegación / Módulos:",
    [
        "1. Captura y Evaluación Individual",
        "2. Base de Datos y Carga Epidemiológica",
        "3. Dashboard y Asociación Neurocognitiva",
    ],
)

# ------------------------------------------------------------------------------
# MÓDULO 1: CAPTURA Y VALID

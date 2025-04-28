# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 12:15:30 2025

@author: Ignac
"""

import streamlit as st
import pandas as pd
import os

# -----------------------------------------
# CARGAR DATOS
# -----------------------------------------
@st.cache_data
def cargar_datos():
    datos = pd.read_excel('Datos.xlsx')
    return datos

datos = cargar_datos()

# -----------------------------------------
# LOGIN SIMPLE PARA ANOTADORES (CON SESIÓN)
# -----------------------------------------
usuarios_validos = {
    'anotador1': 'clave1',
    'anotador2': 'clave2',
    'anotador3': 'clave3'
}

st.title("Anotación de riesgo de pie diabético 🦶")

# Inicializar variables de sesión
if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = ""

# Pantalla de login
if not st.session_state['logueado']:
    usuario = st.text_input('Usuario')
    clave = st.text_input('Contraseña', type='password')
    login = st.button('Ingresar')

    if login:
        if usuario in usuarios_validos and clave == usuarios_validos[usuario]:
            st.session_state['logueado'] = True
            st.session_state['usuario'] = usuario
            st.success(f"¡Bienvenido {usuario}!")
            st.rerun()  # ✅ Refrescar la app para entrar en modo anotación
        else:
            st.error("Usuario o contraseña incorrectos.")
else:
    # Ya logueado
    usuario = st.session_state['usuario']
    st.success(f"¡Bienvenido {usuario}!")

    # -----------------------------------------
    # BUSCAR ÚLTIMO PACIENTE ANOTADO
    # -----------------------------------------
    ultimo_paciente = None
    if os.path.exists('anotaciones.csv'):
        anotaciones_existentes = pd.read_csv('anotaciones.csv')
        anotaciones_usuario = anotaciones_existentes[anotaciones_existentes['Usuario'] == usuario]
        if not anotaciones_usuario.empty:
            ultimo_paciente = anotaciones_usuario['Paciente_ID'].max()

    # -----------------------------------------
    # ELEGIR PACIENTE
    # -----------------------------------------
    if ultimo_paciente is not None:
        st.info(f"Tu último paciente anotado fue el número {ultimo_paciente}.")
        if st.button(f"Continuar con el paciente {ultimo_paciente + 1}"):
            paciente_id = ultimo_paciente + 1
        else:
            paciente_id = st.number_input('Número de Paciente', min_value=1, max_value=len(datos), step=1)
    else:
        paciente_id = st.number_input('Número de Paciente', min_value=1, max_value=len(datos), step=1)

    # -----------------------------------------
    # MOSTRAR DATOS DEL PACIENTE
    # -----------------------------------------
    st.header("Datos del Paciente")
    paciente = datos[datos['ID'] == paciente_id]

    if not paciente.empty:
        for columna in paciente.columns:
            valor = paciente.iloc[0][columna]
            st.write(f"**{columna}:** {valor}")

        # -----------------------------------------
        # SELECCIONAR RIESGO
        # -----------------------------------------
        st.subheader("Clasificación de riesgo")
        riesgo = st.selectbox(
            "Selecciona el riesgo para este paciente:",
            ["", "Riesgo Bajo", "Riesgo Medio", "Riesgo Alto"]
        )

        # -----------------------------------------
        # GUARDAR ANOTACIÓN
        # -----------------------------------------
        if st.button('Guardar Anotación'):
            if riesgo == "":
                st.warning("Debes seleccionar un nivel de riesgo antes de guardar.")
            else:
                nueva_anotacion = pd.DataFrame({
                    'Usuario': [usuario],
                    'Paciente_ID': [paciente_id],
                    'Riesgo': [riesgo]
                })

                if os.path.exists('anotaciones.csv'):
                    anotaciones_existentes = pd.read_csv('anotaciones.csv')
                    anotaciones_actualizadas = pd.concat([anotaciones_existentes, nueva_anotacion], ignore_index=True)
                else:
                    anotaciones_actualizadas = nueva_anotacion

                anotaciones_actualizadas.to_csv('anotaciones.csv', index=False)
                st.success("¡Anotación guardada exitosamente!")
    else:
        st.error("Paciente no encontrado.")


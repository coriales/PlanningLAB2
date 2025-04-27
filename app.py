import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# Importar funciones del planificador
from route_planner import calcular_duracion, planificar_rutas, generar_excel

# Configuración de la página
st.set_page_config(
    page_title="Planificador de Rutas - Eix Ambiental",
    page_icon="📅",
    layout="wide"
)

# Título y descripción
st.title("Planificador de Rutas - Eix Ambiental")
st.markdown("""
Esta aplicación genera una planificación optimizada de rutas para operarios.
Las tareas se distribuyen de lunes a jueves, hasta un máximo de 4 semanas.
""")

# Barra lateral para la configuración
with st.sidebar:
    st.header("Configuración")
    
    # Carga de archivo
    uploaded_file = st.file_uploader("Cargar archivo Excel", type=["xlsx", "xls"])
    
    # Número de operarios
    num_operarios = st.radio("Número de operarios", [1, 2, 3], horizontal=True)
    
    # Información
    st.info("Las tareas se planificarán de lunes a jueves, hasta un máximo de 4 semanas.")

# Área principal
if uploaded_file:
    st.success(f"Archivo cargado: {uploaded_file.name}")
    
    if st.button("Generar Planificación", type="primary"):
        try:
            # Leer el archivo Excel
            df = pd.read_excel(uploaded_file, header=None)
            st.write("Vista previa de datos:")
            st.dataframe(df.head())
            
            # Planificar rutas
            with st.spinner("Generando planificación..."):
                resultado = planificar_rutas(df, num_operarios)
                
                # Generar Excel para descargar
                excel_bytes = generar_excel(resultado)
                
                # Mostrar botón de descarga
                st.download_button(
                    label="📥 Descargar Planificación Excel",
                    data=excel_bytes,
                    file_name=f"Planificacion_Rutas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                
                # Mostrar resumen
                st.subheader("Resumen de la planificación")
                st.write(f"Total de operarios: {num_operarios}")
                st.write(f"Total de tareas planificadas: {resultado['total_tareas']}")
                
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
else:
    st.info("Por favor, cargue un archivo Excel para comenzar.")

# Footer
st.markdown("---")
st.caption("Planificador de Rutas - Eix Ambiental © 2025")
import pandas as pd
import numpy as np
import re
import io
from datetime import datetime, timedelta

def calcular_duracion(descripcion):
    """Calcula la duración de una tarea basada en su descripción."""
    if not isinstance(descripcion, str):
        return 45  # Valor por defecto si no es string
        
    descripcion = descripcion.lower()
    duracion = 0
    
    # Contar legios
    legio_match = re.search(r'(\d+)\s*legio', descripcion)
    if legio_match:
        num_legios = int(legio_match.group(1))
    elif 'legio' in descripcion:
        num_legios = 1
    else:
        num_legios = 0
    
    # Calcular duración según número de legios
    if num_legios == 1:
        duracion = 45  # 45 minutos
    elif num_legios >= 2 and num_legios <= 3:
        duracion = 60  # 1 hora
    elif num_legios >= 4 and num_legios <= 5:
        duracion = 90  # 1.5 horas
    elif num_legios >= 6 and num_legios <= 7:
        duracion = 120  # 2 horas
    elif num_legios >= 7 and num_legios <= 9:
        duracion = 150  # 2.5 horas
    elif num_legios >= 9 and num_legios <= 11:
        duracion = 180  # 3 horas
    
    # Añadir tiempo si incluye revisión
    if 'revisió' in descripcion or 'revisio' in descripcion:
        duracion += 45
    
    return duracion

def planificar_rutas(df, num_operarios):
    """Función simplificada para planificar rutas."""
    # Extraer datos relevantes
    tareas = []
    for _, row in df.iterrows():
        try:
            # Mapeo de las columnas del Excel
            tarea = {
                'cliente': str(row.iloc[3]) if len(row) > 3 and not pd.isna(row.iloc[3]) else "Cliente sin nombre",
                'poblacion': str(row.iloc[6]) if len(row) > 6 and not pd.isna(row.iloc[6]) else "Sin ubicación",
                'direccion': str(row.iloc[4]) if len(row) > 4 and not pd.isna(row.iloc[4]) else "",
                'descripcion': str(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[11]) else ""
            }
            
            # Calcular duración
            tarea['duracion'] = calcular_duracion(tarea['descripcion'])
            
            # Añadir a la lista si tiene datos válidos
            if tarea['cliente'] != "Cliente sin nombre" and tarea['poblacion'] != "Sin ubicación":
                tareas.append(tarea)
        except Exception as e:
            print(f"Error al procesar fila: {e}")
    
    # Versión simplificada de planificación para el prototipo
    # Agrupar por población
    poblaciones = {}
    for tarea in tareas:
        if tarea['poblacion'] not in poblaciones:
            poblaciones[tarea['poblacion']] = []
        poblaciones[tarea['poblacion']].append(tarea)
    
    # Distribuir entre operarios (versión simple)
    operarios = [{
        'operario_id': i+1,
        'tareas': [],
        'total_tiempo': 0
    } for i in range(num_operarios)]
    
    # Asignar tareas por población al operario con menos carga
    for poblacion, tareas_pob in poblaciones.items():
        # Ordenar operarios por carga
        operarios.sort(key=lambda x: x['total_tiempo'])
        # Asignar todas las tareas de esta población al operario con menos carga
        operarios[0]['tareas'].extend(tareas_pob)
        operarios[0]['total_tiempo'] += sum(t['duracion'] for t in tareas_pob)
    
    # Resultado
    return {
        'operarios': operarios,
        'total_tareas': len(tareas)
    }

def generar_excel(resultado):
    """Genera un archivo Excel con la planificación."""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for operario in resultado['operarios']:
            # Crear dataframe para el operario
            data = []
            
            # Agrupar por población
            poblaciones = {}
            for tarea in operario['tareas']:
                if tarea['poblacion'] not in poblaciones:
                    poblaciones[tarea['poblacion']] = []
                poblaciones[tarea['poblacion']].append(tarea)
            
            # Para cada población
            for poblacion, tareas in poblaciones.items():
                # Añadir encabezado de población
                data.append({
                    'Día': 'Lunes',
                    'Población': poblacion,
                    'Cliente': '',
                    'Dirección': '',
                    'Tarea': '',
                    'Duración': ''
                })
                
                # Añadir tareas
                for tarea in tareas:
                    data.append({
                        'Día': '',
                        'Población': '',
                        'Cliente': tarea['cliente'],
                        'Dirección': tarea['direccion'],
                        'Tarea': tarea['descripcion'],
                        'Duración': f"{tarea['duracion']} min"
                    })
            
            # Crear dataframe y guardar en excel
            if data:
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name=f"Operario {operario['operario_id']}", index=False)
    
    output.seek(0)
    return output.getvalue()

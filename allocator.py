import argparse
import csv
import sys
from typing import List, Dict

def cargar_csv(ruta_archivo: str) -> List[Dict]:
    """Lee un archivo CSV y devuelve una lista de diccionarios."""
    datos = []
    try:
        with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                datos.append(fila)
    except FileNotFoundError:
        print(f"[Error] No se encontró el archivo: {ruta_archivo}")
        sys.exit(1)
    return datos

def asignar_capacidad(equipo: List[Dict], backlog: List[Dict], ruta_salida: str = None) -> None:
    """
    Lógica base de asignación:
    Intenta asignar cada tarea al primer miembro del equipo que tenga
    el rol adecuado y suficientes horas disponibles.
    """
    
    reporte = []
    reporte.append("\n--- RESULTADOS DE ASIGNACIÓN ---\n")

    # Convertimos las horas a enteros para poder operar con ellas
    for miembro in equipo:
        miembro['horas_disponibles'] = int(miembro['horas_disponibles'])
        miembro['tareas_asignadas'] = []

    tareas_sin_asignar = []

    # Reordenar las tareas por prioridad
    prioridades = {"Alta": 1, "Media": 2, "Baja": 3}
    backlog.sort(key=lambda x: prioridades.get(x['prioridad'], 4))

    for tarea in backlog:
        horas_restantes_tarea = int(tarea['horas_estimadas'])
        rol_necesario = tarea['rol_requerido']

        for miembro in equipo:
            # Si el miembro tiene el rol correcto y aún le quedan horas
            if miembro['rol'] == rol_necesario and miembro['horas_disponibles'] > 0:
                # Calculamos cuántas horas puede asumir esta persona
                horas_a_asignar = min(horas_restantes_tarea, miembro['horas_disponibles'])
                
                if horas_a_asignar > 0:
                    # Registramos la tarea y las horas específicas que dedicará
                    miembro['tareas_asignadas'].append(f"{tarea['id_tarea']} ({horas_a_asignar}h)")
                    miembro['horas_disponibles'] -= horas_a_asignar
                    horas_restantes_tarea -= horas_a_asignar
                
                # Si la tarea ya se ha completado, salimos del bucle del equipo
                if horas_restantes_tarea == 0:
                    break
        
        # Si después de revisar a todo el equipo aún quedan horas pendientes para la tarea
        if horas_restantes_tarea > 0:
            tareas_sin_asignar.append({
                'id_tarea': tarea['id_tarea'],
                'rol_requerido': rol_necesario,
                'horas_faltantes': horas_restantes_tarea,
                'horas_originales': tarea['horas_estimadas']
            })

    # Construir reporte del equipo
    for miembro in equipo:
        reporte.append(f"👤 {miembro['nombre']} ({miembro['rol']})")
        reporte.append(f"   Horas restantes: {miembro['horas_disponibles']}h")
        if miembro['tareas_asignadas']:
            reporte.append(f"   Tareas: {', '.join(miembro['tareas_asignadas'])}")
        else:
            reporte.append("   Tareas: Ninguna")
        reporte.append("-" * 30)

    if tareas_sin_asignar:
        reporte.append("\n⚠️ Tareas sin asignar:")
        for tarea in tareas_sin_asignar:
            reporte.append(f"   - {tarea['id_tarea']} (Rol requerido: {tarea['rol_requerido']}, Faltan: {tarea['horas_faltantes']}h de {tarea['horas_originales']})")
    else:
        reporte.append("\n✅ Todas las tareas fueron asignadas exitosamente.")
    
    texto_final = "\n".join(reporte)

    # Mostrar por consola (opcional)
    print(texto_final)

    # Guardar en archivo si se pasó el argumento
    if ruta_salida:
        try:
            with open(ruta_salida, 'w', encoding='utf-8') as archivo_salida:
                archivo_salida.write(texto_final)
            print(f"Entregable de planificación guardado en: {ruta_salida}")
        except IOError as e:
            print(f"Error al guardar el archivo: {e}")

def main():
    # Configuración de los argumentos de línea de comandos (CLI)
    parser = argparse.ArgumentParser(
        description="CLI Tool para asignación de capacidad de equipos IT."
    )
    
    parser.add_argument(
        '-e', '--equipo', 
        type=str, 
        default='data/equipo.csv',
        help='Ruta al archivo CSV con los datos del equipo'
    )
    
    parser.add_argument(
        '-b', '--backlog', 
        type=str, 
        default='data/backlog.csv',
        help='Ruta al archivo CSV con las tareas pendientes'
    )

    parser.add_argument(
        '-o', '--output', 
        type=str, 
        default=None,
        help='Ruta al archivo de salida para guardar el reporte (opcional)'
    )

    # Parsear los argumentos introducidos por el usuario
    args = parser.parse_args()

    print(f"Cargando equipo desde: {args.equipo}")
    print(f"Cargando backlog desde: {args.backlog}")

    # Ejecución
    equipo = cargar_csv(args.equipo)
    backlog = cargar_csv(args.backlog)
    
    asignar_capacidad(equipo, backlog, "data/" + args.output if args.output else None)

if __name__ == "__main__":
    # Ejecutar en primer lugar python allocator.py --help para saber cómo usar la herramienta
    main()

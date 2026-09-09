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

def asignar_capacidad(equipo: List[Dict], backlog: List[Dict]) -> None:
    """
    Lógica base de asignación:
    Intenta asignar cada tarea al primer miembro del equipo que tenga
    el rol adecuado y suficientes horas disponibles.
    """
    print("\n--- RESULTADOS DE ASIGNACIÓN ---\n")
    
    # Convertimos las horas a enteros para poder operar con ellas
    for miembro in equipo:
        miembro['horas_disponibles'] = int(miembro['horas_disponibles'])
        miembro['tareas_asignadas'] = []

    tareas_sin_asignar = []

    for tarea in backlog:
        horas_tarea = int(tarea['horas_estimadas'])
        rol_necesario = tarea['rol_requerido']
        asignada = False

        for miembro in equipo:
            if miembro['rol'] == rol_necesario and miembro['horas_disponibles'] >= horas_tarea:
                # Asignar tarea
                miembro['tareas_asignadas'].append(tarea['id_tarea'])
                miembro['horas_disponibles'] -= horas_tarea
                asignada = True
                break
        
        if not asignada:
            tareas_sin_asignar.append(tarea)

    # Imprimir reporte por consola
    for miembro in equipo:
        print(f"👤 {miembro['nombre']} ({miembro['rol']})")
        print(f"   Horas restantes: {miembro['horas_disponibles']}h")
        if miembro['tareas_asignadas']:
            print(f"   Tareas: {', '.join(miembro['tareas_asignadas'])}")
        else:
            print("   Tareas: Ninguna")
        print("-" * 30)

    if tareas_sin_asignar:
        print("\n⚠️ TAREAS SIN ASIGNAR (Falta capacidad o rol adecuado):")
        for t in tareas_sin_asignar:
            print(f"   - {t['id_tarea']} ({t['rol_requerido']}): {t['horas_estimadas']}h")
    else:
        print("\n✅ Todas las tareas fueron asignadas exitosamente.")

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

    # Parsear los argumentos introducidos por el usuario
    args = parser.parse_args()

    print(f"Cargando equipo desde: {args.equipo}")
    print(f"Cargando backlog desde: {args.backlog}")

    # Ejecución
    equipo = cargar_csv(args.equipo)
    backlog = cargar_csv(args.backlog)
    
    asignar_capacidad(equipo, backlog)

if __name__ == "__main__":
    # Ejecutar en primer lugar python allocator.py --help para saber cómo usar la herramienta
    main()

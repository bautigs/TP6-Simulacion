import random
import math
import numpy as np
from scipy import special
import time
import sys

# Configuración inicial
sys.setrecursionlimit(10**9)

# Variables de control
M = 0  # Operadores de mantenimiento
N = 0  # Operadores de emergencia

while True:
    try:
        M = int(input("Cantidad de operadores de planta mantenimiento (M): "))
        N = int(input("Cantidad de operadores de la planta de emergencia (N): "))
        break
    except ValueError:
        print("\nError: Solo se permiten números enteros.\n")
        continue

# Constantes y variables iniciales
HV = 6666666666666  # Un valor muy alto para representar el infinito
iterationIndex = 0
EVENTO = "C.I."  # Evento inicial

i = -1
j = -1
x = -1

# Inicialización del tiempo y variables del sistema
T = 0
TPLL = 0  # Tiempo de próxima llegada de alarma
INE = 0   # Intervalo de notificación de evento
TAA = 0   # Tiempo de atención del evento de alta prioridad
TABM = 0  # Tiempo de atención del evento de media o baja prioridad
NSA = 0   # Número de notificaciones pendientes de alta prioridad
NSB = 0   # Número de notificaciones pendientes de baja prioridad
NSM = 0   # Número de notificaciones pendientes de media prioridad

# Inicialización de operadores
PTON = [0] * N  # Porcentaje de tiempo ocioso de cada operador de emergencia
PTOM = [0] * M  # Porcentaje de tiempo ocioso de cada operador de mantenimiento

# Vectores de tiempo de próxima salida (para operadores)
TPSN = [HV] * N  # Tiempo de próxima resolución de emergencia
TPSM = [HV] * M  # Tiempo de próxima resolución de mantenimiento

# Cola de eventos (se puede usar un heap para manejar la prioridad)
cola_eventos = []

# Funciones para generar tiempos de llegada y atención
def generar_tiempo_llegada():
    return random.expovariate(1.0 / INE)

def generar_tiempo_atencion(prioridad):
    if prioridad == 'alta':
        return random.expovariate(1.0 / TAA)
    else:
        return random.expovariate(1.0 / TABM)

# Ciclo de simulación (ejemplo simplificado)
while True:
    if T >= HV:  # Condición de finalización (puedes definir otra)
        break

    if T == TPLL:
        # Lógica para manejo de la llegada de una alarma
        # Insertar la lógica de manejo de colas y asignación de operadores
        # Calcular el nuevo tiempo de próxima llegada
        TPLL = T + generar_tiempo_llegada()
    
    for idx in range(N):
        if T == TPSN[idx]:
            # Lógica para manejar la resolución de una alarma por parte de un operador de emergencia
            # Actualizar TPSN[idx]
            TPSN[idx] = HV  # Temporalmente establecer como "infinito"
    
    for idx in range(M):
        if T == TPSM[idx]:
            # Lógica para manejar la resolución de una alarma por parte de un operador de mantenimiento
            # Actualizar TPSM[idx]
            TPSM[idx] = HV  # Temporalmente establecer como "infinito"

    # Avanzar el tiempo
    T += 1  # En un caso real, usarías el menor tiempo entre TPLL, TPSN, TPSM

# Mostrar resultados
### INICIALIZAR VECTORES DEBAJO###

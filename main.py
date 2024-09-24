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

#Vector paralelo con últimas atenciones de mantenimiento 
VUAM = ['L'] * M

#Variables de resultado y auxiliares para calcularla
    #PEB = (STSB - STLLB - STAB) / NTAB 
STSB = 0
STLLB = 0
STAB = 0
NTAB = 0

    #PEM = (STSM - STLLM - STAM) / NTAM 
STSM = 0
STLLM = 0
STAM = 0
NTAM = 0

    #PEA = (STSA - STLLA - STAA) / NTAA 
STSA = 0
STLLA = 0
STAA = 0
NTAA = 0

    #PTON[K] = (STOM[K] * 100) / T 
ITOM = [0] * M
STOM = [0] * M

    #PTOM[K] = (STOM[K] * 100) / T
ITON = [0] * N
STON = [0] * M

# Cola de eventos (se puede usar un heap para manejar la prioridad)
cola_eventos = []

# Funciones para generar tiempos de llegada y atención
#TODO cambiar por distribuciones posta

def generar_tiempo_llegada():
    return random.expovariate(1.0 / INE)

def generar_tiempo_atencion(prioridad):
    if prioridad == 'alta':
        return random.expovariate(1.0 / TAA)
    else:
        return random.expovariate(1.0 / TABM)
    
def obtener_menor_TPS_arreglo(arreglo):
    minTPSLista = HV
    minTPSListaIndex = 0

    for i in range(len(arreglo)):
        if arreglo[i] < minTPSLista:
            minTPSLista = arreglo[i]
            minTPSListaIndex = i

    return minTPSListaIndex
   

def obtener_menor_TPSN():
    return obtener_menor_TPS_arreglo(TPSN)

def obtener_menor_TPSM():
    return obtener_menor_TPS_arreglo(TPSM)

#TODO hacer función 
def buscar_operador(tipo_operador):
    return 1

def simular_llegada():
    T = TPLL
    INE = generar_tiempo_llegada()
    TPLL = T + INE  
    R = random.random()
    if R <= 0.12:
        #logica alta prioridad
        NTAA = NTAA + 1 
        STLLAA = STLLAA + T
        NSAA = NSAA + 1
        if NSAA <= N:
            x = buscar_operador('emergencia')
            TAA = generar_tiempo_atencion('alta')
            TPSN[x] = TPSN[x] + TAA
            STAA = STAA + TAA 
            STON[x] = STON[x] + (T - ITON[x]) 

    else: 
        if R <= 0.47:
            NTAM = NTAM + 1 
            STLLAM = STLLAM + T
            NSM = NSM + 1
            if NSB + NSM <= M:
                x = buscar_operador('mantenimiento')
                TABM = generar_tiempo_atencion('media')
                TPSM[x] = TPSM[x] + TABM
                STAM = STAM + TABM 
                VUAM[x] = 'M'
                STOM[x] = STOM[x] + (T - ITOM[x]) 
                
        else: 
            NTAB = NTAB + 1 
            STLLAB = STLLAB + T
            NSB = NSB + 1
            if NSB + NSM <= M:
                x = buscar_operador('mantenimiento')
                TABM = generar_tiempo_atencion('baja')
                TPSM[x] = TPSM[x] + TABM
                STAM = STAM + TABM 
                VUAM[x] = 'B'
                STOM[x] = STOM[x] + (T - ITOM[x]) 


def simular():
    while True:
    # declarar como global todas las variables que esta función (simulación()) vaya a "tocar" para que las modifique globalmente. Así con cualquier otra función
    # que modifique las variables 
        global T,NSM,STSM,NSB,STSB,TABM,STAM,ITOM,NSA,STSA,TAA,STAA,ITOM,STOM,ITON,STOM
        global TPSN,TPSM
        global i, j
        global VUAM
        
        i = obtener_menor_TPSN()
        j = obtener_menor_TPSM()
        
        if TPSM[i] <= TPSN[j]:
            if TPLL > TPSM[j]: 
            #logica salida mantenimiento
                T = TPSM[j]
                if VUAM[j] == 'M':
                    # Fue una salida de media prioridad
                    NSM = NSM - 1
                    STSM = STSM + T
                
                else: 
                    # Fue una salida de baja prioridad
                    NSB = NSB - 1
                    STSB = STSB + T

                VUAM[j] = 'L'
            
                if NSB + NSM >= M: 
                    if NSM - VUAM.count('M') > 0:
                        TABM = generar_tiempo_atencion('media')
                        TPSM[j] = TPSM[j] + TABM
                        STAM = STAM + TABM
                    else: 
                        TABM = generar_tiempo_atencion('baja')
                        TPSM[j] = TPSM[j] + TABM
                        STAB = STAB + TABM
                else:
                    TPSM[j] = HV
                    ITOM[j] = T
                
                
            else:
            #lógica llegada 
                simular_llegada()
                
        else:   
            if TPLL <= TPSN[i]:
            #lógica llegada
                simular_llegada()

            else:
                T = TPSN[i]
                NSA = NSA - 1
                STSA = STSA + T 
                if NSA >= N:
                    TAA  = generar_tiempo_atencion('alta')
                    TPSN[i] = TPSN[i] + TAA
                    STAA = STAA + TAA
                else: 
                    TPSN[i] = HV
                    ITON[i] = T
            #lógica salida emergencia  
                 
                
        
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
        T += 1  #Menor tiempo entre TPLL, TPSN, TPSM

        if T >= HV:  # Condición de finalización
            break

    # Mostrar resultados


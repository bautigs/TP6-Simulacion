import random
import math
import numpy as np
from scipy import special
from scipy import stats
import time
import sys

#Valores de los parámetros que nos dio la funcion de densidad de probabilidad calculada en colab
#Parametros de la distribucion fatiguelife que nos devolvio en google colab el intervalo de arribo
cIntArribo = 2.39187149184872
locIntArribo = -0.9004218245324229
scaleIntArribo =  45.98871781551828

#Parametros de la distribucion fatiguelife que nos devolvio en google colab el tiempo de atencion de baja y media prioridad
cBajaMediaTempAtencion = 2.6700875592560775
locBajaMediaTempAtencion = 0.5314588059087729
scaleBajaMediaTempAtencion =  33.49069102293302

#Parametros de la distribucion gengamma que nos devolvio en google colab el tiempo de atencion de alarmas de alta prioridad
aAltaTempAtencion = 1.6142700910883647
cAltaTempAtencion = 0.3206763803630954
locAltaTempAtencion = 0.15276667079999998
scaleAltaTempAtencion =  0.7434131662822517

datosGeneradosIntArribo = stats.fatiguelife.rvs(c=cIntArribo, loc=locIntArribo, scale=scaleIntArribo, size=4000, random_state=None)
datosGeneradosTiempoAtencionBajaMedia = stats.fatiguelife.rvs(c=cBajaMediaTempAtencion, loc=locBajaMediaTempAtencion, scale=scaleBajaMediaTempAtencion, size=4000, random_state=None)
datosGeneradosTiempoAtencionAlta = stats.gengamma.rvs(a=aAltaTempAtencion, c= cAltaTempAtencion, loc=locAltaTempAtencion, scale=scaleAltaTempAtencion, size=4000, random_state=None)

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
TF = 100000  #Tiempo final de simulacion
T = 0     #Tiempo actual
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

cont = [0,0,0]

# funcion generadora
def devolver_prox_valor(arreglo,acceso):
    global cont 
    ret = arreglo[cont[acceso]]
    cont[acceso] = cont[acceso] + 1 
    return ret 

# Function para obtener el siguiente valor
def generar_tiempo_llegada():
    return devolver_prox_valor(datosGeneradosIntArribo,0)

def generar_tiempo_atencion_baja_media():
    return devolver_prox_valor(datosGeneradosTiempoAtencionBajaMedia,1)

def generar_tiempo_atencion_alta():
    return devolver_prox_valor(datosGeneradosTiempoAtencionAlta,2)


 # def generar_tiempo_atencion(prioridad):

 #     ret = -1 

 #     if prioridad == 'alta':
 #         ret = generar_tiempo_atencion_alta
 #     else:
 #         if prioridad == 'baja' or prioridad == 'media':
 #             ret = generar_tiempo_atencion_baja_media

        

    
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

def buscar_operador_libre_arreglo(arreglo):
    ret = -1
    for i in range(len(arreglo)):
        if arreglo[i] == HV:
            ret = i
            break
            
    return ret 

def buscar_operador(tipo_operador):

    ret = -1 

    if tipo_operador == 'emergencia':
        ret = buscar_operador_libre_arreglo(TPSN)
    else:
        if tipo_operador == 'mantenimiento':
            ret = buscar_operador_libre_arreglo(TPSM)

    print(f"El operador {ret} de {tipo_operador} está libre")
    return ret
        

def simular_llegada():
    global T,NSM,STSM,NSB,STSB,TABM,STAM,NSA,STSA,TAA,STAA,ITOM,STOM,ITON,STON,NTAB,NTAA,NTAM
    global STLLM,STLLA,STLLB
    global TPSN,TPSM,TPLL
    global i, j
    global VUAM
    global INE
    T = TPLL
    INE = generar_tiempo_llegada()
    print(f"El intervalo de arribo generado fue de {INE}")
    TPLL = T + INE  
    R = random.random()
    print(f"Random generado: {R}")
    if R <= 0.12:
        #logica alta prioridad
        NTAA = NTAA + 1 
        STLLA = STLLA + T
        NSA = NSA + 1
        print(f"Salto una alarma de alta prioridad ")
        if NSA <= N:
            x = buscar_operador('emergencia')
            TAA = generar_tiempo_atencion_alta()
            print(f"El tiempo de atencion generado fue de {TAA}")
            TPSN[x] = T + TAA
            STAA = STAA + TAA 
            STON[x] = STON[x] + (T - ITON[x]) 

    else: 
        if R <= 0.47:
            NTAM = NTAM + 1 
            STLLM = STLLM + T
            NSM = NSM + 1
            print(f"Salto una alarma de media prioridad ")
            if NSB + NSM <= M:
                x = buscar_operador('mantenimiento')
                TABM = generar_tiempo_atencion_baja_media()
                print(f"El tiempo de atencion generado fue de {TABM}")
                TPSM[x] = T + TABM
                STAM = STAM + TABM 
                VUAM[x] = 'M'
                STOM[x] = STOM[x] + (T - ITOM[x]) 
                
        else: 
            NTAB = NTAB + 1 
            STLLB = STLLB + T
            NSB = NSB + 1
            print(f"Salto una alarma de baja prioridad")
            if NSB + NSM <= M:
                x = buscar_operador('mantenimiento')
                TABM = generar_tiempo_atencion_baja_media()
                print(f"El tiempo de atencion generado fue de {TABM}")
                TPSM[x] = T + TABM
                STAM = STAM + TABM 
                VUAM[x] = 'B'
                STOM[x] = STOM[x] + (T - ITOM[x]) 


def simular():
    while True:
    # declarar como global todas las variables que esta función (simulación()) vaya a "tocar" para que las modifique globalmente. Así con cualquier otra función
    # que modifique las variables 
        global T,NSM,STSM,NSB,STSB,TABM,STAM,ITOM,NSA,STSA,TAA,STAA,ITOM,STOM,ITON,STOM,NTAB,NTAA,NTAM,STLLA,STAB
        global TPSN,TPSM,TPLL
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

                print(f"Salida del operador de mantenimiento {j} - Resolvio alarma de {VUAM[j]} prioridad")

                VUAM[j] = 'L'
            
                if NSB + NSM >= M: 
                    if NSM - VUAM.count('M') > 0:
                        TABM = generar_tiempo_atencion_baja_media()
                        TPSM[j] = T + TABM
                        STAM = STAM + TABM
                    else: 
                        TABM = generar_tiempo_atencion_baja_media()
                        TPSM[j] = T + TABM
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
                print(f"Salida del operador de emergencia {i} - Resolvio alarma de alta prioridad")
                if NSA >= N:
                    TAA  = generar_tiempo_atencion_alta()
                    TPSN[i] = T + TAA
                    STAA = STAA + TAA
                else: 
                    TPSN[i] = HV
                    ITON[i] = T
            #lógica salida emergencia  
                 
                
        
        # if T == TPLL:
        #     # Lógica para manejo de la llegada de una alarma
        #     # Insertar la lógica de manejo de colas y asignación de operadores
        #     # Calcular el nuevo tiempo de próxima llegada
        #     TPLL = T + generar_tiempo_llegada()
        
        # for idx in range(N):
        #     if T == TPSN[idx]:
        #         # Lógica para manejar la resolución de una alarma por parte de un operador de emergencia
        #         # Actualizar TPSN[idx]
        #         TPSN[idx] = HV  # Temporalmente establecer como "infinito"
        
        # for idx in range(M):
        #     if T == TPSM[idx]:
        #         # Lógica para manejar la resolución de una alarma por parte de un operador de mantenimiento
        #         # Actualizar TPSM[idx]
        #         TPSM[idx] = HV  # Temporalmente establecer como "infinito"

        # Avanzar el tiempo
        #T += 1  #Menor tiempo entre TPLL, TPSN, TPSM

        if T >= TF:  # Condición de finalización
            if NSA + NSM + NSB == 0:
                PEA = (STSA - STLLA - STAA) / NTAA
                PEB = (STSB - STLLB - STAB) / NTAB
                PEM = (STSM - STLLM - STAM) / NTAM

                print(f"\nPromedio de tiempo de espera para la resolución de un evento de prioridad baja en minutos: {PEA}")
                print(f"Promedio de tiempo de espera para la resolución de un evento de prioridad media en minutos: {PEB}")
                print(f"Promedio de tiempo de espera para la resolución de un evento de prioridad alta en minutos: {PEM}")

                print("\nPorcentajes de tiempo ocioso para operadores de emergencia:")
                for i in range(len(TPSN)):

                    PTON[i] = (STON[i] * 100) / T

                    print(f"Porcentaje de tiempo ocioso operador de emergencia número {i}: {PTON[i]} %")
                
                print("\nPorcentajes de tiempo ocioso para operadores de mantenimiento: ")
                for i in range(len(TPSM)):

                    PTOM[i] = (STOM[i] * 100) / T

                    print(f"Porcentaje de tiempo ocioso operador de mantenimiento número {i}: {PTOM[i]} %")

                break
            else: 
                TPLL=HV
        else: 
            continue
        

    # Mostrar resultados

def main():
    print("\n\n### Comenzando simulacion ###\n\n")
    simular()
    print("\n ------------ Fin simulación ------------")

if __name__ == "__main__":
    main()


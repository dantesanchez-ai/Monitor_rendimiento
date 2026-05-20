import json
import os
import random
from datetime import datetime

RUTA_HISTORIAL = os.path.join(os.path.dirname(__file__), "Historial.json")

_ultimas_metricas = None

USO_MINIMO = 5
USO_MAXIMO = 100
TEMP_MINIMA = 32
TEMP_MAXIMA = 72


def generar_metricas():
    """Generar métricas simuladas de uso y temperatura de CPU y GPU."""
    global _ultimas_metricas

    if _ultimas_metricas is None:
        uso_cpu = random.randint(USO_MINIMO, USO_MAXIMO)
        uso_gpu = random.randint(USO_MINIMO, USO_MAXIMO)
        temp_cpu = random.randint(TEMP_MINIMA, TEMP_MAXIMA)
        temp_gpu = random.randint(TEMP_MINIMA, TEMP_MAXIMA)
    else:
        uso_cpu = _fluctuar_valor(_ultimas_metricas["uso_cpu"], USO_MINIMO, USO_MAXIMO, 0.15)
        uso_gpu = _fluctuar_valor(_ultimas_metricas["uso_gpu"], USO_MINIMO, USO_MAXIMO, 0.15)
        temp_cpu = _temperatura_desde_uso(uso_cpu, _ultimas_metricas["temp_cpu"])
        temp_gpu = _temperatura_desde_uso(uso_gpu, _ultimas_metricas["temp_gpu"])

    metricas = {
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uso_cpu": uso_cpu,
        "uso_gpu": uso_gpu,
        "temp_cpu": temp_cpu,
        "temp_gpu": temp_gpu,
    }

    _ultimas_metricas = metricas
    return metricas


def _fluctuar_valor(valor, minimo, maximo, cambio_maximo_percent):
    """Fluctuar un valor hasta un porcentaje máximo de su valor actual."""
    cambio = valor * random.uniform(-cambio_maximo_percent, cambio_maximo_percent)
    return int(min(maximo, max(minimo, valor + cambio)))


def _temperatura_desde_uso(uso, ultima_temp):
    """Calcular nueva temperatura dependiente del uso con variación limitada."""
    temp_objetivo = TEMP_MINIMA + (uso / 100) * (TEMP_MAXIMA - TEMP_MINIMA)
    cambio_percent = random.choice([0.10, 0.15])
    delta_maximo = ultima_temp * cambio_percent
    delta = temp_objetivo - ultima_temp
    if abs(delta) > delta_maximo:
        delta = delta_maximo if delta > 0 else -delta_maximo
    temp = ultima_temp + delta + random.uniform(-1.5, 1.5)
    return int(min(TEMP_MAXIMA, max(TEMP_MINIMA, temp)))


def guardar_lectura(lectura, nombre_archivo=RUTA_HISTORIAL):
    """Agregar una lectura al archivo de historial en formato JSON."""
    historial = []
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            historial = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historial = []

    historial.append(lectura)
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=2, ensure_ascii=False) #Dump sobreescribe el archivo con la versión actualizada.


def cargar_historial(nombre_archivo=RUTA_HISTORIAL):
    """Cargar el historial de lecturas guardadas desde el archivo."""
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def formatear_barra(porcentaje, longitud=24):
    """Devolver una barra de progreso de texto para consola o etiqueta."""
    llenado = int(porcentaje * longitud / 100)
    return "█" * llenado + "─" * (longitud - llenado)

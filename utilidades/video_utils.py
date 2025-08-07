import os
import subprocess

# usa ffprobe para obtener la duracion del video
def obtener_duracion_video(ruta_video):
    try:
        resultado = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", ruta_video],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        duracion = float(resultado.stdout.decode().strip())
        return duracion
    except Exception as e:
        print(f"No se pudo obtener la duracion del video: {e}")
        return None

#divide un video en fragmentos con ffmpeg
def dividir_video_en_fragmentos(ruta_video, carpeta_salida, cantidad_fragmentos=10):

    duracion = obtener_duracion_video(ruta_video)
    if duracion is None:
        print("No se pudo obtener la duracion del video no se puede dividir")
        return

    duracion_fragmento = duracion / cantidad_fragmentos

    # genera ruta de salida para cada fragmento
    nombre_base = os.path.splitext(os.path.basename(ruta_video))[0]
    salida_fragmentos = os.path.join(carpeta_salida, nombre_base + "_%03d.mp4")

    comando = [
        "ffmpeg",
        "-i", ruta_video,
        "-c", "copy",
        "-map", "0",
        "-f", "segment",
        "-segment_time", str(duracion_fragmento),
        "-reset_timestamps", "1",
        salida_fragmentos
    ]

    print(f"Dividiendo video en {cantidad_fragmentos} fragmentos de aproximadamente {duracion_fragmento:.2f} segundos cada uno")
    subprocess.run(comando)
    print(f"Fragmentos guardados en: {carpeta_salida}")


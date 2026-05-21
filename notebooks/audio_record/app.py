import sounddevice as sd
import soundfile as sf
import numpy as np
import keyboard
import matplotlib.pyplot as plt
import os

recording = False
audio_buffer = []  # para almacenar frames
fs = 16000  # frecuencia de muestreo
filename_id = 1   # contador de grabaciones

out_dir = "../../dataset/papa/"

abs_path = os.path.abspath(out_dir)
if not os.path.exists(abs_path):
    os.makedirs(abs_path)

def audio_callback(indata, frames, time, status):
    """Se llama automáticamente con cada bloque de audio."""
    if recording:
        audio_buffer.append(indata.copy())

def toggle_recording(event):
    global recording, audio_buffer, filename_id

    recording = not recording

    if recording:
        print(f"🎙️ Grabando audio #{filename_id} ...")
        audio_buffer = []  # resetear buffer
    else:
        print(f"💾 Grabación #{filename_id} detenida, guardando...")
        audio_data = np.concatenate(audio_buffer, axis=0)
        sf.write(os.path.join(
            out_dir, f"grabacion_{filename_id}.wav"
        ), audio_data, fs)
        print(f"Archivo guardado: grabacion_{filename_id}.wav")

        # Mostrar buffer
        # plt.figure(figsize=(10, 4))
        # data = audio_data.flatten()
        # plt.plot(data)
        # plt.title(f"Grabación #{filename_id}")
        # plt.xlabel("Muestra")
        # plt.ylabel("Amplitud")
        # plt.show()

        filename_id += 1


# Configurar stream
stream = sd.InputStream(samplerate=fs, channels=1, callback=audio_callback)
stream.start()

# Asignar tecla para iniciar/detener
keyboard.on_press_key("enter", toggle_recording)

print("Presiona ENTER para grabar/detener, ESC para salir.")

# Mantener el programa corriendo
keyboard.wait("esc")
stream.stop()
stream.close()
print("👋 Programa terminado.")



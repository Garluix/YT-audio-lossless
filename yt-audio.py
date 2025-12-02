import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import os
import threading
import sys

# --- Función de Descarga (Ejecutada en un Hilo) ---

def descargar_audio_hifi(url_video, directorio_destino, formato_salida, estado_label):
    """
    Descarga el stream de audio con la tasa de bits más alta y lo convierte
    al formato de salida deseado (FLAC o MP3) usando FFmpeg.
    """
    if not url_video or not directorio_destino:
        messagebox.showerror("Error", "Por favor, introduce la URL y selecciona un directorio.")
        estado_label.config(text="Estado: Error")
        return

    # Opciones de yt-dlp para el mejor audio
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': os.path.join(directorio_destino, '%(title)s.%(ext)s'),
        'noplaylist': True, 
        'noprogress': True,
        'verbose': False, 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': formato_salida,
            # '0' para FLAC (sin pérdida), '320' para MP3 (máx. calidad)
            'preferredquality': '0' if formato_salida == 'flac' else '320', 
        }],
    }

    try:
        estado_label.config(text="Estado: Descargando información...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Obtener el título antes de la descarga para el mensaje de estado
            info_dict = ydl.extract_info(url_video, download=False)
            titulo = info_dict.get('title', 'Audio sin título')
            
            estado_label.config(text=f"Estado: Descargando '{titulo}' y convirtiendo a {formato_salida.upper()}...")
            
            # Descargar y convertir
            ydl.download([url_video])
            
            # Finalización
            messagebox.showinfo("Éxito", f"¡Descarga de '{titulo}' a {formato_salida.upper()} completada!\nGuardado en: {directorio_destino}")
            estado_label.config(text="Estado: Descarga completada")

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "ffmpeg" in error_msg:
             messagebox.showerror("Error de Descarga", f"❌ ERROR: FFmpeg no se encontró.\n\n{error_msg}")
        else:
             messagebox.showerror("Error de Descarga", f"No se pudo descargar el audio:\n\n{error_msg}")
        estado_label.config(text="Estado: Error")
        
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        estado_label.config(text="Estado: Error")


# --- Funciones de la Interfaz ---

def seleccionar_directorio(path_var):
    """Abre un diálogo para seleccionar el directorio de destino."""
    directorio = filedialog.askdirectory()
    if directorio:
        path_var.set(directorio)

def iniciar_descarga(url_entry, path_var, calidad_var, estado_label):
    """Obtiene los parámetros e inicia la descarga en un hilo."""
    url = url_entry.get()
    directorio = path_var.get()
    calidad = calidad_var.get()
    
    if not url or not directorio:
        messagebox.showwarning("Advertencia", "Por favor, introduce la URL y selecciona un directorio.")
        return

    # Iniciar la descarga en un hilo para evitar que la GUI se congele
    hilo = threading.Thread(target=descargar_audio_hifi, 
                            args=(url, directorio, calidad.lower().split()[0], estado_label))
    hilo.start()
    estado_label.config(text="Estado: Iniciando descarga en segundo plano...")


# --- Configuración de la GUI (Tkinter) ---

def crear_gui():
    root = tk.Tk()
    root.title("🎶 Descargador de Audio Hi-Fi de YouTube")
    root.geometry("550x300")
    root.resizable(False, False)

    # Variables de control
    url_var = tk.StringVar()
    # Directorio predeterminado en la carpeta de descargas
    path_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Downloads', 'YT_Audio_HiFi'))
    calidad_var = tk.StringVar(value="FLAC (Sin Pérdida)")

    # Estilos
    style = ttk.Style()
    style.configure('TLabel', font=('Arial', 10))
    style.configure('TButton', font=('Arial', 10, 'bold'))

    # Marco principal
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill='both', expand=True)

    # 1. Etiqueta y campo de URL
    ttk.Label(main_frame, text="URL del Video de YouTube:", style='TLabel').grid(row=0, column=0, sticky='w', pady=5)
    url_entry = ttk.Entry(main_frame, textvariable=url_var, width=60)
    url_entry.grid(row=1, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

    # 2. Etiqueta y campo de Directorio
    ttk.Label(main_frame, text="Directorio de Guardado:", style='TLabel').grid(row=2, column=0, sticky='w', pady=5)
    path_entry = ttk.Entry(main_frame, textvariable=path_var, width=50, state='readonly')
    path_entry.grid(row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
    
    # Botón para seleccionar directorio
    ttk.Button(main_frame, text="Buscar Carpeta", command=lambda: seleccionar_directorio(path_var)).grid(row=3, column=2, sticky='e', padx=5)

    # 3. Selector de Calidad
    ttk.Label(main_frame, text="Formato de Audio:", style='TLabel').grid(row=4, column=0, sticky='w', pady=10)
    opciones_calidad = ["FLAC (Sin Pérdida)", "MP3 (320 kbps)"]
    calidad_selector = ttk.Combobox(main_frame, textvariable=calidad_var, values=opciones_calidad, state="readonly", width=25)
    calidad_selector.grid(row=4, column=1, sticky='w', padx=5)

    # 4. Botón de Descarga
    ttk.Button(main_frame, text="📥 DESCARGAR AUDIO", 
               command=lambda: iniciar_descarga(url_entry, path_var, calidad_var, estado_label),
               style='TButton').grid(row=5, column=0, columnspan=3, pady=15, sticky='ew')
    
    # 5. Etiqueta de Estado
    estado_label = ttk.Label(main_frame, text="Estado: Listo", foreground="blue", font=('Arial', 11, 'bold'))
    estado_label.grid(row=6, column=0, columnspan=3, sticky='w', pady=5)

    # Configurar expansión de columnas
    main_frame.grid_columnconfigure(1, weight=1)

    root.mainloop()

if __name__ == "__main__":
    crear_gui()
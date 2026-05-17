import tkinter as tk
from tkinter import messagebox

from data import generar_metricas, guardar_lectura


class MonitorRendimiento:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Monitor Simulado de Rendimiento")
        self.raiz.geometry("520x380")
        self.raiz.resizable(False, False)

        self.vista_actual = 0
        self.vistas = [self.construir_vista_rendimiento, self.construir_vista_temperatura]
        self.tema = "oscuro"
        self.metricas = generar_metricas()

        self.crear_widgets()
        self.mostrar_vista(0)
        self.raiz.after(1200, self.actualizar_metricas)
        self.asignar_atajos()

    def crear_widgets(self):
        self.encabezado = tk.Label(self.raiz, text="Monitor de Rendimiento", font=("Segoe UI", 18, "bold"))
        self.encabezado.pack(pady=(10, 4))

        self.subtitulo = tk.Label(self.raiz, text="Pantalla 1: Uso de CPU y GPU", font=("Segoe UI", 11))
        self.subtitulo.pack(pady=(0, 10))

        self.marco_contenido = tk.Frame(self.raiz)
        self.marco_contenido.pack(fill="both", expand=True, padx=16, pady=8)

        self.marco_inferior = tk.Frame(self.raiz)
        self.marco_inferior.pack(fill="x", pady=(0, 10))

        self.botones = []
        self.agregar_boton_inferior("Vista 1", lambda: self.mostrar_vista(0))
        self.agregar_boton_inferior("Vista 2", lambda: self.mostrar_vista(1))
        self.agregar_boton_inferior("Guardar", self.guardar_lectura_actual)
        self.agregar_boton_inferior("Tema", self.cambiar_tema)
        self.agregar_boton_inferior("Salir", self.raiz.quit)

        self.etiqueta_estado = tk.Label(self.marco_inferior, text="Actualizando...", anchor="w")
        self.etiqueta_estado.pack(side="left", padx=(10, 0))

    def agregar_boton_inferior(self, texto, comando):
        boton = tk.Button(self.marco_inferior, text=texto, width=10, command=comando)
        boton.pack(side="right", padx=4)
        self.botones.append(boton)

    def asignar_atajos(self):
        self.raiz.bind("<Left>", lambda evento: self.mostrar_vista(0))
        self.raiz.bind("<Right>", lambda evento: self.mostrar_vista(1))
        self.raiz.bind("1", lambda evento: self.mostrar_vista(0))
        self.raiz.bind("2", lambda evento: self.mostrar_vista(1))
        self.raiz.bind("s", lambda evento: self.guardar_lectura_actual())

    def limpiar_contenido(self):
        for widget in self.marco_contenido.winfo_children():
            widget.destroy()

    def mostrar_vista(self, indice_vista):
        self.vista_actual = indice_vista % len(self.vistas)
        self.limpiar_contenido()
        self.subtitulo.config(text=f"Pantalla {self.vista_actual + 1}: {['Uso','Temperaturas'][self.vista_actual]}")
        self.vistas[self.vista_actual]()
        self.aplicar_tema()

    def construir_vista_rendimiento(self):
        self.etiqueta_cpu = tk.Label(self.marco_contenido, text="CPU", font=("Segoe UI", 14, "bold"))
        self.etiqueta_cpu.pack(anchor="w")
        self.canvas_cpu = self.crear_canvas_barra(self.marco_contenido)
        self.canvas_cpu.pack(fill="x", pady=(0, 10))

        self.etiqueta_gpu = tk.Label(self.marco_contenido, text="GPU", font=("Segoe UI", 14, "bold"))
        self.etiqueta_gpu.pack(anchor="w")
        self.canvas_gpu = self.crear_canvas_barra(self.marco_contenido)
        self.canvas_gpu.pack(fill="x", pady=(0, 10))

        self.etiqueta_detalle = tk.Label(self.marco_contenido, text="Presiona 1 o 2 para cambiar de vista.", font=("Segoe UI", 10))
        self.etiqueta_detalle.pack(anchor="w", pady=(12, 0))

        self.actualizar_vista_rendimiento()

    def construir_vista_temperatura(self):
        self.etiqueta_temperatura = tk.Label(self.marco_contenido, text="Temperaturas", font=("Segoe UI", 14, "bold"))
        self.etiqueta_temperatura.pack(anchor="w")

        self.marco_temperatura = tk.Frame(self.marco_contenido)
        self.marco_temperatura.pack(fill="x", pady=(6, 0))

        self.etiqueta_temp_cpu = tk.Label(self.marco_temperatura, text="CPU: -- °C", font=("Segoe UI", 12))
        self.etiqueta_temp_cpu.grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        self.etiqueta_temp_gpu = tk.Label(self.marco_temperatura, text="GPU: -- °C", font=("Segoe UI", 12))
        self.etiqueta_temp_gpu.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=4)

        self.descripcion_temp = tk.Label(self.marco_contenido, text="La temperatura sube con el uso de CPU y GPU.", font=("Segoe UI", 10))
        self.descripcion_temp.pack(anchor="w", pady=(8, 0))

        self.mapa_calor = self.crear_mapa_calor(self.marco_contenido)
        self.mapa_calor.pack(fill="x", pady=(8, 0))

        self.actualizar_vista_temperatura()

    def crear_canvas_barra(self, padre):
        canvas = tk.Canvas(padre, height=36, bg="#2b2b2b", highlightthickness=0)
        canvas.create_rectangle(4, 10, 504, 26, fill="#1b1b1b", outline="#444444", tags=("fondo",))
        return canvas

    def crear_mapa_calor(self, padre):
        marco = tk.Frame(padre)
        for i, etiqueta in enumerate(["Bajo", "Medio", "Alto"]):
            caja = tk.Frame(marco, width=160, height=56, bg="#444444")
            caja.grid(row=0, column=i, padx=4, pady=2)
            caja.grid_propagate(False)
            tk.Label(caja, text=etiqueta, fg="#ffffff", bg="#444444", font=("Segoe UI", 10, "bold")).pack(expand=True)
        return marco

    def actualizar_metricas(self):
        self.metricas = generar_metricas()
        if self.vista_actual == 0:
            self.actualizar_vista_rendimiento()
        else:
            self.actualizar_vista_temperatura()

        self.etiqueta_estado.config(text=f"Última actualización: {self.metricas['fecha_hora']}")
        self.raiz.after(1200, self.actualizar_metricas)

    def actualizar_vista_rendimiento(self):
        self.dibujar_barra_uso(self.canvas_cpu, self.metricas["uso_cpu"], "CPU")
        self.dibujar_barra_uso(self.canvas_gpu, self.metricas["uso_gpu"], "GPU")

    def actualizar_vista_temperatura(self):
        self.etiqueta_temp_cpu.config(text=f"CPU: {self.metricas['temp_cpu']} °C")
        self.etiqueta_temp_gpu.config(text=f"GPU: {self.metricas['temp_gpu']} °C")
        self.actualizar_mapa_calor()

    def dibujar_barra_uso(self, canvas, uso, etiqueta):
        canvas.delete("uso")
        ancho_relleno = int(496 * uso / 100)
        color = self.color_por_uso(uso)
        canvas.create_rectangle(4, 10, 4 + ancho_relleno, 26, fill=color, outline="", tags=("uso",))
        canvas.create_text(260, 18, text=f"{etiqueta} {uso}%", fill="#ffffff", font=("Segoe UI", 10, "bold"), tags=("uso",))

    def actualizar_mapa_calor(self):
        nivel_cpu = self.nivel_calor(self.metricas["temp_cpu"])
        nivel_gpu = self.nivel_calor(self.metricas["temp_gpu"])
        cajas = self.mapa_calor.winfo_children()
        for indice, caja in enumerate(cajas):
            color = ["#2e7d32", "#f57f17", "#c62828"][indice]
            caja.config(bg=color)
            for hijo in caja.winfo_children():
                hijo.config(bg=color)

        etiqueta = f"CPU: {'Bajo' if nivel_cpu == 0 else 'Medio' if nivel_cpu == 1 else 'Alto'} | GPU: {'Bajo' if nivel_gpu == 0 else 'Medio' if nivel_gpu == 1 else 'Alto'}"
        if hasattr(self, "etiqueta_mapa_calor"):
            self.etiqueta_mapa_calor.config(text=etiqueta)
        else:
            self.etiqueta_mapa_calor = tk.Label(self.marco_contenido, text=etiqueta, font=("Segoe UI", 11))
            self.etiqueta_mapa_calor.pack(anchor="w", pady=(10, 0))

    def nivel_calor(self, temp):
        if temp < 55:
            return 0
        if temp < 72:
            return 1
        return 2

    def color_por_uso(self, uso):
        if uso >= 80:
            return "#d32f2f"
        if uso >= 60:
            return "#f9a825"
        return "#388e3c"

    def guardar_lectura_actual(self):
        guardar_lectura(self.metricas)
        messagebox.showinfo("Guardado", "Lectura guardada en Historial.json")

    def cambiar_tema(self):
        self.tema = "claro" if self.tema == "oscuro" else "oscuro"
        self.aplicar_tema()

    def aplicar_tema(self):
        fondo = "#121212" if self.tema == "oscuro" else "#f2f2f2"
        texto = "#ffffff" if self.tema == "oscuro" else "#1a1a1a"
        panel_fondo = "#1f1f1f" if self.tema == "oscuro" else "#ffffff"
        boton_fondo = "#2c2c2c" if self.tema == "oscuro" else "#e0e0e0"

        self.raiz.config(bg=fondo)
        self.encabezado.config(bg=fondo, fg=texto)
        self.subtitulo.config(bg=fondo, fg=texto)
        self.marco_contenido.config(bg=fondo)
        self.marco_inferior.config(bg=fondo)
        self.etiqueta_estado.config(bg=fondo, fg=texto)

        for boton in self.botones:
            boton.config(bg=boton_fondo, fg=texto, activebackground="#5a5a5a" if self.tema == "oscuro" else "#d4d4d4")

        for widget in self.marco_contenido.winfo_children():
            try:
                widget.config(bg=fondo, fg=texto)
            except tk.TclError:
                pass

        if hasattr(self, "canvas_cpu"):
            self.canvas_cpu.config(bg=panel_fondo)
            self.canvas_gpu.config(bg=panel_fondo)

        if self.vista_actual == 1 and hasattr(self, "marco_temperatura"):
            for hijo in self.marco_temperatura.winfo_children():
                try:
                    hijo.config(bg=fondo, fg=texto)
                except tk.TclError:
                    pass


if __name__ == "__main__":
    raiz = tk.Tk()
    app = MonitorRendimiento(raiz)
    raiz.mainloop()

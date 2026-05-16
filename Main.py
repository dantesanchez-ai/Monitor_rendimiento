import tkinter as tk
from tkinter import messagebox

from data import generate_metrics, save_reading


class MonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Simulado de Rendimiento")
        self.root.geometry("520x380")
        self.root.resizable(False, False)

        self.current_view = 0
        self.views = [self.build_performance_view, self.build_temperature_view]
        self.theme = "dark"
        self.metrics = generate_metrics()

        self.create_widgets()
        self.show_view(0)
        self.root.after(1200, self.refresh_metrics)
        self.bind_shortcuts()

    def create_widgets(self):
        self.header = tk.Label(self.root, text="Monitor de Rendimiento", font=("Segoe UI", 18, "bold"))
        self.header.pack(pady=(10, 4))

        self.subtitle = tk.Label(self.root, text="Pantalla 1: Uso de CPU y GPU", font=("Segoe UI", 11))
        self.subtitle.pack(pady=(0, 10))

        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True, padx=16, pady=8)

        self.footer_frame = tk.Frame(self.root)
        self.footer_frame.pack(fill="x", pady=(0, 10))

        self.buttons = []
        self.add_footer_button("Vista 1", lambda: self.show_view(0))
        self.add_footer_button("Vista 2", lambda: self.show_view(1))
        self.add_footer_button("Guardar", self.save_current_reading)
        self.add_footer_button("Tema", self.toggle_theme)
        self.add_footer_button("Salir", self.root.quit)

        self.status_label = tk.Label(self.footer_frame, text="Actualizando...", anchor="w")
        self.status_label.pack(side="left", padx=(10, 0))

    def add_footer_button(self, text, command):
        button = tk.Button(self.footer_frame, text=text, width=10, command=command)
        button.pack(side="right", padx=4)
        self.buttons.append(button)

    def bind_shortcuts(self):
        self.root.bind("<Left>", lambda event: self.show_view(0))
        self.root.bind("<Right>", lambda event: self.show_view(1))
        self.root.bind("1", lambda event: self.show_view(0))
        self.root.bind("2", lambda event: self.show_view(1))
        self.root.bind("s", lambda event: self.save_current_reading())

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_view(self, view_index):
        self.current_view = view_index % len(self.views)
        self.clear_content()
        self.subtitle.config(text=f"Pantalla {self.current_view + 1}: {['Uso','Temperaturas'][self.current_view]}")
        self.views[self.current_view]()
        self.apply_theme()

    def build_performance_view(self):
        self.cpu_label = tk.Label(self.content_frame, text="CPU", font=("Segoe UI", 14, "bold"))
        self.cpu_label.pack(anchor="w")
        self.cpu_canvas = self.create_bar_canvas(self.content_frame)
        self.cpu_canvas.pack(fill="x", pady=(0, 10))

        self.gpu_label = tk.Label(self.content_frame, text="GPU", font=("Segoe UI", 14, "bold"))
        self.gpu_label.pack(anchor="w")
        self.gpu_canvas = self.create_bar_canvas(self.content_frame)
        self.gpu_canvas.pack(fill="x", pady=(0, 10))

        self.detail_label = tk.Label(self.content_frame, text="Presiona 1 o 2 para cambiar de vista.", font=("Segoe UI", 10))
        self.detail_label.pack(anchor="w", pady=(12, 0))

        self.update_performance_view()

    def build_temperature_view(self):
        self.temp_label = tk.Label(self.content_frame, text="Temperaturas", font=("Segoe UI", 14, "bold"))
        self.temp_label.pack(anchor="w")

        self.temperature_frame = tk.Frame(self.content_frame)
        self.temperature_frame.pack(fill="x", pady=(6, 0))

        self.cpu_temp_label = tk.Label(self.temperature_frame, text="CPU: -- °C", font=("Segoe UI", 12))
        self.cpu_temp_label.grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        self.gpu_temp_label = tk.Label(self.temperature_frame, text="GPU: -- °C", font=("Segoe UI", 12))
        self.gpu_temp_label.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=4)

        self.temp_description = tk.Label(self.content_frame, text="La temperatura sube con el uso de CPU y GPU.", font=("Segoe UI", 10))
        self.temp_description.pack(anchor="w", pady=(8, 0))

        self.heat_map = self.create_heat_map(self.content_frame)
        self.heat_map.pack(fill="x", pady=(8, 0))

        self.update_temperature_view()

    def create_bar_canvas(self, parent):
        canvas = tk.Canvas(parent, height=36, bg="#2b2b2b", highlightthickness=0)
        canvas.create_rectangle(4, 10, 504, 26, fill="#1b1b1b", outline="#444444", tags=("background",))
        return canvas

    def create_heat_map(self, parent):
        frame = tk.Frame(parent)
        for i, label in enumerate(["Bajo", "Medio", "Alto"]):
            box = tk.Frame(frame, width=160, height=56, bg="#444444")
            box.grid(row=0, column=i, padx=4, pady=2)
            box.grid_propagate(False)
            tk.Label(box, text=label, fg="#ffffff", bg="#444444", font=("Segoe UI", 10, "bold")).pack(expand=True)
        return frame

    def refresh_metrics(self):
        self.metrics = generate_metrics()
        if self.current_view == 0:
            self.update_performance_view()
        else:
            self.update_temperature_view()

        self.status_label.config(text=f"Última actualización: {self.metrics['timestamp']}")
        self.root.after(1200, self.refresh_metrics)

    def update_performance_view(self):
        self.draw_usage_bar(self.cpu_canvas, self.metrics["cpu_usage"], "CPU")
        self.draw_usage_bar(self.gpu_canvas, self.metrics["gpu_usage"], "GPU")

    def update_temperature_view(self):
        self.cpu_temp_label.config(text=f"CPU: {self.metrics['cpu_temp']} °C")
        self.gpu_temp_label.config(text=f"GPU: {self.metrics['gpu_temp']} °C")
        self.update_heat_map()

    def draw_usage_bar(self, canvas, usage, label):
        canvas.delete("usage")
        fill_width = int(496 * usage / 100)
        color = self.color_for_usage(usage)
        canvas.create_rectangle(4, 10, 4 + fill_width, 26, fill=color, outline="", tags=("usage",))
        canvas.create_text(260, 18, text=f"{label} {usage}%", fill="#ffffff", font=("Segoe UI", 10, "bold"), tags=("usage",))

    def update_heat_map(self):
        cpu_level = self.heat_level(self.metrics["cpu_temp"])
        gpu_level = self.heat_level(self.metrics["gpu_temp"])
        boxes = self.heat_map.winfo_children()
        for index, box in enumerate(boxes):
            color = ["#2e7d32", "#f57f17", "#c62828"][index]
            box.config(bg=color)
            for child in box.winfo_children():
                child.config(bg=color)

        label = f"CPU: {'Bajo' if cpu_level == 0 else 'Medio' if cpu_level == 1 else 'Alto'} | GPU: {'Bajo' if gpu_level == 0 else 'Medio' if gpu_level == 1 else 'Alto'}"
        if hasattr(self, "heat_label"):
            self.heat_label.config(text=label)
        else:
            self.heat_label = tk.Label(self.content_frame, text=label, font=("Segoe UI", 11))
            self.heat_label.pack(anchor="w", pady=(10, 0))

    def heat_level(self, temp):
        if temp < 55:
            return 0
        if temp < 72:
            return 1
        return 2

    def color_for_usage(self, usage):
        if usage >= 80:
            return "#d32f2f"
        if usage >= 60:
            return "#f9a825"
        return "#388e3c"

    def save_current_reading(self):
        save_reading(self.metrics)
        messagebox.showinfo("Guardado", "Lectura guardada en monitor_history.json")

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        bg = "#121212" if self.theme == "dark" else "#f2f2f2"
        fg = "#ffffff" if self.theme == "dark" else "#1a1a1a"
        panel_bg = "#1f1f1f" if self.theme == "dark" else "#ffffff"
        button_bg = "#2c2c2c" if self.theme == "dark" else "#e0e0e0"

        self.root.config(bg=bg)
        self.header.config(bg=bg, fg=fg)
        self.subtitle.config(bg=bg, fg=fg)
        self.content_frame.config(bg=bg)
        self.footer_frame.config(bg=bg)
        self.status_label.config(bg=bg, fg=fg)

        for button in self.buttons:
            button.config(bg=button_bg, fg=fg, activebackground="#5a5a5a" if self.theme == "dark" else "#d4d4d4")

        for widget in self.content_frame.winfo_children():
            try:
                widget.config(bg=bg, fg=fg)
            except tk.TclError:
                pass

        if hasattr(self, "cpu_canvas"):
            self.cpu_canvas.config(bg=panel_bg)
            self.gpu_canvas.config(bg=panel_bg)

        if self.current_view == 1 and hasattr(self, "temperature_frame"):
            for child in self.temperature_frame.winfo_children():
                child.config(bg=bg, fg=fg)


if __name__ == "__main__":
    root = tk.Tk()
    app = MonitorApp(root)
    root.mainloop()

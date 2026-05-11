import json
import random
from datetime import datetime

HISTORY_FILE = "monitor_history.json"

def generate_metrics():
    """Generate simulated CPU and GPU usage and temperature metrics."""
    cpu_usage = random.randint(5, 98)
    gpu_usage = random.randint(3, 96)
    cpu_temp = _temperature_from_usage(cpu_usage, 35, 80)
    gpu_temp = _temperature_from_usage(gpu_usage, 30, 78)
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage": cpu_usage,
        "gpu_usage": gpu_usage,
        "cpu_temp": cpu_temp,
        "gpu_temp": gpu_temp,
    }


def _temperature_from_usage(usage, base, max_temp):
    """Convert usage into a simulated temperature value."""
    noise = random.uniform(-2.5, 2.5)
    return int(min(max_temp, max(base, base + usage * 0.45 + noise)))


def save_reading(reading, filename=HISTORY_FILE):
    """Append a reading to the history file in JSON format."""
    history = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(reading)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_history(filename=HISTORY_FILE):
    """Load saved history readings from the history file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def format_bar(percent, length=24):
    """Return a simple text progress bar for console or label display."""
    filled = int(percent * length / 100)
    return "█" * filled + "─" * (length - filled)

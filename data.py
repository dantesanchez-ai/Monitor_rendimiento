import json
import random
from datetime import datetime

HISTORY_FILE = "monitor_history.json"

_last_metrics = None

USAGE_MIN = 5
USAGE_MAX = 100
TEMP_MIN = 32
TEMP_MAX = 72


def generate_metrics():
    """Generate simulated CPU and GPU usage and temperature metrics."""
    global _last_metrics

    if _last_metrics is None:
        cpu_usage = random.randint(USAGE_MIN, USAGE_MAX)
        gpu_usage = random.randint(USAGE_MIN, USAGE_MAX)
        cpu_temp = random.randint(TEMP_MIN, TEMP_MAX)
        gpu_temp = random.randint(TEMP_MIN, TEMP_MAX)
    else:
        cpu_usage = _fluctuate_value(_last_metrics["cpu_usage"], USAGE_MIN, USAGE_MAX, 0.15)
        gpu_usage = _fluctuate_value(_last_metrics["gpu_usage"], USAGE_MIN, USAGE_MAX, 0.15)
        cpu_temp = _temperature_from_usage(cpu_usage, _last_metrics["cpu_temp"])
        gpu_temp = _temperature_from_usage(gpu_usage, _last_metrics["gpu_temp"])

    metrics = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage": cpu_usage,
        "gpu_usage": gpu_usage,
        "cpu_temp": cpu_temp,
        "gpu_temp": gpu_temp,
    }

    _last_metrics = metrics
    return metrics


def _fluctuate_value(value, minimum, maximum, max_percent_change):
    """Fluctuate a value by up to a percentage of its current amount."""
    change = value * random.uniform(-max_percent_change, max_percent_change)
    return int(min(maximum, max(minimum, value + change)))


def _temperature_from_usage(usage, last_temp):
    """Return a new temperature that follows usage, with limited fluctuation."""
    target_temp = TEMP_MIN + (usage / 100) * (TEMP_MAX - TEMP_MIN)
    percent_change = random.choice([0.10, 0.15])
    max_delta = last_temp * percent_change
    delta = target_temp - last_temp
    if abs(delta) > max_delta:
        delta = max_delta if delta > 0 else -max_delta
    temp = last_temp + delta + random.uniform(-1.5, 1.5)
    return int(min(TEMP_MAX, max(TEMP_MIN, temp)))


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

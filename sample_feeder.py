import time
import random
from datetime import datetime, timezone

import requests

BACKEND_URL = "http://localhost:8000"

NODES = ["living_room", "master_bedroom", "bathroom"]


def iso_now():
    return datetime.now(timezone.utc).isoformat()


def send_sensor_data():
    for node_id in NODES:
        base_temp = 22.0 + (0.5 if node_id == "bathroom" else 0.0)
        base_hum = 50.0 + (10.0 if node_id == "bathroom" else 0.0)

        temp1 = base_temp + random.uniform(-0.5, 0.5)
        temp2 = base_temp + random.uniform(-0.5, 0.5)
        hum1 = base_hum + random.uniform(-5.0, 5.0)
        hum2 = base_hum + random.uniform(-5.0, 5.0)

        mold_index = max(0.0, min(3.0, (hum1 - 60) / 10))  # fake formula
        drift_val = abs(hum1 - hum2)

        if mold_index >= 2.0:
            risk_level = 2
        elif mold_index >= 1.0:
            risk_level = 1
        else:
            risk_level = 0

        payload = {
            "type": "data",
            "node_id": node_id,
            "timestamp": iso_now(),
            "readings": {
                "sensor_1": {"temp": temp1, "hum": hum1},
                "sensor_2": {"temp": temp2, "hum": hum2},
                "mold_index": mold_index,
                "drift_val": drift_val,
            },
            "status": {
                "system_health": "OK",
                "risk_level": risk_level,
            },
        }

        try:
            requests.post(f"{BACKEND_URL}/api/data/", json=payload, timeout=5)
        except Exception as e:
            print("Failed to send sensor data:", e)


def send_health_report():
    nodes_info = {}
    for node_id in NODES:
        nodes_info[node_id] = {
            "status": "ONLINE",
            "sensors": "SYNCED" if node_id != "master_bedroom" else "DRIFT_WARNING",
        }

    payload = {
        "type": "health_report",
        "network": {
            "server_node": "ONLINE",
            "thread_mesh": "CONNECTED",
        },
        "nodes": nodes_info,
    }

    try:
        requests.post(f"{BACKEND_URL}/api/health/", json=payload, timeout=5)
    except Exception as e:
        print("Failed to send health report:", e)


def send_random_alert():
    if random.random() < 0.3:
        payload = {
            "type": "alert",
            "node_id": "bathroom",
            "alert_level": "CRITICAL",
            "message": "Mold Growth Risk High. Ventilation Required Immediately.",
            "metrics": {
                "mold_index": round(random.uniform(2.5, 3.0), 2),
                "humidity": round(random.uniform(80, 95), 1),
            },
        }
        try:
            requests.post(f"{BACKEND_URL}/api/alerts/", json=payload, timeout=5)
        except Exception as e:
            print("Failed to send alert:", e)


def send_random_error():
    if random.random() < 0.2:
        payload = {
            "type": "error",
            "node_id": "master_bedroom",
            "error_code": "ERR_SENSOR_DISCONNECT",
            "details": {
                "component": "Sensor 2 (DHT20)",
                "value_received": 0.0,
                "message": "I2C Bus Timeout - Check wiring.",
            },
        }
        try:
            requests.post(f"{BACKEND_URL}/api/errors/", json=payload, timeout=5)
        except Exception as e:
            print("Failed to send error:", e)


def main():
    print("Starting sample feeder. Press Ctrl+C to stop.")
    while True:
        send_sensor_data()
        send_health_report()
        send_random_alert()
        send_random_error()
        time.sleep(5)


if __name__ == "__main__":
    main()

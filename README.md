# Mold Prevention DashBoard

AERIS is a prototype real-time monitoring system for indoor mold risk.  
It ingests JSON messages from wireless sensor nodes (or emulators), stores them in a database, and visualizes system state and environmental risk in a web dashboard.

This repo contains:

- A **FastAPI backend** with SQLite storage  
- A **Streamlit-based web dashboard** for visualization  
- A **sample data generator** (`sample_feeder.py`) so you can test everything without real hardware  

Later, this backend can be integrated with real sensor nodes (e.g., nRF52840 + Zephyr + Thread mesh via a Raspberry Pi border router).

---

## 1. Features

- Real-time **room overview**:
  - Temperature & humidity per room
  - Mold index & risk level (green / amber / red cards)
  - Online / offline status
- **System health** (engineering view):
  - Network status
  - Sensor drift status per node
- **Alerts & errors**:
  - Critical mold-risk alerts
  - Error logs (e.g., sensor disconnects)
- Historical charts:
  - Temperature, humidity, and mold index trends per node
- Designed to be fed by:
  - Sample generator (`sample_feeder.py`)
  - Existing Python emulators
  - Real USB/serial messages from embedded nodes

---

## 2. Technology Stack

**Backend**

- [FastAPI](https://fastapi.tiangolo.com/) – REST API
- [Uvicorn](https://www.uvicorn.org/) – ASGI server
- [SQLAlchemy](https://www.sqlalchemy.org/) – ORM
- **SQLite** – Embedded database

**Frontend (Dashboard)**

- [Streamlit](https://streamlit.io/) – Web UI
- [Plotly](https://plotly.com/python/) – Interactive charts
- [Pandas](https://pandas.pydata.org/) – Data handling

**Utilities**

- `requests` – HTTP client from Python  
- `python-dateutil` – Date/time parsing  

---

## 3. Architecture Overview

### 3.1 System View

```text
+---------------------------+      +---------------------------+
|   Sensor Node (e.g.      |      |   Sensor Node (e.g.      |
|   nRF52840 + Zephyr)     | ...  |   nRF52840 + Zephyr)     |
| - Temp/Humidity Sensor   |      | - Temp/Humidity Sensor   |
| - Mold Index Calculation |      | - Mold Index Calculation |
+-------------+------------+      +-------------+------------+
              |                              |
              +----------- Thread Mesh ------+
                              |
                              v
                  +------------------------+
                  | Border Router (Pi 5)  |
                  | - nRF52840 dongle     |
                  | - OpenThread daemon   |
                  +----------+-----------+
                             |
                     (USB / Serial / UDP)
                             |
                             v
               +-------------------------------+
               |        FastAPI Backend        |
               | - JSON message ingestion      |
               | - SQLite (sensor & alert DB)  |
               | - REST endpoints for dashboard|
               +-------------------------------+
                             |
                             v
               +-------------------------------+
               |    Streamlit Web Dashboard    |
               | - Environment Overview        |
               | - System Health               |
               | - Alerts & Errors             |
               +-------------------------------+
```

For now, the “sensor nodes” are simulated by `sample_feeder.py`, which sends JSON packets to the backend.

---

## 4. Data Model & Message Types

The system expects messages in four JSON formats, distinguished by the `type` field.

### 4.1 Sensor Data (`type = "data"`)

Example:

```json
{
  "type": "data",
  "node_id": "living_room",
  "timestamp": "2025-12-01T12:34:56Z",
  "readings": {
    "sensor_1": { "temp": 22.1, "hum": 52.3 },
    "sensor_2": { "temp": 22.0, "hum": 53.0 },
    "mold_index": 0.8,
    "drift_val": 0.7
  },
  "status": {
    "system_health": "OK",
    "risk_level": 1
  }
}
```

Stored in the `sensor_data` table and used for:

- Room cards (latest values)  
- Historical charts  
- Risk-level coloring  

### 4.2 Alerts (`type = "alert"`)

Example:

```json
{
  "type": "alert",
  "node_id": "bathroom",
  "alert_level": "CRITICAL",
  "message": "Mold Growth Risk High. Ventilation Required Immediately.",
  "metrics": {
    "mold_index": 2.9,
    "humidity": 88.5
  }
}
```

Stored in the `alerts` table and shown in the “Alerts & Errors” tab.

### 4.3 System Health Reports (`type = "health_report"`)

Example:

```json
{
  "type": "health_report",
  "network": {
    "server_node": "ONLINE",
    "thread_mesh": "CONNECTED"
  },
  "nodes": {
    "living_room":   { "status": "ONLINE", "sensors": "SYNCED" },
    "master_bedroom":{ "status": "ONLINE", "sensors": "DRIFT_WARNING" }
  }
}
```

Stored in the `health_reports` table and used to populate the **System Health** tab and the `nodes` table (status/drift).

### 4.4 Errors (`type = "error"`)

Example:

```json
{
  "type": "error",
  "node_id": "master_bedroom",
  "error_code": "ERR_SENSOR_DISCONNECT",
  "details": {
    "component": "Sensor 2 (DHT20)",
    "value_received": 0.0,
    "message": "I2C Bus Timeout - Check wiring."
  }
}
```

Stored in the `error_logs` table and shown in the “Alerts & Errors” tab.

---

## 5. Repository Structure

```text
aeris_project/
├─ requirements.txt          # Python dependencies
├─ sample_feeder.py          # Sample data generator (no hardware required)
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py             # FastAPI entrypoint
│  │  ├─ database.py         # SQLite setup & Session
│  │  ├─ models.py           # SQLAlchemy models
│  │  ├─ schemas.py          # Pydantic schemas
│  │  ├─ deps.py             # DB dependency
│  │  └─ routers/
│  │     ├─ data.py          # /api/data
│  │     ├─ alerts.py        # /api/alerts
│  │     ├─ errors.py        # /api/errors
│  │     ├─ health.py        # /api/health
│  │     └─ nodes.py         # /api/nodes (overview)
└─ dashboard/
   └─ app.py                 # Streamlit dashboard
```

---

## 6. Getting Started (Local Simulation)

### 6.1 Prerequisites

- Python 3.10+  
- pip  

### 6.2 Setup & Installation

```bash
# Clone the repository
git clone <YOUR_REPO_URL> aeris_project
cd aeris_project

# Create a virtual environment
python -m venv .venv

# Activate (Command Prompt on Windows)
.venv\Scripts\activate.bat

# or PowerShell (if execution policy allows)
# .venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 6.3 Run the Backend

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Check it in your browser: <http://127.0.0.1:8000/docs>  
You should see the FastAPI Swagger UI.

### 6.4 Run the Sample Data Feeder

In a **second terminal** (same folder, activate venv again):

```bash
.venv\Scripts\activate.bat
python sample_feeder.py
```

This script will periodically send:

- Sensor data for `living_room`, `master_bedroom`, `bathroom`  
- Health reports  
- Random alerts and error messages  

### 6.5 Run the Dashboard

In a **third terminal**:

```bash
.venv\Scripts\activate.bat
streamlit run dashboard/app.py
```

Streamlit will open a browser window (usually <http://localhost:8501>) with:

- **Environment Overview** tab – colored room cards + history charts  
- **System Health** tab – network & node state table  
- **Alerts & Errors** tab – recent alerts and error logs  

---

## 7. Integrating Real Sensor Data

Once you have real sensor nodes and a border router, you can replace the sample generator with a **serial ingestor**.

### 7.1 Expected Real-Data Flow

1. **Embedded node** (Zephyr) periodically:
   - Reads temperature & humidity sensors  
   - Computes mold index (e.g., Viitanen model)  
   - Formats a JSON packet like the `type:"data"` example above  
2. Node sends this JSON over:
   - UART / USB serial  
   - or UDP/TCP via Thread / IPv6  
3. The **gateway (Raspberry Pi)** runs a Python script that:
   - Reads each JSON line from the serial port or socket  
   - `json.loads` it  
   - POSTs it to the appropriate FastAPI endpoint  

### 7.2 Example Serial Ingestor (placeholder)

You can create a script like this to replace `sample_feeder.py`:

```python
# serial_ingestor.py
import json
import requests
import serial  # pip install pyserial

BACKEND_URL = "http://localhost:8000"
SERIAL_PORT = "COM3"       # or /dev/ttyACM0 on Linux
BAUD_RATE = 115200

def handle_packet(pkt):
    t = pkt.get("type")
    if t == "data":
        requests.post(f"{BACKEND_URL}/api/data/", json=pkt, timeout=5)
    elif t == "alert":
        requests.post(f"{BACKEND_URL}/api/alerts/", json=pkt, timeout=5)
    elif t == "health_report":
        requests.post(f"{BACKEND_URL}/api/health/", json=pkt, timeout=5)
    elif t == "error":
        requests.post(f"{BACKEND_URL}/api/errors/", json=pkt, timeout=5)
    else:
        print("Unknown type:", t)

def main():
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print(f"Reading from {SERIAL_PORT}...")
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                continue
            try:
                pkt = json.loads(line)
                handle_packet(pkt)
            except json.JSONDecodeError:
                print("Invalid JSON:", line)

if __name__ == "__main__":
    main()
```

If your embedded firmware prints **one JSON object per line**, this script will forward them to the backend in the same format as `sample_feeder.py`.

---

## 8. Real-Time Aspects (Optional – for RTS/Academic Reports)

This project is suitable for real-time analysis:

- Define an end-to-end deadline  

  _Example: “Critical mold-risk alert must appear on the dashboard within 5 seconds of detection on the node.”_

- Measure timestamps at:
  - Sensor sampling / mold computation (on node)  
  - Packet transmission & reception at gateway  
  - DB insertion in the backend  
  - Dashboard refresh (Streamlit polling interval)  

- Use those measurements to:
  - Estimate worst-case latency  
  - Check if deadlines are met under load  
  - Discuss schedulability and jitter from network & processing  

These metrics can be documented in a separate report for coursework or research.

---

## 9. Roadmap

- [ ] Replace `sample_feeder.py` with real serial/UDP ingestor  
- [ ] Add authentication for dashboard access  
- [ ] Add configuration UI (alert thresholds, node management)  
- [ ] Deploy as Docker containers (backend + dashboard) on Raspberry Pi  
- [ ] Integrate with real OpenThread network (nRF52840 dongle + RPi)  

---

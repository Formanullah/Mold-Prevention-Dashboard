from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any


class SensorDataCreate(BaseModel):
    type: str = "data"
    node_id: str
    timestamp: datetime
    readings: Dict[str, Any]
    status: Dict[str, Any]


class AlertCreate(BaseModel):
    type: str = "alert"
    node_id: str
    alert_level: str
    message: str
    metrics: Dict[str, Any]


class HealthReportCreate(BaseModel):
    type: str = "health_report"
    network: Dict[str, Any]
    nodes: Dict[str, Any]


class ErrorCreate(BaseModel):
    type: str = "error"
    node_id: str
    error_code: str
    details: Dict[str, Any]

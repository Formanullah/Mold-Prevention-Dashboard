from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, unique=True, index=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="ONLINE")
    drift_status = Column(String, default="SYNCED")


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    temp_1 = Column(Float)
    hum_1 = Column(Float)
    temp_2 = Column(Float)
    hum_2 = Column(Float)
    mold_index = Column(Float)
    drift_val = Column(Float)
    system_health = Column(String)
    risk_level = Column(Integer)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    alert_level = Column(String)
    message = Column(String)
    metrics = Column(JSON)


class HealthReport(Base):
    __tablename__ = "health_reports"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    network = Column(JSON)
    nodes = Column(JSON)


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    error_code = Column(String)
    details = Column(JSON)

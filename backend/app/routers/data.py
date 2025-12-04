from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/", status_code=201)
def ingest_data(payload: schemas.SensorDataCreate, db: Session = Depends(get_db)):
    r1 = payload.readings.get("sensor_1", {})
    r2 = payload.readings.get("sensor_2", {})

    db_obj = models.SensorData(
        node_id=payload.node_id,
        timestamp=payload.timestamp,
        temp_1=r1.get("temp"),
        hum_1=r1.get("hum"),
        temp_2=r2.get("temp"),
        hum_2=r2.get("hum"),
        mold_index=payload.readings.get("mold_index"),
        drift_val=payload.readings.get("drift_val"),
        system_health=payload.status.get("system_health"),
        risk_level=payload.status.get("risk_level"),
    )
    db.add(db_obj)

    node = db.query(models.Node).filter_by(node_id=payload.node_id).first()
    if not node:
        node = models.Node(node_id=payload.node_id)
        db.add(node)

    node.last_seen = payload.timestamp
    node.status = "ONLINE"

    db.commit()
    return {"ok": True}


@router.get("/history")
def get_history(
    node_id: str = Query(...),
    limit: int = Query(200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    q = (
        db.query(models.SensorData)
        .filter(models.SensorData.node_id == node_id)
        .order_by(models.SensorData.timestamp.desc())
        .limit(limit)
    )
    rows = q.all()
    rows = list(reversed(rows))
    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "node_id": r.node_id,
            "temp_1": r.temp_1,
            "hum_1": r.hum_1,
            "temp_2": r.temp_2,
            "hum_2": r.hum_2,
            "mold_index": r.mold_index,
            "drift_val": r.drift_val,
            "system_health": r.system_health,
            "risk_level": r.risk_level,
        }
        for r in rows
    ]

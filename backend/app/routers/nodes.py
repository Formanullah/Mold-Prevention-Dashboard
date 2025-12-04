from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .. import models
from ..deps import get_db

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    now = datetime.utcnow()
    offline_threshold = timedelta(minutes=15)

    nodes = db.query(models.Node).all()
    result = []

    for node in nodes:
        latest_data = (
            db.query(models.SensorData)
            .filter(models.SensorData.node_id == node.node_id)
            .order_by(models.SensorData.timestamp.desc())
            .first()
        )
        if not latest_data:
            continue

        node_status = node.status
        if node.last_seen and now - node.last_seen > offline_threshold:
            node_status = "OFFLINE"

        result.append(
            {
                "node_id": node.node_id,
                "last_seen": node.last_seen.isoformat() if node.last_seen else None,
                "status": node_status,
                "drift_status": node.drift_status,
                "temp_1": latest_data.temp_1,
                "hum_1": latest_data.hum_1,
                "temp_2": latest_data.temp_2,
                "hum_2": latest_data.hum_2,
                "mold_index": latest_data.mold_index,
                "risk_level": latest_data.risk_level,
            }
        )

    return result

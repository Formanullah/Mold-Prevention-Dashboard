from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/", status_code=201)
def ingest_alert(payload: schemas.AlertCreate, db: Session = Depends(get_db)):
    alert = models.Alert(
        node_id=payload.node_id,
        alert_level=payload.alert_level,
        message=payload.message,
        metrics=payload.metrics,
    )
    db.add(alert)

    node = db.query(models.Node).filter_by(node_id=payload.node_id).first()
    if not node:
        node = models.Node(node_id=payload.node_id)
        db.add(node)
    node.last_seen = datetime.utcnow()

    db.commit()
    return {"ok": True}


@router.get("/recent")
def recent_alerts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    q = (
        db.query(models.Alert)
        .order_by(models.Alert.timestamp.desc())
        .limit(limit)
    )
    alerts = q.all()
    return [
        {
            "id": a.id,
            "node_id": a.node_id,
            "timestamp": a.timestamp.isoformat(),
            "alert_level": a.alert_level,
            "message": a.message,
            "metrics": a.metrics,
        }
        for a in alerts
    ]

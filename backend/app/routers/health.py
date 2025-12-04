from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/api/health", tags=["health"])


@router.post("/", status_code=201)
def ingest_health(payload: schemas.HealthReportCreate, db: Session = Depends(get_db)):
    hr = models.HealthReport(
        network=payload.network,
        nodes=payload.nodes,
    )
    db.add(hr)

    for node_id, info in payload.nodes.items():
        node = db.query(models.Node).filter_by(node_id=node_id).first()
        if not node:
            node = models.Node(node_id=node_id)
            db.add(node)
        node.status = info.get("status", node.status)
        node.drift_status = info.get("sensors", node.drift_status)

    db.commit()
    return {"ok": True}


@router.get("/latest")
def latest_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    hr = (
        db.query(models.HealthReport)
        .order_by(models.HealthReport.timestamp.desc())
        .first()
    )
    if not hr:
        return {}
    return {
        "timestamp": hr.timestamp.isoformat(),
        "network": hr.network,
        "nodes": hr.nodes,
    }

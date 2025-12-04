from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/api/errors", tags=["errors"])


@router.post("/", status_code=201)
def ingest_error(payload: schemas.ErrorCreate, db: Session = Depends(get_db)):
    err = models.ErrorLog(
        node_id=payload.node_id,
        error_code=payload.error_code,
        details=payload.details,
    )
    db.add(err)

    node = db.query(models.Node).filter_by(node_id=payload.node_id).first()
    if not node:
        node = models.Node(node_id=payload.node_id)
        db.add(node)
    node.last_seen = datetime.utcnow()

    db.commit()
    return {"ok": True}


@router.get("/recent")
def recent_errors(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    q = (
        db.query(models.ErrorLog)
        .order_by(models.ErrorLog.timestamp.desc())
        .limit(limit)
    )
    errors = q.all()
    return [
        {
            "id": e.id,
            "node_id": e.node_id,
            "timestamp": e.timestamp.isoformat(),
            "error_code": e.error_code,
            "details": e.details,
        }
        for e in errors
    ]

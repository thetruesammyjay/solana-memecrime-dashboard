from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from ..db.models import Alert, TokenAlert, WalletAlert
from ..services.alert_engine import AlertEngine

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/")
async def get_active_alerts(
    alert_type: Optional[str] = None,
    timeframe: Optional[int] = 24,
    db: Session = Depends(get_db)
):
    """Get all active alerts"""
    query = db.query(Alert).filter(Alert.is_active == True)
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    if timeframe:
        cutoff = datetime.utcnow() - timedelta(hours=timeframe)
        query = query.filter(Alert.created_at >= cutoff)
    
    return query.order_by(Alert.created_at.desc()).all()

@router.post("/trigger")
async def trigger_alert_check(
    alert_engine: AlertEngine = Depends()
):
    """Manually trigger alert checks"""
    triggered = await alert_engine.check_all_alerts()
    return {"triggered_alerts": len(triggered)}

@router.put("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Mark an alert as resolved"""
    alert = db.query(Alert).get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = False
    alert.resolved_at = datetime.utcnow()
    db.commit()
    return {"status": "resolved"}
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timedelta
from typing import Optional
import uuid

from app.database import get_db
from app.models.dj import DJ
from app.models.venue import Venue
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionResponse, SessionValidation

router = APIRouter()

# Configurazione durata sessione
SESSION_DURATION_HOURS = 6

# ==================== HELPER FUNCTIONS ====================

def set_session_cookie(response: Response, session_id: uuid.UUID):
    """Setta il cookie di sessione con configurazione sicura"""
    from app.core.config import settings
    
    # In development i cookie sono meno restrittivi per testare da telefono
    is_development = settings.ENVIRONMENT == "development"
    
    response.set_cookie(
        key="session_id",
        value=str(session_id),
        httponly=True,
        secure=not is_development,  # True solo con HTTPS
        samesite="lax" if is_development else "strict",  # ← Meno restrittivo in dev
        max_age=30
        # max_age=SESSION_DURATION_HOURS * 3600
    )

def get_session_from_cookie(request: Request) -> Optional[uuid.UUID]:
    """Recupera session_id dal cookie della request"""
    session_id_str = request.cookies.get("session_id")
    if not session_id_str:
        return None
    try:
        return uuid.UUID(session_id_str)
    except ValueError:
        return None

# ==================== ENDPOINTS ====================

@router.get("/qr-flow/{qr_code_id}")
def qr_flow(qr_code_id: str, request: Request, db: DBSession = Depends(get_db)):
    """
    Endpoint unificato per gestione flusso QR.
    Decide se redirect, welcome o error.
    """
    # 1. Verifica DJ esiste
    dj = db.query(DJ).filter(DJ.qr_code_id == qr_code_id).first()
    if not dj:
        return {"action": "error", "error_type": "qr_not_found"}
    
    # 2. Verifica venue attivo
    active_venue = db.query(Venue).filter(
        Venue.dj_id == dj.id,
        Venue.active == True
    ).first()
    
    if not active_venue:
        return {"action": "error", "error_type": "no_active_venue"}
    
    # 3. Controlla sessione esistente
    session_id = get_session_from_cookie(request)
    
    if session_id:
        session = db.query(Session).filter(
            Session.id == session_id,
            Session.dj_id == dj.id,
            Session.venue_id == active_venue.id,
            Session.expires_at > datetime.utcnow()
        ).first()
        
        if session:
            session.last_activity = datetime.utcnow()
            db.commit()
            return {"action": "redirect", "session_id": str(session.id)}
    
    # 4. Nessuna sessione valida → Welcome
    return {
        "action": "welcome",
        "data": {
            "dj": {
                "id": dj.id,
                "stage_name": dj.stage_name,
                "qr_code_id": dj.qr_code_id
            },
            "active_venue": {
                "id": active_venue.id,
                "name": active_venue.name,
                "address": active_venue.address
            }
        }
    }

@router.post("/create/{qr_code_id}")
def create_session(
    qr_code_id: str, 
    request: Request, 
    response: Response,
    db: DBSession = Depends(get_db)
):
    """
    Crea nuova sessione dopo accettazione utente.
    """
    # Verifica DJ e venue (stesso codice del qr-flow)
    dj = db.query(DJ).filter(DJ.qr_code_id == qr_code_id).first()
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trovato")
    
    active_venue = db.query(Venue).filter(
        Venue.dj_id == dj.id,
        Venue.active == True
    ).first()
    
    if not active_venue:
        raise HTTPException(status_code=400, detail="Nessun locale attivo")
    
    # Crea nuova sessione
    new_session = Session(
        dj_id=dj.id,
        venue_id=active_venue.id,
        expires_at=datetime.utcnow() + timedelta(hours=SESSION_DURATION_HOURS),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    # Setta cookie
    set_session_cookie(response, new_session.id)
    
    return {"session_id": str(new_session.id)}

@router.get("/validate")
def validate_session(request: Request, db: DBSession = Depends(get_db)):
    """
    Valida una sessione esistente.
    Usato dal bot assistant per verificare l'accesso.
    
    Validazioni:
    1. Presenza cookie session_id
    2. Esistenza sessione in database
    3. Sessione non scaduta (< 6 ore)
    4. Venue della sessione ancora attivo
    
    Returns:
        dict: Dati sessione valida con info DJ e venue
        
    Raises:
        HTTPException: 401 per sessioni invalide/scadute, 400 per venue inattivo
    """
    session_id = get_session_from_cookie(request)
    
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Sessione non trovata. Scansiona il QR code del DJ"
        )
    
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Sessione non trovata. Scansiona il QR code."
        )
    
    # Verifica scadenza
    if session.is_expired:
        raise HTTPException(
            status_code=401,
            detail="Sessione scaduta (6 ore). Scansiona nuovamente il QR code."
        )
    
    # Verifica che il venue della sessione sia ancora attivo
    venue = db.query(Venue).filter(Venue.id == session.venue_id).first()
    
    if not venue or not venue.active:
        raise HTTPException(
            status_code=400,
            detail="Il locale non è più attivo."
        )
    
    # Aggiorna last_activity
    session.last_activity = datetime.utcnow()
    db.commit()
    
    dj = db.query(DJ).filter(DJ.id == session.dj_id).first()
    
    # Ritorna dati sessione valida
    return {
        "valid": True,
        "session_id": str(session.id),
        "dj": {
            "id": dj.id, 
            "stage_name": dj.stage_name, 
            "qr_code_id": dj.qr_code_id
        },
        "active_venue": {
            "id": venue.id, 
            "name": venue.name, 
            "address": venue.address
        },
        "expires_at": session.expires_at,
        "remaining_minutes": session.remaining_minutes
    }

@router.get("/cleanup")
def cleanup_expired_sessions(db: DBSession = Depends(get_db)):
    """
    Endpoint per cleanup manuale delle sessioni scadute.
    In produzione dovrebbe essere chiamato da un cronjob.
    """
    
    deleted_count = db.query(Session).filter(
        Session.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    
    return {
        "message": f"{deleted_count} sessioni scadute eliminate",
        "deleted": deleted_count
    }
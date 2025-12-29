from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session as DBSession
from typing import List
from datetime import datetime
import uuid

from app.database import get_db
from app.models.booking import Booking
from app.models.venue import Venue
from app.models.dj import DJ
from app.models.session import Session
from app.schemas.booking import BookingCreate, BookingResponse, BookingWithVenue
from app.api.deps import get_current_dj

from app.core.config import settings

router = APIRouter()

# ==================== DJ ENDPOINTS ====================

@router.get("", response_model=List[BookingWithVenue])
def get_bookings(
    venue_id: int = Query(..., description="ID del locale"),
    current_dj: DJ = Depends(get_current_dj),
    db: DBSession = Depends(get_db)
):
    """
    Ottieni tutte le prenotazioni per un locale specifico (DJ view).
    Include sia prenotazioni utenti che quelle manuali del DJ.
    """
    # Verifica che il locale appartenga al DJ
    venue = db.query(Venue).filter(
        Venue.id == venue_id,
        Venue.dj_id == current_dj.id
    ).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Locale non trovato")
    
    # Ottieni TUTTE le prenotazioni del locale
    bookings = db.query(Booking).filter(
        Booking.venue_id == venue_id
    ).order_by(Booking.created_at.desc()).all()
    
    return [
        BookingWithVenue(
            id=b.id,
            user_name=b.user_name,
            song=b.song,
            key=b.key,
            status=b.status,
            venue_name=venue.name,
            session_id=b.session_id,  # ✅ Incluso
            created_at=b.created_at
        )
        for b in bookings
    ]

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    current_dj: DJ = Depends(get_current_dj),
    db: DBSession = Depends(get_db)
):
    """
    Crea una prenotazione manuale (dal DJ).
    session_id sarà NULL per prenotazioni DJ.
    """
    venue = db.query(Venue).filter(
        Venue.id == booking_data.venue_id,
        Venue.dj_id == current_dj.id
    ).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Locale non trovato")
    
    new_booking = Booking(
        user_name=booking_data.user_name,
        song=booking_data.song,
        key=booking_data.key,
        status="pending",
        venue_id=venue.id,
        session_id=None  # ✅ NULL per prenotazioni DJ
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking

@router.post("/{booking_id}/accept")
def accept_booking(
    booking_id: int,
    current_dj: DJ = Depends(get_current_dj),
    db: DBSession = Depends(get_db)
):
    """Accetta una prenotazione"""
    booking = db.query(Booking).join(Venue).filter(
        Booking.id == booking_id,
        Venue.dj_id == current_dj.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    
    booking.status = "accepted"
    db.commit()
    
    return {"message": "Prenotazione accettata", "status": "accepted"}

@router.post("/{booking_id}/reject")
def reject_booking(
    booking_id: int,
    current_dj: DJ = Depends(get_current_dj),
    db: DBSession = Depends(get_db)
):
    """Rifiuta una prenotazione"""
    booking = db.query(Booking).join(Venue).filter(
        Booking.id == booking_id,
        Venue.dj_id == current_dj.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    
    booking.status = "rejected"
    db.commit()
    
    return {"message": "Prenotazione rifiutata", "status": "rejected"}

@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    current_dj: DJ = Depends(get_current_dj),
    db: DBSession = Depends(get_db)
):
    """Elimina una prenotazione"""
    booking = db.query(Booking).join(Venue).filter(
        Booking.id == booking_id,
        Venue.dj_id == current_dj.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    
    db.delete(booking)
    db.commit()
    
    return {"message": "Prenotazione eliminata con successo"}

@router.delete("/venue/{venue_id}")
def delete_venue_bookings(
    venue_id: int,
    current_dj: DJ = Depends(get_current_dj),
    db: DBSession = Depends(get_db)
):
    """Elimina TUTTE le prenotazioni di un locale"""
    venue = db.query(Venue).filter(
        Venue.id == venue_id,
        Venue.dj_id == current_dj.id
    ).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Locale non trovato")
    
    deleted_count = db.query(Booking).filter(Booking.venue_id == venue_id).delete()
    db.commit()
    
    return {
        "message": "Tutte le prenotazioni eliminate",
        "deleted": deleted_count
    }

@router.delete("/all")
def delete_all_bookings(
    current_dj: DJ = Depends(get_current_dj),
    db: DBSession = Depends(get_db)
):
    """
    Elimina TUTTE le prenotazioni di TUTTI i locali del DJ.
    
    Returns:
        dict: Numero totale di prenotazioni eliminate
    """
    # Elimina tutte le prenotazioni dei venue del DJ
    deleted_count = db.query(Booking).join(Venue).filter(
        Venue.dj_id == current_dj.id
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": "Tutte le prenotazioni dei vari locali sono state eliminate",
        "deleted": deleted_count,
        "dj_stage_name": current_dj.stage_name
    }

# ==================== USER ENDPOINTS ====================

def get_session_from_cookie(request: Request) -> uuid.UUID | None:
    """Helper per recuperare session_id dal cookie"""
    session_id_str = request.cookies.get("session_id")
    if not session_id_str:
        return None
    try:
        return uuid.UUID(session_id_str)
    except ValueError:
        return None

def get_current_session(request: Request, db: DBSession = Depends(get_db)) -> Session:
    """Dependency per validare sessione utente"""
    session_id = get_session_from_cookie(request)
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Sessione non trovata. Scansiona il QR code."
        )
    
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session or session.is_expired:
        raise HTTPException(
            status_code=401,
            detail="Sessione scaduta. Scansiona nuovamente il QR code."
        )
    
    # Aggiorna last_activity
    session.last_activity = datetime.utcnow()
    db.commit()
    
    return session

@router.post("/user", status_code=status.HTTP_201_CREATED)
def create_user_booking(
    user_name: str,
    song: str,
    key: str = "0",
    session: Session = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """
    Crea una prenotazione da parte di un utente via bot assistant.
    Richiede sessione valida e venue attivo.
    
    Validazioni:
    1. Rate limiting dinamico: basato su impostazioni DJ
    2. Venue della sessione ancora attivo
    3. Canzone esistente nel catalogo del DJ
    4. Sessione non scaduta
    """
    # 1. Rate limiting dinamico basato su impostazioni DJ
    dj = db.query(DJ).filter(DJ.id == session.dj_id).first()
    max_bookings = dj.max_bookings_per_user if dj else 999
    
    # Solo applica il limite se non è "nessun limite" (999)
    if max_bookings < 999 and session.booking_count >= max_bookings:
        raise HTTPException(status_code=429, detail="Limite prenotazioni raggiunto")
    
    # 2. Verifica che il venue della sessione sia ancora attivo
    venue = db.query(Venue).filter(Venue.id == session.venue_id).first()
    
    if not venue or not venue.active:
        raise HTTPException(
            status_code=400,
            detail="Il locale della tua sessione non è più attivo. Il DJ ha cambiato locale. Scansiona nuovamente il QR code."
        )
    
    # 3. Verifica canzone nel catalogo
    from app.models.song import Song
    song_exists = db.query(Song).filter(
        Song.dj_id == session.dj_id,
        Song.file_name == song
    ).first()
    
    if not song_exists:
        raise HTTPException(status_code=404, detail="Canzone non trovata nel catalogo")
    
    # 4. Crea prenotazione per il venue della sessione
    new_booking = Booking(
        user_name=user_name,
        song=song,
        key=key,
        status="pending",
        venue_id=session.venue_id,
        session_id=session.id
    )
    
    db.add(new_booking)
    session.booking_count += 1
    db.commit()
    db.refresh(new_booking)
    
    # Calcola remaining_bookings (se nessun limite, mostra 999)
    remaining_bookings = max_bookings - session.booking_count if max_bookings < 999 else 999
    
    return {
        "id": new_booking.id,
        "user_name": new_booking.user_name,
        "song": new_booking.song,
        "key": new_booking.key,
        "status": "pending",
        "venue_name": venue.name,
        "session_id": str(session.id),
        "created_at": new_booking.created_at,
        "message": "Prenotazione inviata! Il DJ la confermerà a breve.",
        "remaining_bookings": remaining_bookings,
        "max_bookings": max_bookings
    }

@router.get("/user/my-bookings")
def get_user_bookings(
    session: Session = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """
    Ottieni le prenotazioni dell'utente nella sessione corrente.
    Utilizza session_id per filtrare solo le prenotazioni dell'utente.
    """
    # Rate limiting dinamico basato su impostazioni DJ
    dj = db.query(DJ).filter(DJ.id == session.dj_id).first()
    max_bookings = dj.max_bookings_per_user if dj else 999
    
    # Recupera venue attivo
    active_venue = db.query(Venue).filter(
        Venue.dj_id == session.dj_id,
        Venue.active == True
    ).first()
    
    # Calcola remaining_slots (se nessun limite, mostra 999)
    remaining_slots = max_bookings - session.booking_count if max_bookings < 999 else 999
    
    if not active_venue:
        return {
            "bookings": [],
            "remaining_slots": remaining_slots,
            "message": "Nessun locale attivo"
        }
    
    # Filtra per session_id invece che per created_at
    bookings = db.query(Booking).filter(
        Booking.session_id == session.id,
        Booking.venue_id == active_venue.id
    ).order_by(Booking.created_at.desc()).all()
    
    return {
        "bookings": [
            {
                "id": b.id,
                "user_name": b.user_name,
                "song": b.song,
                "key": b.key,
                "status": b.status,
                "created_at": b.created_at,
                "can_delete": b.status == "pending"
            }
            for b in bookings
        ],
        "remaining_slots": remaining_slots,
        "venue": {"id": active_venue.id, "name": active_venue.name}
    }

@router.delete("/user/{booking_id}")
def delete_user_booking(
    booking_id: int,
    session: Session = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """
    Permette all'utente di cancellare una sua prenotazione.
    
    Validazioni:
    1. Prenotazione esistente
    2. Prenotazione appartiene alla sessione corrente
    3. Venue della sessione ancora attivo
    
    Args:
        booking_id: ID della prenotazione da cancellare
        session: Sessione utente validata
        db: Database session
        
    Returns:
        dict: Messaggio di conferma + booking_count aggiornato
        
    Raises:
        HTTPException:
            - 404: Prenotazione non trovata o non appartiene all'utente
            - 400: Venue non più attivo
    """
    # Rate limiting dinamico basato su impostazioni DJ
    dj = db.query(DJ).filter(DJ.id == session.dj_id).first()
    max_bookings = dj.max_bookings_per_user if dj else 999
    
    # Verifica venue ancora attivo
    venue = db.query(Venue).filter(Venue.id == session.venue_id).first()
    if not venue or not venue.active:
        raise HTTPException(
            status_code=400,
            detail="Il locale non è più attivo. Non puoi modificare le prenotazioni."
        )
    
    # Trova prenotazione della sessione corrente
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.session_id == session.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Prenotazione non trovata o non appartiene alla tua sessione"
        )
    
    # Elimina prenotazione
    db.delete(booking)
    
    # Decrementa contatore sessione
    session.booking_count = max(0, session.booking_count - 1)
    
    db.commit()
    
    # Calcola remaining_bookings (se nessun limite, mostra 999)
    remaining_bookings = max_bookings - session.booking_count if max_bookings < 999 else 999
    
    return {
        "message": "Prenotazione cancellata con successo",
        "booking_id": booking_id,
        "remaining_bookings": remaining_bookings,
        "available_slots": session.booking_count
    }
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.venue import Venue
from app.models.dj import DJ
from app.schemas.venue import VenueCreate, VenueUpdate, VenueResponse
from app.api.deps import get_current_dj

router = APIRouter()

@router.get("", response_model=List[VenueResponse])
def get_venues(
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Ottieni tutti i locali del DJ"""
    # venues = db.query(Venue).filter(Venue.dj_id == current_dj.id).all()
    venues = db.query(Venue).filter(
        Venue.dj_id == current_dj.id
    ).order_by(
        Venue.active.desc(),  # Prima i locali attivi
        Venue.name.asc()       # Poi ordine alfabetico
    ).all()
    return venues

@router.post("", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(
    venue_data: VenueCreate,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Crea un nuovo locale"""
    new_venue = Venue(
        name=venue_data.name,
        address=venue_data.address,
        capacity=venue_data.capacity,
        notes=venue_data.notes,
        dj_id=current_dj.id
    )
    
    db.add(new_venue)
    db.commit()
    db.refresh(new_venue)
    
    return new_venue

@router.put("/{venue_id}", response_model=VenueResponse)
def update_venue(
    venue_id: int,
    venue_data: VenueUpdate,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Aggiorna un locale"""
    venue = db.query(Venue).filter(
        Venue.id == venue_id,
        Venue.dj_id == current_dj.id
    ).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Locale non trovato")
    
    if venue_data.name is not None:
        venue.name = venue_data.name
    if venue_data.address is not None:
        venue.address = venue_data.address
    if venue_data.capacity is not None:
        venue.capacity = venue_data.capacity
    if venue_data.notes is not None:
        venue.notes = venue_data.notes
    
    db.commit()
    db.refresh(venue)
    
    return venue

@router.post("/{venue_id}/toggle")
def toggle_venue(
    venue_id: int,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Attiva/Disattiva un locale (serata)"""
    venue = db.query(Venue).filter(
        Venue.id == venue_id,
        Venue.dj_id == current_dj.id
    ).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Locale non trovato")
    
    # Se stiamo attivando questo locale, disattiva tutti gli altri
    if not venue.active:
        db.query(Venue).filter(Venue.dj_id == current_dj.id).update({"active": False})
    
    venue.active = not venue.active
    db.commit()
    
    return {"active": venue.active, "message": "Serata attivata" if venue.active else "Serata disattivata"}

@router.delete("/{venue_id}")
def delete_venue(
    venue_id: int,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Elimina un locale"""
    venue = db.query(Venue).filter(
        Venue.id == venue_id,
        Venue.dj_id == current_dj.id
    ).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Locale non trovato")
    
    db.delete(venue)
    db.commit()
    
    return {"message": "Locale eliminato con successo"}
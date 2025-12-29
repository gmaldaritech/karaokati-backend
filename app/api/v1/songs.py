from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.song import Song
from app.models.dj import DJ
from app.models.session import Session
from app.schemas.song import SongCreate, SongBulkCreate, SongResponse, SongListResponse
from app.api.deps import get_current_dj

from fastapi import Request, Query
from datetime import datetime
import uuid

from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd

router = APIRouter()

@router.get("", response_model=SongListResponse)
def get_songs(
    search: Optional[str] = Query(None, description="Cerca nel nome della canzone"),
    page: int = Query(1, ge=1, description="Numero pagina"),
    per_page: int = Query(50, ge=1, le=1000, description="Canzoni per pagina"),
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Ottieni tutte le canzoni del catalogo con paginazione e ricerca"""
    
    # Query base con ordinamento alfabetico
    query = db.query(Song).filter(Song.dj_id == current_dj.id).order_by(Song.file_name)
    
    # Applica filtro ricerca se presente
    if search:
        query = query.filter(Song.file_name.ilike(f"%{search}%"))
    
    # Gestione count ottimizzata
    if search:
        # Per ricerche: limita count per performance
        max_search_results = 1000
        
        # Conta fino a max_search_results + 1 per sapere se ci sono di più
        count_query = query.limit(max_search_results + 1)
        limited_results = count_query.all()
        
        if len(limited_results) > max_search_results:
            total = max_search_results
            limited = True
        else:
            total = len(limited_results) 
            limited = False
    else:
        # Catalogo completo: count normale (veloce su indice dj_id)
        total = query.count()
        limited = False
    
    # Calcola numero pagine
    pages = (total + per_page - 1) // per_page
    
    # Protezione contro pagine eccessive
    max_page = min(page, pages) if pages > 0 else 1
    
    # Recupera solo la pagina richiesta
    songs = query.offset((max_page - 1) * per_page).limit(per_page).all()
    
    return {
        "songs": songs,
        "total": total,
        "pages": pages,
        "current_page": max_page,
        "limited": limited
    }

@router.post("", response_model=SongResponse, status_code=status.HTTP_201_CREATED)
def add_song(
    song_data: SongCreate,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Aggiungi una singola canzone al catalogo"""
    new_song = Song(
        file_name=song_data.file_name,
        dj_id=current_dj.id
    )
    
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    
    return new_song

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def bulk_add_songs(
    bulk_data: SongBulkCreate,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Aggiungi multiple canzoni in una volta (importazione massiva)"""
    songs = [Song(file_name=song, dj_id=current_dj.id) for song in bulk_data.songs]
    db.bulk_save_objects(songs)
    db.commit()
    
    return {
        "message": f"{len(bulk_data.songs)} canzoni aggiunte con successo",
        "count": len(bulk_data.songs)
    }

@router.delete("/{song_id}")
def delete_song(
    song_id: int,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Elimina una canzone dal catalogo"""
    song = db.query(Song).filter(
        Song.id == song_id,
        Song.dj_id == current_dj.id
    ).first()
    
    if not song:
        raise HTTPException(status_code=404, detail="Canzone non trovata")
    
    db.delete(song)
    db.commit()
    
    return {"message": "Canzone eliminata con successo"}

@router.delete("")
def clear_catalog(
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Elimina TUTTE le canzoni dal catalogo"""
    deleted_count = db.query(Song).filter(Song.dj_id == current_dj.id).delete()
    db.commit()
    
    return {
        "message": "Catalogo eliminato con successo",
        "deleted": deleted_count
    }

@router.get("/public/{qr_code_id}")
def get_public_catalog(
    qr_code_id: str,
    search: Optional[str] = None,
    limit: int = Query(50, le=1000),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Ottieni il catalogo pubblico di un DJ (per bot assistant).
    Richiede sessione valida.
    
    Questo endpoint permette agli utenti di cercare canzoni
    nel catalogo del DJ per fare prenotazioni.
    """
    
    # 1. Valida sessione (opzionale ma consigliato per sicurezza)
    session_id_str = request.cookies.get("session_id") if request else None

    print(session_id_str)
    
    if session_id_str:
        try:
            session_id = uuid.UUID(session_id_str)
            session = db.query(Session).filter(
                Session.id == session_id,
                Session.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                raise HTTPException(
                    status_code=401,
                    detail="Sessione non valida. Scansiona il QR code."
                )
        except ValueError:
            raise HTTPException(status_code=401, detail="Session ID non valido")
    
    # 2. Trova DJ
    dj = db.query(DJ).filter(DJ.qr_code_id == qr_code_id).first()
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trovato")
    
    # 3. Query canzoni
    query = db.query(Song).filter(Song.dj_id == dj.id)
    
    if search:
        query = query.filter(Song.file_name.ilike(f"%{search}%"))
    
    songs = query.limit(limit).all()
    
    # 4. Ritorna solo i nomi dei file (non gli ID)
    return {
        "songs": [song.file_name for song in songs],
        "total": db.query(Song).filter(Song.dj_id == dj.id).count(),
        "dj_name": dj.stage_name
    }

@router.post("/generate-excel")
async def generate_excel_from_song_list(
    songs: dict,  # {"songs": ["song1.mp3", "song2.mp3", ...]}
    current_dj: DJ = Depends(get_current_dj)
):
    """
    Genera file Excel da lista di canzoni.
    Usato per "Genera Catalogo Automatico".
    """
    song_list = songs.get("songs", [])
    
    if not song_list:
        raise HTTPException(status_code=400, detail="Lista canzoni vuota")
    
    # Crea DataFrame
    df = pd.DataFrame({'titolo': song_list})
    
    # Genera Excel in memoria
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    # Ritorna file per download
    return StreamingResponse(
        BytesIO(excel_buffer.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=catalogo_{current_dj.stage_name}.xlsx"
        }
    )
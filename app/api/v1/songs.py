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

import re
from sqlalchemy import func, or_, and_, case, desc

FUZZY_THRESHOLD = 0.40  # più alto = più rigido

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
    """Aggiungi multiple canzoni in una volta (salta quelle già presenti)"""
    existing = {
        r[0] for r in db.query(Song.file_name).filter(Song.dj_id == current_dj.id).all()
    }

    to_add = []
    seen = set()
    for name in bulk_data.songs:
        name = name.strip()
        if not name or name in existing or name in seen:
            continue
        seen.add(name)
        to_add.append(Song(file_name=name, dj_id=current_dj.id))

    if to_add:
        db.bulk_save_objects(to_add)
        db.commit()

    skipped = len(bulk_data.songs) - len(to_add)

    return {
        "message": f"{len(to_add)} canzoni aggiunte con successo",
        "count": len(to_add),
        "skipped": skipped
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

@router.get("/export")
def export_catalog(
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """Scarica l'intero catalogo del DJ come Excel (una colonna: 'Titolo Canzone')"""
    rows = db.query(Song.file_name).filter(
        Song.dj_id == current_dj.id
    ).order_by(Song.file_name).all()

    if not rows:
        raise HTTPException(status_code=404, detail="Catalogo vuoto")

    df = pd.DataFrame({"Titolo Canzone": [r[0] for r in rows]})

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=catalogo_karaokati.xlsx"}
    )

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

    Ricerca per parole:
    - parole di 4+ lettere: obbligatorie, devono essere contenute nel nome
      del file oppure assomigliare molto a una sua parte (strict_word_similarity)
    - parole di 1-3 lettere: solo bonus di ordinamento (obbligatorie solo se
      la ricerca è composta esclusivamente da parole corte)
    - risultati ordinati per rilevanza
    """

    # 1. Valida sessione (opzionale ma consigliato per sicurezza)
    session_id_str = request.cookies.get("session_id") if request else None

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

    if search and search.strip():
        phrase = search.strip().lower()
        tokens = [t for t in re.split(r"\s+", phrase) if t]
        long_tokens = [t for t in tokens if len(t) >= 4]
        short_tokens = [t for t in tokens if len(t) < 4]

        conditions = []
        score = 0

        # Parole lunghe: obbligatorie (contenute oppure simili)
        for t in long_tokens:
            like = Song.file_name.ilike(f"%{t}%")
            sim = func.strict_word_similarity(t, Song.file_name)
            conditions.append(or_(like, sim >= FUZZY_THRESHOLD))
            score = score + sim + case((like, 1.0), else_=0.0)

        # Parole corte: bonus se ci sono parole lunghe, altrimenti filtro
        for t in short_tokens:
            like = Song.file_name.ilike(f"%{t}%")
            if long_tokens:
                score = score + case((like, 0.5), else_=0.0)
            else:
                conditions.append(like)
                score = score + case((like, 1.0), else_=0.0)

        # Bonus per somiglianza con la frase intera (aiuta a ordinare i pareggi)
        score = score + func.word_similarity(phrase, Song.file_name)

        query = query.filter(and_(*conditions)).order_by(desc(score), Song.file_name)

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
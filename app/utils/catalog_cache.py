"""
Cache in memoria del numero di canzoni nel catalogo di ogni DJ.

Il totale viene restituito a ogni ricerca pubblica ma cambia solo quando il DJ
modifica il catalogo: invece di fare un COUNT a ogni richiesta lo teniamo in
memoria per qualche minuto e lo invalidiamo quando il catalogo cambia.

Con più worker/istanze ognuno ha la sua cache: l'invalidazione vale solo per il
processo che ha ricevuto la modifica, gli altri si riallineano entro CACHE_TTL.
"""
import threading
import time

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.song import Song

CACHE_TTL = 300  # secondi

_cache: dict[int, tuple[int, float]] = {}
_lock = threading.Lock()


def get_catalog_count(db: Session, dj_id: int) -> int:
    now = time.monotonic()
    with _lock:
        hit = _cache.get(dj_id)
    if hit and hit[1] > now:
        return hit[0]

    count = db.query(func.count()).select_from(Song).filter(Song.dj_id == dj_id).scalar() or 0
    with _lock:
        _cache[dj_id] = (count, now + CACHE_TTL)
    return count


def invalidate_catalog_count(dj_id: int) -> None:
    with _lock:
        _cache.pop(dj_id, None)

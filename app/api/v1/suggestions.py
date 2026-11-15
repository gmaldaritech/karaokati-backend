import threading
from datetime import datetime, date
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.email_service import send_email

router = APIRouter()

MAX_SUGGESTION_LENGTH = 2000  # caratteri
MAX_SUGGESTIONS_PER_DAY = 20  # in totale, per tutti gli utenti

# Contatore giornaliero in memoria: si azzera a mezzanotte (ora italiana)
# e a ogni riavvio del server. Con un solo worker vale per tutto il backend.
_ROME = ZoneInfo("Europe/Rome")
_daily_lock = threading.Lock()
_daily_day: date | None = None
_daily_count = 0


def _take_daily_slot() -> bool:
    """Riserva un invio per oggi. Ritorna False se il limite è già raggiunto."""
    global _daily_day, _daily_count
    today = datetime.now(_ROME).date()
    with _daily_lock:
        if _daily_day != today:
            _daily_day = today
            _daily_count = 0
        if _daily_count >= MAX_SUGGESTIONS_PER_DAY:
            return False
        _daily_count += 1
        return True


class SuggestionRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=MAX_SUGGESTION_LENGTH)

@router.post("/send-suggestion")
def send_suggestion(suggestion: SuggestionRequest):
    """Invia suggerimento via email"""

    # Fuori dal try: altrimenti l'except qui sotto trasformerebbe il 429 in 500
    if not _take_daily_slot():
        print(f"Limite giornaliero suggerimenti raggiunto ({MAX_SUGGESTIONS_PER_DAY})")
        raise HTTPException(
            status_code=429,
            detail="Oggi abbiamo ricevuto molti suggerimenti. Riprova domani, grazie!"
        )

    try:
        # Email a te stesso con il suggerimento
        email_subject = "Nuovo Suggerimento Karaokati"
        email_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #9333ea, #ec4899); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                <h1>🎤 Nuovo Suggerimento Karaokati</h1>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #9333ea;">
                <h3 style="color: #333; margin-top: 0;">Contenuto del Suggerimento:</h3>
                <div style="background: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">
                    <p style="color: #555; line-height: 1.6; white-space: pre-wrap;">{suggestion.content}</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                <p>Inviato tramite la pagina Suggerimenti di Karaokati</p>
                <p>Data: {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        
        # 🆕 Metti qui la TUA email
        success = send_email(
            to_email="admin@karaokati.com",
            subject=email_subject,
            html_body=email_body
        )
        
        if success:
            return {"message": "Suggerimento inviato con successo", "sent": True}
        else:
            raise HTTPException(status_code=500, detail="Errore nell'invio dell'email")
            
    except Exception as e:
        print(f"Errore invio suggerimento: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")
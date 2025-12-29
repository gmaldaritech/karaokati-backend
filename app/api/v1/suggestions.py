from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.core.email_service import send_email

router = APIRouter()

class SuggestionRequest(BaseModel):
    content: str

@router.post("/send-suggestion")
async def send_suggestion(suggestion: SuggestionRequest):
    """Invia suggerimento via email"""
    
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
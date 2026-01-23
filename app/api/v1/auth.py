from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.dj import DJ
from app.schemas.dj import DJRegister, DJLogin, DJUpdate, PasswordChange, TokenResponse, DJResponse, PasswordResetRequest, PasswordReset 
from app.core.security import verify_password, get_password_hash, create_access_token, generate_qr_code_id
from app.core.email_service import generate_verification_token, send_verification_email, send_reset_password_email, send_admin_registration_notification, send_admin_password_reset_notification
from app.api.deps import get_current_dj
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(dj_data: DJRegister, request: Request, db: Session = Depends(get_db)):
    # Verifica se email esiste già 
    existing_dj = db.query(DJ).filter(DJ.email == dj_data.email).first()
    
    if existing_dj:
        if existing_dj.email_verified:
            # Email verificata: blocca registrazione
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email già registrata e verificata"
            )
        else:
            # Email NON verificata: elimina vecchia occorrenza
            db.delete(existing_dj)
            db.commit()
    
    # Genera token di verifica
    verification_token = generate_verification_token()
    qr_code_id = generate_qr_code_id(dj_data.stage_name)
    
    # Crea il DJ (NON VERIFICATO)
    new_dj = DJ(
        full_name=dj_data.full_name,
        stage_name=dj_data.stage_name,
        email=dj_data.email,
        phone=dj_data.phone,
        password_hash=get_password_hash(dj_data.password),
        qr_code_id=qr_code_id,
        email_verified=False,
        email_verification_token=verification_token
    )
    
    db.add(new_dj)
    db.commit()
    db.refresh(new_dj)
    
    # Invia email di verifica
    email_sent = send_verification_email(new_dj.email, verification_token, request)
    send_admin_registration_notification(new_dj.email, new_dj.stage_name, new_dj.full_name, verification_token, request)
    
    return {
        "message": "Registrazione completata! Controlla la tua email per confermare l'account.",
        "email_sent": email_sent,
        "dj": DJResponse(
            id=new_dj.id,
            full_name=new_dj.full_name,
            stage_name=new_dj.stage_name,
            email=new_dj.email,
            phone=new_dj.phone,
            qr_code_id=new_dj.qr_code_id,
            email_verified=new_dj.email_verified,
            max_bookings_per_user=new_dj.max_bookings_per_user
        ),
        "token": None,  # Non diamo token fino alla verifica
        "requires_verification": True
    }

@router.post("/login", response_model=TokenResponse)
def login(credentials: DJLogin, db: Session = Depends(get_db)):
    dj = db.query(DJ).filter(DJ.email == credentials.email).first()
    
    if not dj or not verify_password(credentials.password, dj.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide"
        )
    
    # 🆕 Controlla se email è verificata
    if not dj.email_verified:
        raise HTTPException(
            status_code=400,
            detail="Email non ancora verificata. Controlla la tua posta."
        )
    
    token = create_access_token({"dj_id": dj.id})
    
    return {
        "token": token,
        "dj": DJResponse(
            id=dj.id,
            full_name=dj.full_name,
            stage_name=dj.stage_name,
            email=dj.email,
            phone=dj.phone,
            qr_code_id=dj.qr_code_id,
            email_verified=dj.email_verified,
            max_bookings_per_user=dj.max_bookings_per_user
        )
    }

@router.post("/logout")
def logout(current_dj: DJ = Depends(get_current_dj)):
    """
    Logout del DJ corrente.
    Invalida il token JWT lato client.
    
    Args:
        current_dj: DJ autenticato (per validare token)
        
    Returns:
        dict: Messaggio di conferma logout
        
    Note:
        - JWT stateless: invalidazione gestita dal frontend
        - Frontend deve rimuovere token da localStorage
        - Endpoint utile per conferma logout e logging
    """
    return {
        "message": "Logout completato con successo",
        "dj_id": current_dj.id,
        "stage_name": current_dj.stage_name
    }

@router.post("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Conferma email con token"""
    dj = db.query(DJ).filter(DJ.email_verification_token == token).first()
    
    if not dj:
        raise HTTPException(
            status_code=404,
            detail="Token di verifica non valido o scaduto"
        )
    
    # Attiva l'account
    dj.email_verified = True
    dj.email_verification_token = None
    db.commit()
    
    # Crea token JWT
    # access_token = create_access_token({"dj_id": dj.id})
    access_token = None
    return {
        "message": "Email verificata con successo!",
        "token": access_token,
        "dj": DJResponse(
            id=dj.id,
            full_name=dj.full_name,
            stage_name=dj.stage_name,
            email=dj.email,
            phone=dj.phone,
            qr_code_id=dj.qr_code_id,
            email_verified=dj.email_verified,
            max_bookings_per_user=dj.max_bookings_per_user
        )
    }

@router.post("/request-password-reset")
def request_password_reset(
    request_data: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Richiede reset password"""
    dj = db.query(DJ).filter(DJ.email == request_data.email).first()
    
    if not dj:
        # Non rivelare se email esiste o no
        return {"message": "Se l'email esiste, riceverai le istruzioni per il reset"}
    
    # Genera token reset
    reset_token = generate_verification_token()
    reset_expires = datetime.utcnow() + timedelta(hours=1)
    
    dj.password_reset_token = reset_token
    dj.password_reset_expires = reset_expires
    db.commit()
    
    # Invia email
    email_sent = send_reset_password_email(dj.email, reset_token, request)
    send_admin_password_reset_notification(dj.email, dj.stage_name, reset_token, request)
    
    return {
        "message": "Se l'email esiste, riceverai le istruzioni per il reset",
        "email_sent": email_sent
    }

@router.post("/reset-password")
def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Reset password con token"""
    dj = db.query(DJ).filter(
        DJ.password_reset_token == reset_data.token,
        DJ.password_reset_expires > datetime.utcnow()
    ).first()
    
    if not dj:
        raise HTTPException(
            status_code=400,
            detail="Token non valido o scaduto"
        )
    
    # Aggiorna password
    dj.password_hash = get_password_hash(reset_data.new_password)
    dj.password_reset_token = None
    dj.password_reset_expires = None
    db.commit()
    
    return {"message": "Password resettata con successo"}

# ========== NUOVI ENDPOINT PROFILO ==========
@router.get("/me", response_model=DJResponse)
def get_current_dj_info(current_dj: DJ = Depends(get_current_dj)):
    """
    Ottieni informazioni del DJ corrente autenticato.
    
    Returns:
        DJResponse: Dati completi del profilo DJ
        
    Note:
        - Non include password_hash per sicurezza
        - Mostra QR code ID per condivisione
    """
    return DJResponse(
        id=current_dj.id,
        full_name=current_dj.full_name,
        stage_name=current_dj.stage_name,
        email=current_dj.email,
        phone=current_dj.phone,
        qr_code_id=current_dj.qr_code_id,
        email_verified=current_dj.email_verified,
        max_bookings_per_user=current_dj.max_bookings_per_user
    )

@router.put("/me", response_model=DJResponse)
def update_current_dj(
    dj_update: DJUpdate,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """
    Aggiorna informazioni del DJ corrente.
    
    Args:
        dj_update: Dati da aggiornare (solo campi forniti)
        current_dj: DJ autenticato
        db: Database session
        
    Returns:
        DJResponse: Dati aggiornati del DJ
        
    Raises:
        HTTPException: 400 se email già esistente
        
    Note:
        - Email deve rimanere univoca
        - QR code ID non modificabile
        - Password richiede endpoint separato
    """
    # Verifica email univoca se fornita
    if dj_update.email and dj_update.email != current_dj.email:
        existing_dj = db.query(DJ).filter(
            DJ.email == dj_update.email,
            DJ.id != current_dj.id
        ).first()
        
        if existing_dj:
            raise HTTPException(
                status_code=400,
                detail="Email già utilizzata da altro DJ"
            )
    
    # Aggiorna solo campi forniti
    if dj_update.full_name is not None:
        current_dj.full_name = dj_update.full_name
    if dj_update.stage_name is not None:
        current_dj.stage_name = dj_update.stage_name
    if dj_update.email is not None:
        current_dj.email = dj_update.email
    if dj_update.phone is not None:
        current_dj.phone = dj_update.phone
    if dj_update.max_bookings_per_user is not None:
        current_dj.max_bookings_per_user = dj_update.max_bookings_per_user
    
    db.commit()
    db.refresh(current_dj)
    
    return DJResponse(
        id=current_dj.id,
        full_name=current_dj.full_name,
        stage_name=current_dj.stage_name,
        email=current_dj.email,
        phone=current_dj.phone,
        qr_code_id=current_dj.qr_code_id,
        email_verified=current_dj.email_verified,
        max_bookings_per_user=current_dj.max_bookings_per_user
    )

@router.put("/change-password")
def change_password(
    password_data: PasswordChange,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """
    Cambia password del DJ corrente.
    
    Args:
        password_data: Password attuale e nuova
        current_dj: DJ autenticato
        db: Database session
        
    Returns:
        dict: Messaggio di conferma
        
    Raises:
        HTTPException: 400 se password attuale errata
        
    Note:
        - Richiede conferma password attuale
        - Nuova password viene hashata con bcrypt
    """
    # Verifica password attuale
    if not verify_password(password_data.current_password, current_dj.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Password attuale non corretta"
        )
    
    # Aggiorna con nuova password
    current_dj.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password modificata con successo"}

@router.post("/resend-verification")
def resend_verification(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Reinvia email di verifica"""
    email = request_data.get("email")
    
    dj = db.query(DJ).filter(
        DJ.email == email,
        DJ.email_verified == False
    ).first()
    
    if not dj:
        raise HTTPException(404, "Account non trovato o già verificato")
    
    # Reinvia email con stesso token
    email_sent = send_verification_email(dj.email, dj.email_verification_token)
    
    return {
        "resent": email_sent,
        "message": "Email reinviata con successo"
    }

# @router.delete("/delete-account")
# def delete_account(
#     current_dj: DJ = Depends(get_current_dj),
#     db: Session = Depends(get_db)
# ):
#     """
#     Elimina definitivamente l'account del DJ corrente.
    
#     Args:
#         current_dj: DJ autenticato
#         db: Database session
        
#     Returns:
#         dict: Messaggio di conferma eliminazione
        
#     Note:
#         - Eliminazione a cascata di venue, songs, bookings, sessions
#         - IRREVERSIBILE: tutti i dati vengono persi
#         - Richiede solo autenticazione JWT
#     """
#     # Salva dati per response
#     dj_id = current_dj.id
#     stage_name = current_dj.stage_name
    
#     # Elimina DJ (cascade eliminerà tutto il resto)
#     db.delete(current_dj)
#     db.commit()
    
#     return {
#         "message": "Account eliminato definitivamente",
#         "deleted_dj_id": dj_id,
#         "stage_name": stage_name,
#         "note": "Tutti i dati associati sono stati eliminati permanentemente"
#     }

@router.delete("/delete-account")
def delete_account(
    request: Request,
    current_dj: DJ = Depends(get_current_dj),
    db: Session = Depends(get_db)
):
    """
    Elimina definitivamente l'account del DJ corrente.
    
    Args:
        current_dj: DJ autenticato
        request: HTTP request per email URL dinamici
        db: Database session
        
    Returns:
        dict: Messaggio di conferma eliminazione
        
    Note:
        - Eliminazione a cascata di venue, songs, bookings, sessions
        - IRREVERSIBILE: tutti i dati vengono persi
        - Invia email di conferma all'utente e all'admin
    """
    from app.core.email_service import send_account_deletion_email, send_admin_account_deletion_notification
    
    # Salva dati per email prima dell'eliminazione
    dj_id = current_dj.id
    stage_name = current_dj.stage_name
    dj_email = current_dj.email
    full_name = current_dj.full_name
    
    # Elimina DJ (cascade eliminerà tutto il resto)
    db.delete(current_dj)
    db.commit()
    
    # 🆕 Invia email di conferma
    send_account_deletion_email(dj_email, stage_name, full_name, request)
    send_admin_account_deletion_notification(dj_email, stage_name, full_name, request)
    
    return {
        "message": "Account eliminato definitivamente",
        "deleted_dj_id": dj_id,
        "stage_name": stage_name,
        "email_sent": True,
        "note": "Tutti i dati associati sono stati eliminati permanentemente"
    }
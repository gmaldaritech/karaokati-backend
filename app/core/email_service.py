import secrets
import smtplib
from email.message import EmailMessage
import ssl
from datetime import datetime

# 🆕 Import dei template
from app.core.email_templates import (
    verification_email_template,
    reset_password_email_template,
    account_deletion_email_template,
    admin_registration_notification_template,
    admin_password_reset_notification_template,
    admin_account_deletion_notification_template
)

def generate_verification_token():
    """Genera token sicuro per verifiche"""
    return secrets.token_urlsafe(32)

def get_frontend_url(request=None, path=""):
    """Genera URL frontend dinamico basato su request o config"""
    from app.core.config import settings
    
    if request and hasattr(request, 'headers'):
        frontend_origin = request.headers.get('x-frontend-origin')
        if frontend_origin:
            print(f"{frontend_origin}{path}")
            return f"{frontend_origin}{path}"
    
    print(f"{settings.FRONTEND_URL}{path}")
    return f"{settings.FRONTEND_URL}{path}"

def send_verification_email(email: str, token: str, request=None):
    """Invia email di verifica"""
    from app.core.config import settings
    
    verification_url = get_frontend_url(request, f"/verify-email/{token}")
    terms_url = get_frontend_url(request, "/terms")
    
    # 🆕 Usa template invece di HTML inline
    subject, html_body = verification_email_template(verification_url, terms_url)
    
    return send_email(email, subject, html_body)

def send_reset_password_email(email: str, token: str, request=None):
    """Invia email di reset password"""
    from app.core.config import settings
    
    reset_url = get_frontend_url(request, f"/reset-password/{token}")
    terms_url = get_frontend_url(request, "/terms")
    
    # 🆕 Usa template invece di HTML inline
    subject, html_body = reset_password_email_template(reset_url, terms_url)
    
    return send_email(email, subject, html_body)

def send_account_deletion_email(email: str, stage_name: str, full_name: str, request=None):
    """Invia email di conferma cancellazione account all'utente"""
    terms_url = get_frontend_url(request, "/terms")
    
    # 🆕 Usa template invece di HTML inline
    subject, html_body = account_deletion_email_template(stage_name, full_name, terms_url)
    
    return send_email(email, subject, html_body)

def send_admin_registration_notification(dj_email: str, stage_name: str, full_name: str, verification_token: str, request=None):
    """Invia notifica admin per nuova registrazione"""
    from app.core.config import settings
    
    verification_url = get_frontend_url(request, f"/verify-email/{verification_token}")
    
    # 🆕 Usa template invece di HTML inline
    subject, html_body = admin_registration_notification_template(
        dj_email, stage_name, full_name, verification_token, verification_url
    )
    
    admin_email = settings.SMTP_USER
    return send_email(admin_email, subject, html_body)

def send_admin_password_reset_notification(dj_email: str, stage_name: str, reset_token: str, request=None):
    """Invia notifica admin per reset password"""
    from app.core.config import settings
    
    reset_url = get_frontend_url(request, f"/reset-password/{reset_token}")
    
    # 🆕 Usa template invece di HTML inline
    subject, html_body = admin_password_reset_notification_template(
        dj_email, stage_name, reset_token, reset_url
    )
    
    admin_email = settings.SMTP_USER
    return send_email(admin_email, subject, html_body)

def send_admin_account_deletion_notification(dj_email: str, stage_name: str, full_name: str, request=None):
    """Invia notifica admin per cancellazione account"""
    from app.core.config import settings
    
    # 🆕 Usa template invece di HTML inline
    subject, html_body = admin_account_deletion_notification_template(
        dj_email, stage_name, full_name
    )
    
    admin_email = settings.SMTP_USER
    return send_email(admin_email, subject, html_body)

def send_email(to_email: str, subject: str, html_body: str):
    """Funzione generica per invio email usando EmailMessage"""
    from app.core.config import settings
    
    try:
        # Crea messaggio
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = to_email
        msg.set_content(html_body, subtype='html')
        
        # Configurazione SSL/TLS
        context = ssl.create_default_context()
        
        if settings.SMTP_PORT == 465:
            # Connessione SSL
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context) as server:
                if settings.SMTP_USER:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Connessione TLS (porta 587)
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls(context=context)
                if settings.SMTP_USER:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        
        print(f"Email inviata con successo a {to_email}")
        return True
        
    except Exception as e:
        print(f"Errore invio email a {to_email}: {e}")
        return False
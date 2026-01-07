# app/core/email_service.py
import secrets
import smtplib
from email.message import EmailMessage
import ssl
from datetime import datetime
import time

def generate_verification_token():
    """Genera token sicuro per verifiche"""
    return secrets.token_urlsafe(32)

def send_verification_email(email: str, token: str):
    """Invia email di verifica"""
    from app.core.config import settings
    
    verification_url = f"{settings.FRONTEND_URL}/VerifyEmail/{token}"
    terms_of_services_url = f"{settings.FRONTEND_URL}/TermsOfService"
    
    #subject = "🔥 Attiva il tuo account Karaokati"
    subject = "Attiva il tuo account - Karaokati"
    html_body = f"""
        <!DOCTYPE html>
    <html lang="it">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verifica Email - Karaokati</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #111827;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #111827; padding: 40px 20px;">
        <tr>
        <td align="center">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%;">

            <!-- Card Principale -->
            <tr>
                <td>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(180deg, rgba(88, 28, 135, 0.3), rgba(17, 24, 39, 0.9)); border: 1px solid rgba(147, 51, 234, 0.3); border-radius: 24px; overflow: hidden;">
                    
                    <!-- Header Gradient -->
                    <tr>
                    <td style="background: linear-gradient(135deg, #9333ea, #ec4899); padding: 30px; text-align: center;">
                        <table role="presentation" cellspacing="0" cellpadding="0" align="center">
                        <tr>
                            <td style="background-color: rgba(255,255,255,0.2); border-radius: 50%; padding: 20px;">
                            <img src="https://img.icons8.com/fluency/64/ffffff/new-post.png" alt="Email" width="48" height="48" style="display: block;">
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>

                    <!-- Contenuto -->
                    <tr>
                    <td style="padding: 40px 30px;">
                        <h1 style="color: #ffffff; font-size: 26px; font-weight: bold; margin: 0 0 10px 0; text-align: center;">
                        Benvenuto su Karaokati
                        </h1>
                        <p style="color: #9ca3af; font-size: 16px; margin: 0 0 30px 0; text-align: center;">
                        Verifica il tuo indirizzo email per iniziare
                        </p>

                        <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                        Ciao! 👋
                        </p>
                        <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                        Grazie per esserti registrato su <strong style="color: #c084fc;">Karaokati</strong>, la piattaforma per DJ karaoke professionisti.
                        </p>
                        <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 30px 0;">
                        Per completare la registrazione e attivare il tuo account, clicca sul pulsante qui sotto:
                        </p>

                        <!-- CTA Button -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                            <td align="center" style="padding: 10px 0 30px 0;">
                            <a href="{verification_url}" style="display: inline-block; background: linear-gradient(135deg, #9333ea, #ec4899); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; padding: 16px 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(147, 51, 234, 0.4);">
                                ✉️ Verifica Email
                            </a>
                            </td>
                        </tr>
                        </table>

                        <!-- Info Box -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; margin-bottom: 20px;">
                        <tr>
                            <td style="padding: 20px;">
                            <p style="color: #86efac; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                                ⏰ Link valido per 24 ore
                            </p>
                            <p style="color: #4ade80; font-size: 13px; margin: 0; line-height: 1.5;">
                                Una volta verificato, potrai accedere a tutti i servizi della piattaforma.
                            </p>
                            </td>
                        </tr>
                        </table>

                        <!-- Welcome Box -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px;">
                        <tr>
                            <td style="padding: 20px;">
                            <p style="color: #93c5fd; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                                🎤 Cosa potrai fare:
                            </p>
                            <p style="color: #3b82f6; font-size: 13px; margin: 0; line-height: 1.5;">
                                Gestire locali, cataloghi musicali e prenotazioni karaoke in un unico posto.
                            </p>
                            </td>
                        </tr>
                        </table>

                        <!-- Alternative Link -->
                        <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 25px 0 0 0; text-align: center;">
                        Se il pulsante non funziona, copia e incolla questo link nel browser:
                        </p>
                        <p style="color: #a78bfa; font-size: 12px; word-break: break-all; margin: 10px 0 0 0; text-align: center;">
                        {verification_url}
                        </p>
                    </td>
                    </tr>

                    <!-- Divider -->
                    <tr>
                    <td style="padding: 0 30px;">
                        <div style="border-top: 1px solid rgba(147, 51, 234, 0.2);"></div>
                    </td>
                    </tr>

                    <!-- Footer Note -->
                    <tr>
                    <td style="padding: 25px 30px;">
                        <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 0; text-align: center;">
                        Se non hai creato un account su Karaokati, puoi ignorare questa email in sicurezza.
                        </p>
                    </td>
                    </tr>
                    <!-- Footer Note -->
                    <tr>
                    <td style="padding: 25px 30px;">
                        <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 0; text-align: center;">
                        Per qualsiasi problema, contattaci su <a href="mailto:admin@karaokati.com" style="color: #c084fc; text-decoration: none;">support@karaokati.com</a>
                        </p>
                    </td>
                    </tr>

                </table>
                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="padding: 30px 20px; text-align: center;">
                <p style="color: #6b7280; font-size: 13px; margin: 0 0 10px 0;">
                    © 2024 Karaokati. Tutti i diritti riservati.
                </p>
                <p style="color: #4b5563; font-size: 12px; margin: 0;">
                    <a href="{terms_of_services_url}" style="color: #9ca3af; text-decoration: none;">Termini di Servizio</a>
                </p>
                </td>
            </tr>

            </table>
        </td>
        </tr>
    </table>
    </body>
    </html>
    """
    # html_body = f"""
    # <html>
    # <head>
    #     <meta charset="UTF-8">
    # </head>
    # <body style="font-family: Arial, sans-serif; margin: 20px; color: #333;">
        
    #     <h2>Benvenuto su Karaokati</h2>
        
    #     <p>Ciao,</p>
        
    #     <p>Per accedere al tuo account, clicca questo link:</p>
        
    #     <p><a href="{verification_url}" style="color: #0066cc;">Accedi al tuo account</a></p>
        
    #     <p>Oppure copia questo indirizzo nel browser:</p>
    #     <p style="background: #f5f5f5; padding: 10px; word-break: break-all; font-size: 12px;">
    #         {verification_url}
    #     </p>
        
    #     <p>Il link funziona per 24 ore.</p>
        
    #     <hr>
        
    #     <p style="font-size: 12px; color: #666;">
    #         Karaokati - Piattaforma DJ<br>
    #         Se non hai richiesto questo messaggio, ignoralo.
    #     </p>
        
    # </body>
    # </html>
    # """
    # html_body = f"""
    # <html>
    # <head>
    #     <meta charset="UTF-8">
    # </head>
    # <body style="font-family: Arial, sans-serif; margin: 20px; color: #333;">
        
    #     <h2>Benvenuto su Karaokati</h2>
        
    #     <p>Ciao,</p>
        
    # </body>
    # </html>
    # """
    return send_email(email, subject, html_body)

def send_reset_password_email(email: str, token: str):
    """Invia email di reset password"""
    from app.core.config import settings
    
    reset_url = f"{settings.FRONTEND_URL}/ResetPassword/{token}"
    terms_of_services_url = f"{settings.FRONTEND_URL}/TermsOfService"
    
    # subject = "🔐 Reset Password - Karaokati"
    subject = "Reset Password - Karaokati"
    html_body = f"""
        <!DOCTYPE html>
    <html lang="it">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password - Karaokati</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #111827;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #111827; padding: 40px 20px;">
        <tr>
        <td align="center">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%;">
            
            <!-- Card Principale -->
            <tr>
                <td>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(180deg, rgba(88, 28, 135, 0.3), rgba(17, 24, 39, 0.9)); border: 1px solid rgba(147, 51, 234, 0.3); border-radius: 24px; overflow: hidden;">
                    
                    <!-- Header Gradient -->
                    <tr>
                    <td style="background: linear-gradient(135deg, #9333ea, #ec4899); padding: 30px; text-align: center;">
                        <table role="presentation" cellspacing="0" cellpadding="0" align="center">
                        <tr>
                            <td style="background-color: rgba(255,255,255,0.2); border-radius: 50%; padding: 20px;">
                            <img src="https://img.icons8.com/fluency/64/ffffff/lock.png" alt="Lock" width="48" height="48" style="display: block;">
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>

                    <!-- Contenuto -->
                    <tr>
                    <td style="padding: 40px 30px;">
                        <h1 style="color: #ffffff; font-size: 26px; font-weight: bold; margin: 0 0 10px 0; text-align: center;">
                        Reset della Password
                        </h1>
                        <p style="color: #9ca3af; font-size: 16px; margin: 0 0 30px 0; text-align: center;">
                        Hai richiesto di reimpostare la tua password
                        </p>

                        <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                        Ciao! 👋
                        </p>
                        <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                        Abbiamo ricevuto una richiesta per reimpostare la password del tuo account <strong style="color: #c084fc;">Karaokati</strong>.
                        </p>
                        <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 30px 0;">
                        Se sei stato tu, clicca sul pulsante qui sotto per creare una nuova password:
                        </p>

                        <!-- CTA Button -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                            <td align="center" style="padding: 10px 0 30px 0;">
                            <a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #9333ea, #ec4899); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; padding: 16px 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(147, 51, 234, 0.4);">
                                🔑 Reimposta Password
                            </a>
                            </td>
                        </tr>
                        </table>

                        <!-- Info Box Scadenza -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 12px; margin-bottom: 20px;">
                        <tr>
                            <td style="padding: 20px;">
                            <p style="color: #fde68a; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                                ⏰ Link temporaneo
                            </p>
                            <p style="color: #fbbf24; font-size: 13px; margin: 0; line-height: 1.5;">
                                Per motivi di sicurezza, questo link è valido solo per 1 ora.
                            </p>
                            </td>
                        </tr>
                        </table>

                        <!-- Security Warning Box -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px;">
                        <tr>
                            <td style="padding: 20px;">
                            <p style="color: #fca5a5; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                                🛡️ Non hai richiesto questo reset?
                            </p>
                            <p style="color: #ef4444; font-size: 13px; margin: 0; line-height: 1.5;">
                                Se non sei stato tu a fare questa richiesta, ignora questa email. La tua password rimarrà invariata e il tuo account è al sicuro.
                            </p>
                            </td>
                        </tr>
                        </table>

                        <!-- Alternative Link -->
                        <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 25px 0 0 0; text-align: center;">
                        Se il pulsante non funziona, copia e incolla questo link nel browser:
                        </p>
                        <p style="color: #a78bfa; font-size: 12px; word-break: break-all; margin: 10px 0 0 0; text-align: center;">
                        {reset_url}
                        </p>
                    </td>
                    </tr>

                    <!-- Divider -->
                    <tr>
                    <td style="padding: 0 30px;">
                        <div style="border-top: 1px solid rgba(147, 51, 234, 0.2);"></div>
                    </td>
                    </tr>

                    <!-- Footer Note -->
                    <tr>
                    <td style="padding: 25px 30px;">
                        <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 0; text-align: center;">
                        Per qualsiasi problema, contattaci su <a href="mailto:admin@karaokati.com" style="color: #c084fc; text-decoration: none;">support@karaokati.com</a>
                        </p>
                    </td>
                    </tr>

                </table>
                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="padding: 30px 20px; text-align: center;">
                <p style="color: #6b7280; font-size: 13px; margin: 0 0 10px 0;">
                    © 2024 Karaokati. Tutti i diritti riservati.
                </p>
                <p style="color: #4b5563; font-size: 12px; margin: 0;">
                    <a href="{terms_of_services_url}" style="color: #9ca3af; text-decoration: none;">Termini di Servizio</a>
                </p>
                </td>
            </tr>

            </table>
        </td>
        </tr>
    </table>
    </body>
    </html>
    """
    # html_body = f"""
    # <html>
    # <head>
    #     <meta charset="UTF-8">
    # </head>
    # <body style="font-family: Arial, sans-serif; margin: 20px; color: #333;">
        
    #     <h2>Reset password Karaokati</h2>
        
    #     <p>Ciao,</p>
        
    #     <p>Per reimpostare la tua password, clicca questo link:</p>
        
    #     <p><a href="{reset_url}" style="color: #0066cc;">Reimposta password</a></p>
        
    #     <p>Oppure copia questo indirizzo nel browser:</p>
    #     <p style="background: #f5f5f5; padding: 10px; word-break: break-all; font-size: 12px;">
    #         {reset_url}
    #     </p>
        
    #     <p>Il link funziona per 1 ora.</p>
        
    #     <hr>
        
    #     <p style="font-size: 12px; color: #666;">
    #         Karaokati - Piattaforma DJ<br>
    #         Se non hai richiesto questo messaggio, ignoralo.
    #     </p>
        
    # </body>
    # </html>
    # """
    
    return send_email(email, subject, html_body)

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

def send_admin_registration_notification(dj_email: str, stage_name: str, full_name: str, verification_token: str):
    """Invia notifica admin per nuova registrazione"""
    from app.core.config import settings
    
    verification_url = f"{settings.FRONTEND_URL}/VerifyEmail/{verification_token}"
    
    subject = "Nuova Registrazione - Karaokati"
    html_body = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nuova Registrazione DJ</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #111827;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #111827; padding: 40px 20px;">
        <tr>
        <td align="center">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%;">
            
            <tr>
                <td>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(180deg, rgba(88, 28, 135, 0.3), rgba(17, 24, 39, 0.9)); border: 1px solid rgba(147, 51, 234, 0.3); border-radius: 24px; overflow: hidden;">
                    
                    <!-- Header -->
                    <tr>
                    <td style="background: linear-gradient(135deg, #10b981, #059669); padding: 30px; text-align: center;">
                        <table role="presentation" cellspacing="0" cellpadding="0" align="center">
                        <tr>
                            <td style="background-color: rgba(255,255,255,0.2); border-radius: 50%; padding: 20px;">
                            <img src="https://img.icons8.com/fluency/64/ffffff/microphone.png" alt="Microphone" width="48" height="48" style="display: block;">
                            </td>
                        </tr>
                        </table>
                        <h1 style="color: white; margin: 15px 0 0 0; font-size: 24px;">🎤 Nuova Registrazione DJ</h1>
                    </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                    <td style="padding: 40px 30px;">
                        <h2 style="color: #ffffff; font-size: 20px; margin: 0 0 25px 0;">Dettagli Registrazione:</h2>
                        
                        <table style="width: 100%; border-collapse: collapse; background-color: rgba(88, 28, 135, 0.2); border-radius: 8px; padding: 20px;">
                            <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #c084fc; font-weight: 600;">Nome Completo:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #d1d5db;">{full_name}</td>
                            </tr>
                            <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #c084fc; font-weight: 600;">Stage Name:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #d1d5db;">{stage_name}</td>
                            </tr>
                            <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #c084fc; font-weight: 600;">Email:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #d1d5db;">{dj_email}</td>
                            </tr>
                            <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #c084fc; font-weight: 600;">Token Verifica:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #d1d5db; font-family: monospace; font-size: 11px; line-height: 1.4; word-break: break-all;">{verification_token}</td>
                            </tr>
                            <td style="padding: 12px 20px; color: #c084fc; font-weight: 600;">Timestamp:</td>
                            <td style="padding: 12px 20px; color: #d1d5db;">{datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')} UTC</td>
                            </tr>
                        </table>

                        <!-- URL Box -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; margin: 25px 0;">
                        <tr>
                            <td style="padding: 20px;">
                            <p style="color: #93c5fd; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                                🔗 Link di Verifica
                            </p>
                            <p style="color: #3b82f6; font-size: 12px; margin: 0; line-height: 1.5; word-break: break-all; font-family: monospace;">
                                {verification_url}
                            </p>
                            </td>
                        </tr>
                        </table>

                        <!-- Status Box -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; margin: 25px 0;">
                        <tr>
                            <td style="padding: 20px;">
                            <p style="color: #86efac; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                                📧 Stato Account
                            </p>
                            <p style="color: #4ade80; font-size: 13px; margin: 0; line-height: 1.5;">
                                Il DJ deve ancora verificare la sua email prima di poter accedere alla piattaforma.
                            </p>
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                    <td style="padding: 25px 30px; text-align: center; border-top: 1px solid rgba(147, 51, 234, 0.2);">
                        <p style="color: #6b7280; font-size: 12px; margin: 0;">
                        Notifica automatica dal sistema Karaokati Admin
                        </p>
                    </td>
                    </tr>

                </table>
                </td>
            </tr>

            </table>
        </td>
        </tr>
    </table>
    </body>
    </html>
    """
    
    admin_email = settings.SMTP_USER
    return send_email(admin_email, subject, html_body)

def send_admin_password_reset_notification(dj_email: str, stage_name: str, reset_token: str):
    """Invia notifica admin per reset password"""
    from app.core.config import settings
    
    reset_url = f"{settings.FRONTEND_URL}/ResetPassword/{reset_token}"
    
    subject = "Reset Password - Karaokati"
    html_body = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password Richiesto</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #111827;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #111827; padding: 40px 20px;">
        <tr>
        <td align="center">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%;">
            
            <tr>
                <td>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(180deg, rgba(88, 28, 135, 0.3), rgba(17, 24, 39, 0.9)); border: 1px solid rgba(147, 51, 234, 0.3); border-radius: 24px; overflow: hidden;">
                    
                    <!-- Header -->
                    <tr>
                    <td style="background: linear-gradient(135deg, #f59e0b, #ef4444); padding: 30px; text-align: center;">
                        <table role="presentation" cellspacing="0" cellpadding="0" align="center">
                        <tr>
                            <td style="background-color: rgba(255,255,255,0.2); border-radius: 50%; padding: 20px;">
                            <img src="https://img.icons8.com/fluency/64/ffffff/lock.png" alt="Lock" width="48" height="48" style="display: block;">
                            </td>
                        </tr>
                        </table>
                        <h1 style="color: white; margin: 15px 0 0 0; font-size: 24px;">🔒 Reset Password Richiesto</h1>
                    </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                    <td style="padding: 40px 30px;">
                        <h2 style="color: #ffffff; font-size: 20px; margin: 0 0 25px 0;">Dettagli Richiesta:</h2>
                        
                        <table style="width: 100%; border-collapse: collapse; background-color: rgba(88, 28, 135, 0.2); border-radius: 8px; padding: 20px;">
                            <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #c084fc; font-weight: 600;">Stage Name:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #d1d5db;">{stage_name}</td>
                            </tr>
                            <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #c084fc; font-weight: 600;">Email:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #d1d5db;">{dj_email}</td>
                            </tr>
                            <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #c084fc; font-weight: 600;">Token Reset:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(147, 51, 234, 0.3); color: #d1d5db; font-family: monospace; font-size: 11px; line-height: 1.4; word-break: break-all;">{reset_token}</td>
                            </tr>
                            <tr>
                            <td style="padding: 12px 20px; color: #c084fc; font-weight: 600;">Timestamp:</td>
                            <td style="padding: 12px 20px; color: #d1d5db;">{datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')} UTC</td>
                            </tr>
                        </table>

                        <!-- URL Box -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; margin: 25px 0;">
                        <tr>
                            <td style="padding: 20px;">
                            <p style="color: #93c5fd; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                                🔗 Link di Reset
                            </p>
                            <p style="color: #3b82f6; font-size: 12px; margin: 0; line-height: 1.5; word-break: break-all; font-family: monospace;">
                                {reset_url}
                            </p>
                            </td>
                        </tr>
                        </table>

                        <!-- Warning Box -->
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 12px; margin: 25px 0;">
                        <tr>
                            <td style="padding: 20px;">
                            <p style="color: #fde68a; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                                ⚠️ Azione Richiesta
                            </p>
                            <p style="color: #fbbf24; font-size: 13px; margin: 0; line-height: 1.5;">
                                Un DJ ha richiesto il reset della password. Il link inviato è valido per 1 ora.
                            </p>
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                    <td style="padding: 25px 30px; text-align: center; border-top: 1px solid rgba(147, 51, 234, 0.2);">
                        <p style="color: #6b7280; font-size: 12px; margin: 0;">
                        Notifica automatica dal sistema Karaokati Admin
                        </p>
                    </td>
                    </tr>

                </table>
                </td>
            </tr>

            </table>
        </td>
        </tr>
    </table>
    </body>
    </html>
    """
    
    admin_email = settings.SMTP_USER
    return send_email(admin_email, subject, html_body)
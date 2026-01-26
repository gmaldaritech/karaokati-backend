from datetime import datetime
import uuid

def verification_email_template(verification_url: str, terms_url: str) -> tuple[str, str]:
    """Template email di verifica account con correzione per il clipping di Gmail"""
    
    # Generiamo un ID breve e univoco per ogni invio
    unique_id = str(uuid.uuid4())[:8]
    
    subject = "🚀 Benvenuto in Karaokati - Completa la registrazione"
    
    html_body = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verifica Email - Karaokati</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #111827;">

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: linear-gradient(135deg, #9333ea, #ec4899); padding: 50px 20px;">
    <tr>
    <td align="center">
        <div style="background-color: rgba(255,255,255,0.2); border-radius: 50%; padding: 20px; display: inline-block; margin-bottom: 20px;">
            <img src="https://img.icons8.com/fluency/64/ffffff/new-post.png" alt="Email" width="48" height="48" style="display: block;">
        </div>
        <h1 style="color: #ffffff; font-size: 26px; font-weight: bold; margin: 0 0 10px 0; text-align: center;">
            Benvenuto su Karaokati
        </h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 16px; margin: 0; text-align: center;">
            Verifica il tuo indirizzo email per iniziare
        </p>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: linear-gradient(180deg, rgba(88, 28, 135, 0.3), rgba(17, 24, 39, 0.9)); padding: 40px 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; padding: 0 10px;">
            <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                Ciao! 👋
            </p>
            <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                Grazie per esserti registrato su <strong style="color: #c084fc;">Karaokati</strong>, la piattaforma per DJ karaoke professionisti.
            </p>
            <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 30px 0;">
                Per completare la registrazione e attivare il tuo account, clicca sul pulsante qui sotto:
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" style="display: inline-block; background: linear-gradient(135deg, #9333ea, #ec4899); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; padding: 16px 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(147, 51, 234, 0.4);">
                    ✉️ Verifica Email
                </a>
            </div>
            
            <div style="background-color: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; padding: 20px; margin: 20px 0;">
                <p style="color: #86efac; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                    ⏰ Link valido per 24 ore
                </p>
                <p style="color: #4ade80; font-size: 13px; margin: 0; line-height: 1.5;">
                    Una volta verificato, potrai accedere a tutti i servizi della piattaforma.
                </p>
            </div>
            
            <div style="background-color: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 20px; margin: 20px 0;">
                <p style="color: #93c5fd; font-size: 14px; margin: 0 0 15px 0; font-weight: 600;">
                    🎤 Cosa potrai fare:
                </p>
                <ul style="color: #3b82f6; font-size: 13px; margin: 0; padding-left: 20px; line-height: 1.8; text-align: left;">
                    <li>🏢 Gestire i tuoi locali e serate</li>
                    <li>🎵 Organizzare il catalogo musicale</li>
                    <li>📱 Ricevere prenotazioni via QR code</li>
                </ul>
            </div>
            
            <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 25px 0 0 0; text-align: center;">
                Se il pulsante non funziona, copia e incolla questo link nel browser:
            </p>
            <p style="color: #a78bfa; font-size: 12px; word-break: break-all; margin: 10px 0 0 0; text-align: center;">
                {verification_url}
            </p>
        </div>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: rgba(17, 24, 39, 0.9); padding: 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; border-top: 1px solid rgba(147, 51, 234, 0.2);"></div>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: rgba(17, 24, 39, 0.9); padding: 25px 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; text-align: center;">
            <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 0 0 15px 0;">
                Se non hai creato un account su Karaokati, puoi ignorare questa email in sicurezza.
            </p>
            <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 0 0 20px 0;">
                Per qualsiasi problema, contattaci su <a href="mailto:support@karaokati.com" style="color: #c084fc; text-decoration: none;">support@karaokati.com</a>
            </p>
            <p style="color: #9333ea; font-size: 16px; font-weight: 600; margin: 0;">
                Il Team Karaokati 🎤
            </p>
        </div>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #111827; padding: 30px 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; text-align: center;">
            <p style="color: #6b7280; font-size: 13px; margin: 0 0 10px 0;">
                © 2026 Karaokati. Tutti i diritti riservati.
            </p>
            <p style="color: #4b5563; font-size: 12px; margin: 0;">
                <a href="{terms_url}" style="color: #9ca3af; text-decoration: none;">Termini di Servizio</a>
            </p>
            
            <div style="display: none; max-height: 0px; overflow: hidden; font-size: 1px; line-height: 1px; color: #111827;">
                Ref ID: {unique_id}
            </div>
        </div>
    </td>
    </tr>
    </table>

    </body>
    </html>
    """
    return subject, html_body

def reset_password_email_template(reset_url: str, terms_url: str) -> tuple[str, str]:
    """Template email reset password con anti-clipping"""
    unique_id = str(uuid.uuid4())[:8]
    subject = "🔐 Reset della tua password Karaokati"
    html_body = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password - Karaokati</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #111827;">

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: linear-gradient(135deg, #9333ea, #ec4899); padding: 50px 20px;">
    <tr>
    <td align="center">
        <div style="background-color: rgba(255,255,255,0.2); border-radius: 50%; padding: 20px; display: inline-block; margin-bottom: 20px;">
            <img src="https://img.icons8.com/fluency/64/ffffff/lock.png" alt="Lock" width="48" height="48" style="display: block;">
        </div>
        <h1 style="color: #ffffff; font-size: 26px; font-weight: bold; margin: 0 0 10px 0; text-align: center;">
            Reset della Password
        </h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 16px; margin: 0; text-align: center;">
            Hai richiesto di reimpostare la tua password
        </p>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: linear-gradient(180deg, rgba(88, 28, 135, 0.3), rgba(17, 24, 39, 0.9)); padding: 40px 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; padding: 0 10px;">
            <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                Ciao! 👋
            </p>
            <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                Abbiamo ricevuto una richiesta per reimpostare la password del tuo account <strong style="color: #c084fc;">Karaokati</strong>.
            </p>
            <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 30px 0;">
                Se sei stato tu, clicca sul pulsante qui sotto per creare una nuova password:
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #9333ea, #ec4899); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; padding: 16px 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(147, 51, 234, 0.4);">
                    🔑 Reimposta Password
                </a>
            </div>
            
            <div style="background-color: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 12px; padding: 20px; margin: 20px 0;">
                <p style="color: #fde68a; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                    ⏰ Link valido per 1 ora
                </p>
                <p style="color: #fbbf24; font-size: 13px; margin: 0; line-height: 1.5;">
                    Se non hai richiesto questo reset, ignora questa email.
                </p>
            </div>
            
            <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 25px 0 0 0; text-align: center;">
                Se il pulsante non funziona, copia questo link:
            </p>
            <p style="color: #a78bfa; font-size: 12px; word-break: break-all; margin: 10px 0 0 0; text-align: center;">
                {reset_url}
            </p>
        </div>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: rgba(17, 24, 39, 0.9); padding: 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; border-top: 1px solid rgba(147, 51, 234, 0.2);"></div>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: rgba(17, 24, 39, 0.9); padding: 25px 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; text-align: center;">
            <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 0 0 15px 0;">
                Se non hai creato un account su Karaokati, puoi ignorare questa email in sicurezza.
            </p>
            <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 0 0 20px 0;">
                Per qualsiasi problema, contattaci su <a href="mailto:support@karaokati.com" style="color: #c084fc; text-decoration: none;">support@karaokati.com</a>
            </p>
            <p style="color: #9333ea; font-size: 16px; font-weight: 600; margin: 0;">
                Il Team Karaokati 🎤
            </p>
        </div>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #111827; padding: 30px 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; text-align: center;">
            <p style="color: #6b7280; font-size: 13px; margin: 0 0 10px 0;">
                © 2026 Karaokati. Tutti i diritti riservati.
            </p>
            <p style="color: #4b5563; font-size: 12px; margin: 0;">
                <a href="{terms_url}" style="color: #9ca3af; text-decoration: none;">Termini di Servizio</a>
            </p>
            <div style="display: none; max-height: 0px; overflow: hidden; font-size: 1px; color: #111827;">
                Ref: {unique_id}
            </div>
        </div>
    </td>
    </tr>
    </table>

    </body>
    </html>
    """
    return subject, html_body

def account_deletion_email_template(stage_name: str, full_name: str, terms_url: str) -> tuple[str, str]:
    """Template email cancellazione account utente con anti-clipping"""
    unique_id = str(uuid.uuid4())[:8]
    subject = "👋 Addio da Karaokati - Account rimosso"
    html_body = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Eliminato - Karaokati</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #111827;">

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: linear-gradient(135deg, #9333ea, #ec4899); padding: 50px 20px;">
    <tr>
    <td align="center">
        <div style="background-color: rgba(255, 255, 255, 0.2); border-radius: 50%; padding: 20px; display: inline-block; margin-bottom: 20px;">
            <span style="font-size: 40px; color: white;">👋</span>
        </div>
        <h1 style="color: white; font-size: 28px; font-weight: 700; margin: 0 0 10px 0; text-align: center;">
            Arrivederci, {stage_name}!
        </h1>
        <p style="color: rgba(255, 255, 255, 0.9); font-size: 16px; margin: 0; text-align: center;">
            Il tuo account Karaokati è stato eliminato con successo
        </p>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: linear-gradient(180deg, rgba(88, 28, 135, 0.3), rgba(17, 24, 39, 0.9)); padding: 40px 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; padding: 0 10px;">
            <p style="color: #d1d5db; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                Ciao <strong style="color: #c084fc;">{full_name}</strong>,
            </p>
            <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                Il tuo account DJ <strong style="color: #c084fc;">{stage_name}</strong> è stato eliminato definitivamente dal nostro sistema.
            </p>
            
            <div style="background-color: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 20px; margin: 25px 0;">
                <p style="color: #93c5fd; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                    📋 Dati eliminati
                </p>
                <ul style="color: #3b82f6; font-size: 13px; margin: 0; padding-left: 16px; line-height: 1.8; text-align: left;">
                    <li>🎤 Profilo DJ e informazioni personali</li>
                    <li>🎵 Catalogo canzoni completo</li>
                    <li>📅 Cronologia prenotazioni</li>
                    <li>📱 QR Code e configurazioni</li>
                </ul>
            </div>
            
            <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin: 25px 0 0 0;">
                Grazie per aver utilizzato <strong style="color: #c084fc;">Karaokati</strong>! 
                Se dovessi cambiare idea, potrai sempre creare un nuovo account.
            </p>
        </div>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: rgba(17, 24, 39, 0.9); padding: 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; border-top: 1px solid rgba(147, 51, 234, 0.2);"></div>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: rgba(17, 24, 39, 0.9); padding: 25px 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; text-align: center;">
            <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 0 0 15px 0;">
                Speriamo di rivederti presto su Karaokati.
            </p>
            <p style="color: #9333ea; font-size: 16px; font-weight: 600; margin: 0;">
                Il Team Karaokati 🎤
            </p>
        </div>
    </td>
    </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #111827; padding: 30px 20px;">
    <tr>
    <td align="center">
        <div style="max-width: 600px; margin: 0 auto; text-align: center;">
            <p style="color: #6b7280; font-size: 13px; margin: 0 0 10px 0;">
                © 2026 Karaokati. Tutti i diritti riservati.
            </p>
            <p style="color: #4b5563; font-size: 12px; margin: 0;">
                <a href="{terms_url}" style="color: #9ca3af; text-decoration: none;">Termini di Servizio</a>
            </p>
            <div style="display: none; max-height: 0px; overflow: hidden; font-size: 1px; color: #111827;">
                Trace: {unique_id}
            </div>
        </div>
    </td>
    </tr>
    </table>

    </body>
    </html>
    """
    return subject, html_body

def admin_registration_notification_template(dj_email: str, stage_name: str, full_name: str, verification_token: str, verification_url: str) -> tuple[str, str]:
    """Template notifica admin registrazione"""
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
    return subject, html_body

def admin_password_reset_notification_template(dj_email: str, stage_name: str, reset_token: str, reset_url: str) -> tuple[str, str]:
    """Template notifica admin reset password"""
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
    return subject, html_body

def admin_account_deletion_notification_template(dj_email: str, stage_name: str, full_name: str) -> tuple[str, str]:
    """Template notifica admin cancellazione account"""
    subject = "Account Eliminato - Karaokati"
    html_body = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account DJ Eliminato</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #111827;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #111827; padding: 40px 20px;">
        <tr>
        <td align="center">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%;">
            <tr>
                <td>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(180deg, rgba(239, 68, 68, 0.3), rgba(17, 24, 39, 0.9)); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 24px; overflow: hidden;">
                    <tr>
                    <td style="background: linear-gradient(135deg, #dc2626, #991b1b); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">🗑️ Account DJ Eliminato</h1>
                    </td>
                    </tr>
                    <tr>
                    <td style="padding: 30px;">
                        <h2 style="color: #333; margin: 0 0 20px 0;">Dettagli Cancellazione:</h2>
                        <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; font-weight: 600;">Nome Completo:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(239, 68, 68, 0.3); color: #d1d5db;">{full_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; font-weight: 600;">Stage Name:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(239, 68, 68, 0.3); color: #d1d5db;">{stage_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; font-weight: 600;">Email:</td>
                            <td style="padding: 12px 20px; border-bottom: 1px solid rgba(239, 68, 68, 0.3); color: #d1d5db;">{dj_email}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 20px; color: #fca5a5; font-weight: 600;">Data Eliminazione:</td>
                            <td style="padding: 12px 20px; color: #d1d5db;">{datetime.now().strftime('%d/%m/%Y %H:%M')}</td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                    <tr>
                    <td style="padding: 25px 30px; text-align: center; border-top: 1px solid rgba(239, 68, 68, 0.2);">
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
    return subject, html_body
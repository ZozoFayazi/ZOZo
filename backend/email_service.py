"""
Email Service for ZOZO Burger
Handles all email communications using Resend
"""
import os
import resend
from datetime import datetime
from typing import Optional
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

logger = logging.getLogger(__name__)

# Initialize Resend with API key
resend.api_key = os.getenv('RESEND_API_KEY')

# Default sender email
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'noreply@zozo-burger.de')

# Google Review Links for each location
LOCATION_REVIEW_LINKS = {
    "rellingen": "https://search.google.com/local/writereview?placeid=ChIJn9Dn6hSUuEcRZdj8BGyKqGk",
    "henstedt-ulzburg": None  # Will be added later
}

def get_email_logo_url():
    """Get ZOZO Burger logo URL - publicly accessible"""
    return "https://customer-assets.emergentagent.com/job_zozofinal/artifacts/ucrdxkwy_IMG_8154.jpeg"

def get_base_email_template(content: str, title: str = "ZOZO Burger") -> str:
    """Base HTML template for all emails - optimized for email clients (Gmail, iPhone Mail, Outlook)"""
    logo_url = get_email_logo_url()
    
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>{title}</title>
        <!--[if mso]>
        <noscript>
            <xml>
                <o:OfficeDocumentSettings>
                    <o:PixelsPerInch>96</o:PixelsPerInch>
                </o:OfficeDocumentSettings>
            </xml>
        </noscript>
        <![endif]-->
        <style type="text/css">
            /* Reset styles for email clients */
            body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
            table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
            img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
            body {{
                margin: 0 !important;
                padding: 0 !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
                background-color: #0a0a0a;
                color: #ffffff;
                width: 100% !important;
                height: 100% !important;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #1a1a1a;
            }}
            .header {{
                background-color: #1a1a1a;
                padding: 30px 20px;
                text-align: center;
            }}
            .header img {{
                max-width: 180px;
                height: auto;
                display: block;
                margin: 0 auto;
            }}
            .content {{
                padding: 40px 30px;
                line-height: 1.8;
                background-color: #1a1a1a;
            }}
            .content h1 {{
                color: #dc2626;
                font-size: 24px;
                margin: 0 0 20px 0;
                text-align: center;
                font-weight: bold;
            }}
            .content p {{
                color: #e5e5e5;
                font-size: 16px;
                margin: 0 0 15px 0;
                line-height: 1.6;
            }}
            .button {{
                display: inline-block;
                padding: 16px 40px;
                background-color: #dc2626;
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                margin: 20px 0;
                text-align: center;
            }}
            .code-box {{
                background-color: #0a0a0a;
                border: 2px solid #dc2626;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .code {{
                font-size: 32px;
                font-weight: bold;
                color: #dc2626;
                letter-spacing: 8px;
                font-family: 'Courier New', monospace;
            }}
            .info-box {{
                background-color: rgba(220, 38, 38, 0.15);
                border-left: 4px solid #dc2626;
                padding: 15px 20px;
                margin: 20px 0;
                border-radius: 0 4px 4px 0;
            }}
            .footer {{
                background-color: #0a0a0a;
                padding: 30px 20px;
                text-align: center;
                border-top: 1px solid #333333;
            }}
            .footer p {{
                color: #666666;
                font-size: 14px;
                margin: 5px 0;
            }}
            .footer a {{
                color: #dc2626;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{logo_url}" alt="ZOZO Burger Logo">
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                <p>ZOZO Burger - Premium Burger, Pizza & More</p>
                <p>Rellingen • Henstedt-Ulzburg</p>
                <p>
                    <a href="https://www.zozo-burger.de">www.zozo-burger.de</a> • 
                    <a href="mailto:info@zozo-burger.de">info@zozo-burger.de</a>
                </p>
                <p style="margin-top: 20px; font-size: 12px;">
                    Diese E-Mail wurde automatisch generiert. Bitte nicht antworten.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email via Resend"""
    try:
        # Ensure API key is set
        if not resend.api_key:
            resend.api_key = os.getenv('RESEND_API_KEY')
        
        if not resend.api_key:
            logger.error("RESEND_API_KEY not configured")
            return False
        
        # Use configured sender email, fallback to Resend test domain if domain not verified
        sender = SENDER_EMAIL
        
        # Check if using custom domain - may need verification
        # For production, use verified domain: noreply@zozo-burger.de
        # For testing/development, can use: onboarding@resend.dev
        use_test_domain = os.getenv('RESEND_USE_TEST_DOMAIN', 'false').lower() == 'true'
        if use_test_domain:
            sender = 'onboarding@resend.dev'
            logger.info("Using Resend test domain for sending")
        
        params = {
            "from": f"ZOZO Burger <{sender}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        response = resend.Emails.send(params)
        
        if response and response.get('id'):
            logger.info(f"Email sent successfully to {to_email}, ID: {response.get('id')}")
            return True
        else:
            logger.error(f"Email send failed: {response}")
            return False
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Email send error: {error_msg}")
        
        # Check for domain verification error
        if 'not verified' in error_msg.lower():
            logger.warning(
                "Domain not verified at Resend. "
                "Please verify zozo-burger.de at https://resend.com/domains "
                "or set RESEND_USE_TEST_DOMAIN=true for testing"
            )
        
        return False

def send_verification_email(email: str, verification_code: str) -> bool:
    """Send email verification code"""
    content = f"""
        <h1>🔐 E-Mail Verifizierung</h1>
        <p>Willkommen bei ZOZO Burger!</p>
        <p>Um deine E-Mail-Adresse zu bestätigen, verwende bitte den folgenden Verifizierungscode:</p>
        
        <div class="code-box">
            <div class="code">{verification_code}</div>
        </div>
        
        <p>Dieser Code ist <strong>10 Minuten</strong> gültig.</p>
        
        <div class="info-box">
            <p><strong>⚡ Warum verifizieren?</strong></p>
            <p>Damit wir dir Bestellbestätigungen, Status-Updates und exklusive Angebote zusenden können!</p>
        </div>
        
        <p>Falls du diese E-Mail nicht angefordert hast, kannst du sie ignorieren.</p>
    """
    
    html = get_base_email_template(content, "E-Mail Verifizierung")
    return send_email(email, "🔐 ZOZO Burger - Verifiziere deine E-Mail", html)

def send_order_confirmation_email(order: dict, location: dict) -> bool:
    """Send order confirmation email"""
    customer = order.get('customer', {})
    items_html = ""
    
    for item in order.get('items', []):
        size_text = f" ({item.get('size')})" if item.get('size') else ""
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #333;">
                {item.get('quantity')}x {item.get('name')}{size_text}
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #333; text-align: right;">
                €{(item.get('price', 0) * item.get('quantity', 1)):.2f}
            </td>
        </tr>
        """
    
    points_earned = int(order.get('total', 0) / 10)
    
    content = f"""
        <h1>✅ Bestellung bestätigt!</h1>
        <p>Vielen Dank für deine Bestellung bei ZOZO Burger!</p>
        
        <div class="info-box">
            <p><strong>📋 Bestellnummer:</strong> {order.get('order_number')}</p>
            <p><strong>🏪 Filiale:</strong> {location.get('name')}</p>
            <p><strong>⏱️ Geschätzte Lieferzeit:</strong> {order.get('estimated_time', 30)} Minuten</p>
        </div>
        
        <h2 style="color: #dc2626; margin-top: 30px;">Deine Bestellung:</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            {items_html}
            <tr style="font-weight: bold; font-size: 18px;">
                <td style="padding: 15px 10px; border-top: 2px solid #dc2626;">Gesamt</td>
                <td style="padding: 15px 10px; border-top: 2px solid #dc2626; text-align: right; color: #dc2626;">
                    €{order.get('total', 0):.2f}
                </td>
            </tr>
        </table>
        
        <div class="info-box">
            <p><strong>🎁 Treuepunkte verdient: {points_earned} Punkte!</strong></p>
            <p>Du hast {points_earned} Treuepunkte für diese Bestellung gesammelt.</p>
        </div>
        
        <p><strong>📍 Lieferadresse:</strong><br>
        {customer.get('name')}<br>
        {customer.get('address')}<br>
        {customer.get('postal_code')} {customer.get('city')}</p>
        
        <p><strong>💳 Zahlungsmethode:</strong> {order.get('payment_method', 'Nicht angegeben')}</p>
        
        <p style="margin-top: 30px;">Wir bereiten deine Bestellung bereits zu! 🔥</p>
    """
    
    html = get_base_email_template(content, "Bestellung bestätigt")
    return send_email(customer.get('email'), f"✅ Bestellung {order.get('order_number')} bestätigt", html)

def send_status_update_email(order: dict, new_status: str, location: dict) -> bool:
    """Send order status update email"""
    customer = order.get('customer', {})
    
    status_messages = {
        "confirmed": {
            "emoji": "✅",
            "title": "Bestellung bestätigt",
            "message": "Deine Bestellung wurde bestätigt und wird jetzt vorbereitet."
        },
        "preparing": {
            "emoji": "👨‍🍳",
            "title": "In Zubereitung",
            "message": "Deine Bestellung wird gerade frisch zubereitet!"
        },
        "ready": {
            "emoji": "📦",
            "title": "Bereit zur Abholung",
            "message": "Deine Bestellung ist fertig und wartet auf dich!"
        },
        "out_for_delivery": {
            "emoji": "🚗",
            "title": "Unterwegs zu dir",
            "message": "Deine Bestellung ist auf dem Weg zu dir!"
        },
        "delivered": {
            "emoji": "🎉",
            "title": "Zugestellt",
            "message": "Guten Appetit! Deine Bestellung wurde zugestellt."
        }
    }
    
    status_info = status_messages.get(new_status, status_messages["confirmed"])
    
    content = f"""
        <h1>{status_info['emoji']} {status_info['title']}</h1>
        <p>{status_info['message']}</p>
        
        <div class="info-box">
            <p><strong>📋 Bestellnummer:</strong> {order.get('order_number')}</p>
            <p><strong>🏪 Filiale:</strong> {location.get('name')}</p>
        </div>
        
        <p>Du kannst den Status deiner Bestellung jederzeit online verfolgen.</p>
        
        <div style="text-align: center;">
            <a href="https://zozo-prelaunch.preview.emergentagent.com/order-tracking" 
               class="button">
                📍 Bestellung verfolgen
            </a>
        </div>
    """
    
    html = get_base_email_template(content, f"Status-Update: {status_info['title']}")
    return send_email(customer.get('email'), f"{status_info['emoji']} Bestellung {order.get('order_number')} - {status_info['title']}", html)

def send_review_request_email(order: dict, location: dict) -> bool:
    """Send review request email 2 hours after delivery"""
    customer = order.get('customer', {})
    location_slug = location.get('slug', 'rellingen')
    review_link = LOCATION_REVIEW_LINKS.get(location_slug)
    
    if not review_link:
        logger.warning(f"No review link configured for location: {location_slug}")
        return False
    
    content = f"""
        <h1>⭐ Wie war dein ZOZO Burger?</h1>
        <p>Hallo {customer.get('name', 'lieber Gast')}!</p>
        <p>Wir hoffen, deine Bestellung hat dir geschmeckt! 😋</p>
        
        <div class="info-box">
            <p>Deine Meinung ist uns wichtig! Hilf uns, noch besser zu werden.</p>
        </div>
        
        <p>Es würde uns sehr freuen, wenn du uns auf Google bewerten könntest. 
        Dein Feedback hilft uns, unseren Service zu verbessern und anderen Gästen bei ihrer Entscheidung.</p>
        
        <div style="text-align: center;">
            <a href="{review_link}" class="button">
                ⭐ Jetzt auf Google bewerten
            </a>
        </div>
        
        <p style="margin-top: 30px; text-align: center;">Vielen Dank für deine Unterstützung! 🙏</p>
        
        <div style="text-align: center; margin-top: 40px;">
            <p><strong>🎁 Noch mehr Vorteile?</strong></p>
            <p>Sammle Treuepunkte bei jeder Bestellung und sichere dir leckere Belohnungen!</p>
            <a href="{os.environ.get('APP_URL', 'http://localhost:3000')}/rewards" 
               style="color: #dc2626; text-decoration: underline;">
                Zu den Belohnungen →
            </a>
        </div>
    """
    
    html = get_base_email_template(content, "Bewerte uns auf Google")
    return send_email(customer.get('email'), "⭐ Wie hat dir deine ZOZO Burger Bestellung geschmeckt?", html)


def send_group_order_invite_email(to_email: str, group_code: str, host_name: str, share_link: str) -> bool:
    """Send invitation email to join a group order"""
    content = f"""
        <h1>👥 Du wurdest zu einer Gruppenbestellung eingeladen!</h1>
        <p>Hey!</p>
        <p><strong>{host_name}</strong> hat dich zu einer gemeinsamen ZOZO Burger Bestellung eingeladen.</p>
        
        <div class="info-box">
            <p><strong>🍔 So funktioniert's:</strong></p>
            <p>1. Klicke auf den Button unten</p>
            <p>2. Füge deine Lieblings-Burger & Snacks hinzu</p>
            <p>3. Alle sehen in Echtzeit, was bestellt wird</p>
            <p>4. Der Host schließt die Bestellung ab</p>
        </div>
        
        <div class="code-box">
            <p style="color: #e5e5e5; margin-bottom: 10px;">Gruppencode:</p>
            <div class="code">{group_code}</div>
        </div>
        
        <div style="text-align: center;">
            <a href="{share_link}" class="button">
                🍔 Jetzt mitmachen
            </a>
        </div>
        
        <p style="margin-top: 30px; font-size: 14px; color: #888;">
            <strong>⏰ Hinweis:</strong> Gruppenbestellungen sind 1 Stunde gültig. Sei schnell dabei!
        </p>
    """
    
    html = get_base_email_template(content, "Gruppenbestellung Einladung")
    return send_email(to_email, f"👥 {host_name} lädt dich zur Gruppenbestellung ein!", html)


def send_password_reset_email(email: str, reset_token: str) -> bool:
    """Send password reset email"""
    reset_link = f"https://zozo-prelaunch.preview.emergentagent.com/admin/reset-password?token={reset_token}"
    
    content = f"""
        <h1>🔑 Passwort zurücksetzen</h1>
        <p>Du hast eine Anfrage zum Zurücksetzen deines Passworts gestellt.</p>
        
        <div class="info-box">
            <p>Klicke auf den Button unten, um ein neues Passwort zu erstellen.</p>
            <p>Dieser Link ist <strong>1 Stunde</strong> gültig.</p>
        </div>
        
        <div style="text-align: center;">
            <a href="{reset_link}" class="button">
                🔑 Passwort zurücksetzen
            </a>
        </div>
        
        <p style="margin-top: 30px;">Falls du diese Anfrage nicht gestellt hast, kannst du diese E-Mail ignorieren.</p>
    """
    
    html = get_base_email_template(content, "Passwort zurücksetzen")
    return send_email(email, "🔑 ZOZO Burger - Passwort zurücksetzen", html)


def send_password_changed_email(email: str, name: str = None) -> bool:
    """Send confirmation email when password has been changed"""
    display_name = name or "Admin"
    timestamp = datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')
    
    content = f"""
        <h1>✅ Passwort erfolgreich geändert</h1>
        <p>Hallo {display_name},</p>
        <p>dein Passwort wurde soeben erfolgreich geändert.</p>
        
        <div class="info-box">
            <p><strong>📅 Datum:</strong> {timestamp}</p>
            <p><strong>📧 Account:</strong> {email}</p>
        </div>
        
        <div style="background: rgba(220, 38, 38, 0.15); border: 1px solid #dc2626; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #ffffff;"><strong>⚠️ Das warst nicht du?</strong></p>
            <p style="margin: 10px 0 0 0; color: #e5e5e5; font-size: 14px;">
                Falls du diese Änderung nicht vorgenommen hast, kontaktiere uns umgehend unter 
                <a href="mailto:info@zozo-burger.de" style="color: #dc2626;">info@zozo-burger.de</a>
            </p>
        </div>
        
        <p style="margin-top: 30px;">Dein ZOZO Burger Team 🍔</p>
    """
    
    html = get_base_email_template(content, "Passwort geändert")
    return send_email(email, "✅ ZOZO Burger - Passwort erfolgreich geändert", html)


def send_2fa_enabled_email(email: str, name: str = None) -> bool:
    """Send confirmation email when 2FA has been enabled"""
    display_name = name or "Admin"
    timestamp = datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')
    
    content = f"""
        <h1>🛡️ Zwei-Faktor-Authentifizierung aktiviert</h1>
        <p>Hallo {display_name},</p>
        <p>die Zwei-Faktor-Authentifizierung wurde erfolgreich für deinen Account aktiviert.</p>
        
        <div class="info-box">
            <p><strong>📅 Aktiviert am:</strong> {timestamp}</p>
            <p><strong>📧 Account:</strong> {email}</p>
        </div>
        
        <div style="background: rgba(34, 197, 94, 0.15); border: 1px solid #22c55e; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #22c55e;"><strong>✅ Dein Konto ist jetzt sicherer!</strong></p>
            <p style="margin: 10px 0 0 0; color: #e5e5e5; font-size: 14px;">
                Ab sofort wird bei jedem Login ein zusätzlicher Code aus deiner Authenticator-App benötigt.
            </p>
        </div>
        
        <div class="info-box">
            <p><strong>💡 Wichtig:</strong></p>
            <p style="font-size: 14px;">Bewahre deine Backup-Codes sicher auf! Du benötigst sie, falls du den Zugang zu deiner Authenticator-App verlierst.</p>
        </div>
        
        <p style="margin-top: 30px;">Dein ZOZO Burger Team 🍔</p>
    """
    
    html = get_base_email_template(content, "2FA aktiviert")
    return send_email(email, "🛡️ ZOZO Burger - 2FA erfolgreich aktiviert", html)


def send_2fa_disabled_email(email: str, name: str = None) -> bool:
    """Send notification email when 2FA has been disabled"""
    display_name = name or "Admin"
    timestamp = datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')
    
    content = f"""
        <h1>⚠️ Zwei-Faktor-Authentifizierung deaktiviert</h1>
        <p>Hallo {display_name},</p>
        <p>die Zwei-Faktor-Authentifizierung wurde für deinen Account deaktiviert.</p>
        
        <div class="info-box">
            <p><strong>📅 Deaktiviert am:</strong> {timestamp}</p>
            <p><strong>📧 Account:</strong> {email}</p>
        </div>
        
        <div style="background: rgba(234, 179, 8, 0.15); border: 1px solid #eab308; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #eab308;"><strong>⚠️ Dein Konto ist jetzt weniger geschützt</strong></p>
            <p style="margin: 10px 0 0 0; color: #e5e5e5; font-size: 14px;">
                Wir empfehlen, die 2FA schnellstmöglich wieder zu aktivieren, um dein Konto zu schützen.
            </p>
        </div>
        
        <div style="background: rgba(220, 38, 38, 0.15); border: 1px solid #dc2626; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #ffffff;"><strong>❗ Das warst nicht du?</strong></p>
            <p style="margin: 10px 0 0 0; color: #e5e5e5; font-size: 14px;">
                Falls du diese Änderung nicht vorgenommen hast, wurde möglicherweise unberechtigt auf dein Konto zugegriffen. 
                Kontaktiere uns sofort unter <a href="mailto:info@zozo-burger.de" style="color: #dc2626;">info@zozo-burger.de</a>
            </p>
        </div>
        
        <p style="margin-top: 30px;">Dein ZOZO Burger Team 🍔</p>
    """
    
    html = get_base_email_template(content, "2FA deaktiviert")
    return send_email(email, "⚠️ ZOZO Burger - 2FA wurde deaktiviert", html)


def send_security_alert_email(email: str, name: str = None, alert_type: str = "new_login", details: dict = None) -> bool:
    """Send security alert email for suspicious activity"""
    display_name = name or "Admin"
    timestamp = datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')
    details = details or {}
    
    alert_configs = {
        "new_login": {
            "title": "Neuer Login erkannt",
            "emoji": "🔔",
            "description": "Es wurde ein neuer Login auf deinem Konto registriert.",
            "color": "#3b82f6"  # Blue
        },
        "failed_login": {
            "title": "Fehlgeschlagene Login-Versuche",
            "emoji": "🚨",
            "description": "Wir haben mehrere fehlgeschlagene Login-Versuche auf deinem Konto festgestellt.",
            "color": "#dc2626"  # Red
        },
        "password_reset_request": {
            "title": "Passwort-Reset angefordert",
            "emoji": "🔑",
            "description": "Es wurde eine Anfrage zum Zurücksetzen deines Passworts gestellt.",
            "color": "#eab308"  # Yellow
        },
        "account_locked": {
            "title": "Konto vorübergehend gesperrt",
            "emoji": "🔒",
            "description": "Dein Konto wurde aufgrund von zu vielen fehlgeschlagenen Login-Versuchen vorübergehend gesperrt.",
            "color": "#dc2626"  # Red
        }
    }
    
    config = alert_configs.get(alert_type, alert_configs["new_login"])
    
    # Build details section
    details_html = ""
    if details:
        details_items = []
        if details.get("ip_address"):
            details_items.append(f"<p><strong>🌐 IP-Adresse:</strong> {details['ip_address']}</p>")
        if details.get("location"):
            details_items.append(f"<p><strong>📍 Standort:</strong> {details['location']}</p>")
        if details.get("device"):
            details_items.append(f"<p><strong>💻 Gerät:</strong> {details['device']}</p>")
        if details.get("browser"):
            details_items.append(f"<p><strong>🌐 Browser:</strong> {details['browser']}</p>")
        if details_items:
            details_html = f"""
                <div class="info-box">
                    <p><strong>📋 Details:</strong></p>
                    {''.join(details_items)}
                </div>
            """
    
    content = f"""
        <h1>{config['emoji']} {config['title']}</h1>
        <p>Hallo {display_name},</p>
        <p>{config['description']}</p>
        
        <div class="info-box">
            <p><strong>📅 Zeitpunkt:</strong> {timestamp}</p>
            <p><strong>📧 Account:</strong> {email}</p>
        </div>
        
        {details_html}
        
        <div style="background: rgba({','.join(str(int(config['color'][i:i+2], 16)) for i in (1, 3, 5))}, 0.15); border: 1px solid {config['color']}; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #ffffff;"><strong>Das warst nicht du?</strong></p>
            <p style="margin: 10px 0 0 0; color: #e5e5e5; font-size: 14px;">
                Wenn du diese Aktivität nicht erkennst, ändere umgehend dein Passwort und aktiviere die Zwei-Faktor-Authentifizierung.
            </p>
        </div>
        
        <div style="text-align: center;">
            <a href="https://zozo-prelaunch.preview.emergentagent.com/admin/login" class="button">
                🔐 Zum Admin-Bereich
            </a>
        </div>
        
        <p style="margin-top: 30px;">Dein ZOZO Burger Sicherheitsteam 🛡️</p>
    """
    
    html = get_base_email_template(content, f"Sicherheitswarnung: {config['title']}")
    return send_email(email, f"{config['emoji']} ZOZO Burger - Sicherheitswarnung: {config['title']}", html)


def send_test_email(to_email: str) -> dict:
    """Send a test email to verify configuration"""
    try:
        content = f"""
            <h1>✅ Test-Email erfolgreich!</h1>
            <p>Diese E-Mail bestätigt, dass die E-Mail-Konfiguration korrekt eingerichtet ist.</p>
            
            <div class="info-box">
                <p><strong>📧 Gesendet an:</strong> {to_email}</p>
                <p><strong>⏰ Zeitstempel:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
                <p><strong>📤 Provider:</strong> Resend</p>
            </div>
            
            <p>Die E-Mail-Integration funktioniert einwandfrei! 🎉</p>
        """
        
        html = get_base_email_template(content, "Test-Email")
        success = send_email(to_email, "✅ ZOZO Burger - Test-Email erfolgreich", html)
        
        return {
            "success": success,
            "message": "Test-Email wurde gesendet" if success else "Fehler beim Senden der Test-Email",
            "to": to_email,
            "provider": "Resend"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "to": to_email,
            "provider": "Resend"
        }


def send_all_template_previews(to_email: str) -> dict:
    """Send all email templates to preview address for testing"""
    results = {}
    
    # Test data
    test_name = "Max Mustermann"
    test_order = {
        "order_number": "ZOZO-TEST-001",
        "total": 24.99,
        "estimated_time": 30,
        "items": [
            {"name": "Cheeseburger", "size": "Large", "price": 12.29, "quantity": 2}
        ],
        "customer": {
            "name": test_name,
            "email": to_email,
            "address": "Musterstraße 1",
            "postal_code": "25462",
            "city": "Rellingen"
        },
        "payment_method": "Bar bei Lieferung"
    }
    test_location = {
        "name": "ZOZO Burger Rellingen",
        "slug": "rellingen"
    }
    
    # 1. Password Reset
    results["password_reset"] = send_password_reset_email(to_email, "test-reset-token-xyz")
    
    # 2. Password Changed
    results["password_changed"] = send_password_changed_email(to_email, test_name)
    
    # 3. 2FA Enabled
    results["2fa_enabled"] = send_2fa_enabled_email(to_email, test_name)
    
    # 4. 2FA Disabled
    results["2fa_disabled"] = send_2fa_disabled_email(to_email, test_name)
    
    # 5. Security Alert (New Login)
    results["security_alert"] = send_security_alert_email(
        to_email, 
        test_name, 
        "new_login",
        {
            "ip_address": "192.168.1.1",
            "location": "Hamburg, Deutschland",
            "device": "Chrome auf Windows",
            "browser": "Chrome 120"
        }
    )
    
    return {
        "success": all(results.values()),
        "results": results,
        "to": to_email,
        "templates_sent": len([r for r in results.values() if r])
    }

"""
Email Service for ZOZO Burger
Handles all email communications using Resend
"""
import os
import resend
from datetime import datetime
from typing import Optional
import logging

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
    """Get ZOZO Burger logo URL"""
    return "https://customer-assets.emergentagent.com/job_custom-burger-maker/artifacts/crcay6aj_IMG_8154.jpeg"

def get_base_email_template(content: str, title: str = "ZOZO Burger") -> str:
    """Base HTML template for all emails"""
    logo_url = get_email_logo_url()
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Helvetica Neue', Arial, sans-serif;
                background-color: #0a0a0a;
                color: #ffffff;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
            }}
            .header {{
                background: #b91c1c;
                padding: 30px 20px;
                text-align: center;
                border-bottom: 4px solid #dc2626;
            }}
            .header img {{
                max-width: 200px;
                height: auto;
            }}
            .content {{
                padding: 40px 30px;
                line-height: 1.8;
            }}
            .content h1 {{
                color: #dc2626;
                font-size: 28px;
                margin-bottom: 20px;
                text-align: center;
            }}
            .content p {{
                color: #e5e5e5;
                font-size: 16px;
                margin-bottom: 15px;
            }}
            .button {{
                display: inline-block;
                padding: 15px 40px;
                background: #dc2626;
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                margin: 20px 0;
                text-align: center;
            }}
            .button:hover {{
                background: #b91c1c;
            }}
            .code-box {{
                background: #1a1a1a;
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
                background: rgba(220, 38, 38, 0.1);
                border-left: 4px solid #dc2626;
                padding: 15px 20px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .footer {{
                background: #0a0a0a;
                padding: 30px 20px;
                text-align: center;
                border-top: 2px solid #1a1a1a;
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
        
        params = {
            "from": f"ZOZO Burger <{SENDER_EMAIL}>",
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
        logger.error(f"Email send error: {str(e)}")
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
            <a href="https://zozofinal.preview.emergentagent.com/order-tracking" 
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
            <a href="https://zozofinal.preview.emergentagent.com/rewards" 
               style="color: #dc2626; text-decoration: underline;">
                Zu den Belohnungen →
            </a>
        </div>
    """
    
    html = get_base_email_template(content, "Bewerte uns auf Google")
    return send_email(customer.get('email'), "⭐ Wie hat dir deine ZOZO Burger Bestellung geschmeckt?", html)


def send_password_reset_email(email: str, reset_token: str) -> bool:
    """Send password reset email"""
    reset_link = f"https://zozofinal.preview.emergentagent.com/admin/reset-password?token={reset_token}"
    
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

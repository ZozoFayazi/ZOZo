"""
Enterprise Email Service for ZOZO Burger
Real email sending via Resend + beautiful templates + automation
Created: 22 January 2026
"""

import resend
import os
from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Resend API Key
resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@zozo-burger.de')
APP_URL = os.environ.get('APP_URL', 'https://burger-pipeline-fix.preview.emergentagent.com')


class EmailTemplates:
    """Professional email templates for ZOZO Burger"""
    
    @staticmethod
    def get_base_template(content: str, preheader: str = "") -> str:
        """Base template with ZOZO branding"""
        return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="x-apple-disable-message-reformatting">
    <title>ZOZO Burger</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0a0a0a;
            color: #ffffff;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #1a1a1a;
        }}
        .header {{
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            padding: 40px 20px;
            text-align: center;
        }}
        .logo {{
            width: 80px;
            height: 80px;
            margin: 0 auto 16px;
            background-color: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: bold;
            color: #dc2626;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .button {{
            display: inline-block;
            padding: 14px 32px;
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            background-color: #0a0a0a;
            padding: 30px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        .preheader {{
            display: none;
            max-height: 0;
            overflow: hidden;
        }}
    </style>
</head>
<body>
    <div class="preheader">{preheader}</div>
    <div class="container">
        <div class="header">
            <div class="logo">ZB</div>
            <h1 style="margin: 0; color: white; font-size: 24px;">ZOZO Burger</h1>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            <p style="margin: 0 0 10px 0;">ZOZO Burger - Premium Burger Delivery</p>
            <p style="margin: 0 0 10px 0;">Rellingen & Henstedt-Ulzburg</p>
            <p style="margin: 20px 0 10px 0;">
                <a href="{{{{APP_URL}}}}/newsletter/unsubscribe?token={{{{UNSUBSCRIBE_TOKEN}}}}" 
                   style="color: #666; text-decoration: underline;">
                    Abmelden
                </a>
            </p>
            <p style="margin: 10px 0 0 0; color: #444;">
                © 2026 ZOZO Burger. Alle Rechte vorbehalten.
            </p>
        </div>
    </div>
</body>
</html>
        """
    
    @staticmethod
    def welcome_email(customer_name: str, discount_code: str = "WELCOME10") -> str:
        """Welcome email for new newsletter subscribers"""
        content = f"""
            <h2 style="color: #dc2626; margin-top: 0;">Willkommen bei ZOZO Burger! 🎉</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Hallo {customer_name},
            </p>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Vielen Dank, dass du dich für unseren Newsletter angemeldet hast! 
                Wir freuen uns, dich in der ZOZO-Familie begrüßen zu dürfen.
            </p>
            <div style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); 
                        padding: 20px; border-radius: 12px; margin: 30px 0; text-align: center;">
                <p style="margin: 0 0 10px 0; font-size: 14px; color: rgba(255,255,255,0.9);">DEIN WILLKOMMENS-RABATT</p>
                <p style="margin: 0; font-size: 32px; font-weight: bold; color: white; letter-spacing: 2px;">{discount_code}</p>
                <p style="margin: 10px 0 0 0; font-size: 14px; color: rgba(255,255,255,0.9);">10% Rabatt auf deine nächste Bestellung</p>
            </div>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Als Newsletter-Abonnent erhältst du:
            </p>
            <ul style="font-size: 16px; line-height: 1.8; color: #e5e5e5;">
                <li>🎁 Exklusive Rabatte und Deals</li>
                <li>🍔 Frühzeitiger Zugang zu neuen Produkten</li>
                <li>📰 News und Updates</li>
                <li>🎂 Geburtstags-Überraschungen</li>
            </ul>
            <div style="text-align: center;">
                <a href="{APP_URL}/menu" class="button">
                    Jetzt Bestellen
                </a>
            </div>
            <p style="font-size: 14px; color: #999; margin-top: 30px;">
                Wir freuen uns auf deine Bestellung!<br>
                Dein ZOZO Burger Team
            </p>
        """
        return EmailTemplates.get_base_template(content, "Willkommen! Hier ist dein 10% Rabatt")
    
    @staticmethod
    def order_followup_email(customer_name: str, order_id: str, order_total: float, customer_email: str = "") -> str:
        """Post-order follow-up email with review link"""
        # Encode params for URL
        import urllib.parse
        review_url = f"{APP_URL}/review?order={order_id}&email={urllib.parse.quote(customer_email)}"
        
        content = f"""
            <h2 style="color: #dc2626; margin-top: 0;">Wie war deine Bestellung? 🍔</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Hallo {customer_name},
            </p>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                vielen Dank für deine Bestellung #{order_id}! Wir hoffen, dass es dir geschmeckt hat.
            </p>
            <div style="background-color: #2a2a2a; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #dc2626;">
                <p style="margin: 0; font-size: 14px; color: #999;">Deine Bestellung</p>
                <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: white;">€{order_total:.2f}</p>
            </div>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Deine Meinung ist uns wichtig! Bewerte deine Bestellung und erhalte einen Dankeschön-Gutschein! 🎁
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <p style="margin-bottom: 15px; color: #e5e5e5; font-weight: 600;">Wie würdest du deine Bestellung bewerten?</p>
                <div style="margin-bottom: 20px;">
                    <a href="{review_url}&rating=5" style="text-decoration: none; font-size: 36px; margin: 0 4px;">⭐</a>
                    <a href="{review_url}&rating=4" style="text-decoration: none; font-size: 36px; margin: 0 4px;">⭐</a>
                    <a href="{review_url}&rating=3" style="text-decoration: none; font-size: 36px; margin: 0 4px;">⭐</a>
                    <a href="{review_url}&rating=2" style="text-decoration: none; font-size: 36px; margin: 0 4px;">⭐</a>
                    <a href="{review_url}&rating=1" style="text-decoration: none; font-size: 36px; margin: 0 4px;">⭐</a>
                </div>
                <p style="font-size: 13px; color: #999; margin-bottom: 20px;">Klick auf die Sterne für deine Bewertung</p>
            </div>
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                        padding: 20px; border-radius: 12px; margin: 25px 0; text-align: center;">
                <p style="margin: 0 0 8px 0; font-size: 14px; color: rgba(255,255,255,0.9);">🎁 BONUS BEI 5 STERNEN</p>
                <p style="margin: 0; font-size: 20px; font-weight: bold; color: white;">5% Gutschein geschenkt!</p>
            </div>
            <div style="text-align: center;">
                <a href="{review_url}" class="button">
                    Jetzt detailliert bewerten
                </a>
            </div>
            <div style="text-align: center; margin-top: 30px;">
                <a href="{APP_URL}/menu" style="color: #999; text-decoration: underline; font-size: 14px;">
                    Oder erneut bestellen
                </a>
            </div>
            <p style="font-size: 14px; color: #999; margin-top: 30px;">
                Bis bald!<br>
                Dein ZOZO Burger Team
            </p>
        """
        return EmailTemplates.get_base_template(content, "Wie war deine Bestellung? Bewerte & erhalte 5% Gutschein!")
    
    @staticmethod
    def reactivation_email(customer_name: str, favorite_product: str = "Classic Burger", days_inactive: int = 30, discount_code: str = "COMEBACK15") -> str:
        """Reactivation email for at-risk customers with PERSONAL discount code"""
        content = f"""
            <h2 style="color: #dc2626; margin-top: 0;">Wir vermissen dich! 😢</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Hallo {customer_name},
            </p>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                es ist schon {days_inactive} Tage her, seit wir dich das letzte Mal verwöhnen durften. 
                Dein Lieblings-Burger wartet auf dich!
            </p>
            <div style="background-color: #2a2a2a; padding: 30px; border-radius: 12px; margin: 30px 0; text-align: center;">
                <p style="margin: 0 0 15px 0; font-size: 18px; color: #e5e5e5;">🍔 Du liebst:</p>
                <p style="margin: 0; font-size: 28px; font-weight: bold; color: #dc2626;">{favorite_product}</p>
            </div>
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                        padding: 25px; border-radius: 12px; margin: 30px 0; text-align: center;
                        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.3);">
                <p style="margin: 0 0 10px 0; font-size: 14px; color: rgba(0,0,0,0.7); font-weight: 600;">🎁 DEIN PERSÖNLICHER COMEBACK-CODE</p>
                <p style="margin: 0; font-size: 36px; font-weight: bold; color: #1a1a1a; letter-spacing: 3px; font-family: monospace;">{discount_code}</p>
                <p style="margin: 15px 0 5px 0; font-size: 18px; font-weight: bold; color: #1a1a1a;">20% RABATT</p>
                <p style="margin: 0; font-size: 13px; color: rgba(0,0,0,0.6);">Nur für dich • Einmalig verwendbar • 14 Tage gültig</p>
            </div>
            <div style="background-color: #1e3a8a; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3b82f6;">
                <p style="margin: 0; font-size: 14px; color: #93c5fd;">
                    💡 <strong style="color: white;">Hinweis:</strong> Dieser Code wurde speziell für dich erstellt und kann nur einmal verwendet werden.
                </p>
            </div>
            <div style="text-align: center;">
                <a href="{APP_URL}/menu" class="button" style="font-size: 18px; padding: 16px 40px;">
                    Jetzt mit Code bestellen!
                </a>
            </div>
            <p style="font-size: 14px; color: #999; margin-top: 30px; text-align: center;">
                Wir freuen uns auf dein Comeback!<br>
                Dein ZOZO Burger Team ❤️
            </p>
        """
        return EmailTemplates.get_base_template(content, "Dein persönlicher 20% Rabatt wartet auf dich!")
    
    @staticmethod
    def vip_upgrade_email(customer_name: str, total_orders: int, total_spent: float) -> str:
        """VIP upgrade notification email"""
        content = f"""
            <h2 style="color: #fbbf24; margin-top: 0;">🏆 Herzlichen Glückwunsch, VIP!</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Hallo {customer_name},
            </p>
            <p style="font-size: 18px; line-height: 1.6; color: #e5e5e5; font-weight: 600;">
                Du bist jetzt ein ZOZO VIP-Kunde! 🎉
            </p>
            <div style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); 
                        padding: 30px; border-radius: 12px; margin: 30px 0; text-align: center;">
                <p style="margin: 0 0 20px 0; font-size: 48px;">👑</p>
                <p style="margin: 0 0 10px 0; font-size: 24px; font-weight: bold; color: #1a1a1a;">VIP STATUS</p>
                <p style="margin: 0; font-size: 14px; color: rgba(0,0,0,0.7);">
                    {total_orders} Bestellungen • €{total_spent:.2f} Gesamtumsatz
                </p>
            </div>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Als VIP-Kunde erhältst du ab sofort:
            </p>
            <ul style="font-size: 16px; line-height: 1.8; color: #e5e5e5;">
                <li>🎁 Exklusive VIP-Deals (nur für dich!)</li>
                <li>🚀 Prioritäts-Lieferung</li>
                <li>💰 Doppelte Treuepunkte</li>
                <li>🎂 Geburtstags-Überraschung</li>
                <li>👨‍🍳 Früher Zugang zu neuen Produkten</li>
            </ul>
            <div style="text-align: center;">
                <a href="{APP_URL}/menu" class="button">
                    VIP-Vorteile nutzen
                </a>
            </div>
            <p style="font-size: 14px; color: #999; margin-top: 30px; text-align: center;">
                Danke für deine Treue!<br>
                Dein ZOZO Burger Team 👑
            </p>
        """
        return EmailTemplates.get_base_template(content, "Du bist jetzt VIP!")
    
    @staticmethod
    def promotional_email(title: str, description: str, cta_text: str = "Jetzt bestellen", cta_url: str = None) -> str:
        """Generic promotional email template"""
        if not cta_url:
            cta_url = f"{APP_URL}/menu"
        
        content = f"""
            <h2 style="color: #dc2626; margin-top: 0;">{title}</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                {description}
            </p>
            <div style="text-align: center; margin: 40px 0;">
                <a href="{cta_url}" class="button" style="font-size: 18px; padding: 16px 40px;">
                    {cta_text}
                </a>
            </div>
        """
        return EmailTemplates.get_base_template(content, title)


class EmailService:
    """Enterprise Email Service with Resend"""
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str = SENDER_EMAIL,
        reply_to: str = None
    ) -> Dict:
        """
        Send email via Resend
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            from_email: Sender email
            reply_to: Reply-to email
        
        Returns:
            {success: bool, message: str, email_id: str}
        """
        try:
            params = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            if reply_to:
                params["reply_to"] = reply_to
            
            response = resend.Emails.send(params)
            
            logger.info(f"Email sent successfully to {to_email}: {response.get('id')}")
            
            return {
                "success": True,
                "message": "Email gesendet",
                "email_id": response.get('id')
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                "success": False,
                "message": f"Fehler: {str(e)}",
                "email_id": None
            }
    
    @staticmethod
    async def send_welcome_email(subscriber_email: str, subscriber_name: str, unsubscribe_token: str) -> Dict:
        """Send welcome email to new subscriber"""
        html = EmailTemplates.welcome_email(subscriber_name or "Liebe*r Kunde*in")
        html = html.replace('{{APP_URL}}', APP_URL)
        html = html.replace('{{UNSUBSCRIBE_TOKEN}}', unsubscribe_token)
        
        return await EmailService.send_email(
            to_email=subscriber_email,
            subject="🎉 Willkommen bei ZOZO Burger - 10% Rabatt für dich!",
            html_content=html
        )
    
    @staticmethod
    async def send_order_followup(customer_email: str, customer_name: str, order_id: str, order_total: float, unsubscribe_token: str) -> Dict:
        """Send order follow-up email with review link"""
        html = EmailTemplates.order_followup_email(customer_name or "Liebe*r Kunde*in", order_id, order_total, customer_email)
        html = html.replace('{{APP_URL}}', APP_URL)
        html = html.replace('{{UNSUBSCRIBE_TOKEN}}', unsubscribe_token)
        
        return await EmailService.send_email(
            to_email=customer_email,
            subject=f"Bewerte deine Bestellung & erhalte 5% Gutschein! ⭐",
            html_content=html
        )
    
    @staticmethod
    async def send_reactivation_email(
        customer_email: str, 
        customer_name: str, 
        favorite_product: str,
        days_inactive: int,
        unsubscribe_token: str,
        discount_code: str = "COMEBACK15"
    ) -> Dict:
        """Send reactivation email to inactive customers with personal discount code"""
        html = EmailTemplates.reactivation_email(customer_name or "Liebe*r Kunde*in", favorite_product, days_inactive, discount_code)
        html = html.replace('{{APP_URL}}', APP_URL)
        html = html.replace('{{UNSUBSCRIBE_TOKEN}}', unsubscribe_token)
        
        return await EmailService.send_email(
            to_email=customer_email,
            subject="Dein persönlicher 20% Comeback-Rabatt 🎁",
            html_content=html
        )
    
    @staticmethod
    async def send_vip_upgrade_email(
        customer_email: str,
        customer_name: str,
        total_orders: int,
        total_spent: float,
        unsubscribe_token: str
    ) -> Dict:
        """Send VIP upgrade notification"""
        html = EmailTemplates.vip_upgrade_email(customer_name or "Liebe*r Kunde*in", total_orders, total_spent)
        html = html.replace('{{APP_URL}}', APP_URL)
        html = html.replace('{{UNSUBSCRIBE_TOKEN}}', unsubscribe_token)
        
        return await EmailService.send_email(
            to_email=customer_email,
            subject="🏆 Herzlichen Glückwunsch - Du bist jetzt VIP!",
            html_content=html
        )
    
    @staticmethod
    async def send_campaign_email(
        to_email: str,
        subject: str,
        html_content: str,
        campaign_id: str,
        unsubscribe_token: str
    ) -> Dict:
        """Send campaign email with tracking"""
        # Add tracking pixel
        tracking_pixel = f'<img src="{APP_URL}/api/newsletter/track-open/{campaign_id}/{to_email}" width="1" height="1" style="display:none;" />'
        
        # Replace placeholders
        html_with_tracking = html_content.replace('{{APP_URL}}', APP_URL)
        html_with_tracking = html_with_tracking.replace('{{UNSUBSCRIBE_TOKEN}}', unsubscribe_token)
        html_with_tracking += tracking_pixel
        
        return await EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_with_tracking
        )



# ==================== LEGACY EMAIL FUNCTIONS (STUBS) ====================
# These are stub functions for backward compatibility with server.py
# TODO: Refactor server.py to use EmailService class methods

def send_verification_email(email: str, code: str) -> bool:
    """Send verification email with code"""
    try:
        # Build verification email HTML
        content = f"""
            <h2 style="color: #dc2626; margin-top: 0;">E-Mail Verifizierung 🔐</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Vielen Dank für deine Registrierung bei ZOZO Burger!
            </p>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Dein Verifizierungscode:
            </p>
            <div style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); 
                        padding: 30px; border-radius: 12px; margin: 30px 0; text-align: center;">
                <p style="margin: 0; font-size: 48px; font-weight: bold; color: white; letter-spacing: 8px;">{code}</p>
            </div>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Gib diesen Code auf der Website ein, um deine E-Mail-Adresse zu bestätigen.
            </p>
            <p style="font-size: 14px; color: #999; margin-top: 30px;">
                Der Code ist 15 Minuten gültig.<br>
                Falls du diese E-Mail nicht angefordert hast, ignoriere sie bitte.
            </p>
        """
        
        html_content = EmailTemplates.get_base_template(content, f"Dein Verifizierungscode: {code}")
        
        # Send email via Resend
        params = {
            "from": SENDER_EMAIL,
            "to": [email],
            "subject": f"ZOZO Burger - Verifizierungscode: {code}",
            "html": html_content
        }
        
        response = resend.Emails.send(params)
        logger.info(f"Verification email sent to {email}: {response.get('id')}")
        return True
        
    except Exception as e:
        logger.error(f"send_verification_email error for {email}: {str(e)}")
        return False

def send_status_update_email(order: dict, status: str, location: dict) -> bool:
    """Send order status update email"""
    try:
        customer_email = order.get('customer_email')
        if not customer_email:
            logger.warning(f"No customer email for order {order.get('order_id')}")
            return False
        
        customer_name = order.get('customer_name', 'Kunde')
        order_number = order.get('order_number', order.get('order_id', 'N/A'))
        
        # Status messages
        status_messages = {
            'preparing': {
                'title': 'Bestellung wird zubereitet 👨‍🍳',
                'message': 'Deine Bestellung wird gerade frisch zubereitet!',
                'emoji': '🍔'
            },
            'ready': {
                'title': 'Bestellung ist fertig ✅',
                'message': 'Deine Bestellung ist fertig und wartet auf die Abholung!',
                'emoji': '📦'
            },
            'out_for_delivery': {
                'title': 'Bestellung unterwegs 🚗',
                'message': 'Deine Bestellung ist auf dem Weg zu dir!',
                'emoji': '🚚'
            },
            'delivered': {
                'title': 'Bestellung zugestellt 🎉',
                'message': 'Deine Bestellung wurde zugestellt. Guten Appetit!',
                'emoji': '✨'
            }
        }
        
        status_info = status_messages.get(status, {
            'title': 'Bestellstatus aktualisiert',
            'message': f'Status: {status}',
            'emoji': '📱'
        })
        
        # Build email content
        content = f"""
            <h2 style="color: #dc2626; margin-top: 0;">{status_info['title']}</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Hallo {customer_name},
            </p>
            <p style="font-size: 18px; line-height: 1.6; color: #fff; font-weight: 600;">
                {status_info['message']}
            </p>
            
            <div style="background-color: #2a2a2a; padding: 20px; border-radius: 12px; margin: 25px 0; border-left: 4px solid #dc2626;">
                <p style="margin: 0; font-size: 14px; color: #999;">Bestellnummer</p>
                <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: white;">{order_number}</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="{APP_URL}/orders" class="button">
                    Bestellstatus verfolgen
                </a>
            </div>
            
            <p style="font-size: 14px; color: #999; margin-top: 30px;">
                Dein ZOZO Burger Team
            </p>
        """
        
        html_content = EmailTemplates.get_base_template(content, f"Status Update: {status_info['title']}")
        
        # Send email via Resend
        params = {
            "from": SENDER_EMAIL,
            "to": [customer_email],
            "subject": f"ZOZO Burger - {status_info['title']} (Bestellung {order_number})",
            "html": html_content
        }
        
        response = resend.Emails.send(params)
        logger.info(f"Status update email sent to {customer_email}: {response.get('id')}")
        return True
        
    except Exception as e:
        logger.error(f"send_status_update_email error for order {order.get('order_id')}: {str(e)}")
        return False

def send_review_request_email(order: dict, location: dict) -> bool:
    """Legacy stub - sends review request email"""
    try:
        # This is a stub - implement if needed
        logger.warning(f"send_review_request_email called (stub) for order {order.get('order_id')}")
        return True
    except Exception as e:
        logger.error(f"send_review_request_email error: {str(e)}")
        return False

def send_order_confirmation_email(order: dict, location: dict) -> bool:
    """Send order confirmation email"""
    try:
        customer_email = order.get('customer_email')
        if not customer_email:
            logger.warning(f"No customer email for order {order.get('order_id')}")
            return False
        
        customer_name = order.get('customer_name', 'Kunde')
        order_number = order.get('order_number', order.get('order_id', 'N/A'))
        order_total = order.get('total', 0)
        delivery_address = order.get('delivery_address', 'Nicht angegeben')
        delivery_time = order.get('delivery_time', 'Schnellstmöglich')
        
        # Build items list
        items_html = ""
        for item in order.get('items', []):
            item_name = item.get('name', 'Unbekannt')
            item_price = item.get('price', 0)
            item_qty = item.get('quantity', 1)
            
            items_html += f"""
                <div style="padding: 12px 0; border-bottom: 1px solid #333;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="color: #fff; font-weight: 600;">{item_qty}x {item_name}</span>
                        <span style="color: #dc2626; font-weight: 600;">€{item_price:.2f}</span>
                    </div>
            """
            
            # Add customizations
            customizations = item.get('customizations', [])
            if customizations:
                for custom in customizations:
                    items_html += f'<div style="font-size: 13px; color: #999; margin-left: 20px;">• {custom}</div>'
            
            # Add removed ingredients
            removed = item.get('removed_ingredients', [])
            if removed:
                for removal in removed:
                    items_html += f'<div style="font-size: 13px; color: #f87171; margin-left: 20px;">- Ohne {removal}</div>'
            
            items_html += "</div>"
        
        # Build email content
        content = f"""
            <h2 style="color: #dc2626; margin-top: 0;">Bestellung bestätigt! 🎉</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                Hallo {customer_name},
            </p>
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5;">
                vielen Dank für deine Bestellung! Wir haben sie erhalten und bereiten sie jetzt zu.
            </p>
            
            <div style="background-color: #2a2a2a; padding: 20px; border-radius: 12px; margin: 25px 0; border: 2px solid #dc2626;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <span style="color: #999;">Bestellnummer:</span>
                    <span style="color: #fff; font-weight: bold;">{order_number}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <span style="color: #999;">Lieferadresse:</span>
                    <span style="color: #fff;">{delivery_address}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #999;">Lieferzeit:</span>
                    <span style="color: #fff;">{delivery_time}</span>
                </div>
            </div>
            
            <h3 style="color: #dc2626; margin: 30px 0 15px 0;">Deine Bestellung:</h3>
            <div style="background-color: #1a1a1a; padding: 20px; border-radius: 12px;">
                {items_html}
                <div style="padding-top: 20px; border-top: 2px solid #dc2626; margin-top: 15px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #fff; font-size: 18px; font-weight: bold;">Gesamtbetrag:</span>
                        <span style="color: #dc2626; font-size: 24px; font-weight: bold;">€{order_total:.2f}</span>
                    </div>
                </div>
            </div>
            
            <p style="font-size: 16px; line-height: 1.6; color: #e5e5e5; margin-top: 30px;">
                Wir melden uns, sobald deine Bestellung auf dem Weg ist! 🚗
            </p>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="{APP_URL}/orders" class="button">
                    Bestellstatus verfolgen
                </a>
            </div>
            
            <p style="font-size: 14px; color: #999; margin-top: 30px;">
                Guten Appetit!<br>
                Dein ZOZO Burger Team
            </p>
        """
        
        html_content = EmailTemplates.get_base_template(content, f"Bestellung {order_number} bestätigt")
        
        # Send email via Resend
        params = {
            "from": SENDER_EMAIL,
            "to": [customer_email],
            "subject": f"ZOZO Burger - Bestellung {order_number} bestätigt",
            "html": html_content
        }
        
        response = resend.Emails.send(params)
        logger.info(f"Order confirmation email sent to {customer_email}: {response.get('id')}")
        return True
        
    except Exception as e:
        logger.error(f"send_order_confirmation_email error for order {order.get('order_id')}: {str(e)}")
        return False

def send_group_order_invite_email(group_order: dict, invitee_email: str) -> bool:
    """Legacy stub - sends group order invite email"""
    try:
        # This is a stub - implement if needed
        logger.warning(f"send_group_order_invite_email called (stub) for {invitee_email}")
        return True
    except Exception as e:
        logger.error(f"send_group_order_invite_email error: {str(e)}")
        return False

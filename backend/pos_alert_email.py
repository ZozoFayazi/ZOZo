"""POS Failure Alert Email Service"""
import os
import logging
from typing import Dict, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# Check if detailed alerts are enabled (DSGVO-sensitive)
INCLUDE_ORDER_DETAILS = os.getenv('INCLUDE_ORDER_DETAILS_IN_ALERT_EMAIL', 'false').lower() == 'true'
ALERT_EMAIL_PRIMARY = os.getenv('POS_ALERT_EMAIL', 'info@zozo-burger.de')


async def send_pos_failure_alert(
    db: AsyncIOMotorDatabase,
    order_number: str,
    location_slug: str,
    error: str,
    error_type: str,
    order_data: Dict,
    retry_count: int
):
    """
    Send alert email when POS push fails after all retries
    
    Args:
        db: Database connection
        order_number: Order number (e.g. ZOZO-1025)
        location_slug: Location identifier
        error: Error message
        error_type: 'hard' or 'soft'
        order_data: Full order data (used if INCLUDE_ORDER_DETAILS=true)
        retry_count: Number of retry attempts
    """
    try:
        # Get location details for email recipient
        location = await db.locations.find_one({"slug": location_slug})
        if not location:
            logger.error(f"Location not found for alert email: {location_slug}")
            return
        
        location_name = location.get('name', location_slug)
        location_email = location.get('email')
        
        # Determine recipients
        recipients = [ALERT_EMAIL_PRIMARY]
        if location_email and location_email != ALERT_EMAIL_PRIMARY:
            recipients.append(location_email)
        
        # Build email subject
        subject = f"🚨 [KRITISCH] POS FEHLER – Bestellung {order_number} nicht übertragen ({location_name})"
        
        # Build email body
        error_type_label = "Verbindungsfehler" if error_type == "hard" else "API-Fehler"
        total = order_data.get('total', 0)
        payment_method = order_data.get('payment_method', 'Unbekannt')
        
        # Basic info (always included)
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #fff; padding: 20px;">
            <div style="background: #dc2626; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">⚠️ POS-Übertragung fehlgeschlagen</h1>
            </div>
            
            <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 15px; margin: 20px 0; border-radius: 6px;">
                <p style="margin: 0; color: #991b1b; font-weight: bold;">
                    Eine bezahlte Bestellung konnte nicht an das Kassensystem übertragen werden!
                </p>
            </div>
            
            <div style="background: #f9fafb; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                <h2 style="margin: 0 0 15px 0; font-size: 18px; color: #111827;">Bestellinformationen</h2>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #6b7280; width: 140px;">Bestellung:</td>
                        <td style="padding: 8px 0; font-weight: bold;">{order_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #6b7280;">Standort:</td>
                        <td style="padding: 8px 0;">{location_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #6b7280;">Betrag:</td>
                        <td style="padding: 8px 0; font-weight: bold;">€{total:.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #6b7280;">Zahlungsart:</td>
                        <td style="padding: 8px 0;">{payment_method}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #6b7280;">Fehlertyp:</td>
                        <td style="padding: 8px 0;"><span style="background: #fef2f2; color: #dc2626; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{error_type_label}</span></td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #6b7280;">Auto-Retries:</td>
                        <td style="padding: 8px 0;">{retry_count} Versuche</td>
                    </tr>
                </table>
            </div>
            
            <div style="background: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin-bottom: 20px;">
                <p style="margin: 0 0 5px 0; font-weight: bold; color: #991b1b;">Fehlermeldung:</p>
                <p style="margin: 0; color: #991b1b; font-family: monospace; font-size: 13px;">{error}</p>
            </div>
        """
        
        # Add detailed order info if enabled
        if INCLUDE_ORDER_DETAILS:
            html_body += """
            <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; margin-bottom: 20px; border-radius: 6px;">
                <p style="margin: 0; color: #856404; font-size: 12px;">
                    ⚠️ <strong>Datenschutzhinweis:</strong> Diese E-Mail enthält Kundendaten. Nur intern verwenden!
                </p>
            </div>
            
            <div style="background: #f9fafb; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                <h3 style="margin: 0 0 10px 0; font-size: 16px;">Kundeninformationen</h3>
            """
            
            customer_name = order_data.get('customer_name', 'N/A')
            customer_phone = order_data.get('customer_phone', 'N/A')
            delivery_address = order_data.get('delivery_address', 'N/A')
            
            html_body += f"""
                <p style="margin: 5px 0;"><strong>Name:</strong> {customer_name}</p>
                <p style="margin: 5px 0;"><strong>Telefon:</strong> {customer_phone}</p>
                <p style="margin: 5px 0;"><strong>Adresse:</strong> {delivery_address}</p>
            </div>
            
            <div style="background: #f9fafb; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                <h3 style="margin: 0 0 10px 0; font-size: 16px;">Bestellpositionen</h3>
                <ul style="margin: 0; padding-left: 20px;">
            """
            
            items = order_data.get('items', [])
            for item in items:
                item_name = item.get('name', 'Unbekannt')
                item_qty = item.get('quantity', 1)
                item_price = item.get('price', 0)
                size = item.get('size', '')
                size_text = f" ({size})" if size else ""
                
                html_body += f"""
                    <li style="margin: 5px 0;">{item_qty}x {item_name}{size_text} - €{item_price:.2f}</li>
                """
            
            html_body += """
                </ul>
            </div>
            """
        
        # Action button
        admin_url = "https://zozo-cashx-pos.preview.emergentagent.com/admin/pos/failed-orders"
        
        html_body += f"""
            <div style="background: #dbeafe; border: 1px solid #3b82f6; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                <p style="margin: 0 0 10px 0; color: #1e40af;">
                    ✅ <strong>Die Bestellung wurde lokal gespeichert.</strong> Kein Umsatz geht verloren!
                </p>
                <p style="margin: 0; color: #1e40af; font-size: 14px;">
                    Sie können die Bestellung manuell über das Admin-Panel an das POS senden.
                </p>
            </div>
            
            <a href="{admin_url}" 
               style="display: inline-block; background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                Im Admin-Panel prüfen →
            </a>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center;">
                <p style="margin: 0; color: #6b7280; font-size: 12px;">
                    ZOZO Burger | Automatische System-Benachrichtigung<br>
                    <a href="{admin_url}" style="color: #3b82f6;">Admin-Panel öffnen</a>
                </p>
            </div>
        </div>
        """
        
        # Send email via Resend
        try:
            import resend
            
            resend.api_key = os.environ.get('RESEND_API_KEY')
            use_test_domain = os.getenv('RESEND_USE_TEST_DOMAIN', 'false').lower() == 'true'
            
            sender_email = "onboarding@resend.dev" if use_test_domain else "noreply@zozo-burger.de"
            
            params = {
                "from": f"ZOZO Burger Alert <{sender_email}>",
                "to": recipients,
                "subject": subject,
                "html": html_body
            }
            
            email = resend.Emails.send(params)
            logger.info(f"POS failure alert sent for {order_number} to {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send POS alert email: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Error in send_pos_failure_alert: {str(e)}")
        return False

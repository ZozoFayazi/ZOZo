"""
Email Templates for ZOZO Burger Order Confirmations
Complete, production-ready templates with all order details
"""

def get_order_confirmation_html(order: dict, location: dict) -> str:
    """
    Generate complete order confirmation email HTML
    Shows ALL details: items, modifiers, payment, delivery, etc.
    """
    customer = order.get('customer', {})
    items = order.get('items', [])
    is_pickup = order.get('is_pickup', False)
    
    # Build items HTML with modifiers expanded
    items_html = ""
    for item in items:
        quantity = item.get('quantity', 1)
        name = item.get('name', '')
        price = item.get('price', 0)
        size = item.get('size', '')
        
        # Main item
        size_text = f" ({size})" if size else ""
        items_html += f"""
        <tr style="background-color: #1e1e1e;">
            <td style="padding: 12px; border-bottom: 1px solid #333; color: #ffffff; font-weight: 600;">
                {quantity}x {name}{size_text}
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #333; text-align: right; color: #ffffff; font-weight: 600;">
                €{(price * quantity):.2f}
            </td>
        </tr>
        """
        
        # Modifiers (from modifiers{} object)
        modifiers = item.get('modifiers', {})
        if modifiers:
            for group_id, mod_data in modifiers.items():
                if isinstance(mod_data, dict):
                    mod_name = mod_data.get('name', '')
                    mod_price = mod_data.get('price', 0.0)
                    
                    price_text = f" (+€{mod_price:.2f})" if mod_price > 0 else ""
                    
                    items_html += f"""
                    <tr style="background-color: #1a1a1a;">
                        <td style="padding: 8px 12px 8px 30px; border-bottom: 1px solid #2a2a2a; color: #a0a0a0; font-size: 14px;">
                            → {mod_name}{price_text}
                        </td>
                        <td style="padding: 8px 12px; border-bottom: 1px solid #2a2a2a; text-align: right; color: #a0a0a0; font-size: 14px;">
                        </td>
                    </tr>
                    """
        
        # Customizations (legacy string array)
        customizations = item.get('customizations', [])
        for custom in customizations:
            if isinstance(custom, str):
                items_html += f"""
                <tr style="background-color: #1a1a1a;">
                    <td style="padding: 8px 12px 8px 30px; border-bottom: 1px solid #2a2a2a; color: #a0a0a0; font-size: 14px;">
                        → {custom}
                    </td>
                    <td style="padding: 8px 12px; border-bottom: 1px solid #2a2a2a;"></td>
                </tr>
                """
        
        # Extras
        extras = item.get('extras', [])
        for extra in extras:
            if isinstance(extra, dict):
                extra_name = extra.get('name', '')
                extra_price = extra.get('price', 0.0)
                items_html += f"""
                <tr style="background-color: #1a1a1a;">
                    <td style="padding: 8px 12px 8px 30px; border-bottom: 1px solid #2a2a2a; color: #a0a0a0; font-size: 14px;">
                        + {extra_name}
                    </td>
                    <td style="padding: 8px 12px; border-bottom: 1px solid #2a2a2a; text-align: right; color: #a0a0a0; font-size: 14px;">
                        €{extra_price:.2f}
                    </td>
                </tr>
                """
        
        # Removed ingredients
        removed = item.get('removed_ingredients', [])
        for removal in removed:
            items_html += f"""
            <tr style="background-color: #1a1a1a;">
                <td style="padding: 8px 12px 8px 30px; border-bottom: 1px solid #2a2a2a; color: #888; font-size: 14px; font-style: italic;">
                    - Ohne {removal}
                </td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #2a2a2a;"></td>
            </tr>
            """
    
    # Order date/time
    created_at = order.get('created_at')
    if created_at:
        from datetime import datetime
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        order_date = created_at.strftime('%d.%m.%Y')
        order_time = created_at.strftime('%H:%M')
    else:
        order_date = 'N/A'
        order_time = 'N/A'
    
    # Calculate points earned
    points_earned = order.get('points_earned', int(order.get('total', 0) / 10))
    
    # Payment method display
    payment_method_map = {
        'cash': 'Barzahlung',
        'card': 'Kartenzahlung',
        'paypal': 'PayPal'
    }
    payment_method = payment_method_map.get(order.get('payment_method', 'cash'), order.get('payment_method', 'Barzahlung'))
    
    # PayPal transaction ID if available
    paypal_transaction = order.get('paypal_transaction_id', '')
    paypal_info = f"""
        <p style="color: #a0a0a0; font-size: 14px; margin-top: 5px;">
            Transaktions-ID: {paypal_transaction}
        </p>
    """ if paypal_transaction else ""
    
    # Delivery address HTML (only for delivery orders)
    delivery_address_html = ""
    if not is_pickup:
        delivery_address_html = f"""
        <div style="background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #dc2626; font-size: 16px; margin: 0 0 12px 0; font-weight: 600;">📍 Lieferadresse</h3>
            <p style="color: #ffffff; margin: 0; line-height: 1.6;">
                {customer.get('name', '')}<br>
                {customer.get('address', '')}<br>
                {customer.get('postal_code', '')} {customer.get('city', '')}
            </p>
            {f'<p style="color: #a0a0a0; margin-top: 8px; font-size: 14px;">Hinweis: {customer.get("notes", "")}</p>' if customer.get('notes') else ''}
        </div>
        """
    
    # Contact info
    location_phone = location.get('phone', '04101 39 84 850')
    location_name = location.get('name', 'ZOZO Burger')
    location_address = f"{location.get('address', '')}, {location.get('postal_code', '')} {location.get('city', '')}"
    
    # Build complete HTML
    logo_url = "https://customer-assets.emergentagent.com/job_zozofinal/artifacts/ucrdxkwy_IMG_8154.jpeg"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bestellbestätigung</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif; background-color: #0a0a0a; color: #ffffff;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0a0a0a;">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%; background-color: #1a1a1a; border-radius: 12px; overflow: hidden;">
                        
                        <!-- Header with Logo -->
                        <tr>
                            <td style="background-color: #1a1a1a; padding: 30px 20px; text-align: center;">
                                <img src="{logo_url}" alt="ZOZO Burger" style="max-width: 100px; height: auto; display: block; margin: 0 auto;">
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px; background-color: #1a1a1a;">
                                
                                <!-- Title -->
                                <h1 style="color: #dc2626; font-size: 28px; margin: 0 0 10px 0; text-align: center; font-weight: bold;">
                                    ✅ Bestellung bestätigt!
                                </h1>
                                <p style="color: #e5e5e5; font-size: 16px; text-align: center; margin: 0 0 30px 0;">
                                    Vielen Dank für deine Bestellung bei ZOZO Burger!
                                </p>
                                
                                <!-- Order Info Box -->
                                <div style="background-color: #dc2626; border-radius: 8px; padding: 20px; margin: 0 0 30px 0;">
                                    <p style="color: #ffffff; margin: 0 0 8px 0; font-size: 14px;">
                                        <strong style="font-size: 16px;">📋 Bestellnummer:</strong> {order.get('order_number')}
                                    </p>
                                    <p style="color: #ffffff; margin: 0 0 8px 0; font-size: 14px;">
                                        <strong>📅 Datum:</strong> {order_date} um {order_time} Uhr
                                    </p>
                                    <p style="color: #ffffff; margin: 0 0 8px 0; font-size: 14px;">
                                        <strong>🏪 Filiale:</strong> {location_name}
                                    </p>
                                    <p style="color: #ffffff; margin: 0; font-size: 14px;">
                                        <strong>{'📦 Abholung' if is_pickup else '🚚 Lieferung'}:</strong> ca. {order.get('estimated_time', 30)} Minuten
                                    </p>
                                </div>
                                
                                <!-- Delivery Address (if delivery) -->
                                {delivery_address_html}
                                
                                <!-- Customer Info -->
                                <div style="background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 20px; margin: 0 0 30px 0;">
                                    <h3 style="color: #dc2626; font-size: 16px; margin: 0 0 12px 0; font-weight: 600;">👤 Kontaktdaten</h3>
                                    <p style="color: #ffffff; margin: 0;">
                                        {customer.get('name', '')}<br>
                                        {customer.get('phone', '')}<br>
                                        {customer.get('email', '')}
                                    </p>
                                </div>
                                
                                <!-- Items Table -->
                                <h2 style="color: #dc2626; font-size: 20px; margin: 0 0 15px 0; font-weight: 600;">📋 Deine Bestellung</h2>
                                <table width="100%" cellpadding="0" cellspacing="0" style="width: 100%; border-collapse: collapse; margin: 0 0 30px 0; background-color: #1e1e1e; border-radius: 8px; overflow: hidden;">
                                    {items_html}
                                    
                                    <!-- Subtotal -->
                                    <tr>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; color: #a0a0a0;">
                                            Zwischensumme
                                        </td>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; text-align: right; color: #a0a0a0;">
                                            €{order.get('subtotal', 0):.2f}
                                        </td>
                                    </tr>
                                    
                                    <!-- Delivery Fee -->
                                    {f'''
                                    <tr>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; color: #a0a0a0;">
                                            Liefergebühr
                                        </td>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; text-align: right; color: #a0a0a0;">
                                            €{order.get('delivery_fee', 0):.2f}
                                        </td>
                                    </tr>
                                    ''' if order.get('delivery_fee', 0) > 0 else ''}
                                    
                                    <!-- Pickup Discount -->
                                    {f'''
                                    <tr>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; color: #10b981;">
                                            Abholrabatt (10%)
                                        </td>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; text-align: right; color: #10b981;">
                                            -€{order.get('pickup_discount', 0):.2f}
                                        </td>
                                    </tr>
                                    ''' if order.get('pickup_discount', 0) > 0 else ''}
                                    
                                    <!-- Daily Deal Discount -->
                                    {f'''
                                    <tr>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; color: #10b981;">
                                            Tagesangebot ({order.get('daily_deal_info', 'Rabatt')})
                                        </td>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; text-align: right; color: #10b981;">
                                            -€{order.get('daily_deal_discount', 0):.2f}
                                        </td>
                                    </tr>
                                    ''' if order.get('daily_deal_discount', 0) > 0 else ''}
                                    
                                    <!-- Points Discount -->
                                    {f'''
                                    <tr>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; color: #10b981;">
                                            Treuepunkte ({order.get('points_redeemed', 0)} Punkte)
                                        </td>
                                        <td style="padding: 12px; border-bottom: 1px solid #333; text-align: right; color: #10b981;">
                                            -€{order.get('discount', 0):.2f}
                                        </td>
                                    </tr>
                                    ''' if order.get('points_redeemed', 0) > 0 else ''}
                                    
                                    <!-- Total -->
                                    <tr style="font-weight: bold; font-size: 20px;">
                                        <td style="padding: 20px 12px; border-top: 2px solid #dc2626; color: #ffffff;">
                                            Gesamt
                                        </td>
                                        <td style="padding: 20px 12px; border-top: 2px solid #dc2626; text-align: right; color: #dc2626;">
                                            €{order.get('total', 0):.2f}
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Payment Info -->
                                <div style="background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 20px; margin: 0 0 30px 0;">
                                    <h3 style="color: #dc2626; font-size: 16px; margin: 0 0 12px 0; font-weight: 600;">💳 Zahlung</h3>
                                    <p style="color: #ffffff; margin: 0; font-size: 14px;">
                                        <strong>Zahlungsart:</strong> {payment_method}
                                    </p>
                                    {paypal_info}
                                </div>
                                
                                <!-- Loyalty Points -->
                                {f'''
                                <div style="background-color: #4f46e5; border-radius: 8px; padding: 20px; margin: 0 0 30px 0;">
                                    <p style="color: #ffffff; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">
                                        🎁 Du hast {points_earned} Treuepunkte verdient!
                                    </p>
                                    <p style="color: #e0e0ff; margin: 0; font-size: 14px;">
                                        Sammle Punkte und sichere dir leckere Belohnungen!
                                    </p>
                                </div>
                                ''' if points_earned > 0 else ''}
                                
                                <!-- Important Note -->
                                <div style="background-color: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 20px; margin: 0 0 30px 0;">
                                    <p style="color: #92400e; margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">
                                        ⚠️ Bitte prüfe deine Angaben
                                    </p>
                                    <p style="color: #92400e; margin: 0; font-size: 14px; line-height: 1.6;">
                                        Falls etwas nicht stimmt oder du Fragen hast, ruf uns bitte sofort an:<br>
                                        <strong style="font-size: 16px;">{location_phone}</strong>
                                    </p>
                                </div>
                                
                                <!-- Footer -->
                                <div style="text-align: center; padding-top: 20px; border-top: 1px solid #333;">
                                    <p style="color: #a0a0a0; font-size: 14px; margin: 0 0 10px 0;">
                                        {location_name}<br>
                                        {location_address}
                                    </p>
                                    <p style="color: #a0a0a0; font-size: 14px; margin: 0;">
                                        Wir bereiten deine Bestellung bereits zu! 🔥
                                    </p>
                                </div>
                                
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return html

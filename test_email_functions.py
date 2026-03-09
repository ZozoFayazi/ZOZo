#!/usr/bin/env python3
"""
E-Mail Test-Skript
Testet die E-Mail-Funktionen mit echten Beispieldaten
"""
import sys
sys.path.insert(0, '/app/backend')

from email_service import send_verification_email, send_order_confirmation_email, send_status_update_email
from datetime import datetime, timezone

def test_verification_email():
    print("\n" + "="*80)
    print("TEST 1: VERIFIZIERUNGS-E-MAIL")
    print("="*80)
    
    test_email = "test@example.com"  # Ändern Sie diese zu einer echten E-Mail zum Testen
    test_code = "ABC123"
    
    print(f"Sende Verifizierungs-E-Mail an: {test_email}")
    print(f"Code: {test_code}")
    
    success = send_verification_email(test_email, test_code)
    
    if success:
        print("✅ Verifizierungs-E-Mail wurde erfolgreich gesendet!")
    else:
        print("❌ Fehler beim Senden der Verifizierungs-E-Mail")
    
    return success

def test_order_confirmation():
    print("\n" + "="*80)
    print("TEST 2: BESTELLBESTÄTIGUNGS-E-MAIL")
    print("="*80)
    
    test_order = {
        'order_id': 'TEST-001',
        'order_number': 'ZOZO-9999',
        'customer_email': 'test@example.com',  # Ändern Sie diese zu einer echten E-Mail
        'customer_name': 'Max Mustermann',
        'total': 28.50,
        'delivery_address': 'Teststraße 123, 12345 Teststadt',
        'delivery_time': 'Heute, 18:30 - 19:00',
        'items': [
            {
                'name': 'Champion Burger Medium 125g Menü',
                'price': 16.09,
                'quantity': 1,
                'customizations': ['+ Sesam Brötchen', '+ Pommes', '+ Cola 0,5l'],
                'removed_ingredients': ['Zwiebeln', 'Gurken']
            },
            {
                'name': 'Caesar Salad',
                'price': 9.19,
                'quantity': 1,
                'customizations': ['+ Extra Parmesan'],
                'removed_ingredients': []
            }
        ]
    }
    
    test_location = {
        'name': 'Rellingen',
        'slug': 'rellingen'
    }
    
    print(f"Sende Bestellbestätigung an: {test_order['customer_email']}")
    print(f"Bestellung: {test_order['order_number']}")
    print(f"Gesamt: €{test_order['total']:.2f}")
    
    success = send_order_confirmation_email(test_order, test_location)
    
    if success:
        print("✅ Bestellbestätigungs-E-Mail wurde erfolgreich gesendet!")
    else:
        print("❌ Fehler beim Senden der Bestellbestätigungs-E-Mail")
    
    return success

def test_status_update():
    print("\n" + "="*80)
    print("TEST 3: STATUS-UPDATE E-MAIL")
    print("="*80)
    
    test_order = {
        'order_id': 'TEST-001',
        'order_number': 'ZOZO-9999',
        'customer_email': 'test@example.com',  # Ändern Sie diese zu einer echten E-Mail
        'customer_name': 'Max Mustermann'
    }
    
    test_location = {
        'name': 'Rellingen',
        'slug': 'rellingen'
    }
    
    status = 'out_for_delivery'  # preparing, ready, out_for_delivery, delivered
    
    print(f"Sende Status-Update an: {test_order['customer_email']}")
    print(f"Status: {status}")
    
    success = send_status_update_email(test_order, status, test_location)
    
    if success:
        print("✅ Status-Update E-Mail wurde erfolgreich gesendet!")
    else:
        print("❌ Fehler beim Senden der Status-Update E-Mail")
    
    return success

def main():
    print("\n")
    print("🚀 ZOZO BURGER E-MAIL TEST SUITE")
    print("="*80)
    print("\n⚠️  WICHTIG: Ändern Sie die test@example.com zu einer echten E-Mail!")
    print("    Bearbeiten Sie /app/test_email_functions.py\n")
    
    results = {
        'verification': test_verification_email(),
        'confirmation': test_order_confirmation(),
        'status_update': test_status_update()
    }
    
    print("\n" + "="*80)
    print("ZUSAMMENFASSUNG")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n✅ Erfolgreich: {passed}/{total}")
    print(f"❌ Fehlgeschlagen: {total - passed}/{total}\n")
    
    if passed == total:
        print("🎉 ALLE TESTS BESTANDEN!")
        print("\nNächste Schritte:")
        print("1. Re-deployen Sie die Anwendung")
        print("2. Testen Sie mit echten Kundenbestellungen")
        print("3. Prüfen Sie, ob E-Mails ankommen")
    else:
        print("⚠️  EINIGE TESTS FEHLGESCHLAGEN")
        print("\nÜberprüfen Sie:")
        print("1. RESEND_API_KEY in .env korrekt?")
        print("2. SENDER_EMAIL verifiziert bei Resend?")
        print("3. Backend-Logs für Details:")
        print("   tail -n 100 /var/log/supervisor/backend.err.log")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()

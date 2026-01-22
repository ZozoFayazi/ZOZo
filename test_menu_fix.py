#!/usr/bin/env python3
"""
Test-Skript: ExpertOrder Menü-Struktur Validierung
Überprüft, ob die Sauce-Fix und pos_push_history-Fix aktiv sind
"""

import os
from pymongo import MongoClient
import json
from datetime import datetime

def main():
    print("="*80)
    print("EXPERTORDER MENÜ-FIX VALIDIERUNG")
    print("="*80)
    
    # 1. Code-Dateien prüfen
    print("\n1. CODE-DATEIEN PRÜFUNG")
    print("-"*80)
    
    expertorder_path = "/app/backend/pos_connectors/expertorder.py"
    pos_service_path = "/app/backend/pos_service.py"
    
    # Check if sauce logic exists
    if os.path.exists(expertorder_path):
        with open(expertorder_path, 'r') as f:
            content = f.read()
            
        if "SAUCE/DIP" in content and "is_sauce" in content:
            print("✅ Sauce-Fix in expertorder.py gefunden")
        else:
            print("❌ Sauce-Fix NICHT gefunden in expertorder.py")
            print("   Code muss neu deployed werden!")
    else:
        print(f"❌ {expertorder_path} nicht gefunden")
    
    # Check if pos_push_history is saved
    if os.path.exists(pos_service_path):
        with open(pos_service_path, 'r') as f:
            content = f.read()
            
        if '"pos_push_history"' in content and "$push" in content:
            print("✅ pos_push_history-Fix in pos_service.py gefunden")
        else:
            print("❌ pos_push_history-Fix NICHT gefunden in pos_service.py")
            print("   Code muss neu deployed werden!")
    else:
        print(f"❌ {pos_service_path} nicht gefunden")
    
    # 2. Datenbank-Analyse
    print("\n2. DATENBANK-ANALYSE")
    print("-"*80)
    
    try:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        
        # Get latest order
        latest_order = db.orders.find_one(sort=[('created_at', -1)])
        
        if not latest_order:
            print("❌ Keine Bestellungen in der Datenbank gefunden")
            print("   Bitte Testbestellung durchführen")
            client.close()
            return
        
        print(f"Neueste Bestellung: {latest_order.get('order_number', 'N/A')}")
        print(f"Erstellt: {latest_order.get('created_at')}")
        
        # Check items structure
        items = latest_order.get('items', [])
        if not items:
            print("❌ Bestellung hat keine Items")
            client.close()
            return
        
        first_item = items[0]
        item_name = first_item.get('name', '')
        
        print(f"\nItem: {item_name}")
        
        # Check if it's a menu
        is_menu = 'menü' in item_name.lower() or 'menu' in item_name.lower()
        
        if is_menu:
            print("✅ Menü erkannt")
            
            # Check modifiers
            modifiers = first_item.get('modifiers', {})
            
            if modifiers:
                print(f"\n✅ Modifiers vorhanden ({len(modifiers)} Typen):")
                
                has_beilage = 'beilage' in modifiers
                has_getraenk = 'getraenk' in modifiers
                has_sauce = 'sauce' in modifiers
                
                if has_beilage:
                    print(f"  ✅ Beilage: {modifiers['beilage'].get('name')}")
                else:
                    print("  ❌ Beilage FEHLT")
                
                if has_getraenk:
                    print(f"  ✅ Getränk: {modifiers['getraenk'].get('name')}")
                else:
                    print("  ❌ Getränk FEHLT")
                
                if has_sauce:
                    print(f"  ✅ Sauce: {modifiers['sauce'].get('name')}")
                else:
                    print("  ⚠️ Sauce FEHLT (oder nicht gewählt)")
                
                # Summary
                if has_beilage and has_getraenk:
                    print("\n✅ DATENBANK-STRUKTUR IST KORREKT")
                else:
                    print("\n❌ DATENBANK-STRUKTUR UNVOLLSTÄNDIG")
            else:
                print("❌ KEINE Modifiers - Menü-Struktur fehlt komplett!")
        else:
            print("⚠️ Kein Menü - normales Item")
        
        # Check pos_push_history
        print("\n3. POS PUSH HISTORY")
        print("-"*80)
        
        push_history = latest_order.get('pos_push_history', [])
        
        if push_history:
            print(f"✅ pos_push_history vorhanden ({len(push_history)} Einträge)")
            
            latest_push = push_history[-1]
            print(f"\nNeuester Push:")
            print(f"  Status: {latest_push.get('status')}")
            print(f"  Timestamp: {latest_push.get('timestamp')}")
            print(f"  Provider: {latest_push.get('provider')}")
            
            # Check if payload exists
            if 'payload' in latest_push:
                print("  ✅ Payload gespeichert")
                
                # Analyze payload
                payload = latest_push['payload']
                payload_items = payload.get('items', [])
                
                if payload_items:
                    first_payload_item = payload_items[0]
                    print(f"\n  Payload Item: {first_payload_item.get('name')}")
                    
                    # Check if it has nested items (children)
                    nested_items = first_payload_item.get('items', [])
                    
                    if nested_items:
                        print(f"  ✅ Verschachtelte Items gefunden ({len(nested_items)} Komponenten):")
                        
                        for nested in nested_items:
                            print(f"    - {nested.get('name')}")
                        
                        # Check if sauce is in nested items
                        has_sauce_in_payload = any('sauce' in item.get('name', '').lower() or 
                                                   'ketchup' in item.get('name', '').lower() or
                                                   'mayo' in item.get('name', '').lower()
                                                   for item in nested_items)
                        
                        if has_sauce_in_payload:
                            print("\n  ✅ SAUCE IM PAYLOAD GEFUNDEN - FIX FUNKTIONIERT!")
                        else:
                            print("\n  ⚠️ Sauce im Payload nicht gefunden")
                            print("     (Möglicherweise keine Sauce gewählt)")
                    else:
                        print("  ⚠️ KEINE verschachtelten Items im Payload")
                        print("     Menü-Komponenten werden NICHT gesendet!")
                        print("\n  ❌ EXPERTORDER-FIX FUNKTIONIERT NICHT!")
            else:
                print("  ❌ Payload NICHT gespeichert")
        else:
            print("❌ pos_push_history ist LEER")
            print("   Fix wurde entweder:")
            print("   1. Noch nicht deployed")
            print("   2. Bestellung wurde vor dem Fix erstellt")
            print("   3. Bestellung wurde nicht an POS gesendet")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Fehler bei Datenbankverbindung: {str(e)}")
    
    print("\n" + "="*80)
    print("ZUSAMMENFASSUNG")
    print("="*80)
    print("""
WENN ALLE CHECKS ✅ SIND:
  → Fixes sind aktiv und funktionieren
  → Neue Bestellungen sollten korrekt an ExpertOrder gesendet werden

WENN CHECKS ❌ SIND:
  → Code muss neu deployed werden
  → Führen Sie nach Deployment eine neue Testbestellung durch
  → Führen Sie dieses Skript erneut aus

TESTBESTELLUNG EMPFOHLEN:
  1. Menü bestellen (z.B. Champion Burger Medium Menü)
  2. Beilage wählen (Pommes)
  3. Getränk wählen (Cola)  
  4. Sauce wählen (Ketchup)
  5. Bestellung absenden
  6. Dieses Skript erneut ausführen
  7. Kassenbon prüfen
    """)

if __name__ == "__main__":
    main()

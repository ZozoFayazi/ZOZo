#!/usr/bin/env python3
"""
DEPLOYMENT-STATUS CHECKER
Prüft, ob die neuesten Fixes auf dem System aktiv sind
"""

import os
import sys

def check_file_content(filepath, search_strings, file_description):
    """Check if file contains expected strings"""
    print(f"\n{'='*80}")
    print(f"CHECKING: {file_description}")
    print(f"File: {filepath}")
    print(f"{'='*80}")
    
    if not os.path.exists(filepath):
        print(f"❌ FILE NOT FOUND!")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    all_found = True
    for search_str in search_strings:
        if search_str in content:
            print(f"✅ FOUND: '{search_str[:60]}...'")
        else:
            print(f"❌ MISSING: '{search_str[:60]}...'")
            all_found = False
    
    return all_found

def main():
    print("\n" + "="*80)
    print("ZOZO BURGER DEPLOYMENT STATUS CHECK")
    print("="*80)
    print("\nThis script checks if the latest bug fixes are deployed.\n")
    
    results = {}
    
    # Check 1: Frontend - Menü-Fix in ProductCustomizer
    results['frontend_menu_fix'] = check_file_content(
        '/app/frontend/src/components/ProductCustomizer.jsx',
        [
            'Build menu modifiers separately',
            'menuModifiers.beilage',
            'menuModifiers.getraenk',
            '...selectedModifiers, ...menuModifiers'
        ],
        'Frontend Menü-Fix'
    )
    
    # Check 2: Backend - Sauce-Fix in ExpertOrder
    results['backend_sauce_fix'] = check_file_content(
        '/app/backend/pos_connectors/expertorder.py',
        [
            '# 7. SAUCE/DIP',
            'is_sauce',
            "any(keyword in group_id.lower() for keyword in ['sauce', 'dip'"
        ],
        'Backend Sauce-Fix'
    )
    
    # Check 3: Backend - POS Push History Fix
    results['backend_push_history'] = check_file_content(
        '/app/backend/pos_service.py',
        [
            '"pos_push_history": push_history_entry',
            '"payload": order_data',
            '$push'
        ],
        'Backend POS Push History Fix'
    )
    
    # Check 4: Backend - E-Mail Fix
    results['backend_email_fix'] = check_file_content(
        '/app/backend/email_service.py',
        [
            'response = resend.Emails.send(params)',
            'ZOZO Burger - Verifizierungscode',
            'ZOZO Burger - Bestellung'
        ],
        'Backend E-Mail Fix'
    )
    
    # Check 5: Frontend - Henstedt Redirect
    results['frontend_henstedt_redirect'] = check_file_content(
        '/app/frontend/src/pages/LocationsPage.jsx',
        [
            'Temporäre Weiterleitung für Henstedt-Ulzburg',
            'foodbooking.com/api/fb/0ybj4'
        ],
        'Frontend Henstedt Redirect'
    )
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n✅ Deployed: {passed}/{total} fixes")
    print(f"❌ Missing: {total - passed}/{total} fixes\n")
    
    if passed == total:
        print("🎉 ALL FIXES ARE DEPLOYED!")
        print("\nSystem is ready for testing.")
        print("\nNächste Schritte:")
        print("1. Testbestellung mit Menü aufgeben")
        print("2. Kassenbon prüfen (Beilage, Getränk, Sauce)")
        print("3. E-Mail-Posteingang prüfen")
    else:
        print("⚠️  NOT ALL FIXES ARE DEPLOYED!")
        print("\nDas deployed System hat NICHT die neuesten Fixes!")
        print("\n🚨 ACTION REQUIRED:")
        print("1. RE-DEPLOYMENT durchführen")
        print("2. Dieses Skript NACH dem Deployment erneut ausführen")
        print("3. Erst dann testen")
        
        print("\n❌ Missing fixes:")
        for fix_name, deployed in results.items():
            if not deployed:
                print(f"   - {fix_name}")
    
    print("\n" + "="*80 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

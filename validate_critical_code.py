#!/usr/bin/env python3
"""
🔒 CRITICAL CODE VALIDATOR
Prüft, ob die kritischen Fixes noch im Code vorhanden sind
Läuft automatisch nach jedem Deployment oder Code-Änderung
"""

import os
import sys
from typing import Dict, List, Tuple

class CriticalCodeValidator:
    """Validates that critical code sections are still intact"""
    
    # Kritische Code-Abschnitte, die NIEMALS entfernt werden dürfen
    CRITICAL_PATTERNS = {
        'CheckoutDialog.jsx': {
            'file': '/app/frontend/src/components/CheckoutDialog.jsx',
            'patterns': [
                ('LOCATION_VALIDATION', 'if (!locationToUse || !locationToUse.id)'),
                ('MODIFIERS_INCLUDED', 'modifiers: item.modifiers || {}'),
                ('CUSTOMIZATIONS_INCLUDED', 'customizations: item.customizations || []'),
                ('REMOVED_INGREDIENTS', 'removed_ingredients: item.removed_ingredients || []'),
                ('EXTRAS_INCLUDED', 'extras: item.extras || []'),
                ('CRITICAL_WARNING', 'CRITICAL FIX - DO NOT REMOVE - 22.01.2026')
            ],
            'description': 'Checkout-Dialog sendet ALLE Cart-Felder zum Backend'
        },
        
        'ProductCustomizer.jsx': {
            'file': '/app/frontend/src/components/ProductCustomizer.jsx',
            'patterns': [
                ('MENU_MODIFIERS_SEPARATE', 'const menuModifiers = {}'),
                ('BEILAGE_AS_MODIFIER', 'menuModifiers.beilage'),
                ('GETRAENK_AS_MODIFIER', 'menuModifiers.getraenk'),
                ('MODIFIERS_MERGE', '...selectedModifiers, ...menuModifiers'),
                ('NO_MODIFIERS_IN_CUSTOMIZATIONS', 'CHANGED 22.01.2026: Modifiers werden NICHT'),
                ('MODIFIER_PRICE_CALC', 'const modifierPrice = Object.values(selectedModifiers).reduce')
            ],
            'description': 'Menü-Komponenten als modifiers + Duplikat-Prävention'
        },
        
        'expertorder.py': {
            'file': '/app/backend/pos_connectors/expertorder.py',
            'patterns': [
                ('SAUCE_LOGIC', '# 7. SAUCE/DIP'),
                ('SAUCE_DETECTION', 'is_sauce = any(keyword in group_id.lower()'),
                ('NORMAL_SIZE_MENU', "size_upper == 'NORMAL'"),
                ('NORMAL_SIZE_100G', 'Normal 100g'),
                ('HINWEIS_AS_NOTE', "if 'note' not in menu_main_item"),
                ('DUPLICATE_PREVENTION', 'if any(mod_name in custom or custom in mod_name')
            ],
            'description': 'ExpertOrder: Sauce + Größen + Hinweise + Duplikat-Prävention'
        },
        
        'pos_service.py': {
            'file': '/app/backend/pos_service.py',
            'patterns': [
                ('PUSH_HISTORY_SUCCESS', '"pos_push_history": push_history_entry'),
                ('PUSH_HISTORY_PAYLOAD', '"payload": order_data'),
                ('PUSH_OPERATION', '$push')
            ],
            'description': 'POS Push History wird in Datenbank gespeichert'
        },
        
        'email_service.py': {
            'file': '/app/backend/email_service.py',
            'patterns': [
                ('VERIFICATION_EMAIL_REAL', 'response = resend.Emails.send(params)'),
                ('VERIFICATION_SUBJECT', 'ZOZO Burger - Verifizierungscode'),
                ('ORDER_CONFIRMATION_REAL', 'send_order_confirmation_email'),
                ('ORDER_CONFIRMATION_HTML', 'Bestellung bestätigt'),
            ],
            'description': 'E-Mails werden ECHT versendet (keine Stubs)'
        }
    }
    
    @classmethod
    def validate_file(cls, file_key: str) -> Tuple[bool, List[str]]:
        """Validate a single critical file"""
        config = cls.CRITICAL_PATTERNS[file_key]
        filepath = config['file']
        patterns = config['patterns']
        
        if not os.path.exists(filepath):
            return False, [f"FILE MISSING: {filepath}"]
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing = []
        for pattern_name, pattern in patterns:
            if pattern not in content:
                missing.append(f"MISSING: {pattern_name} ('{pattern[:50]}...')")
        
        if missing:
            return False, missing
        
        return True, []
    
    @classmethod
    def validate_all(cls) -> Dict:
        """Validate all critical files"""
        results = {}
        
        for file_key, config in cls.CRITICAL_PATTERNS.items():
            is_valid, errors = cls.validate_file(file_key)
            results[file_key] = {
                'valid': is_valid,
                'errors': errors,
                'description': config['description']
            }
        
        return results


def main():
    print("\n" + "="*80)
    print("🔒 CRITICAL CODE VALIDATION")
    print("="*80)
    print("\nPrüft, ob alle kritischen Fixes noch im Code vorhanden sind.\n")
    
    results = CriticalCodeValidator.validate_all()
    
    total = len(results)
    valid_count = sum(1 for r in results.values() if r['valid'])
    invalid_count = total - valid_count
    
    print(f"{'='*80}")
    print("VALIDATION RESULTS")
    print(f"{'='*80}\n")
    
    for file_key, result in results.items():
        status = "✅ VALID" if result['valid'] else "❌ INVALID"
        print(f"{status} - {file_key}")
        print(f"   {result['description']}")
        
        if not result['valid']:
            print(f"\n   🚨 FEHLER GEFUNDEN:")
            for error in result['errors']:
                print(f"      - {error}")
        
        print()
    
    print(f"{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"✅ Valid: {valid_count}/{total}")
    print(f"❌ Invalid: {invalid_count}/{total}\n")
    
    if valid_count == total:
        print("🎉 ALL CRITICAL CODE IS INTACT!")
        print("\nAlle wichtigen Fixes sind vorhanden.")
        print("Das System ist sicher und bereit für Production.\n")
        return True
    else:
        print("🚨 CRITICAL CODE MISSING OR MODIFIED!")
        print("\n⚠️  WARNUNG: Kritischer Code wurde entfernt oder geändert!")
        print("\nACTION REQUIRED:")
        print("1. Prüfen Sie, welche Patterns fehlen (siehe oben)")
        print("2. Stellen Sie den Code aus Backups wieder her:")
        print("   cp /app/backups/critical_fixes_2026_01_22/[FILE].WORKING /app/[path]/[FILE]")
        print("3. Oder: Implementieren Sie die Fixes erneut")
        print("4. Führen Sie dieses Script erneut aus zur Validierung\n")
        
        print("📁 Backups verfügbar in:")
        print("   /app/backups/critical_fixes_2026_01_22/\n")
        
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

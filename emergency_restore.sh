#!/bin/bash
# 🚨 NOTFALL-RESTORE
# Stellt alle kritischen Dateien aus Backups wieder her

echo ""
echo "="================================================================
echo "🚨 EMERGENCY RESTORE - Kritische Dateien wiederherstellen"
echo "=================================================================="
echo ""
echo "⚠️  WARNUNG: Dies überschreibt die aktuellen Dateien!"
echo ""
read -p "Fortfahren? (ja/nein): " confirm

if [ "$confirm" != "ja" ]; then
    echo "Abgebrochen."
    exit 1
fi

echo ""
echo "Starte Restore..."
echo ""

# Frontend Dateien
echo "📁 Restore Frontend..."
cp /app/backups/critical_fixes_2026_01_22/CheckoutDialog.jsx.WORKING \
   /app/frontend/src/components/CheckoutDialog.jsx && echo "✅ CheckoutDialog.jsx"

cp /app/backups/critical_fixes_2026_01_22/ProductCustomizer.jsx.WORKING \
   /app/frontend/src/components/ProductCustomizer.jsx && echo "✅ ProductCustomizer.jsx"

# Backend Dateien
echo ""
echo "📁 Restore Backend..."
cp /app/backups/critical_fixes_2026_01_22/expertorder.py.WORKING \
   /app/backend/pos_connectors/expertorder.py && echo "✅ expertorder.py"

cp /app/backups/critical_fixes_2026_01_22/pos_service.py.WORKING \
   /app/backend/pos_service.py && echo "✅ pos_service.py"

cp /app/backups/critical_fixes_2026_01_22/email_service.py.WORKING \
   /app/backend/email_service.py && echo "✅ email_service.py"

# Services neu starten
echo ""
echo "🔄 Starte Services neu..."
supervisorctl restart backend frontend

sleep 5

echo ""
echo "=================================================================="
echo "✅ RESTORE ABGESCHLOSSEN!"
echo "=================================================================="
echo ""
echo "Nächste Schritte:"
echo "1. Validation ausführen:"
echo "   python /app/validate_critical_code.py"
echo ""
echo "2. Logs prüfen:"
echo "   tail -n 50 /var/log/supervisor/backend.err.log"
echo "   tail -n 50 /var/log/supervisor/frontend.err.log"
echo ""
echo "3. Testbestellung durchführen"
echo ""

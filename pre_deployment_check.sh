#!/bin/bash
# 🔒 PRE-DEPLOYMENT VALIDATION HOOK
# Muss VOR jedem Deployment ausgeführt werden!

set -e  # Exit on any error

echo ""
echo "=================================================================="
echo "🔒 PRE-DEPLOYMENT VALIDATION"
echo "=================================================================="
echo ""

# 1. Code Validation
echo "1️⃣ Validiere kritischen Code..."
python /app/validate_critical_code.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ VALIDATION FAILED!"
    echo "🚨 DEPLOYMENT BLOCKIERT!"
    echo ""
    echo "Kritischer Code fehlt oder wurde geändert."
    echo "Bitte beheben Sie die Fehler vor dem Deployment."
    echo ""
    exit 1
fi

echo ""

# 2. Backup-Vergleich
echo "2️⃣ Vergleiche mit letztem funktionierenden Backup..."

LATEST_BACKUP=$(ls -td /app/backups/FINAL_LOCKED_VERSION_* 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "⚠️  Kein Backup gefunden - überspringe Vergleich"
else
    echo "   Backup: $LATEST_BACKUP"
    
    # Vergleiche kritische Dateien
    DIFF_FOUND=0
    
    if ! diff -q "$LATEST_BACKUP/CheckoutDialog.jsx" "/app/frontend/src/components/CheckoutDialog.jsx" > /dev/null 2>&1; then
        echo "   ⚠️  CheckoutDialog.jsx wurde geändert"
        DIFF_FOUND=1
    fi
    
    if ! diff -q "$LATEST_BACKUP/expertorder.py" "/app/backend/pos_connectors/expertorder.py" > /dev/null 2>&1; then
        echo "   ⚠️  expertorder.py wurde geändert"
        DIFF_FOUND=1
    fi
    
    if [ $DIFF_FOUND -eq 1 ]; then
        echo ""
        echo "⚠️  WARNUNG: Kritische Dateien wurden seit letztem Backup geändert!"
        echo ""
        read -p "Trotzdem fortfahren? (ja/nein): " confirm
        if [ "$confirm" != "ja" ]; then
            echo "Deployment abgebrochen."
            exit 1
        fi
    else
        echo "   ✅ Keine Änderungen an kritischen Dateien"
    fi
fi

echo ""

# 3. Services Status
echo "3️⃣ Prüfe Service-Status..."
supervisorctl status backend frontend | grep RUNNING > /dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ Backend und Frontend laufen"
else
    echo "   ❌ Services laufen nicht korrekt!"
    supervisorctl status
    exit 1
fi

echo ""

# 4. Test-Verbindung
echo "4️⃣ Teste Backend-Verbindung..."
curl -s http://localhost:8001/api/health > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✅ Backend antwortet"
else
    echo "   ⚠️  Backend Health-Check fehlgeschlagen"
fi

echo ""

# 5. Checksum-Validation (wenn vorhanden)
if [ -f "$LATEST_BACKUP/CHECKSUMS.txt" ]; then
    echo "5️⃣ Validiere Checksums..."
    
    cd "$LATEST_BACKUP"
    sha256sum -c CHECKSUMS.txt --quiet > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Alle Backups unverändert"
    else
        echo "   ⚠️  Backup-Checksums stimmen nicht überein"
    fi
    
    cd - > /dev/null
fi

echo ""
echo "=================================================================="
echo "✅ PRE-DEPLOYMENT VALIDATION ERFOLGREICH!"
echo "=================================================================="
echo ""
echo "Das System ist bereit für Deployment."
echo ""
echo "Nächste Schritte:"
echo "1. Deployment durchführen (Emergent Portal)"
echo "2. Nach Deployment: post_deployment_check.sh ausführen"
echo ""

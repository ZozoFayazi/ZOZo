#!/bin/bash
# Admin Authentication Verification Script
# Erstellt: 22. Januar 2026

echo "========================================"
echo "Admin Authentication Verification"
echo "========================================"
echo ""

# Check 1: Dokumentation existiert
if [ -f "/app/ADMIN_AUTHENTICATION_FIX_EINGEFROREN.md" ]; then
    echo "✅ Dokumentation vorhanden"
else
    echo "❌ FEHLER: Dokumentation fehlt!"
    exit 1
fi

# Check 2: Backups existieren
if [ -d "/app/backups/admin_auth_fix_22_01_2026" ]; then
    BACKUP_COUNT=$(ls /app/backups/admin_auth_fix_22_01_2026/*.WORKING 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -eq 5 ]; then
        echo "✅ Alle 5 Backups vorhanden"
    else
        echo "❌ FEHLER: Nur $BACKUP_COUNT von 5 Backups vorhanden!"
        exit 1
    fi
else
    echo "❌ FEHLER: Backup-Ordner fehlt!"
    exit 1
fi

# Check 3: Kritische Dateien verwenden sessionStorage
echo ""
echo "Überprüfe Token-Verwendung..."

FILES=(
    "/app/frontend/src/pages/CampaignManagement.jsx"
    "/app/frontend/src/pages/OrderManagement.jsx"
    "/app/frontend/src/pages/NewsletterManagement.jsx"
    "/app/frontend/src/pages/FeaturedProducts.jsx"
    "/app/frontend/src/pages/LocationSettingsV2.jsx"
)

for file in "${FILES[@]}"; do
    if grep -q "sessionStorage.getItem('adminToken')" "$file"; then
        echo "✅ $(basename $file) - verwendet sessionStorage korrekt"
    else
        echo "❌ FEHLER: $(basename $file) - verwendet NICHT sessionStorage!"
        exit 1
    fi
    
    # Check für falsche Token-Namen
    if grep -q "localStorage.getItem('zozoAuthToken')" "$file"; then
        echo "❌ FEHLER: $(basename $file) - verwendet noch zozoAuthToken!"
        exit 1
    fi
done

# Check 4: CampaignManagement hat activeTab State
if grep -q "const \[activeTab, setActiveTab\] = useState" "/app/frontend/src/pages/CampaignManagement.jsx"; then
    echo "✅ CampaignManagement.jsx - activeTab State definiert"
else
    echo "❌ FEHLER: CampaignManagement.jsx - activeTab State fehlt!"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ ALLE CHECKS BESTANDEN"
echo "Admin Authentication ist korrekt konfiguriert!"
echo "========================================"

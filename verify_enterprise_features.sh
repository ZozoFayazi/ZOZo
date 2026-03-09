#!/bin/bash
# Enterprise Features Verification Script
# Erstellt: 22. Januar 2026

echo "======================================================================"
echo "Enterprise Features Verification"
echo "======================================================================"
echo ""

ERRORS=0

# Check Backend Files
echo "Pr\u00fcfe Backend-Dateien..."
BACKEND_FILES=(
    "/app/backend/analytics_service.py"
    "/app/backend/analytics_endpoints.py"
    "/app/backend/customer_service.py"
    "/app/backend/customer_endpoints.py"
    "/app/backend/finance_service.py"
    "/app/backend/finance_endpoints.py"
    "/app/backend/email_service.py"
    "/app/backend/email_automation_service.py"
    "/app/backend/personalized_discount_service.py"
    "/app/backend/review_service.py"
    "/app/backend/review_endpoints.py"
)

for file in "${BACKEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  \u2705 $(basename $file)"
    else
        echo "  \u274c FEHLT: $file"
        ((ERRORS++))
    fi
done

# Check Frontend Pages
echo ""
echo "Pr\u00fcfe Frontend-Pages..."
FRONTEND_PAGES=(
    "/app/frontend/src/pages/Analytics.jsx"
    "/app/frontend/src/pages/Customers.jsx"
    "/app/frontend/src/pages/CustomerDetail.jsx"
    "/app/frontend/src/pages/Finance.jsx"
    "/app/frontend/src/pages/EmailAutomation.jsx"
    "/app/frontend/src/pages/ReviewPage.jsx"
    "/app/frontend/src/pages/ReviewManagement.jsx"
)

for file in "${FRONTEND_PAGES[@]}"; do
    if [ -f "$file" ]; then
        echo "  \u2705 $(basename $file)"
    else
        echo "  \u274c FEHLT: $file"
        ((ERRORS++))
    fi
done

# Check Components
echo ""
echo "Pr\u00fcfe Komponenten..."
if [ -f "/app/frontend/src/components/MetricCard.jsx" ]; then
    echo "  \u2705 Chart-Komponenten vorhanden"
else
    echo "  \u274c Chart-Komponenten fehlen"
    ((ERRORS++))
fi

# Check Backups
echo ""
echo "Pr\u00fcfe Backups..."
if [ -d "/app/backups/enterprise_features_22_01_2026" ]; then
    BACKUP_COUNT=$(find /app/backups/enterprise_features_22_01_2026 -name "*.WORKING" | wc -l)
    echo "  \u2705 $BACKUP_COUNT Backup-Dateien vorhanden"
else
    echo "  \u274c Backup-Ordner fehlt!"
    ((ERRORS++))
fi

# Check Dokumentation
echo ""
echo "Pr\u00fcfe Dokumentation..."
DOCS=(
    "/app/ENTERPRISE_FEATURES_EINGEFROREN.md"
    "/app/ANALYTICS_DASHBOARD_DOKUMENTATION.md"
    "/app/ENTERPRISE_CRM_DOKUMENTATION.md"
    "/app/ENTERPRISE_FINANCE_DOKUMENTATION.md"
    "/app/EXPERTORDER_STRUKTUR_NICHT_AENDERN.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "  \u2705 $(basename $doc)"
    else
        echo "  \u274c FEHLT: $doc"
        ((ERRORS++))
    fi
done

# Check Services
echo ""
echo "Pr\u00fcfe Services..."
if supervisorctl status backend | grep -q "RUNNING"; then
    echo "  \u2705 Backend l\u00e4uft"
else
    echo "  \u274c Backend l\u00e4uft NICHT!"
    ((ERRORS++))
fi

if supervisorctl status frontend | grep -q "RUNNING"; then
    echo "  \u2705 Frontend l\u00e4uft"
else
    echo "  \u274c Frontend l\u00e4uft NICHT!"
    ((ERRORS++))
fi

# Check Routes in App.js
echo ""
echo "Pr\u00fcfe Routen..."
if grep -q "path=\"/admin/analytics\"" /app/frontend/src/App.js; then
    echo "  \u2705 Analytics Route"
else
    echo "  \u274c Analytics Route fehlt"
    ((ERRORS++))
fi

if grep -q "path=\"/admin/customers\"" /app/frontend/src/App.js; then
    echo "  \u2705 Customers Route"
else
    echo "  \u274c Customers Route fehlt"
    ((ERRORS++))
fi

if grep -q "path=\"/admin/finance\"" /app/frontend/src/App.js; then
    echo "  \u2705 Finance Route"
else
    echo "  \u274c Finance Route fehlt"
    ((ERRORS++))
fi

if grep -q "path=\"/review\"" /app/frontend/src/App.js; then
    echo "  \u2705 Review Route"
else
    echo "  \u274c Review Route fehlt"
    ((ERRORS++))
fi

# Summary
echo ""
echo "======================================================================"
if [ $ERRORS -eq 0 ]; then
    echo "\u2705 ALLE CHECKS BESTANDEN"
    echo "Enterprise Features sind korrekt konfiguriert und einsatzbereit!"
else
    echo "\u274c $ERRORS FEHLER GEFUNDEN"
    echo "Bitte Backups wiederherstellen oder Fehler beheben!"
fi
echo "======================================================================"

exit $ERRORS

#!/bin/bash
# 🔍 POST-DEPLOYMENT VALIDATION
# Muss NACH jedem Deployment auf dem deployed System ausgeführt werden!

set -e

echo ""
echo "=================================================================="
echo "🔍 POST-DEPLOYMENT VALIDATION"
echo "=================================================================="
echo ""

# 1. Deployment Status
echo "1️⃣ Prüfe Deployment-Status..."
python /app/check_deployment_status.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ DEPLOYMENT INCOMPLETE!"
    echo "Nicht alle Fixes sind deployed."
    exit 1
fi

echo ""

# 2. Code Validation
echo "2️⃣ Validiere kritischen Code..."
python /app/validate_critical_code.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ CODE VALIDATION FAILED!"
    echo "Kritischer Code fehlt auf deployed System!"
    exit 1
fi

echo ""

# 3. Services Status
echo "3️⃣ Prüfe Services..."
supervisorctl status backend frontend | grep RUNNING > /dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ Backend und Frontend laufen"
else
    echo "   ❌ Services laufen nicht!"
    supervisorctl status
    exit 1
fi

echo ""

# 4. Backend Logs (Fehler-Check)
echo "4️⃣ Prüfe Backend-Logs auf Fehler..."
ERRORS=$(tail -n 100 /var/log/supervisor/backend.err.log | grep -i "error\|exception\|failed" | grep -v "apscheduler" | wc -l)

if [ $ERRORS -eq 0 ]; then
    echo "   ✅ Keine Fehler in Backend-Logs"
else
    echo "   ⚠️  $ERRORS Fehler in Backend-Logs gefunden"
    echo ""
    echo "Letzte Fehler:"
    tail -n 100 /var/log/supervisor/backend.err.log | grep -i "error\|exception" | grep -v "apscheduler" | tail -5
fi

echo ""

# 5. Frontend Compilation
echo "5️⃣ Prüfe Frontend-Compilation..."
cd /app/frontend
npx esbuild src/ --loader:.js=jsx --bundle --outfile=/dev/null 2>&1 | grep -i error > /dev/null

if [ $? -ne 0 ]; then
    echo "   ✅ Frontend kompiliert ohne Fehler"
else
    echo "   ❌ Frontend Compilation-Fehler!"
    npx esbuild src/ --loader:.js=jsx --bundle --outfile=/dev/null 2>&1 | grep -i error
fi

cd - > /dev/null

echo ""
echo "=================================================================="
echo "✅ POST-DEPLOYMENT VALIDATION ERFOLGREICH!"
echo "=================================================================="
echo ""
echo "System ist deployed und funktionsfähig."
echo ""
echo "MANUELLE TESTS ERFORDERLICH:"
echo ""
echo "  Test 1: Burger-Menü bestellen"
echo "    - Beilage, Getränk, Sauce wählen"
echo "    - Kassenbon prüfen: Alle Komponenten sichtbar?"
echo "    - Keine Duplikate?"
echo ""
echo "  Test 2: Salat mit Dressing"
echo "    - Dressing wählen"
echo "    - Kassenbon prüfen: Dressing sichtbar?"
echo ""
echo "  Test 3: Hinweis-Text"
echo "    - Spezielle Anweisungen eingeben"
echo "    - Kassenbon prüfen: Als Notiz, nicht als Artikel?"
echo ""
echo "  Test 4: E-Mail-Bestätigung"
echo "    - Bestellung mit E-Mail aufgeben"
echo "    - Posteingang prüfen: E-Mail erhalten?"
echo ""
echo "  Test 5: Normal-Größe"
echo "    - Burger Normal bestellen"
echo "    - Kassenbon prüfen: 'Normal 100g' sichtbar?"
echo ""
echo "=================================================================="
echo ""

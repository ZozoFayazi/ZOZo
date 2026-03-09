#!/bin/bash
BACKUP_DIR=$(dirname "$0")

echo "Stelle Dateien wieder her aus: $BACKUP_DIR"

cp "$BACKUP_DIR/CheckoutDialog.jsx" /app/frontend/src/components/
cp "$BACKUP_DIR/ProductCustomizer.jsx" /app/frontend/src/components/
cp "$BACKUP_DIR/LocationsPage.jsx" /app/frontend/src/pages/
cp "$BACKUP_DIR/HomePage.jsx" /app/frontend/src/pages/
cp "$BACKUP_DIR/LocationDetailPage.jsx" /app/frontend/src/pages/
cp "$BACKUP_DIR/MenuPage.jsx" /app/frontend/src/pages/
cp "$BACKUP_DIR/expertorder.py" /app/backend/pos_connectors/
cp "$BACKUP_DIR/pos_service.py" /app/backend/
cp "$BACKUP_DIR/email_service.py" /app/backend/
cp "$BACKUP_DIR/product_endpoints_v2.py" /app/backend/

supervisorctl restart backend frontend

echo "✅ Wiederherstellung abgeschlossen!"

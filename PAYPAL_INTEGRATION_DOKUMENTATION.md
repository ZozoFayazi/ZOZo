# PayPal Integration für ZOZO Burger

## ✅ KONFIGURATION ABGESCHLOSSEN

Die PayPal-Integration wurde erfolgreich für den **Henstedt-Ulzburg** Standort konfiguriert.

---

## 📋 Übersicht

### Standort-Konfiguration

**Location:** ZOZO Burger Henstedt-Ulzburg  
**Location ID:** `422cac42-cfdf-4869-b2cb-0b09aa24d02c`  
**Status:** ✅ AKTIV  
**Modus:** 🔴 LIVE (Produktiv)

### PayPal Credentials

- **Client ID:** `AWac3d_1EW-cqqAKNYOkOQM6_THWw3jLKGREqFS4heb5jn2TIFHcWcK6E6hNBRirXD3XP5cBhT8w6R8Q`
- **Secret Key:** `ECLyn3S30HV4QNiN8gOCFLv--0tp0Zi3FwOBxeRliIcTWzSi-EA0HP03B22_VYFEHC4CdRxRnUBTK1qh`
- **Modus:** LIVE (Production)

---

## 🔧 Technische Details

### Backend-Integration

**Neue Dateien:**
- `/app/backend/paypal_service.py` - PayPal Service Klasse
- `/app/setup_paypal_henstedt.py` - Setup-Skript für Credentials

**API Endpoints:**
- `POST /api/paypal/create-order` - Erstellt PayPal-Bestellung
- `POST /api/paypal/capture-order` - Führt Zahlung durch
- `GET /api/paypal/client-id/{location_id}` - Holt Client ID für Frontend
- `GET /admin/paypal-settings/{location_id}` - Admin: Zeigt PayPal-Einstellungen
- `PATCH /admin/paypal-settings/{location_id}` - Admin: Aktualisiert PayPal-Einstellungen

### Frontend-Integration

**Neue Dateien:**
- `/app/frontend/src/components/PayPalCheckout.jsx` - PayPal Button Komponente

**Modifizierte Dateien:**
- `/app/frontend/src/components/CheckoutDialog.jsx` - Integration des PayPal-Flows

### Datenbank

**Collection:** `location_settings`  
**Felder:**
```json
{
  "location_id": "422cac42-cfdf-4869-b2cb-0b09aa24d02c",
  "paypal_client_id": "AWac3d_1EW...",
  "paypal_client_secret": "ECLyn3S30...",
  "paypal_enabled": true,
  "paypal_sandbox_mode": false
}
```

---

## 🎯 Bestellablauf mit PayPal

### 1. Kunde wählt PayPal
- Kunde füllt Checkout-Formular aus
- Wählt "PayPal" als Zahlungsmethode
- Klickt auf "Jetzt bestellen"

### 2. Bestellung wird erstellt
- Backend erstellt ZOZO-Bestellung in der Datenbank
- Status: `payment_pending`
- Bestellnummer wird generiert

### 3. PayPal-Zahlung
- Frontend zeigt PayPal-Buttons
- Kunde wird zu PayPal weitergeleitet
- Kunde meldet sich bei PayPal an und bestätigt Zahlung

### 4. Zahlung wird verarbeitet
- Backend erfasst PayPal-Zahlung (`capture`)
- Bestellung wird aktualisiert:
  - `payment_status: "paid"`
  - `paypal_transaction_id: "..."`
  - `paid_at: timestamp`

### 5. Bestätigung
- Kunde sieht Erfolgsbildschirm
- Bestellung wird an POS (ExpertOrder) gesendet
- Kunde erhält Bestellnummer

---

## 💰 Zahlungsfluss

```
Kunde → ZOZO Frontend → ZOZO Backend → PayPal API
                                              ↓
                                    [Kunde zahlt]
                                              ↓
Bestätigung ← ZOZO Backend ← PayPal API (Capture)
```

### Geldfluss

Alle Zahlungen für Bestellungen am **Henstedt-Ulzburg** Standort fließen direkt auf das PayPal-Konto, das mit den oben genannten Credentials verknüpft ist.

---

## 🧪 Testing

### Automatischer Test
```bash
cd /app
python test_paypal_integration.py
```

### Manueller Test
1. Öffne: https://tastycart-3.preview.emergentagent.com
2. Wähle Standort: **Henstedt-Ulzburg**
3. Füge Produkte zum Warenkorb hinzu
4. Gehe zu Checkout
5. Wähle **PayPal** als Zahlungsmethode
6. Fülle Lieferadresse aus (Henstedt-Ulzburg PLZ: 24558)
7. Klicke "Jetzt bestellen"
8. Schließe PayPal-Zahlung ab

---

## 🔒 Sicherheit

- ✅ Client Secret wird niemals an Frontend gesendet
- ✅ PayPal-API-Kommunikation nur über Backend
- ✅ Credentials in Datenbank gespeichert
- ✅ HTTPS für alle PayPal-Transaktionen
- ✅ Transaktions-IDs werden für Audit-Trail gespeichert

---

## 📊 Admin-Panel

### PayPal-Einstellungen verwalten

Admins können PayPal-Einstellungen über das Admin-Panel verwalten:

**Endpoint:** `/admin/paypal-settings/{location_id}`

**Zugriff:** Nur `owner` Role kann Einstellungen ändern

---

## 🛠️ Fehlerbehebung

### PayPal-Button wird nicht angezeigt
- Prüfe, ob Location korrekt ausgewählt ist
- Prüfe Browser-Konsole auf JavaScript-Fehler
- Verifiziere, dass `paypal_enabled: true` in DB

### Zahlung schlägt fehl
- Prüfe PayPal-Dashboard für Transaktionsdetails
- Verifiziere Client ID und Secret
- Prüfe Backend-Logs: `tail -f /var/log/supervisor/backend.err.log`

### "PayPal not configured" Fehler
```bash
# Credentials erneut einrichten:
cd /app
python setup_paypal_henstedt.py
```

---

## 📝 Rellingen-Standort konfigurieren

Um PayPal auch für **Rellingen** zu aktivieren:

1. PayPal-Credentials für Rellingen besorgen (Client ID + Secret)
2. Setup-Skript anpassen oder Admin-API nutzen:

```bash
curl -X PATCH http://localhost:8001/api/admin/paypal-settings/{rellingen_location_id} \
  -H "Authorization: Bearer {owner_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "paypal_client_id": "RELLINGEN_CLIENT_ID",
    "paypal_client_secret": "RELLINGEN_SECRET",
    "paypal_enabled": true,
    "paypal_sandbox_mode": false
  }'
```

---

## ✅ Status

| Feature | Status |
|---------|--------|
| Backend PayPal Service | ✅ Implementiert |
| API Endpoints | ✅ Implementiert |
| Frontend PayPal Buttons | ✅ Implementiert |
| Checkout-Integration | ✅ Implementiert |
| Henstedt-Ulzburg Config | ✅ Konfiguriert |
| Database Schema | ✅ Aktualisiert |
| Testing | ✅ Validiert |
| Dokumentation | ✅ Erstellt |

---

## 📞 Support

Bei Fragen zur PayPal-Integration:
1. Prüfe diese Dokumentation
2. Teste mit dem automatischen Test-Skript
3. Prüfe Backend-Logs für Fehlerdetails

**Wichtig:** Die PayPal-Credentials sind LIVE-Credentials. Alle Transaktionen sind real und werden in Echtzeit verarbeitet.

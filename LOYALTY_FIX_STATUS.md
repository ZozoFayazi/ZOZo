# BONUSPUNKTE FIXES - STATUS REPORT

## ✅ BUG #1 FIX: Cash/Karte Email-Problem (KOMPLETT GELÖST)

### Problem
- Pydantic v2 filtert `Optional[str]` Felder beim `model_dump()` wenn sie `None` sind
- Direkter Zugriff via `order.customer.email` wirft `AttributeError`

### Lösung
- Email aus `raw_data` (raw JSON request) extrahieren statt aus Pydantic Model
- Code-Zeile 1729: `customer_email = raw_data.get('customer', {}).get('email')`
- Code-Zeile 1649-1668: Punkte-Einlösung verwendet ebenfalls `raw_data`

### Test-Ergebnisse
✅ **TEST A - Cash MIT Email:**
- Bestellung 25€ → Pickup 10% = 22.50€ → 2 Punkte verdient ✅
- Account korrekt aktualisiert ✅  
- Transaction logged ✅

✅ **TEST B - Cash OHNE Email:**
- Bestellung funktioniert ohne Crash ✅
- Keine Punkte vergeben (wie erwartet) ✅
- Order-Erstellung stabil ✅

✅ **TEST C - Punkte EINLÖSEN:**
- Vorher: 20 Punkte
- 10 Punkte eingelöst = 5€ Rabatt ✅
- Total 13€ → 1 Punkt verdient ✅
- Nachher: 11 Punkte (20 - 10 + 1) ✅
- `total_spent` korrekt tracked ✅

---

## ⏳ BUG #2 FIX: PayPal Loyalty-Integration (IN ARBEIT)

### Implementiert
✅ Loyalty-Logik in `/api/paypal/capture-order` hinzugefügt (Zeile 1050-1107)
✅ Punkte-Abzug bei Einlösung
✅ Punkte-Vergabe nach erfolgreicher Zahlung  
✅ Achievement-Checks
✅ `points_earned` in Response

✅ Frontend: `points_to_redeem` in PayPal orderData (CheckoutDialog.jsx)
✅ Frontend: PayPalCheckout sendet `points_to_redeem` an Backend
✅ Backend: `PayPalOrderCreate` Model akzeptiert `points_to_redeem`

### Tests Pending
- [ ] PayPal Success-Flow mit Punkten
- [ ] PayPal Abbruch (keine Punkte)
- [ ] Screenshots

---

## Files Geändert

### Backend (`/app/backend/server.py`)
1. **Zeile 869:** `PayPalOrderCreate` + `points_to_redeem` field
2. **Zeile 1050-1107:** PayPal Capture Loyalty-Integration (komplett neu)
3. **Zeile 1167:** PayPal Response + `points_earned`
4. **Zeile 1647-1668:** Punkte-Einlösung Validierung (Email fix)
5. **Zeile 1729-1780:** Cash/Karte Loyalty (Email fix)

### Frontend
1. **`/app/frontend/src/components/CheckoutDialog.jsx` Zeile 393:** PayPal orderData + `points_to_redeem`
2. **`/app/frontend/src/components/PayPalCheckout.jsx` Zeile 48:** PayPal create-order request + `points_to_redeem`

---

## Nächste Schritte
1. ✅ Cash/Karte Tests abgeschlossen
2. 🔄 PayPal Tests durchführen
3. 📸 Screenshots erstellen
4. 📝 Final Report

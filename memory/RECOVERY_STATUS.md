# ZoZo Burger - Recovery Status

## Aktueller Status: WARTEND AUF EMERGENT SUPPORT

**Datum:** 09. März 2026
**Problem:** Quellcode (Backend + Frontend) fehlt nach Fork/Rollback
**Ticket:** Bei Emergent Support eingereicht, eskaliert an Senior Technical Team

---

## Was funktioniert:

### Datenbank (MongoDB Atlas) - VOLLSTÄNDIG INTAKT
- **URL:** mongodb+srv://zozoadmin:****@cluster0.adpiixq.mongodb.net/
- **DB Name:** zozo_burger

| Collection | Dokumente |
|------------|-----------|
| menu_items | 111 |
| orders | 266 |
| categories | 18 |
| modifier_groups | 15 |
| locations | 2 |
| admins | 5 |
| discount_codes | 5 |
| daily_deals | 4 |
| loyalty_accounts | 31 |
| newsletter_subscribers | 15 |

### Standorte
1. ZOZO Burger Rellingen (slug: rellingen)
2. ZOZO Burger Henstedt-Ulzburg (slug: henstedt-ulzburg)

### Kategorien
- Vorspeisen & Salate
- Burger
- Smash Burger
- Pizza
- Pasta
- Wraps
- Pizzabrötchen
- Fingerfood
- Imbiss
- Kiddy Zone
- (und mehr...)

### PayPal Integration
- Client IDs vorhanden für beide Standorte
- Secrets vorhanden

---

## Was fehlt:

### Backend Code
- server.py
- Alle Python Module (auth, models, endpoints, services)
- Nur __pycache__ und .env vorhanden

### Frontend Code
- package.json
- src/ Ordner
- public/ Ordner
- Nur node_modules und .env vorhanden

---

## Nächste Schritte nach Code-Wiederherstellung:

1. **Code auf GitHub sichern** ("Save to Github")
2. **Stabiles Deployment einrichten:**
   - Railway oder Render empfohlen
   - Einmalige DNS-Konfiguration
   - Keine Änderungen bei Preview-Wechsel mehr nötig
3. **DNS in Cloudflare anpassen:**
   - A Records für zozo-burger.de löschen
   - CNAME auf stabile Hosting-URL setzen

---

## Vorhandene API Keys (.env):

```
RESEND_API_KEY=re_KS2rud3s_GSvEJZHwnpLdJm9TU5WuK18g
SENDER_EMAIL=noreply@zozo-burger.de
POS_ALERT_EMAIL=info@zozo-burger.de
JWT_SECRET=vorhanden
ADMIN_JWT_SECRET=vorhanden
```

---

## Kontakte:

- **Emergent Support:** support@emergent.sh
- **Live Domain:** zozo-burger.de (aktuell DOWN)

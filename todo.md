# Phase 1: Dialog-Vereinfachung - Aufgabenliste

## Status: In Progress

### Aufgaben:

- [ ] **Task 1**: ProductCustomizer.jsx erweitern
  - Menu-Upgrade State-Variablen hinzufügen (upgradeToMenu, selectedSide, selectedDrink)
  - Menu-Upgrade-Option UI implementieren (Toggle zwischen "Als Burger" und "Als Menü")
  - Beilagen-Auswahl (Pommes, Sweet Potato, Twister, Country) mit Selektor
  - Getränke-Auswahl (Coca Cola, Fanta, Sprite, etc.) mit Selektor
  - Preis-Berechnung anpassen für Menu-Upgrade
  - Validierung: Beilage + Getränk müssen ausgewählt sein, wenn Menü aktiviert
  - Warenkorb-Logic erweitern für Menu-Items
  - data-testid für alle neuen interaktiven Elemente
  
- [ ] **Task 2**: MenuPage.jsx anpassen
  - MenuUpgradeDialog Import entfernen
  - menuUpgradeOpen & upgradingItem State entfernen
  - MenuUpgradeDialog Komponente aus JSX entfernen
  - handleAddToCart Logic vereinfachen (kein separater Menu-Upgrade-Dialog mehr)
  - ProductCustomizer direkt für alle customizable Items öffnen
  - Sicherstellen dass CategoryUpsellDialog weiterhin funktioniert
  
- [ ] **Task 3**: MenuUpgradeDialog.jsx löschen
  - Datei entfernen (nicht mehr benötigt)
  
- [ ] **Task 4**: Frontend Build testen
  - `esbuild src/ --loader:.js=jsx --bundle --outfile=/dev/null` ausführen
  - Alle Fehler beheben
  
- [ ] **Task 5**: Screenshots & Funktionstest
  - Screenshot des neuen kombinierten Dialogs
  - Burger mit und ohne Menu-Upgrade testen
  - Sicherstellen dass Preise korrekt berechnet werden
  - CategoryUpsellDialog danach testen
  
- [ ] **Task 6**: Service-Logs überprüfen
  - Frontend & Backend Logs auf Fehler prüfen
  - Sicherstellen dass keine Console-Errors vorhanden sind

---

**Abnahmekriterien:**
- ✅ Nur noch 2 Dialoge im Bestellablauf (nicht 3)
- ✅ Alle Funktionen aus beiden alten Dialogen sind im neuen Dialog enthalten
- ✅ Keine Console-Errors
- ✅ Preise werden korrekt berechnet
- ✅ Design-Guidelines befolgt (Farben, Fonts, Spacing)
- ✅ Alle data-testid vorhanden

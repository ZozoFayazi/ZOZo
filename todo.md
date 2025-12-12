# Phase 1: Dialog-Vereinfachung - Aufgabenliste

## Status: In Progress

### Aufgaben:

- [x] **Task 1**: ProductCustomizer.jsx erweitern ✅
  - Menu-Upgrade State-Variablen hinzugefügt (upgradeToMenu, selectedSide, selectedDrink)
  - Menu-Upgrade-Option UI implementiert (Toggle zwischen "Als Burger" und "Als Menü")
  - Beilagen-Auswahl (Pommes, Sweet Potato, Twister, Country) mit Selektor
  - Getränke-Auswahl (Coca Cola, Fanta, Sprite, etc.) mit Selektor
  - Preis-Berechnung angepasst für Menu-Upgrade
  - Validierung: Beilage + Getränk müssen ausgewählt sein, wenn Menü aktiviert
  - Warenkorb-Logic erweitert für Menu-Items
  - data-testid für alle neuen interaktiven Elemente
  
- [x] **Task 2**: MenuPage.jsx angepasst ✅
  - MenuUpgradeDialog Import entfernt
  - menuUpgradeOpen & upgradingItem State entfernt
  - MenuUpgradeDialog Komponente aus JSX entfernt
  - handleAddToCart Logic vereinfacht (kein separater Menu-Upgrade-Dialog mehr)
  - ProductCustomizer direkt für alle customizable Items öffnen
  - CategoryUpsellDialog funktioniert weiterhin
  
- [x] **Task 3**: MenuUpgradeDialog.jsx gelöscht ✅
  - Datei entfernt (nicht mehr benötigt)
  
- [x] **Task 4**: Frontend Build getestet ✅
  - `esbuild src/ --loader:.js=jsx --bundle --outfile=/dev/null` ausgeführt
  - Keine Fehler
  
- [x] **Task 5**: Screenshots & Funktionstest ✅
  - Screenshot des neuen kombinierten Dialogs
  - Burger mit und ohne Menu-Upgrade getestet
  - Preise werden korrekt berechnet (€7.99 → €13.89)
  - CategoryUpsellDialog danach funktioniert
  
- [x] **Task 6**: Service-Logs überprüft ✅
  - Frontend & Backend Logs auf Fehler geprüft
  - Keine Console-Errors vorhanden

---

**Abnahmekriterien:**
- ✅ Nur noch 2 Dialoge im Bestellablauf (nicht 3)
- ✅ Alle Funktionen aus beiden alten Dialogen sind im neuen Dialog enthalten
- ✅ Keine Console-Errors
- ✅ Preise werden korrekt berechnet
- ✅ Design-Guidelines befolgt (Farben, Fonts, Spacing)
- ✅ Alle data-testid vorhanden

**PHASE 1 ABGESCHLOSSEN! ✅**

#!/usr/bin/env python3
"""
Complete Delivery Zone Validation
Tests all postal codes for both locations
"""
import requests

API_URL = "https://menu-config.preview.emergentagent.com/api"

# Postal codes per location (from DB)
rellingen_plz = [
    "25462", "25469", "22547", "22549", "22607", "22869",
    "22589", "22609", "22525", "22523", "25474", "25421"
]

henstedt_plz = [
    "25451", "22889", "22844", "22846", "22848", "22850",
    "22851", "25474", "25486", "24629", "24558", "24568", "24576"
]

def check_plz(postal_code):
    """Check delivery availability for a postal code"""
    try:
        resp = requests.get(f"{API_URL}/check-delivery-zone?postal_code={postal_code}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data
        return {"available": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"available": False, "error": str(e)}

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

print_section("LIEFERGEBIETS-VALIDIERUNG - KOMPLETT")

# Test Rellingen
print_section("RELLINGEN - PLZ-Check")

rellingen_ok = 0
rellingen_fail = 0

for plz in rellingen_plz:
    result = check_plz(plz)
    
    if result.get('available'):
        location_name = result.get('location', {}).get('name', 'Unknown')
        mbw = result.get('min_order_value', 0)
        delivery_fee = result.get('delivery_fee', 0)
        
        if 'rellingen' in location_name.lower():
            print(f"✅ {plz}: Lieferbar (MBW: €{mbw:.2f}, Gebühr: €{delivery_fee:.2f})")
            rellingen_ok += 1
        else:
            print(f"⚠️  {plz}: Lieferbar aber FALSCHE FILIALE ({location_name})")
            rellingen_fail += 1
    else:
        print(f"❌ {plz}: NICHT lieferbar - {result.get('message', 'Unknown')}")
        rellingen_fail += 1

# Test Henstedt-Ulzburg
print_section("HENSTEDT-ULZBURG - PLZ-Check")

henstedt_ok = 0
henstedt_fail = 0

for plz in henstedt_plz:
    result = check_plz(plz)
    
    if result.get('available'):
        location_name = result.get('location', {}).get('name', 'Unknown')
        mbw = result.get('min_order_value', 0)
        delivery_fee = result.get('delivery_fee', 0)
        
        if 'henstedt' in location_name.lower():
            print(f"✅ {plz}: Lieferbar (MBW: €{mbw:.2f}, Gebühr: €{delivery_fee:.2f})")
            henstedt_ok += 1
        else:
            print(f"⚠️  {plz}: Lieferbar aber FALSCHE FILIALE ({location_name})")
            henstedt_fail += 1
    else:
        print(f"❌ {plz}: NICHT lieferbar - {result.get('message', 'Unknown')}")
        henstedt_fail += 1

# Summary
print_section("ZUSAMMENFASSUNG")

print(f"🏪 RELLINGEN:")
print(f"   ✅ OK: {rellingen_ok}/{len(rellingen_plz)}")
if rellingen_fail > 0:
    print(f"   ❌ Fehler: {rellingen_fail}")

print(f"\n🏪 HENSTEDT-ULZBURG:")
print(f"   ✅ OK: {henstedt_ok}/{len(henstedt_plz)}")
if henstedt_fail > 0:
    print(f"   ❌ Fehler: {henstedt_fail}")

total_ok = rellingen_ok + henstedt_ok
total_tested = len(rellingen_plz) + len(henstedt_plz)

print(f"\n📊 GESAMT: {total_ok}/{total_tested} PLZ korrekt")

if total_ok == total_tested:
    print(f"\n✅ ALLE LIEFERGEBIETE KORREKT KONFIGURIERT!")
else:
    print(f"\n⚠️  {total_tested - total_ok} PLZ haben Probleme!")


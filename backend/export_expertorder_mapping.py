"""
ExpertOrder Article Mapping Export Tool
Generates a mapping list for ExpertOrder POS configuration
"""
import asyncio
import os
import csv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def export_articles_for_expertorder():
    """Export all articles that need to be mapped in ExpertOrder"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Get all categories
    categories = await db.categories.find({"active": True}).to_list(100)
    category_map = {str(cat.get('_id')): cat.get('name') for cat in categories}
    
    # Get all products
    products = await db.menu_items.find({"active": True}).to_list(1000)
    
    # Get all modifier groups
    modifier_groups = await db.modifier_groups.find({}).to_list(100)
    
    print('=' * 100)
    print('🏷️  EXPERTORDER ARTIKEL-MAPPING LISTE')
    print('=' * 100)
    print()
    print('HINWEIS: Diese Artikel müssen einmalig im ExpertOrder Kassensystem zugeordnet werden.')
    print('          Gehe in ExpertOrder zu: Einstellungen → Artikel-Zuordnung → Online-Bestellungen')
    print()
    print('=' * 100)
    
    # Create CSV file
    csv_filename = f'/tmp/expertorder_artikel_mapping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';')
        
        # Header
        csv_writer.writerow([
            'Typ',
            'Kategorie',
            'Artikelname (ZOZO)',
            'Größe',
            'Preis',
            'UID (wird gesendet)',
            'ExpertOrder Artikel-ID (leer lassen - im Kassensystem mappen!)'
        ])
        
        print('\n📦 HAUPTPRODUKTE:')
        print('-' * 100)
        print(f"{'Kategorie':<20} {'Artikelname':<40} {'Größe':<10} {'Preis':<10} {'UID':<30}")
        print('-' * 100)
        
        for product in sorted(products, key=lambda x: (category_map.get(x.get('category_id'), ''), x.get('name', ''))):
            cat_name = category_map.get(product.get('category_id'), 'Unbekannt')
            name = product.get('name', 'N/A')
            
            # Handle products with sizes
            if product.get('price_medium') or product.get('price_large'):
                # Medium
                if product.get('price_medium'):
                    uid = f"{name.upper().replace(' ', '_')}_MEDIUM"
                    print(f"{cat_name:<20} {name:<40} {'Medium':<10} €{product.get('price_medium'):<9.2f} {uid:<30}")
                    csv_writer.writerow(['Produkt', cat_name, name, 'Medium', product.get('price_medium'), uid, ''])
                
                # Large
                if product.get('price_large'):
                    uid = f"{name.upper().replace(' ', '_')}_LARGE"
                    print(f"{cat_name:<20} {name:<40} {'Large':<10} €{product.get('price_large'):<9.2f} {uid:<30}")
                    csv_writer.writerow(['Produkt', cat_name, name, 'Large', product.get('price_large'), uid, ''])
            else:
                # Normal size
                uid = f"{name.upper().replace(' ', '_')}"
                price = product.get('price_normal', 0)
                print(f"{cat_name:<20} {name:<40} {'Normal':<10} €{price:<9.2f} {uid:<30}")
                csv_writer.writerow(['Produkt', cat_name, name, 'Normal', price, uid, ''])
        
        print()
        print('=' * 100)
        print()
        print('🔧 MENÜ-KOMPONENTEN (Beilage, Getränk, etc.):')
        print('-' * 100)
        print(f"{'Gruppe':<30} {'Option':<40} {'Preis':<10} {'UID (bereits konfiguriert)':<40}")
        print('-' * 100)
        
        for group in modifier_groups:
            group_name = group.get('name', 'Unbekannt')
            group_id = group.get('id', 'N/A')
            
            for option in group.get('options', []):
                opt_name = option.get('name', 'N/A')
                opt_price = option.get('price', 0)
                opt_uid = option.get('pos_item_id', 'NICHT GESETZT')
                
                print(f"{group_name:<30} {opt_name:<40} €{opt_price:<9.2f} {opt_uid:<40}")
                csv_writer.writerow(['Modifier', group_name, opt_name, '-', opt_price, opt_uid, ''])
    
    print()
    print('=' * 100)
    print(f'✅ CSV-Export erstellt: {csv_filename}')
    print('=' * 100)
    print()
    print('📋 NÄCHSTE SCHRITTE:')
    print()
    print('1. Öffne ExpertOrder Kassensystem')
    print('2. Gehe zu: Einstellungen → Online-Shop → Artikel-Zuordnung')
    print('3. Für jeden Artikel in der Liste:')
    print('   - ZOZO sendet UID: "HAMBURGER_MEDIUM"')
    print('   - Ordne zu: Dein Kassensystem-Artikel "Hamburger 125g"')
    print('4. Speichere die Zuordnungen')
    print('5. Test-Bestellung aufgeben')
    print()
    print('💡 TIPP: Die Modifier (Beilage, Getränk) haben bereits UIDs und sollten')
    print('         automatisch funktionieren, falls bereits im Kassensystem vorhanden!')
    print()
    
    client.close()
    
    return csv_filename

if __name__ == "__main__":
    csv_file = asyncio.run(export_articles_for_expertorder())
    print(f'\n📁 Datei bereit zum Download: {csv_file}')

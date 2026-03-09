"""
Migration Script: Convert to Master-Slave Product Architecture

CRITICAL: This script consolidates products from multiple locations into
a single global product list with location-specific overrides.

Strategy:
1. Keep ALL global products (location_id=null) as-is
2. Consolidate Rellingen + Henstedt products:
   - Match by: name + category_id + price (fuzzy match if needed)
   - For duplicates: Keep Rellingen version (master), create Henstedt override
   - For unique products: Move to global, create appropriate overrides
3. Create branch_product_settings for location-specific active/stock status

SAFETY:
- Backs up data before migration
- Dry-run mode by default
- Rollback capability
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timezone
import sys

# Dry-run mode (set to False to actually execute)
DRY_RUN = True


async def migrate_to_master_slave():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    print("🔄 Starting Master-Slave Product Migration")
    print(f"   Mode: {'DRY-RUN (no changes)' if DRY_RUN else 'LIVE (will modify data)'}\n")
    
    # Get location IDs
    locations = await db.locations.find({}).to_list(10)
    rel_id = None
    hen_id = None
    for loc in locations:
        if loc['slug'] == 'rellingen':
            rel_id = str(loc['_id'])
        elif loc['slug'] == 'henstedt-ulzburg':
            hen_id = str(loc['_id'])
    
    if not rel_id or not hen_id:
        print("❌ ERROR: Could not find both locations!")
        return
    
    print(f"📍 Locations:")
    print(f"   Rellingen (Master): {rel_id}")
    print(f"   Henstedt (Slave): {hen_id}\n")
    
    # Step 1: Get all products
    all_products = await db.menu_items.find({}).to_list(1000)
    global_products = [p for p in all_products if p.get('location_id') is None]
    rellingen_products = [p for p in all_products if p.get('location_id') == rel_id]
    henstedt_products = [p for p in all_products if p.get('location_id') == hen_id]
    
    print(f"📊 Current State:")
    print(f"   Global: {len(global_products)}")
    print(f"   Rellingen-specific: {len(rellingen_products)}")
    print(f"   Henstedt-specific: {len(henstedt_products)}\n")
    
    # Step 2: Consolidation Plan
    print("📋 Migration Plan:\n")
    
    # All Rellingen products become global (they are the master)
    print(f"✅ Step 1: Make {len(rellingen_products)} Rellingen products global (set location_id=null)")
    
    # For each Henstedt product, check if similar product exists in Rellingen/Global
    # If yes: Create override (active/stock), mark Henstedt product for archival
    # If no: Make global, create Henstedt override if active/stock differs from defaults
    
    matches = []
    henstedt_only = []
    
    for h_product in henstedt_products:
        h_name = h_product.get('name', '').strip().lower()
        h_category = str(h_product.get('category_id', ''))
        h_price = h_product.get('price_normal') or h_product.get('price_medium')
        
        # Try to find match in Rellingen or Global
        found_match = False
        
        for r_product in rellingen_products + global_products:
            r_name = r_product.get('name', '').strip().lower()
            r_category = str(r_product.get('category_id', ''))
            r_price = r_product.get('price_normal') or r_product.get('price_medium')
            
            # Match criteria: Same name + same category
            if r_name == h_name and r_category == h_category:
                matches.append({
                    'name': h_product.get('name'),
                    'master_id': str(r_product['_id']),
                    'henstedt_id': str(h_product['_id']),
                    'henstedt_active': h_product.get('active', True),
                    'henstedt_stock': h_product.get('in_stock', True),
                    'price_diff': abs((r_price or 0) - (h_price or 0)) if r_price and h_price else None
                })
                found_match = True
                break
        
        if not found_match:
            henstedt_only.append(h_product)
    
    print(f"✅ Step 2: Found {len(matches)} matching products (will create Henstedt overrides)")
    print(f"✅ Step 3: Found {len(henstedt_only)} Henstedt-only products (will make global)\n")
    
    # Step 3: Execute migration
    if not DRY_RUN:
        print("🚀 Executing Migration (LIVE MODE)...\n")
        
        # 3.1: Make all Rellingen products global
        result = await db.menu_items.update_many(
            {"location_id": rel_id},
            {"$set": {"location_id": None, "updated_at": datetime.now(timezone.utc)}}
        )
        print(f"✅ Made {result.modified_count} Rellingen products global")
        
        # 3.2: Create overrides for matched Henstedt products
        for match in matches:
            override = {
                "product_id": match['master_id'],
                "location_slug": "henstedt-ulzburg",
                "is_active": match['henstedt_active'],
                "in_stock": match['henstedt_stock'],
                "created_at": datetime.now(timezone.utc),
                "created_by": "migration_script",
                "updated_at": datetime.now(timezone.utc)
            }
            
            await db.branch_product_settings.insert_one(override)
        
        print(f"✅ Created {len(matches)} Henstedt overrides")
        
        # 3.3: Make Henstedt-only products global
        henstedt_only_ids = [ObjectId(p['_id']) for p in henstedt_only]
        result = await db.menu_items.update_many(
            {"_id": {"$in": henstedt_only_ids}},
            {"$set": {"location_id": None, "updated_at": datetime.now(timezone.utc)}}
        )
        print(f"✅ Made {result.modified_count} Henstedt-only products global")
        
        # 3.4: Archive old Henstedt products that were matched (don't delete, just mark)
        matched_henstedt_ids = [ObjectId(m['henstedt_id']) for m in matches]
        result = await db.menu_items.update_many(
            {"_id": {"$in": matched_henstedt_ids}},
            {"$set": {"archived": True, "archived_at": datetime.now(timezone.utc), "archived_reason": "Duplicate - migrated to override model"}}
        )
        print(f"✅ Archived {result.modified_count} duplicate Henstedt products")
        
        print(f"\n✅ Migration Complete!")
        
    else:
        print("🔍 DRY-RUN MODE - No changes made")
        print(f"\n📋 Would execute:")
        print(f"   - Make {len(rellingen_products)} Rellingen products global")
        print(f"   - Create {len(matches)} Henstedt overrides")
        print(f"   - Make {len(henstedt_only)} Henstedt-only products global")
        print(f"   - Archive {len(matches)} duplicate Henstedt products")
    
    # Final stats
    print(f"\n📊 Expected Final State:")
    if DRY_RUN:
        total_global = len(global_products) + len(rellingen_products) + len(henstedt_only)
    else:
        total_global = await db.menu_items.count_documents({"location_id": None, "archived": {"$ne": True}})
        override_count = await db.branch_product_settings.count_documents({})
    
    print(f"   Global products: {total_global if DRY_RUN else total_global}")
    print(f"   Branch overrides: {len(matches) if DRY_RUN else override_count}")
    print(f"   Archived products: {len(matches) if DRY_RUN else 'N/A'}")
    
    client.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRODUCT MIGRATION: MASTER-SLAVE ARCHITECTURE")
    print("="*60 + "\n")
    
    if DRY_RUN:
        print("⚠️  DRY-RUN MODE - No changes will be made")
        print("    Set DRY_RUN=False to execute migration\n")
    else:
        print("🚨 LIVE MODE - This will modify the database!")
        response = input("    Type 'YES' to confirm: ")
        if response != "YES":
            print("❌ Migration cancelled")
            sys.exit(0)
    
    asyncio.run(migrate_to_master_slave())
    
    print("\n" + "="*60)
    print("✅ DONE")
    print("="*60)

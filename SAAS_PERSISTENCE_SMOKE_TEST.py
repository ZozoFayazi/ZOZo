#!/usr/bin/env python3
"""
SaaS Persistence Smoke Test
Verifies all tenant data is persistent and correct
"""
import os
import sys
from pymongo import MongoClient
from datetime import datetime

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

report = []
report.append("="*80)
report.append("🧪 SAAS PERSISTENCE SMOKE TEST")
report.append("="*80)
report.append(f"Timestamp: {datetime.now().isoformat()}")
report.append("")

all_passed = True

# 1. Check tenants exist
report.append("1️⃣ TENANTS CHECK:")
report.append("-"*80)
tenant_count = db.tenants.count_documents({})
if tenant_count > 0:
    report.append(f"✅ Tenants: {tenant_count} found")
    tenants = list(db.tenants.find({}))
    
    for tenant in tenants:
        tenant_id = tenant.get('tenant_id')
        tenant_name = tenant.get('name')
        report.append(f"\n📦 Tenant: {tenant_name} ({tenant_id})")
        
        # Check branding
        branding = tenant.get('branding', {})
        if branding and branding.get('primary_color'):
            report.append(f"   ✅ Branding: Colors set ({branding['primary_color']})")
        else:
            report.append(f"   ❌ Branding: Missing")
            all_passed = False
        
        # Check template
        template = tenant.get('template_id')
        if template:
            report.append(f"   ✅ Template: {template}")
        else:
            report.append(f"   ❌ Template: Missing")
            all_passed = False
        
        # 2. Check locations for this tenant
        report.append(f"\n   2️⃣ LOCATIONS (tenant: {tenant_id}):")
        locations = list(db.locations.find({"tenant_id": tenant_id}))
        if locations:
            report.append(f"      ✅ Locations: {len(locations)} found")
            
            for loc in locations:
                loc_name = loc.get('name', 'Unknown')
                report.append(f"\n      📍 {loc_name}")
                
                # Check PayPal
                pp_cid = loc.get('paypal_client_id')
                pp_secret = loc.get('paypal_secret_key')
                if pp_cid and pp_secret:
                    mode = "LIVE" if not loc.get('paypal_sandbox_mode', True) else "SANDBOX"
                    report.append(f"         ✅ PayPal: {mode} configured")
                else:
                    report.append(f"         ⚠️  PayPal: Not configured")
                
                # Check POS
                pos = loc.get('pos_config', {})
                if pos and pos.get('enabled'):
                    report.append(f"         ✅ POS: {pos.get('provider', 'unknown').upper()} enabled")
                else:
                    report.append(f"         ⚠️  POS: Not configured")
                
                # Check opening hours
                hours = loc.get('opening_hours', [])
                special = loc.get('special_opening_days', [])
                if hours:
                    report.append(f"         ✅ Opening Hours: {len(hours)} days configured")
                else:
                    report.append(f"         ⚠️  Opening Hours: Not configured")
                
                if special:
                    report.append(f"         ✅ Special Days: {len(special)} configured")
        else:
            report.append(f"      ❌ Locations: None found")
            all_passed = False
        
        # 3. Check menu items
        report.append(f"\n   3️⃣ MENU (tenant: {tenant_id}):")
        menu_count = db.menu_items.count_documents({"tenant_id": tenant_id})
        cat_count = db.categories.count_documents({"tenant_id": tenant_id})
        
        if menu_count > 0:
            report.append(f"      ✅ Products: {menu_count}")
        else:
            report.append(f"      ⚠️  Products: None")
        
        if cat_count > 0:
            report.append(f"      ✅ Categories: {cat_count}")
        else:
            report.append(f"      ⚠️  Categories: None")
        
        # 4. Check modifier groups
        mod_count = db.modifier_groups.count_documents({"tenant_id": tenant_id})
        if mod_count > 0:
            report.append(f"      ✅ Modifier Groups: {mod_count}")
else:
    report.append("❌ No tenants found!")
    all_passed = False

report.append("")
report.append("="*80)
if all_passed:
    report.append("✅ ALL CHECKS PASSED - PERSISTENCE VERIFIED")
else:
    report.append("❌ SOME CHECKS FAILED - SEE DETAILS ABOVE")
report.append("="*80)

# Print to console
for line in report:
    print(line)

# Write to file
with open('/tmp/persistence_report.txt', 'w') as f:
    f.write('\n'.join(report))

print(f"\n📄 Report written to: /tmp/persistence_report.txt")

# Exit with proper code
sys.exit(0 if all_passed else 1)

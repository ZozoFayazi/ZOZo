"""
Order Validator Service for ZOZO Burger
Validates order structure before saving/sending to POS
Prevents ExpertOrder format errors
Created: 22 January 2026
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class OrderValidator:
    """Validates order structure for ExpertOrder compatibility"""
    
    @staticmethod
    def validate_order(order_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate order structure
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required_fields = ['order_id', 'customer_name', 'location_id', 'items', 'total']
        for field in required_fields:
            if field not in order_data:
                errors.append(f"Fehlendes Pflichtfeld: {field}")
        
        # Validate items
        items = order_data.get('items', [])
        
        if not items:
            errors.append("Bestellung hat keine Items!")
            return False, errors
        
        for idx, item in enumerate(items):
            item_errors = OrderValidator._validate_item(item, idx)
            errors.extend(item_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_item(item: Dict, idx: int) -> List[str]:
        """Validate a single order item"""
        errors = []
        
        # Check required item fields
        if 'name' not in item:
            errors.append(f"Item {idx}: Fehlt 'name'")
        
        if 'price' not in item:
            errors.append(f"Item {idx}: Fehlt 'price'")
        
        # Check for common mistakes
        item_name = item.get('name', '')
        
        # ERROR 1: Größe im Namen (sollte in size-Feld sein)
        if any(size in item_name for size in ['125g', '180g', 'Medium', 'Large', 'MEDIUM', 'LARGE']):
            if '125g' in item_name or '180g' in item_name:
                errors.append(f"Item {idx} '{item_name}': ❌ Größe im Namen! Nutze stattdessen 'size'-Feld")
        
        # Check if it's a menu
        is_menu = 'menü' in item_name.lower() or 'menu' in item_name.lower()
        
        if is_menu:
            # Menu-specific validation
            menu_errors = OrderValidator._validate_menu_item(item, idx)
            errors.extend(menu_errors)
        
        return errors
    
    @staticmethod
    def _validate_menu_item(item: Dict, idx: int) -> List[str]:
        """Validate menu item structure for ExpertOrder"""
        errors = []
        warnings = []
        
        # ERROR 2: Using wrong field for menu components
        if 'menu_components' in item:
            errors.append(
                f"Item {idx}: ❌ 'menu_components' Objekt erkannt! "
                f"ExpertOrder Connector unterstützt das NICHT! "
                f"Verwende stattdessen: customizations, removed_ingredients, extras, modifiers"
            )
        
        # ERROR 3: All customizations in one array
        customizations = item.get('customizations', [])
        
        if customizations and len(customizations) > 2:
            # Check if it contains beilage/getränk/sauce
            has_side = any('pommes' in c.lower() or 'fries' in c.lower() or 'onion rings' in c.lower() 
                          for c in customizations if isinstance(c, str))
            has_drink = any('cola' in c.lower() or 'fanta' in c.lower() or 'sprite' in c.lower() 
                           for c in customizations if isinstance(c, str))
            has_sauce = any('ketchup' in c.lower() or 'mayo' in c.lower() or 'sauce' in c.lower() 
                           for c in customizations if isinstance(c, str))
            has_removals = any(c.startswith('- ') or 'ohne' in c.lower() 
                              for c in customizations if isinstance(c, str))
            
            if has_side:
                errors.append(
                    f"Item {idx}: ❌ Beilage in customizations! "
                    f"Muss in modifiers.beilage Objekt!"
                )
            
            if has_drink:
                errors.append(
                    f"Item {idx}: ❌ Getränk in customizations! "
                    f"Muss in modifiers.getraenk Objekt!"
                )
            
            if has_sauce:
                errors.append(
                    f"Item {idx}: ❌ Sauce in customizations! "
                    f"Muss in modifiers.sauce Objekt!"
                )
            
            if has_removals:
                errors.append(
                    f"Item {idx}: ❌ Removals ('- Ohne...') in customizations! "
                    f"Muss in removed_ingredients Array (ohne Prefix)!"
                )
        
        # WARN: Missing modifiers for menu
        if not item.get('modifiers'):
            warnings.append(
                f"Item {idx}: ⚠️ Menü ohne 'modifiers' - Beilage/Getränk fehlen möglicherweise!"
            )
        else:
            # NEW VALIDATION: Check for duplicate sides/drinks
            modifiers = item.get('modifiers', {})
            
            # Count beilage entries
            beilage_count = sum(1 for key in modifiers.keys() if 'beilage' in key.lower())
            if beilage_count > 1:
                errors.append(
                    f"Item {idx}: ❌ MEHRERE BEILAGEN erkannt ({beilage_count})! "
                    f"Pro Menü ist nur EINE Beilage erlaubt!"
                )
            
            # Count getränk entries  
            getraenk_count = sum(1 for key in modifiers.keys() if 'getr' in key.lower() or 'drink' in key.lower())
            if getraenk_count > 1:
                errors.append(
                    f"Item {idx}: ❌ MEHRERE GETRÄNKE erkannt ({getraenk_count})! "
                    f"Pro Menü ist nur EIN Getränk erlaubt!"
                )
        
        # Log warnings
        for warn in warnings:
            logger.warning(warn)
        
        return errors
    
    @staticmethod
    def get_validation_report(order_data: Dict) -> Dict:
        """
        Get detailed validation report
        
        Returns:
            {
                valid: bool,
                errors: [],
                warnings: [],
                message: str
            }
        """
        is_valid, errors = OrderValidator.validate_order(order_data)
        
        return {
            "valid": is_valid,
            "errors": errors,
            "error_count": len(errors),
            "message": "Bestellung ist gültig" if is_valid else f"{len(errors)} Fehler gefunden"
        }


class OrderAutoConverter:
    """
    Automatically convert common wrong formats to correct format
    ONLY for known patterns - doesn't fix everything!
    """
    
    @staticmethod
    def auto_fix_menu_item(item: Dict) -> Tuple[Dict, List[str]]:
        """
        Try to automatically fix common menu item format errors
        
        Returns:
            (fixed_item, list_of_fixes_applied)
        """
        fixes_applied = []
        fixed_item = dict(item)  # Copy
        
        # Check if it's a menu
        is_menu = 'menü' in item.get('name', '').lower() or 'menu' in item.get('name', '').lower()
        
        if not is_menu:
            return fixed_item, fixes_applied
        
        # FIX 1: Convert menu_components to correct fields
        if 'menu_components' in fixed_item:
            components = fixed_item.pop('menu_components')
            fixes_applied.append("Converted menu_components to modifiers")
            
            # Initialize modifiers if not exists
            if 'modifiers' not in fixed_item:
                fixed_item['modifiers'] = {}
            
            # Map components
            if isinstance(components, dict):
                if 'side' in components:
                    fixed_item['modifiers']['beilage'] = {
                        "name": components['side'].get('selected') if isinstance(components['side'], dict) else components['side'],
                        "price": 0.0
                    }
                
                if 'drink' in components:
                    fixed_item['modifiers']['getraenk'] = {
                        "name": components['drink'].get('selected') if isinstance(components['drink'], dict) else components['drink'],
                        "price": 0.0
                    }
                
                if 'dressing' in components:
                    fixed_item['modifiers']['sauce'] = {
                        "name": components['dressing'].get('selected') if isinstance(components['dressing'], dict) else components['dressing'],
                        "price": 0.0
                    }
                
                if 'bun' in components:
                    if 'customizations' not in fixed_item:
                        fixed_item['customizations'] = []
                    bun_name = components['bun'].get('selected') if isinstance(components['bun'], dict) else components['bun']
                    fixed_item['customizations'].append(f"+ {bun_name}")
        
        # FIX 2: Extract removals from customizations
        if 'customizations' in fixed_item:
            customizations = fixed_item['customizations']
            new_customizations = []
            removals = []
            extras_to_move = []
            
            for custom in customizations:
                if isinstance(custom, str):
                    # Check if it's a removal
                    if custom.startswith('- ') or 'ohne' in custom.lower():
                        # Extract item name
                        removal = custom.replace('- Ohne ', '').replace('- ohne ', '').replace('- ', '').strip()
                        removals.append(removal)
                        fixes_applied.append(f"Moved '{custom}' to removed_ingredients")
                    
                    # Check if it's a side/drink/sauce (should be in modifiers)
                    elif any(keyword in custom.lower() for keyword in ['pommes', 'fries', 'onion rings']):
                        # This is a side
                        if 'modifiers' not in fixed_item:
                            fixed_item['modifiers'] = {}
                        fixed_item['modifiers']['beilage'] = {
                            "name": custom.replace('+ ', '').strip(),
                            "price": 0.0
                        }
                        fixes_applied.append(f"Moved '{custom}' to modifiers.beilage")
                    
                    elif any(keyword in custom.lower() for keyword in ['cola', 'fanta', 'sprite', 'wasser']):
                        # This is a drink
                        if 'modifiers' not in fixed_item:
                            fixed_item['modifiers'] = {}
                        fixed_item['modifiers']['getraenk'] = {
                            "name": custom.replace('+ ', '').strip(),
                            "price": 0.0
                        }
                        fixes_applied.append(f"Moved '{custom}' to modifiers.getraenk")
                    
                    elif any(keyword in custom.lower() for keyword in ['ketchup', 'mayo', 'bbq', 'sauce']):
                        # This is a sauce
                        if 'modifiers' not in fixed_item:
                            fixed_item['modifiers'] = {}
                        fixed_item['modifiers']['sauce'] = {
                            "name": custom.replace('+ ', '').strip(),
                            "price": 0.0
                        }
                        fixes_applied.append(f"Moved '{custom}' to modifiers.sauce")
                    
                    # Keep only Brötchen in customizations
                    elif 'brötchen' in custom.lower() or 'bun' in custom.lower():
                        new_customizations.append(custom)
                    
                    # Everything else might be an extra
                    elif custom.startswith('+ ') and 'extra' in custom.lower():
                        extra_name = custom.replace('+ ', '').strip()
                        extras_to_move.append({"name": extra_name, "price": 0.0})
                        fixes_applied.append(f"Moved '{custom}' to extras")
                    else:
                        # Keep as is (unknown)
                        new_customizations.append(custom)
            
            # Apply fixes
            if removals:
                fixed_item['removed_ingredients'] = removals
            
            if extras_to_move:
                if 'extras' not in fixed_item:
                    fixed_item['extras'] = []
                fixed_item['extras'].extend(extras_to_move)
            
            fixed_item['customizations'] = new_customizations
        
        return fixed_item, fixes_applied
    
    @staticmethod
    def convert_order(order_data: Dict) -> Tuple[Dict, List[str]]:
        """
        Auto-convert order to correct format
        
        Returns:
            (converted_order, list_of_fixes_applied)
        """
        all_fixes = []
        converted_order = dict(order_data)
        
        # Convert each item
        if 'items' in converted_order:
            new_items = []
            for idx, item in enumerate(converted_order['items']):
                fixed_item, fixes = OrderAutoConverter.auto_fix_menu_item(item)
                new_items.append(fixed_item)
                
                if fixes:
                    all_fixes.append(f"Item {idx} ({item.get('name', 'Unknown')}): {', '.join(fixes)}")
            
            converted_order['items'] = new_items
        
        return converted_order, all_fixes

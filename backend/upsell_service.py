"""
Upselling Service for ZOZO Burger
Context-aware upsell recommendations
Created: 23 January 2026
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class UpsellService:
    """Service for generating context-aware upsell offers"""
    
    # Dips-Liste (gleich für alle Kategorien)
    DIPS = [
        {"id": "mayo", "name": "Mayonnaise", "price": 0.99},
        {"id": "ketchup", "name": "Ketchup", "price": 0.99},
        {"id": "sweet-sour", "name": "Sweet&Sour-Sauce", "price": 0.99},
        {"id": "sweet-chili", "name": "Sweet Chili-Sauce", "price": 1.19},
        {"id": "chili", "name": "Chilisauce", "price": 1.49},
        {"id": "garlic", "name": "Knobi-Dip", "price": 1.99},
        {"id": "snack-dressing", "name": "Snack Dressing", "price": 1.99},
        {"id": "sour-cream", "name": "Sour Cream", "price": 1.99},
        {"id": "remoulade", "name": "Remoulade", "price": 1.99},
        {"id": "bbq", "name": "BBQ-Sauce", "price": 1.99},
        {"id": "curry", "name": "Curry Sauce", "price": 1.99}
    ]
    
    # Getränke
    DRINKS = {
        "0.5L": [
            {"id": "vio-still-05", "name": "Vio Still 0,5L", "price": 2.49, "pfand": 0.25},
            {"id": "cola-05", "name": "Coca Cola 0,5L", "price": 2.99, "pfand": 0.25},
            {"id": "cola-zero-05", "name": "Coca Cola Zero 0,5L", "price": 2.99, "pfand": 0.25},
            {"id": "fanta-05", "name": "Fanta 0,5L", "price": 2.99, "pfand": 0.25},
            {"id": "mezzo-05", "name": "Mezzo Mix 0,5L", "price": 2.99, "pfand": 0.25},
            {"id": "sprite-05", "name": "Sprite 0,5L", "price": 2.99, "pfand": 0.25}
        ],
        "1.0L": [
            {"id": "cola-10", "name": "Coca Cola 1,0L", "price": 3.89, "pfand": 0.15},
            {"id": "cola-zero-10", "name": "Coca Cola Zero 1,0L", "price": 3.89, "pfand": 0.15},
            {"id": "fanta-10", "name": "Fanta 1,0L", "price": 3.89, "pfand": 0.15},
            {"id": "mezzo-10", "name": "Mezzo Mix 1,0L", "price": 3.89, "pfand": 0.15},
            {"id": "sprite-10", "name": "Sprite 1,0L", "price": 3.89, "pfand": 0.15}
        ],
        "0.3L": [
            {"id": "apfel-03", "name": "Vio Apfelschorle 0,3L", "price": 2.89, "pfand": 0.15},
            {"id": "rhabarber-03", "name": "Vio Rhabarberschorle 0,3L", "price": 2.89, "pfand": 0.15},
            {"id": "johannisbeer-03", "name": "Vio Johannisbeer-Schorle 0,3L", "price": 2.89, "pfand": 0.15}
        ],
        "0.4L": [
            {"id": "fuze-peach", "name": "Fuze Tea Pfirsich 0,4L", "price": 2.89, "pfand": 0.25},
            {"id": "fuze-lemon", "name": "Fuze Tea Zitrone 0,4L", "price": 2.89, "pfand": 0.25}
        ]
    }
    
    # Desserts
    DESSERTS = [
        {"id": "brownie", "name": "American ZOZO Brownie", "price": 3.49},
        {"id": "tiramisu", "name": "TiramizOZO", "price": 3.49, "alcohol": True},
        {"id": "muffin", "name": "Miss Chocolic Muffin", "price": 3.49}
    ]
    
    # Extra Sidekicks
    SIDEKICKS = [
        {"id": "mozza-sticks", "name": "Mozzarella Sticks (6 Stück)", "price": 6.39},
        {"id": "nuggets-6", "name": "Chicken Nuggets (6 Stück)", "price": 6.99},
        {"id": "wings-6", "name": "Chicken Wings (6 Stück)", "price": 7.99},
        {"id": "crunchy-6", "name": "Crunchy Wings (6 Stück)", "price": 8.49},
        {"id": "fire-6", "name": "Fire Wings (6 Stück)", "price": 8.49},
        {"id": "chili-cheese", "name": "Chili Cheese Nuggets (8 Stück)", "price": 6.89},
        {"id": "onion-rings", "name": "Onion Rings (8 Stück)", "price": 5.99}
    ]
    
    # Beilagen-Alternativen (für Menü-Tausch)
    SIDE_ALTERNATIVES = [
        {"id": "pommes", "name": "Pommes Frites", "price": 0.00},
        {"id": "sweet-potato", "name": "Sweet Potato Fries", "price": 0.99},
        {"id": "twister", "name": "Twister", "price": 0.99},
        {"id": "country", "name": "Country Potatoes", "price": 0.99},
        {"id": "potato-dippers", "name": "Potato Dippers", "price": 0.99}
    ]
    
    @classmethod
    def get_upsells_for_burger_single(cls, burger_size: str) -> Dict:
        """Get upsells for single burger (not menu)"""
        
        # A1: Mehr Fleisch (passende Größe)
        extra_patty = None
        if burger_size and 'medium' in burger_size.lower():
            extra_patty = {"id": "extra-patty-125", "name": "Extra Beef Patty 125g", "price": 5.90}
        elif burger_size and 'large' in burger_size.lower():
            extra_patty = {"id": "extra-patty-180", "name": "Extra Beef Patty 180g", "price": 7.90}
        
        categories = [
            {
                "id": "more-meat",
                "headline": "Mehr Fleisch, mehr Glück.",
                "type": "single-select",
                "items": [extra_patty] if extra_patty else []
            },
            {
                "id": "cheese",
                "headline": "Käse macht alles besser.",
                "type": "single-select",
                "items": [{"id": "extra-cheese", "name": "Extra Käse", "price": 1.50}]
            },
            {
                "id": "crunch",
                "headline": "Crunch gefällig ?",
                "type": "single-select",
                "items": [{"id": "fried-onions", "name": "Röstzwiebeln", "price": 1.00}]
            },
            {
                "id": "toppings",
                "headline": "Ein bisschen extra geht immer.",
                "type": "multi-select",
                "items": [
                    {"id": "jalapenos", "name": "Jalapeños", "price": 1.00},
                    {"id": "mushrooms", "name": "Champignons", "price": 1.50},
                    {"id": "olives", "name": "Oliven", "price": 1.50},
                    {"id": "peppers", "name": "Peperoni", "price": 1.00},
                    {"id": "rucola", "name": "Rucola", "price": 1.00},
                    {"id": "lettuce", "name": "Eisbergsalat", "price": 0.50},
                    {"id": "tomato", "name": "Tomate", "price": 0.50},
                    {"id": "onions", "name": "Zwiebeln", "price": 0.50},
                    {"id": "red-onions", "name": "Rote Zwiebeln", "price": 0.50},
                    {"id": "pickles", "name": "Gewürzgurken", "price": 0.50},
                    {"id": "bacon", "name": "Bacon", "price": 2.00},
                    {"id": "egg", "name": "Spiegelei", "price": 2.00}
                ]
            },
            {
                "id": "dips",
                "headline": "Ohne Dip ist es nur halb so wild.",
                "type": "quantity-select",
                "info": "Extra verpackt geliefert",
                "max_per_item": 5,
                "max_total": 10,
                "items": cls.DIPS
            }
        ]
        
        return {"categories": categories}
    
    @classmethod
    def get_upsells_for_burger_menu(cls) -> Dict:
        """Get upsells for burger menu"""
        
        categories = [
            {
                "id": "side-swap",
                "headline": "Pommes sind top…",
                "type": "single-select",
                "info": "Pommes inklusive, Alternative +€0.99",
                "items": cls.SIDE_ALTERNATIVES
            },
            {
                "id": "extra-sidekick",
                "headline": "Nur gucken zählt nicht, rein damit.",
                "type": "multi-select",
                "info": "Zusätzlich zu deiner Beilage",
                "items": cls.SIDEKICKS
            },
            {
                "id": "dips",
                "headline": "Ohne Dip ist es nur halb so wild.",
                "type": "quantity-select",
                "info": "Extra verpackt geliefert",
                "max_per_item": 5,
                "max_total": 10,
                "items": cls.DIPS
            },
            {
                "id": "drinks",
                "headline": None,
                "type": "multi-select",
                "grouped": True,
                "items": cls.DRINKS
            },
            {
                "id": "dessert",
                "headline": "Nur ein kleines Happy End",
                "type": "multi-select",
                "items": cls.DESSERTS
            }
        ]
        
        return {"categories": categories}
    
    @classmethod
    def get_upsells_for_others(cls) -> Dict:
        """Get upsells for Pizza, Pasta, Salad, Fingerfood"""
        
        categories = [
            {
                "id": "dips",
                "headline": "Ohne Dip ist es nur halb so wild.",
                "type": "quantity-select",
                "info": "Extra verpackt geliefert",
                "max_per_item": 5,
                "max_total": 10,
                "items": cls.DIPS
            },
            {
                "id": "drinks",
                "headline": None,
                "type": "multi-select",
                "grouped": True,
                "items": cls.DRINKS
            },
            {
                "id": "dessert",
                "headline": "Nur ein kleines Happy End",
                "type": "multi-select",
                "items": cls.DESSERTS
            }
        ]
        
        return {"categories": categories}
    
    @classmethod
    def get_upsells(cls, product_type: str, is_menu: bool = False, size: str = None) -> Dict:
        """Get upsells based on context"""
        
        product_type_lower = product_type.lower()
        
        if 'burger' in product_type_lower:
            if is_menu:
                return cls.get_upsells_for_burger_menu()
            else:
                return cls.get_upsells_for_burger_single(size)
        
        # Pizza, Pasta, Salad, Fingerfood
        return cls.get_upsells_for_others()

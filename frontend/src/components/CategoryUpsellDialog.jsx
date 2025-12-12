import React, { useState, useEffect } from 'react';
import { X, Plus, TrendingUp } from 'lucide-react';

function CategoryUpsellDialog({ category, onAddUpsell, onClose }) {
  const [selectedUpsells, setSelectedUpsells] = useState([]);

  // Define upsell suggestions per category
  const upsellData = {
    pizza: {
      title: "🍕 Deine Pizza braucht einen Sidekick!",
      subtitle: "Perfekt dazu:",
      items: [
        { name: "Coca Cola 0,5l", price: 3.24, emoji: "🥤" },
        { name: "Fanta 0,5l", price: 3.24, emoji: "🍊" },
        { name: "Pizzabrötchen 6 Stück", price: 5.99, emoji: "🥖" },
      ]
    },
    pasta: {
      title: "🍝 Macht deine Pasta komplett!",
      subtitle: "Gönn dir dazu:",
      items: [
        { name: "Pizzabrötchen 6 Stück", price: 5.99, emoji: "🥖" },
        { name: "Caesar Salad", price: 8.59, emoji: "🥗" },
        { name: "Coca Cola 0,5l", price: 3.24, emoji: "🥤" },
      ]
    },
    wraps: {
      title: "🌯 Noch Hunger?",
      subtitle: "Mach's zum Menü:",
      items: [
        { name: "French Fries", price: 4.99, emoji: "🍟" },
        { name: "Coca Cola 0,5l", price: 3.24, emoji: "🥤" },
        { name: "Onion Rings", price: 5.69, emoji: "🧅" },
      ]
    },
    salat: {
      title: "🥗 Noch was zum Sattwerden?",
      subtitle: "Perfekte Ergänzung:",
      items: [
        { name: "Pizzabrötchen 6 Stück", price: 5.99, emoji: "🥖" },
        { name: "Vio Still 0,5l", price: 2.74, emoji: "💧" },
      ]
    },
    fingerfood: {
      title: "🍗 Extra Dip gefällig?",
      subtitle: "Macht's noch leckerer:",
      items: [
        { name: "BBQ-Sauce", price: 1.99, emoji: "🍯" },
        { name: "Knoblauchsauce", price: 1.99, emoji: "🧄" },
        { name: "Sweet Chili-Sauce", price: 1.19, emoji: "🌶️" },
        { name: "Coca Cola 0,5l", price: 3.24, emoji: "🥤" },
      ]
    },
    pizzabroetchen: {
      title: "🥖 Noch was zu trinken?",
      subtitle: "Dazu passt:",
      items: [
        { name: "Coca Cola 0,5l", price: 3.24, emoji: "🥤" },
        { name: "Fanta 0,5l", price: 3.24, emoji: "🍊" },
        { name: "Extra Dip", price: 1.99, emoji: "🍯" },
      ]
    },
    imbiss: {
      title: "🌭 Durst?",
      subtitle: "Perfekt dazu:",
      items: [
        { name: "Coca Cola 0,5l", price: 3.24, emoji: "🥤" },
        { name: "Fanta 0,5l", price: 3.24, emoji: "🍊" },
      ]
    },
    default: {
      title: "🍰 Noch was Süßes dazu?",
      subtitle: "Perfekter Abschluss:",
      items: [
        { name: "Tiramizozo", price: 3.49, emoji: "🍰" },
        { name: "American ZOZO Brownie", price: 3.49, emoji: "🍫" },
        { name: "Miss Chocolic Muffin", price: 3.49, emoji: "🧁" },
      ]
    }
  };

  // Get the right upsell data for this category
  const getCategoryData = () => {
    const categorySlug = category?.toLowerCase() || '';
    
    if (categorySlug.includes('pizza')) return upsellData.pizza;
    if (categorySlug.includes('pasta')) return upsellData.pasta;
    if (categorySlug.includes('wrap')) return upsellData.wraps;
    if (categorySlug.includes('salat')) return upsellData.salat;
    if (categorySlug.includes('fingerfood')) return upsellData.fingerfood;
    if (categorySlug.includes('pizzabr')) return upsellData.pizzabroetchen;
    if (categorySlug.includes('imbiss')) return upsellData.imbiss;
    
    return upsellData.default; // Dessert upsell as default
  };

  const data = getCategoryData();

  const toggleUpsell = (item) => {
    if (selectedUpsells.find(u => u.name === item.name)) {
      setSelectedUpsells(selectedUpsells.filter(u => u.name !== item.name));
    } else {
      setSelectedUpsells([...selectedUpsells, item]);
    }
  };

  const handleAddAll = () => {
    selectedUpsells.forEach(item => {
      onAddUpsell({
        menu_item_id: `upsell-${item.name.toLowerCase().replace(/\s+/g, '-')}`,
        name: item.name,
        price: item.price,
        quantity: 1,
        size: 'normal'
      });
    });
    onClose();
  };

  const totalUpsellPrice = selectedUpsells.reduce((sum, item) => sum + item.price, 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
        data-testid="upsell-backdrop"
      />
      
      {/* Dialog */}
      <div className="relative bg-card border border-border rounded-2xl max-w-lg w-full shadow-2xl animate-scale-in">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-secondary rounded-lg transition-colors z-10"
          data-testid="close-upsell-dialog"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Content */}
        <div className="p-8">
          {/* Header with Icon */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/20 rounded-full mb-4">
              <TrendingUp className="h-8 w-8 text-primary" />
            </div>
            <h2 className="text-2xl font-bold mb-2">{data.title}</h2>
            <p className="text-muted-foreground">{data.subtitle}</p>
          </div>

          {/* Upsell Items */}
          <div className="space-y-3 mb-6">
            {data.items.map((item) => {
              const isSelected = selectedUpsells.find(u => u.name === item.name);
              return (
                <button
                  key={item.name}
                  onClick={() => toggleUpsell(item)}
                  className={`w-full p-4 rounded-xl border-2 transition-all text-left ${
                    isSelected
                      ? 'border-primary bg-primary/10 scale-[1.02]'
                      : 'border-border hover:border-primary/50'
                  }`}
                  data-testid={`upsell-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl">{item.emoji}</span>
                      <div>
                        <p className="font-semibold">{item.name}</p>
                        <p className="text-sm text-primary font-bold">+€{item.price.toFixed(2)}</p>
                      </div>
                    </div>
                    {isSelected && (
                      <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                        <Plus className="h-4 w-4 text-white rotate-45" />
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            {selectedUpsells.length > 0 && (
              <button
                onClick={handleAddAll}
                className="btn-primary w-full"
                data-testid="add-upsells-button"
              >
                <Plus className="h-5 w-5 mr-2" />
                Hinzufügen (€{totalUpsellPrice.toFixed(2)})
              </button>
            )}
            
            <button
              onClick={onClose}
              className="w-full py-3 text-muted-foreground hover:text-foreground transition-colors"
              data-testid="no-thanks-button"
            >
              Nein danke, weiter zur Speisekarte
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CategoryUpsellDialog;

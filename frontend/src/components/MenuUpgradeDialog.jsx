import React, { useState } from 'react';
import { X, Check, Plus } from 'lucide-react';

function MenuUpgradeDialog({ item, onClose, onAddToCart }) {
  const [upgradeToMenu, setUpgradeToMenu] = useState(false);
  const [selectedSide, setSelectedSide] = useState('');
  const [selectedDrink, setSelectedDrink] = useState('');

  // Beilagen options
  const sides = [
    { id: 'fries', name: 'Pommes', price: 0 },
    { id: 'sweet-potato', name: 'Sweet Potato Fries', price: 0 },
    { id: 'twister', name: 'Twister Fries', price: 0 },
    { id: 'country', name: 'Country Potatoes', price: 0 },
  ];

  // Getränke options
  const drinks = [
    { id: 'cola', name: 'Coca Cola 0,5l', price: 0 },
    { id: 'cola-zero', name: 'Coca Cola Zero 0,5l', price: 0 },
    { id: 'fanta', name: 'Fanta 0,5l', price: 0 },
    { id: 'mezzo', name: 'Mezzo Mix 0,5l', price: 0 },
    { id: 'sprite', name: 'Sprite 0,5l', price: 0 },
    { id: 'water', name: 'ViO Still 0,5l', price: 0 },
  ];

  // Determine the correct prices based on selected size
  const burgerPrice = item.price_normal || item.price_medium || 0;
  const menuPrice = item.has_sizes && item.selected_size === 'large'
    ? item.menu_upgrade_price_large 
    : item.menu_upgrade_price || item.menu_upgrade_price_medium || 0;
  const upgradeCost = menuPrice - burgerPrice;

  const handleAddToCart = () => {
    if (upgradeToMenu && (!selectedSide || !selectedDrink)) {
      return; // Validation: side and drink must be selected
    }

    const cartItem = {
      menu_item_id: item.id,
      name: upgradeToMenu ? `${item.name} Menü` : item.name,
      price: upgradeToMenu ? menuPrice : burgerPrice,
      quantity: 1,
      size: 'normal',
      extras: [],
      removed: []
    };

    if (upgradeToMenu) {
      // Add side and drink as extras (but with 0 price as they're included)
      const side = sides.find(s => s.id === selectedSide);
      const drink = drinks.find(d => d.id === selectedDrink);
      
      if (side) {
        cartItem.extras.push({
          name: `Beilage: ${side.name}`,
          price: 0
        });
      }
      if (drink) {
        cartItem.extras.push({
          name: `Getränk: ${drink.name}`,
          price: 0
        });
      }
    }

    onAddToCart(cartItem);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
        data-testid="menu-upgrade-backdrop"
      />
      
      {/* Dialog */}
      <div className="relative bg-card border border-border rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-secondary rounded-lg transition-colors z-10"
          data-testid="close-upgrade-dialog"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Content */}
        <div className="p-8">
          {/* Item Info */}
          <div className="mb-6">
            <h2 className="text-2xl font-bold mb-2">{item.name}</h2>
            <p className="text-muted-foreground">{item.description}</p>
          </div>

          {/* Upgrade Options */}
          <div className="space-y-4 mb-6">
            {/* Als Burger */}
            <button
              onClick={() => setUpgradeToMenu(false)}
              className={`w-full p-6 rounded-xl border-2 transition-all ${
                !upgradeToMenu
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50'
              }`}
              data-testid="option-burger-only"
            >
              <div className="flex items-center justify-between">
                <div className="text-left">
                  <h3 className="font-semibold text-lg mb-1">🍔 Als Burger</h3>
                  <p className="text-sm text-muted-foreground">Nur der Burger</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary">€{burgerPrice.toFixed(2)}</div>
                </div>
              </div>
            </button>

            {/* Als Menü */}
            {item.can_upgrade_to_menu && (
              <button
                onClick={() => setUpgradeToMenu(true)}
                className={`w-full p-6 rounded-xl border-2 transition-all ${
                  upgradeToMenu
                    ? 'border-primary bg-primary/10'
                    : 'border-border hover:border-primary/50'
                }`}
                data-testid="option-as-menu"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="text-left">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-lg">🍟🥤 Als Menü</h3>
                      <span className="px-2 py-1 bg-primary/20 text-primary text-xs font-bold rounded">
                        +€{upgradeCost.toFixed(2)}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">Burger + Beilage + Getränk 0,5l</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary">€{menuPrice.toFixed(2)}</div>
                  </div>
                </div>

                {upgradeToMenu && (
                  <div className="space-y-4 pt-4 border-t border-border" onClick={(e) => e.stopPropagation()}>
                    {/* Beilage Selection */}
                    <div>
                      <label className="block text-sm font-medium mb-2">Wähle deine Beilage:</label>
                      <div className="grid grid-cols-2 gap-2">
                        {sides.map((side) => (
                          <button
                            key={side.id}
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedSide(side.id);
                            }}
                            className={`p-3 rounded-lg border transition-all text-left ${
                              selectedSide === side.id
                                ? 'border-primary bg-primary/20'
                                : 'border-border hover:border-primary/50'
                            }`}
                            data-testid={`side-${side.id}`}
                          >
                            <div className="flex items-center gap-2">
                              {selectedSide === side.id && <Check className="h-4 w-4 text-primary" />}
                              <span className="text-sm">{side.name}</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Getränk Selection */}
                    <div>
                      <label className="block text-sm font-medium mb-2">Wähle dein Getränk:</label>
                      <div className="grid grid-cols-2 gap-2">
                        {drinks.map((drink) => (
                          <button
                            key={drink.id}
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedDrink(drink.id);
                            }}
                            className={`p-3 rounded-lg border transition-all text-left ${
                              selectedDrink === drink.id
                                ? 'border-primary bg-primary/20'
                                : 'border-border hover:border-primary/50'
                            }`}
                            data-testid={`drink-${drink.id}`}
                          >
                            <div className="flex items-center gap-2">
                              {selectedDrink === drink.id && <Check className="h-4 w-4 text-primary" />}
                              <span className="text-sm">{drink.name}</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </button>
            )}
          </div>

          {/* Add to Cart Button */}
          <button
            onClick={handleAddToCart}
            disabled={upgradeToMenu && (!selectedSide || !selectedDrink)}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            data-testid="add-to-cart-final"
          >
            <Plus className="h-5 w-5 mr-2" />
            In den Warenkorb (€{(upgradeToMenu ? menuPrice : burgerPrice).toFixed(2)})
          </button>

          {upgradeToMenu && (!selectedSide || !selectedDrink) && (
            <p className="text-sm text-red-500 text-center mt-2">
              Bitte wähle eine Beilage und ein Getränk
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default MenuUpgradeDialog;

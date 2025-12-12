import React, { useState } from 'react';
import { X, Plus, Minus, Check } from 'lucide-react';
import { toast } from 'sonner';

// Parse extras from string format "Extra Käse (+€1.50)" to object
const parseExtras = (extrasArray) => {
  if (!extrasArray || !Array.isArray(extrasArray)) return [];
  
  return extrasArray.map(extra => {
    const match = extra.match(/^(.+?)\s*\(\+€([\d.]+)\)$/);
    if (match) {
      return { name: match[1].trim(), price: parseFloat(match[2]) };
    }
    return { name: extra, price: 0 };
  });
};

function ProductCustomizer({ item, size, onAddToCart, onClose }) {
  const [quantity, setQuantity] = useState(1);
  const [selectedExtras, setSelectedExtras] = useState([]);
  const [selectedRemovals, setSelectedRemovals] = useState([]);
  const [specialInstructions, setSpecialInstructions] = useState('');
  
  // Menu upgrade state
  const [upgradeToMenu, setUpgradeToMenu] = useState(false);
  const [selectedSide, setSelectedSide] = useState('');
  const [selectedDrink, setSelectedDrink] = useState('');

  // Get product-specific removable ingredients and extras
  const removableIngredients = item.removable_ingredients || [];
  const availableExtras = parseExtras(item.available_extras || []);

  // Menu upgrade options
  const sides = [
    { id: 'fries', name: 'Pommes' },
    { id: 'sweet-potato', name: 'Sweet Potato Fries' },
    { id: 'twister', name: 'Twister Fries' },
    { id: 'country', name: 'Country Potatoes' },
  ];

  const drinks = [
    { id: 'cola', name: 'Coca Cola 0,5l' },
    { id: 'cola-zero', name: 'Coca Cola Zero 0,5l' },
    { id: 'fanta', name: 'Fanta 0,5l' },
    { id: 'mezzo', name: 'Mezzo Mix 0,5l' },
    { id: 'sprite', name: 'Sprite 0,5l' },
    { id: 'water', name: 'ViO Still 0,5l' },
  ];

  const basePrice = size === 'medium' && item.price_medium 
    ? item.price_medium 
    : size === 'large' && item.price_large 
    ? item.price_large 
    : item.price_normal || 0;
  
  // Menu upgrade price
  const menuUpgradePrice = size === 'large' && item.menu_upgrade_price_large
    ? item.menu_upgrade_price_large
    : item.menu_upgrade_price || item.menu_upgrade_price_medium || 0;
  
  const canUpgradeToMenu = item.can_upgrade_to_menu && menuUpgradePrice > 0;

  const extrasTotal = selectedExtras.reduce((sum, extra) => sum + extra.price, 0);
  const itemPrice = upgradeToMenu ? menuUpgradePrice : basePrice;
  const totalPrice = (itemPrice + extrasTotal) * quantity;

  const toggleExtra = (extra) => {
    if (selectedExtras.find(e => e.name === extra.name)) {
      setSelectedExtras(selectedExtras.filter(e => e.name !== extra.name));
    } else {
      setSelectedExtras([...selectedExtras, extra]);
    }
  };

  const toggleRemoval = (removal) => {
    if (selectedRemovals.includes(removal)) {
      setSelectedRemovals(selectedRemovals.filter(r => r !== removal));
    } else {
      setSelectedRemovals([...selectedRemovals, removal]);
    }
  };

  const handleAddToCart = () => {
    // Validation for menu upgrade
    if (upgradeToMenu && (!selectedSide || !selectedDrink)) {
      toast.error('Bitte wähle eine Beilage und ein Getränk für das Menü');
      return;
    }

    let customizedName = upgradeToMenu ? `${item.name} Menü` : item.name;
    
    // Build extras array including menu components
    const allExtras = [...selectedExtras];
    
    if (upgradeToMenu) {
      const side = sides.find(s => s.id === selectedSide);
      const drink = drinks.find(d => d.id === selectedDrink);
      
      if (side) {
        allExtras.push({
          name: `Beilage: ${side.name}`,
          price: 0
        });
      }
      if (drink) {
        allExtras.push({
          name: `Getränk: ${drink.name}`,
          price: 0
        });
      }
    }
    
    if (allExtras.length > 0 || selectedRemovals.length > 0) {
      const modifications = [];
      if (allExtras.length > 0) {
        modifications.push(`+ ${allExtras.map(e => e.name).join(', ')}`);
      }
      if (selectedRemovals.length > 0) {
        modifications.push(`- ${selectedRemovals.join(', ')}`);
      }
      customizedName += ` (${modifications.join(' ')})`;
    }

    if (specialInstructions) {
      customizedName += ` | Hinweis: ${specialInstructions}`;
    }

    onAddToCart({
      menu_item_id: item.id,
      name: customizedName,
      price: itemPrice + extrasTotal,
      size: size || null,
      quantity: quantity,
      extras: allExtras,
      removed: selectedRemovals
    });

    toast.success(`${customizedName} zum Warenkorb hinzugefügt`);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="relative bg-card border border-border rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-scale-in">
        {/* Header with Image */}
        {item.image_url && (
          <div className="aspect-video overflow-hidden">
            <img
              src={item.image_url}
              alt={item.name}
              className="w-full h-full object-cover"
            />
          </div>
        )}

        <div className="p-6 space-y-6">
          {/* Title and Close */}
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-serif font-semibold mb-2">{item.name}</h2>
              {item.description && (
                <p className="text-sm text-muted-foreground">{item.description}</p>
              )}
              <p className="text-lg font-bold text-primary mt-2">
                Basis: €{basePrice.toFixed(2)}
                {size && ` (${size})`}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-secondary rounded-lg transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Extras */}
          {availableExtras.length > 0 && (
            <div>
              <h3 className="font-semibold mb-3">Extras hinzufügen</h3>
              <div className="grid grid-cols-2 gap-3">
                {availableExtras.map((extra) => {
                  const isSelected = selectedExtras.find(e => e.name === extra.name);
                  return (
                    <button
                      key={extra.name}
                      onClick={() => toggleExtra(extra)}
                      className={`p-3 rounded-lg border-2 transition-all text-left ${
                        isSelected
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-primary/40'
                      }`}
                      data-testid={`extra-${extra.name.toLowerCase().replace(/\s+/g, '-')}`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">{extra.name}</p>
                          <p className="text-xs text-muted-foreground">+€{extra.price.toFixed(2)}</p>
                        </div>
                        {isSelected && <Check className="h-4 w-4 text-primary" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Removals */}
          {removableIngredients.length > 0 && (
            <div>
              <h3 className="font-semibold mb-3">Zutaten entfernen</h3>
              <div className="flex flex-wrap gap-2">
                {removableIngredients.map((removal) => {
                  const isSelected = selectedRemovals.includes(removal);
                  return (
                    <button
                      key={removal}
                      onClick={() => toggleRemoval(removal)}
                      className={`px-3 py-1.5 rounded-full text-sm transition-all ${
                        isSelected
                          ? 'bg-destructive/20 text-destructive border-2 border-destructive'
                          : 'bg-secondary text-foreground border-2 border-transparent hover:border-border'
                      }`}
                      data-testid={`remove-${removal.toLowerCase().replace(/\s+/g, '-')}`}
                    >
                      {isSelected && '− '}Ohne {removal}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Special Instructions */}
          <div>
            <h3 className="font-semibold mb-3">Besondere Wünsche</h3>
            <textarea
              value={specialInstructions}
              onChange={(e) => setSpecialInstructions(e.target.value)}
              placeholder="z.B. extra scharf, gut durchgebraten..."
              rows={3}
              className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              data-testid="special-instructions-input"
            />
          </div>

          {/* Menu Upgrade Section */}
          {canUpgradeToMenu && (
            <div className="space-y-4 p-4 bg-accent rounded-xl border border-border">
              <h3 className="font-semibold text-lg">🍔 Als Menü upgraden?</h3>
              
              <div className="grid grid-cols-2 gap-3">
                {/* Als Burger */}
                <button
                  onClick={() => setUpgradeToMenu(false)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    !upgradeToMenu
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/40'
                  }`}
                  data-testid="option-burger-only"
                >
                  <div>
                    <h4 className="font-medium mb-1">Nur Burger</h4>
                    <p className="text-sm text-muted-foreground">€{basePrice.toFixed(2)}</p>
                  </div>
                </button>

                {/* Als Menü */}
                <button
                  onClick={() => setUpgradeToMenu(true)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    upgradeToMenu
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/40'
                  }`}
                  data-testid="option-as-menu"
                >
                  <div>
                    <h4 className="font-medium mb-1">Als Menü</h4>
                    <p className="text-sm text-muted-foreground">€{menuUpgradePrice.toFixed(2)}</p>
                    <p className="text-xs text-primary font-semibold mt-1">
                      +€{(menuUpgradePrice - basePrice).toFixed(2)}
                    </p>
                  </div>
                </button>
              </div>

              {/* Menu Options: Beilage & Getränk */}
              {upgradeToMenu && (
                <div className="space-y-4 mt-4 pt-4 border-t border-border">
                  {/* Beilage Selection */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Wähle deine Beilage:</label>
                    <div className="grid grid-cols-2 gap-2">
                      {sides.map((side) => (
                        <button
                          key={side.id}
                          onClick={() => setSelectedSide(side.id)}
                          className={`p-3 rounded-lg border-2 transition-all text-left ${
                            selectedSide === side.id
                              ? 'border-primary bg-primary/20'
                              : 'border-border hover:border-primary/40'
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
                          onClick={() => setSelectedDrink(drink.id)}
                          className={`p-3 rounded-lg border-2 transition-all text-left ${
                            selectedDrink === drink.id
                              ? 'border-primary bg-primary/20'
                              : 'border-border hover:border-primary/40'
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

                  {/* Validation Message */}
                  {(!selectedSide || !selectedDrink) && (
                    <p className="text-sm text-destructive">
                      Bitte wähle eine Beilage und ein Getränk
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Quantity and Total */}
          <div className="flex items-center justify-between p-4 bg-background rounded-lg border border-border">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium">Menge:</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="p-2 hover:bg-secondary rounded-lg transition-colors"
                >
                  <Minus className="h-4 w-4" />
                </button>
                <span className="w-8 text-center font-semibold">{quantity}</span>
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="p-2 hover:bg-secondary rounded-lg transition-colors"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Gesamt</p>
              <p className="text-2xl font-bold text-primary">€{totalPrice.toFixed(2)}</p>
            </div>
          </div>

          {/* Add to Cart Button */}
          <button
            onClick={handleAddToCart}
            className="btn-primary w-full"
            data-testid="add-to-cart-final"
          >
            <Plus className="inline h-5 w-5 mr-2" />
            Zum Warenkorb hinzufügen (€{totalPrice.toFixed(2)})
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProductCustomizer;

import React, { useState } from 'react';
import { X, Plus, Minus, Check } from 'lucide-react';
import { toast } from 'sonner';

// Helper function to build full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  // Convert /uploads/... to /api/uploads/... for Kubernetes Ingress routing
  if (imageUrl.startsWith('/uploads/')) {
    return `${backendUrl}/api${imageUrl}`;
  }
  return `${backendUrl}${imageUrl}`;
};

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

function ProductCustomizer({ item, size, onAddToCart, onClose, modifierGroups = [] }) {
  const [quantity, setQuantity] = useState(1);
  const [selectedExtras, setSelectedExtras] = useState([]);
  const [selectedRemovals, setSelectedRemovals] = useState([]);
  const [specialInstructions, setSpecialInstructions] = useState('');
  const [selectedModifiers, setSelectedModifiers] = useState({});
  
  // Menu upgrade state
  const [upgradeToMenu, setUpgradeToMenu] = useState(false);
  const [selectedSide, setSelectedSide] = useState('');
  const [selectedDrink, setSelectedDrink] = useState('');
  
  // ⚠️ CRITICAL: Ensure only ONE side and ONE drink can be selected
  // This prevents multiple sides/drinks in a single menu
  const handleSideSelection = (sideId) => {
    // Toggle: if same side clicked again, deselect
    setSelectedSide(selectedSide === sideId ? '' : sideId);
  };
  
  const handleDrinkSelection = (drinkId) => {
    // Toggle: if same drink clicked again, deselect
    setSelectedDrink(selectedDrink === drinkId ? '' : drinkId);
  };
  
  // Bun selection state (for burgers)
  const [selectedBun, setSelectedBun] = useState('');
  
  // Get modifier groups for this product
  const productModifiers = modifierGroups.filter(g => 
    item.modifier_group_ids?.includes(g.id)
  );

  // Get product-specific removable ingredients and extras
  const removableIngredients = item.removable_ingredients || [];
  const availableExtras = parseExtras(item.available_extras || []);

  // Ingredient icons mapping
  const getIngredientIcon = (ingredient) => {
    const lower = ingredient.toLowerCase();
    if (lower.includes('tomat')) return { type: 'emoji', icon: '🍅' };
    if (lower.includes('zwiebel')) return { type: 'emoji', icon: '🧅' };
    if (lower.includes('gurke') || lower.includes('pickle')) return { type: 'emoji', icon: '🥒' };
    if (lower.includes('salat')) return { type: 'emoji', icon: '🥬' };
    if (lower.includes('käse') || lower.includes('cheese')) return { type: 'emoji', icon: '🧀' };
    if (lower.includes('bacon') || lower.includes('speck')) return { type: 'emoji', icon: '🥓' };
    if (lower.includes('beef') || lower.includes('patty') || lower.includes('fleisch')) {
      return { 
        type: 'image', 
        icon: 'https://customer-assets.emergentagent.com/job_gourmet-bites-15/artifacts/gxkjc9an_IMG_1232.png' 
      };
    }
    if (lower.includes('spiegelei') || lower.includes('fried egg')) return { type: 'emoji', icon: '🍳' };
    if (lower.includes('ei') || lower.includes('egg')) return { type: 'emoji', icon: '🥚' };
    if (lower.includes('jalapeño') || lower.includes('chili')) return { type: 'emoji', icon: '🌶️' };
    if (lower.includes('pilz') || lower.includes('champignon')) return { type: 'emoji', icon: '🍄' };
    if (lower.includes('paprika')) return { type: 'emoji', icon: '🫑' };
    return { type: 'emoji', icon: '🍴' }; // Default icon
  };
  
  // Check if this is a burger (but not a Smash Burger or Salad) - requires bun selection
  const requiresBunSelection = item.name && 
    (item.name.toLowerCase().includes('burger') && 
     !item.name.toLowerCase().includes('smash') &&
     !item.name.toLowerCase().includes('salad') &&
     !item.name.toLowerCase().includes('salat'));
  
  // Available bun types
  const bunTypes = [
    { id: 'brioche', name: 'Briochebrötchen' },
    { id: 'semolina', name: 'Semolinabrötchen' }
  ];

  // Menu upgrade options (sides with prices)
  const sides = [
    { id: 'fries', name: 'Pommes', price: 0 },
    { id: 'sweet-potato', name: 'Sweet Potato Fries', price: 0.99 },
    { id: 'twister', name: 'Twister Fries', price: 0.99 },
    { id: 'country', name: 'Country Potatoes', price: 0.99 },
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
  
  // Calculate modifier price (from selectedModifiers)
  const modifierPrice = Object.values(selectedModifiers).reduce((sum, modifierData) => {
    if (typeof modifierData === 'object' && modifierData.price) {
      return sum + modifierData.price;
    }
    return sum;
  }, 0);
  
  // Calculate side surcharge (if menu and premium side selected)
  const selectedSideObj = sides.find(s => s.id === selectedSide);
  const sideSurcharge = upgradeToMenu && selectedSideObj ? selectedSideObj.price : 0;
  
  const itemPrice = upgradeToMenu ? menuUpgradePrice : basePrice;
  const totalPrice = (itemPrice + extrasTotal + sideSurcharge + modifierPrice) * quantity;

  // Check if all required modifiers are selected
  const hasRequiredModifiers = productModifiers.every(group => {
    if (group.required) {
      return selectedModifiers[group.id] !== undefined && selectedModifiers[group.id] !== null;
    }
    return true;
  });

  // Disable "Add to Cart" if:
  // 1. Bun selection is required but not selected
  // 2. Menu upgrade is selected but side/drink not selected
  // 3. Required modifiers are not selected
  const isAddToCartDisabled = 
    (requiresBunSelection && !selectedBun) ||
    (upgradeToMenu && (!selectedSide || !selectedDrink)) ||
    !hasRequiredModifiers;

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
    // Validation: Check required modifier groups
    const missingModifiers = productModifiers.filter(g => 
      g.required && !selectedModifiers[g.id]
    );
    
    if (missingModifiers.length > 0) {
      toast.error(`Bitte wählen: ${missingModifiers[0].title}`);
      return;
    }
    
    // Validation for bun selection (required for burgers except Smash)
    if (requiresBunSelection && !selectedBun) {
      toast.error('Bitte wähle eine Brötchen-Art');
      return;
    }
    
    // Validation for menu upgrade
    if (upgradeToMenu && (!selectedSide || !selectedDrink)) {
      toast.error('Bitte wähle eine Beilage und ein Getränk für das Menü');
      return;
    }

    let customizedName = upgradeToMenu ? `${item.name} Menü` : item.name;
    
    // Build customizations array for display AND POS
    const customizations = [];
    
    // ⚠️ CHANGED 22.01.2026: Modifiers werden NICHT zu customizations hinzugefügt!
    // Modifiers werden separat als 'modifiers' Objekt übergeben
    // Nur Brötchen, Extras und Hinweise gehen in customizations
    
    // Add bun type (WITHOUT adding to name)
    if (selectedBun) {
      const bunName = bunTypes.find(b => b.id === selectedBun)?.name;
      if (bunName) {
        customizations.push(`+ ${bunName}`);
      }
    }
    
    // Build extras array (WITHOUT menu components - they go to modifiers)
    const allExtras = [...selectedExtras];
    
    // ⚠️ CRITICAL FIX - DO NOT REMOVE - 22.01.2026 ⚠️
    // Menu components MUST be sent as 'modifiers', NOT as 'extras'
    // Without this: Menü-Beilage und Getränk fehlen auf Kassenbon!
    const menuModifiers = {};
    
    if (upgradeToMenu) {
      const side = sides.find(s => s.id === selectedSide);
      const drink = drinks.find(d => d.id === selectedDrink);
      
      if (side) {
        menuModifiers.beilage = {
          name: side.name,
          price: side.price, // 0 for Pommes, 0.99 for premium sides
          pos_item_id: side.pos_item_id || `SIDE-${side.id}`
        };
        // Also add surcharge to extras if premium side
        if (side.price > 0) {
          allExtras.push({
            name: `${side.name} Aufpreis`,
            price: side.price
          });
        }
      }
      if (drink) {
        menuModifiers.getraenk = {
          name: drink.name,
          price: 0,
          pos_item_id: drink.pos_item_id || `DRINK-${drink.id}`
        };
      }
    }
    // ⚠️ END CRITICAL FIX ⚠️
    
    // Add extras and removals to customizations (NOT to name in parentheses)
    // Each will appear as separate line in cart AND on POS receipt
    if (allExtras.length > 0) {
      allExtras.forEach(extra => {
        customizations.push(`+ ${extra.name}`);
      });
    }
    
    // ⚠️ CHANGED 22.01.2026: removed_ingredients NICHT zu customizations hinzufügen!
    // Sie werden separat als 'removed_ingredients' Array übergeben
    // Backend verarbeitet sie direkt aus removed_ingredients
    
    // Nur Spezialanweisungen als Hinweis hinzufügen
    if (specialInstructions) {
      customizations.push(`Hinweis: ${specialInstructions}`);
    }

    onAddToCart({
      menu_item_id: item.id,
      name: customizedName,  // Clean name without parentheses
      price: itemPrice + extrasTotal + sideSurcharge + modifierPrice,
      size: size || null,
      quantity: quantity,
      category: item.category_id,  // Für Daily Deal Matching
      customizations: customizations,  // All selections as separate lines
      extras: allExtras,
      removed_ingredients: selectedRemovals,
      // ⚠️ CRITICAL FIX - DO NOT REMOVE - 22.01.2026 ⚠️
      // Merge regular modifiers + menu modifiers
      // menuModifiers contains: beilage, getraenk (from menu upgrade)
      // selectedModifiers contains: sauce, dressing, pasta type, etc.
      modifiers: { ...selectedModifiers, ...menuModifiers }
      // ⚠️ END CRITICAL FIX ⚠️
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
              src={getImageUrl(item.image_url)}
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

          {/* Menu Upgrade Section - FIRST */}
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
                          <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              {selectedSide === side.id && <Check className="h-4 w-4 text-primary" />}
                              <span className="text-sm">{side.name}</span>
                            </div>
                            {side.price > 0 && (
                              <span className="text-xs text-primary font-semibold">+€{side.price.toFixed(2)}</span>
                            )}
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
                </div>
              )}
            </div>
          )}

          {/* Bun Selection (Required for Burgers) */}
          {requiresBunSelection && (
            <div className="p-4 bg-accent rounded-xl border-2 border-primary/40">
              <h3 className="font-semibold mb-1">Wähle dein Brötchen</h3>
              <p className="text-xs text-muted-foreground mb-3">Bitte wähle eine Brötchen-Art</p>
              <div className="grid grid-cols-2 gap-3">
                {bunTypes.map((bun) => (
                  <button
                    key={bun.id}
                    onClick={() => setSelectedBun(bun.id)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      selectedBun === bun.id
                        ? 'border-primary bg-primary/20'
                        : 'border-border hover:border-primary/40'
                    }`}
                    data-testid={`bun-${bun.id}`}
                  >
                    <div className="flex items-center gap-2">
                      {selectedBun === bun.id && <Check className="h-4 w-4 text-primary" />}
                      <span className="text-sm font-medium">{bun.name}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}


          {/* Modifier Groups (Required selections like Dressing, Pasta Type) */}
          {productModifiers.length > 0 && (
            <div className="space-y-4">
              {productModifiers.map((group) => (
                <div key={group.id} data-testid={`modifier-group-${group.id}`}>
                  <h3 className="font-semibold mb-3">
                    {group.name || group.title}
                    {group.required && <span className="text-red-500 ml-1">*</span>}
                  </h3>
                  <div className="space-y-2">
                    {group.options.map((option) => {
                      const isSelected = selectedModifiers[group.id]?.name === option.name;
                      const priceText = option.price > 0 ? ` (+€${option.price.toFixed(2)})` : '';
                      
                      return (
                        <button
                          key={option.id || option.name}
                          onClick={() => setSelectedModifiers({
                            ...selectedModifiers, 
                            [group.id]: {
                              id: option.id || `opt-${group.id}`,
                              name: option.name,
                              price: option.price || 0,
                              pos_item_id: option.pos_item_id || `${group.id.toUpperCase()}-${option.name.toUpperCase().replace(/\s+/g, '-')}`
                            }
                          })}
                          className={`w-full p-3 rounded-lg border-2 transition-all text-left ${
                            isSelected
                              ? 'border-primary bg-primary/10'
                              : 'border-border hover:border-primary/40'
                          }`}
                          data-testid={`modifier-option-${option.id || option.name.toLowerCase().replace(/\s+/g, '-')}`}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="font-medium">{option.name}{priceText}</span>
                              {option.description && (
                                <p className="text-xs text-muted-foreground mt-1">{option.description}</p>
                              )}
                            </div>
                            {isSelected && <Check className="h-5 w-5 text-primary" />}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Extras */}
          {availableExtras.length > 0 && (
            <div>
              <h3 className="font-semibold mb-3">Extras hinzufügen</h3>
              <div className="grid grid-cols-2 gap-3">
                {availableExtras.map((extra) => {
                  const isSelected = selectedExtras.find(e => e.name === extra.name);
                  const icon = getIngredientIcon(extra.name);
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
                        <div className="flex items-center gap-2">
                          {icon.type === 'image' ? (
                            <img 
                              src={icon.icon} 
                              alt="" 
                              className="w-6 h-6 object-contain"
                            />
                          ) : (
                            <span className="text-xl">{icon.icon}</span>
                          )}
                          <div>
                            <p className="text-sm font-medium">{extra.name}</p>
                            <p className="text-xs text-muted-foreground">+€{extra.price.toFixed(2)}</p>
                          </div>
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
                  const icon = getIngredientIcon(removal);
                  return (
                    <button
                      key={removal}
                      onClick={() => toggleRemoval(removal)}
                      className={`px-3 py-1.5 rounded-full text-sm transition-all flex items-center gap-2 ${
                        isSelected
                          ? 'bg-destructive/20 text-destructive border-2 border-destructive'
                          : 'bg-secondary text-foreground border-2 border-transparent hover:border-border'
                      }`}
                      data-testid={`remove-${removal.toLowerCase().replace(/\s+/g, '-')}`}
                    >
                      {icon.type === 'image' ? (
                        <img 
                          src={icon.icon} 
                          alt="" 
                          className="w-5 h-5 object-contain"
                        />
                      ) : (
                        <span className="text-lg">{icon.icon}</span>
                      )}
                      <span>{isSelected && '− '}Ohne {removal}</span>
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
            disabled={isAddToCartDisabled}
            className={`btn-primary w-full ${isAddToCartDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
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

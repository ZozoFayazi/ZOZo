import React, { useState, useMemo } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { toast } from 'sonner';
import { ShoppingCart, Plus, Minus, Check, Sparkles } from 'lucide-react';

export default function UpsellDialog({ open, onClose, upsellData, onConfirm, productName }) {
  const [selections, setSelections] = useState({});
  const [dipQuantities, setDipQuantities] = useState({});
  
  const categories = upsellData?.categories || [];
  
  // Calculate total upsell price
  const totalUpsellPrice = useMemo(() => {
    let total = 0;
    
    Object.entries(selections).forEach(([categoryId, items]) => {
      const category = categories.find(c => c.id === categoryId);
      
      if (category?.type === 'quantity-select') {
        // Dips with quantities
        Object.entries(dipQuantities).forEach(([dipId, qty]) => {
          if (qty > 0) {
            const dip = category.items.find(i => i.id === dipId);
            if (dip) total += dip.price * qty;
          }
        });
      } else if (category?.type === 'single-select') {
        // Single item
        const item = category.items.find(i => i.id === items);
        if (item) total += item.price;
      } else if (category?.type === 'multi-select') {
        // Multiple items
        if (Array.isArray(items)) {
          items.forEach(itemId => {
            let item;
            if (category.grouped) {
              // Drinks grouped
              Object.values(category.items).forEach(group => {
                const found = group.find(i => i.id === itemId);
                if (found) item = found;
              });
            } else {
              item = category.items.find(i => i.id === itemId);
            }
            if (item) {
              total += item.price;
              if (item.pfand) total += item.pfand;
            }
          });
        }
      }
    });
    
    return total;
  }, [selections, dipQuantities, categories]);
  
  const handleSingleSelect = (categoryId, itemId) => {
    setSelections(prev => ({
      ...prev,
      [categoryId]: prev[categoryId] === itemId ? null : itemId
    }));
  };
  
  const handleMultiSelect = (categoryId, itemId) => {
    setSelections(prev => {
      const current = prev[categoryId] || [];
      if (current.includes(itemId)) {
        return { ...prev, [categoryId]: current.filter(id => id !== itemId) };
      } else {
        return { ...prev, [categoryId]: [...current, itemId] };
      }
    });
  };
  
  const handleDipQuantity = (dipId, change) => {
    setDipQuantities(prev => {
      const current = prev[dipId] || 0;
      const newQty = Math.max(0, Math.min(5, current + change));
      
      // Check total limit
      const totalDips = Object.values({...prev, [dipId]: newQty}).reduce((sum, q) => sum + q, 0);
      if (totalDips > 10 && change > 0) {
        toast.error('Maximal 10 Dips pro Bestellung');
        return prev;
      }
      
      return { ...prev, [dipId]: newQty };
    });
  };
  
  const handleConfirm = () => {
    const upsellItems = [];
    
    categories.forEach(category => {
      if (category.type === 'quantity-select') {
        // Dips
        Object.entries(dipQuantities).forEach(([dipId, qty]) => {
          if (qty > 0) {
            const dip = category.items.find(i => i.id === dipId);
            if (dip) {
              for (let i = 0; i < qty; i++) {
                upsellItems.push({
                  name: dip.name,
                  price: dip.price,
                  category: 'dip'
                });
              }
            }
          }
        });
      } else if (category.type === 'single-select') {
        const itemId = selections[category.id];
        if (itemId) {
          const item = category.items.find(i => i.id === itemId);
          if (item && item.price > 0) {
            upsellItems.push({
              name: item.name,
              price: item.price,
              category: category.id
            });
          }
        }
      } else if (category.type === 'multi-select') {
        const itemIds = selections[category.id] || [];
        itemIds.forEach(itemId => {
          let item;
          if (category.grouped) {
            Object.values(category.items).forEach(group => {
              const found = group.find(i => i.id === itemId);
              if (found) item = found;
            });
          } else {
            item = category.items.find(i => i.id === itemId);
          }
          if (item) {
            upsellItems.push({
              name: item.name,
              price: item.price + (item.pfand || 0),
              category: category.id,
              pfand: item.pfand
            });
          }
        });
      }
    });
    
    onConfirm(upsellItems);
    onClose();
  };
  
  const handleSkip = () => {
    onConfirm([]);
    onClose();
  };
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            Perfektioniere deine Bestellung!
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6 py-4">
          {categories.map(category => (
            <CategorySection
              key={category.id}
              category={category}
              selections={selections}
              dipQuantities={dipQuantities}
              onSingleSelect={handleSingleSelect}
              onMultiSelect={handleMultiSelect}
              onDipQuantity={handleDipQuantity}
            />
          ))}
        </div>
        
        <div className="flex items-center justify-between gap-4 pt-4 border-t">
          <Button variant="outline" onClick={handleSkip} data-testid="upsell-skip">
            Nein, danke
          </Button>
          <div className="flex items-center gap-3">
            {totalUpsellPrice > 0 && (
              <div className="text-sm text-muted-foreground">
                Extras: <span className="font-bold text-primary">+€{totalUpsellPrice.toFixed(2)}</span>
              </div>
            )}
            <Button onClick={handleConfirm} size="lg" data-testid="upsell-confirm">
              <ShoppingCart className="w-4 h-4 mr-2" />
              Zum Warenkorb
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function CategorySection({ category, selections, dipQuantities, onSingleSelect, onMultiSelect, onDipQuantity }) {
  if (!category.items || category.items.length === 0) return null;
  
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">{category.headline}</CardTitle>
        {category.info && <p className="text-sm text-muted-foreground mt-1">{category.info}</p>}
      </CardHeader>
      <CardContent>
        {category.type === 'quantity-select' ? (
          <DipsSection
            items={category.items}
            quantities={dipQuantities}
            onQuantityChange={onDipQuantity}
            maxPerItem={category.max_per_item}
            maxTotal={category.max_total}
          />
        ) : category.grouped ? (
          <DrinksSection
            items={category.items}
            selected={selections[category.id] || []}
            onSelect={(itemId) => onMultiSelect(category.id, itemId)}
          />
        ) : category.type === 'single-select' ? (
          <div className="grid grid-cols-1 gap-2">
            {category.items.map(item => (
              <button
                key={item.id}
                onClick={() => onSingleSelect(category.id, item.id)}
                className={`p-3 rounded-lg border-2 text-left transition-all flex items-center justify-between ${
                  selections[category.id] === item.id
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <span>{item.name}</span>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-primary">+€{item.price.toFixed(2)}</span>
                  {selections[category.id] === item.id && <Check className="w-4 h-4 text-primary" />}
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {category.items.map(item => (
              <button
                key={item.id}
                onClick={() => onMultiSelect(category.id, item.id)}
                className={`p-3 rounded-lg border-2 text-left transition-all flex items-center justify-between ${
                  (selections[category.id] || []).includes(item.id)
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <span className="text-sm">{item.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-primary">+€{item.price.toFixed(2)}</span>
                  {(selections[category.id] || []).includes(item.id) && <Check className="w-4 h-4 text-primary" />}
                </div>
              </button>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function DipsSection({ items, quantities, onQuantityChange, maxPerItem, maxTotal }) {
  const totalDips = Object.values(quantities).reduce((sum, q) => sum + q, 0);
  
  return (
    <div className="space-y-2">
      {totalDips > 0 && (
        <div className="text-xs text-muted-foreground mb-3">
          {totalDips}/{maxTotal} Dips gewählt · Max {maxPerItem} pro Sorte
        </div>
      )}
      
      {items.map(dip => {
        const qty = quantities[dip.id] || 0;
        
        return (
          <div
            key={dip.id}
            className={`p-3 rounded-lg border-2 transition-all ${
              qty > 0 ? 'border-primary bg-primary/5' : 'border-border'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="font-medium text-sm">{dip.name}</div>
                <div className="text-xs text-primary font-bold">€{dip.price.toFixed(2)}</div>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onQuantityChange(dip.id, -1)}
                  disabled={qty === 0}
                  className="h-8 w-8 p-0"
                >
                  <Minus className="w-3 h-3" />
                </Button>
                <span className="w-8 text-center font-bold">{qty}</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onQuantityChange(dip.id, 1)}
                  disabled={qty >= maxPerItem || totalDips >= maxTotal}
                  className="h-8 w-8 p-0"
                >
                  <Plus className="w-3 h-3" />
                </Button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function DrinksSection({ items, selected, onSelect }) {
  return (
    <div className="space-y-4">
      {Object.entries(items).map(([size, drinks]) => (
        <div key={size}>
          <h4 className="text-sm font-semibold mb-2 text-muted-foreground">
            {size} {drinks[0]?.pfand && `(+€${drinks[0].pfand.toFixed(2)} Pfand)`}
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {drinks.map(drink => (
              <button
                key={drink.id}
                onClick={() => onSelect(drink.id)}
                className={`p-3 rounded-lg border-2 text-left transition-all flex items-center justify-between ${
                  selected.includes(drink.id)
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <span className="text-sm">{drink.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-primary">€{drink.price.toFixed(2)}</span>
                  {selected.includes(drink.id) && <Check className="w-4 h-4 text-primary" />}
                </div>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

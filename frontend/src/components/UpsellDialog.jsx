import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Plus, X } from 'lucide-react';

function UpsellDialog({ open, onClose, upsellItems, onAddToCart, onSkip }) {
  const [selectedItems, setSelectedItems] = useState([]);

  const handleToggleItem = (item) => {
    if (selectedItems.find(i => i.id === item.id)) {
      setSelectedItems(selectedItems.filter(i => i.id !== item.id));
    } else {
      setSelectedItems([...selectedItems, { ...item, quantity: 1 }]);
    }
  };

  const handleAddSelected = () => {
    selectedItems.forEach(item => onAddToCart(item));
    onClose();
  };

  const handleSkip = () => {
    onSkip();
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl" data-testid="upsell-dialog">
        <DialogHeader>
          <DialogTitle>Möchtest du noch etwas dazu? 🍟🥤</DialogTitle>
        </DialogHeader>

        <div className="space-y-6 max-h-[60vh] overflow-y-auto py-4">
          {Object.entries(upsellItems).map(([category, items]) => (
            <div key={category} className="space-y-3">
              <h3 className="font-semibold text-lg">{category}</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {items.map(item => {
                  const isSelected = selectedItems.find(i => i.id === item.id);
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleToggleItem(item)}
                      className={`p-3 rounded-lg border-2 transition-all text-left ${
                        isSelected 
                          ? 'border-primary bg-primary/10' 
                          : 'border-border hover:border-primary/50'
                      }`}
                      data-testid={`upsell-item-${item.id}`}
                    >
                      {item.image_url && (
                        <img 
                          src={item.image_url} 
                          alt={item.name}
                          className="w-full h-20 object-cover rounded mb-2"
                        />
                      )}
                      <p className="font-medium text-sm">{item.name}</p>
                      <p className="text-primary font-semibold text-sm">
                        €{item.price.toFixed(2)}
                      </p>
                      {isSelected && (
                        <div className="mt-1 flex items-center gap-1 text-primary text-xs">
                          <Plus className="h-3 w-3" />
                          Ausgewählt
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={handleSkip} data-testid="upsell-skip">
            Nein, danke
          </Button>
          {selectedItems.length > 0 && (
            <Button onClick={handleAddSelected} data-testid="upsell-add-selected">
              {selectedItems.length} {selectedItems.length === 1 ? 'Artikel' : 'Artikel'} hinzufügen
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default UpsellDialog;

import React, { useState } from 'react';
import { X, ShoppingBag, Truck } from 'lucide-react';
import { toast } from 'sonner';

function OrderTypeSelection({ locations, onComplete, onClose }) {
  const [step, setStep] = useState(1); // 1 = order type, 2 = location
  const [orderType, setOrderType] = useState(''); // 'pickup' or 'delivery'
  const [selectedLocation, setSelectedLocation] = useState('');

  const handleOrderTypeSelect = (type) => {
    setOrderType(type);
    setStep(2);
  };

  const handleContinue = () => {
    if (!selectedLocation) {
      toast.error('Bitte wähle eine Filiale');
      return;
    }

    const location = locations.find(loc => loc.id === selectedLocation);
    if (!location) {
      toast.error('Filiale nicht gefunden');
      return;
    }

    // Pass selected data to parent
    onComplete({
      orderType,
      location
    });
  };

  const handleBack = () => {
    setStep(1);
    setOrderType('');
    setSelectedLocation('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
        data-testid="order-type-backdrop"
      />
      
      {/* Dialog */}
      <div className="relative bg-card border border-border rounded-2xl max-w-lg w-full shadow-2xl">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-secondary rounded-lg transition-colors z-10"
          data-testid="close-order-type-dialog"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Content */}
        <div className="p-8">
          {step === 1 ? (
            // Step 1: Order Type Selection
            <>
              <div className="text-center mb-8">
                <h2 className="text-2xl font-serif font-bold mb-2">🍔 Wie möchtest du bestellen?</h2>
                <p className="text-muted-foreground">Wähle deine bevorzugte Option</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Pickup Option */}
                <button
                  onClick={() => handleOrderTypeSelect('pickup')}
                  className="p-6 rounded-xl border-2 border-border hover:border-primary bg-card hover:bg-primary/5 transition-all group"
                  data-testid="order-type-pickup"
                >
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                      <ShoppingBag className="h-8 w-8 text-primary" />
                    </div>
                    <h3 className="font-semibold text-lg">Abholen</h3>
                    <p className="text-sm text-muted-foreground text-center">
                      Bestelle und hole dein Essen ab
                    </p>
                  </div>
                </button>

                {/* Delivery Option */}
                <button
                  onClick={() => handleOrderTypeSelect('delivery')}
                  className="p-6 rounded-xl border-2 border-border hover:border-primary bg-card hover:bg-primary/5 transition-all group"
                  data-testid="order-type-delivery"
                >
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                      <Truck className="h-8 w-8 text-primary" />
                    </div>
                    <h3 className="font-semibold text-lg">Liefern</h3>
                    <p className="text-sm text-muted-foreground text-center">
                      Lass dir dein Essen liefern
                    </p>
                  </div>
                </button>
              </div>
            </>
          ) : (
            // Step 2: Location Selection
            <>
              <div className="mb-6">
                <button
                  onClick={handleBack}
                  className="text-sm text-muted-foreground hover:text-foreground mb-4"
                >
                  ← Zurück
                </button>
                <h2 className="text-2xl font-serif font-bold mb-2">
                  📍 Wähle deine Filiale
                </h2>
                <p className="text-sm text-muted-foreground">
                  {orderType === 'pickup' ? 'Wo möchtest du abholen?' : 'Von welcher Filiale liefern lassen?'}
                </p>
              </div>

              {/* Location Dropdown */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">
                  Filiale auswählen:
                </label>
                <select
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  className="w-full px-4 py-3 bg-background border-2 border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-base"
                  data-testid="location-select-dropdown"
                >
                  <option value="">Bitte auswählen...</option>
                  {locations.map((location) => (
                    <option key={location.id} value={location.id}>
                      {location.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Selected Location Info */}
              {selectedLocation && (
                <div className="p-4 bg-accent rounded-lg border border-border mb-6">
                  {(() => {
                    const location = locations.find(loc => loc.id === selectedLocation);
                    return location ? (
                      <div>
                        <p className="font-semibold mb-1">{location.name}</p>
                        <p className="text-sm text-muted-foreground">{location.address}</p>
                        {location.phone && (
                          <p className="text-sm text-muted-foreground">Tel: {location.phone}</p>
                        )}
                      </div>
                    ) : null;
                  })()}
                </div>
              )}

              {/* Continue Button */}
              <button
                onClick={handleContinue}
                disabled={!selectedLocation}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="continue-to-menu-button"
              >
                Weiter zur Speisekarte
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default OrderTypeSelection;

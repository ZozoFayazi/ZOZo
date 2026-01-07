import React, { useState, useCallback } from 'react';
import { X, Plus, Minus, Trash2, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';
import { createOrder } from '../api';
import CheckoutDialog from './CheckoutDialog';
import DailyDealDiscount from './DailyDealDiscount';

function CartDrawer({ open, onClose, cart, cartTotal, removeFromCart, updateCartItemQuantity, clearCart, selectedLocation }) {
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [dailyDealDiscount, setDailyDealDiscount] = useState(0);
  const [discountInfo, setDiscountInfo] = useState(null);

  const handleDiscountCalculated = useCallback((amount, info) => {
    setDailyDealDiscount(amount || 0);
    setDiscountInfo(info);
  }, []);

  const deliveryFee = cartTotal < 15 ? 2.50 : 0;
  const discountedSubtotal = Math.max(0, cartTotal - dailyDealDiscount);
  const total = discountedSubtotal + deliveryFee;

  const handleCheckout = () => {
    if (!selectedLocation) {
      toast.error('Bitte wähle zuerst einen Standort');
      return;
    }
    if (cart.length === 0) {
      toast.error('Dein Warenkorb ist leer');
      return;
    }
    setCheckoutOpen(true);
  };

  if (!open) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 animate-fade-in"
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        className="fixed right-0 top-0 h-full w-full max-w-md bg-card border-l border-border z-50 animate-slide-in"
        data-testid="cart-sheet"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center space-x-3">
            <ShoppingBag className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Warenkorb</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-secondary rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4" style={{ maxHeight: 'calc(100vh - 280px)' }}>
          {cart.length === 0 ? (
            <div className="text-center py-12">
              <ShoppingBag className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground">Dein Warenkorb ist leer</p>
            </div>
          ) : (
            cart.map((item, index) => (
              <div
                key={`${item.menu_item_id}-${item.size}-${index}`}
                className="flex items-start space-x-4 p-4 bg-background rounded-lg border border-border"
              >
                <div className="flex-1">
                  <h3 className="font-medium mb-1">{item.name}</h3>
                  {item.size && (
                    <p className="text-xs text-muted-foreground mb-2">{item.size}</p>
                  )}
                  <p className="text-sm font-semibold text-primary">
                    €{(item.price * item.quantity).toFixed(2)}
                  </p>
                </div>

                {/* Quantity Controls */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => updateCartItemQuantity(item.menu_item_id, item.size, item.quantity - 1)}
                    className="p-1 hover:bg-secondary rounded transition-colors"
                  >
                    <Minus className="h-4 w-4" />
                  </button>
                  <span className="w-8 text-center font-medium">{item.quantity}</span>
                  <button
                    onClick={() => updateCartItemQuantity(item.menu_item_id, item.size, item.quantity + 1)}
                    className="p-1 hover:bg-secondary rounded transition-colors"
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                </div>

                {/* Remove Button */}
                <button
                  onClick={() => removeFromCart(item.menu_item_id, item.size)}
                  className="p-2 hover:bg-destructive/10 hover:text-destructive rounded transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-border p-6 space-y-4">
          {/* Summary */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Zwischensumme</span>
              <span>€{cartTotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Liefergebühr</span>
              <span>{deliveryFee === 0 ? 'Kostenlos' : `€${deliveryFee.toFixed(2)}`}</span>
            </div>
            {cartTotal < 15 && cartTotal > 0 && (
              <p className="text-xs text-warning">Noch €{(15 - cartTotal).toFixed(2)} für kostenlose Lieferung</p>
            )}
            <div className="flex justify-between text-lg font-semibold pt-2 border-t border-border">
              <span>Gesamt</span>
              <span className="text-primary">€{total.toFixed(2)}</span>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-2">
            <button
              onClick={handleCheckout}
              disabled={cart.length === 0}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="checkout-button"
            >
              Zur Kasse
            </button>
            {cart.length > 0 && (
              <button
                onClick={clearCart}
                className="w-full text-sm text-destructive hover:underline"
              >
                Warenkorb leeren
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Checkout Dialog */}
      <CheckoutDialog
        open={checkoutOpen}
        onClose={() => setCheckoutOpen(false)}
        cart={cart}
        cartTotal={cartTotal}
        deliveryFee={deliveryFee}
        total={total}
        selectedLocation={selectedLocation}
        clearCart={clearCart}
        onCloseCart={onClose}
      />
    </>
  );
}

export default CartDrawer;

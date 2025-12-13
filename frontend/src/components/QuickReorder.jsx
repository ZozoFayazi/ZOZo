import React, { useState, useEffect } from 'react';
import { RotateCcw, Clock, X } from 'lucide-react';
import { toast } from 'sonner';

function QuickReorder({ addToCart }) {
  const [orderHistory, setOrderHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadOrderHistory();
  }, []);

  const loadOrderHistory = async () => {
    // Get email from localStorage (if customer has ordered before)
    const lastCustomerEmail = localStorage.getItem('lastCustomerEmail');
    if (!lastCustomerEmail) return;

    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/order-history/${lastCustomerEmail}?limit=3`
      );
      
      if (response.ok) {
        const data = await response.json();
        setOrderHistory(data);
      }
    } catch (error) {
      console.error('Error loading order history:', error);
    } finally {
      setLoading(false);
    }
  };

  const reorderItems = (order) => {
    let itemsAdded = 0;
    
    order.items.forEach(item => {
      // Add each item to cart
      for (let i = 0; i < item.quantity; i++) {
        addToCart({
          id: item.menu_item_id,
          name: item.name,
          price: item.price,
          size: item.size,
          customizations: item.customizations || {}
        });
        itemsAdded++;
      }
    });

    toast.success(`${itemsAdded} Artikel wieder hinzugefügt!`);
    setShowHistory(false);
  };

  if (orderHistory.length === 0) return null;

  return (
    <div className="mb-6">
      {/* Collapsed Button */}
      {!showHistory && (
        <button
          onClick={() => setShowHistory(true)}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-accent border-2 border-primary/20 hover:border-primary/40 rounded-lg transition-all"
          data-testid="quick-reorder-toggle"
        >
          <RotateCcw className="h-5 w-5 text-primary" />
          <span className="font-medium">Letzte Bestellung wiederholen</span>
        </button>
      )}

      {/* Expanded History */}
      {showHistory && (
        <div className="bg-accent border-2 border-primary/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              Deine letzten Bestellungen
            </h3>
            <button
              onClick={() => setShowHistory(false)}
              className="p-1 hover:bg-secondary rounded-lg transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="space-y-3">
            {orderHistory.map((order) => (
              <div
                key={order.id}
                className="bg-background border border-border rounded-lg p-3 hover:border-primary/40 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="text-sm font-medium">
                      {new Date(order.created_at).toLocaleDateString('de-DE', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {order.items.length} Artikel • €{order.total.toFixed(2)}
                    </p>
                  </div>
                  <button
                    onClick={() => reorderItems(order)}
                    className="btn-primary text-sm px-3 py-1 flex items-center gap-1"
                    data-testid={`reorder-${order.id}`}
                  >
                    <RotateCcw className="h-4 w-4" />
                    Wiederholen
                  </button>
                </div>

                {/* Order Items Preview */}
                <div className="flex flex-wrap gap-1 mt-2">
                  {order.items.slice(0, 3).map((item, idx) => (
                    <span
                      key={idx}
                      className="text-xs bg-secondary px-2 py-1 rounded-full"
                    >
                      {item.quantity}x {item.name}
                    </span>
                  ))}
                  {order.items.length > 3 && (
                    <span className="text-xs text-muted-foreground px-2 py-1">
                      +{order.items.length - 3} mehr
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default QuickReorder;

import React, { useState, useEffect } from 'react';
import { RotateCcw, X } from 'lucide-react';
import { getOrderHistory } from '../api';
import { toast } from 'sonner';

function QuickReorder({ onReorder }) {
  const [open, setOpen] = useState(false);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [customerInfo, setCustomerInfo] = useState({ email: '', phone: '' });

  const loadOrderHistory = async () => {
    const savedEmail = localStorage.getItem('zozoCustomerEmail');
    const savedPhone = localStorage.getItem('zozoCustomerPhone');
    
    if (!savedEmail && !savedPhone) {
      toast.error('Keine gespeicherten Bestellungen gefunden');
      return;
    }

    setLoading(true);
    try {
      const history = await getOrderHistory(savedEmail, savedPhone);
      setOrders(history);
      if (history.length === 0) {
        toast.info('Noch keine abgeschlossenen Bestellungen');
      }
    } catch (error) {
      console.error('Error loading history:', error);
      toast.error('Fehler beim Laden der Bestellhistorie');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickReorder = (order) => {
    // Add all items from the order to cart
    order.items.forEach(item => {
      onReorder({
        menu_item_id: item.menu_item_id,
        name: item.name,
        price: item.price,
        size: item.size,
        quantity: item.quantity
      });
    });
    
    toast.success(`${order.items.length} Artikel zum Warenkorb hinzugefügt`);
    setOpen(false);
  };

  const handleOpen = () => {
    setOpen(true);
    loadOrderHistory();
  };

  if (!open) {
    return (
      <button
        onClick={handleOpen}
        className="flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-secondary rounded-lg transition-colors"
        title="Letzte Bestellung wiederholen"
      >
        <RotateCcw className="h-4 w-4" />
        <span className="hidden sm:inline">Wiederholen</span>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm animate-fade-in"
        onClick={() => setOpen(false)}
      />

      {/* Dialog */}
      <div className="relative bg-card border border-border rounded-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto animate-scale-in">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border sticky top-0 bg-card z-10">
          <div>
            <h2 className="text-lg font-semibold">Bestellung wiederholen</h2>
            <p className="text-sm text-muted-foreground">Wähle eine vorherige Bestellung</p>
          </div>
          <button
            onClick={() => setOpen(false)}
            className="p-2 hover:bg-secondary rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Lade Bestellhistorie...</p>
            </div>
          ) : orders.length === 0 ? (
            <div className="text-center py-12">
              <RotateCcw className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground">Noch keine abgeschlossenen Bestellungen</p>
            </div>
          ) : (
            <div className="space-y-4">
              {orders.map((order) => (
                <div
                  key={order.id}
                  className="bg-background border border-border rounded-xl p-6 space-y-4 hover:border-primary/40 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold">{order.order_number}</p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(order.created_at).toLocaleDateString('de-DE', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary">€{order.total.toFixed(2)}</p>
                      <p className="text-xs text-muted-foreground">{order.items.length} Artikel</p>
                    </div>
                  </div>

                  {/* Items Preview */}
                  <div className="space-y-2">
                    {order.items.slice(0, 3).map((item, idx) => (
                      <div key={idx} className="flex justify-between text-sm">
                        <span className="text-muted-foreground">
                          {item.quantity}x {item.name}
                          {item.size && ` (${item.size})`}
                        </span>
                        <span className="text-foreground">€{(item.price * item.quantity).toFixed(2)}</span>
                      </div>
                    ))}
                    {order.items.length > 3 && (
                      <p className="text-xs text-muted-foreground">
                        + {order.items.length - 3} weitere Artikel
                      </p>
                    )}
                  </div>

                  <button
                    onClick={() => handleQuickReorder(order)}
                    className="btn-primary w-full"
                  >
                    <RotateCcw className="inline h-4 w-4 mr-2" />
                    Diese Bestellung wiederholen
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default QuickReorder;

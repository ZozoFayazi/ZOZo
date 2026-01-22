import React, { useState, useEffect } from 'react';
import { Package, Clock, CheckCircle, Truck, MapPin, X, RefreshCw, Settings } from 'lucide-react';
import { toast } from 'sonner';
import OrderActionsDialog from '../components/OrderActionsDialog';

function OrderManagement() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, confirmed, preparing, ready, on_the_way, completed
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showActionsDialog, setShowActionsDialog] = useState(false);
  const [actionsOrder, setActionsOrder] = useState(null);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/orders`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (!response.ok) throw new Error('Failed to fetch orders');

      const data = await response.json();
      setOrders(data);
    } catch (error) {
      console.error('Error loading orders:', error);
      toast.error('Fehler beim Laden der Bestellungen');
    } finally {
      setLoading(false);
    }
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/orders/${orderId}/status`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ status: newStatus })
        }
      );

      if (!response.ok) throw new Error('Failed to update status');

      toast.success('Status aktualisiert');
      loadOrders();
      setSelectedOrder(null);
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error('Fehler beim Aktualisieren');
    }
  };

  const getStatusInfo = (status) => {
    const statusMap = {
      confirmed: { label: 'Bestätigt', icon: CheckCircle, color: 'bg-blue-500/10 text-blue-500' },
      preparing: { label: 'In Vorbereitung', icon: Package, color: 'bg-orange-500/10 text-orange-500' },
      ready: { label: 'Bereit', icon: MapPin, color: 'bg-green-500/10 text-green-500' },
      on_the_way: { label: 'Unterwegs', icon: Truck, color: 'bg-purple-500/10 text-purple-500' },
      completed: { label: 'Abgeschlossen', icon: CheckCircle, color: 'bg-green-600/10 text-green-600' },
      cancelled: { label: 'Storniert', icon: X, color: 'bg-red-500/10 text-red-500' }
    };
    return statusMap[status] || { label: status, icon: Package, color: 'bg-gray-500/10 text-gray-500' };
  };

  const filteredOrders = filter === 'all' ? orders : orders.filter(order => order.status === filter);

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container-custom">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-serif font-bold">Bestellverwaltung</h1>
            <p className="text-sm text-muted-foreground">
              {filteredOrders.length} {filteredOrders.length === 1 ? 'Bestellung' : 'Bestellungen'}
            </p>
          </div>
          <button
            onClick={loadOrders}
            className="btn-secondary flex items-center gap-2"
            data-testid="refresh-orders-button"
          >
            <RefreshCw className="h-4 w-4" />
            Aktualisieren
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {[
            { value: 'all', label: 'Alle' },
            { value: 'confirmed', label: 'Bestätigt' },
            { value: 'preparing', label: 'In Vorbereitung' },
            { value: 'ready', label: 'Bereit' },
            { value: 'on_the_way', label: 'Unterwegs' },
            { value: 'completed', label: 'Abgeschlossen' }
          ].map((item) => (
            <button
              key={item.value}
              onClick={() => setFilter(item.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                filter === item.value
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-foreground hover:bg-secondary/80'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* Orders List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-4 text-muted-foreground">Lade Bestellungen...</p>
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="bg-accent rounded-lg p-12 text-center">
            <Package className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">Keine Bestellungen gefunden</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredOrders.map((order) => {
              const statusInfo = getStatusInfo(order.status);
              return (
                <div
                  key={order.id}
                  className="bg-card border border-border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => setSelectedOrder(order)}
                  data-testid={`order-card-${order.order_number}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold">{order.order_number}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {order.is_pickup ? '📦 Abholung' : '🚚 Lieferung'}
                        </span>
                        {/* POS Status Badge */}
                        {order.pos_status && (order.pos_status === 'error' || order.pos_status === 'failed') && (
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-500 border border-red-500/20">
                            ⚠️ POS-Fehler
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-1">{order.customer.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(order.created_at).toLocaleString('de-DE')}
                      </p>
                    </div>
                    <div className="text-right flex flex-col gap-2">
                      <p className="text-lg font-bold text-primary">€{order.total.toFixed(2)}</p>
                      <p className="text-xs text-muted-foreground">{order.items.length} Artikel</p>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setActionsOrder(order);
                          setShowActionsDialog(true);
                        }}
                        className="btn-secondary text-xs py-1 px-3 flex items-center gap-1"
                        title="Order Management"
                      >
                        <Settings className="h-3 w-3" />
                        Aktionen
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Order Detail Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-card border border-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold mb-1">{selectedOrder.order_number}</h2>
                  <p className="text-sm text-muted-foreground">
                    {new Date(selectedOrder.created_at).toLocaleString('de-DE')}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="p-2 hover:bg-secondary rounded-lg transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Customer Info */}
              <div className="bg-accent rounded-lg p-4 mb-4">
                <h3 className="font-semibold mb-2">Kunde</h3>
                <p className="text-sm">{selectedOrder.customer.name}</p>
                <p className="text-sm text-muted-foreground">{selectedOrder.customer.phone}</p>
                {selectedOrder.customer.email && (
                  <p className="text-sm text-muted-foreground">{selectedOrder.customer.email}</p>
                )}
                {!selectedOrder.is_pickup && (
                  <p className="text-sm text-muted-foreground mt-2">
                    {selectedOrder.customer.address}, {selectedOrder.customer.postal_code}{' '}
                    {selectedOrder.customer.city}
                  </p>
                )}
              </div>

              {/* Items */}
              <div className="mb-4">
                <h3 className="font-semibold mb-2">Bestellte Artikel</h3>
                <div className="space-y-1">
                  {selectedOrder.items.map((item, index) => (
                    <div key={index} className="border-l-2 border-primary/50 pl-3 py-2">
                      {/* Main Item */}
                      <div className="flex justify-between text-sm font-medium">
                        <span>
                          {item.quantity}x {item.name}
                          {item.size && ` (${item.size})`}
                        </span>
                        <span>€{(item.price * item.quantity).toFixed(2)}</span>
                      </div>
                      
                      {/* Modifiers */}
                      {item.modifiers && Object.keys(item.modifiers).length > 0 && (
                        <div className="ml-4 mt-1 space-y-0.5">
                          {Object.values(item.modifiers).map((mod, idx) => (
                            <div key={idx} className="text-xs text-muted-foreground">
                              → {mod.name} {mod.price > 0 && `(+€${mod.price.toFixed(2)})`}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Customizations */}
                      {item.customizations && item.customizations.length > 0 && (
                        <div className="ml-4 mt-1 space-y-0.5">
                          {item.customizations.map((custom, idx) => (
                            <div key={idx} className="text-xs text-muted-foreground">
                              → {custom}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Extras */}
                      {item.extras && item.extras.length > 0 && (
                        <div className="ml-4 mt-1 space-y-0.5">
                          {item.extras.map((extra, idx) => (
                            <div key={idx} className="text-xs text-muted-foreground">
                              + {extra.name || extra} {extra.price > 0 && `(€${extra.price.toFixed(2)})`}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Removed Ingredients */}
                      {item.removed_ingredients && item.removed_ingredients.length > 0 && (
                        <div className="ml-4 mt-1 space-y-0.5">
                          {item.removed_ingredients.map((removal, idx) => (
                            <div key={idx} className="text-xs text-muted-foreground italic">
                              - Ohne {removal}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                
                {/* Pricing Breakdown */}
                <div className="border-t border-border mt-4 pt-3 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Zwischensumme</span>
                    <span>€{selectedOrder.subtotal.toFixed(2)}</span>
                  </div>
                  {selectedOrder.delivery_fee > 0 && (
                    <div className="flex justify-between text-sm">
                      <span>Liefergebühr</span>
                      <span>€{selectedOrder.delivery_fee.toFixed(2)}</span>
                    </div>
                  )}
                  {selectedOrder.pickup_discount > 0 && (
                    <div className="flex justify-between text-sm text-green-600">
                      <span>Abholrabatt (10%)</span>
                      <span>-€{selectedOrder.pickup_discount.toFixed(2)}</span>
                    </div>
                  )}
                  {selectedOrder.daily_deal_discount > 0 && (
                    <div className="flex justify-between text-sm text-green-600">
                      <span>Tagesangebot</span>
                      <span>-€{selectedOrder.daily_deal_discount.toFixed(2)}</span>
                    </div>
                  )}
                  {selectedOrder.discount > 0 && (
                    <div className="flex justify-between text-sm text-green-600">
                      <span>Treuepunkte ({selectedOrder.points_redeemed || 0} Pkt)</span>
                      <span>-€{selectedOrder.discount.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between font-bold text-lg border-t border-border pt-2">
                    <span>Gesamt</span>
                    <span className="text-primary">€{selectedOrder.total.toFixed(2)}</span>
                  </div>
                </div>
              </div>
              
              {/* Payment & POS Status */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                {/* Payment Info */}
                <div className="bg-accent rounded-lg p-4">
                  <h3 className="font-semibold mb-2 text-sm">💳 Zahlung</h3>
                  <p className="text-sm capitalize">{selectedOrder.payment_method || 'cash'}</p>
                  {selectedOrder.paypal_transaction_id && (
                    <p className="text-xs text-muted-foreground mt-1">
                      ID: {selectedOrder.paypal_transaction_id.substring(0, 20)}...
                    </p>
                  )}
                  {selectedOrder.payment_status && (
                    <span className={`inline-block mt-2 px-2 py-1 rounded text-xs ${
                      selectedOrder.payment_status === 'paid' ? 'bg-green-500/10 text-green-600' : 'bg-yellow-500/10 text-yellow-600'
                    }`}>
                      {selectedOrder.payment_status === 'paid' ? 'Bezahlt' : 'Offen'}
                    </span>
                  )}
                </div>
                
                {/* POS Status */}
                <div className="bg-accent rounded-lg p-4">
                  <h3 className="font-semibold mb-2 text-sm">🖥️ POS Status</h3>
                  <p className="text-sm capitalize">
                    {selectedOrder.pos_status || 'pending'}
                  </p>
                  {selectedOrder.pos_error && (
                    <p className="text-xs text-red-600 mt-1">
                      Error: {selectedOrder.pos_error.substring(0, 50)}...
                    </p>
                  )}
                  {selectedOrder.pos_pushed_at && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Gesendet: {new Date(selectedOrder.pos_pushed_at).toLocaleTimeString('de-DE')}
                    </p>
                  )}
                </div>
              </div>

              {/* Status Actions */}
              <div>
                <h3 className="font-semibold mb-3">Status ändern</h3>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'confirmed', label: 'Bestätigt', icon: CheckCircle },
                    { value: 'preparing', label: 'In Vorbereitung', icon: Package },
                    {
                      value: selectedOrder.is_pickup ? 'ready' : 'on_the_way',
                      label: selectedOrder.is_pickup ? 'Bereit' : 'Unterwegs',
                      icon: selectedOrder.is_pickup ? MapPin : Truck
                    },
                    { value: 'completed', label: 'Abgeschlossen', icon: CheckCircle }
                  ].map((status) => (
                    <button
                      key={status.value}
                      onClick={() => updateOrderStatus(selectedOrder.id, status.value)}
                      disabled={selectedOrder.status === status.value}
                      className={`p-3 rounded-lg border-2 transition-all text-left flex items-center gap-2 ${
                        selectedOrder.status === status.value
                          ? 'border-primary bg-primary/10 cursor-not-allowed'
                          : 'border-border hover:border-primary hover:bg-accent'
                      }`}
                    >
                      <status.icon className="h-5 w-5" />
                      <span className="text-sm font-medium">{status.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Order Actions Dialog */}
      <OrderActionsDialog
        order={actionsOrder}
        isOpen={showActionsDialog}
        onClose={() => {
          setShowActionsDialog(false);
          setActionsOrder(null);
        }}
        onSuccess={() => {
          loadOrders();
        }}
      />
    </div>
  );
}

export default OrderManagement;

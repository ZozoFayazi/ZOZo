import React, { useState } from 'react';
import { Search, Package, Clock, CheckCircle, Truck, MapPin } from 'lucide-react';
import { toast } from 'sonner';

function OrderTracking() {
  const [orderNumber, setOrderNumber] = useState('');
  const [orderStatus, setOrderStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!orderNumber.trim()) {
      toast.error('Bitte gib eine Bestellnummer ein');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/order-status/${orderNumber.trim()}`
      );

      if (!response.ok) {
        if (response.status === 404) {
          toast.error('Bestellung nicht gefunden');
        } else {
          toast.error('Fehler beim Abrufen des Status');
        }
        setOrderStatus(null);
        return;
      }

      const data = await response.json();
      setOrderStatus(data);
      toast.success('Bestellung gefunden!');
    } catch (error) {
      console.error('Error fetching order status:', error);
      toast.error('Verbindungsfehler');
      setOrderStatus(null);
    } finally {
      setLoading(false);
    }
  };

  const getStatusInfo = (status) => {
    const statusMap = {
      confirmed: { label: 'Bestätigt', icon: CheckCircle, color: 'text-blue-500', step: 1 },
      preparing: { label: 'In Vorbereitung', icon: Package, color: 'text-orange-500', step: 2 },
      ready: { label: 'Bereit zur Abholung', icon: MapPin, color: 'text-green-500', step: 3 },
      on_the_way: { label: 'Unterwegs', icon: Truck, color: 'text-purple-500', step: 3 },
      completed: { label: 'Abgeschlossen', icon: CheckCircle, color: 'text-green-600', step: 4 },
      cancelled: { label: 'Storniert', icon: CheckCircle, color: 'text-red-500', step: 0 }
    };
    return statusMap[status] || { label: status, icon: Package, color: 'text-gray-500', step: 0 };
  };

  const renderProgressBar = () => {
    if (!orderStatus) return null;

    const currentStatus = getStatusInfo(orderStatus.status);
    const isPickup = orderStatus.is_pickup;

    const steps = [
      { label: 'Bestätigt', step: 1 },
      { label: 'In Vorbereitung', step: 2 },
      { label: isPickup ? 'Bereit' : 'Unterwegs', step: 3 },
      { label: isPickup ? 'Abgeholt' : 'Geliefert', step: 4 }
    ];

    return (
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <React.Fragment key={step.step}>
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all ${
                    currentStatus.step >= step.step
                      ? 'bg-primary border-primary text-primary-foreground'
                      : 'bg-background border-border text-muted-foreground'
                  }`}
                >
                  {currentStatus.step >= step.step ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : (
                    <span className="text-sm font-medium">{step.step}</span>
                  )}
                </div>
                <p
                  className={`text-xs mt-2 text-center ${
                    currentStatus.step >= step.step ? 'text-foreground font-medium' : 'text-muted-foreground'
                  }`}
                >
                  {step.label}
                </p>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-2 transition-all ${
                    currentStatus.step > step.step ? 'bg-primary' : 'bg-border'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container-custom max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-serif font-bold mb-2">Bestellstatus verfolgen</h1>
          <p className="text-muted-foreground">
            Gib deine Bestellnummer ein, um den aktuellen Status zu sehen
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <input
                type="text"
                value={orderNumber}
                onChange={(e) => setOrderNumber(e.target.value)}
                placeholder="z.B. ZOZO-1001"
                className="w-full pl-10 pr-4 py-3 bg-background border-2 border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                data-testid="order-number-input"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary px-6 disabled:opacity-50"
              data-testid="search-order-button"
            >
              {loading ? 'Suche...' : 'Suchen'}
            </button>
          </div>
        </form>

        {/* Order Status Display */}
        {orderStatus && (
          <div className="space-y-6">
            {/* Order Info Card */}
            <div className="bg-card border border-border rounded-xl p-6" data-testid="order-status-card">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold mb-1">
                    Bestellung {orderStatus.order_number}
                  </h2>
                  <p className="text-sm text-muted-foreground">{orderStatus.location_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-primary">€{orderStatus.total.toFixed(2)}</p>
                  <p className="text-xs text-muted-foreground">
                    {orderStatus.is_pickup ? 'Abholung' : 'Lieferung'}
                  </p>
                </div>
              </div>

              {/* Progress Bar */}
              {renderProgressBar()}

              {/* Current Status */}
              <div className="bg-accent rounded-lg p-4 mb-4">
                <div className="flex items-center gap-3">
                  {React.createElement(getStatusInfo(orderStatus.status).icon, {
                    className: `h-6 w-6 ${getStatusInfo(orderStatus.status).color}`
                  })}
                  <div className="flex-1">
                    <p className="font-semibold">{getStatusInfo(orderStatus.status).label}</p>
                    <p className="text-sm text-muted-foreground">
                      Bestellt am {new Date(orderStatus.created_at).toLocaleString('de-DE')}
                    </p>
                  </div>
                  {orderStatus.estimated_time && orderStatus.status !== 'completed' && (
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      <span className="text-sm">~{orderStatus.estimated_time} Min.</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Status History */}
              {orderStatus.status_history && orderStatus.status_history.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold mb-3 text-muted-foreground">Verlauf</h3>
                  <div className="space-y-2">
                    {orderStatus.status_history
                      .slice()
                      .reverse()
                      .map((entry, index) => (
                        <div
                          key={index}
                          className="flex items-start gap-3 text-sm pb-2 border-b border-border last:border-0"
                        >
                          <div className="w-2 h-2 rounded-full bg-primary mt-1.5" />
                          <div className="flex-1">
                            <p className="font-medium">{getStatusInfo(entry.status).label}</p>
                            <p className="text-xs text-muted-foreground">
                              {new Date(entry.timestamp).toLocaleString('de-DE')}
                            </p>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Help Text */}
        {!orderStatus && (
          <div className="bg-accent rounded-lg p-6 text-center">
            <Package className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground mb-2">
              Deine Bestellnummer findest du in der Bestätigungs-E-Mail
            </p>
            <p className="text-sm text-muted-foreground">
              Format: ZOZO-XXXX
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default OrderTracking;

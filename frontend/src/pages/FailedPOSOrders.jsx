import React, { useState, useEffect } from 'react';
import { AlertTriangle, RefreshCw, Clock, MapPin, XCircle, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

function FailedPOSOrders() {
  const [failedOrders, setFailedOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [retrying, setRetrying] = useState(null);

  useEffect(() => {
    loadFailedOrders();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadFailedOrders, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadFailedOrders = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/pos/failed-orders`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (!response.ok) throw new Error('Failed to fetch failed orders');

      const data = await response.json();
      setFailedOrders(data.failed_orders || []);
    } catch (error) {
      console.error('Error loading failed orders:', error);
      toast.error('Fehler beim Laden der fehlgeschlagenen Bestellungen');
    } finally {
      setLoading(false);
    }
  };

  const retryFailedOrder = async (failedOrderId, orderNumber) => {
    setRetrying(failedOrderId);
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/pos/failed-orders/${failedOrderId}/retry`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          }
        }
      );

      const result = await response.json();

      if (result.success) {
        toast.success(`Bestellung ${orderNumber} erfolgreich an POS gesendet!`);
        // Remove from list or reload
        loadFailedOrders();
      } else {
        toast.error(`Retry fehlgeschlagen: ${result.message}`);
        // Reload to get updated retry count
        loadFailedOrders();
      }
    } catch (error) {
      console.error('Error retrying order:', error);
      toast.error('Fehler beim erneuten Senden der Bestellung');
    } finally {
      setRetrying(null);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getErrorTypeColor = (errorType) => {
    if (errorType === 'hard') {
      return 'bg-red-500/10 text-red-600 border-red-500/20';
    }
    return 'bg-orange-500/10 text-orange-600 border-orange-500/20';
  };

  const getErrorTypeLabel = (errorType) => {
    if (errorType === 'hard') {
      return 'Verbindungsfehler';
    }
    return 'API-Fehler';
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container-custom">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-serif font-bold flex items-center gap-3">
                <AlertTriangle className="h-7 w-7 text-orange-600" />
                POS Fehlgeschlagene Bestellungen
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Bestellungen, die nicht automatisch an das POS-System übertragen werden konnten
              </p>
            </div>
            <button
              onClick={loadFailedOrders}
              className="btn-secondary flex items-center gap-2"
              data-testid="refresh-failed-orders-button"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Aktualisieren
            </button>
          </div>
        </div>

        {/* Alert Banner */}
        {failedOrders.length > 0 && (
          <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-orange-600">Umsatz-Schutz aktiv</h3>
                <p className="text-sm text-orange-600/90 mt-1">
                  {failedOrders.length} {failedOrders.length === 1 ? 'Bestellung wurde' : 'Bestellungen wurden'} 
                  {' '}nicht automatisch an das POS übertragen. Diese Bestellungen sind lokal gespeichert und 
                  können hier manuell nachgesendet werden.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Failed Orders List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-4 text-muted-foreground">Lade fehlgeschlagene Bestellungen...</p>
          </div>
        ) : failedOrders.length === 0 ? (
          <div className="bg-accent rounded-lg p-12 text-center">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
            <h3 className="font-semibold text-lg mb-2">Alles synchronisiert</h3>
            <p className="text-muted-foreground">
              Keine fehlgeschlagenen POS-Übertragungen. Alle Bestellungen wurden erfolgreich gesendet.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {failedOrders.map((failedOrder) => (
              <div
                key={failedOrder._id}
                className="bg-card border border-border rounded-lg p-5 hover:shadow-md transition-shadow"
                data-testid={`failed-order-${failedOrder.order_number}`}
              >
                <div className="flex items-start justify-between gap-4">
                  {/* Left: Order Info */}
                  <div className="flex-1 space-y-3">
                    {/* Order Number & Location */}
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="font-semibold text-lg">
                        {failedOrder.order_number || 'N/A'}
                      </h3>
                      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                        <MapPin className="h-4 w-4" />
                        {failedOrder.location_slug || 'Unknown'}
                      </div>
                      {/* Error Type Badge */}
                      <span className={`px-2.5 py-1 rounded-md text-xs font-medium border ${getErrorTypeColor(failedOrder.error_type)}`}>
                        {getErrorTypeLabel(failedOrder.error_type)}
                      </span>
                    </div>

                    {/* Timestamp */}
                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      <span>Fehlgeschlagen am: {formatDate(failedOrder.created_at)}</span>
                    </div>

                    {/* Error Message */}
                    <div className="bg-red-500/5 border border-red-500/10 rounded-md p-3">
                      <p className="text-sm text-red-600 font-medium mb-1">Fehlermeldung:</p>
                      <p className="text-sm text-red-600/80 font-mono break-all">
                        {failedOrder.error || 'Unknown error'}
                      </p>
                    </div>

                    {/* Retry Count */}
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-muted-foreground">Automatische Versuche:</span>
                      <span className="font-semibold">{failedOrder.retry_count || 0}</span>
                    </div>
                  </div>

                  {/* Right: Action Button */}
                  <div className="flex-shrink-0">
                    <button
                      onClick={() => retryFailedOrder(failedOrder._id, failedOrder.order_number)}
                      disabled={retrying === failedOrder._id}
                      className="btn-primary flex items-center gap-2 min-w-[140px] justify-center"
                      data-testid={`retry-button-${failedOrder.order_number}`}
                    >
                      {retrying === failedOrder._id ? (
                        <>
                          <RefreshCw className="h-4 w-4 animate-spin" />
                          Sende...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="h-4 w-4" />
                          Retry
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info Box */}
        <div className="mt-8 bg-blue-500/5 border border-blue-500/10 rounded-lg p-4">
          <h3 className="font-semibold text-blue-600 mb-2">ℹ️ Was bedeutet das?</h3>
          <ul className="text-sm text-blue-600/80 space-y-1.5">
            <li>• <strong>Verbindungsfehler (Hard):</strong> Das POS-System war nicht erreichbar (Netzwerk, Server offline)</li>
            <li>• <strong>API-Fehler (Soft):</strong> Das POS hat die Bestellung abgelehnt (z.B. ungültige Daten, Konfiguration)</li>
            <li>• Bestellungen werden automatisch 3x mit exponentieller Verzögerung wiederholt (2s, 5s, 10s)</li>
            <li>• Nach 3 Fehlversuchen landen Bestellungen in dieser Queue für manuelles Retry</li>
            <li>• Die Bestellung ist lokal gespeichert und bezahlt - kein Umsatz geht verloren</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default FailedPOSOrders;

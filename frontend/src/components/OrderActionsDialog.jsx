import React, { useState, useEffect } from 'react';
import { X, RefreshCw, Building2, CheckCircle, AlertTriangle, FileText } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function OrderActionsDialog({ order, isOpen, onClose, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState('');
  const [transferReason, setTransferReason] = useState('');
  const [manualReason, setManualReason] = useState('');
  const [errorLog, setErrorLog] = useState(null);
  const [showErrorLog, setShowErrorLog] = useState(false);
  
  useEffect(() => {
    if (isOpen) {
      loadLocations();
      loadErrorLog();
    }
  }, [isOpen]);

  const loadLocations = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/locations`);
      setLocations(response.data);
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  };

  const loadErrorLog = async () => {
    try {
      const token = localStorage.getItem('zozoAuthToken');
      const response = await axios.get(
        `${API_URL}/api/admin/orders/${order.id || order._id}/error-log`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setErrorLog(response.data);
    } catch (error) {
      console.error('Error loading error log:', error);
    }
  };

  const handleRetryPOS = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('zozoAuthToken');
      const response = await axios.post(
        `${API_URL}/api/admin/orders/${order.id || order._id}/pos/retry`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        toast.success('Bestellung erfolgreich an POS gesendet');
        onSuccess?.();
        onClose();
      } else {
        toast.error(response.data.message || 'Fehler beim Senden an POS');
      }
    } catch (error) {
      console.error('Retry POS error:', error);
      toast.error(error.response?.data?.detail || 'Fehler beim erneuten Senden');
    } finally {
      setLoading(false);
    }
  };

  const handleTransferStore = async () => {
    if (!selectedLocation) {
      toast.error('Bitte wähle eine Filiale aus');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('zozoAuthToken');
      const response = await axios.post(
        `${API_URL}/api/admin/orders/${order.id || order._id}/transfer-store`,
        {
          new_location_id: selectedLocation,
          reason: transferReason || 'Filialenwechsel auf Admin-Anfrage',
          push_to_pos: true
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        toast.success(`Bestellung erfolgreich übertragen nach ${response.data.new_location.name}`);
        onSuccess?.();
        onClose();
      } else {
        toast.error('Fehler beim Übertragen');
      }
    } catch (error) {
      console.error('Transfer error:', error);
      toast.error(error.response?.data?.detail || 'Fehler beim Übertragen der Bestellung');
    } finally {
      setLoading(false);
    }
  };

  const handleManualOverride = async () => {
    if (!manualReason) {
      toast.error('Bitte gib einen Grund an');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('zozoAuthToken');
      const response = await axios.post(
        `${API_URL}/api/admin/orders/${order.id || order._id}/manual-override`,
        {
          reason: manualReason,
          override_type: 'manual_processing'
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        toast.success('Bestellung als manuell bearbeitet markiert');
        onSuccess?.();
        onClose();
      }
    } catch (error) {
      console.error('Manual override error:', error);
      toast.error(error.response?.data?.detail || 'Fehler beim Markieren');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-card rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-border">
        {/* Header */}
        <div className="sticky top-0 bg-card border-b border-border p-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Bestellung {order.order_number}</h2>
            <p className="text-sm text-muted-foreground">Enterprise Order Management</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-secondary rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Order Status Info */}
          <div className="bg-muted/30 rounded-lg p-4">
            <h3 className="font-semibold mb-2">Status-Übersicht</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Status:</span>
                <span className="ml-2 font-medium">{order.status}</span>
              </div>
              <div>
                <span className="text-muted-foreground">POS-Status:</span>
                <span className={`ml-2 font-medium ${
                  order.pos_status === 'sent' || order.pos_status === 'success' 
                    ? 'text-green-600' 
                    : order.pos_status === 'error' || order.pos_status === 'failed'
                    ? 'text-red-600'
                    : 'text-orange-600'
                }`}>
                  {order.pos_status || 'pending'}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Filiale:</span>
                <span className="ml-2 font-medium">{order.location_slug || order.location_id}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Gesamt:</span>
                <span className="ml-2 font-medium">€{order.total?.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Action 1: Retry POS */}
          <div className="border border-border rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <RefreshCw className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Erneut an POS senden</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Versucht die Bestellung erneut an das POS-System zu senden
                </p>
                <button
                  onClick={handleRetryPOS}
                  disabled={loading}
                  className="btn-primary text-sm disabled:opacity-50"
                >
                  {loading ? 'Sende...' : 'Jetzt erneut senden'}
                </button>
              </div>
            </div>
          </div>

          {/* Action 2: Transfer Store */}
          <div className="border border-border rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Building2 className="h-5 w-5 text-blue-500" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Filiale wechseln</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Übertrage Bestellung an eine andere Filiale
                </p>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-2">Ziel-Filiale</label>
                    <select
                      value={selectedLocation}
                      onChange={(e) => setSelectedLocation(e.target.value)}
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      disabled={loading}
                    >
                      <option value="">Filiale auswählen...</option>
                      {locations.map((loc) => (
                        <option key={loc.id || loc._id} value={loc.id || loc._id}>
                          {loc.name} - {loc.city}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Grund (optional)</label>
                    <input
                      type="text"
                      value={transferReason}
                      onChange={(e) => setTransferReason(e.target.value)}
                      placeholder="z.B. Kunde hat falsche Filiale gewählt"
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      disabled={loading}
                    />
                  </div>
                  
                  <button
                    onClick={handleTransferStore}
                    disabled={loading || !selectedLocation}
                    className="btn-secondary text-sm disabled:opacity-50"
                  >
                    {loading ? 'Übertrage...' : 'Filiale wechseln & an POS senden'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Action 3: Manual Override */}
          <div className="border border-border rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-green-500/10 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Als manuell bearbeitet markieren</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Markiere diese Bestellung als manuell verarbeitet (telefonisch/persönlich)
                </p>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-2">Grund</label>
                    <input
                      type="text"
                      value={manualReason}
                      onChange={(e) => setManualReason(e.target.value)}
                      placeholder="z.B. Telefonische Bestellung übernommen"
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      disabled={loading}
                    />
                  </div>
                  
                  <button
                    onClick={handleManualOverride}
                    disabled={loading || !manualReason}
                    className="btn-secondary text-sm disabled:opacity-50"
                  >
                    {loading ? 'Markiere...' : 'Als manuell markieren'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Error Log */}
          <div className="border border-border rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-orange-500/10 rounded-lg">
                <FileText className="h-5 w-5 text-orange-500" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold">Fehlerprotokoll</h3>
                  <button
                    onClick={() => setShowErrorLog(!showErrorLog)}
                    className="text-sm text-primary hover:underline"
                  >
                    {showErrorLog ? 'Ausblenden' : 'Anzeigen'}
                  </button>
                </div>
                
                {showErrorLog && errorLog && (
                  <div className="mt-3 space-y-2 bg-muted/30 rounded-lg p-3 max-h-64 overflow-y-auto">
                    {errorLog.errors?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium mb-2">Fehler:</h4>
                        {errorLog.errors.map((error, idx) => (
                          <div key={idx} className="text-sm bg-red-500/10 border border-red-500/20 rounded p-2 mb-2">
                            <div className="font-medium text-red-600">{error.type}</div>
                            <div className="text-xs text-muted-foreground">{error.message}</div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {errorLog.attempts?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium mb-2">Versuche ({errorLog.attempts.length}):</h4>
                        {errorLog.attempts.map((attempt, idx) => (
                          <div key={idx} className="text-sm bg-background rounded p-2 mb-2">
                            <div className="flex items-center justify-between">
                              <span className={`font-medium ${
                                attempt.status === 'resolved' ? 'text-green-600' : 'text-orange-600'
                              }`}>
                                {attempt.status || 'failed'}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {new Date(attempt.timestamp).toLocaleString('de-DE')}
                              </span>
                            </div>
                            {attempt.error_message && (
                              <div className="text-xs text-muted-foreground mt-1">
                                {attempt.error_message}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {(!errorLog.errors || errorLog.errors.length === 0) && 
                     (!errorLog.attempts || errorLog.attempts.length === 0) && (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        Keine Fehler protokolliert
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OrderActionsDialog;

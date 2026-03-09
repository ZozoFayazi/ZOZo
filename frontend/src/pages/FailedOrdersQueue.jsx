import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { toast } from 'sonner';
import { AlertTriangle, CheckCircle, RotateCcw, Trash2, Clock } from 'lucide-react';

export default function FailedOrdersQueue() {
  const { token } = useAdminAuth();
  const [failedOrders, setFailedOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [retrying, setRetrying] = useState(null);

  useEffect(() => {
    fetchFailedOrders();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchFailedOrders, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchFailedOrders = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/admin/pos/failed-orders`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setFailedOrders(data);
      }
    } catch (error) {
      console.error('Error fetching failed orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async (orderId) => {
    setRetrying(orderId);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(
        `${backendUrl}/api/admin/pos/retry-failed-order/${orderId}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        toast.success('Bestellung erneut gesendet');
        fetchFailedOrders();
      } else {
        toast.error('Fehler beim erneuten Senden');
      }
    } catch (error) {
      console.error('Retry error:', error);
      toast.error('Verbindungsfehler');
    } finally {
      setRetrying(null);
    }
  };

  const handleResolve = async (orderId) => {
    if (!window.confirm('Als manuell gelöst markieren?')) return;

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(
        `${backendUrl}/api/admin/pos/resolve-failed-order/${orderId}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        toast.success('Als gelöst markiert');
        fetchFailedOrders();
      } else {
        toast.error('Fehler');
      }
    } catch (error) {
      toast.error('Verbindungsfehler');
    }
  };

  const pendingOrders = failedOrders.filter(o => o.status === 'pending');
  const resolvedOrders = failedOrders.filter(o => o.status === 'resolved');

  return (
    <AdminLayout>
      <div className="space-y-6 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">POS Fehler-Queue</h1>
            <p className="text-muted-foreground mt-2">
              Bestellungen die nicht an das POS-System gesendet werden konnten
            </p>
          </div>
          <Button onClick={fetchFailedOrders} variant="outline">
            <RotateCcw className="h-4 w-4 mr-2" />
            Aktualisieren
          </Button>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Ausstehend</p>
                  <p className="text-3xl font-bold text-orange-600">{pendingOrders.length}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Gelöst</p>
                  <p className="text-3xl font-bold text-green-600">{resolvedOrders.length}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Gesamt</p>
                  <p className="text-3xl font-bold">{failedOrders.length}</p>
                </div>
                <Clock className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Pending Orders */}
        {pendingOrders.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                Ausstehende Bestellungen ({pendingOrders.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Bestellnummer</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Fehler</TableHead>
                    <TableHead>Versuche</TableHead>
                    <TableHead>Erstellt</TableHead>
                    <TableHead className="text-right">Aktionen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pendingOrders.map((order) => (
                    <TableRow key={order._id || order.id}>
                      <TableCell className="font-medium">{order.order_number}</TableCell>
                      <TableCell>{order.location_slug}</TableCell>
                      <TableCell className="max-w-xs">
                        <p className="text-sm text-destructive truncate" title={order.error}>
                          {order.error}
                        </p>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{order.retry_count || 0}</Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(order.created_at).toLocaleString('de-DE')}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex gap-2 justify-end">
                          <Button
                            size="sm"
                            onClick={() => handleRetry(order._id || order.id)}
                            disabled={retrying === (order._id || order.id)}
                          >
                            {retrying === (order._id || order.id) ? (
                              'Sendet...'
                            ) : (
                              <>
                                <RotateCcw className="h-4 w-4 mr-1" />
                                Wiederholen
                              </>
                            )}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleResolve(order._id || order.id)}
                          >
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Gelöst
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {/* No Failed Orders */}
        {!loading && pendingOrders.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Keine ausstehenden Fehler</h3>
              <p className="text-muted-foreground">
                Alle Bestellungen wurden erfolgreich an das POS-System gesendet.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="text-muted-foreground mt-4">Lade Fehler-Queue...</p>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}

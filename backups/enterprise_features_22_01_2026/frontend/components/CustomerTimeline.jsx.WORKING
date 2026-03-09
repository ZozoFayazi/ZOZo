import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Clock, Package, MapPin, Euro } from 'lucide-react';
import { Badge } from './ui/badge';

function CustomerTimeline({ orders }) {
  if (!orders || orders.length === 0) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-primary" />
            Bestell-Historie
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Keine Bestellungen vorhanden
          </div>
        </CardContent>
      </Card>
    );
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      'completed': { label: 'Abgeschlossen', color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' },
      'new': { label: 'Neu', color: 'bg-blue-500/10 text-blue-600 border-blue-500/20' },
      'preparing': { label: 'Vorbereitung', color: 'bg-orange-500/10 text-orange-600 border-orange-500/20' },
      'cancelled': { label: 'Storniert', color: 'bg-red-500/10 text-red-600 border-red-500/20' }
    };

    const config = statusConfig[status] || { label: status, color: 'bg-muted text-muted-foreground' };
    return <Badge className={`${config.color} border text-xs`}>{config.label}</Badge>;
  };

  return (
    <Card className="border-border" data-testid="customer-timeline">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-primary" />
          Bestell-Historie ({orders.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {orders.map((order, index) => (
            <div 
              key={order.order_id} 
              className="flex gap-4 p-4 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors border border-border"
              data-testid={`timeline-order-${index}`}
            >
              {/* Left: Date Indicator */}
              <div className="flex flex-col items-center">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Package className="h-5 w-5 text-primary" />
                </div>
                {index !== orders.length - 1 && (
                  <div className="w-0.5 flex-1 bg-border mt-2"></div>
                )}
              </div>

              {/* Right: Order Details */}
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="font-medium text-foreground">#{order.order_id}</div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(order.date).toLocaleDateString('de-DE', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                  {getStatusBadge(order.status)}
                </div>

                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Package className="h-4 w-4" />
                    {order.items_count} Artikel
                  </div>
                  {order.location && (
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {order.location}
                    </div>
                  )}
                  <div className="flex items-center gap-1 font-semibold text-foreground">
                    <Euro className="h-4 w-4" />
                    {order.total.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default CustomerTimeline;

import React from 'react';
import { Card, CardContent } from './ui/card';
import RFMBadge from './RFMBadge';
import { Mail, Phone, Calendar, ShoppingCart, Euro, Clock, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

function CustomerCard({ customer }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/admin/customers/${encodeURIComponent(customer.customer_id)}`);
  };

  return (
    <Card 
      className="border-border hover:border-primary/50 transition-all cursor-pointer hover:shadow-lg"
      onClick={handleClick}
      data-testid={`customer-card-${customer.customer_id}`}
    >
      <CardContent className="p-6">
        {/* Header: Name + RFM Badge */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-foreground mb-1">{customer.name}</h3>
            <div className="flex flex-col gap-1 text-sm text-muted-foreground">
              {customer.email && (
                <div className="flex items-center gap-1.5">
                  <Mail className="h-3.5 w-3.5" />
                  {customer.email}
                </div>
              )}
              {customer.phone && (
                <div className="flex items-center gap-1.5">
                  <Phone className="h-3.5 w-3.5" />
                  {customer.phone}
                </div>
              )}
            </div>
          </div>
          <RFMBadge segment={customer.rfm.segment} score={customer.rfm.rfm_score} />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-muted/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
              <ShoppingCart className="h-3.5 w-3.5" />
              Bestellungen
            </div>
            <div className="text-2xl font-bold text-foreground">{customer.completed_orders}</div>
          </div>

          <div className="bg-muted/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
              <Euro className="h-3.5 w-3.5" />
              Gesamtumsatz
            </div>
            <div className="text-2xl font-bold text-foreground">€{customer.total_spent.toFixed(2)}</div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-muted-foreground">
              <TrendingUp className="h-4 w-4" />
              Ø Bestellwert
            </div>
            <div className="font-semibold text-foreground">€{customer.avg_order_value.toFixed(2)}</div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Clock className="h-4 w-4" />
              Letzte Bestellung
            </div>
            <div className="font-medium text-foreground">
              {customer.days_since_last_order === 0 ? 'Heute' :
               customer.days_since_last_order === 1 ? 'Gestern' :
               `vor ${customer.days_since_last_order} Tagen`}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Calendar className="h-4 w-4" />
              Kunde seit
            </div>
            <div className="font-medium text-foreground">
              {customer.customer_lifetime_days} Tagen
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default CustomerCard;

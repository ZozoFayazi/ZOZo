import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AdminLayout from '../components/AdminLayout';
import CustomerTimeline from '../components/CustomerTimeline';
import RFMBadge from '../components/RFMBadge';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { 
  ArrowLeft, 
  Mail, 
  Phone, 
  Calendar, 
  ShoppingCart, 
  Euro,
  Clock,
  TrendingUp,
  MapPin,
  Star,
  Send
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function CustomerDetail() {
  const { customerId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [customer, setCustomer] = useState(null);

  useEffect(() => {
    loadCustomerDetail();
  }, [customerId]);

  const loadCustomerDetail = async () => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await axios.get(
        `${API_URL}/api/admin/customers/${encodeURIComponent(customerId)}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCustomer(response.data);
    } catch (error) {
      console.error('Error loading customer:', error);
      toast.error('Fehler beim Laden der Kundendaten');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="min-h-screen bg-background p-4 lg:p-8">
          <div className="max-w-6xl mx-auto">
            <div className="animate-pulse space-y-4">
              <div className="h-8 bg-muted rounded w-1/4"></div>
              <div className="h-64 bg-muted rounded"></div>
              <div className="h-96 bg-muted rounded"></div>
            </div>
          </div>
        </div>
      </AdminLayout>
    );
  }

  if (!customer) {
    return (
      <AdminLayout>
        <div className="min-h-screen bg-background p-4 lg:p-8">
          <div className="max-w-6xl mx-auto text-center py-12">
            <h2 className="text-2xl font-bold text-foreground mb-4">Kunde nicht gefunden</h2>
            <Button onClick={() => navigate('/admin/customers')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Zurück zur Übersicht
            </Button>
          </div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="min-h-screen bg-background p-4 lg:p-8" data-testid="customer-detail-page">
        <div className="max-w-6xl mx-auto">
          {/* Back Button */}
          <Button 
            variant="ghost" 
            onClick={() => navigate('/admin/customers')}
            className="mb-4"
            data-testid="back-button"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Zurück zur Übersicht
          </Button>

          {/* Customer Header */}
          <Card className="border-border mb-6">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h1 className="text-3xl font-bold text-foreground mb-2">{customer.name}</h1>
                  <div className="flex flex-col gap-2 text-muted-foreground">
                    {customer.email && (
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        {customer.email}
                      </div>
                    )}
                    {customer.phone && (
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4" />
                        {customer.phone}
                      </div>
                    )}
                  </div>
                </div>
                <RFMBadge segment={customer.rfm.segment} score={customer.rfm.rfm_score} />
              </div>

              {/* Quick Actions */}
              <div className="flex gap-2">
                {customer.email && (
                  <Button variant="outline" size="sm" asChild>
                    <a href={`mailto:${customer.email}`}>
                      <Mail className="h-4 w-4 mr-2" />
                      E-Mail senden
                    </a>
                  </Button>
                )}
                {customer.phone && (
                  <Button variant="outline" size="sm" asChild>
                    <a href={`tel:${customer.phone}`}>
                      <Phone className="h-4 w-4 mr-2" />
                      Anrufen
                    </a>
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card className="border-border">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <ShoppingCart className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Bestellungen</div>
                    <div className="text-2xl font-bold text-foreground">{customer.completed_orders}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-border">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                    <Euro className="h-5 w-5 text-emerald-600" />
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Gesamtumsatz</div>
                    <div className="text-2xl font-bold text-foreground">€{customer.total_spent.toFixed(2)}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-border">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <TrendingUp className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Ø Bestellwert</div>
                    <div className="text-2xl font-bold text-foreground">€{customer.avg_order_value.toFixed(2)}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-border">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="h-10 w-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
                    <Clock className="h-5 w-5 text-orange-600" />
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Letzte Bestellung</div>
                    <div className="text-lg font-bold text-foreground">
                      {customer.days_since_last_order === 0 ? 'Heute' :
                       customer.days_since_last_order === 1 ? 'Gestern' :
                       `vor ${customer.days_since_last_order}d`}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Additional Info Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Favorite Products */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-amber-500" />
                  Lieblingsprodukte
                </CardTitle>
              </CardHeader>
              <CardContent>
                {customer.favorite_products && customer.favorite_products.length > 0 ? (
                  <div className="space-y-3">
                    {customer.favorite_products.map((product, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                        <span className="font-medium text-foreground">{product.name}</span>
                        <span className="text-sm text-muted-foreground">{product.count}x bestellt</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-muted-foreground">
                    Keine Daten verfügbar
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Customer Info */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-primary" />
                  Kundeninformationen
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Kunde seit</span>
                    <span className="font-semibold text-foreground">
                      {new Date(customer.first_order_date).toLocaleDateString('de-DE')}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Kundenlebensdauer</span>
                    <span className="font-semibold text-foreground">{customer.customer_lifetime_days} Tage</span>
                  </div>
                  {customer.preferred_location && (
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        Bevorzugte Filiale
                      </span>
                      <span className="font-semibold text-foreground capitalize">{customer.preferred_location}</span>
                    </div>
                  )}
                  <div className="pt-4 border-t border-border">
                    <div className="text-sm text-muted-foreground mb-2">RFM-Details</div>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="bg-muted/30 rounded p-2">
                        <div className="text-xs text-muted-foreground">Recency</div>
                        <div className="text-lg font-bold text-foreground">{customer.rfm.r_score}/5</div>
                      </div>
                      <div className="bg-muted/30 rounded p-2">
                        <div className="text-xs text-muted-foreground">Frequency</div>
                        <div className="text-lg font-bold text-foreground">{customer.rfm.f_score}/5</div>
                      </div>
                      <div className="bg-muted/30 rounded p-2">
                        <div className="text-xs text-muted-foreground">Monetary</div>
                        <div className="text-lg font-bold text-foreground">{customer.rfm.m_score}/5</div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Order Timeline */}
          <CustomerTimeline orders={customer.order_timeline} />
        </div>
      </div>
    </AdminLayout>
  );
}

export default CustomerDetail;

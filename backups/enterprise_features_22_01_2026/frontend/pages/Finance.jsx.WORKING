import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { 
  Euro, 
  TrendingUp, 
  TrendingDown, 
  ShoppingCart, 
  CreditCard,
  RefreshCw,
  Download,
  Calendar,
  Building2,
  PieChart,
  BarChart3
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { AreaChart, Area, BarChart, Bar, PieChart as RePieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function Finance() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [rangeType, setRangeType] = useState('this_month');
  
  // Data states
  const [overview, setOverview] = useState(null);
  const [locationRevenue, setLocationRevenue] = useState([]);
  const [categoryRevenue, setCategoryRevenue] = useState([]);
  const [dailyTrend, setDailyTrend] = useState([]);
  const [topProducts, setTopProducts] = useState([]);

  useEffect(() => {
    loadFinanceData();
  }, [rangeType]);

  const loadFinanceData = async () => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('adminToken');
      const headers = { Authorization: `Bearer ${token}` };
      const params = { range_type: rangeType };

      const [overviewRes, locationRes, categoryRes, trendRes, productsRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/finance/overview`, { headers, params }),
        axios.get(`${API_URL}/api/admin/finance/revenue-by-location`, { headers, params }),
        axios.get(`${API_URL}/api/admin/finance/revenue-by-category`, { headers, params }),
        axios.get(`${API_URL}/api/admin/finance/daily-trend`, { headers, params }),
        axios.get(`${API_URL}/api/admin/finance/top-products`, { headers, params: { ...params, limit: 10 } })
      ]);

      setOverview(overviewRes.data);
      setLocationRevenue(locationRes.data.data);
      setCategoryRevenue(categoryRes.data.data);
      setDailyTrend(trendRes.data.data);
      setTopProducts(productsRes.data.data);
    } catch (error) {
      console.error('Error loading finance data:', error);
      toast.error('Fehler beim Laden der Finanzdaten');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadFinanceData();
    setRefreshing(false);
    toast.success('Daten aktualisiert');
  };

  const handleExportCSV = async () => {
    try {
      const token = sessionStorage.getItem('adminToken');
      const params = new URLSearchParams({ range_type: rangeType });

      const response = await fetch(
        `${API_URL}/api/admin/finance/export/csv?${params}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `zozo-finance-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);

      toast.success('CSV erfolgreich exportiert');
    } catch (error) {
      console.error('Error exporting CSV:', error);
      toast.error('Fehler beim Export');
    }
  };

  const getRangeLabel = () => {
    const labels = {
      'today': 'Heute',
      'yesterday': 'Gestern',
      'this_week': 'Diese Woche',
      'this_month': 'Dieser Monat',
      'last_month': 'Letzter Monat',
      'this_year': 'Dieses Jahr',
      '30days': 'Letzte 30 Tage'
    };
    return labels[rangeType] || rangeType;
  };

  const getTrendIcon = (value) => {
    if (value > 0) return <TrendingUp className="h-4 w-4 text-emerald-600" />;
    if (value < 0) return <TrendingDown className="h-4 w-4 text-red-600" />;
    return null;
  };

  return (
    <AdminLayout>
      <div className="min-h-screen bg-background p-4 lg:p-8" data-testid="finance-page">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <Euro className="h-8 w-8 text-emerald-600" />
            Finanz-Management
          </h1>
          <p className="text-muted-foreground">
            Umfassende Finanzberichte und Umsatz-Analysen
          </p>
        </div>

        {/* Filters & Actions */}
        <div className="flex flex-wrap items-center gap-3 mb-6 bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium text-foreground">Zeitraum:</span>
          </div>
          
          {['today', 'this_week', 'this_month', 'last_month', '30days'].map(range => (
            <Button
              key={range}
              variant={rangeType === range ? 'default' : 'outline'}
              size="sm"
              onClick={() => setRangeType(range)}
              data-testid={`filter-${range}`}
            >
              {getRangeLabel.call({ rangeType: range })}
            </Button>
          ))}

          <div className="ml-auto flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Aktualisieren
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCSV}
            >
              <Download className="h-4 w-4 mr-2" />
              CSV Export
            </Button>
          </div>
        </div>

        {/* Main Metrics */}
        {overview && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <Card className="border-border">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                      <Euro className="h-5 w-5 text-emerald-600" />
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Brutto-Umsatz</div>
                      <div className="text-2xl font-bold text-foreground">€{overview.overview.total_revenue_gross.toLocaleString('de-DE')}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-sm">
                    {getTrendIcon(overview.overview.revenue_growth_percent)}
                    <span className={overview.overview.revenue_growth_percent >= 0 ? 'text-emerald-600' : 'text-red-600'}>
                      {Math.abs(overview.overview.revenue_growth_percent)}%
                    </span>
                    <span className="text-muted-foreground">vs. vorher</span>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-border">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                      <BarChart3 className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Netto-Umsatz</div>
                      <div className="text-2xl font-bold text-foreground">€{overview.overview.total_revenue_net.toLocaleString('de-DE')}</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Ohne 19% MwSt.
                  </div>
                </CardContent>
              </Card>

              <Card className="border-border">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="h-10 w-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
                      <TrendingUp className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">MwSt. (19%)</div>
                      <div className="text-2xl font-bold text-foreground">€{overview.overview.total_tax.toLocaleString('de-DE')}</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Steuerliches Reporting
                  </div>
                </CardContent>
              </Card>

              <Card className="border-border">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                      <ShoppingCart className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Ø Bestellwert</div>
                      <div className="text-2xl font-bold text-foreground">€{overview.overview.avg_order_value.toFixed(2)}</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {overview.overview.total_orders} Bestellungen
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Daily Trend */}
              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-primary" />
                    Täglicher Umsatz-Verlauf
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {dailyTrend.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={dailyTrend}>
                        <defs>
                          <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                        <XAxis 
                          dataKey="date" 
                          stroke="hsl(var(--muted-foreground))"
                          fontSize={12}
                          tickFormatter={(value) => new Date(value).toLocaleDateString('de-DE', { day: '2-digit', month: 'short' })}
                        />
                        <YAxis 
                          stroke="hsl(var(--muted-foreground))"
                          fontSize={12}
                          tickFormatter={(value) => `€${value}`}
                        />
                        <Tooltip 
                          contentStyle={{
                            backgroundColor: 'hsl(var(--card))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px'
                          }}
                          formatter={(value) => [`€${value}`, 'Umsatz']}
                        />
                        <Area type="monotone" dataKey="revenue_gross" stroke="#10b981" strokeWidth={2} fill="url(#colorRevenue)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                      Keine Daten verfügbar
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Payment Methods */}
              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="h-5 w-5 text-primary" />
                    Zahlungsarten
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {Object.keys(overview.payment_methods).length > 0 ? (
                    <div className="space-y-4">
                      {Object.entries(overview.payment_methods).map(([method, data], index) => (
                        <div key={method} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-foreground">{method}</span>
                            <span className="text-sm text-muted-foreground">{data.count}x</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 h-8 bg-muted rounded-lg overflow-hidden">
                              <div 
                                className="h-full flex items-center justify-end px-3"
                                style={{ 
                                  width: `${data.percentage}%`,
                                  backgroundColor: COLORS[index % COLORS.length]
                                }}
                              >
                                <span className="text-sm font-bold text-white">
                                  €{data.revenue.toFixed(2)}
                                </span>
                              </div>
                            </div>
                            <span className="text-sm font-semibold text-foreground w-12 text-right">
                              {data.percentage}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                      Keine Daten verfügbar
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Additional Grids */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Location Revenue */}
              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building2 className="h-5 w-5 text-primary" />
                    Umsatz nach Filiale
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {locationRevenue.length > 0 ? (
                    <div className="space-y-3">
                      {locationRevenue.map((loc, index) => (
                        <div key={loc.location_id} className="p-4 bg-muted/30 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-foreground">{loc.location_name}</span>
                            <span className="text-sm text-muted-foreground">{loc.orders} Orders</span>
                          </div>
                          <div className="grid grid-cols-3 gap-2 text-sm">
                            <div>
                              <div className="text-muted-foreground">Brutto</div>
                              <div className="font-bold text-foreground">€{loc.revenue_gross.toFixed(2)}</div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">Netto</div>
                              <div className="font-bold text-foreground">€{loc.revenue_net.toFixed(2)}</div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">Ø Wert</div>
                              <div className="font-bold text-foreground">€{loc.avg_order_value.toFixed(2)}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      Keine Daten verfügbar
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Top Products */}
              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <PieChart className="h-5 w-5 text-amber-500" />
                    Top 10 Produkte (Umsatz)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {topProducts.length > 0 ? (
                    <div className="space-y-2">
                      {topProducts.map((product, index) => (
                        <div 
                          key={index}
                          className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <div className={`flex items-center justify-center h-8 w-8 rounded-full font-bold text-sm ${
                              index === 0 ? 'bg-amber-500 text-white' :
                              index === 1 ? 'bg-gray-400 text-white' :
                              index === 2 ? 'bg-orange-600 text-white' :
                              'bg-muted text-muted-foreground'
                            }`}>
                              {index + 1}
                            </div>
                            <div>
                              <div className="font-medium text-foreground">{product.product}</div>
                              <div className="text-xs text-muted-foreground">{product.quantity}x verkauft</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-foreground">€{product.revenue.toFixed(2)}</div>
                            <div className="text-xs text-muted-foreground">Ø €{product.avg_price.toFixed(2)}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      Keine Daten verfügbar
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </AdminLayout>
  );
}

export default Finance;

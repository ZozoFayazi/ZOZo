import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  Award, 
  Sparkles, 
  RefreshCw, 
  Calendar,
  DollarSign,
  ShoppingCart
} from 'lucide-react';

const ProductAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Fetch analytics data
  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/analytics/summary`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch analytics');

      const data = await response.json();
      setAnalytics(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Manual badge update
  const updateBadges = async () => {
    try {
      setUpdating(true);
      setSuccess(null);
      setError(null);

      const response = await fetch(`${backendUrl}/api/admin/analytics/update-badges`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to update badges');

      const result = await response.json();
      
      setSuccess(`Badges aktualisiert! ${result.bestsellers} Bestseller, ${result.trending} Trending, ${result.new} Neue Produkte`);
      
      // Refresh analytics
      await fetchAnalytics();
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdating(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Lade Analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Produkt Analytics</h1>
          <p className="text-gray-600 mt-1">
            Automatische Performance-Analyse basierend auf Verkaufszahlen
          </p>
        </div>
        <Button
          onClick={updateBadges}
          disabled={updating}
          className="gap-2"
        >
          {updating ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Aktualisiere...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              Badges jetzt aktualisieren
            </>
          )}
        </Button>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 border-green-200">
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Aktive Produkte</p>
                <p className="text-2xl font-bold">
                  {analytics?.total_active_products || 0}
                </p>
              </div>
              <ShoppingCart className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Bestseller</p>
                <p className="text-2xl font-bold">
                  {analytics?.bestsellers?.length || 0}
                </p>
              </div>
              <Award className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Trending</p>
                <p className="text-2xl font-bold">
                  {analytics?.trending?.length || 0}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Neue Produkte</p>
                <p className="text-2xl font-bold">
                  {analytics?.new_products_count || 0}
                </p>
              </div>
              <Sparkles className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <Tabs defaultValue="bestsellers" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="bestsellers">
            <Award className="w-4 h-4 mr-2" />
            Bestseller
          </TabsTrigger>
          <TabsTrigger value="trending">
            <TrendingUp className="w-4 h-4 mr-2" />
            Trending
          </TabsTrigger>
        </TabsList>

        {/* Bestsellers Tab */}
        <TabsContent value="bestsellers">
          <Card>
            <CardHeader>
              <CardTitle>Top 10 Bestseller (Letzte 30 Tage)</CardTitle>
            </CardHeader>
            <CardContent>
              {analytics?.bestsellers?.length > 0 ? (
                <div className="space-y-4">
                  {analytics.bestsellers.map((item, index) => (
                    <div
                      key={item.product_id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex items-center justify-center w-8 h-8 bg-green-100 text-green-700 rounded-full font-bold">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-semibold">{item.product_name}</p>
                          <p className="text-sm text-gray-600">
                            {item.total_orders} Bestellungen
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xl font-bold text-green-600">
                          {item.total_quantity} verkauft
                        </p>
                        <p className="text-sm text-gray-600 flex items-center gap-1">
                          <DollarSign className="w-3 h-3" />
                          €{item.total_revenue.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Award className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Noch keine Verkaufsdaten vorhanden</p>
                  <p className="text-sm mt-2">Bestseller werden nach den ersten Bestellungen angezeigt</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Trending Tab */}
        <TabsContent value="trending">
          <Card>
            <CardHeader>
              <CardTitle>Trending Produkte (Letzte 7 Tage)</CardTitle>
            </CardHeader>
            <CardContent>
              {analytics?.trending?.length > 0 ? (
                <div className="space-y-4">
                  {analytics.trending.map((item, index) => (
                    <div
                      key={item.product_id}
                      className="flex items-center justify-between p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg hover:shadow-md transition"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex items-center justify-center w-8 h-8 bg-orange-100 text-orange-700 rounded-full font-bold">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-semibold">{item.product_name}</p>
                          <p className="text-sm text-gray-600">
                            {item.previous_sales} → {item.current_sales} Verkäufe
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-orange-600 flex items-center gap-1">
                          <TrendingUp className="w-5 h-5" />
                          +{item.growth_rate}%
                        </p>
                        <p className="text-sm text-gray-600">Wachstum</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Keine Trending-Produkte gefunden</p>
                  <p className="text-sm mt-2">
                    Produkte mit >50% Wachstum werden hier angezeigt
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Last Update Info */}
      {analytics?.last_updated && (
        <div className="text-center text-sm text-gray-500 flex items-center justify-center gap-2">
          <Calendar className="w-4 h-4" />
          Letzte Aktualisierung: {new Date(analytics.last_updated).toLocaleString('de-DE')}
        </div>
      )}
    </div>
  );
};

export default ProductAnalytics;

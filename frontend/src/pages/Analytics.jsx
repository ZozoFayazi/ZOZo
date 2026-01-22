import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import AdminLayout from '../components/AdminLayout';
import MetricCard from '../components/MetricCard';
import RevenueChart from '../components/RevenueChart';
import PeakHoursChart from '../components/PeakHoursChart';
import TopProductsList from '../components/TopProductsList';
import LocationComparison from '../components/LocationComparison';
import { Button } from '../components/ui/button';
import { 
  DollarSign, 
  ShoppingCart, 
  Users, 
  TrendingUp, 
  RefreshCw, 
  Download,
  Calendar
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function Analytics() {
  const { admin } = useAdminAuth();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Filters
  const [rangeType, setRangeType] = useState('7days');
  const [selectedLocation, setSelectedLocation] = useState(null);
  
  // Data states
  const [overview, setOverview] = useState(null);
  const [revenueTrend, setRevenueTrend] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [peakHours, setPeakHours] = useState([]);
  const [locationComparison, setLocationComparison] = useState([]);

  useEffect(() => {
    loadAllAnalytics();
  }, [rangeType, selectedLocation]);

  const loadAllAnalytics = async () => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('adminToken');
      const headers = { Authorization: `Bearer ${token}` };
      const params = { range_type: rangeType };
      
      if (selectedLocation) {
        params.location_id = selectedLocation;
      }

      // Load all analytics data in parallel
      const [overviewRes, trendRes, productsRes, peakRes, locationRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/analytics/overview`, { headers, params }),
        axios.get(`${API_URL}/api/admin/analytics/revenue-trend`, { headers, params }),
        axios.get(`${API_URL}/api/admin/analytics/top-products`, { headers, params: { ...params, limit: 10 } }),
        axios.get(`${API_URL}/api/admin/analytics/peak-hours`, { headers, params }),
        axios.get(`${API_URL}/api/admin/analytics/location-comparison`, { headers, params: { range_type: rangeType } })
      ]);

      setOverview(overviewRes.data.stats);
      setRevenueTrend(trendRes.data.data);
      setTopProducts(productsRes.data.data);
      setPeakHours(peakRes.data.data);
      setLocationComparison(locationRes.data.data);

    } catch (error) {
      console.error('Error loading analytics:', error);
      toast.error('Fehler beim Laden der Analytics-Daten');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAllAnalytics();
    setRefreshing(false);
    toast.success('Daten aktualisiert');
  };

  const handleExportCSV = async () => {
    try {
      const token = sessionStorage.getItem('adminToken');
      const params = new URLSearchParams({ range_type: rangeType });
      if (selectedLocation) params.append('location_id', selectedLocation);

      const response = await fetch(
        `${API_URL}/api/admin/analytics/export/csv?${params}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `zozo-analytics-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);

      toast.success('CSV erfolgreich exportiert');
    } catch (error) {
      console.error('Error exporting CSV:', error);
      toast.error('Fehler beim Export');
    }
  };

  const getRangeLabel = () => {
    switch (rangeType) {
      case 'today': return 'Heute';
      case 'yesterday': return 'Gestern';
      case '7days': return 'Letzte 7 Tage';
      case '30days': return 'Letzte 30 Tage';
      default: return rangeType;
    }
  };

  return (
    <AdminLayout>
      <div className="min-h-screen bg-background p-4 lg:p-8" data-testid="analytics-page">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">📊 Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Übersicht über Ihre Geschäftsmetriken und Performance
          </p>
        </div>

        {/* Filters & Actions */}
        <div className="flex flex-wrap items-center gap-3 mb-6 bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium text-foreground">Zeitraum:</span>
          </div>
          
          {['today', 'yesterday', '7days', '30days'].map(range => (
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
              data-testid="refresh-button"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Aktualisieren
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCSV}
              data-testid="export-csv-button"
            >
              <Download className="h-4 w-4 mr-2" />
              CSV Export
            </Button>
          </div>
        </div>

        {/* Main Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <MetricCard
            title="Gesamtumsatz"
            value={overview?.revenue.total || 0}
            change={overview?.revenue.change}
            icon={DollarSign}
            prefix="€"
            loading={loading}
          />
          
          <MetricCard
            title="Bestellungen"
            value={overview?.orders.total || 0}
            change={overview?.orders.change}
            icon={ShoppingCart}
            loading={loading}
          />
          
          <MetricCard
            title="Kunden"
            value={overview?.customers.total || 0}
            icon={Users}
            loading={loading}
          />
          
          <MetricCard
            title="Ø Bestellwert"
            value={overview?.avg_order_value.value || 0}
            change={overview?.avg_order_value.change}
            icon={TrendingUp}
            prefix="€"
            loading={loading}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="lg:col-span-2">
            <RevenueChart data={revenueTrend} loading={loading} />
          </div>
          
          <PeakHoursChart data={peakHours} loading={loading} />
          
          <TopProductsList data={topProducts} loading={loading} />
        </div>

        {/* Location Comparison */}
        {!selectedLocation && locationComparison.length > 0 && (
          <div className="mb-6">
            <LocationComparison data={locationComparison} loading={loading} />
          </div>
        )}

        {/* Additional Stats */}
        {overview && !loading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-card border border-border rounded-lg p-4">
              <div className="text-sm text-muted-foreground mb-1">Neue Bestellungen</div>
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {overview.orders.new}
              </div>
            </div>
            
            <div className="bg-card border border-border rounded-lg p-4">
              <div className="text-sm text-muted-foreground mb-1">In Vorbereitung</div>
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                {overview.orders.preparing}
              </div>
            </div>
            
            <div className="bg-card border border-border rounded-lg p-4">
              <div className="text-sm text-muted-foreground mb-1">Abgeschlossen</div>
              <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                {overview.orders.completed}
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}

export default Analytics;

import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import CustomerCard from '../components/CustomerCard';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  Users, 
  Search, 
  Download, 
  RefreshCw,
  Filter,
  TrendingUp,
  Package,
  Euro,
  UserCheck
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function Customers() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [segmentStats, setSegmentStats] = useState(null);
  const [total, setTotal] = useState(0);
  
  // Filters
  const [selectedSegment, setSelectedSegment] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('total_spent');

  useEffect(() => {
    loadCustomers();
    loadSegmentStats();
  }, [selectedSegment, sortBy]);

  const loadCustomers = async () => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('adminToken');
      const params = {
        sort_by: sortBy,
        sort_order: 'desc',
        limit: 100
      };
      
      if (selectedSegment) {
        params.segment = selectedSegment;
      }
      
      if (searchQuery) {
        params.search = searchQuery;
      }

      const response = await axios.get(`${API_URL}/api/admin/customers/`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });

      setCustomers(response.data.customers);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Error loading customers:', error);
      toast.error('Fehler beim Laden der Kunden');
    } finally {
      setLoading(false);
    }
  };

  const loadSegmentStats = async () => {
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await axios.get(`${API_URL}/api/admin/customers/segments/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSegmentStats(response.data);
    } catch (error) {
      console.error('Error loading segment stats:', error);
    }
  };

  const handleSearch = () => {
    loadCustomers();
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([loadCustomers(), loadSegmentStats()]);
    setRefreshing(false);
    toast.success('Daten aktualisiert');
  };

  const handleExportCSV = async () => {
    try {
      const token = sessionStorage.getItem('adminToken');
      const params = new URLSearchParams();
      if (selectedSegment) params.append('segment', selectedSegment);
      if (searchQuery) params.append('search', searchQuery);

      const response = await fetch(
        `${API_URL}/api/admin/customers/export/csv?${params}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `zozo-customers-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);

      toast.success('CSV erfolgreich exportiert');
    } catch (error) {
      console.error('Error exporting CSV:', error);
      toast.error('Fehler beim Export');
    }
  };

  const getSegmentColor = (segment) => {
    switch (segment) {
      case 'VIP': return 'from-amber-500 to-yellow-500';
      case 'Active': return 'from-emerald-500 to-green-500';
      case 'Regular': return 'from-blue-500 to-cyan-500';
      case 'At-Risk': return 'from-orange-500 to-red-500';
      case 'Lost': return 'from-gray-600 to-gray-700';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  return (
    <AdminLayout>
      <div className="min-h-screen bg-background p-4 lg:p-8" data-testid="customers-page">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <Users className="h-8 w-8 text-primary" />
            Kunden-CRM
          </h1>
          <p className="text-muted-foreground">
            Enterprise Customer Relationship Management
          </p>
        </div>

        {/* Segment Stats */}
        {segmentStats && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
            {Object.entries(segmentStats).map(([segment, stats]) => (
              <Card 
                key={segment}
                className={`border-2 cursor-pointer transition-all ${
                  selectedSegment === segment 
                    ? 'border-primary shadow-lg' 
                    : 'border-transparent hover:border-border'
                }`}
                onClick={() => setSelectedSegment(selectedSegment === segment ? null : segment)}
                data-testid={`segment-${segment.toLowerCase()}`}
              >
                <CardContent className="p-4">
                  <div className={`h-12 w-12 rounded-lg bg-gradient-to-br ${getSegmentColor(segment)} mb-3 flex items-center justify-center`}>
                    <UserCheck className="h-6 w-6 text-white" />
                  </div>
                  <div className="text-sm font-medium text-muted-foreground mb-1">{segment}</div>
                  <div className="text-2xl font-bold text-foreground mb-1">{stats.count}</div>
                  <div className="text-xs text-muted-foreground">€{stats.total_revenue.toFixed(2)}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Filters & Actions */}
        <div className="flex flex-wrap items-center gap-3 mb-6 bg-card border border-border rounded-lg p-4">
          <div className="flex-1 flex gap-2">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Suche nach Name, E-Mail oder Telefon..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-10"
                data-testid="search-input"
              />
            </div>
            <Button onClick={handleSearch} data-testid="search-button">
              Suchen
            </Button>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Sortieren:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-background border border-border rounded-md px-3 py-2 text-sm"
              data-testid="sort-select"
            >
              <option value="total_spent">Umsatz</option>
              <option value="total_orders">Bestellungen</option>
              <option value="last_order_date">Letzte Bestellung</option>
              <option value="rfm_score">RFM Score</option>
            </select>
          </div>

          <div className="flex gap-2">
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
              data-testid="export-button"
            >
              <Download className="h-4 w-4 mr-2" />
              CSV Export
            </Button>
          </div>
        </div>

        {/* Results Info */}
        <div className="mb-4 flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            {selectedSegment && (
              <span className="mr-2">
                Filter: <span className="font-semibold text-foreground">{selectedSegment}</span>
              </span>
            )}
            <span className="font-semibold text-foreground">{total}</span> Kunden gefunden
          </div>
          {selectedSegment && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedSegment(null)}
            >
              Filter zurücksetzen
            </Button>
          )}
        </div>

        {/* Customer Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <Card key={i} className="border-border">
                <CardContent className="p-6">
                  <div className="space-y-3">
                    <div className="h-6 bg-muted animate-pulse rounded w-3/4"></div>
                    <div className="h-4 bg-muted animate-pulse rounded w-1/2"></div>
                    <div className="h-20 bg-muted animate-pulse rounded"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : customers.length === 0 ? (
          <Card className="border-border">
            <CardContent className="p-12 text-center">
              <Users className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-foreground mb-2">Keine Kunden gefunden</h3>
              <p className="text-muted-foreground">
                {searchQuery ? 'Versuchen Sie eine andere Suche' : 'Es wurden noch keine Bestellungen aufgegeben'}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customers.map(customer => (
              <CustomerCard key={customer.customer_id} customer={customer} />
            ))}
          </div>
        )}
      </div>
    </AdminLayout>
  );
}

export default Customers;

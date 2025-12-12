import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAdminOrders, updateOrderStatus, getDashboardStats } from '../api';
import { toast } from 'sonner';
import { Package, Clock, CheckCircle, TrendingUp, LogOut, Settings } from 'lucide-react';

function AdminDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('zozoAuthToken');
    const userData = localStorage.getItem('zozoUser');
    
    if (!token || !userData) {
      navigate('/admin');
      return;
    }

    setUser(JSON.parse(userData));
    loadDashboardData();
  }, [navigate]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [ordersData, statsData] = await Promise.all([
        getAdminOrders(),
        getDashboardStats()
      ]);
      setOrders(ordersData);
      setStats(statsData);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      if (error.response?.status === 401) {
        toast.error('Sitzung abgelaufen. Bitte melde dich erneut an.');
        handleLogout();
      } else {
        toast.error('Fehler beim Laden der Daten');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (orderId, newStatus) => {
    try {
      await updateOrderStatus(orderId, newStatus);
      toast.success('Bestellstatus aktualisiert');
      loadDashboardData();
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error('Fehler beim Aktualisieren des Status');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('zozoAuthToken');
    localStorage.removeItem('zozoUser');
    navigate('/admin');
  };

  const filteredOrders = statusFilter === 'all'
    ? orders
    : orders.filter(order => order.status === statusFilter);

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'new':
        return 'bg-warning/10 text-warning border-warning';
      case 'accepted':
      case 'preparing':
        return 'bg-primary/10 text-primary border-primary';
      case 'out_for_delivery':
        return 'bg-blue-500/10 text-blue-500 border-blue-500';
      case 'completed':
        return 'bg-success/10 text-success border-success';
      case 'cancelled':
        return 'bg-destructive/10 text-destructive border-destructive';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'new':
        return 'Neu';
      case 'accepted':
        return 'Angenommen';
      case 'preparing':
        return 'In Zubereitung';
      case 'out_for_delivery':
        return 'Unterwegs';
      case 'completed':
        return 'Abgeschlossen';
      case 'cancelled':
        return 'Storniert';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Lade Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b border-border">
        <div className="container-custom py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <img
                src="https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg"
                alt="ZOZO Burger"
                className="h-10"
              />
              <div>
                <h1 className="text-lg font-semibold">Admin Dashboard</h1>
                <p className="text-sm text-muted-foreground">
                  {user?.role === 'owner' ? 'Alle Standorte' : 'Standort Manager'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigate('/admin/settings')}
                className="flex items-center space-x-2 px-4 py-2 text-sm text-foreground hover:bg-secondary rounded-lg transition-colors"
              >
                <Settings className="h-4 w-4" />
                <span>Einstellungen</span>
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span>Abmelden</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container-custom py-8">
        {/* Stats Cards */}
        {stats && (
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Heute</span>
                <Clock className="h-5 w-5 text-primary" />
              </div>
              <p className="text-2xl font-bold">{stats.today_orders}</p>
              <p className="text-xs text-muted-foreground mt-1">Bestellungen</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Neue</span>
                <Package className="h-5 w-5 text-warning" />
              </div>
              <p className="text-2xl font-bold">{stats.new_orders}</p>
              <p className="text-xs text-muted-foreground mt-1">Zu bearbeiten</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Abgeschlossen</span>
                <CheckCircle className="h-5 w-5 text-success" />
              </div>
              <p className="text-2xl font-bold">{stats.completed_orders}</p>
              <p className="text-xs text-muted-foreground mt-1">Gesamt</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Umsatz</span>
                <TrendingUp className="h-5 w-5 text-primary" />
              </div>
              <p className="text-2xl font-bold">€{stats.total_revenue.toFixed(2)}</p>
              <p className="text-xs text-muted-foreground mt-1">Abgeschlossene Bestellungen</p>
            </div>
          </div>
        )}

        {/* Orders Section */}
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          {/* Tabs */}
          <div className="flex items-center space-x-1 p-4 border-b border-border overflow-x-auto" data-testid="orders-status-tabs">
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                statusFilter === 'all'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-secondary'
              }`}
            >
              Alle ({orders.length})
            </button>
            <button
              onClick={() => setStatusFilter('new')}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                statusFilter === 'new'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-secondary'
              }`}
            >
              Neu ({orders.filter(o => o.status === 'new').length})
            </button>
            <button
              onClick={() => setStatusFilter('preparing')}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                statusFilter === 'preparing'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-secondary'
              }`}
            >
              In Zubereitung ({orders.filter(o => o.status === 'preparing').length})
            </button>
            <button
              onClick={() => setStatusFilter('completed')}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                statusFilter === 'completed'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-secondary'
              }`}
            >
              Abgeschlossen ({orders.filter(o => o.status === 'completed').length})
            </button>
          </div>

          {/* Orders Table */}
          <div className="overflow-x-auto" data-testid="orders-table">
            <table className="w-full">
              <thead className="bg-muted/30 border-b border-border">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Bestellung
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Kunde
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Artikel
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Gesamt
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Aktionen
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredOrders.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-muted-foreground">
                      Keine Bestellungen gefunden
                    </td>
                  </tr>
                ) : (
                  filteredOrders.map((order) => (
                    <tr key={order.id} className="hover:bg-muted/20 transition-colors">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium">{order.order_number}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(order.created_at).toLocaleString('de-DE')}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium">{order.customer.name}</p>
                          <p className="text-xs text-muted-foreground">{order.customer.phone}</p>
                          <p className="text-xs text-muted-foreground">{order.customer.address}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-sm">{order.items.length} Artikel</p>
                      </td>
                      <td className="px-6 py-4">
                        <p className="font-semibold text-primary">€{order.total.toFixed(2)}</p>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusBadgeColor(order.status)}`}>
                          {getStatusLabel(order.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {order.status !== 'completed' && order.status !== 'cancelled' && (
                          <select
                            value={order.status}
                            onChange={(e) => handleStatusUpdate(order.id, e.target.value)}
                            className="px-3 py-1.5 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                          >
                            <option value="new">Neu</option>
                            <option value="accepted">Angenommen</option>
                            <option value="preparing">In Zubereitung</option>
                            <option value="out_for_delivery">Unterwegs</option>
                            <option value="completed">Abgeschlossen</option>
                            <option value="cancelled">Storniert</option>
                          </select>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;

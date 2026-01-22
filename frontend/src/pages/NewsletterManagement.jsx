import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Users, TrendingUp, Send, Plus, ArrowLeft, Eye, Download } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function NewsletterManagement() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [subscribers, setSubscribers] = useState([]);
  const [segments, setSegments] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // overview, subscribers, campaigns

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('adminToken');
      const [statsRes, subscribersRes, segmentsRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/newsletter/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/admin/newsletter/subscribers?status=active`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/admin/newsletter/segments`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setStats(statsRes.data);
      setSubscribers(subscribersRes.data);
      setSegments(segmentsRes.data.segments || {});
    } catch (error) {
      console.error('Error loading newsletter data:', error);
      toast.error('Fehler beim Laden der Newsletter-Daten');
    } finally {
      setLoading(false);
    }
  };

  const exportSubscribers = () => {
    const csv = ['Email,Name,Status,Subscribed Date,Total Orders,Total Spent'];
    subscribers.forEach(sub => {
      csv.push([
        sub.email,
        sub.name || '',
        sub.status,
        new Date(sub.subscribed_at).toLocaleDateString('de-DE'),
        sub.metadata?.total_orders || 0,
        (sub.metadata?.total_spent || 0).toFixed(2)
      ].join(','));
    });
    
    const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `newsletter-subscribers-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    
    toast.success('Abonnenten exportiert');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Lade Newsletter-Daten...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b border-border">
        <div className="container-custom py-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/admin/dashboard')}
              className="p-2 hover:bg-secondary rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-serif font-semibold">📧 Newsletter & E-Mail Marketing</h1>
              <p className="text-sm text-muted-foreground">
                Verwalte Abonnenten und versende Kampagnen
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-custom py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <Users className="h-5 w-5 text-primary" />
              <span className="text-2xl font-bold">{stats?.total_subscribers || 0}</span>
            </div>
            <p className="text-sm text-muted-foreground">Gesamt Abonnenten</p>
          </div>

          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <Mail className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{stats?.active_subscribers || 0}</span>
            </div>
            <p className="text-sm text-muted-foreground">Aktive Abonnenten</p>
          </div>

          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold text-blue-600">{stats?.new_this_week || 0}</span>
            </div>
            <p className="text-sm text-muted-foreground">Neu diese Woche</p>
          </div>

          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">
                {stats?.growth_rate?.toFixed(1) || 0}%
              </span>
            </div>
            <p className="text-sm text-muted-foreground">Wachstumsrate</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => navigate('/admin/newsletter/campaigns/new')}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Neue Kampagne
          </button>
          <button
            onClick={exportSubscribers}
            className="btn-secondary flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Abonnenten exportieren
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-border">
          {[
            { id: 'overview', label: 'Übersicht' },
            { id: 'subscribers', label: 'Abonnenten' },
            { id: 'segments', label: 'Segmente' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 font-medium transition-colors border-b-2 ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">📊 Schnellübersicht</h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div className="flex justify-between py-2 border-b border-border">
                  <span className="text-muted-foreground">Aktive Abonnenten:</span>
                  <span className="font-semibold">{stats?.active_subscribers || 0}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border">
                  <span className="text-muted-foreground">Abgemeldet:</span>
                  <span className="font-semibold">{stats?.unsubscribed || 0}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border">
                  <span className="text-muted-foreground">Bounced:</span>
                  <span className="font-semibold">{stats?.bounced || 0}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border">
                  <span className="text-muted-foreground">Wachstum (7 Tage):</span>
                  <span className="font-semibold text-green-600">+{stats?.new_this_week || 0}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'subscribers' && (
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50 border-b border-border">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold">E-Mail</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Bestellungen</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Umsatz</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Segmente</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Abonniert am</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {subscribers.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-4 py-8 text-center text-muted-foreground">
                      Noch keine Abonnenten
                    </td>
                  </tr>
                ) : (
                  subscribers.slice(0, 50).map((sub) => (
                    <tr key={sub.id || sub._id} className="hover:bg-muted/30">
                      <td className="px-4 py-3 text-sm">{sub.email}</td>
                      <td className="px-4 py-3 text-sm">{sub.name || '-'}</td>
                      <td className="px-4 py-3 text-sm">{sub.metadata?.total_orders || 0}</td>
                      <td className="px-4 py-3 text-sm">€{(sub.metadata?.total_spent || 0).toFixed(2)}</td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex gap-1 flex-wrap">
                          {(sub.metadata?.segments || []).slice(0, 2).map((seg, idx) => (
                            <span key={idx} className="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full">
                              {seg}
                            </span>
                          ))}
                          {(sub.metadata?.segments || []).length > 2 && (
                            <span className="text-xs text-muted-foreground">
                              +{(sub.metadata?.segments || []).length - 2}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {new Date(sub.subscribed_at).toLocaleDateString('de-DE')}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'segments' && (
          <div className="grid md:grid-cols-3 gap-6">
            {Object.entries(segments).map(([segmentName, count]) => (
              <div key={segmentName} className="bg-card border border-border rounded-xl p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold capitalize">
                    {segmentName.replace(/_/g, ' ')}
                  </h3>
                  <span className="text-2xl font-bold text-primary">{count}</span>
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  {count} {count === 1 ? 'Abonnent' : 'Abonnenten'}
                </p>
                <button
                  onClick={() => navigate(`/admin/newsletter/campaigns/new?segment=${segmentName}`)}
                  className="btn-secondary w-full text-sm flex items-center justify-center gap-2"
                >
                  <Send className="h-4 w-4" />
                  Kampagne erstellen
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default NewsletterManagement;

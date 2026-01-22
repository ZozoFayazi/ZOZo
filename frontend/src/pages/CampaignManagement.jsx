import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, ArrowLeft, Plus, Eye, Trash2, BarChart3 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function CampaignManagement() {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('campaigns');
  const [segments, setSegments] = useState({
    all: 0,
    new_customers: 0,
    repeat_customers: 0,
    inactive: 0
  });

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await axios.get(`${API_URL}/api/admin/newsletter/campaigns`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCampaigns(response.data);
    } catch (error) {
      console.error('Error loading campaigns:', error);
      toast.error('Fehler beim Laden der Kampagnen');
    } finally {
      setLoading(false);
    }
  };

  const sendCampaign = async (campaignId) => {
    if (!confirm('Möchtest du diese Kampagne wirklich senden?')) return;

    try {
      const token = localStorage.getItem('zozoAuthToken');
      const response = await axios.post(
        `${API_URL}/api/admin/newsletter/campaigns/${campaignId}/send`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success(response.data.message || 'Kampagne gesendet');
      loadCampaigns();
    } catch (error) {
      console.error('Error sending campaign:', error);
      toast.error('Fehler beim Senden der Kampagne');
    }
  };

  const deleteCampaign = async (campaignId) => {
    if (!confirm('Kampagne wirklich löschen?')) return;

    try {
      const token = localStorage.getItem('zozoAuthToken');
      await axios.delete(
        `${API_URL}/api/admin/newsletter/campaigns/${campaignId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success('Kampagne gelöscht');
      loadCampaigns();
    } catch (error) {
      console.error('Error deleting campaign:', error);
      toast.error('Fehler beim Löschen');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      draft: { label: 'Entwurf', color: 'bg-gray-500/10 text-gray-500' },
      ready: { label: 'Bereit', color: 'bg-blue-500/10 text-blue-500' },
      sending: { label: 'Wird gesendet', color: 'bg-orange-500/10 text-orange-500' },
      sent: { label: 'Gesendet', color: 'bg-green-500/10 text-green-500' },
      failed: { label: 'Fehlgeschlagen', color: 'bg-red-500/10 text-red-500' }
    };
    return badges[status] || badges.draft;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b border-border">
        <div className="container-custom py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/admin/newsletter')}
                className="p-2 hover:bg-secondary rounded-lg transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-2xl font-serif font-semibold">🚀 E-Mail Kampagnen</h1>
                <p className="text-sm text-muted-foreground">
                  {campaigns.length} {campaigns.length === 1 ? 'Kampagne' : 'Kampagnen'}
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/admin/newsletter/campaigns/new')}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Neue Kampagne
            </button>
          </div>
        </div>
      </div>

      <div className="container-custom py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : campaigns.length === 0 ? (
          <div className="bg-card border border-border rounded-xl p-12 text-center">
            <Send className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Noch keine Kampagnen</h3>
            <p className="text-muted-foreground mb-4">
              Erstelle deine erste E-Mail-Kampagne
            </p>
            <button
              onClick={() => navigate('/admin/newsletter/campaigns/new')}
              className="btn-primary"
            >
              Erste Kampagne erstellen
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {campaigns.map((campaign) => {
              const statusBadge = getStatusBadge(campaign.status);
              const stats = campaign.stats || {};
              const openRate = stats.sent > 0 ? ((stats.opened / stats.sent) * 100).toFixed(1) : 0;
              const clickRate = stats.sent > 0 ? ((stats.clicked / stats.sent) * 100).toFixed(1) : 0;

              return (
                <div
                  key={campaign.id || campaign._id}
                  className="bg-card border border-border rounded-xl p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold">{campaign.title}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusBadge.color}`}>
                          {statusBadge.label}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        Betreff: {campaign.subject}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Erstellt: {new Date(campaign.created_at).toLocaleString('de-DE')}
                        {campaign.segment && ` • Segment: ${campaign.segment}`}
                      </p>
                    </div>
                    
                    <div className="flex gap-2">
                      {campaign.status === 'ready' && (
                        <button
                          onClick={() => sendCampaign(campaign.id || campaign._id)}
                          className="btn-primary text-sm flex items-center gap-2"
                        >
                          <Send className="h-4 w-4" />
                          Senden
                        </button>
                      )}
                      <button
                        onClick={() => navigate(`/admin/newsletter/campaigns/${campaign.id || campaign._id}`)}
                        className="btn-secondary text-sm p-2"
                        title="Ansehen"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      {campaign.status === 'draft' && (
                        <button
                          onClick={() => deleteCampaign(campaign.id || campaign._id)}
                          className="btn-secondary text-sm p-2 hover:text-red-600"
                          title="Löschen"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Campaign Stats */}
                  {campaign.status === 'sent' && (
                    <div className="grid grid-cols-5 gap-4 pt-4 border-t border-border">
                      <div className="text-center">
                        <div className="text-2xl font-bold">{stats.sent || 0}</div>
                        <div className="text-xs text-muted-foreground">Versendet</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{stats.opened || 0}</div>
                        <div className="text-xs text-muted-foreground">Geöffnet ({openRate}%)</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{stats.clicked || 0}</div>
                        <div className="text-xs text-muted-foreground">Geklickt ({clickRate}%)</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">{stats.bounced || 0}</div>
                        <div className="text-xs text-muted-foreground">Bounced</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">{stats.unsubscribed || 0}</div>
                        <div className="text-xs text-muted-foreground">Abgemeldet</div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {activeTab === 'segments' && (
          <div className="grid md:grid-cols-3 gap-6">
            {Object.entries(segments).map(([segmentName, count]) => (
              <div key={segmentName} className="bg-card border border-border rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-2 capitalize">
                  {segmentName.replace(/_/g, ' ')}
                </h3>
                <p className="text-3xl font-bold text-primary mb-4">{count}</p>
                <button
                  onClick={() => navigate(`/admin/newsletter/campaigns/new?segment=${segmentName}`)}
                  className="btn-primary w-full text-sm"
                >
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

export default CampaignManagement;

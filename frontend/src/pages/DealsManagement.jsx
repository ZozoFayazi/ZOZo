import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Edit, Trash2, Tag } from 'lucide-react';
import { toast } from 'sonner';
import { getAdminDeals, createDeal, updateDeal, deleteDeal } from '../api';

function DealsManagement() {
  const navigate = useNavigate();
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingDeal, setEditingDeal] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    discount_type: 'percentage',
    discount_value: 0,
    min_order_value: 0,
    image_url: ''
  });

  useEffect(() => {
    loadDeals();
  }, []);

  const loadDeals = async () => {
    setLoading(true);
    try {
      const data = await getAdminDeals();
      setDeals(data);
    } catch (error) {
      console.error('Error loading deals:', error);
      toast.error('Fehler beim Laden der Deals');
      if (error.response?.status === 401) {
        navigate('/admin');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (editingDeal) {
        await updateDeal(editingDeal.id, formData);
        toast.success('Deal aktualisiert');
      } else {
        await createDeal(formData);
        toast.success('Deal erstellt');
      }
      
      setShowForm(false);
      setEditingDeal(null);
      setFormData({
        title: '',
        description: '',
        discount_type: 'percentage',
        discount_value: 0,
        min_order_value: 0,
        image_url: ''
      });
      loadDeals();
    } catch (error) {
      console.error('Error saving deal:', error);
      toast.error('Fehler beim Speichern');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (deal) => {
    setEditingDeal(deal);
    setFormData({
      title: deal.title,
      description: deal.description,
      discount_type: deal.discount_type,
      discount_value: deal.discount_value,
      min_order_value: deal.min_order_value || 0,
      image_url: deal.image_url || ''
    });
    setShowForm(true);
  };

  const handleDelete = async (dealId) => {
    if (!window.confirm('Deal wirklich löschen?')) return;

    try {
      await deleteDeal(dealId);
      toast.success('Deal gelöscht');
      loadDeals();
    } catch (error) {
      console.error('Error deleting deal:', error);
      toast.error('Fehler beim Löschen');
    }
  };

  if (loading && !showForm) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Lade Deals...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b border-border">
        <div className="container-custom py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/admin/dashboard')}
                className="p-2 hover:bg-secondary rounded-lg transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-2xl font-serif font-semibold">Deals & Promotions</h1>
                <p className="text-sm text-muted-foreground">Verwalte aktuelle Angebote</p>
              </div>
            </div>
            <button
              onClick={() => {
                setEditingDeal(null);
                setFormData({
                  title: '',
                  description: '',
                  discount_type: 'percentage',
                  discount_value: 0,
                  min_order_value: 0,
                  image_url: ''
                });
                setShowForm(true);
              }}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Neuer Deal
            </button>
          </div>
        </div>
      </div>

      <div className="container-custom py-8">
        {/* Form */}
        {showForm && (
          <div className="bg-card border border-border rounded-xl p-6 mb-8">
            <h2 className="text-lg font-semibold mb-4">
              {editingDeal ? 'Deal bearbeiten' : 'Neuer Deal'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Titel *</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="z.B. 20% auf alle Burger"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Rabatt-Typ *</label>
                  <select
                    value={formData.discount_type}
                    onChange={(e) => setFormData({ ...formData, discount_type: e.target.value })}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="percentage">Prozent (%)</option>
                    <option value="fixed_amount">Fester Betrag (€)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Beschreibung *</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                  rows={3}
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  placeholder="Beschreibe das Angebot..."
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Rabatt-Wert * ({formData.discount_type === 'percentage' ? '%' : '€'})
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.discount_value}
                    onChange={(e) => setFormData({ ...formData, discount_value: parseFloat(e.target.value) })}
                    required
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Mindestbestellwert (€)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.min_order_value}
                    onChange={(e) => setFormData({ ...formData, min_order_value: parseFloat(e.target.value) })}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Bild-URL (optional)</label>
                <input
                  type="url"
                  value={formData.image_url}
                  onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="https://..."
                />
              </div>

              <div className="flex gap-2">
                <button type="submit" disabled={loading} className="btn-primary disabled:opacity-50">
                  {loading ? 'Speichert...' : 'Speichern'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setEditingDeal(null);
                  }}
                  className="btn-secondary"
                >
                  Abbrechen
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Deals List */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {deals.map((deal) => (
            <div
              key={deal.id}
              className="bg-card border border-border rounded-xl overflow-hidden"
            >
              {deal.image_url && (
                <div className="aspect-video overflow-hidden">
                  <img
                    src={deal.image_url}
                    alt={deal.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <div className="p-5 space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="inline-flex items-center gap-2 px-2 py-1 rounded-full bg-primary/20 text-primary text-xs font-bold mb-2">
                      <Tag className="h-3 w-3" />
                      {deal.discount_type === 'percentage' 
                        ? `${deal.discount_value}%`
                        : `€${deal.discount_value}`}
                    </div>
                    <h3 className="font-semibold">{deal.title}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-2">{deal.description}</p>
                    {deal.min_order_value > 0 && (
                      <p className="text-xs text-muted-foreground mt-2">
                        Ab €{deal.min_order_value}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex gap-2 pt-2 border-t border-border">
                  <button
                    onClick={() => handleEdit(deal)}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-secondary hover:bg-muted rounded-lg transition-colors text-sm"
                  >
                    <Edit className="h-4 w-4" />
                    Bearbeiten
                  </button>
                  <button
                    onClick={() => handleDelete(deal.id)}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-destructive/10 hover:bg-destructive/20 text-destructive rounded-lg transition-colors text-sm"
                  >
                    <Trash2 className="h-4 w-4" />
                    Löschen
                  </button>
                </div>

                <div className={`text-xs px-2 py-1 rounded ${deal.active ? 'bg-success/10 text-success' : 'bg-muted text-muted-foreground'}`}>
                  {deal.active ? 'Aktiv' : 'Inaktiv'}
                </div>
              </div>
            </div>
          ))}
        </div>

        {deals.length === 0 && !showForm && (
          <div className="text-center py-12">
            <Tag className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <p className="text-muted-foreground">Noch keine Deals erstellt</p>
            <button
              onClick={() => setShowForm(true)}
              className="mt-4 btn-primary"
            >
              Ersten Deal erstellen
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default DealsManagement;

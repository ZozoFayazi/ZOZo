import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Plus, Edit2, Trash2, ArrowLeft, Tag, Percent, DollarSign, ShoppingBag, Truck } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function DiscountCodes() {
  const navigate = useNavigate();
  const [codes, setCodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingCode, setEditingCode] = useState(null);

  const [formData, setFormData] = useState({
    code: '',
    description: '',
    discount_type: 'percentage',
    discount_value: 10,
    min_order_value: 0,
    order_type: '',
    max_uses: '',
    valid_from: '',
    valid_until: '',
    active: true
  });

  useEffect(() => {
    const token = localStorage.getItem('zozoAuthToken');
    if (!token) {
      navigate('/admin');
      return;
    }
    loadCodes();
  }, [navigate]);

  const loadCodes = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('zozoAuthToken');
      const response = await axios.get(`${API_URL}/api/admin/discount-codes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setCodes(response.data);
    } catch (error) {
      console.error('Error loading codes:', error);
      toast.error('Fehler beim Laden der Rabattcodes');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      ...formData,
      code: formData.code.toUpperCase(),
      discount_value: parseFloat(formData.discount_value),
      min_order_value: parseFloat(formData.min_order_value) || 0,
      max_uses: formData.max_uses ? parseInt(formData.max_uses) : null,
      order_type: formData.order_type || null,
      location_ids: []
    };

    try {
      const token = localStorage.getItem('zozoAuthToken');
      if (editingCode) {
        await axios.patch(
          `${API_URL}/api/admin/discount-codes/${editingCode.id}`,
          payload,
          { headers: { 'Authorization': `Bearer ${token}` } }
        );
        toast.success('Rabattcode aktualisiert');
      } else {
        await axios.post(
          `${API_URL}/api/admin/discount-codes`,
          payload,
          { headers: { 'Authorization': `Bearer ${token}` } }
        );
        toast.success('Rabattcode erstellt');
      }
      
      setShowCreateDialog(false);
      setEditingCode(null);
      resetForm();
      loadCodes();
    } catch (error) {
      console.error('Error saving code:', error);
      toast.error(error.response?.data?.detail || 'Fehler beim Speichern');
    }
  };

  const handleEdit = (code) => {
    setEditingCode(code);
    setFormData({
      code: code.code,
      description: code.description || '',
      discount_type: code.discount_type,
      discount_value: code.discount_value,
      min_order_value: code.min_order_value || 0,
      order_type: code.order_type || '',
      max_uses: code.max_uses || '',
      valid_from: code.valid_from ? code.valid_from.split('T')[0] : '',
      valid_until: code.valid_until ? code.valid_until.split('T')[0] : '',
      active: code.active
    });
    setShowCreateDialog(true);
  };

  const handleDelete = async (codeId) => {
    if (!window.confirm('Rabattcode wirklich löschen?')) return;

    try {
      const token = localStorage.getItem('zozoAuthToken');
      await axios.delete(`${API_URL}/api/admin/discount-codes/${codeId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      toast.success('Rabattcode gelöscht');
      loadCodes();
    } catch (error) {
      console.error('Error deleting code:', error);
      toast.error('Fehler beim Löschen');
    }
  };

  const resetForm = () => {
    setFormData({
      code: '',
      description: '',
      discount_type: 'percentage',
      discount_value: 10,
      min_order_value: 0,
      order_type: '',
      max_uses: '',
      valid_from: '',
      valid_until: '',
      active: true
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Lade Rabattcodes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container-custom">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/admin/dashboard')} className="btn-secondary flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              Zurück
            </button>
            <div>
              <h1 className="heading-2">Rabattcodes</h1>
              <p className="text-muted-foreground">Verwalte Rabattcodes und Aktionen</p>
            </div>
          </div>
          <button onClick={() => { resetForm(); setEditingCode(null); setShowCreateDialog(true); }} className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Neuer Code
          </button>
        </div>

        <div className="grid gap-4">
          {codes.map(code => (
            <div key={code.id} className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="px-4 py-2 bg-primary/10 border border-primary/20 rounded-lg">
                      <span className="text-xl font-bold text-primary font-mono">{code.code}</span>
                    </div>
                    {!code.active && (
                      <span className="px-3 py-1 bg-red-500/10 text-red-500 text-xs font-semibold rounded-full">Inaktiv</span>
                    )}
                  </div>
                  {code.description && <p className="text-muted-foreground mb-4">{code.description}</p>}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground mb-1">Rabatt</p>
                      <p className="font-semibold flex items-center gap-1">
                        {code.discount_type === 'percentage' ? (
                          <><Percent className="h-4 w-4 text-primary" /> {code.discount_value}%</>
                        ) : (
                          <><DollarSign className="h-4 w-4 text-primary" /> €{code.discount_value}</>
                        )}
                      </p>
                    </div>
                    {code.min_order_value > 0 && (
                      <div>
                        <p className="text-muted-foreground mb-1">Mindestbestellwert</p>
                        <p className="font-semibold">€{code.min_order_value.toFixed(2)}</p>
                      </div>
                    )}
                    {code.order_type && (
                      <div>
                        <p className="text-muted-foreground mb-1">Typ</p>
                        <p className="font-semibold flex items-center gap-1">
                          {code.order_type === 'pickup' ? (
                            <><ShoppingBag className="h-4 w-4" /> Abholung</>
                          ) : (
                            <><Truck className="h-4 w-4" /> Lieferung</>
                          )}
                        </p>
                      </div>
                    )}
                    {code.max_uses && (
                      <div>
                        <p className="text-muted-foreground mb-1">Verwendungen</p>
                        <p className="font-semibold">{code.current_uses || 0} / {code.max_uses}</p>
                      </div>
                    )}
                    {code.valid_until && (
                      <div>
                        <p className="text-muted-foreground mb-1">Gültig bis</p>
                        <p className="font-semibold">{new Date(code.valid_until).toLocaleDateString('de-DE')}</p>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => handleEdit(code)} className="p-2 hover:bg-secondary rounded-lg transition-colors">
                    <Edit2 className="h-4 w-4" />
                  </button>
                  <button onClick={() => handleDelete(code.id)} className="p-2 hover:bg-destructive/10 hover:text-destructive rounded-lg transition-colors">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}

          {codes.length === 0 && (
            <div className="text-center py-12 bg-card border border-border rounded-xl">
              <Tag className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground">Noch keine Rabattcodes erstellt</p>
            </div>
          )}
        </div>
      </div>

      {showCreateDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
          <div className="bg-card border border-border rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-2xl font-serif font-semibold mb-6">{editingCode ? 'Code bearbeiten' : 'Neuer Rabattcode'}</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Code *</label>
                  <input type="text" value={formData.code} onChange={(e) => setFormData({...formData, code: e.target.value.toUpperCase()})} className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary" placeholder="ABHOLER10" required />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Rabatt-Typ *</label>
                  <select value={formData.discount_type} onChange={(e) => setFormData({...formData, discount_type: e.target.value})} className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary">
                    <option value="percentage">Prozent (%)</option>
                    <option value="fixed">Fix-Betrag (€)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Beschreibung</label>
                <input type="text" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary" placeholder="10% Rabatt für Abholer" />
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">{formData.discount_type === 'percentage' ? 'Prozent *' : 'Betrag (€) *'}</label>
                  <input type="number" step="0.01" value={formData.discount_value} onChange={(e) => setFormData({...formData, discount_value: e.target.value})} className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary" required />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Mindestbestellwert (€)</label>
                  <input type="number" step="0.01" value={formData.min_order_value} onChange={(e) => setFormData({...formData, min_order_value: e.target.value})} className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Max. Verwendungen</label>
                  <input type="number" value={formData.max_uses} onChange={(e) => setFormData({...formData, max_uses: e.target.value})} className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary" placeholder="Unbegrenzt" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Nur für</label>
                <select value={formData.order_type} onChange={(e) => setFormData({...formData, order_type: e.target.value})} className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">Abholung & Lieferung</option>
                  <option value="pickup">Nur Abholung</option>
                  <option value="delivery">Nur Lieferung</option>
                </select>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Gültig von</label>
                  <input type="date" value={formData.valid_from} onChange={(e) => setFormData({...formData, valid_from: e.target.value})} className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Gültig bis</label>
                  <input type="date" value={formData.valid_until} onChange={(e) => setFormData({...formData, valid_until: e.target.value})} className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" checked={formData.active} onChange={(e) => setFormData({...formData, active: e.target.checked})} className="w-4 h-4" id="active" />
                <label htmlFor="active" className="text-sm font-medium">Code ist aktiv</label>
              </div>
              <div className="flex gap-3 pt-4">
                <button type="submit" className="btn-primary flex-1">{editingCode ? 'Aktualisieren' : 'Erstellen'}</button>
                <button type="button" onClick={() => { setShowCreateDialog(false); setEditingCode(null); resetForm(); }} className="btn-secondary flex-1">Abbrechen</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default DiscountCodes;

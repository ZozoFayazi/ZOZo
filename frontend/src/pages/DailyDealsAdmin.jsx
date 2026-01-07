import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar, 
  Percent, 
  Gift, 
  Edit2, 
  Trash2, 
  Plus,
  Save,
  X,
  Check,
  AlertCircle,
  Tag,
  RefreshCw,
  ArrowLeft
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';

const WEEKDAYS = [
  { value: 0, label: 'Montag' },
  { value: 1, label: 'Dienstag' },
  { value: 2, label: 'Mittwoch' },
  { value: 3, label: 'Donnerstag' },
  { value: 4, label: 'Freitag' },
  { value: 5, label: 'Samstag' },
  { value: 6, label: 'Sonntag' },
];

const DISCOUNT_TYPES = [
  { value: 'percentage', label: 'Prozent-Rabatt', icon: Percent },
  { value: '2for1', label: '2 für 1', icon: Gift },
];

const TARGET_TYPES = [
  { value: 'category', label: 'Kategorie (z.B. Pasta, Pizza)' },
  { value: 'product', label: 'Einzelnes Produkt' },
  { value: 'size', label: 'Produkt + Größe (z.B. Hamburger Klein)' },
];

function DailyDealsAdmin() {
  const navigate = useNavigate();
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingDeal, setEditingDeal] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    weekday: 0,
    title: '',
    description: '',
    discount_type: 'percentage',
    discount_value: 20,
    target_type: 'category',
    target_value: '',
    target_size: '',
    requires_same_item: false,
    badge_text: 'Tagesangebot',
    badge_color: '#FF6B35',
    active: true,
    applies_to_all_locations: true,
  });

  useEffect(() => {
    loadDeals();
  }, []);

  const loadDeals = async () => {
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/daily-deals`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDeals(data);
      } else if (response.status === 401) {
        toast.error('Sitzung abgelaufen. Bitte erneut anmelden.');
      }
    } catch (error) {
      console.error('Error loading deals:', error);
      toast.error('Fehler beim Laden der Tagesangebote');
    } finally {
      setLoading(false);
    }
  };

  const setupDefaultDeals = async () => {
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/daily-deals/setup-defaults`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        toast.success('Standard-Tagesangebote eingerichtet!');
        loadDeals();
      } else {
        toast.error('Fehler beim Einrichten');
      }
    } catch (error) {
      console.error('Error setting up defaults:', error);
      toast.error('Fehler beim Einrichten');
    }
  };

  const openCreateDialog = (weekday = null) => {
    setEditingDeal(null);
    setFormData({
      weekday: weekday ?? 0,
      title: '',
      description: '',
      discount_type: 'percentage',
      discount_value: 20,
      target_type: 'category',
      target_value: '',
      target_size: '',
      requires_same_item: false,
      badge_text: 'Tagesangebot',
      badge_color: '#FF6B35',
      active: true,
      applies_to_all_locations: true,
    });
    setIsDialogOpen(true);
  };

  const openEditDialog = (deal) => {
    setEditingDeal(deal);
    setFormData({
      weekday: deal.weekday,
      title: deal.title || '',
      description: deal.description || '',
      discount_type: deal.discount_type || 'percentage',
      discount_value: deal.discount_value || 0,
      target_type: deal.target_type || 'category',
      target_value: deal.target_value || '',
      target_size: deal.target_size || '',
      requires_same_item: deal.requires_same_item || false,
      badge_text: deal.badge_text || 'Tagesangebot',
      badge_color: deal.badge_color || '#FF6B35',
      active: deal.active ?? true,
      applies_to_all_locations: deal.applies_to_all_locations ?? true,
    });
    setIsDialogOpen(true);
  };

  const handleSave = async () => {
    if (!formData.title || !formData.target_value) {
      toast.error('Bitte alle Pflichtfelder ausfüllen');
      return;
    }

    setSaving(true);
    try {
      const token = sessionStorage.getItem('adminToken');
      const url = editingDeal 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin/daily-deals/${editingDeal.id}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin/daily-deals`;
      
      const response = await fetch(url, {
        method: editingDeal ? 'PATCH' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success(editingDeal ? 'Tagesangebot aktualisiert!' : 'Tagesangebot erstellt!');
        setIsDialogOpen(false);
        loadDeals();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fehler beim Speichern');
      }
    } catch (error) {
      console.error('Error saving deal:', error);
      toast.error('Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (dealId) => {
    if (!window.confirm('Tagesangebot wirklich löschen?')) return;

    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/daily-deals/${dealId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        toast.success('Tagesangebot gelöscht');
        loadDeals();
      } else {
        toast.error('Fehler beim Löschen');
      }
    } catch (error) {
      console.error('Error deleting deal:', error);
      toast.error('Fehler beim Löschen');
    }
  };

  const toggleActive = async (deal) => {
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/daily-deals/${deal.id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ active: !deal.active })
      });

      if (response.ok) {
        toast.success(deal.active ? 'Deaktiviert' : 'Aktiviert');
        loadDeals();
      }
    } catch (error) {
      console.error('Error toggling deal:', error);
    }
  };

  // Group deals by weekday for display
  const dealsByWeekday = WEEKDAYS.map(day => ({
    ...day,
    deal: deals.find(d => d.weekday === day.value)
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="daily-deals-admin">
      {/* Header with Back Button */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-4">
          {/* Back Button */}
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => navigate('/admin/dashboard')}
            className="shrink-0"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" />
              Tagesangebote
            </h1>
            <p className="text-muted-foreground">
              Verwalte die automatischen Tagesangebote für jeden Wochentag
            </p>
          </div>
        </div>
        
        <div className="flex gap-2">
          {deals.length === 0 && (
            <Button onClick={setupDefaultDeals} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Standard-Angebote einrichten
            </Button>
          )}
          <Button onClick={() => openCreateDialog()}>
            <Plus className="h-4 w-4 mr-2" />
            Neues Angebot
          </Button>
        </div>
      </div>

      {/* Info Alert */}
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Tagesangebote werden automatisch angewendet. Kunden sehen das aktuelle Angebot auf der Startseite 
          und der Rabatt wird im Warenkorb automatisch berechnet.
        </AlertDescription>
      </Alert>

      {/* Weekday Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {dealsByWeekday.map(({ value, label, deal }) => (
          <Card 
            key={value} 
            className={`transition-all ${deal?.active ? 'border-primary/50' : 'opacity-60'}`}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  {label}
                </CardTitle>
                {deal && (
                  <Switch 
                    checked={deal.active} 
                    onCheckedChange={() => toggleActive(deal)}
                  />
                )}
              </div>
            </CardHeader>
            <CardContent>
              {deal ? (
                <div className="space-y-3">
                  {/* Deal Badge */}
                  <div 
                    className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-white text-xs font-medium"
                    style={{ backgroundColor: deal.badge_color }}
                  >
                    {deal.discount_type === '2for1' ? (
                      <Gift className="h-3 w-3" />
                    ) : (
                      <Percent className="h-3 w-3" />
                    )}
                    {deal.badge_text}
                  </div>
                  
                  {/* Deal Info */}
                  <div>
                    <h4 className="font-semibold">{deal.title}</h4>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {deal.description}
                    </p>
                  </div>
                  
                  {/* Target */}
                  <div className="text-xs text-muted-foreground">
                    Ziel: <span className="font-medium">{deal.target_value}</span>
                    {deal.target_size && ` (${deal.target_size})`}
                  </div>
                  
                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={() => openEditDialog(deal)}
                      className="flex-1"
                    >
                      <Edit2 className="h-3 w-3 mr-1" />
                      Bearbeiten
                    </Button>
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      onClick={() => handleDelete(deal.id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-sm text-muted-foreground mb-3">
                    Kein Angebot für {label}
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => openCreateDialog(value)}
                  >
                    <Plus className="h-3 w-3 mr-1" />
                    Angebot erstellen
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingDeal ? 'Tagesangebot bearbeiten' : 'Neues Tagesangebot'}
            </DialogTitle>
            <DialogDescription>
              {editingDeal 
                ? `Bearbeite das Angebot für ${WEEKDAYS.find(d => d.value === formData.weekday)?.label}`
                : 'Erstelle ein neues Tagesangebot für einen Wochentag'
              }
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Weekday */}
            <div className="space-y-2">
              <Label>Wochentag *</Label>
              <Select 
                value={String(formData.weekday)} 
                onValueChange={(v) => setFormData({...formData, weekday: parseInt(v)})}
                disabled={!!editingDeal}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {WEEKDAYS.map(day => (
                    <SelectItem key={day.value} value={String(day.value)}>
                      {day.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Title */}
            <div className="space-y-2">
              <Label>Titel *</Label>
              <Input 
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                placeholder="z.B. Pasta-Montag"
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label>Beschreibung</Label>
              <Input 
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="z.B. 20% Rabatt auf alle Pasta-Gerichte"
              />
            </div>

            {/* Discount Type */}
            <div className="space-y-2">
              <Label>Rabatt-Typ *</Label>
              <Select 
                value={formData.discount_type} 
                onValueChange={(v) => setFormData({...formData, discount_type: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DISCOUNT_TYPES.map(type => (
                    <SelectItem key={type.value} value={type.value}>
                      <div className="flex items-center gap-2">
                        <type.icon className="h-4 w-4" />
                        {type.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Discount Value (nur bei percentage) */}
            {formData.discount_type === 'percentage' && (
              <div className="space-y-2">
                <Label>Rabatt in % *</Label>
                <Input 
                  type="number"
                  min="1"
                  max="100"
                  value={formData.discount_value}
                  onChange={(e) => setFormData({...formData, discount_value: parseFloat(e.target.value)})}
                />
              </div>
            )}

            {/* Requires Same Item (nur bei 2for1) */}
            {formData.discount_type === '2for1' && (
              <div className="flex items-center justify-between">
                <div>
                  <Label>Gleiche Produkte erforderlich</Label>
                  <p className="text-xs text-muted-foreground">
                    Für 2-für-1 müssen 2 gleiche Produkte bestellt werden
                  </p>
                </div>
                <Switch 
                  checked={formData.requires_same_item}
                  onCheckedChange={(v) => setFormData({...formData, requires_same_item: v})}
                />
              </div>
            )}

            {/* Target Type */}
            <div className="space-y-2">
              <Label>Ziel-Typ *</Label>
              <Select 
                value={formData.target_type} 
                onValueChange={(v) => setFormData({...formData, target_type: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TARGET_TYPES.map(type => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Target Value */}
            <div className="space-y-2">
              <Label>Ziel-Wert *</Label>
              <Input 
                value={formData.target_value}
                onChange={(e) => setFormData({...formData, target_value: e.target.value})}
                placeholder={
                  formData.target_type === 'category' 
                    ? 'z.B. pasta, pizza, wraps' 
                    : formData.target_type === 'size'
                    ? 'z.B. hamburger'
                    : 'Produkt-ID oder Name'
                }
              />
              <p className="text-xs text-muted-foreground">
                {formData.target_type === 'category' && 'Kategorie-Slug (kleingeschrieben)'}
                {formData.target_type === 'product' && 'Produkt-ID oder Teil des Namens'}
                {formData.target_type === 'size' && 'Produkt-Name (z.B. hamburger)'}
              </p>
            </div>

            {/* Target Size (nur bei size) */}
            {formData.target_type === 'size' && (
              <div className="space-y-2">
                <Label>Größe *</Label>
                <Input 
                  value={formData.target_size}
                  onChange={(e) => setFormData({...formData, target_size: e.target.value})}
                  placeholder="z.B. klein, medium, groß"
                />
              </div>
            )}

            {/* Badge Text */}
            <div className="space-y-2">
              <Label>Badge-Text</Label>
              <Input 
                value={formData.badge_text}
                onChange={(e) => setFormData({...formData, badge_text: e.target.value})}
                placeholder="z.B. 🍝 -20%"
              />
            </div>

            {/* Badge Color */}
            <div className="space-y-2">
              <Label>Badge-Farbe</Label>
              <div className="flex gap-2">
                <Input 
                  type="color"
                  value={formData.badge_color}
                  onChange={(e) => setFormData({...formData, badge_color: e.target.value})}
                  className="w-16 h-10 p-1"
                />
                <Input 
                  value={formData.badge_color}
                  onChange={(e) => setFormData({...formData, badge_color: e.target.value})}
                  placeholder="#FF6B35"
                  className="flex-1"
                />
              </div>
            </div>

            {/* Active */}
            <div className="flex items-center justify-between">
              <Label>Aktiv</Label>
              <Switch 
                checked={formData.active}
                onCheckedChange={(v) => setFormData({...formData, active: v})}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              <X className="h-4 w-4 mr-2" />
              Abbrechen
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default DailyDealsAdmin;

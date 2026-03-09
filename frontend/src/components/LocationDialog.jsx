import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Switch } from './ui/switch';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { Loader2, X, Plus } from 'lucide-react';

const DAYS = [
  { value: 'monday', label: 'Montag' },
  { value: 'tuesday', label: 'Dienstag' },
  { value: 'wednesday', label: 'Mittwoch' },
  { value: 'thursday', label: 'Donnerstag' },
  { value: 'friday', label: 'Freitag' },
  { value: 'saturday', label: 'Samstag' },
  { value: 'sunday', label: 'Sonntag' }
];

export default function LocationDialog({ open, onClose, location, onSuccess }) {
  const { token, isSuperAdmin } = useAdminAuth();
  const isEdit = !!location;
  const [loading, setLoading] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    address: '',
    city: '',
    postal_code: '',
    lat: 0,
    lng: 0,
    phone: '',
    email: '',
    google_review_url: '',
    is_active: true,
    seo: {
      meta_title: '',
      meta_description: '',
      keywords: ''
    }
  });
  
  const [openingHours, setOpeningHours] = useState(
    DAYS.map(day => ({
      day: day.value,
      is_open: true,
      open_time: '11:00',
      close_time: '22:45'
    }))
  );
  
  const [deliveryArea, setDeliveryArea] = useState({
    mode: 'radius',
    radius_km: 5.0,
    postal_codes: [],
    delivery_fee: 0.0,
    min_order_value: 15.0,
    estimated_delivery_time: '30-45 Min'
  });
  
  const [postalCodeInput, setPostalCodeInput] = useState('');
  
  // Load location data when editing
  useEffect(() => {
    if (location) {
      setFormData({
        name: location.name || '',
        slug: location.slug || '',
        address: location.address || '',
        city: location.city || '',
        postal_code: location.postal_code || '',
        lat: location.lat || 0,
        lng: location.lng || 0,
        phone: location.phone || '',
        email: location.email || '',
        google_review_url: location.google_review_url || '',
        is_active: location.is_active ?? true,
        seo: location.seo || { meta_title: '', meta_description: '', keywords: '' }
      });
      
      if (location.opening_hours && location.opening_hours.length > 0) {
        setOpeningHours(location.opening_hours);
      }
      
      if (location.delivery_area) {
        setDeliveryArea({
          mode: location.delivery_area.mode || 'radius',
          radius_km: location.delivery_area.radius_km || 5.0,
          postal_codes: location.delivery_area.postal_codes || [],
          delivery_fee: location.delivery_area.delivery_fee || 0.0,
          min_order_value: location.delivery_area.min_order_value || 15.0,
          estimated_delivery_time: location.delivery_area.estimated_delivery_time || '30-45 Min'
        });
      }
    }
  }, [location]);
  
  const handleSubmit = async () => {
    // Validation
    if (!formData.name || !formData.slug || !formData.address || !formData.city) {
      toast.error('Bitte füllen Sie alle Pflichtfelder aus');
      return;
    }
    
    setLoading(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const payload = {
        ...formData,
        opening_hours: openingHours,
        delivery_area: deliveryArea
      };
      
      const url = isEdit 
        ? `${backendUrl}/api/admin/locations/${location.slug}`
        : `${backendUrl}/api/admin/locations`;
      
      const method = isEdit ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Speichern');
      }
      
      const result = await response.json();
      toast.success(isEdit ? 'Filiale aktualisiert' : 'Filiale erstellt');
      onSuccess(result);
      onClose();
    } catch (error) {
      console.error('Save location error:', error);
      toast.error(error.message || 'Fehler beim Speichern');
    } finally {
      setLoading(false);
    }
  };
  
  const addPostalCode = () => {
    if (postalCodeInput && !deliveryArea.postal_codes.includes(postalCodeInput)) {
      setDeliveryArea(prev => ({
        ...prev,
        postal_codes: [...prev.postal_codes, postalCodeInput]
      }));
      setPostalCodeInput('');
    }
  };
  
  const removePostalCode = (code) => {
    setDeliveryArea(prev => ({
      ...prev,
      postal_codes: prev.postal_codes.filter(c => c !== code)
    }));
  };
  
  const canEditField = (field) => {
    if (isSuperAdmin()) return true;
    const allowedFields = ['phone', 'email', 'opening_hours', 'delivery_area'];
    return allowedFields.includes(field);
  };
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto" data-testid="location-dialog">
        <DialogHeader>
          <DialogTitle>
            {isEdit ? 'Filiale bearbeiten' : 'Neue Filiale erstellen'}
          </DialogTitle>
          <DialogDescription>
            {isEdit ? 'Ändern Sie die Einstellungen Ihrer Filiale' : 'Erstellen Sie eine neue ZOZO Burger Filiale'}
          </DialogDescription>
        </DialogHeader>
        
        <Tabs defaultValue="details" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="hours">Öffnungszeiten</TabsTrigger>
            <TabsTrigger value="delivery">Liefergebiet</TabsTrigger>
            <TabsTrigger value="seo">SEO</TabsTrigger>
          </TabsList>
          
          {/* Tab 1: Details */}
          <TabsContent value="details" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  disabled={isEdit && !canEditField('name')}
                  data-testid="location-name"
                />
                {isEdit && !canEditField('name') && (
                  <p className="text-xs text-muted-foreground">Nur Super Admin kann dieses Feld ändern</p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="slug">Slug *</Label>
                <Input
                  id="slug"
                  value={formData.slug}
                  onChange={(e) => setFormData(prev => ({ ...prev, slug: e.target.value }))}
                  disabled={isEdit && !canEditField('slug')}
                  placeholder="rellingen"
                  data-testid="location-slug"
                />
                {isEdit && !canEditField('slug') && (
                  <p className="text-xs text-muted-foreground">Nur Super Admin kann dieses Feld ändern</p>
                )}
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="address">Adresse *</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
                  disabled={isEdit && !canEditField('address')}
                  data-testid="location-address"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="city">Stadt *</Label>
                <Input
                  id="city"
                  value={formData.city}
                  onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                  disabled={isEdit && !canEditField('city')}
                  data-testid="location-city"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="postal_code">PLZ</Label>
                <Input
                  id="postal_code"
                  value={formData.postal_code}
                  onChange={(e) => setFormData(prev => ({ ...prev, postal_code: e.target.value }))}
                  disabled={isEdit && !canEditField('postal_code')}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="phone">Telefon</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                  data-testid="location-phone"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">E-Mail</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                data-testid="location-email"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="google_review_url">Google Review URL</Label>
              <Input
                id="google_review_url"
                value={formData.google_review_url}
                onChange={(e) => setFormData(prev => ({ ...prev, google_review_url: e.target.value }))}
                disabled={isEdit && !canEditField('google_review_url')}
              />
            </div>
            
            {isSuperAdmin() && (
              <div className="flex items-center space-x-2">
                <Switch
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_active: checked }))}
                  data-testid="location-active"
                />
                <Label htmlFor="is_active">Filiale aktiv</Label>
              </div>
            )}
          </TabsContent>
          
          {/* Tab 2: Öffnungszeiten */}
          <TabsContent value="hours" className="space-y-4">
            <div className="space-y-2">
              {DAYS.map((day, index) => (
                <div key={day.value} className="flex items-center gap-4 p-3 border rounded-lg">
                  <div className="w-32">
                    <span className="font-medium">{day.label}</span>
                  </div>
                  <Switch
                    checked={openingHours[index].is_open}
                    onCheckedChange={(checked) => {
                      const newHours = [...openingHours];
                      newHours[index].is_open = checked;
                      setOpeningHours(newHours);
                    }}
                    data-testid={`hours-${day.value}-open`}
                  />
                  {openingHours[index].is_open ? (
                    <>
                      <Input
                        type="time"
                        value={openingHours[index].open_time}
                        onChange={(e) => {
                          const newHours = [...openingHours];
                          newHours[index].open_time = e.target.value;
                          setOpeningHours(newHours);
                        }}
                        className="w-32"
                        data-testid={`hours-${day.value}-start`}
                      />
                      <span>bis</span>
                      <Input
                        type="time"
                        value={openingHours[index].close_time}
                        onChange={(e) => {
                          const newHours = [...openingHours];
                          newHours[index].close_time = e.target.value;
                          setOpeningHours(newHours);
                        }}
                        className="w-32"
                        data-testid={`hours-${day.value}-end`}
                      />
                    </>
                  ) : (
                    <span className="text-muted-foreground">Geschlossen</span>
                  )}
                </div>
              ))}
            </div>
          </TabsContent>
          
          {/* Tab 3: Liefergebiet */}
          <TabsContent value="delivery" className="space-y-4">
            <div className="space-y-4">
              <div className="flex gap-4">
                <Button
                  type="button"
                  variant={deliveryArea.mode === 'radius' ? 'default' : 'outline'}
                  onClick={() => setDeliveryArea(prev => ({ ...prev, mode: 'radius' }))}
                  data-testid="delivery-mode-radius"
                >
                  Radius
                </Button>
                <Button
                  type="button"
                  variant={deliveryArea.mode === 'postal_codes' ? 'default' : 'outline'}
                  onClick={() => setDeliveryArea(prev => ({ ...prev, mode: 'postal_codes' }))}
                  data-testid="delivery-mode-plz"
                >
                  PLZ-Liste
                </Button>
              </div>
              
              {deliveryArea.mode === 'radius' ? (
                <div className="space-y-2">
                  <Label htmlFor="radius">Lieferradius (km)</Label>
                  <Input
                    id="radius"
                    type="number"
                    step="0.1"
                    value={deliveryArea.radius_km}
                    onChange={(e) => setDeliveryArea(prev => ({ ...prev, radius_km: parseFloat(e.target.value) }))}
                    data-testid="delivery-radius"
                  />
                </div>
              ) : (
                <div className="space-y-2">
                  <Label>Postleitzahlen</Label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="z.B. 25462"
                      value={postalCodeInput}
                      onChange={(e) => setPostalCodeInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addPostalCode())}
                      data-testid="delivery-plz-input"
                    />
                    <Button type="button" onClick={addPostalCode} data-testid="delivery-plz-add">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {deliveryArea.postal_codes.map(code => (
                      <Badge key={code} variant="secondary" className="flex items-center gap-1">
                        {code}
                        <X
                          className="h-3 w-3 cursor-pointer"
                          onClick={() => removePostalCode(code)}
                        />
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="delivery_fee">Liefergebühr (€)</Label>
                  <Input
                    id="delivery_fee"
                    type="number"
                    step="0.1"
                    value={deliveryArea.delivery_fee}
                    onChange={(e) => setDeliveryArea(prev => ({ ...prev, delivery_fee: parseFloat(e.target.value) }))}
                    data-testid="delivery-fee"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="min_order">Mindestbestellwert (€)</Label>
                  <Input
                    id="min_order"
                    type="number"
                    step="0.1"
                    value={deliveryArea.min_order_value}
                    onChange={(e) => setDeliveryArea(prev => ({ ...prev, min_order_value: parseFloat(e.target.value) }))}
                    data-testid="delivery-min-order"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="delivery_time">Geschätzte Lieferzeit</Label>
                <Input
                  id="delivery_time"
                  value={deliveryArea.estimated_delivery_time}
                  onChange={(e) => setDeliveryArea(prev => ({ ...prev, estimated_delivery_time: e.target.value }))}
                  placeholder="30-45 Min"
                  data-testid="delivery-time"
                />
              </div>
            </div>
          </TabsContent>
          
          {/* Tab 4: SEO */}
          <TabsContent value="seo" className="space-y-4">
            {isSuperAdmin() ? (
              <>
                <div className="space-y-2">
                  <Label htmlFor="meta_title">Meta Title</Label>
                  <Input
                    id="meta_title"
                    value={formData.seo.meta_title}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      seo: { ...prev.seo, meta_title: e.target.value }
                    }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="meta_description">Meta Description</Label>
                  <Input
                    id="meta_description"
                    value={formData.seo.meta_description}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      seo: { ...prev.seo, meta_description: e.target.value }
                    }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="keywords">Keywords</Label>
                  <Input
                    id="keywords"
                    value={formData.seo.keywords}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      seo: { ...prev.seo, keywords: e.target.value }
                    }))}
                  />
                </div>
              </>
            ) : (
              <p className="text-muted-foreground">Nur Super Admin kann SEO-Einstellungen bearbeiten.</p>
            )}
          </TabsContent>
        </Tabs>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Abbrechen
          </Button>
          <Button onClick={handleSubmit} disabled={loading} data-testid="location-save">
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isEdit ? 'Speichern' : 'Erstellen'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Save, Plus, X } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function LocationSettings() {
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);
  const [postalCodeInput, setPostalCodeInput] = useState('');

  useEffect(() => {
    loadLocationSettings();
  }, []);

  const loadLocationSettings = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('zozoAuthToken');
      const response = await axios.get(`${API_URL}/api/admin/location-settings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLocations(response.data);
    } catch (error) {
      console.error('Error loading settings:', error);
      toast.error('Fehler beim Laden der Einstellungen');
      if (error.response?.status === 401) {
        navigate('/admin');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (locationId) => {
    setSaving(true);
    try {
      const location = locations.find(l => l.id === locationId);
      const token = localStorage.getItem('zozoAuthToken');
      
      await axios.patch(
        `${API_URL}/api/admin/location-settings/${locationId}`,
        {
          postal_codes: location.delivery_zone.postal_codes,
          min_order_value: parseFloat(location.delivery_zone.min_order_value),
          delivery_fee: parseFloat(location.delivery_zone.delivery_fee),
          free_delivery_threshold: parseFloat(location.delivery_zone.free_delivery_threshold)
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      toast.success('Einstellungen gespeichert');
      setEditingLocation(null);
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  const handleFieldChange = (locationId, field, value) => {
    setLocations(locations.map(loc => {
      if (loc.id === locationId) {
        return {
          ...loc,
          delivery_zone: {
            ...loc.delivery_zone,
            [field]: value
          }
        };
      }
      return loc;
    }));
  };

  const addPostalCode = (locationId) => {
    if (!postalCodeInput.trim() || postalCodeInput.length !== 5) {
      toast.error('Bitte gültige 5-stellige PLZ eingeben');
      return;
    }

    setLocations(locations.map(loc => {
      if (loc.id === locationId) {
        const currentCodes = loc.delivery_zone?.postal_codes || [];
        if (currentCodes.includes(postalCodeInput)) {
          toast.error('PLZ bereits vorhanden');
          return loc;
        }
        return {
          ...loc,
          delivery_zone: {
            ...loc.delivery_zone,
            postal_codes: [...currentCodes, postalCodeInput]
          }
        };
      }
      return loc;
    }));
    
    setPostalCodeInput('');
    toast.success('PLZ hinzugefügt');
  };

  const removePostalCode = (locationId, code) => {
    setLocations(locations.map(loc => {
      if (loc.id === locationId) {
        return {
          ...loc,
          delivery_zone: {
            ...loc.delivery_zone,
            postal_codes: loc.delivery_zone.postal_codes.filter(c => c !== code)
          }
        };
      }
      return loc;
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Lade Einstellungen...</p>
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
              <h1 className="text-2xl font-serif font-semibold">Standort-Einstellungen</h1>
              <p className="text-sm text-muted-foreground">
                Verwalte Liefergebiete und Gebühren
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-custom py-8">
        <div className="space-y-8">
          {locations.map((location) => (
            <div
              key={location.id}
              className="bg-card border border-border rounded-xl overflow-hidden"
            >
              {/* Location Header */}
              <div className="p-6 border-b border-border bg-muted/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <MapPin className="h-6 w-6 text-primary" />
                    <div>
                      <h2 className="text-xl font-semibold">{location.name}</h2>
                      <p className="text-sm text-muted-foreground">
                        {location.address}, {location.city}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setEditingLocation(editingLocation === location.id ? null : location.id)}
                    className="btn-secondary px-4 py-2 text-sm"
                  >
                    {editingLocation === location.id ? 'Ansicht' : 'Bearbeiten'}
                  </button>
                </div>
              </div>

              {/* Settings Content */}
              <div className="p-6 space-y-6">
                {/* Delivery Fees */}
                <div className="grid md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Mindestbestellwert (€)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={location.delivery_zone?.min_order_value || 0}
                      onChange={(e) => handleFieldChange(location.id, 'min_order_value', e.target.value)}
                      disabled={editingLocation !== location.id}
                      className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Liefergebühr (€)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={location.delivery_zone?.delivery_fee || 0}
                      onChange={(e) => handleFieldChange(location.id, 'delivery_fee', e.target.value)}
                      disabled={editingLocation !== location.id}
                      className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Kostenlose Lieferung ab (€)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={location.delivery_zone?.free_delivery_threshold || 0}
                      onChange={(e) => handleFieldChange(location.id, 'free_delivery_threshold', e.target.value)}
                      disabled={editingLocation !== location.id}
                      className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                    />
                  </div>
                </div>

                {/* Postal Codes */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Liefergebiete (Postleitzahlen)
                  </label>
                  
                  {editingLocation === location.id && (
                    <div className="flex gap-2 mb-4">
                      <input
                        type="text"
                        maxLength={5}
                        placeholder="PLZ hinzufügen"
                        value={postalCodeInput}
                        onChange={(e) => setPostalCodeInput(e.target.value.replace(/\D/g, ''))}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            addPostalCode(location.id);
                          }
                        }}
                        className="flex-1 px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                      <button
                        onClick={() => addPostalCode(location.id)}
                        className="btn-primary px-4 py-2"
                      >
                        <Plus className="h-5 w-5" />
                      </button>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2">
                    {(location.delivery_zone?.postal_codes || []).map((code) => (
                      <div
                        key={code}
                        className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 border border-primary/20 rounded-full text-sm"
                      >
                        <span className="font-medium">{code}</span>
                        {editingLocation === location.id && (
                          <button
                            onClick={() => removePostalCode(location.id, code)}
                            className="hover:text-destructive transition-colors"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Save Button */}
                {editingLocation === location.id && (
                  <div className="pt-4 border-t border-border">
                    <button
                      onClick={() => handleSave(location.id)}
                      disabled={saving}
                      className="btn-primary flex items-center gap-2 disabled:opacity-50"
                    >
                      <Save className="h-4 w-4" />
                      {saving ? 'Speichert...' : 'Änderungen speichern'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default LocationSettings;

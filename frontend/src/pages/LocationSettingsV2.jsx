import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Save, Plus, X, Edit2, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function LocationSettingsV2() {
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);
  
  // PLZ Form State
  const [plzForm, setPlzForm] = useState({
    postalCode: '',
    minOrderValue: '',
    deliveryFee: ''
  });
  
  const [editingPLZ, setEditingPLZ] = useState(null);

  useEffect(() => {
    loadLocationSettings();
  }, []);

  const loadLocationSettings = async () => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('adminToken');
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
      const token = sessionStorage.getItem('adminToken');
      
      // Prepare postal_code_settings as object: {"24558": {mbw: 15, fee: 3}, ...}
      const postalCodeSettings = {};
      const postalCodes = location.delivery_zone?.postal_codes || [];
      const postalCodeMBW = location.delivery_zone?.postal_code_mbw || {};
      
      postalCodes.forEach(plz => {
        postalCodeSettings[plz] = postalCodeMBW[plz] || {
          mbw: location.delivery_zone?.default_min_order_value || 0,
          fee: location.delivery_zone?.delivery_fee || 0
        };
      });
      
      await axios.patch(
        `${API_URL}/api/admin/location-settings/${locationId}`,
        {
          postal_codes: postalCodes,
          postal_code_settings: postalCodeSettings,
          default_min_order_value: parseFloat(location.delivery_zone?.default_min_order_value || 0),
          delivery_fee: parseFloat(location.delivery_zone?.delivery_fee || 0),
          free_delivery_threshold: parseFloat(location.delivery_zone?.free_delivery_threshold || 0)
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      toast.success('Einstellungen gespeichert');
      setEditingLocation(null);
      setEditingPLZ(null);
      setPlzForm({ postalCode: '', minOrderValue: '', deliveryFee: '' });
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  const handleDefaultFieldChange = (locationId, field, value) => {
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

  const addOrUpdatePLZ = (locationId) => {
    if (!plzForm.postalCode.trim() || plzForm.postalCode.length !== 5) {
      toast.error('Bitte gültige 5-stellige PLZ eingeben');
      return;
    }
    
    if (!plzForm.minOrderValue || !plzForm.deliveryFee) {
      toast.error('Bitte MBW und Lieferkosten eingeben');
      return;
    }

    setLocations(locations.map(loc => {
      if (loc.id === locationId) {
        const currentCodes = loc.delivery_zone?.postal_codes || [];
        const currentMBW = loc.delivery_zone?.postal_code_mbw || {};
        
        // Add PLZ to list if not exists
        const newCodes = currentCodes.includes(plzForm.postalCode) 
          ? currentCodes 
          : [...currentCodes, plzForm.postalCode];
        
        // Add or update MBW/Fee for this PLZ
        const newMBW = {
          ...currentMBW,
          [plzForm.postalCode]: {
            mbw: parseFloat(plzForm.minOrderValue),
            fee: parseFloat(plzForm.deliveryFee)
          }
        };
        
        return {
          ...loc,
          delivery_zone: {
            ...loc.delivery_zone,
            postal_codes: newCodes,
            postal_code_mbw: newMBW
          }
        };
      }
      return loc;
    }));
    
    setPlzForm({ postalCode: '', minOrderValue: '', deliveryFee: '' });
    setEditingPLZ(null);
    toast.success(editingPLZ ? 'PLZ aktualisiert' : 'PLZ hinzugefügt');
  };

  const removePLZ = (locationId, code) => {
    setLocations(locations.map(loc => {
      if (loc.id === locationId) {
        const newMBW = { ...loc.delivery_zone?.postal_code_mbw };
        delete newMBW[code];
        
        return {
          ...loc,
          delivery_zone: {
            ...loc.delivery_zone,
            postal_codes: loc.delivery_zone.postal_codes.filter(c => c !== code),
            postal_code_mbw: newMBW
          }
        };
      }
      return loc;
    }));
    toast.success('PLZ entfernt');
  };

  const startEditPLZ = (locationId, plz) => {
    const location = locations.find(l => l.id === locationId);
    const plzSettings = location?.delivery_zone?.postal_code_mbw?.[plz] || {
      mbw: location?.delivery_zone?.default_min_order_value || 0,
      fee: location?.delivery_zone?.delivery_fee || 0
    };
    
    setPlzForm({
      postalCode: plz,
      minOrderValue: plzSettings.mbw.toString(),
      deliveryFee: plzSettings.fee.toString()
    });
    setEditingPLZ(plz);
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
                Verwalte Liefergebiete mit individuellen Mindestbestellwerten
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
                    onClick={() => {
                      if (editingLocation === location.id) {
                        setEditingLocation(null);
                        setPlzForm({ postalCode: '', minOrderValue: '', deliveryFee: '' });
                        setEditingPLZ(null);
                      } else {
                        setEditingLocation(location.id);
                      }
                    }}
                    className="btn-secondary px-4 py-2 text-sm"
                  >
                    {editingLocation === location.id ? 'Ansicht' : 'Bearbeiten'}
                  </button>
                </div>
              </div>

              {/* Settings Content */}
              <div className="p-6 space-y-6">
                {/* Default Settings */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Standard-Einstellungen</h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Standard-MBW (€)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={location.delivery_zone?.default_min_order_value || 0}
                        onChange={(e) => handleDefaultFieldChange(location.id, 'default_min_order_value', e.target.value)}
                        disabled={editingLocation !== location.id}
                        className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Standard-Liefergebühr (€)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={location.delivery_zone?.delivery_fee || 0}
                        onChange={(e) => handleDefaultFieldChange(location.id, 'delivery_fee', e.target.value)}
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
                        onChange={(e) => handleDefaultFieldChange(location.id, 'free_delivery_threshold', e.target.value)}
                        disabled={editingLocation !== location.id}
                        className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                      />
                    </div>
                  </div>
                </div>

                {/* PLZ Management */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">PLZ-Verwaltung</h3>
                  
                  {/* PLZ Add Form */}
                  {editingLocation === location.id && (
                    <div className="bg-muted/30 border border-border rounded-lg p-4 mb-4">
                      <div className="grid md:grid-cols-4 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">PLZ</label>
                          <input
                            type="text"
                            maxLength={5}
                            placeholder="24558"
                            value={plzForm.postalCode}
                            onChange={(e) => setPlzForm({...plzForm, postalCode: e.target.value.replace(/\D/g, '')})}
                            disabled={editingPLZ !== null}
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">MBW (€)</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="15.00"
                            value={plzForm.minOrderValue}
                            onChange={(e) => setPlzForm({...plzForm, minOrderValue: e.target.value})}
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Lieferkosten (€)</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="3.00"
                            value={plzForm.deliveryFee}
                            onChange={(e) => setPlzForm({...plzForm, deliveryFee: e.target.value})}
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                          />
                        </div>
                        <div className="flex items-end gap-2">
                          <button
                            onClick={() => addOrUpdatePLZ(location.id)}
                            className="flex-1 btn-primary px-4 py-2 flex items-center justify-center gap-2"
                          >
                            <Plus className="h-4 w-4" />
                            {editingPLZ ? 'Aktualisieren' : 'Hinzufügen'}
                          </button>
                          {editingPLZ && (
                            <button
                              onClick={() => {
                                setEditingPLZ(null);
                                setPlzForm({ postalCode: '', minOrderValue: '', deliveryFee: '' });
                              }}
                              className="btn-secondary px-4 py-2"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* PLZ Table */}
                  <div className="border border-border rounded-lg overflow-hidden">
                    <table className="w-full">
                      <thead className="bg-muted/50">
                        <tr>
                          <th className="px-4 py-3 text-left text-sm font-semibold">PLZ</th>
                          <th className="px-4 py-3 text-left text-sm font-semibold">Mindestbestellwert</th>
                          <th className="px-4 py-3 text-left text-sm font-semibold">Lieferkosten</th>
                          {editingLocation === location.id && (
                            <th className="px-4 py-3 text-right text-sm font-semibold">Aktionen</th>
                          )}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {(location.delivery_zone?.postal_codes || []).length === 0 ? (
                          <tr>
                            <td colSpan="4" className="px-4 py-8 text-center text-muted-foreground">
                              Keine PLZ konfiguriert. Füge eine hinzu!
                            </td>
                          </tr>
                        ) : (
                          (location.delivery_zone?.postal_codes || []).map((plz) => {
                            const plzSettings = location.delivery_zone?.postal_code_mbw?.[plz] || {
                              mbw: location.delivery_zone?.default_min_order_value || 0,
                              fee: location.delivery_zone?.delivery_fee || 0
                            };
                            
                            return (
                              <tr key={plz} className="hover:bg-muted/30 transition-colors">
                                <td className="px-4 py-3 font-medium">{plz}</td>
                                <td className="px-4 py-3">€{plzSettings.mbw?.toFixed(2) || '0.00'}</td>
                                <td className="px-4 py-3">€{plzSettings.fee?.toFixed(2) || '0.00'}</td>
                                {editingLocation === location.id && (
                                  <td className="px-4 py-3 text-right">
                                    <div className="flex items-center justify-end gap-2">
                                      <button
                                        onClick={() => startEditPLZ(location.id, plz)}
                                        className="p-2 hover:bg-secondary rounded-lg transition-colors"
                                        title="Bearbeiten"
                                      >
                                        <Edit2 className="h-4 w-4" />
                                      </button>
                                      <button
                                        onClick={() => removePLZ(location.id, plz)}
                                        className="p-2 hover:bg-destructive/10 hover:text-destructive rounded-lg transition-colors"
                                        title="Löschen"
                                      >
                                        <Trash2 className="h-4 w-4" />
                                      </button>
                                    </div>
                                  </td>
                                )}
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
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
                      {saving ? 'Speichert...' : 'Alle Änderungen speichern'}
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

export default LocationSettingsV2;

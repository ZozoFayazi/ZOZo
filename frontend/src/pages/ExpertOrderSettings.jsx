import React, { useState, useEffect } from 'react';
import { Shield, Key, TestTube, Save, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

function ExpertOrderSettings() {
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [settings, setSettings] = useState({
    expertorder_api_key: '',
    expertorder_enabled: false,
    expertorder_test_mode: true
  });
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    loadLocations();
  }, []);

  useEffect(() => {
    if (selectedLocation) {
      loadSettings(selectedLocation);
    }
  }, [selectedLocation]);

  const loadLocations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/location-settings`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setLocations(data);
        if (data.length > 0) {
          setSelectedLocation(data[0].id);
        }
      }
    } catch (error) {
      toast.error('Fehler beim Laden der Standorte');
    }
  };

  const loadSettings = async (locationId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/expertorder-settings/${locationId}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      if (response.ok) {
        const data = await response.json();
        setSettings({
          expertorder_api_key: data.expertorder_api_key || '',
          expertorder_enabled: data.expertorder_enabled || false,
          expertorder_test_mode: data.expertorder_test_mode !== false
        });
      }
    } catch (error) {
      toast.error('Fehler beim Laden der Einstellungen');
    }
  };

  const saveSettings = async () => {
    if (!selectedLocation) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/expertorder-settings/${selectedLocation}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(settings)
        }
      );
      
      if (response.ok) {
        toast.success('Einstellungen gespeichert!');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fehler beim Speichern');
      }
    } catch (error) {
      toast.error('Fehler beim Speichern der Einstellungen');
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    if (!selectedLocation) return;
    
    setTesting(true);
    setTestResult(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/expertorder/test?location_id=${selectedLocation}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      
      const result = await response.json();
      setTestResult(result);
      
      if (result.success) {
        toast.success('Verbindung erfolgreich getestet!');
      } else {
        toast.error(`Test fehlgeschlagen: ${result.message}`);
      }
    } catch (error) {
      toast.error('Fehler beim Testen der Verbindung');
      setTestResult({ success: false, message: error.message });
    } finally {
      setTesting(false);
    }
  };

  const selectedLocationData = locations.find(l => l.id === selectedLocation);

  return (
    <div className="min-h-screen bg-background">
      <div className="container-custom py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="heading-2 mb-2">ExpertOrder Integration</h1>
          <p className="text-muted-foreground">
            Verbinde deine Standorte mit dem ExpertOrder Kassensystem
          </p>
        </div>

        {/* Location Selector */}
        <div className="glass rounded-2xl p-6 mb-6">
          <label className="block text-sm font-medium mb-2">Standort auswählen</label>
          <select
            value={selectedLocation || ''}
            onChange={(e) => setSelectedLocation(e.target.value)}
            className="w-full bg-background border border-border rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary focus:outline-none"
            data-testid="location-select"
          >
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </div>

        {selectedLocationData && (
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Settings Form */}
            <div className="lg:col-span-2 space-y-6">
              {/* API Key */}
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Key className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-semibold">API-Schlüssel</h3>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      ExpertOrder API Key
                    </label>
                    <input
                      type="password"
                      value={settings.expertorder_api_key}
                      onChange={(e) => setSettings({ ...settings, expertorder_api_key: e.target.value })}
                      placeholder="9615d48a-cc88-4c3e-8e43-102047366a71"
                      className="w-full bg-background border border-border rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary focus:outline-none font-mono text-sm"
                      data-testid="api-key-input"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      Den API-Schlüssel findest du in deinem ExpertOrder-Dashboard
                    </p>
                  </div>
                </div>
              </div>

              {/* Toggle Settings */}
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Shield className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-semibold">Einstellungen</h3>
                </div>
                
                <div className="space-y-4">
                  {/* Enable Integration */}
                  <div className="flex items-center justify-between p-4 bg-background/50 rounded-xl">
                    <div>
                      <p className="font-medium">Integration aktivieren</p>
                      <p className="text-sm text-muted-foreground">
                        Bestellungen automatisch an ExpertOrder senden
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.expertorder_enabled}
                        onChange={(e) => setSettings({ ...settings, expertorder_enabled: e.target.checked })}
                        className="sr-only peer"
                        data-testid="enable-toggle"
                      />
                      <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>

                  {/* Test Mode */}
                  <div className="flex items-center justify-between p-4 bg-background/50 rounded-xl">
                    <div>
                      <p className="font-medium">Test-Modus</p>
                      <p className="text-sm text-muted-foreground">
                        Verwendet Test-Endpoint (empfohlen für erste Tests)
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.expertorder_test_mode}
                        onChange={(e) => setSettings({ ...settings, expertorder_test_mode: e.target.checked })}
                        className="sr-only peer"
                        data-testid="test-mode-toggle"
                      />
                      <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4">
                <button
                  onClick={saveSettings}
                  disabled={loading}
                  className="btn-primary flex items-center gap-2"
                  data-testid="save-button"
                >
                  <Save className="h-4 w-4" />
                  {loading ? 'Speichert...' : 'Einstellungen speichern'}
                </button>
                
                <button
                  onClick={testConnection}
                  disabled={testing || !settings.expertorder_api_key}
                  className="btn-secondary flex items-center gap-2"
                  data-testid="test-button"
                >
                  <TestTube className="h-4 w-4" />
                  {testing ? 'Teste...' : 'Verbindung testen'}
                </button>
              </div>
            </div>

            {/* Info Panel */}
            <div className="space-y-6">
              {/* Test Result */}
              {testResult && (
                <div className={`glass rounded-2xl p-6 border-2 ${
                  testResult.success ? 'border-green-500/50' : 'border-red-500/50'
                }`}>
                  <div className="flex items-center gap-3 mb-3">
                    {testResult.success ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                    <h3 className="font-semibold">
                      {testResult.success ? 'Test erfolgreich' : 'Test fehlgeschlagen'}
                    </h3>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">
                    {testResult.message}
                  </p>
                  {testResult.status_code && (
                    <p className="text-xs text-muted-foreground">
                      Status Code: {testResult.status_code}
                    </p>
                  )}
                </div>
              )}

              {/* How It Works */}
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <AlertCircle className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold">So funktioniert's</h3>
                </div>
                <div className="space-y-3 text-sm text-muted-foreground">
                  <div className="flex gap-2">
                    <span className="text-primary font-bold">1.</span>
                    <p>API-Schlüssel von ExpertOrder Dashboard kopieren</p>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-primary font-bold">2.</span>
                    <p>Schlüssel hier einfügen und Test-Modus aktivieren</p>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-primary font-bold">3.</span>
                    <p>Verbindung testen mit Test-Bestellung</p>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-primary font-bold">4.</span>
                    <p>Integration aktivieren für automatische Weiterleitung</p>
                  </div>
                </div>
              </div>

              {/* Documentation Link */}
              <div className="glass rounded-2xl p-6">
                <h3 className="font-semibold mb-2">Dokumentation</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Weitere Informationen zur ExpertOrder API
                </p>
                <a
                  href="https://osp.expertorder.de/api-doc/push"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline text-sm"
                >
                  API-Dokumentation öffnen →
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ExpertOrderSettings;

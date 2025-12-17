import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { ScrollArea } from '../components/ui/scroll-area';
import { Separator } from '../components/ui/separator';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../components/ui/alert-dialog';
import { toast } from 'sonner';
import { 
  Cable, 
  MapPin, 
  Settings2, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  Eye,
  EyeOff,
  Play,
  History,
  Wifi,
  WifiOff,
  TestTube,
  Loader2,
  Clock,
  User
} from 'lucide-react';

export default function POSSettings() {
  const { token, admin, isSuperAdmin } = useAdminAuth();
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [posConfig, setPosConfig] = useState(null);
  const [posProviders, setPosProviders] = useState([]);
  const [posLogs, setPosLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [testResultDialogOpen, setTestResultDialogOpen] = useState(false);
  const [testResult, setTestResult] = useState(null);
  
  // Form state for config dialog
  const [formData, setFormData] = useState({
    provider: 'none',
    test_mode: true,
    merchant_id: '',
    api_key: '',
    username: '',
    secret: '',
    base_url: ''
  });

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Fetch locations
  const fetchLocations = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/admin/locations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch locations');
      const data = await response.json();
      setLocations(data.locations);
      
      // Auto-select first location
      if (data.locations.length > 0 && !selectedLocation) {
        setSelectedLocation(data.locations[0]);
      }
    } catch (error) {
      console.error('Fetch locations error:', error);
      toast.error('Fehler beim Laden der Standorte');
    }
  };

  // Fetch POS providers
  const fetchProviders = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/admin/pos/providers`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch providers');
      const data = await response.json();
      setPosProviders(data.providers);
    } catch (error) {
      console.error('Fetch providers error:', error);
    }
  };

  // Fetch POS config for selected location
  const fetchPosConfig = async (slug) => {
    try {
      const response = await fetch(`${backendUrl}/api/admin/locations/${slug}/pos/config`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch POS config');
      const data = await response.json();
      setPosConfig(data);
    } catch (error) {
      console.error('Fetch POS config error:', error);
      toast.error('Fehler beim Laden der POS-Konfiguration');
    }
  };

  // Fetch POS logs for selected location
  const fetchPosLogs = async (slug) => {
    try {
      const response = await fetch(`${backendUrl}/api/admin/locations/${slug}/pos/logs?limit=20`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch logs');
      const data = await response.json();
      setPosLogs(data.logs);
    } catch (error) {
      console.error('Fetch logs error:', error);
    }
  };

  useEffect(() => {
    if (token) {
      setLoading(true);
      Promise.all([fetchLocations(), fetchProviders()])
        .finally(() => setLoading(false));
    }
  }, [token]);

  useEffect(() => {
    if (selectedLocation && token) {
      fetchPosConfig(selectedLocation.slug);
      fetchPosLogs(selectedLocation.slug);
    }
  }, [selectedLocation, token]);

  // Open config dialog
  const openConfigDialog = () => {
    setFormData({
      provider: posConfig?.provider || 'none',
      test_mode: posConfig?.test_mode ?? true,
      merchant_id: '',
      api_key: '',
      username: '',
      secret: '',
      base_url: posConfig?.base_url || ''
    });
    setConfigDialogOpen(true);
  };

  // Save POS configuration
  const saveConfig = async () => {
    if (!selectedLocation) return;
    
    setSaving(true);
    try {
      const response = await fetch(
        `${backendUrl}/api/admin/locations/${selectedLocation.slug}/pos/config`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData)
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Speichern');
      }

      toast.success('POS-Konfiguration gespeichert');
      setConfigDialogOpen(false);
      fetchPosConfig(selectedLocation.slug);
      fetchPosLogs(selectedLocation.slug);
    } catch (error) {
      console.error('Save config error:', error);
      toast.error(error.message || 'Fehler beim Speichern der Konfiguration');
    } finally {
      setSaving(false);
    }
  };

  // Test POS connection
  const testConnection = async (simulateFailure = false) => {
    if (!selectedLocation) return;
    
    setTesting(true);
    try {
      const response = await fetch(
        `${backendUrl}/api/admin/locations/${selectedLocation.slug}/pos/test`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ simulate_failure: simulateFailure })
        }
      );

      const result = await response.json();
      setTestResult(result);
      setTestResultDialogOpen(true);
      
      if (result.success) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
      
      // Refresh config and logs
      fetchPosConfig(selectedLocation.slug);
      fetchPosLogs(selectedLocation.slug);
    } catch (error) {
      console.error('Test connection error:', error);
      toast.error('Verbindungstest fehlgeschlagen');
    } finally {
      setTesting(false);
    }
  };

  // Get status badge variant
  const getStatusBadge = (status) => {
    switch (status) {
      case 'connected':
        return <Badge className="bg-[hsl(var(--success)/0.12)] text-[hsl(var(--success))] border-[hsl(var(--success))]" data-testid="pos-status-connected"><CheckCircle2 className="h-3 w-3 mr-1" /> Verbunden</Badge>;
      case 'error':
        return <Badge className="bg-[hsl(var(--destructive)/0.12)] text-[hsl(var(--destructive))] border-[hsl(var(--destructive))]" data-testid="pos-status-error"><XCircle className="h-3 w-3 mr-1" /> Fehler</Badge>;
      case 'testing':
        return <Badge className="bg-[hsl(var(--warning)/0.12)] text-[hsl(var(--warning))] border-[hsl(var(--warning))]" data-testid="pos-status-testing"><TestTube className="h-3 w-3 mr-1" /> Testmodus</Badge>;
      default:
        return <Badge variant="secondary" data-testid="pos-status-disconnected"><WifiOff className="h-3 w-3 mr-1" /> Nicht verbunden</Badge>;
    }
  };

  // Get provider name
  const getProviderName = (id) => {
    const provider = posProviders.find(p => p.id === id);
    return provider?.name || id;
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '-';
    return new Date(timestamp).toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="pos-settings-page">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <Cable className="h-6 w-6" />
              POS-System Integration
            </h1>
            <p className="text-muted-foreground">
              Kassensystem-Anbindung pro Standort konfigurieren
            </p>
          </div>
        </div>

        {/* Location Selector */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              Standort auswählen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Select
              value={selectedLocation?.slug || ''}
              onValueChange={(slug) => {
                const loc = locations.find(l => l.slug === slug);
                setSelectedLocation(loc);
              }}
              data-testid="pos-location-select"
            >
              <SelectTrigger className="w-full md:w-[300px]">
                <SelectValue placeholder="Standort wählen..." />
              </SelectTrigger>
              <SelectContent>
                {locations.map((loc) => (
                  <SelectItem key={loc.slug} value={loc.slug}>
                    {loc.name} ({loc.city})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {selectedLocation && posConfig && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* POS Configuration Card */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Settings2 className="h-5 w-5" />
                      POS-Konfiguration
                    </CardTitle>
                    <CardDescription>
                      {selectedLocation.name} - {selectedLocation.city}
                    </CardDescription>
                  </div>
                  {getStatusBadge(posConfig.status)}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Provider Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground text-xs">Provider</Label>
                    <p className="font-medium">{getProviderName(posConfig.provider)}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground text-xs">Modus</Label>
                    <div className="flex items-center gap-2">
                      {posConfig.test_mode ? (
                        <Badge className="bg-[hsl(var(--warning)/0.12)] text-[hsl(var(--warning))]" data-testid="pos-testmode-badge">
                          <TestTube className="h-3 w-3 mr-1" /> Testmodus
                        </Badge>
                      ) : (
                        <Badge className="bg-[hsl(var(--success)/0.12)] text-[hsl(var(--success))]">
                          <Wifi className="h-3 w-3 mr-1" /> Live
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Credentials Status */}
                <div>
                  <Label className="text-muted-foreground text-xs mb-2 block">Credentials</Label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    <div className={`flex items-center gap-1 text-sm ${posConfig.has_merchant_id ? 'text-[hsl(var(--success))]' : 'text-muted-foreground'}`}>
                      {posConfig.has_merchant_id ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                      Merchant ID
                    </div>
                    <div className={`flex items-center gap-1 text-sm ${posConfig.has_api_key ? 'text-[hsl(var(--success))]' : 'text-muted-foreground'}`}>
                      {posConfig.has_api_key ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                      API Key
                    </div>
                    <div className={`flex items-center gap-1 text-sm ${posConfig.has_username ? 'text-[hsl(var(--success))]' : 'text-muted-foreground'}`}>
                      {posConfig.has_username ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                      Username
                    </div>
                    <div className={`flex items-center gap-1 text-sm ${posConfig.has_secret ? 'text-[hsl(var(--success))]' : 'text-muted-foreground'}`}>
                      {posConfig.has_secret ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                      Secret
                    </div>
                  </div>
                </div>

                {posConfig.base_url && (
                  <div>
                    <Label className="text-muted-foreground text-xs">API URL</Label>
                    <p className="font-mono text-sm">{posConfig.base_url}</p>
                  </div>
                )}

                <Separator />

                {/* Status Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <Label className="text-muted-foreground text-xs">Letzte Synchronisation</Label>
                    <p className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatTime(posConfig.last_sync_at)}
                    </p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground text-xs">Zuletzt geändert von</Label>
                    <p className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {posConfig.updated_by || '-'}
                    </p>
                  </div>
                </div>

                {/* Error Display */}
                {posConfig.last_error && (
                  <div className="p-3 rounded-lg bg-[hsl(var(--destructive)/0.1)] border border-[hsl(var(--destructive)/0.3)]">
                    <Label className="text-[hsl(var(--destructive))] text-xs flex items-center gap-1 mb-1">
                      <AlertTriangle className="h-3 w-3" /> Letzter Fehler ({formatTime(posConfig.last_error_at)})
                    </Label>
                    <p className="text-sm text-foreground">{posConfig.last_error}</p>
                  </div>
                )}
              </CardContent>
              <CardFooter className="flex flex-wrap gap-2 border-t pt-4">
                <Button
                  onClick={openConfigDialog}
                  data-testid="pos-config-button"
                >
                  <Settings2 className="h-4 w-4 mr-2" />
                  Konfigurieren
                </Button>
                <Button
                  variant="outline"
                  onClick={() => testConnection(false)}
                  disabled={testing || posConfig.provider === 'none'}
                  data-testid="pos-test-connection-button"
                >
                  {testing ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4 mr-2" />
                  )}
                  Verbindung testen
                </Button>
                {posConfig.test_mode && (
                  <Button
                    variant="outline"
                    onClick={() => testConnection(true)}
                    disabled={testing || posConfig.provider === 'none'}
                    data-testid="pos-test-failure-button"
                  >
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    Fehler simulieren
                  </Button>
                )}
              </CardFooter>
            </Card>

            {/* Logs Card */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <History className="h-4 w-4" />
                  POS-Protokoll
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-[400px]" data-testid="pos-logs-area">
                  {posLogs.length === 0 ? (
                    <div className="p-4 text-center text-muted-foreground">
                      Keine Protokolleinträge vorhanden
                    </div>
                  ) : (
                    <div className="divide-y divide-border">
                      {posLogs.map((log) => (
                        <div key={log._id} className="p-3 hover:bg-muted/30 transition-colors">
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                {log.success ? (
                                  <CheckCircle2 className="h-3 w-3 text-[hsl(var(--success))] flex-shrink-0" />
                                ) : (
                                  <XCircle className="h-3 w-3 text-[hsl(var(--destructive))] flex-shrink-0" />
                                )}
                                <span className="text-sm font-medium truncate">
                                  {log.action === 'test_connection' && 'Verbindungstest'}
                                  {log.action === 'push_order' && 'Bestellung gesendet'}
                                  {log.action === 'config_update' && 'Konfiguration geändert'}
                                </span>
                                {log.is_test_mode && (
                                  <Badge variant="outline" className="text-[10px] px-1 py-0">TEST</Badge>
                                )}
                              </div>
                              <p className="text-xs text-muted-foreground mt-0.5 truncate">
                                {log.message}
                              </p>
                              {log.admin_email && (
                                <p className="text-xs text-muted-foreground">
                                  von {log.admin_email}
                                </p>
                              )}
                            </div>
                            <span className="text-xs text-muted-foreground whitespace-nowrap">
                              {formatTime(log.timestamp)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Config Dialog */}
        <Dialog open={configDialogOpen} onOpenChange={setConfigDialogOpen}>
          <DialogContent className="sm:max-w-[500px]" data-testid="pos-config-dialog">
            <DialogHeader>
              <DialogTitle>POS-Konfiguration</DialogTitle>
              <DialogDescription>
                Kassensystem für {selectedLocation?.name} konfigurieren
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              {/* Provider Selection */}
              <div className="space-y-2">
                <Label>POS-Provider</Label>
                <Select
                  value={formData.provider}
                  onValueChange={(value) => setFormData({ ...formData, provider: value })}
                  data-testid="pos-provider-select"
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Provider wählen..." />
                  </SelectTrigger>
                  <SelectContent>
                    {posProviders.map((provider) => (
                      <SelectItem 
                        key={provider.id} 
                        value={provider.id}
                        disabled={!provider.available}
                      >
                        <div className="flex items-center gap-2">
                          {provider.name}
                          {!provider.available && (
                            <Badge variant="outline" className="text-xs">Bald verfügbar</Badge>
                          )}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Test Mode Toggle */}
              <div className="flex items-center justify-between rounded-lg border p-3">
                <div className="space-y-0.5">
                  <Label className="font-medium">Testmodus</Label>
                  <p className="text-xs text-muted-foreground">
                    Simuliert Verbindungen ohne echte API-Aufrufe
                  </p>
                </div>
                <Switch
                  checked={formData.test_mode}
                  onCheckedChange={(checked) => setFormData({ ...formData, test_mode: checked })}
                  data-testid="pos-testmode-switch"
                />
              </div>

              {/* Provider-specific fields */}
              {formData.provider === 'expertorder' && (
                <div className="space-y-4">
                  <Separator />
                  <p className="text-sm font-medium">ExpertOrder Credentials</p>
                  
                  <div className="space-y-2">
                    <Label htmlFor="merchant_id">Merchant ID *</Label>
                    <Input
                      id="merchant_id"
                      value={formData.merchant_id}
                      onChange={(e) => setFormData({ ...formData, merchant_id: e.target.value })}
                      placeholder={posConfig?.has_merchant_id ? "••••••••" : "Merchant ID eingeben"}
                      data-testid="pos-merchant-id-input"
                    />
                    {posConfig?.has_merchant_id && (
                      <p className="text-xs text-muted-foreground">Leer lassen, um bestehenden Wert zu behalten</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="api_key">API Key</Label>
                    <Input
                      id="api_key"
                      type="password"
                      value={formData.api_key}
                      onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                      placeholder={posConfig?.has_api_key ? "••••••••" : "API Key eingeben"}
                      data-testid="pos-api-key-input"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="username">Benutzername</Label>
                      <Input
                        id="username"
                        value={formData.username}
                        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                        placeholder={posConfig?.has_username ? "••••••••" : "Username"}
                        data-testid="pos-username-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="secret">Secret</Label>
                      <Input
                        id="secret"
                        type="password"
                        value={formData.secret}
                        onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
                        placeholder={posConfig?.has_secret ? "••••••••" : "Secret"}
                        data-testid="pos-secret-input"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="base_url">API URL (optional)</Label>
                    <Input
                      id="base_url"
                      value={formData.base_url}
                      onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                      placeholder="https://api.expertorder.com/v1"
                      data-testid="pos-base-url-input"
                    />
                  </div>
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setConfigDialogOpen(false)}>
                Abbrechen
              </Button>
              <Button onClick={saveConfig} disabled={saving} data-testid="pos-save-config-button">
                {saving ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : null}
                Speichern
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Test Result Dialog */}
        <Dialog open={testResultDialogOpen} onOpenChange={setTestResultDialogOpen}>
          <DialogContent className="sm:max-w-[400px]" data-testid="pos-test-result-dialog">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                {testResult?.success ? (
                  <>
                    <CheckCircle2 className="h-5 w-5 text-[hsl(var(--success))]" />
                    Verbindung erfolgreich
                  </>
                ) : (
                  <>
                    <XCircle className="h-5 w-5 text-[hsl(var(--destructive))]" />
                    Verbindung fehlgeschlagen
                  </>
                )}
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <p className="text-sm">{testResult?.message}</p>
              
              {testResult?.is_test_mode && (
                <Badge className="bg-[hsl(var(--warning)/0.12)] text-[hsl(var(--warning))]">
                  <TestTube className="h-3 w-3 mr-1" /> Testmodus - Simuliert
                </Badge>
              )}

              {testResult?.details && (
                <div className="p-3 rounded-lg bg-muted/50">
                  <Label className="text-xs text-muted-foreground">Details</Label>
                  <pre className="text-xs mt-1 overflow-auto">
                    {JSON.stringify(testResult.details, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <DialogFooter>
              <Button onClick={() => setTestResultDialogOpen(false)}>
                Schließen
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AdminLayout>
  );
}

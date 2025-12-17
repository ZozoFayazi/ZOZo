import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import AdminLayout from '../components/AdminLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ScrollArea } from '../components/ui/scroll-area';
import { Separator } from '../components/ui/separator';
import { toast } from 'sonner';
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Lock,
  User,
  Clock,
  Search,
  RefreshCw,
  Filter,
  Activity,
  Loader2,
  Smartphone,
  Key
} from 'lucide-react';
import TwoFactorSetup from '../components/TwoFactorSetup';

export default function SecurityDashboard() {
  const { token, admin, isSuperAdmin, updateAdminData } = useAdminAuth();
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [logs, setLogs] = useState([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [filters, setFilters] = useState({
    category: '',
    result: '',
    severity: '',
    action: ''
  });
  
  // 2FA state
  const [twoFAStatus, setTwoFAStatus] = useState(null);
  const [show2FASetup, setShow2FASetup] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  const PAGE_SIZE = 25;

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/admin/security/summary?hours=24`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch summary');
      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error('Summary fetch error:', error);
      toast.error('Fehler beim Laden der Sicherheitsübersicht');
    }
  };

  const fetchLogs = async (page = 0) => {
    try {
      const params = new URLSearchParams({
        limit: PAGE_SIZE.toString(),
        offset: (page * PAGE_SIZE).toString()
      });
      
      if (filters.category) params.append('category', filters.category);
      if (filters.result) params.append('result', filters.result);
      if (filters.severity) params.append('severity', filters.severity);
      if (filters.action) params.append('action', filters.action);

      const response = await fetch(`${backendUrl}/api/admin/security/audit-logs?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch logs');
      const data = await response.json();
      setLogs(data.logs);
      setTotalLogs(data.total);
    } catch (error) {
      console.error('Logs fetch error:', error);
      toast.error('Fehler beim Laden der Audit-Logs');
    }
  };

  // Fetch 2FA status
  const fetch2FAStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/admin/auth/2fa/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch 2FA status');
      const data = await response.json();
      setTwoFAStatus(data);
    } catch (error) {
      console.error('2FA status fetch error:', error);
    }
  };

  useEffect(() => {
    if (token && isSuperAdmin()) {
      setLoading(true);
      Promise.all([fetchSummary(), fetchLogs(), fetch2FAStatus()])
        .finally(() => setLoading(false));
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      fetchLogs(currentPage);
    }
  }, [currentPage, filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(0);
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '-';
    return new Date(timestamp).toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'critical':
        return <Badge className="bg-[hsl(var(--destructive))] text-white">KRITISCH</Badge>;
      case 'high':
        return <Badge className="bg-[hsl(var(--destructive)/0.8)] text-white">HOCH</Badge>;
      case 'medium':
        return <Badge className="bg-[hsl(var(--warning)/0.8)] text-white">MITTEL</Badge>;
      default:
        return <Badge variant="secondary">NIEDRIG</Badge>;
    }
  };

  const getCategoryBadge = (category) => {
    const colors = {
      auth: 'bg-blue-500/20 text-blue-400',
      security: 'bg-red-500/20 text-red-400',
      product: 'bg-green-500/20 text-green-400',
      location: 'bg-yellow-500/20 text-yellow-400',
      order: 'bg-purple-500/20 text-purple-400',
      pos: 'bg-cyan-500/20 text-cyan-400',
      admin: 'bg-orange-500/20 text-orange-400',
      system: 'bg-gray-500/20 text-gray-400'
    };
    return <Badge className={colors[category] || colors.system}>{category?.toUpperCase()}</Badge>;
  };

  if (!isSuperAdmin()) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Shield className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-xl font-semibold">Zugriff verweigert</h2>
            <p className="text-muted-foreground">Nur Super Admins können das Security Dashboard einsehen.</p>
          </div>
        </div>
      </AdminLayout>
    );
  }

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
      <div className="space-y-6" data-testid="security-dashboard">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <Shield className="h-6 w-6" />
              Sicherheit & Audit
            </h1>
            <p className="text-muted-foreground">
              Überwachen Sie Sicherheitsereignisse und Admin-Aktivitäten
            </p>
          </div>
          <Button variant="outline" onClick={() => { fetchSummary(); fetchLogs(currentPage); }}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Aktualisieren
          </Button>
        </div>

        {/* 2FA Card */}
        <Card className={twoFAStatus?.enabled ? 'border-[hsl(var(--success)/0.5)]' : 'border-[hsl(var(--warning)/0.5)]'}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${twoFAStatus?.enabled ? 'bg-[hsl(var(--success)/0.1)]' : 'bg-[hsl(var(--warning)/0.1)]'}`}>
                  <Smartphone className={`h-5 w-5 ${twoFAStatus?.enabled ? 'text-[hsl(var(--success))]' : 'text-[hsl(var(--warning))]'}`} />
                </div>
                <div>
                  <p className="font-medium">Zwei-Faktor-Authentifizierung</p>
                  <p className="text-sm text-muted-foreground">
                    {twoFAStatus?.enabled 
                      ? `Aktiviert • ${twoFAStatus.backup_codes_remaining} Backup-Codes übrig`
                      : 'Nicht aktiviert'
                    }
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {twoFAStatus?.enabled ? (
                  <Badge className="bg-[hsl(var(--success)/0.12)] text-[hsl(var(--success))]">
                    <CheckCircle2 className="h-3 w-3 mr-1" /> Aktiv
                  </Badge>
                ) : (
                  <>
                    {twoFAStatus?.required && (
                      <Badge variant="destructive" className="mr-2">Erforderlich</Badge>
                    )}
                    <Button onClick={() => setShow2FASetup(true)} data-testid="enable-2fa-button">
                      <Shield className="h-4 w-4 mr-2" />
                      2FA aktivieren
                    </Button>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-[hsl(var(--destructive)/0.1)]">
                  <AlertTriangle className="h-5 w-5 text-[hsl(var(--destructive))]" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{summary?.failed_logins || 0}</p>
                  <p className="text-xs text-muted-foreground">Fehlgeschlagene Logins (24h)</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-[hsl(var(--warning)/0.1)]">
                  <Lock className="h-5 w-5 text-[hsl(var(--warning))]" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{summary?.rate_limit_events || 0}</p>
                  <p className="text-xs text-muted-foreground">Rate-Limit Ereignisse</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-[hsl(var(--destructive)/0.1)]">
                  <XCircle className="h-5 w-5 text-[hsl(var(--destructive))]" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{summary?.high_severity_events?.length || 0}</p>
                  <p className="text-xs text-muted-foreground">Kritische Ereignisse</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-[hsl(var(--success)/0.1)]">
                  <Activity className="h-5 w-5 text-[hsl(var(--success))]" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{totalLogs}</p>
                  <p className="text-xs text-muted-foreground">Gesamte Log-Einträge</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* High Severity Events */}
        {summary?.high_severity_events?.length > 0 && (
          <Card className="border-[hsl(var(--destructive)/0.5)]">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2 text-[hsl(var(--destructive))]">
                <AlertTriangle className="h-4 w-4" />
                Kritische Ereignisse (letzte 24h)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {summary.high_severity_events.map((event, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-[hsl(var(--destructive)/0.05)] rounded-lg">
                    <div className="flex items-center gap-3">
                      {getSeverityBadge(event.severity)}
                      <span className="text-sm font-medium">{event.action}</span>
                      <span className="text-sm text-muted-foreground">von {event.actor_email}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">{formatTime(event.timestamp)}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Audit Logs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Audit-Protokoll
            </CardTitle>
            <CardDescription>
              Vollständiges Protokoll aller System- und Admin-Aktivitäten
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Filters */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
              <div>
                <Label className="text-xs">Kategorie</Label>
                <Select value={filters.category || 'all'} onValueChange={(v) => handleFilterChange('category', v === 'all' ? '' : v)}>
                  <SelectTrigger data-testid="filter-category">
                    <SelectValue placeholder="Alle" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Alle</SelectItem>
                    <SelectItem value="auth">Auth</SelectItem>
                    <SelectItem value="security">Security</SelectItem>
                    <SelectItem value="product">Produkt</SelectItem>
                    <SelectItem value="location">Standort</SelectItem>
                    <SelectItem value="order">Bestellung</SelectItem>
                    <SelectItem value="pos">POS</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label className="text-xs">Ergebnis</Label>
                <Select value={filters.result || 'all'} onValueChange={(v) => handleFilterChange('result', v === 'all' ? '' : v)}>
                  <SelectTrigger data-testid="filter-result">
                    <SelectValue placeholder="Alle" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Alle</SelectItem>
                    <SelectItem value="success">Erfolg</SelectItem>
                    <SelectItem value="failure">Fehler</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label className="text-xs">Schweregrad</Label>
                <Select value={filters.severity || 'all'} onValueChange={(v) => handleFilterChange('severity', v === 'all' ? '' : v)}>
                  <SelectTrigger data-testid="filter-severity">
                    <SelectValue placeholder="Alle" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Alle</SelectItem>
                    <SelectItem value="critical">Kritisch</SelectItem>
                    <SelectItem value="high">Hoch</SelectItem>
                    <SelectItem value="medium">Mittel</SelectItem>
                    <SelectItem value="low">Niedrig</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="col-span-2">
                <Label className="text-xs">Aktion suchen</Label>
                <Input
                  placeholder="z.B. login, product..."
                  value={filters.action}
                  onChange={(e) => handleFilterChange('action', e.target.value)}
                  data-testid="filter-action"
                />
              </div>
            </div>

            <Separator className="my-4" />

            {/* Logs Table */}
            <ScrollArea className="h-[400px]" data-testid="audit-logs-area">
              <div className="space-y-2">
                {logs.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    Keine Log-Einträge gefunden
                  </div>
                ) : (
                  logs.map((log, idx) => (
                    <div 
                      key={log._id || idx} 
                      className={`p-3 rounded-lg border ${
                        log.result === 'failure' ? 'border-[hsl(var(--destructive)/0.3)] bg-[hsl(var(--destructive)/0.03)]' : 'border-border bg-muted/20'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center flex-wrap gap-2 mb-1">
                            {getSeverityBadge(log.severity)}
                            {getCategoryBadge(log.category)}
                            {log.result === 'success' ? (
                              <CheckCircle2 className="h-4 w-4 text-[hsl(var(--success))]" />
                            ) : (
                              <XCircle className="h-4 w-4 text-[hsl(var(--destructive))]" />
                            )}
                            <span className="font-medium text-sm">{log.action}</span>
                          </div>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <User className="h-3 w-3" />
                              {log.actor_email}
                            </span>
                            {log.target && (
                              <span>Ziel: {log.target_type} - {log.target}</span>
                            )}
                            {log.ip_address && (
                              <span>IP: {log.ip_address}</span>
                            )}
                          </div>
                          {log.details && Object.keys(log.details).length > 0 && (
                            <div className="mt-1 text-xs text-muted-foreground">
                              Details: {JSON.stringify(log.details).slice(0, 100)}
                              {JSON.stringify(log.details).length > 100 && '...'}
                            </div>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground whitespace-nowrap">
                          {formatTime(log.timestamp)}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>

            {/* Pagination */}
            {totalLogs > PAGE_SIZE && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t">
                <span className="text-sm text-muted-foreground">
                  Zeige {currentPage * PAGE_SIZE + 1} - {Math.min((currentPage + 1) * PAGE_SIZE, totalLogs)} von {totalLogs}
                </span>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => Math.max(0, p - 1))}
                    disabled={currentPage === 0}
                  >
                    Zurück
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => p + 1)}
                    disabled={(currentPage + 1) * PAGE_SIZE >= totalLogs}
                  >
                    Weiter
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 2FA Setup Dialog */}
      <TwoFactorSetup
        open={show2FASetup}
        onOpenChange={setShow2FASetup}
        forced={twoFAStatus?.required && !twoFAStatus?.enabled}
        onSuccess={() => {
          fetch2FAStatus();
          if (updateAdminData) {
            updateAdminData({ totp_enabled: true });
          }
        }}
      />
    </AdminLayout>
  );
}

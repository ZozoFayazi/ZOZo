import React, { useState } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { 
  Zap, 
  Mail, 
  Send, 
  Users, 
  TrendingUp,
  Gift,
  Crown,
  RefreshCw,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function EmailAutomation() {
  const [loading, setLoading] = useState({});

  const runAutomation = async (type, endpoint, params = {}) => {
    setLoading(prev => ({ ...prev, [type]: true }));
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await axios.post(
        `${API_URL}/api/admin/newsletter/automation/${endpoint}`,
        null,
        { 
          headers: { Authorization: `Bearer ${token}` },
          params
        }
      );

      const data = response.data;
      if (data.success) {
        toast.success(data.message || 'Automation erfolgreich ausgeführt');
        if (data.emails_sent !== undefined) {
          toast.info(`${data.emails_sent} Emails versendet${data.errors ? `, ${data.errors} Fehler` : ''}`);
        }
      } else {
        toast.error(data.message || 'Automation fehlgeschlagen');
      }
    } catch (error) {
      console.error(`Error running ${type} automation:`, error);
      toast.error(`Fehler bei ${type}-Automation`);
    } finally {
      setLoading(prev => ({ ...prev, [type]: false }));
    }
  };

  const automations = [
    {
      id: 'welcome',
      title: 'Willkommens-Emails',
      description: 'Automatische Willkommens-Email mit 10% Rabatt-Code für neue Newsletter-Abonnenten',
      icon: Gift,
      color: 'emerald',
      trigger: 'Sofort nach Anmeldung',
      status: 'Aktiv',
      action: () => toast.info('Läuft automatisch bei jeder Newsletter-Anmeldung')
    },
    {
      id: 'reactivation',
      title: 'Reaktivierungs-Kampagne',
      description: 'Sendet 15% Comeback-Rabatt an Kunden, die länger als 30 Tage nicht bestellt haben (At-Risk Segment)',
      icon: RefreshCw,
      color: 'orange',
      trigger: 'Manuell',
      status: 'Bereit',
      action: () => runAutomation('reactivation', 'reactivation', { days_threshold: 30 })
    },
    {
      id: 'vip',
      title: 'VIP-Upgrade Benachrichtigungen',
      description: 'Gratuliert Kunden, die zum VIP-Status aufgestiegen sind (RFM Score ≥ 4.5)',
      icon: Crown,
      color: 'amber',
      trigger: 'Täglich prüfen',
      status: 'Bereit',
      action: () => runAutomation('vip', 'vip-upgrades')
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      emerald: {
        bg: 'bg-emerald-500/10',
        text: 'text-emerald-600',
        border: 'border-emerald-500/20'
      },
      orange: {
        bg: 'bg-orange-500/10',
        text: 'text-orange-600',
        border: 'border-orange-500/20'
      },
      amber: {
        bg: 'bg-amber-500/10',
        text: 'text-amber-600',
        border: 'border-amber-500/20'
      }
    };
    return colors[color] || colors.emerald;
  };

  return (
    <AdminLayout>
      <div className="min-h-screen bg-background p-4 lg:p-8" data-testid="email-automation-page">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <Zap className="h-8 w-8 text-amber-500" />
            Email Marketing Automation
          </h1>
          <p className="text-muted-foreground">
            Automatisierte Email-Kampagnen für bessere Kundenbindung
          </p>
        </div>

        <Card className="border-blue-500/50 bg-blue-500/5 mb-6">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-foreground mb-1">✅ Echte Email-Integration aktiv!</h3>
                <p className="text-sm text-muted-foreground">
                  Emails werden jetzt über Resend versendet. Alle automatischen Kampagnen sind einsatzbereit.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {automations.map(automation => {
            const colorClasses = getColorClasses(automation.color);
            const Icon = automation.icon;

            return (
              <Card key={automation.id} className="border-border">
                <CardHeader>
                  <div className={`h-12 w-12 rounded-lg ${colorClasses.bg} flex items-center justify-center mb-3`}>
                    <Icon className={`h-6 w-6 ${colorClasses.text}`} />
                  </div>
                  <CardTitle className="text-lg">{automation.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    {automation.description}
                  </p>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Trigger:</span>
                      <span className="font-medium text-foreground">{automation.trigger}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Status:</span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colorClasses.bg} ${colorClasses.text} border ${colorClasses.border}`}>
                        {automation.status}
                      </span>
                    </div>
                  </div>

                  <Button 
                    className="w-full"
                    onClick={automation.action}
                    disabled={loading[automation.id]}
                    data-testid={`automation-${automation.id}-button`}
                  >
                    {loading[automation.id] ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Läuft...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Jetzt ausführen
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5 text-primary" />
              Verfügbare Email-Templates
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 bg-muted/30 rounded-lg border border-border">
                <h4 className="font-semibold text-foreground mb-2">🎉 Willkommens-Email</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Professionelles Template mit ZOZO Branding, 10% Rabatt-Code, Vorteile-Liste
                </p>
                <div className="flex gap-2 text-xs text-muted-foreground">
                  <span className="px-2 py-1 bg-background rounded">Responsive</span>
                  <span className="px-2 py-1 bg-background rounded">Dark Design</span>
                  <span className="px-2 py-1 bg-background rounded">Personalisiert</span>
                </div>
              </div>

              <div className="p-4 bg-muted/30 rounded-lg border border-border">
                <h4 className="font-semibold text-foreground mb-2">📦 Order Follow-Up</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Feedback-Anfrage nach Bestellung, 5-Sterne-Bewertung, Erneut bestellen CTA
                </p>
                <div className="flex gap-2 text-xs text-muted-foreground">
                  <span className="px-2 py-1 bg-background rounded">Order Details</span>
                  <span className="px-2 py-1 bg-background rounded">Star Rating</span>
                </div>
              </div>

              <div className="p-4 bg-muted/30 rounded-lg border border-border">
                <h4 className="font-semibold text-foreground mb-2">🔄 Reaktivierungs-Email</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  15% Comeback-Rabatt, Lieblings-Produkt hervorgehoben, emotionale Ansprache
                </p>
                <div className="flex gap-2 text-xs text-muted-foreground">
                  <span className="px-2 py-1 bg-background rounded">15% Rabatt</span>
                  <span className="px-2 py-1 bg-background rounded">Favoriten</span>
                </div>
              </div>

              <div className="p-4 bg-muted/30 rounded-lg border border-border">
                <h4 className="font-semibold text-foreground mb-2">👑 VIP-Upgrade</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Gratulations-Email mit VIP-Status, exklusive Vorteile, Premium-Design
                </p>
                <div className="flex gap-2 text-xs text-muted-foreground">
                  <span className="px-2 py-1 bg-background rounded">Gold Design</span>
                  <span className="px-2 py-1 bg-background rounded">Vorteile-Liste</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-3 gap-4 mt-6">
          <Card className="border-border">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <Mail className="h-5 w-5 text-emerald-600" />
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Willkommens-Emails</div>
                  <div className="text-xl font-bold text-foreground">Automatisch</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Reaktivierungs-Rate</div>
                  <div className="text-xl font-bold text-foreground">~15-25%</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <Crown className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">VIP-Kunden</div>
                  <div className="text-xl font-bold text-foreground">Auto-Benachrichtigung</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AdminLayout>
  );
}

export default EmailAutomation;

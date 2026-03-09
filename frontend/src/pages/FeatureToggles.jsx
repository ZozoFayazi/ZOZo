import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Settings,
  ArrowLeft,
  RefreshCw,
  Check,
  X,
  Eye,
  EyeOff,
  AlertCircle,
  ChefHat,
  MapPin,
  Tag,
  Users,
  Star,
  ShoppingCart
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';

const FEATURE_ICONS = {
  burger_builder: ChefHat,
  order_tracking: MapPin,
  daily_deals: Tag,
  group_orders: Users,
  rewards: Star,
  reviews: Star
};

const FEATURE_CATEGORIES = {
  menu: { label: 'Menü', color: 'bg-blue-500' },
  orders: { label: 'Bestellungen', color: 'bg-green-500' },
  promotions: { label: 'Aktionen', color: 'bg-orange-500' },
  social: { label: 'Sozial', color: 'bg-purple-500' }
};

function FeatureToggles() {
  const navigate = useNavigate();
  const [features, setFeatures] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState({});

  useEffect(() => {
    loadFeatures();
  }, []);

  const loadFeatures = async () => {
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/features`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFeatures(data);
      } else if (response.status === 401) {
        toast.error('Sitzung abgelaufen');
        navigate('/admin/login');
      }
    } catch (error) {
      console.error('Error loading features:', error);
      toast.error('Fehler beim Laden der Features');
    } finally {
      setLoading(false);
    }
  };

  const toggleFeature = async (featureKey, enabled) => {
    setSaving(prev => ({ ...prev, [featureKey]: true }));
    
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/features/${featureKey}?enabled=${enabled}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        setFeatures(prev => ({
          ...prev,
          [featureKey]: { ...prev[featureKey], enabled }
        }));
        toast.success(`${features[featureKey]?.name} ${enabled ? 'aktiviert' : 'deaktiviert'}`);
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fehler beim Ändern');
      }
    } catch (error) {
      console.error('Error toggling feature:', error);
      toast.error('Fehler beim Ändern des Features');
    } finally {
      setSaving(prev => ({ ...prev, [featureKey]: false }));
    }
  };

  const initializeFeatures = async () => {
    try {
      const token = sessionStorage.getItem('adminToken');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/features/initialize`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        toast.success('Features initialisiert');
        loadFeatures();
      }
    } catch (error) {
      console.error('Error initializing features:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Group features by category
  const featuresByCategory = Object.entries(features).reduce((acc, [key, feature]) => {
    const cat = feature.category || 'other';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push({ key, ...feature });
    return acc;
  }, {});

  return (
    <div className="space-y-6" data-testid="feature-toggles">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-4">
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
              <Settings className="h-6 w-6 text-primary" />
              Feature-Verwaltung
            </h1>
            <p className="text-muted-foreground">
              Aktiviere oder deaktiviere Features auf der Website
            </p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadFeatures}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Aktualisieren
          </Button>
          {Object.keys(features).length === 0 && (
            <Button onClick={initializeFeatures}>
              Features initialisieren
            </Button>
          )}
        </div>
      </div>

      {/* Info Alert */}
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Deaktivierte Features werden auf der Website ausgeblendet. 
          Dies ist nützlich um Features erst intern zu testen bevor sie öffentlich werden.
        </AlertDescription>
      </Alert>

      {/* Feature Cards by Category */}
      {Object.entries(FEATURE_CATEGORIES).map(([catKey, catInfo]) => {
        const catFeatures = featuresByCategory[catKey];
        if (!catFeatures || catFeatures.length === 0) return null;

        return (
          <div key={catKey} className="space-y-3">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${catInfo.color}`} />
              <h2 className="text-lg font-semibold">{catInfo.label}</h2>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {catFeatures.map((feature) => {
                const Icon = FEATURE_ICONS[feature.key] || Settings;
                
                return (
                  <Card 
                    key={feature.key}
                    className={`transition-all ${feature.enabled ? 'border-green-500/50' : 'border-border opacity-75'}`}
                  >
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3">
                          <div className={`p-2 rounded-lg ${feature.enabled ? 'bg-green-500/10' : 'bg-muted'}`}>
                            <Icon className={`h-5 w-5 ${feature.enabled ? 'text-green-500' : 'text-muted-foreground'}`} />
                          </div>
                          
                          <div>
                            <h3 className="font-semibold flex items-center gap-2">
                              {feature.name}
                              {feature.enabled ? (
                                <Badge variant="outline" className="text-green-600 border-green-500/50">
                                  <Eye className="h-3 w-3 mr-1" />
                                  Sichtbar
                                </Badge>
                              ) : (
                                <Badge variant="outline" className="text-muted-foreground">
                                  <EyeOff className="h-3 w-3 mr-1" />
                                  Ausgeblendet
                                </Badge>
                              )}
                            </h3>
                            <p className="text-sm text-muted-foreground mt-1">
                              {feature.description}
                            </p>
                          </div>
                        </div>
                        
                        <Switch
                          checked={feature.enabled}
                          onCheckedChange={(checked) => toggleFeature(feature.key, checked)}
                          disabled={saving[feature.key]}
                          className="shrink-0"
                        />
                      </div>
                      
                      {feature.updated_by && (
                        <p className="text-xs text-muted-foreground mt-3 pt-3 border-t">
                          Zuletzt geändert von {feature.updated_by}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        );
      })}

      {Object.keys(features).length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Settings className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Keine Features konfiguriert</h3>
            <p className="text-muted-foreground mb-4">
              Klicken Sie auf "Features initialisieren" um die Standard-Features einzurichten.
            </p>
            <Button onClick={initializeFeatures}>
              Features initialisieren
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default FeatureToggles;

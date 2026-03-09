import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import {
  Building2,
  Palette,
  Layout,
  Upload,
  MapPin,
  Rocket,
  Check,
  ChevronRight,
  ChevronLeft,
  Loader2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const TEMPLATES = [
  {
    id: 'modern',
    name: 'Modern',
    description: 'Wolt/Lieferando Style - Minimalistisch & schnell',
    preview: '/templates/modern-preview.png'
  },
  {
    id: 'classic',
    name: 'Classic Restaurant',
    description: 'Traditionell & elegant',
    preview: '/templates/classic-preview.png'
  },
  {
    id: 'minimal',
    name: 'Minimal Fast',
    description: 'Ultra-schnell & simpel',
    preview: '/templates/minimal-preview.png'
  }
];

const TenantOnboardingWizard = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [tenantId, setTenantId] = useState(null);
  
  // Step 1: Tenant Info
  const [tenantInfo, setTenantInfo] = useState({
    name: '',
    slug: '',
    admin_email: '',
    admin_password: '',
    language: 'de',
    timezone: 'Europe/Berlin'
  });
  
  // Step 2: Branding
  const [branding, setBranding] = useState({
    logo_url: null,
    primary_color: '#DC2626',
    accent_color: '#F59E0B',
    font_family: 'Inter'
  });
  
  // Step 3: Template
  const [selectedTemplate, setSelectedTemplate] = useState('modern');
  
  // Step 4: Menu CSV
  const [csvFile, setCsvFile] = useState(null);
  const [csvPreview, setCsvPreview] = useState(null);
  
  // Step 5: Location
  const [location, setLocation] = useState({
    name: '',
    address: '',
    postal_code: '',
    city: '',
    phone: '',
    email: ''
  });
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  const token = localStorage.getItem('token');
  
  const steps = [
    { num: 1, title: 'Tenant erstellen', icon: Building2 },
    { num: 2, title: 'Branding', icon: Palette },
    { num: 3, title: 'Template', icon: Layout },
    { num: 4, title: 'Menü Import', icon: Upload },
    { num: 5, title: 'Standort', icon: MapPin },
    { num: 6, title: 'Live schalten', icon: Rocket }
  ];
  
  const progress = (currentStep / steps.length) * 100;
  
  // Auto-generate slug from name
  const handleNameChange = (name) => {
    setTenantInfo(prev => ({
      ...prev,
      name,
      slug: name.toLowerCase()
        .replace(/ä/g, 'ae')
        .replace(/ö/g, 'oe')
        .replace(/ü/g, 'ue')
        .replace(/ß/g, 'ss')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '')
    }));
  };
  
  // Step 1: Create Tenant
  const createTenant = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/super-admin/tenants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(tenantInfo)
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Erstellen');
      }
      
      const result = await response.json();
      setTenantId(result.tenant_id);
      toast.success('Tenant erstellt!');
      setCurrentStep(2);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  // Step 2: Update Branding
  const saveBranding = async () => {
    if (!tenantId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/super-admin/tenants/${tenantId}/branding`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(branding)
      });
      
      if (!response.ok) throw new Error('Fehler beim Speichern');
      
      toast.success('Branding gespeichert!');
      setCurrentStep(3);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  // Step 3: Update Template
  const saveTemplate = async () => {
    if (!tenantId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/super-admin/tenants/${tenantId}/template`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ template_id: selectedTemplate })
      });
      
      if (!response.ok) throw new Error('Fehler');
      
      toast.success('Template gespeichert!');
      setCurrentStep(4);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  // Step 4: Import CSV
  const handleCsvUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setCsvFile(file);
    
    // Read and preview
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.split('\n').slice(0, 6);
      setCsvPreview(lines.join('\n'));
    };
    reader.readAsText(file);
  };
  
  const importMenu = async () => {
    if (!csvFile || !tenantId) return;
    
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', csvFile);
      
      const response = await fetch(`${backendUrl}/api/super-admin/tenants/${tenantId}/import-menu`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (!response.ok) throw new Error('Import fehlgeschlagen');
      
      const result = await response.json();
      toast.success(`${result.products_created} Produkte, ${result.categories_created} Kategorien importiert!`);
      setCurrentStep(5);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  // Step 5: Create Location (simplified - can be expanded)
  const createLocation = async () => {
    setLoading(true);
    try {
      // Create location via existing API
      // For now, skip to publish
      toast.success('Standort konfiguriert!');
      setCurrentStep(6);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  // Step 6: Publish
  const publishTenant = async () => {
    if (!tenantId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/super-admin/tenants/${tenantId}/publish`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Fehler beim Veröffentlichen');
      
      toast.success('🎉 Tenant ist jetzt live!');
      setTimeout(() => navigate('/admin/tenants'), 2000);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Neuen Kunden anlegen</h1>
          <p className="text-muted-foreground">In wenigen Minuten zum eigenen Food Ordering Shop</p>
        </div>
        
        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step) => {
              const Icon = step.icon;
              const isComplete = currentStep > step.num;
              const isCurrent = currentStep === step.num;
              
              return (
                <div key={step.num} className="flex items-center">
                  <div className={`
                    flex items-center justify-center w-10 h-10 rounded-full border-2
                    ${
                      isComplete ? 'bg-green-500 border-green-500 text-white' :
                      isCurrent ? 'bg-primary border-primary text-white' :
                      'bg-background border-border text-muted-foreground'
                    }
                  `}>
                    {isComplete ? <Check className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
                  </div>
                  {step.num < steps.length && (
                    <div className={`w-16 h-0.5 ${
                      isComplete ? 'bg-green-500' : 'bg-border'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
          <Progress value={progress} className="h-2" />
        </div>
        
        {/* Step Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {React.createElement(steps[currentStep - 1].icon, { className: 'w-5 h-5' })}
              Schritt {currentStep}: {steps[currentStep - 1].title}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            
            {/* Step 1: Tenant Info */}
            {currentStep === 1 && (
              <div className="space-y-4">
                <div>
                  <Label>Firmenname *</Label>
                  <Input
                    value={tenantInfo.name}
                    onChange={(e) => handleNameChange(e.target.value)}
                    placeholder="z.B. Pizza Palace"
                    className="mt-2"
                  />
                </div>
                
                <div>
                  <Label>URL-Slug *</Label>
                  <Input
                    value={tenantInfo.slug}
                    onChange={(e) => setTenantInfo(prev => ({ ...prev, slug: e.target.value }))}
                    placeholder="pizza-palace"
                    className="mt-2"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Shop URL: /{tenantInfo.slug || 'ihr-slug'}
                  </p>
                </div>
                
                <div>
                  <Label>Admin Email *</Label>
                  <Input
                    type="email"
                    value={tenantInfo.admin_email}
                    onChange={(e) => setTenantInfo(prev => ({ ...prev, admin_email: e.target.value }))}
                    placeholder="admin@pizzapalace.de"
                    className="mt-2"
                  />
                </div>
                
                <div>
                  <Label>Admin Passwort *</Label>
                  <Input
                    type="password"
                    value={tenantInfo.admin_password}
                    onChange={(e) => setTenantInfo(prev => ({ ...prev, admin_password: e.target.value }))}
                    placeholder="Sicheres Passwort"
                    className="mt-2"
                  />
                </div>
                
                <Button
                  onClick={createTenant}
                  disabled={loading || !tenantInfo.name || !tenantInfo.slug || !tenantInfo.admin_email || !tenantInfo.admin_password}
                  className="w-full"
                  size="lg"
                >
                  {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <ChevronRight className="w-4 h-4 mr-2" />}
                  Tenant erstellen
                </Button>
              </div>
            )}
            
            {/* Step 2: Branding */}
            {currentStep === 2 && (
              <div className="space-y-4">
                <div>
                  <Label>Primärfarbe</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      type="color"
                      value={branding.primary_color}
                      onChange={(e) => setBranding(prev => ({ ...prev, primary_color: e.target.value }))}
                      className="w-20 h-10"
                    />
                    <Input
                      value={branding.primary_color}
                      onChange={(e) => setBranding(prev => ({ ...prev, primary_color: e.target.value }))}
                      placeholder="#DC2626"
                    />
                  </div>
                </div>
                
                <div>
                  <Label>Akzentfarbe</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      type="color"
                      value={branding.accent_color}
                      onChange={(e) => setBranding(prev => ({ ...prev, accent_color: e.target.value }))}
                      className="w-20 h-10"
                    />
                    <Input
                      value={branding.accent_color}
                      onChange={(e) => setBranding(prev => ({ ...prev, accent_color: e.target.value }))}
                      placeholder="#F59E0B"
                    />
                  </div>
                </div>
                
                {/* Preview */}
                <div className="p-6 border rounded-lg" style={{
                  background: `linear-gradient(135deg, ${branding.primary_color}22 0%, ${branding.accent_color}22 100%)`
                }}>
                  <h3 className="text-lg font-bold mb-2" style={{ color: branding.primary_color }}>
                    {tenantInfo.name}
                  </h3>
                  <Button style={{
                    backgroundColor: branding.primary_color,
                    color: 'white'
                  }}>
                    Jetzt bestellen
                  </Button>
                </div>
                
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setCurrentStep(1)} className="flex-1">
                    <ChevronLeft className="w-4 h-4 mr-2" />
                    Zurück
                  </Button>
                  <Button onClick={saveBranding} disabled={loading} className="flex-1">
                    {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <ChevronRight className="w-4 h-4 mr-2" />}
                    Weiter
                  </Button>
                </div>
              </div>
            )}
            
            {/* Step 3: Template */}
            {currentStep === 3 && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  {TEMPLATES.map(template => (
                    <button
                      key={template.id}
                      onClick={() => setSelectedTemplate(template.id)}
                      className={`p-4 border-2 rounded-lg text-left transition-all ${
                        selectedTemplate === template.id
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-primary/40'
                      }`}
                    >
                      <div className="aspect-video bg-gray-100 rounded mb-2 flex items-center justify-center">
                        <Layout className="w-8 h-8 text-gray-400" />
                      </div>
                      <h4 className="font-semibold">{template.name}</h4>
                      <p className="text-xs text-muted-foreground mt-1">{template.description}</p>
                      {selectedTemplate === template.id && (
                        <Check className="w-5 h-5 text-primary mt-2" />
                      )}
                    </button>
                  ))}
                </div>
                
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setCurrentStep(2)} className="flex-1">
                    <ChevronLeft className="w-4 h-4 mr-2" />
                    Zurück
                  </Button>
                  <Button onClick={saveTemplate} disabled={loading} className="flex-1">
                    {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <ChevronRight className="w-4 h-4 mr-2" />}
                    Weiter
                  </Button>
                </div>
              </div>
            )}
            
            {/* Step 4: CSV Upload */}
            {currentStep === 4 && (
              <div className="space-y-4">
                <div>
                  <Label>Menü CSV hochladen</Label>
                  <Input
                    type="file"
                    accept=".csv"
                    onChange={handleCsvUpload}
                    className="mt-2"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Format: category,name,description,price,price_medium,price_large,allergens
                  </p>
                </div>
                
                {csvPreview && (
                  <div>
                    <Label>Vorschau:</Label>
                    <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-x-auto">
                      {csvPreview}
                    </pre>
                  </div>
                )}
                
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setCurrentStep(3)} className="flex-1">
                    <ChevronLeft className="w-4 h-4 mr-2" />
                    Zurück
                  </Button>
                  <Button onClick={importMenu} disabled={loading || !csvFile} className="flex-1">
                    {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
                    Importieren
                  </Button>
                </div>
              </div>
            )}
            
            {/* Step 5: Location */}
            {currentStep === 5 && (
              <div className="space-y-4">
                <Alert>
                  <AlertDescription>
                    Standorte können später im Admin-Bereich verwaltet werden. 
                    Für jetzt: Weiter zum Live-Schalten.
                  </AlertDescription>
                </Alert>
                
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setCurrentStep(4)} className="flex-1">
                    <ChevronLeft className="w-4 h-4 mr-2" />
                    Zurück
                  </Button>
                  <Button onClick={createLocation} disabled={loading} className="flex-1">
                    <ChevronRight className="w-4 h-4 mr-2" />
                    Weiter
                  </Button>
                </div>
              </div>
            )}
            
            {/* Step 6: Publish */}
            {currentStep === 6 && (
              <div className="space-y-4">
                <div className="text-center py-8">
                  <Rocket className="w-16 h-16 mx-auto mb-4 text-primary" />
                  <h2 className="text-2xl font-bold mb-2">Bereit zum Live-Schalten!</h2>
                  <p className="text-muted-foreground mb-6">
                    Ihr Shop wird unter /{tenantInfo.slug} erreichbar sein.
                  </p>
                  
                  <Alert className="mb-6">
                    <AlertDescription>
                      <strong>Zusammenfassung:</strong>
                      <ul className="mt-2 space-y-1 text-left">
                        <li>• Tenant: {tenantInfo.name}</li>
                        <li>• Template: {selectedTemplate}</li>
                        <li>• Farben: {branding.primary_color} / {branding.accent_color}</li>
                        {csvFile && <li>• Menü: {csvFile.name}</li>}
                      </ul>
                    </AlertDescription>
                  </Alert>
                </div>
                
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setCurrentStep(5)} className="flex-1">
                    <ChevronLeft className="w-4 h-4 mr-2" />
                    Zurück
                  </Button>
                  <Button onClick={publishTenant} disabled={loading} className="flex-1" size="lg">
                    {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Rocket className="w-4 h-4 mr-2" />}
                    🚀 Jetzt Live schalten!
                  </Button>
                </div>
              </div>
            )}
            
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TenantOnboardingWizard;

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Plus, Eye, Settings, Rocket } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const TenantsManagement = () => {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  const token = localStorage.getItem('token');
  
  useEffect(() => {
    fetchTenants();
  }, []);
  
  const fetchTenants = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/super-admin/tenants`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Fehler');
      
      const data = await response.json();
      setTenants(data);
    } catch (error) {
      console.error(error);
      toast.error('Fehler beim Laden');
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <div className="p-6">Lädt...</div>;
  }
  
  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Tenants</h1>
          <p className="text-muted-foreground mt-1">Verwalten Sie alle Kunden</p>
        </div>
        <Button onClick={() => navigate('/admin/tenants/new')} size="lg">
          <Plus className="w-4 h-4 mr-2" />
          Neuen Kunden anlegen
        </Button>
      </div>
      
      <div className="grid gap-4">
        {tenants.map(tenant => (
          <Card key={tenant.tenant_id}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold">{tenant.name}</h3>
                  <p className="text-sm text-muted-foreground">/{tenant.slug}</p>
                  <div className="flex gap-2 mt-2">
                    <Badge variant={tenant.status === 'active' ? 'default' : 'secondary'}>
                      {tenant.status}
                    </Badge>
                    <Badge variant="outline">{tenant.template_id}</Badge>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Eye className="w-4 h-4 mr-2" />
                    Vorschau
                  </Button>
                  <Button variant="outline" size="sm">
                    <Settings className="w-4 h-4 mr-2" />
                    Bearbeiten
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default TenantsManagement;

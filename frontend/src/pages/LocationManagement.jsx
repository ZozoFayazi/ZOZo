import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import AdminLayout from '../components/AdminLayout';
import LocationDialog from '../components/LocationDialog';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
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
import { Plus, MapPin, Phone, Mail, Edit, Trash2, Globe, Clock } from 'lucide-react';

export default function LocationManagement() {
  const { token, admin, isSuperAdmin } = useAdminAuth();
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [locationToDelete, setLocationToDelete] = useState(null);

  const fetchLocations = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/admin/locations`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch locations');
      }

      const data = await response.json();
      setLocations(data.locations);
    } catch (error) {
      console.error('Fetch locations error:', error);
      toast.error('Fehler beim Laden der Filialen');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchLocations();
    }
  }, [token]);

  const handleCreateClick = () => {
    setSelectedLocation(null);
    setDialogOpen(true);
  };

  const handleEditClick = (location) => {
    setSelectedLocation(location);
    setDialogOpen(true);
  };

  const handleDeleteClick = (location) => {
    setLocationToDelete(location);
    setDeleteDialogOpen(true);
  };

  const handleDelete = async () => {
    if (!locationToDelete) return;

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/admin/locations/${locationToDelete.slug}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Fehler beim Löschen');
      }

      toast.success('Filiale gelöscht');
      fetchLocations();
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Fehler beim Löschen');
    } finally {
      setDeleteDialogOpen(false);
      setLocationToDelete(null);
    }
  };

  const handleDialogSuccess = () => {
    fetchLocations();
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="p-6">
          <p className="text-muted-foreground">Lädt...</p>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground" data-testid="locations-page-title">
              {isSuperAdmin() ? 'Filialverwaltung' : 'Meine Filiale'}
            </h1>
            <p className="text-muted-foreground mt-1">
              {isSuperAdmin() 
                ? 'Verwalten Sie alle ZOZO Burger Standorte' 
                : 'Verwalten Sie die Einstellungen Ihrer Filiale'}
            </p>
          </div>
          {isSuperAdmin() && (
            <Button onClick={handleCreateClick} data-testid="locations-add-button">
              <Plus className="h-4 w-4 mr-2" />
              Neue Filiale
            </Button>
          )}
        </div>

        {/* Locations Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {locations.map((location) => (
            <Card 
              key={location.id} 
              className="border-border hover:border-primary/50 transition-colors"
              data-testid={`location-card-${location.slug}`}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-xl">{location.name}</CardTitle>
                    <CardDescription className="mt-1">{location.slug}</CardDescription>
                  </div>
                  <Badge 
                    variant={location.is_active ? "default" : "secondary"}
                    data-testid={`location-status-${location.slug}`}
                    className={location.is_active ? "bg-[hsl(var(--success))] text-white" : ""}
                  >
                    {location.is_active ? 'Aktiv' : 'Inaktiv'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* Address */}
                <div className="flex items-start gap-2 text-sm">
                  <MapPin className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-foreground">{location.address}</p>
                    <p className="text-muted-foreground">{location.postal_code} {location.city}</p>
                  </div>
                </div>

                {/* Phone */}
                {location.phone && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <a 
                      href={`tel:${location.phone}`} 
                      className="text-foreground hover:text-primary"
                    >
                      {location.phone}
                    </a>
                  </div>
                )}

                {/* Email */}
                {location.email && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <a 
                      href={`mailto:${location.email}`} 
                      className="text-foreground hover:text-primary truncate"
                    >
                      {location.email}
                    </a>
                  </div>
                )}

                {/* Delivery Info */}
                {location.delivery_area && (
                  <div className="flex items-start gap-2 text-sm">
                    <Globe className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-foreground">
                        {location.delivery_area.mode === 'radius' 
                          ? `${location.delivery_area.radius_km} km Radius` 
                          : `${location.delivery_area.postal_codes?.length || 0} PLZ-Gebiete`}
                      </p>
                      <p className="text-muted-foreground">
                        {location.delivery_area.delivery_fee}€ Liefergebühr • 
                        Min. {location.delivery_area.min_order_value}€
                      </p>
                    </div>
                  </div>
                )}

                {/* Opening Hours */}
                <div className="flex items-start gap-2 text-sm">
                  <Clock className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-foreground">Mo-So: 11:00 - 22:45</p>
                    <p className="text-muted-foreground text-xs">{location.opening_hours?.length || 7} Tage konfiguriert</p>
                  </div>
                </div>

                {/* Actions */}
                <div className="pt-3 flex gap-2 border-t border-border">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1"
                    onClick={() => handleEditClick(location)}
                    data-testid={`location-edit-${location.slug}`}
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    Bearbeiten
                  </Button>
                  {isSuperAdmin() && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleDeleteClick(location)}
                      className="text-destructive hover:bg-destructive hover:text-destructive-foreground"
                      data-testid={`location-delete-${location.slug}`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {locations.length === 0 && (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <MapPin className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Keine Filialen vorhanden
              </h3>
              <p className="text-muted-foreground text-center mb-4">
                {isSuperAdmin() 
                  ? 'Erstellen Sie Ihre erste Filiale, um zu beginnen.' 
                  : 'Sie haben noch keinen Zugriff auf eine Filiale.'}
              </p>
              {isSuperAdmin() && (
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Erste Filiale erstellen
                </Button>
              )}
            </CardContent>
          </Card>
        )}
        </div>
      </div>

      {/* Location Dialog (Create/Edit) */}
      <LocationDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        location={selectedLocation}
        onSuccess={handleDialogSuccess}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Filiale löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              Möchten Sie wirklich die Filiale "{locationToDelete?.name}" löschen? Diese Aktion kann nicht rückgängig gemacht werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Löschen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </AdminLayout>
  );
}

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, ArrowRight, Share2, Clock, Check, MapPin, X } from 'lucide-react';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { Button } from '../components/ui/button';

function StartGroupOrder({ selectedLocation, setSelectedLocation }) {
  const navigate = useNavigate();
  const [hostName, setHostName] = useState('');
  const [hostEmail, setHostEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [showLocationDialog, setShowLocationDialog] = useState(false);
  const [locations, setLocations] = useState([]);
  const [loadingLocations, setLoadingLocations] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Load locations for the dialog
  const loadLocations = async () => {
    setLoadingLocations(true);
    try {
      const response = await fetch(`${backendUrl}/api/locations`);
      if (response.ok) {
        const data = await response.json();
        setLocations(data);
      }
    } catch (error) {
      console.error('Error loading locations:', error);
    } finally {
      setLoadingLocations(false);
    }
  };

  // Open location dialog and load locations
  const handleChangeLocation = () => {
    setShowLocationDialog(true);
    if (locations.length === 0) {
      loadLocations();
    }
  };

  // Select a location from the dialog
  const handleSelectLocation = (location) => {
    setSelectedLocation(location);
    setShowLocationDialog(false);
    toast.success(`Standort gewählt: ${location.name}`);
  };

  const createGroupOrder = async () => {
    if (!hostName.trim()) {
      toast.error('Bitte gib deinen Namen ein');
      return;
    }

    if (!selectedLocation) {
      toast.error('Bitte wähle erst einen Standort');
      setShowLocationDialog(true);
      loadLocations();
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${backendUrl}/api/group-orders/create?host_name=${encodeURIComponent(hostName)}&location_id=${selectedLocation.id}&host_email=${encodeURIComponent(hostEmail || '')}`, {
        method: 'POST'
      });

      if (response.ok) {
        const data = await response.json();
        toast.success('Gruppenbestellung erstellt! 🎉');
        navigate(`/group-order/${data.group_code}`);
      } else {
        toast.error('Fehler beim Erstellen');
      }
    } catch (error) {
      console.error('Error creating group order:', error);
      toast.error('Fehler beim Erstellen');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container mx-auto px-4 max-w-3xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Users className="h-12 w-12 text-primary" />
            <h1 className="text-4xl font-serif font-bold">Social Ordering</h1>
          </div>
          <p className="text-lg text-muted-foreground">
            Bestellt gemeinsam mit Freunden, Familie oder Kollegen!
          </p>
        </div>

        {/* How it works */}
        <div className="bg-card rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-semibold mb-6">Wie funktioniert's?</h2>
          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="bg-primary text-primary-foreground rounded-full h-8 w-8 flex items-center justify-center flex-shrink-0 font-bold">
                1
              </div>
              <div>
                <h3 className="font-semibold mb-1">Gruppenbestellung erstellen</h3>
                <p className="text-sm text-muted-foreground">
                  Du erstellst eine neue Gruppenbestellung und erhältst einen einzigartigen Code
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-primary text-primary-foreground rounded-full h-8 w-8 flex items-center justify-center flex-shrink-0 font-bold">
                2
              </div>
              <div>
                <h3 className="font-semibold mb-1 flex items-center gap-2">
                  <Share2 className="h-4 w-4" />
                  Link teilen
                </h3>
                <p className="text-sm text-muted-foreground">
                  Teile den Link mit deinen Freunden per WhatsApp, E-Mail oder Social Media
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-primary text-primary-foreground rounded-full h-8 w-8 flex items-center justify-center flex-shrink-0 font-bold">
                3
              </div>
              <div>
                <h3 className="font-semibold mb-1">Gemeinsam auswählen</h3>
                <p className="text-sm text-muted-foreground">
                  Jeder kann Items zum gemeinsamen Warenkorb hinzufügen. Ihr seht in Echtzeit, was andere bestellen
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-primary text-primary-foreground rounded-full h-8 w-8 flex items-center justify-center flex-shrink-0 font-bold">
                4
              </div>
              <div>
                <h3 className="font-semibold mb-1 flex items-center gap-2">
                  <Check className="h-4 w-4" />
                  Bestellung abschließen
                </h3>
                <p className="text-sm text-muted-foreground">
                  Der Host schließt die Bestellung ab und bezahlt. Die Bestellung wird zu euch geliefert!
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-border flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>Gruppenbestellungen sind 1 Stunde lang gültig</span>
          </div>
        </div>

        {/* Create Form */}
        <div className="bg-gradient-to-br from-primary/10 to-accent rounded-xl p-8">
          <h2 className="text-2xl font-semibold mb-6">Gruppenbestellung starten</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Dein Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={hostName}
                onChange={(e) => setHostName(e.target.value)}
                placeholder="z.B. Max Mustermann"
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                data-testid="host-name-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                E-Mail (optional)
              </label>
              <input
                type="email"
                value={hostEmail}
                onChange={(e) => setHostEmail(e.target.value)}
                placeholder="max@example.com"
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                data-testid="host-email-input"
              />
            </div>

            {/* Location Selection - Inline Dialog */}
            {selectedLocation ? (
              <div className="bg-background rounded-lg p-4 border border-border" data-testid="selected-location-box">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <MapPin className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Ausgewählter Standort:</p>
                      <p className="font-semibold">{selectedLocation.name}</p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleChangeLocation}
                    data-testid="change-location-button"
                  >
                    Ändern
                  </Button>
                </div>
              </div>
            ) : (
              <div 
                className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 cursor-pointer hover:bg-yellow-500/20 transition-colors"
                onClick={handleChangeLocation}
                data-testid="select-location-prompt"
              >
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
                    <MapPin className="h-5 w-5 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-yellow-600 dark:text-yellow-500">
                      Bitte wähle zuerst einen Standort aus
                    </p>
                    <p className="text-xs text-yellow-600/70 dark:text-yellow-500/70">
                      Klicke hier, um einen Standort zu wählen
                    </p>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={createGroupOrder}
              disabled={loading || !selectedLocation}
              className="w-full bg-primary text-primary-foreground py-4 rounded-lg hover:bg-primary/90 transition-colors font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="create-group-order-button"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Erstelle Gruppenbestellung...
                </>
              ) : (
                <>
                  Gruppenbestellung erstellen
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Location Selection Dialog */}
      <Dialog open={showLocationDialog} onOpenChange={setShowLocationDialog}>
        <DialogContent className="sm:max-w-md" data-testid="location-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-primary" />
              Standort wählen
            </DialogTitle>
            <DialogDescription>
              Wähle den Standort für deine Gruppenbestellung
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-3 py-4">
            {loadingLocations ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : locations.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">
                Keine Standorte verfügbar
              </p>
            ) : (
              locations.map((location) => (
                <button
                  key={location.id}
                  onClick={() => handleSelectLocation(location)}
                  className={`w-full p-4 rounded-lg border transition-all text-left hover:border-primary hover:bg-primary/5 ${
                    selectedLocation?.id === location.id 
                      ? 'border-primary bg-primary/10' 
                      : 'border-border'
                  }`}
                  data-testid={`location-option-${location.slug}`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{location.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {location.address}, {location.postal_code} {location.city}
                      </p>
                    </div>
                    {selectedLocation?.id === location.id && (
                      <Check className="h-5 w-5 text-primary" />
                    )}
                  </div>
                </button>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default StartGroupOrder;

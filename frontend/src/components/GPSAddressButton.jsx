import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { MapPin, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const GPSAddressButton = ({ onAddressFilled, disabled = false }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const handleGetLocation = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    // Check if geolocation is available
    if (!navigator.geolocation) {
      setError('not_available');
      setLoading(false);
      toast.error('Standort ist auf diesem Gerät gerade nicht verfügbar. Bitte Adresse manuell eingeben.');
      return;
    }

    // Request position
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        try {
          // Call reverse geocode API
          const response = await fetch(
            `${backendUrl}/api/geocode/reverse?lat=${latitude}&lng=${longitude}`
          );

          if (!response.ok) {
            throw new Error('Reverse geocode failed');
          }

          const data = await response.json();

          if (data.error) {
            setError('reverse_failed');
            toast.error('Adresse konnte nicht automatisch gefunden werden. Bitte gib sie kurz manuell ein.');
          } else if (data.success) {
            // Fill address fields
            const address = {
              street: data.house_number 
                ? `${data.street} ${data.house_number}` 
                : data.street,
              postal_code: data.postal_code,
              city: data.city
            };

            onAddressFilled(address);
            setSuccess(true);
            toast.success('Adresse eingefügt. Bitte kurz prüfen.');
          }
        } catch (err) {
          console.error('Reverse geocode error:', err);
          setError('reverse_failed');
          toast.error('Adresse konnte nicht automatisch gefunden werden. Bitte gib sie kurz manuell ein.');
        } finally {
          setLoading(false);
        }
      },
      (err) => {
        setLoading(false);

        if (err.code === 1) {
          // Permission denied
          setError('permission_denied');
          toast.error('Kein Problem. Du kannst deine Adresse einfach manuell eingeben.');
        } else if (err.code === 3) {
          // Timeout
          setError('timeout');
          toast.error('Standort konnte nicht schnell genug ermittelt werden. Bitte Adresse manuell eingeben.');
        } else {
          setError('not_available');
          toast.error('Standort ist auf diesem Gerät gerade nicht verfügbar. Bitte Adresse manuell eingeben.');
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 8000,
        maximumAge: 60000
      }
    );
  };

  return (
    <div className="space-y-3">
      <Button
        type="button"
        variant="outline"
        onClick={handleGetLocation}
        disabled={loading || disabled}
        className="w-full"
        data-testid="gps-location-button"
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Standort wird ermittelt…
          </>
        ) : (
          <>
            <MapPin className="w-4 h-4 mr-2" />
            📍 Aktuellen Standort verwenden
          </>
        )}
      </Button>

      <p className="text-xs text-muted-foreground text-center">
        Wir nutzen deinen Standort nur, um deine Adresse vorzuschlagen. Es wird nichts gespeichert.
      </p>

      {success && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Adresse eingefügt. Bitte kurz prüfen.
          </AlertDescription>
        </Alert>
      )}

      {error === 'permission_denied' && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Kein Problem. Du kannst deine Adresse einfach manuell eingeben.
            <button
              onClick={handleGetLocation}
              className="text-primary underline ml-2 text-sm"
            >
              Standortzugriff erneut versuchen
            </button>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default GPSAddressButton;

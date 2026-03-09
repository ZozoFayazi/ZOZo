import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Clock, AlertCircle, CheckCircle } from 'lucide-react';

/**
 * OpeningStatusBanner Component
 * Displays current opening status for a location
 */
const OpeningStatusBanner = ({ locationSlug, className = "" }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (!locationSlug) return;

    const fetchStatus = async () => {
      try {
        const response = await fetch(`${backendUrl}/api/locations/${locationSlug}/is-open`);
        const data = await response.json();
        setStatus(data);
      } catch (error) {
        console.error('Fetch opening status error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchStatus, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [locationSlug, backendUrl]);

  if (loading || !status) return null;

  // Format next opening time
  const formatNextOpening = (nextOpening) => {
    if (!nextOpening) return null;
    
    try {
      const date = new Date(nextOpening);
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(today.getDate() + 1);
      
      const isToday = date.toDateString() === today.toDateString();
      const isTomorrow = date.toDateString() === tomorrow.toDateString();
      
      const timeStr = date.toLocaleTimeString('de-DE', {
        hour: '2-digit',
        minute: '2-digit'
      });
      
      if (isToday) {
        return `Heute ab ${timeStr} Uhr`;
      } else if (isTomorrow) {
        return `Morgen ab ${timeStr} Uhr`;
      } else {
        return date.toLocaleDateString('de-DE', {
          weekday: 'long',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
    } catch {
      return null;
    }
  };

  if (status.is_open) {
    // Currently open
    return (
      <Alert className={`bg-green-50 border-green-200 ${className}`}>
        <CheckCircle className="h-4 w-4 text-green-600" />
        <AlertDescription className="text-green-800">
          <span className="font-semibold">Jetzt geöffnet</span>
          {status.current_slot && (
            <span className="ml-2">
              • Bis {status.current_slot.end} Uhr
            </span>
          )}
        </AlertDescription>
      </Alert>
    );
  }

  // Currently closed
  const nextOpeningText = formatNextOpening(status.next_opening);
  
  return (
    <Alert className={`bg-red-50 border-red-200 ${className}`} data-testid="closed-banner">
      <AlertCircle className="h-4 w-4 text-red-600" />
      <AlertDescription className="text-red-800">
        <div>
          <span className="font-semibold">Aktuell geschlossen</span>
          {status.reason && (
            <span className="ml-2">• {status.reason}</span>
          )}
        </div>
        {nextOpeningText && (
          <div className="mt-1 text-sm">
            Nächste Öffnung: {nextOpeningText}
          </div>
        )}
      </AlertDescription>
    </Alert>
  );
};

export default OpeningStatusBanner;

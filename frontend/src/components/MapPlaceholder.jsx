import React, { useState, useEffect } from 'react';
import { MapPin, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';

/**
 * 2-Klick Google Maps Lösung (DSGVO/TDDDG-konform)
 * 
 * Maps wird nur geladen nach:
 * 1. Explizitem Klick auf "Karte laden" Button
 * 2. Oder wenn Consent für externalMedia bereits gegeben wurde
 */
function MapPlaceholder({ address, city, className = '' }) {
  const [mapLoaded, setMapLoaded] = useState(false);
  const [hasConsent, setHasConsent] = useState(false);

  useEffect(() => {
    // Check if user has already given consent for external media
    const savedConsent = localStorage.getItem('zozo_cookie_consent');
    if (savedConsent) {
      try {
        const consent = JSON.parse(savedConsent);
        if (consent.preferences?.externalMedia) {
          setHasConsent(true);
          setMapLoaded(true);
        }
      } catch (e) {
        // Invalid consent, keep as false
      }
    }

    // Listen for consent changes
    const handleConsentChange = (event) => {
      const prefs = event.detail;
      if (prefs?.externalMedia) {
        setHasConsent(true);
        setMapLoaded(true);
      } else {
        setHasConsent(false);
        setMapLoaded(false);
      }
    };

    window.addEventListener('consentChanged', handleConsentChange);
    return () => window.removeEventListener('consentChanged', handleConsentChange);
  }, []);

  const loadMap = () => {
    // Save consent for external media
    const savedConsent = localStorage.getItem('zozo_cookie_consent');
    let consent = {
      version: CONSENT_VERSION,
      preferences: { necessary: true, statistics: false, marketing: false, externalMedia: true },
      timestamp: new Date().toISOString()
    };

    if (savedConsent) {
      try {
        const existing = JSON.parse(savedConsent);
        consent.preferences = { ...existing.preferences, externalMedia: true };
      } catch (e) {
        // Use default
      }
    }

    localStorage.setItem('zozo_cookie_consent', JSON.stringify(consent));
    window.cookieConsent = consent.preferences;
    window.dispatchEvent(new CustomEvent('consentChanged', { detail: consent.preferences }));
    
    setHasConsent(true);
    setMapLoaded(true);
  };

  const mapUrl = `https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=${encodeURIComponent(address + ', ' + city)}&zoom=15`;

  if (mapLoaded) {
    return (
      <div className={className} data-testid="google-map-loaded">
        <iframe
          src={mapUrl}
          width="100%"
          height="100%"
          style={{ border: 0, borderRadius: '0.5rem' }}
          allowFullScreen
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          title="Google Maps Standort"
        />
      </div>
    );
  }

  // Placeholder (2-Klick-Lösung)
  return (
    <div 
      className={`${className} bg-secondary/50 border-2 border-dashed border-border rounded-lg flex flex-col items-center justify-center p-8 text-center`}
      data-testid="map-placeholder"
    >
      <div className="bg-primary/10 p-4 rounded-full mb-4">
        <MapPin className="h-8 w-8 text-primary" />
      </div>
      
      <h3 className="font-semibold text-lg mb-2">Google Maps - Interaktive Karte</h3>
      
      <p className="text-sm text-muted-foreground mb-4 max-w-md">
        Durch das Laden der Karte werden Daten an Google übertragen. 
        Weitere Informationen finden Sie in unserer{' '}
        <a href="/datenschutz" className="text-primary hover:underline">
          Datenschutzerklärung
        </a>.
      </p>

      <Button 
        onClick={loadMap}
        className="bg-primary gap-2"
        data-testid="load-map-button"
      >
        <MapPin className="h-4 w-4" />
        Karte laden & Standort anzeigen
      </Button>

      {/* Alternative: Direct Google Maps link */}
      <a
        href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address + ', ' + city)}`}
        target="_blank"
        rel="noopener noreferrer"
        className="text-sm text-muted-foreground hover:text-primary transition-colors mt-4 flex items-center gap-1"
      >
        In Google Maps öffnen
        <ExternalLink className="h-3 w-3" />
      </a>
    </div>
  );
}

export default MapPlaceholder;

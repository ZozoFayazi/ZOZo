import React, { useState, useEffect } from 'react';
import { X, Cookie, Shield, BarChart3, MessageSquare, Map } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Switch } from './ui/switch';
import { Button } from './ui/button';

const CONSENT_KEY = 'zozo_cookie_consent';
const CONSENT_VERSION = '1.0';

function CookieBanner() {
  const [showBanner, setShowBanner] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [preferences, setPreferences] = useState({
    necessary: true, // Always true, locked
    statistics: false,
    marketing: false,
    externalMedia: false
  });

  useEffect(() => {
    // Check if user has already given consent
    const savedConsent = localStorage.getItem(CONSENT_KEY);
    
    if (!savedConsent) {
      // Show banner after 1 second
      setTimeout(() => setShowBanner(true), 1000);
    } else {
      // Load saved preferences
      try {
        const consent = JSON.parse(savedConsent);
        if (consent.version === CONSENT_VERSION) {
          setPreferences(consent.preferences);
          applyConsent(consent.preferences);
        } else {
          // Version mismatch - show banner again
          setShowBanner(true);
        }
      } catch (e) {
        setShowBanner(true);
      }
    }

    // Listen for manual cookie settings open
    const handleOpenSettings = () => {
      setShowSettings(true);
    };
    window.addEventListener('openCookieSettings', handleOpenSettings);
    return () => window.removeEventListener('openCookieSettings', handleOpenSettings);
  }, []);

  const saveConsent = (prefs) => {
    const consent = {
      version: CONSENT_VERSION,
      preferences: prefs,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem(CONSENT_KEY, JSON.stringify(consent));
    applyConsent(prefs);
  };

  const applyConsent = (prefs) => {
    // Apply consent settings
    // Statistics
    if (prefs.statistics) {
      // Enable analytics (currently none)
    } else {
      // Disable analytics
    }

    // Marketing
    if (prefs.marketing) {
      // Enable marketing cookies (currently none)
    } else {
      // Disable marketing
    }

    // External Media (Google Maps)
    // This is handled by the MapPlaceholder component
    window.cookieConsent = prefs;
    window.dispatchEvent(new CustomEvent('consentChanged', { detail: prefs }));
  };

  const acceptAll = () => {
    const allAccepted = {
      necessary: true,
      statistics: true,
      marketing: true,
      externalMedia: true
    };
    setPreferences(allAccepted);
    saveConsent(allAccepted);
    setShowBanner(false);
    setShowSettings(false);
  };

  const rejectAll = () => {
    const onlyNecessary = {
      necessary: true,
      statistics: false,
      marketing: false,
      externalMedia: false
    };
    setPreferences(onlyNecessary);
    saveConsent(onlyNecessary);
    setShowBanner(false);
    setShowSettings(false);
  };

  const savePreferences = () => {
    const finalPrefs = { ...preferences, necessary: true };
    saveConsent(finalPrefs);
    setShowBanner(false);
    setShowSettings(false);
  };

  const openSettings = () => {
    setShowBanner(false);
    setShowSettings(true);
  };

  if (!showBanner && !showSettings) return null;

  return (
    <>
      {/* Layer 1: Main Banner */}
      {showBanner && !showSettings && (
        <div 
          className="fixed bottom-0 left-0 right-0 z-50 bg-card border-t border-border shadow-2xl"
          data-testid="cookie-banner-layer1"
        >
          <div className="container-custom py-6">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-start gap-4 flex-1">
                <div className="bg-primary/10 p-3 rounded-lg flex-shrink-0">
                  <Cookie className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">Cookies & Datenschutz</h3>
                  <p className="text-sm text-muted-foreground">
                    Wir verwenden technisch notwendige Cookies für den Betrieb dieser Website. 
                    Mit Ihrer Zustimmung nutzen wir auch Cookies für Statistiken und externe Inhalte (Google Maps).
                    {' '}
                    <a href="/datenschutz" className="text-primary hover:underline">
                      Mehr erfahren
                    </a>
                  </p>
                </div>
              </div>

              {/* 3 gleichwertige Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                <Button
                  onClick={rejectAll}
                  variant="outline"
                  className="border-2"
                  data-testid="cookie-reject-button"
                >
                  Ablehnen
                </Button>
                <Button
                  onClick={openSettings}
                  variant="outline"
                  className="border-2"
                  data-testid="cookie-settings-button"
                >
                  Einstellungen
                </Button>
                <Button
                  onClick={acceptAll}
                  className="bg-primary"
                  data-testid="cookie-accept-button"
                >
                  Alle akzeptieren
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Layer 2: Settings Dialog */}
      <Dialog open={showSettings} onOpenChange={setShowSettings}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="cookie-settings-dialog">
          <DialogHeader>
            <DialogTitle className="text-2xl font-serif flex items-center gap-3">
              <Shield className="h-6 w-6 text-primary" />
              Cookie-Einstellungen
            </DialogTitle>
            <DialogDescription>
              Wählen Sie, welche Cookies Sie zulassen möchten. Notwendige Cookies sind für den Betrieb der Website erforderlich.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 mt-6">
            {/* Necessary Cookies */}
            <div className="flex items-start justify-between gap-4 p-4 bg-secondary/50 rounded-lg">
              <div className="flex items-start gap-3 flex-1">
                <Cookie className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold mb-1">Notwendige Cookies</h4>
                  <p className="text-sm text-muted-foreground">
                    Erforderlich für grundlegende Funktionen (Warenkorb, Session, Sicherheit). 
                    Können nicht deaktiviert werden.
                  </p>
                </div>
              </div>
              <Switch checked={true} disabled className="mt-1" data-testid="cookie-necessary-toggle" />
            </div>

            {/* Statistics */}
            <div className="flex items-start justify-between gap-4 p-4 border border-border rounded-lg">
              <div className="flex items-start gap-3 flex-1">
                <BarChart3 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold mb-1">Statistik-Cookies</h4>
                  <p className="text-sm text-muted-foreground">
                    Helfen uns zu verstehen, wie Besucher die Website nutzen (anonymisiert).
                  </p>
                </div>
              </div>
              <Switch 
                checked={preferences.statistics} 
                onCheckedChange={(checked) => setPreferences({ ...preferences, statistics: checked })}
                className="mt-1"
                data-testid="cookie-statistics-toggle"
              />
            </div>

            {/* Marketing */}
            <div className="flex items-start justify-between gap-4 p-4 border border-border rounded-lg">
              <div className="flex items-start gap-3 flex-1">
                <MessageSquare className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold mb-1">Marketing-Cookies</h4>
                  <p className="text-sm text-muted-foreground">
                    Werden verwendet, um personalisierte Werbung anzuzeigen.
                  </p>
                </div>
              </div>
              <Switch 
                checked={preferences.marketing} 
                onCheckedChange={(checked) => setPreferences({ ...preferences, marketing: checked })}
                className="mt-1"
                data-testid="cookie-marketing-toggle"
              />
            </div>

            {/* External Media */}
            <div className="flex items-start justify-between gap-4 p-4 border border-border rounded-lg">
              <div className="flex items-start gap-3 flex-1">
                <Map className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold mb-1">Externe Medien (Google Maps)</h4>
                  <p className="text-sm text-muted-foreground">
                    Ermöglicht die Anzeige von interaktiven Karten. Lädt Inhalte von Google-Servern.
                  </p>
                </div>
              </div>
              <Switch 
                checked={preferences.externalMedia} 
                onCheckedChange={(checked) => setPreferences({ ...preferences, externalMedia: checked })}
                className="mt-1"
                data-testid="cookie-external-media-toggle"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 mt-8 pt-6 border-t border-border">
            <Button
              onClick={rejectAll}
              variant="outline"
              className="flex-1"
              data-testid="cookie-settings-reject-all"
            >
              Alle ablehnen
            </Button>
            <Button
              onClick={savePreferences}
              variant="outline"
              className="flex-1"
              data-testid="cookie-settings-save"
            >
              Auswahl speichern
            </Button>
            <Button
              onClick={acceptAll}
              className="flex-1 bg-primary"
              data-testid="cookie-settings-accept-all"
            >
              Alle akzeptieren
            </Button>
          </div>

          <p className="text-xs text-muted-foreground text-center mt-4">
            Weitere Informationen finden Sie in unserer{' '}
            <a href="/datenschutz" className="text-primary hover:underline">
              Datenschutzerklärung
            </a>
          </p>
        </DialogContent>
      </Dialog>
    </>
  );
}

export default CookieBanner;

import React from 'react';
import { Building2, Mail, Phone, MapPin } from 'lucide-react';

function Impressum() {
  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container-custom max-w-4xl">
        <h1 className="text-4xl font-serif font-bold mb-8">Impressum</h1>
        
        <div className="bg-card border border-border rounded-lg p-8 space-y-6">
          <div className="space-y-4">
            <h2 className="text-2xl font-serif font-semibold text-primary">Angaben gemäß § 5 TMG</h2>
            
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <Building2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                <div>
                  <p className="font-semibold">ZOZO Burger</p>
                  <p className="text-muted-foreground">Betreiber der Online-Bestellplattform</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                <div>
                  <p className="font-semibold">Standort Rellingen:</p>
                  <p>Möwenstraße 2</p>
                  <p>25462 Rellingen</p>
                  <p className="text-muted-foreground mt-1">Deutschland</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                <div>
                  <p className="font-semibold">Standort Henstedt-Ulzburg:</p>
                  <p>Edisonstraße 11</p>
                  <p>Henstedt-Ulzburg</p>
                  <p className="text-muted-foreground mt-1">Deutschland</p>
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-border pt-6 space-y-3">
            <h3 className="text-lg font-semibold">Kontakt</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <Phone className="h-5 w-5 text-primary" />
                <a href="tel:+4941013984850" className="hover:text-primary transition-colors">
                  04101 3984 850
                </a>
              </div>
              <div className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-primary" />
                <a href="mailto:info@zozo-burger.de" className="hover:text-primary transition-colors">
                  info@zozo-burger.de
                </a>
              </div>
            </div>
          </div>

          <div className="border-t border-border pt-6 space-y-3">
            <h3 className="text-lg font-semibold">Vertreten durch</h3>
            <p className="text-muted-foreground">Inhaber: [Bitte ergänzen]</p>
            <p className="text-sm text-amber-600">⚠️ Rechtlicher Hinweis: Bitte vollständige Inhaberdaten vor Go-Live eintragen</p>
          </div>

          <div className="border-t border-border pt-6 space-y-3">
            <h3 className="text-lg font-semibold">Registereintrag</h3>
            <div className="space-y-1 text-muted-foreground">
              <p className="text-sm text-amber-600">⚠️ Falls Eintragung vorhanden, bitte ergänzen:</p>
              <p>Registergericht: [Bitte ergänzen]</p>
              <p>Registernummer: [Bitte ergänzen]</p>
            </div>
          </div>

          <div className="border-t border-border pt-6 space-y-3">
            <h3 className="text-lg font-semibold">Umsatzsteuer-ID</h3>
            <p className="text-muted-foreground">
              Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:
            </p>
            <p className="font-mono">[Bitte USt-IdNr. ergänzen]</p>
            <p className="text-sm text-amber-600">⚠️ Falls vorhanden, bitte vor Go-Live eintragen</p>
          </div>

          <div className="border-t border-border pt-6 space-y-3">
            <h3 className="text-lg font-semibold">Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h3>
            <p>[Inhaber - Bitte ergänzen]</p>
            <p className="text-muted-foreground">Anschrift wie oben</p>
          </div>

          <div className="border-t border-border pt-6 space-y-3">
            <h3 className="text-lg font-semibold">EU-Streitschlichtung</h3>
            <p className="text-muted-foreground">
              Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:
            </p>
            <a 
              href="https://ec.europa.eu/consumers/odr" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              https://ec.europa.eu/consumers/odr
            </a>
            <p className="text-muted-foreground mt-2">
              Unsere E-Mail-Adresse finden Sie oben im Impressum.
            </p>
          </div>

          <div className="border-t border-border pt-6 space-y-3">
            <h3 className="text-lg font-semibold">Verbraucherstreitbeilegung</h3>
            <p className="text-muted-foreground">
              Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer 
              Verbraucherschlichtungsstelle teilzunehmen.
            </p>
          </div>

          <div className="bg-blue-500/10 border border-blue-500/20 rounded-md p-4 mt-6">
            <p className="text-sm text-blue-600">
              <strong>Hinweis:</strong> Die obigen Angaben sind Platzhalter und müssen durch die 
              tatsächlichen Unternehmensdaten ersetzt werden.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Impressum;

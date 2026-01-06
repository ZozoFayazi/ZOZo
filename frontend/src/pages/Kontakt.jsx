import React from 'react';
import { Mail, Phone, MapPin, Clock } from 'lucide-react';

function Kontakt() {
  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container-custom max-w-4xl">
        <h1 className="text-4xl font-serif font-bold mb-8">Kontakt</h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          {/* Kontaktinformationen */}
          <div className="bg-card border border-border rounded-lg p-8 space-y-6">
            <h2 className="text-2xl font-serif font-semibold text-primary mb-4">Wie können wir Ihnen helfen?</h2>
            
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="bg-primary/10 p-3 rounded-lg">
                  <Phone className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1">Telefon</h3>
                  <a href="tel:+4940123456" className="text-primary hover:underline">
                    +49 (0) 40 123 456
                  </a>
                  <p className="text-sm text-muted-foreground mt-1">
                    Mo-So: 11:00 - 22:00 Uhr
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="bg-primary/10 p-3 rounded-lg">
                  <Mail className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1">E-Mail</h3>
                  <a href="mailto:info@zozo-burger.de" className="text-primary hover:underline">
                    info@zozo-burger.de
                  </a>
                  <p className="text-sm text-muted-foreground mt-1">
                    Wir antworten innerhalb von 24 Stunden
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="bg-primary/10 p-3 rounded-lg">
                  <MapPin className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1">Adresse</h3>
                  <p className="text-muted-foreground">
                    ZOZO Burger GmbH<br />
                    Musterstraße 123<br />
                    12345 Musterstadt
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="bg-primary/10 p-3 rounded-lg">
                  <Clock className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1">Öffnungszeiten</h3>
                  <p className="text-muted-foreground">
                    Montag - Sonntag<br />
                    11:00 - 22:45 Uhr
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Standorte */}
          <div className="bg-card border border-border rounded-lg p-8">
            <h2 className="text-2xl font-serif font-semibold text-primary mb-4">Unsere Standorte</h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">ZOZO Burger Rellingen</h3>
                <p className="text-muted-foreground text-sm mb-2">
                  Hauptstraße 70<br />
                  25462 Rellingen
                </p>
                <a 
                  href="tel:+494101234567" 
                  className="text-primary hover:underline text-sm"
                >
                  Tel: +49 (0) 4101 234 567
                </a>
              </div>

              <div className="border-t border-border pt-4">
                <h3 className="font-semibold mb-2">ZOZO Burger Henstedt-Ulzburg</h3>
                <p className="text-muted-foreground text-sm mb-2">
                  Bahnhofstraße 15<br />
                  24558 Henstedt-Ulzburg
                </p>
                <a 
                  href="tel:+494193234567" 
                  className="text-primary hover:underline text-sm"
                >
                  Tel: +49 (0) 4193 234 567
                </a>
              </div>

              <div className="border-t border-border pt-4">
                <a 
                  href="/standorte" 
                  className="btn-primary w-full text-center"
                >
                  Alle Standorte anzeigen
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-8 bg-card border border-border rounded-lg p-8">
          <h2 className="text-2xl font-serif font-semibold text-primary mb-6">Häufige Fragen</h2>
          
          <div className="space-y-4">
            <details className="group">
              <summary className="cursor-pointer font-semibold hover:text-primary transition-colors">
                Wie lange dauert die Lieferung?
              </summary>
              <p className="text-muted-foreground mt-2 pl-4">
                Die Lieferzeit beträgt in der Regel 30-45 Minuten. Die genaue Zeit erhalten Sie bei der Bestellung.
              </p>
            </details>

            <details className="group border-t border-border pt-4">
              <summary className="cursor-pointer font-semibold hover:text-primary transition-colors">
                Kann ich meine Bestellung stornieren?
              </summary>
              <p className="text-muted-foreground mt-2 pl-4">
                Eine Stornierung ist nur möglich, solange die Bestellung noch nicht in Zubereitung ist. 
                Bitte kontaktieren Sie uns umgehend telefonisch.
              </p>
            </details>

            <details className="group border-t border-border pt-4">
              <summary className="cursor-pointer font-semibold hover:text-primary transition-colors">
                Welche Zahlungsmethoden werden akzeptiert?
              </summary>
              <p className="text-muted-foreground mt-2 pl-4">
                Wir akzeptieren Barzahlung bei Lieferung sowie Online-Zahlung per Kreditkarte oder PayPal.
              </p>
            </details>

            <details className="group border-t border-border pt-4">
              <summary className="cursor-pointer font-semibold hover:text-primary transition-colors">
                Gibt es einen Mindestbestellwert?
              </summary>
              <p className="text-muted-foreground mt-2 pl-4">
                Ja, der Mindestbestellwert beträgt 12,00€. Die Lieferkosten betragen 2,50€ 
                (ab 15,00€ Bestellwert versandkostenfrei).
              </p>
            </details>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Kontakt;

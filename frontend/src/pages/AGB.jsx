import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';

function AGB() {
  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container-custom max-w-4xl">
        {/* Back Button */}
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"
        >
          <ChevronLeft className="h-4 w-4" />
          Zurück zur Startseite
        </Link>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-serif font-bold mb-4">Allgemeine Geschäftsbedingungen (AGB)</h1>
          <p className="text-muted-foreground">ZOZO Burger - Stand: Januar 2026</p>
        </div>

        {/* Content */}
        <div className="bg-card border border-border rounded-xl p-8 space-y-8">
          {/* 1. Geltungsbereich */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Geltungsbereich</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                Diese Allgemeinen Geschäftsbedingungen (AGB) gelten für alle Bestellungen über die Website 
                und mobile Anwendungen von ZOZO Burger.
              </p>
              <p>
                Betreiber: Zonik Solutions GmbH, Möwenstraße 2, 25462 Rellingen
              </p>
            </div>
          </section>

          {/* 2. Vertragsschluss */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Vertragsschluss</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                Der Vertrag kommt mit der Bestellbestätigung per E-Mail zustande. Mit der Bestellung 
                bestätigen Sie, dass Sie diese AGB gelesen und akzeptiert haben.
              </p>
              <p>
                Wir behalten uns vor, Bestellungen ohne Angabe von Gründen abzulehnen.
              </p>
            </div>
          </section>

          {/* 3. Preise und Zahlung */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Preise und Zahlung</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                Alle Preise verstehen sich in Euro inkl. der gesetzlichen Mehrwertsteuer.
              </p>
              <p>
                <strong>Zahlungsarten:</strong>
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>Barzahlung bei Lieferung oder Abholung</li>
                <li>Kartenzahlung bei Lieferung oder Abholung</li>
                <li>PayPal (Online-Zahlung)</li>
              </ul>
              <p>
                Liefergebühren: €2.50 (kostenlos ab €15 Bestellwert)
              </p>
              <p>
                Mindestbestellwert: variiert je nach Standort (€10-12)
              </p>
            </div>
          </section>

          {/* 4. Lieferung und Abholung */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Lieferung und Abholung</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                <strong>Lieferung:</strong> Die Lieferzeit beträgt ca. 30-45 Minuten. Dies sind Schätzwerte 
                und können je nach Auslastung variieren.
              </p>
              <p>
                <strong>Abholung:</strong> Ihre Bestellung ist in ca. 15 Minuten zur Abholung bereit.
              </p>
              <p>
                Wir liefern nur innerhalb unserer definierten Lieferzonen. Diese können Sie bei der 
                Eingabe Ihrer Postleitzahl einsehen.
              </p>
            </div>
          </section>

          {/* 5. Widerrufsrecht */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Widerrufsrecht</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                Gemäß § 312g Abs. 2 Nr. 1 BGB besteht bei Lieferungen von Waren, die schnell verderben 
                können oder deren Verfallsdatum schnell überschritten würde, kein Widerrufsrecht.
              </p>
              <p>
                Da wir frische Lebensmittel verkaufen, ist ein Widerruf nach Bestellbestätigung 
                ausgeschlossen.
              </p>
              <p>
                <strong>Stornierung:</strong> Sie können Ihre Bestellung telefonisch stornieren, solange 
                diese noch nicht in Zubereitung ist.
              </p>
            </div>
          </section>

          {/* 6. Gewährleistung */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Gewährleistung und Reklamation</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                Sollten Sie mit der Qualität Ihrer Bestellung nicht zufrieden sein, kontaktieren Sie 
                uns bitte umgehend telefonisch oder per E-Mail.
              </p>
              <p>
                Reklamationen nehmen wir innerhalb von 24 Stunden nach Lieferung entgegen.
              </p>
              <p>
                <strong>Kontakt:</strong> 04101 3984 850 oder info@zozo-burger.de
              </p>
            </div>
          </section>

          {/* 7. Allergene und Inhaltsstoffe */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Allergene und Inhaltsstoffe</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                Informationen zu Allergenen und Inhaltsstoffen sind in unserer Speisekarte gekennzeichnet.
              </p>
              <p>
                Trotz sorgfältiger Zubereitung können wir Spuren von Allergenen nicht vollständig 
                ausschließen (Kreuzkontamination in der Küche).
              </p>
              <p>
                Bei Fragen zu Allergenen kontaktieren Sie uns bitte VOR der Bestellung.
              </p>
            </div>
          </section>

          {/* 8. Datenschutz */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Datenschutz</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                Ihre personenbezogenen Daten werden ausschließlich zur Abwicklung Ihrer Bestellung 
                verwendet und nicht an Dritte weitergegeben.
              </p>
              <p>
                Weitere Informationen finden Sie in unserer{' '}
                <Link to="/datenschutz" className="text-primary hover:underline">
                  Datenschutzerklärung
                </Link>.
              </p>
            </div>
          </section>

          {/* 9. Haftung */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Haftungsbeschränkung</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                Wir haften für Schäden nur bei Vorsatz und grober Fahrlässigkeit. Die Haftung für 
                leicht fahrlässige Pflichtverletzungen ist ausgeschlossen, soweit nicht Schäden aus 
                der Verletzung des Lebens, des Körpers oder der Gesundheit betroffen sind.
              </p>
            </div>
          </section>

          {/* 10. Schlussbestimmungen */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">10. Schlussbestimmungen</h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts.
              </p>
              <p>
                Sollten einzelne Bestimmungen dieser AGB unwirksam sein, bleibt die Wirksamkeit 
                der übrigen Bestimmungen unberührt.
              </p>
            </div>
          </section>

          {/* Contact */}
          <section className="border-t border-border pt-8">
            <h2 className="text-2xl font-semibold mb-4">Kontakt</h2>
            <div className="space-y-2 text-muted-foreground">
              <p><strong>Zonik Solutions GmbH</strong></p>
              <p>Möwenstraße 2, 25462 Rellingen</p>
              <p>Telefon: 04101 3984 850</p>
              <p>E-Mail: info@zozo-burger.de</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default AGB;

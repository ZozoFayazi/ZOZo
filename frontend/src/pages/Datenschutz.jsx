import React from 'react';
import { Shield, Lock, Eye, UserX, FileText } from 'lucide-react';

function Datenschutz() {
  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container-custom max-w-4xl">
        <h1 className="text-4xl font-serif font-bold mb-8">Datenschutzerklärung</h1>
        
        <div className="bg-card border border-border rounded-lg p-8 space-y-8">
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <Shield className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
              <div>
                <h2 className="text-2xl font-serif font-semibold text-primary mb-2">1. Datenschutz auf einen Blick</h2>
                <p className="text-muted-foreground">
                  Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen 
                  Daten passiert, wenn Sie diese Website besuchen und bei uns bestellen.
                </p>
              </div>
            </div>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <h3 className="text-xl font-semibold">Allgemeine Hinweise</h3>
            <p className="text-muted-foreground">
              Personenbezogene Daten sind alle Daten, mit denen Sie persönlich identifiziert werden können. 
              Ausführliche Informationen zum Thema Datenschutz entnehmen Sie unserer unter diesem Text aufgeführten 
              Datenschutzerklärung.
            </p>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-xl font-semibold mb-3">2. Datenerfassung bei Bestellung</h3>
                <p className="text-muted-foreground mb-3">
                  Wir erheben folgende personenbezogene Daten, wenn Sie bei uns bestellen:
                </p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>Name und Anrede</li>
                  <li>Lieferadresse (Straße, Postleitzahl, Ort)</li>
                  <li>Telefonnummer</li>
                  <li>E-Mail-Adresse</li>
                  <li>Bestellte Produkte und Mengen</li>
                  <li>Zahlungsinformationen</li>
                </ul>
                <p className="text-muted-foreground mt-3">
                  Diese Daten sind erforderlich zur Vertragserfüllung (Lieferung Ihrer Bestellung) gemäß Art. 6 Abs. 1 lit. b DSGVO.
                </p>
              </div>
            </div>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <div className="flex items-start gap-3">
              <Lock className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-xl font-semibold mb-3">3. Cookies und Webanalyse</h3>
                <p className="text-muted-foreground mb-3">
                  Diese Website verwendet ausschließlich technisch notwendige Cookies, die für den Betrieb 
                  der Website erforderlich sind (z.B. Session-Cookie, Warenkorb).
                </p>
                <p className="text-muted-foreground">
                  <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an der 
                  Funktionsfähigkeit der Website).
                </p>
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-md p-4 mt-4">
                  <p className="text-sm text-blue-600">
                    Sie können Ihre Cookie-Einstellungen jederzeit über den Link "Cookie-Einstellungen" im Footer ändern.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <h3 className="text-xl font-semibold">4. Google Maps</h3>
            <p className="text-muted-foreground">
              Wir verwenden Google Maps zur Anzeige unserer Standorte. Die Karte wird nur geladen, 
              wenn Sie aktiv zustimmen (2-Klick-Lösung). Weitere Informationen finden Sie in der 
              <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline ml-1">
                Datenschutzerklärung von Google
              </a>.
            </p>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <h3 className="text-xl font-semibold">5. E-Mail-Versand (Resend)</h3>
            <p className="text-muted-foreground">
              Für den Versand von Bestätigungsmails nutzen wir den Dienst Resend. 
              Ihre E-Mail-Adresse wird ausschließlich zur Auftragsabwicklung verwendet.
            </p>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <h3 className="text-xl font-semibold">6. Weitergabe an POS-System</h3>
            <p className="text-muted-foreground">
              Ihre Bestelldaten werden an unser Kassensystem (POS) übertragen, um die Bestellung 
              zu verarbeiten. Dies erfolgt auf Grundlage der Vertragserfüllung (Art. 6 Abs. 1 lit. b DSGVO).
            </p>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <div className="flex items-start gap-3">
              <Eye className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-xl font-semibold mb-3">7. Ihre Rechte als Betroffener</h3>
                <p className="text-muted-foreground mb-3">
                  Sie haben folgende Rechte gemäß DSGVO:
                </p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li><strong>Auskunft:</strong> Sie können Auskunft über Ihre gespeicherten Daten verlangen (Art. 15 DSGVO)</li>
                  <li><strong>Berichtigung:</strong> Sie können die Berichtigung unrichtiger Daten verlangen (Art. 16 DSGVO)</li>
                  <li><strong>Löschung:</strong> Sie können die Löschung Ihrer Daten verlangen (Art. 17 DSGVO)</li>
                  <li><strong>Einschränkung:</strong> Sie können die Einschränkung der Verarbeitung verlangen (Art. 18 DSGVO)</li>
                  <li><strong>Widerspruch:</strong> Sie können der Verarbeitung widersprechen (Art. 21 DSGVO)</li>
                  <li><strong>Datenübertragbarkeit:</strong> Sie können Ihre Daten in einem strukturierten Format erhalten (Art. 20 DSGVO)</li>
                </ul>
                <p className="text-muted-foreground mt-4">
                  Zur Ausübung Ihrer Rechte wenden Sie sich bitte an: <a href="mailto:info@zozo-burger.de" className="text-primary hover:underline">info@zozo-burger.de</a>
                </p>
              </div>
            </div>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <h3 className="text-xl font-semibold">8. Speicherdauer</h3>
            <p className="text-muted-foreground">
              Bestelldaten werden für steuerrechtliche Zwecke 10 Jahre aufbewahrt. 
              Danach erfolgt die automatische Löschung, sofern keine anderen rechtlichen 
              Verpflichtungen bestehen.
            </p>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <div className="flex items-start gap-3">
              <UserX className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-xl font-semibold mb-3">9. Widerrufsrecht</h3>
                <p className="text-muted-foreground">
                  Sie haben das Recht, Ihre Einwilligung zur Datenverarbeitung jederzeit zu widerrufen. 
                  Der Widerruf berührt nicht die Rechtmäßigkeit der bis zum Widerruf erfolgten Verarbeitung.
                </p>
              </div>
            </div>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <h3 className="text-xl font-semibold">10. Verantwortliche Stelle</h3>
            <p className="text-muted-foreground">
              ZOZO Burger GmbH<br />
              Musterstraße 123<br />
              12345 Musterstadt<br />
              E-Mail: info@zozo-burger.de
            </p>
          </div>

          <div className="border-t border-border pt-6 space-y-4">
            <h3 className="text-xl font-semibold">11. Beschwerderecht bei Aufsichtsbehörde</h3>
            <p className="text-muted-foreground">
              Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde über die Verarbeitung 
              Ihrer personenbezogenen Daten zu beschweren.
            </p>
          </div>

          <div className="bg-blue-500/10 border border-blue-500/20 rounded-md p-4 mt-8">
            <p className="text-sm text-blue-600">
              <strong>Hinweis:</strong> Diese Datenschutzerklärung ist eine Vorlage und muss durch einen 
              Datenschutz-Generator (z.B. eRecht24) oder einen Anwalt an die tatsächlichen Gegebenheiten 
              angepasst werden.
            </p>
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-muted-foreground">
            Stand dieser Datenschutzerklärung: Januar 2026
          </p>
        </div>
      </div>
    </div>
  );
}

export default Datenschutz;

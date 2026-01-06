import React, { useState } from 'react';
import { Scale, FileText, ShieldAlert } from 'lucide-react';

function Rechtliches() {
  const [activeTab, setActiveTab] = useState('agb');

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container-custom max-w-4xl">
        <h1 className="text-4xl font-serif font-bold mb-8">Rechtliche Informationen</h1>
        
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-8 overflow-x-auto">
          <button
            onClick={() => setActiveTab('agb')}
            className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
              activeTab === 'agb'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary hover:bg-secondary/80'
            }`}
          >
            AGB
          </button>
          <button
            onClick={() => setActiveTab('widerruf')}
            className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
              activeTab === 'widerruf'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary hover:bg-secondary/80'
            }`}
          >
            Widerrufsbelehrung
          </button>
          <button
            onClick={() => setActiveTab('speisen')}
            className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
              activeTab === 'speisen'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary hover:bg-secondary/80'
            }`}
          >
            Speisen-Hinweise
          </button>
        </div>

        {/* AGB Tab */}
        {activeTab === 'agb' && (
          <div className="bg-card border border-border rounded-lg p-8 space-y-6">
            <div className="flex items-start gap-3">
              <Scale className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
              <div>
                <h2 className="text-2xl font-serif font-semibold text-primary mb-4">
                  Allgemeine Geschäftsbedingungen (AGB)
                </h2>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-2">§ 1 Geltungsbereich</h3>
                <p className="text-muted-foreground">
                  Diese Allgemeinen Geschäftsbedingungen (AGB) gelten für alle Bestellungen über die 
                  Online-Bestellplattform www.zozo-burger.de der ZOZO Burger GmbH.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">§ 2 Vertragsschluss</h3>
                <p className="text-muted-foreground mb-2">
                  Der Vertrag kommt zustande durch:
                </p>
                <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                  <li>Auswahl der Produkte und Hinzufügen zum Warenkorb</li>
                  <li>Eingabe der Lieferadresse und Kontaktdaten</li>
                  <li>Bestätigung durch Klick auf "Kostenpflichtig bestellen"</li>
                  <li>Erhalt der Bestellbestätigung per E-Mail</li>
                </ol>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">§ 3 Preise und Zahlung</h3>
                <p className="text-muted-foreground mb-2">
                  Alle Preise verstehen sich inklusive der gesetzlichen Mehrwertsteuer. 
                  Zusätzlich fallen Lieferkosten an (siehe Checkout).
                </p>
                <p className="text-muted-foreground">
                  <strong>Mindestbestellwert:</strong> 12,00€<br />
                  <strong>Lieferkosten:</strong> 2,50€ (ab 15,00€ versandkostenfrei)
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">§ 4 Lieferung</h3>
                <p className="text-muted-foreground">
                  Die Lieferung erfolgt im angegebenen Liefergebiet. Die voraussichtliche Lieferzeit 
                  wird bei der Bestellung angezeigt (in der Regel 30-45 Minuten).
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">§ 5 Gewährleistung</h3>
                <p className="text-muted-foreground">
                  Bei Mängeln der gelieferten Ware (z.B. falsche oder beschädigte Produkte) kontaktieren Sie 
                  uns bitte umgehend. Wir werden eine Ersatzlieferung veranlassen oder den Kaufpreis erstatten.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">§ 6 Haftung</h3>
                <p className="text-muted-foreground">
                  Wir haften für Schäden aus der Verletzung des Lebens, des Körpers oder der Gesundheit sowie 
                  für Schäden aus vorsätzlichen oder grob fahrlässigen Pflichtverletzungen unbeschränkt.
                </p>
              </div>
            </div>

            <div className="bg-blue-500/10 border border-blue-500/20 rounded-md p-4 mt-6">
              <p className="text-sm text-blue-600">
                <strong>Hinweis:</strong> Diese AGB sind eine Vorlage und müssen durch einen Rechtsanwalt 
                oder einen AGB-Generator (z.B. IT-Recht Kanzlei) an die tatsächlichen Geschäftsprozesse 
                angepasst werden.
              </p>
            </div>
          </div>
        )}

        {/* Widerruf Tab */}
        {activeTab === 'widerruf' && (
          <div className="bg-card border border-border rounded-lg p-8 space-y-6">
            <div className="flex items-start gap-3">
              <FileText className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
              <div>
                <h2 className="text-2xl font-serif font-semibold text-primary mb-4">
                  Widerrufsbelehrung
                </h2>
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-orange-500/10 border border-orange-500/20 rounded-md p-4">
                <h3 className="text-lg font-semibold text-orange-600 mb-2">Wichtiger Hinweis</h3>
                <p className="text-sm text-orange-600">
                  Bei Lieferungen von schnell verderblichen Lebensmitteln (wie Burger, Pizza, etc.) 
                  besteht KEIN Widerrufsrecht gemäß § 312g Abs. 2 Nr. 1 BGB.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">Ausschluss des Widerrufsrechts</h3>
                <p className="text-muted-foreground">
                  Das Widerrufsrecht besteht nicht bei Verträgen zur Lieferung von Waren, die schnell verderben 
                  können oder deren Verfallsdatum schnell überschritten würde (§ 312g Abs. 2 Nr. 1 BGB).
                </p>
                <p className="text-muted-foreground mt-2">
                  Da unsere Produkte (Burger, Pizza, Salate, etc.) frisch zubereitet werden und eine kurze 
                  Haltbarkeit haben, ist ein Widerruf nach Lieferung ausgeschlossen.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">Stornierung vor Zubereitung</h3>
                <p className="text-muted-foreground">
                  Sie können Ihre Bestellung stornieren, solange diese noch nicht in Zubereitung ist. 
                  Kontaktieren Sie uns dafür bitte umgehend telefonisch:
                </p>
                <a href="tel:+4940123456" className="text-primary hover:underline block mt-2">
                  Tel: +49 (0) 40 123 456
                </a>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">Reklamation bei Mängeln</h3>
                <p className="text-muted-foreground">
                  Bei Mängeln (falsche oder beschädigte Produkte) kontaktieren Sie uns bitte umgehend. 
                  Wir werden eine Ersatzlieferung veranlassen oder den Kaufpreis erstatten.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Speisen-Hinweise Tab */}
        {activeTab === 'speisen' && (
          <div className="bg-card border border-border rounded-lg p-8 space-y-6">
            <div className="flex items-start gap-3">
              <ShieldAlert className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
              <div>
                <h2 className="text-2xl font-serif font-semibold text-primary mb-4">
                  Allergene und Zusatzstoffe
                </h2>
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-red-500/10 border border-red-500/20 rounded-md p-4">
                <h3 className="text-lg font-semibold text-red-600 mb-2">⚠️ Wichtiger Hinweis</h3>
                <p className="text-sm text-red-600">
                  Trotz größter Sorgfalt können unsere Produkte Spuren von Allergenen enthalten. 
                  Bei Allergien oder Unverträglichkeiten kontaktieren Sie uns bitte vor der Bestellung.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">Kennzeichnungspflichtige Allergene</h3>
                <p className="text-muted-foreground mb-3">
                  Unsere Produkte können folgende Allergene enthalten:
                </p>
                <div className="grid md:grid-cols-2 gap-2">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                    <span className="text-muted-foreground">A - Glutenhaltiges Getreide</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                    <span className="text-muted-foreground">C - Eier</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                    <span className="text-muted-foreground">F - Soja</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                    <span className="text-muted-foreground">G - Milch/Laktose</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                    <span className="text-muted-foreground">J - Senf</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                    <span className="text-muted-foreground">L - Sellerie</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">Zusatzstoffe</h3>
                <p className="text-muted-foreground mb-3">
                  Folgende Zusatzstoffe können in unseren Produkten enthalten sein:
                </p>
                <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                  <li>1 - mit Farbstoff</li>
                  <li>2 - mit Konservierungsstoff</li>
                  <li>3 - mit Antioxidationsmittel</li>
                  <li>4 - mit Geschmacksverstärker</li>
                  <li>8 - geschwefelt</li>
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">Nährwertinformationen</h3>
                <p className="text-muted-foreground">
                  Detaillierte Nährwertangaben zu unseren Produkten finden Sie in unserer Speisekarte 
                  oder erfragen Sie diese telefonisch.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2">Kontakt bei Fragen</h3>
                <p className="text-muted-foreground">
                  Bei Fragen zu Allergenen oder Inhaltsstoffen erreichen Sie uns:
                </p>
                <div className="mt-2 space-y-1">
                  <p className="text-muted-foreground">
                    <strong>Telefon:</strong> <a href="tel:+4940123456" className="text-primary hover:underline">+49 (0) 40 123 456</a>
                  </p>
                  <p className="text-muted-foreground">
                    <strong>E-Mail:</strong> <a href="mailto:info@zozo-burger.de" className="text-primary hover:underline">info@zozo-burger.de</a>
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Rechtliches;

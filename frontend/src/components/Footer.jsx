import React from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Phone, Mail, Clock, Instagram, Facebook } from 'lucide-react';

function Footer() {
  return (
    <footer className="bg-accent/50 border-t border-border mt-20">
      <div className="container-custom py-12">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-xl font-serif font-bold mb-4">ZOZO BURGER</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Premium Burger, Pizza, Pasta & More. Frisch zubereitet, schnell geliefert.
            </p>
            <div className="flex gap-3">
              <a
                href="#"
                className="p-2 bg-secondary hover:bg-primary hover:text-primary-foreground rounded-lg transition-colors"
                aria-label="Instagram"
              >
                <Instagram className="h-4 w-4" />
              </a>
              <a
                href="#"
                className="p-2 bg-secondary hover:bg-primary hover:text-primary-foreground rounded-lg transition-colors"
                aria-label="Facebook"
              >
                <Facebook className="h-4 w-4" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold mb-4">Schnelllinks</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/menu" className="text-muted-foreground hover:text-primary transition-colors">
                  Speisekarte
                </Link>
              </li>
              <li>
                <Link to="/order-tracking" className="text-muted-foreground hover:text-primary transition-colors">
                  Bestellstatus
                </Link>
              </li>
              <li>
                <Link to="/locations" className="text-muted-foreground hover:text-primary transition-colors">
                  Standorte
                </Link>
              </li>
            </ul>
          </div>

          {/* Locations */}
          <div>
            <h4 className="font-semibold mb-4">Standorte</h4>
            <div className="space-y-4 text-sm text-muted-foreground">
              <div>
                <p className="font-medium text-foreground mb-1">Rellingen</p>
                <div className="flex items-start gap-2">
                  <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>Hauptstraße 30<br />25462 Rellingen</span>
                </div>
              </div>
              <div>
                <p className="font-medium text-foreground mb-1">Henstedt-Ulzburg</p>
                <div className="flex items-start gap-2">
                  <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>Hamburger Straße 115<br />24558 Henstedt-Ulzburg</span>
                </div>
              </div>
            </div>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold mb-4">Kontakt</h4>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li className="flex items-center gap-2">
                <Phone className="h-4 w-4 flex-shrink-0" />
                <a href="tel:+4941013984850" className="hover:text-primary transition-colors">
                  04101 3984 850
                </a>
              </li>
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4 flex-shrink-0" />
                <a href="mailto:info@zozo-burger.de" className="hover:text-primary transition-colors">
                  info@zozo-burger.de
                </a>
              </li>
              <li className="flex items-start gap-2">
                <Clock className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <div>
                  <p>Mo-So: 11:00 - 22:45 Uhr</p>
                </div>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-border flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} ZOZO Burger. Alle Rechte vorbehalten.
          </p>
          <div className="flex flex-wrap justify-center gap-4 md:gap-6 text-sm">
            <Link to="/impressum" className="text-muted-foreground hover:text-primary transition-colors">
              Impressum
            </Link>
            <Link to="/datenschutz" className="text-muted-foreground hover:text-primary transition-colors">
              Datenschutz
            </Link>
            <Link to="/rechtliches" className="text-muted-foreground hover:text-primary transition-colors">
              AGB
            </Link>
            <Link to="/kontakt" className="text-muted-foreground hover:text-primary transition-colors">
              Kontakt
            </Link>
            <button 
              onClick={() => window.dispatchEvent(new CustomEvent('openCookieSettings'))}
              className="text-muted-foreground hover:text-primary transition-colors cursor-pointer"
            >
              Cookie-Einstellungen
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;

import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { getLocations } from '../api';
import { MapPin, Clock, Phone, Mail, ChevronRight } from 'lucide-react';
import { Button } from '../components/ui/button';

function LocationsPage({ setSelectedLocation }) {
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    loadLocations();
  }, []);

  const loadLocations = async () => {
    try {
      const data = await getLocations();
      setLocations(data);
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  };

  const handleOrder = (location) => {
    setSelectedLocation(location);
    navigate('/menu');
  };

  // JSON-LD Schema for Locations Overview
  const locationsSchema = {
    "@context": "https://schema.org",
    "@type": "FoodEstablishment",
    "name": "ZOZO Burger",
    "description": "ZOZO Burger - Premium Burger, Pizza, Pasta & mehr. Lieferservice in Rellingen und Henstedt-Ulzburg.",
    "url": window.location.origin + "/standorte",
    "image": "https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg",
    "department": locations.map(loc => ({
      "@type": "Restaurant",
      "name": loc.name,
      "address": {
        "@type": "PostalAddress",
        "streetAddress": loc.address,
        "addressLocality": loc.city,
        "postalCode": loc.postal_code,
        "addressCountry": "DE"
      },
      "telephone": loc.phone,
      "url": `${window.location.origin}/standorte/${loc.slug}`
    }))
  };

  return (
    <>
      <Helmet>
        <title>Standorte | ZOZO Burger - Lieferservice Rellingen & Henstedt-Ulzburg</title>
        <meta name="description" content="Finde deinen ZOZO Burger Standort! Lieferservice in Rellingen und Henstedt-Ulzburg. Premium Burger, Pizza, Pasta & mehr. Schnelle Lieferung garantiert." />
        <meta name="keywords" content="ZOZO Burger Standorte, Burger Lieferservice Rellingen, Burger Lieferservice Henstedt-Ulzburg, Pizza Lieferservice Hamburg" />
        <link rel="canonical" href={`${window.location.origin}/standorte`} />
        <meta property="og:title" content="Standorte | ZOZO Burger Lieferservice" />
        <meta property="og:description" content="Finde deinen ZOZO Burger Standort! Premium Burger, Pizza & Pasta Lieferservice." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content={`${window.location.origin}/standorte`} />
        <script type="application/ld+json">
          {JSON.stringify(locationsSchema)}
        </script>
      </Helmet>
      
    <div className="min-h-screen bg-background py-16" data-testid="locations-page">
      <div className="container-custom">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="heading-2 mb-4">Unsere Standorte</h1>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Besuche uns oder bestelle bequem online. Wir liefern schnell und zuverlässig in deiner Region.
          </p>
        </div>

        {/* Locations Grid */}
        <div className="grid lg:grid-cols-2 gap-8">
          {locations.map((location) => (
            <div
              key={location.id}
              className="bg-card border border-border rounded-xl overflow-hidden card-hover"
              data-testid={location.slug === 'rellingen' ? 'rellingen-card' : 'henstedt-card'}
            >
              {/* Map Embed */}
              <div className="aspect-video bg-muted relative" data-testid="map-embed">
                <iframe
                  title={`Map of ${location.name}`}
                  src={`https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=${encodeURIComponent(location.address + ', ' + location.city)}&zoom=15`}
                  className="w-full h-full border-0"
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                />
              </div>

              {/* Details */}
              <div className="p-8 space-y-6">
                <div>
                  <h2 className="text-2xl font-serif font-semibold mb-4">{location.name}</h2>
                  
                  <div className="space-y-3 text-muted-foreground">
                    <div className="flex items-start space-x-3">
                      <MapPin className="h-5 w-5 mt-0.5 flex-shrink-0 text-primary" />
                      <div>
                        <p>{location.address}</p>
                        <p>{location.postal_code} {location.city}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <Clock className="h-5 w-5 flex-shrink-0 text-primary" />
                      <p>{location.opening_hours}</p>
                    </div>
                    
                    {location.phone && (
                      <div className="flex items-center space-x-3">
                        <Phone className="h-5 w-5 flex-shrink-0 text-primary" />
                        <a href={`tel:${location.phone}`} className="hover:text-primary transition-colors">
                          {location.phone}
                        </a>
                      </div>
                    )}
                    
                    {location.email && (
                      <div className="flex items-center space-x-3">
                        <Mail className="h-5 w-5 flex-shrink-0 text-primary" />
                        <a href={`mailto:${location.email}`} className="hover:text-primary transition-colors">
                          {location.email}
                        </a>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button
                    onClick={() => handleOrder(location)}
                    className="flex-1"
                    data-testid={`order-${location.slug}`}
                  >
                    Hier bestellen
                  </Button>
                  <Button 
                    variant="outline" 
                    asChild
                    data-testid={`details-${location.slug}`}
                  >
                    <Link to={`/standorte/${location.slug}`}>
                      Mehr Info
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="mt-16 bg-accent rounded-xl p-8 text-center">
          <h3 className="text-xl font-serif font-semibold mb-4">Liefergebiete</h3>
          <p className="text-muted-foreground mb-4">
            Wir liefern in einem Umkreis von 5 km um unsere Standorte.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <span className="px-4 py-2 bg-card border border-border rounded-full text-sm">Rellingen</span>
            <span className="px-4 py-2 bg-card border border-border rounded-full text-sm">Henstedt-Ulzburg</span>
            <span className="px-4 py-2 bg-card border border-border rounded-full text-sm">Pinneberg</span>
            <span className="px-4 py-2 bg-card border border-border rounded-full text-sm">Quickborn</span>
            <span className="px-4 py-2 bg-card border border-border rounded-full text-sm">Kaltenkirchen</span>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}

export default LocationsPage;

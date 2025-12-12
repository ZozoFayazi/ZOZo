import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Clock, Phone, ArrowRight } from 'lucide-react';
import { getLocations } from '../api';

function HomePage({ selectedLocation, setSelectedLocation }) {
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    loadLocations();
  }, []);

  const loadLocations = async () => {
    try {
      const data = await getLocations(true); // Include opening status
      setLocations(data);
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  };

  const handleOrder = (location) => {
    setSelectedLocation(location);
    navigate('/menu');
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative noise-overlay bg-gradient-to-br from-background via-background to-accent py-20 md:py-32 overflow-hidden">
        <div className="container-custom">
          <div className="grid lg:grid-cols-12 gap-12 items-center">
            {/* Text Content */}
            <div className="lg:col-span-5 space-y-6 animate-fade-in">
              <p className="eyebrow" data-testid="hero-eyebrow">
                Rellingen • Henstedt-Ulzburg
              </p>
              <h1 className="heading-1 text-foreground">
                ZOZO BURGER
              </h1>
              <p className="text-lg sm:text-xl text-primary font-serif tracking-wide uppercase">
                BURGER · PIZZA · PASTA & MORE
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Premium Qualität, frisch zubereitet und in 30-45 Minuten bei dir. 
                Genieße beste Zutaten und authentischen Geschmack.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <button
                  onClick={() => navigate('/menu')}
                  className="btn-primary"
                  data-testid="hero-primary-cta-button"
                >
                  Jetzt bestellen
                  <ArrowRight className="inline-block ml-2 h-5 w-5" />
                </button>
                <button
                  onClick={() => navigate('/menu')}
                  className="btn-secondary"
                  data-testid="hero-secondary-cta-button"
                >
                  Speisekarte ansehen
                </button>
              </div>
            </div>

            {/* Hero Image */}
            <div className="lg:col-span-7">
              <div className="relative parallax-image">
                <img
                  src="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&h=800&fit=crop"
                  alt="Premium Burger"
                  className="rounded-2xl shadow-2xl w-full h-auto object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Categories */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container-custom">
          <div className="text-center mb-12">
            <h2 className="heading-2 mb-4">Unsere Spezialitäten</h2>
            <p className="text-muted-foreground">Von saftig bis knusprig – für jeden Geschmack</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Burger */}
            <div className="group relative overflow-hidden rounded-xl bg-card border border-border card-hover cursor-pointer" onClick={() => navigate('/menu')}>
              <div className="aspect-[4/3] overflow-hidden">
                <img
                  src="https://images.unsplash.com/photo-1550547660-d9450f859349?w=600&h=450&fit=crop"
                  alt="Burger"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-serif font-semibold mb-2">Burger</h3>
                <p className="text-muted-foreground text-sm">Saftige Patties, frische Zutaten</p>
              </div>
            </div>

            {/* Pizza */}
            <div className="group relative overflow-hidden rounded-xl bg-card border border-border card-hover cursor-pointer" onClick={() => navigate('/menu')}>
              <div className="aspect-[4/3] overflow-hidden">
                <img
                  src="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&h=450&fit=crop"
                  alt="Pizza"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-serif font-semibold mb-2">Pizza</h3>
                <p className="text-muted-foreground text-sm">Knuspriger Teig, reichhaltig belegt</p>
              </div>
            </div>

            {/* Pasta */}
            <div className="group relative overflow-hidden rounded-xl bg-card border border-border card-hover cursor-pointer" onClick={() => navigate('/menu')}>
              <div className="aspect-[4/3] overflow-hidden">
                <img
                  src="https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&h=450&fit=crop"
                  alt="Pasta"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-serif font-semibold mb-2">Pasta</h3>
                <p className="text-muted-foreground text-sm">Italienische Klassiker, frisch gekocht</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Locations Section */}
      <section className="py-16 md:py-24 bg-accent">
        <div className="container-custom">
          <div className="text-center mb-12">
            <h2 className="heading-2 mb-4">Unsere Standorte</h2>
            <p className="text-muted-foreground">Wähle deinen bevorzugten Standort</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {locations.map((location) => (
              <div
                key={location.id}
                className="bg-card border border-border rounded-xl p-8 space-y-4 card-hover"
                data-testid={location.slug === 'rellingen' ? 'rellingen-card' : 'henstedt-card'}
              >
                <h3 className="text-2xl font-serif font-semibold">{location.name}</h3>
                
                <div className="space-y-3 text-muted-foreground">
                  <div className="flex items-start space-x-3">
                    <MapPin className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    <div>
                      <p>{location.address}</p>
                      <p>{location.postal_code} {location.city}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <Clock className="h-5 w-5 flex-shrink-0" />
                    <p>{location.opening_hours}</p>
                  </div>
                  
                  {location.phone && (
                    <div className="flex items-center space-x-3">
                      <Phone className="h-5 w-5 flex-shrink-0" />
                      <a href={`tel:${location.phone}`} className="hover:text-primary transition-colors">
                        {location.phone}
                      </a>
                    </div>
                  )}
                </div>

                <div className="flex gap-3 mt-4">
                  <button
                    onClick={() => handleOrder(location)}
                    className="btn-primary flex-1"
                    data-testid={`order-${location.slug}`}
                  >
                    Hier bestellen
                  </button>
                  <a
                    href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(location.address + ', ' + location.postal_code + ' ' + location.city)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary flex items-center justify-center gap-2 px-6"
                    data-testid={`route-${location.slug}`}
                  >
                    <MapPin className="h-4 w-4" />
                    Route
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container-custom">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div className="space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-4">
                <Clock className="h-8 w-8" />
              </div>
              <h3 className="text-lg font-semibold">Schnelle Lieferung</h3>
              <p className="text-muted-foreground text-sm">30-45 Minuten direkt zu dir nach Hause</p>
            </div>

            <div className="space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-4">
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold">Frische Zutaten</h3>
              <p className="text-muted-foreground text-sm">Nur beste Qualität für unsere Gerichte</p>
            </div>

            <div className="space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-4">
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold">Mit Liebe gemacht</h3>
              <p className="text-muted-foreground text-sm">Jedes Gericht wird mit Sorgfalt zubereitet</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Clock, Phone, ArrowRight, Sparkles } from 'lucide-react';
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
      {/* Hero Section - Redesigned */}
      <section className="relative noise-overlay bg-gradient-to-br from-background via-accent/30 to-background py-24 md:py-36 overflow-hidden">
        {/* Subtle Glow Effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px]" />
          <div className="absolute bottom-1/3 left-1/3 w-[400px] h-[400px] bg-primary/5 rounded-full blur-[100px]" />
        </div>

        <div className="container-custom relative z-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Text Content - Left */}
            <div className="space-y-8 animate-fade-in">
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 glass rounded-full border border-primary/20">
                <MapPin className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium tracking-wide">RELLINGEN • HENSTEDT-ULZBURG</span>
              </div>

              {/* Main Headline */}
              <div className="space-y-4">
                <h1 className="text-6xl md:text-7xl lg:text-8xl font-serif font-bold leading-none tracking-tight">
                  ZOZO<br />
                  <span className="text-primary">BURGER</span>
                </h1>
                <div className="flex items-center gap-3 text-muted-foreground text-sm tracking-[0.2em] uppercase">
                  <span className="w-12 h-px bg-primary" />
                  <span>Burger · Pizza · Pasta & More</span>
                </div>
              </div>

              {/* Description */}
              <p className="text-lg text-foreground/80 leading-relaxed max-w-lg">
                Premium Qualität, frisch zubereitet und in <span className="text-primary font-semibold">30-45 Minuten</span> bei dir. 
                Genieße beste Zutaten und authentischen Geschmack.
              </p>

              {/* Stats/Features */}
              <div className="grid grid-cols-3 gap-6 pt-4">
                <div className="text-center">
                  <p className="text-3xl font-bold text-primary">4.9</p>
                  <p className="text-xs text-muted-foreground mt-1">★★★★★</p>
                </div>
                <div className="text-center border-x border-border px-2">
                  <p className="text-3xl font-bold text-primary">30min</p>
                  <p className="text-xs text-muted-foreground mt-1">Lieferzeit</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-primary">100%</p>
                  <p className="text-xs text-muted-foreground mt-1">Frisch</p>
                </div>
              </div>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <button
                  onClick={() => setShowOrderTypeDialog(true)}
                  className="btn-primary group relative overflow-hidden shadow-lg shadow-primary/30"
                  data-testid="hero-primary-cta-button"
                >
                  <span className="relative z-10 flex items-center justify-center gap-2">
                    Jetzt bestellen
                    <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </button>
                <button
                  onClick={() => navigate('/menu')}
                  className="btn-secondary group"
                  data-testid="hero-secondary-cta-button"
                >
                  <span className="flex items-center justify-center gap-2">
                    Speisekarte ansehen
                    <Sparkles className="h-5 w-5" />
                  </span>
                </button>
              </div>
            </div>

            {/* Hero Image - Right */}
            <div className="relative animate-fade-in animation-delay-200">
              {/* Main Image */}
              <div className="relative">
                <div className="aspect-square rounded-3xl overflow-hidden glass-premium">
                  <img
                    src="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&h=1200&fit=crop"
                    alt="Premium Burger"
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
                  />
                </div>
                
                {/* Floating Badge - Top Right */}
                <div className="absolute -top-4 -right-4 glass-premium px-6 py-4 rounded-2xl border border-primary/20 shadow-xl">
                  <p className="text-xs text-muted-foreground mb-1">Ab nur</p>
                  <p className="text-2xl font-bold text-primary">€7.99</p>
                </div>

                {/* Floating Badge - Bottom Left */}
                <div className="absolute -bottom-4 -left-4 glass-premium px-6 py-4 rounded-2xl border border-primary/20 shadow-xl">
                  <div className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-primary" />
                    <div>
                      <p className="text-xs text-muted-foreground">Lieferung in</p>
                      <p className="text-lg font-bold">30-45 Min</p>
                    </div>
                  </div>
                </div>
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
                <div className="flex items-start justify-between">
                  <h3 className="text-2xl font-serif font-semibold">{location.name}</h3>
                  {location.opening_status && (
                    <span 
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${
                        location.opening_status.is_open 
                          ? 'bg-green-500/10 text-green-500 border border-green-500/20' 
                          : 'bg-red-500/10 text-red-500 border border-red-500/20'
                      }`}
                      data-testid={`status-${location.slug}`}
                    >
                      <span className={`w-2 h-2 rounded-full ${location.opening_status.is_open ? 'bg-green-500' : 'bg-red-500'}`} />
                      {location.opening_status.is_open ? 'Geöffnet' : 'Geschlossen'}
                    </span>
                  )}
                </div>
                
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
                    <div>
                      <p>{location.opening_hours}</p>
                      {location.opening_status && location.opening_status.next_opening && (
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {location.opening_status.next_opening}
                        </p>
                      )}
                    </div>
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

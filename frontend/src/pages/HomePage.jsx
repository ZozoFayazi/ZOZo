import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Clock, Phone, ArrowRight, Sparkles, ChevronLeft, ChevronRight, Users, Check } from 'lucide-react';
import { getLocations } from '../api';
import OrderTypeSelection from '../components/OrderTypeSelection';
import Reviews from '../components/Reviews';
import DailyDealBanner from '../components/DailyDealBanner';
import useEmblaCarousel from 'embla-carousel-react';

// Helper function to build full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  // Convert /uploads/... to /api/uploads/... for Kubernetes Ingress routing
  if (imageUrl.startsWith('/uploads/')) {
    return `${backendUrl}/api${imageUrl}`;
  }
  return `${backendUrl}${imageUrl}`;
};

function HomePage({ selectedLocation, setSelectedLocation }) {
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [showOrderTypeDialog, setShowOrderTypeDialog] = useState(false);
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true, duration: 30 });

  useEffect(() => {
    loadLocations();
    loadFeaturedProducts();
  }, []);

  const loadLocations = async () => {
    try {
      const data = await getLocations(true); // Include opening status
      setLocations(data);
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  };

  const loadFeaturedProducts = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/featured-products`);
      if (response.ok) {
        const data = await response.json();
        setFeaturedProducts(data);
      }
    } catch (error) {
      console.error('Error loading featured products:', error);
    }
  };

  const handleOrder = (location) => {
    setSelectedLocation(location);
    navigate('/menu');
  };

  const handleOrderTypeComplete = (data) => {
    setSelectedLocation(data.location);
    setShowOrderTypeDialog(false);
    navigate('/menu');
  };

  return (
    <>
      {/* Order Type Selection Modal */}
      {showOrderTypeDialog && (
        <OrderTypeSelection
          locations={locations}
          onComplete={handleOrderTypeComplete}
          onClose={() => setShowOrderTypeDialog(false)}
        />
      )}
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
            <div className="space-y-8 animate-fade-in" role="region" aria-label="Willkommensnachricht">
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

              {/* CTAs - Mobile Optimized */}
              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <button
                  onClick={() => setShowOrderTypeDialog(true)}
                  className="btn-primary group relative overflow-hidden shadow-lg shadow-primary/30 py-4 sm:py-3 text-lg sm:text-base active:scale-95 transition-transform"
                  data-testid="hero-primary-cta-button"
                >
                  <span className="relative z-10 flex items-center justify-center gap-2">
                    Jetzt bestellen
                    <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </button>
                <button
                  onClick={() => navigate('/menu')}
                  className="btn-secondary group py-4 sm:py-3 text-lg sm:text-base active:scale-95 transition-transform"
                  data-testid="hero-secondary-cta-button"
                >
                  <span className="flex items-center justify-center gap-2">
                    Speisekarte ansehen
                    <Sparkles className="h-5 w-5" />
                  </span>
                </button>
              </div>
            </div>

            {/* Hero Carousel - Right */}
            <div className="relative animate-fade-in animation-delay-200">
              <div className="relative">
                {featuredProducts.length > 0 ? (
                  <>
                    {/* Carousel */}
                    <div className="overflow-hidden rounded-3xl" ref={emblaRef}>
                      <div className="flex">
                        {featuredProducts.map((product) => {
                          const getBadgeStyle = (badge) => {
                            const styles = {
                              new: 'bg-blue-500',
                              limited: 'bg-orange-500',
                              bestseller: 'bg-green-500',
                              hot: 'bg-red-500'
                            };
                            return styles[badge] || 'bg-gray-500';
                          };

                          const getBadgeLabel = (badge) => {
                            const labels = {
                              new: 'NEU',
                              limited: 'Nur kurze Zeit',
                              bestseller: 'Bestseller',
                              hot: 'Hot Deal'
                            };
                            return labels[badge] || badge;
                          };

                          return (
                            <div key={product.id} className="flex-[0_0_100%] min-w-0">
                              <div className="aspect-square glass-premium relative">
                                <img loading="lazy"
                                  src={getImageUrl(product.image_url) || 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&h=1200&fit=crop'}
                                  alt={product.name}
                                  className="w-full h-full object-cover"
                                />
                                
                                {/* Product Info Overlay */}
                                <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/50 to-transparent flex items-end p-8">
                                  <div className="text-white w-full space-y-3">
                                    {/* Product Name */}
                                    <h3 className="text-3xl md:text-4xl font-serif font-bold leading-tight">
                                      {product.name}
                                    </h3>
                                    
                                    {/* Description/Ingredients */}
                                    {product.description && (
                                      <p className="text-base text-white/90 leading-relaxed line-clamp-2">
                                        {product.description}
                                      </p>
                                    )}
                                    
                                    {/* Price */}
                                    <div className="flex items-center justify-between pt-2">
                                      <div className="flex items-baseline gap-2">
                                        <span className="text-4xl font-bold text-primary font-numeric">
                                          €{(product.price_normal || product.price_medium || 0).toFixed(2)}
                                        </span>
                                        {product.price_medium && (
                                          <span className="text-sm text-white/60">
                                            ab
                                          </span>
                                        )}
                                      </div>
                                      
                                      {/* Quick Order Button */}
                                      <button
                                        onClick={() => {
                                          setShowOrderTypeDialog(true);
                                        }}
                                        className="bg-primary hover:bg-primary/90 text-white px-6 py-3 rounded-full font-semibold transition-all hover:scale-105 flex items-center gap-2"
                                        data-testid={`featured-order-${product.id}`}
                                      >
                                        Bestellen
                                        <ArrowRight className="h-4 w-4" />
                                      </button>
                                    </div>
                                  </div>
                                </div>

                                {/* Badge */}
                                {product.badge && (
                                  <div className={`absolute top-6 right-6 ${getBadgeStyle(product.badge)} text-white px-4 py-2 rounded-full text-sm font-bold shadow-lg`}>
                                    {getBadgeLabel(product.badge)}
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Carousel Navigation */}
                    {featuredProducts.length > 1 && (
                      <>
                        <button
                          onClick={() => emblaApi?.scrollPrev()}
                          className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full glass-premium flex items-center justify-center hover:bg-primary/20 transition-colors"
                        >
                          <ChevronLeft className="h-6 w-6" />
                        </button>
                        <button
                          onClick={() => emblaApi?.scrollNext()}
                          className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full glass-premium flex items-center justify-center hover:bg-primary/20 transition-colors"
                        >
                          <ChevronRight className="h-6 w-6" />
                        </button>
                      </>
                    )}
                  </>
                ) : (
                  // Fallback wenn keine Featured Products
                  <div className="aspect-square rounded-3xl overflow-hidden glass-premium">
                    <img loading="lazy"
                      src="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&h=1200&fit=crop"
                      alt="Premium Burger"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Daily Deal Banner */}
      <DailyDealBanner />

      {/* Social Ordering CTA */}
      <section className="py-12 bg-gradient-to-br from-primary/10 to-accent">
        <div className="container-custom">
          <div className="bg-card rounded-2xl p-8 md:p-12 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                <Users className="h-8 w-8 text-primary" />
                <h2 className="text-3xl font-serif font-bold">Gemeinsam bestellen?</h2>
              </div>
              <p className="text-lg text-muted-foreground mb-4">
                Perfekt für Büro, Partys oder Familien-Events! Erstellt eine Gruppenbestellung und teilt den Link.
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-primary" /> Jeder kann Items hinzufügen
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-primary" /> Alle sehen die Gesamtbestellung
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-primary" /> Einfach per Link teilen
                </li>
              </ul>
            </div>
            <div>
              <button
                onClick={() => navigate('/start-group-order')}
                className="bg-primary text-primary-foreground px-8 py-4 rounded-xl hover:bg-primary/90 transition-all font-semibold text-lg flex items-center gap-2 hover:scale-105 shadow-lg"
              >
                Gruppenbestellung starten
                <ArrowRight className="h-5 w-5" />
              </button>
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
                <img loading="lazy"
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
                <img loading="lazy"
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
                <img loading="lazy"
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

      {/* Reviews Section */}
      <Reviews />
    </div>
    </>
  );
}

export default HomePage;

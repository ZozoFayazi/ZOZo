import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Clock, Phone, ArrowRight, Sparkles, Zap, Heart } from 'lucide-react';
import { getLocations } from '../api';
import OrderTypeSelection from '../components/OrderTypeSelection';

function HomePage({ selectedLocation, setSelectedLocation }) {
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);
  const [deals, setDeals] = useState([]);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [showOrderTypeDialog, setShowOrderTypeDialog] = useState(false);

  useEffect(() => {
    loadLocations();
    
    // Subtle mouse tracking for parallax
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth - 0.5) * 20,
        y: (e.clientY / window.innerHeight - 0.5) * 20
      });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const loadLocations = async () => {
    try {
      const data = await getLocations();
      setLocations(data);
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  };

  const loadDeals = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/deals`);
      const data = await response.json();
      setDeals(data);
    } catch (error) {
      console.error('Error loading deals:', error);
    }
  };

  useEffect(() => {
    loadDeals();
  }, []);

  const handleOrder = (location) => {
    setSelectedLocation(location);
    navigate('/menu');
  };

  return (
    <div className="min-h-screen overflow-hidden">
      {/* Hero Section - Ultra Modern */}
      <section className="relative min-h-[90vh] flex items-center noise-overlay gradient-bg">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div 
            className="absolute top-20 right-20 w-96 h-96 bg-primary/20 rounded-full blur-[100px] animate-pulse"
            style={{ 
              transform: `translate(${mousePosition.x}px, ${mousePosition.y}px)`,
              transition: 'transform 0.3s ease-out'
            }}
          />
          <div 
            className="absolute bottom-20 left-20 w-80 h-80 bg-primary/10 rounded-full blur-[120px]"
            style={{ 
              transform: `translate(${-mousePosition.x}px, ${-mousePosition.y}px)`,
              transition: 'transform 0.3s ease-out'
            }}
          />
        </div>

        <div className="container-custom relative z-10">
          <div className="grid lg:grid-cols-12 gap-12 lg:gap-16 items-center">
            {/* Text Content - Left Side */}
            <div className="lg:col-span-6 space-y-8">
              <div className="space-y-6 opacity-0 animate-fade-in-up">
                <div className="flex items-center gap-3">
                  <Sparkles className="h-5 w-5 text-primary" />
                  <p className="eyebrow text-primary" data-testid="hero-eyebrow">
                    Rellingen • Henstedt-Ulzburg
                  </p>
                </div>
                
                <h1 className="heading-1">
                  <span className="block mb-2">ZOZO</span>
                  <span className="block gradient-text">BURGER</span>
                </h1>
                
                <p className="text-xl sm:text-2xl text-primary/90 font-serif tracking-wide uppercase font-semibold">
                  BURGER · PIZZA · PASTA & MORE
                </p>
                
                <p className="text-lg text-muted-foreground leading-relaxed max-w-xl">
                  Erlebe Premium-Qualität, frisch zubereitet mit Leidenschaft. 
                  In nur 30-45 Minuten direkt zu dir – heiß, lecker und unwiderstehlich.
                </p>
              </div>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4 opacity-0 animate-fade-in-up animation-delay-400">
                <button
                  onClick={() => navigate('/menu')}
                  className="btn-primary glow-primary group"
                  data-testid="hero-primary-cta-button"
                >
                  <span className="flex items-center justify-center gap-2">
                    Jetzt bestellen
                    <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </button>
                <button
                  onClick={() => navigate('/menu')}
                  className="btn-secondary"
                  data-testid="hero-secondary-cta-button"
                >
                  Speisekarte ansehen
                </button>
              </div>

              {/* Quick Stats */}
              <div className="flex flex-wrap gap-8 pt-8 opacity-0 animate-fade-in-up animation-delay-600">
                <div>
                  <div className="text-3xl font-bold text-foreground mb-1">30-45</div>
                  <div className="text-sm text-muted-foreground">Minuten Lieferzeit</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-foreground mb-1">2</div>
                  <div className="text-sm text-muted-foreground">Standorte</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-foreground mb-1">50+</div>
                  <div className="text-sm text-muted-foreground">Gerichte</div>
                </div>
              </div>
            </div>

            {/* Hero Video - Right Side with 3D Effect */}
            <div className="lg:col-span-6 opacity-0 animate-scale-in animation-delay-200">
              <div className="relative">
                {/* Main Video/Image */}
                <div className="parallax-wrapper rounded-3xl overflow-hidden shadow-2xl">
                  <div 
                    className="parallax-image relative"
                    style={{
                      transform: `translate(${mousePosition.x * 0.5}px, ${mousePosition.y * 0.5}px)`
                    }}
                  >
                    {/* Video Background */}
                    <video
                      autoPlay
                      loop
                      muted
                      playsInline
                      className="w-full h-auto object-cover"
                      poster="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&h=900&fit=crop&q=90"
                    >
                      <source src="https://cdn.pixabay.com/video/2022/01/18/104620-667158651_large.mp4" type="video/mp4" />
                      {/* Fallback to image if video doesn't load */}
                      <img
                        src="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&h=900&fit=crop&q=90"
                        alt="Premium ZOZO Burger"
                        className="w-full h-auto object-cover"
                      />
                    </video>
                  </div>
                </div>
                
                {/* Floating Badge */}
                <div className="absolute -bottom-6 -left-6 glass rounded-2xl p-6 shadow-xl">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                      <Zap className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold">Blitzschnell</div>
                      <div className="text-xs text-muted-foreground">Heiß geliefert</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Deals Section */}
      {deals.length > 0 && (
        <section className="py-16 md:py-24 bg-primary/5 relative overflow-hidden">
          {/* Background Decoration */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-primary/10 rounded-full blur-[120px]" />
          
          <div className="container-custom relative z-10">
            <div className="text-center mb-12">
              <p className="eyebrow mb-4 text-primary">Aktuelle Angebote</p>
              <h2 className="heading-2 mb-6">Spare Jetzt!</h2>
              <p className="text-lg text-muted-foreground">
                Exklusive Deals nur für kurze Zeit
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {deals.map((deal) => (
                <div
                  key={deal.id}
                  className="glass rounded-2xl overflow-hidden card-tilt cursor-pointer"
                  onClick={() => navigate('/menu')}
                >
                  {deal.image_url && (
                    <div className="aspect-video overflow-hidden">
                      <img
                        src={deal.image_url}
                        alt={deal.title}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      />
                    </div>
                  )}
                  <div className="p-6 space-y-3">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/20 text-primary text-xs font-bold uppercase tracking-wide">
                      <Sparkles className="h-3 w-3" />
                      {deal.discount_type === 'percentage' 
                        ? `${deal.discount_value}% Rabatt`
                        : `€${deal.discount_value} Rabatt`}
                    </div>
                    <h3 className="text-xl font-serif font-semibold">{deal.title}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-2">{deal.description}</p>
                    {deal.min_order_value && (
                      <p className="text-xs text-muted-foreground">
                        Ab €{deal.min_order_value} Bestellwert
                      </p>
                    )}
                    <button className="btn-primary w-full text-sm py-2">
                      Jetzt bestellen <ArrowRight className="inline h-4 w-4 ml-1" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Featured Categories - Bento Grid */}
      <section className="py-20 md:py-32 bg-background relative">
        <div className="container-custom">
          <div className="text-center mb-16">
            <p className="eyebrow mb-4">Unsere Spezialitäten</p>
            <h2 className="heading-2 mb-6">Von Saftig bis Knusprig</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Entdecke unsere vielfältige Auswahl – jedes Gericht mit Liebe zubereitet
            </p>
          </div>

          {/* Asymmetric Bento Grid */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Large Feature Card - Burger */}
            <div 
              className="md:col-span-2 group relative overflow-hidden rounded-2xl bg-card border border-border card-tilt cursor-pointer h-[400px]"
              onClick={() => navigate('/menu')}
            >
              <div className="absolute inset-0">
                <img
                  src="https://images.unsplash.com/photo-1550547660-d9450f859349?w=900&h=600&fit=crop&q=90"
                  alt="Premium Burger"
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
              </div>
              <div className="relative z-10 h-full flex flex-col justify-end p-8">
                <div className="glass-light rounded-xl p-4 inline-block">
                  <h3 className="text-3xl font-serif font-bold mb-2">Burger</h3>
                  <p className="text-muted-foreground">Saftige Patties, frische Premium-Zutaten</p>
                </div>
              </div>
            </div>

            {/* Pizza Card */}
            <div 
              className="group relative overflow-hidden rounded-2xl bg-card border border-border card-tilt cursor-pointer h-[400px]"
              onClick={() => navigate('/menu')}
            >
              <div className="absolute inset-0">
                <img
                  src="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&h=600&fit=crop&q=90"
                  alt="Pizza"
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
              </div>
              <div className="relative z-10 h-full flex flex-col justify-end p-6">
                <div className="glass-light rounded-xl p-4">
                  <h3 className="text-2xl font-serif font-bold mb-2">Pizza</h3>
                  <p className="text-sm text-muted-foreground">Knuspriger Teig, reichhaltig belegt</p>
                </div>
              </div>
            </div>

            {/* Pasta Card */}
            <div 
              className="group relative overflow-hidden rounded-2xl bg-card border border-border card-tilt cursor-pointer h-[300px]"
              onClick={() => navigate('/menu')}
            >
              <div className="absolute inset-0">
                <img
                  src="https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&h=400&fit=crop&q=90"
                  alt="Pasta"
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
              </div>
              <div className="relative z-10 h-full flex flex-col justify-end p-6">
                <div className="glass-light rounded-xl p-4">
                  <h3 className="text-2xl font-serif font-bold mb-2">Pasta</h3>
                  <p className="text-sm text-muted-foreground">Italienische Klassiker</p>
                </div>
              </div>
            </div>

            {/* Fingerfood Card */}
            <div 
              className="md:col-span-2 group relative overflow-hidden rounded-2xl bg-card border border-border card-tilt cursor-pointer h-[300px]"
              onClick={() => navigate('/menu')}
            >
              <div className="absolute inset-0">
                <img
                  src="https://images.unsplash.com/photo-1562967914-608f82629710?w=900&h=400&fit=crop&q=90"
                  alt="Fingerfood"
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
              </div>
              <div className="relative z-10 h-full flex flex-col justify-end p-6">
                <div className="glass-light rounded-xl p-4 inline-block">
                  <h3 className="text-2xl font-serif font-bold mb-2">Fingerfood & More</h3>
                  <p className="text-muted-foreground">Perfekt zum Teilen oder Snacken</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Locations Section - Modern Cards */}
      <section className="py-20 md:py-32 bg-accent/30">
        <div className="container-custom">
          <div className="text-center mb-16">
            <p className="eyebrow mb-4">Unsere Standorte</p>
            <h2 className="heading-2 mb-6">Wähle deinen Standort</h2>
            <p className="text-lg text-muted-foreground">
              Schnelle Lieferung in deiner Nähe
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {locations.map((location) => (
              <div
                key={location.id}
                className="glass rounded-3xl p-8 space-y-6 card-tilt"
                data-testid={location.slug === 'rellingen' ? 'rellingen-card' : 'henstedt-card'}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-2xl font-serif font-bold mb-2">{location.name}</h3>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                      <Sparkles className="h-3 w-3" />
                      Jetzt verfügbar
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4 text-muted-foreground">
                  <div className="flex items-start gap-3">
                    <MapPin className="h-5 w-5 mt-0.5 flex-shrink-0 text-primary" />
                    <div>
                      <p className="text-foreground">{location.address}</p>
                      <p>{location.postal_code} {location.city}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <Clock className="h-5 w-5 flex-shrink-0 text-primary" />
                    <p className="text-foreground">{location.opening_hours}</p>
                  </div>
                  
                  {location.phone && (
                    <div className="flex items-center gap-3">
                      <Phone className="h-5 w-5 flex-shrink-0 text-primary" />
                      <a href={`tel:${location.phone}`} className="hover:text-primary transition-colors text-foreground">
                        {location.phone}
                      </a>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleOrder(location)}
                  className="btn-primary w-full"
                >
                  Hier bestellen
                  <ArrowRight className="inline-block ml-2 h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section - Modern Icons */}
      <section className="py-20 md:py-32 bg-background">
        <div className="container-custom">
          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-6 group hover:scale-110 transition-transform">
                <Clock className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Blitzschnell</h3>
              <p className="text-muted-foreground leading-relaxed">
                30-45 Minuten direkt zu dir – frisch und heiß
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-6 group hover:scale-110 transition-transform">
                <Zap className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Premium Qualität</h3>
              <p className="text-muted-foreground leading-relaxed">
                Nur beste Zutaten für unsere Gerichte
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-6 group hover:scale-110 transition-transform">
                <Heart className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Mit Liebe gemacht</h3>
              <p className="text-muted-foreground leading-relaxed">
                Jedes Gericht mit Sorgfalt zubereitet
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Clock, Phone, ArrowRight, Sparkles, Zap, Heart, Star, TrendingUp } from 'lucide-react';
import { getLocations } from '../api';
import OrderTypeSelection from '../components/OrderTypeSelection';

function HomePage({ selectedLocation, setSelectedLocation }) {
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);
  const [deals, setDeals] = useState([]);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [showOrderTypeDialog, setShowOrderTypeDialog] = useState(false);

  useEffect(() => {
    loadData();
    
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 20,
        y: (e.clientY / window.innerHeight) * 20
      });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const loadData = async () => {
    try {
      const locs = await getLocations();
      setLocations(locs);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleOrder = (location) => {
    setSelectedLocation(location);
    navigate('/menu');
  };

  const handleOrderTypeComplete = ({ orderType, location }) => {
    setSelectedLocation(location);
    localStorage.setItem('orderType', orderType);
    setShowOrderTypeDialog(false);
    navigate('/menu');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* CINEMATIC HERO SECTION */}
      <section className="relative gradient-bg noise-overlay py-20 sm:py-28 lg:py-36 overflow-hidden">
        {/* Animated Glow Orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div 
            className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] animate-pulse"
            style={{ transform: `translate(${mousePosition.x}px, ${mousePosition.y}px)` }}
          />
          <div 
            className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[hsl(var(--gold))]/10 rounded-full blur-[120px] animate-pulse"
            style={{ 
              transform: `translate(${-mousePosition.x}px, ${-mousePosition.y}px)`,
              animationDelay: '1s'
            }}
          />
        </div>

        <div className="container-custom relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* LEFT: Content */}
            <div className="lg:col-span-7 space-y-8">
              {/* Eyebrow with Gold Accent */}
              <div className="inline-flex items-center gap-2 px-4 py-2 glass rounded-full border border-[hsl(var(--gold))]/20">
                <Star className="h-4 w-4 text-[hsl(var(--gold))]" />
                <span className="eyebrow text-foreground">Rellingen • Henstedt-Ulzburg</span>
              </div>

              {/* Main Headline - MASSIVE */}
              <div className="space-y-4 opacity-0 animate-fade-in-up">
                <h1 className="heading-1 text-6xl sm:text-7xl lg:text-8xl">
                  ZOZO
                  <span className="block gradient-text">BURGER</span>
                </h1>
                <p className="text-xl sm:text-2xl text-muted-foreground font-medium tracking-wide">
                  BURGER · PIZZA · PASTA & MORE
                </p>
              </div>

              {/* Value Props with Glass Cards */}
              <div className="grid grid-cols-3 gap-4 opacity-0 animate-fade-in-up animation-delay-200">
                <div className="glass p-4 rounded-2xl text-center hover:scale-105 transition-transform">
                  <Zap className="h-6 w-6 text-primary mx-auto mb-2" />
                  <p className="text-xs font-medium">Schnelle Lieferung</p>
                </div>
                <div className="glass p-4 rounded-2xl text-center hover:scale-105 transition-transform">
                  <Heart className="h-6 w-6 text-[hsl(var(--gold))] mx-auto mb-2" />
                  <p className="text-xs font-medium">Premium Qualität</p>
                </div>
                <div className="glass p-4 rounded-2xl text-center hover:scale-105 transition-transform">
                  <Star className="h-6 w-6 text-primary mx-auto mb-2" />
                  <p className="text-xs font-medium">Top bewertet</p>
                </div>
              </div>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4 opacity-0 animate-fade-in-up animation-delay-400">
                <button
                  onClick={() => setShowOrderTypeDialog(true)}
                  className="btn-primary glow-primary group relative overflow-hidden"
                  data-testid="hero-primary-cta-button"
                >
                  <span className="flex items-center justify-center gap-2 relative z-10">
                    <Sparkles className="h-5 w-5" />
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
                    <TrendingUp className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </button>
              </div>
            </div>

            {/* RIGHT: Hero Image with Parallax */}
            <div className="lg:col-span-5 relative opacity-0 animate-fade-in-up animation-delay-600">
              <div className="parallax-wrapper aspect-square relative">
                <div 
                  className="parallax-image w-full h-full bg-cover bg-center rounded-3xl glass-premium"
                  style={{
                    backgroundImage: `url('https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=90')`,
                    transform: `translateY(${mousePosition.y * 0.5}px) scale(1.05)`
                  }}
                />
                {/* Floating Badge */}
                <div className="absolute top-6 right-6 glass-premium px-6 py-3 rounded-2xl gold-accent-border">
                  <p className="font-numeric text-2xl font-bold text-[hsl(var(--gold))]">4.9</p>
                  <p className="text-xs text-muted-foreground">⭐⭐⭐⭐⭐</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CATEGORIES BENTO GRID */}
      <section className="py-20 sm:py-28 bg-accent/30">
        <div className="container-custom">
          <div className="text-center mb-16 space-y-4">
            <h2 className="heading-2">Entdecke unser Angebot</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Von saftigen Burgern bis zu knuspriger Pizza – bei uns findest du alles für deinen Hunger
            </p>
          </div>

          {/* Bento Grid Layout */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { name: 'Burger', emoji: '🍔', color: 'primary' },
              { name: 'Pizza', emoji: '🍕', color: 'warning' },
              { name: 'Pasta', emoji: '🍝', color: 'success' },
              { name: 'Salate', emoji: '🥗', color: 'info' },
              { name: 'Desserts', emoji: '🍰', color: 'gold' },
              { name: 'Getränke', emoji: '🥤', color: 'primary' }
            ].map((cat, idx) => (
              <button
                key={cat.name}
                onClick={() => navigate('/menu')}
                className="glass-premium p-6 rounded-3xl hover:scale-105 transition-all duration-300 group relative overflow-hidden"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-[hsl(var(--${cat.color}))]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative z-10 text-center space-y-3">
                  <div className="text-5xl mb-2">{cat.emoji}</div>
                  <p className="font-semibold text-lg">{cat.name}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* LOCATIONS */}
      <section className="py-20 sm:py-28 noise-overlay">
        <div className="container-custom">
          <div className="text-center mb-16 space-y-4">
            <h2 className="heading-2">Unsere Standorte</h2>
            <p className="text-muted-foreground text-lg">Zwei Filialen in deiner Nähe</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {locations.map((location, idx) => (
              <div 
                key={location.id}
                className="glass-premium p-8 rounded-3xl card-tilt group relative overflow-hidden"
                style={{ animationDelay: `${idx * 200}ms` }}
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl" />
                <div className="relative z-10 space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-2xl font-serif font-semibold mb-2">{location.name}</h3>
                      <div className="space-y-2 text-muted-foreground">
                        <p className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-primary" />
                          {location.address}
                        </p>
                        <p className="flex items-center gap-2">
                          <Phone className="h-4 w-4 text-primary" />
                          {location.phone}
                        </p>
                        {location.hours && (
                          <p className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-primary" />
                            {location.hours}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleOrder(location)}
                    className="w-full mt-6 bg-secondary hover:bg-primary text-foreground hover:text-primary-foreground px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 group-hover:shadow-[0_8px_24px_rgba(176,0,32,0.3)]"
                  >
                    Hier bestellen
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Order Type Selection Dialog */}
      {showOrderTypeDialog && (
        <OrderTypeSelection
          locations={locations}
          onComplete={handleOrderTypeComplete}
          onClose={() => setShowOrderTypeDialog(false)}
        />
      )}
    </div>
  );
}

export default HomePage;
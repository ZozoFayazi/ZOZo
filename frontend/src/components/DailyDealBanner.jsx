import React, { useState, useEffect } from 'react';
import { Clock, Percent, Gift, Tag } from 'lucide-react';

/**
 * DailyDealBanner - Zeigt das aktuelle Tagesangebot auf der Startseite
 */
function DailyDealBanner() {
  const [deal, setDeal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeLeft, setTimeLeft] = useState('');

  useEffect(() => {
    loadTodayDeal();
    
    // Update countdown every minute
    const interval = setInterval(() => {
      updateTimeLeft();
    }, 60000);
    
    return () => clearInterval(interval);
  }, []);

  const loadTodayDeal = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/daily-deal`);
      if (response.ok) {
        const data = await response.json();
        if (data && data.title) {
          setDeal(data);
        }
      }
    } catch (error) {
      console.error('Error loading daily deal:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateTimeLeft = () => {
    const now = new Date();
    const endOfDay = new Date();
    endOfDay.setHours(23, 59, 59, 999);
    
    const diff = endOfDay - now;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    setTimeLeft(`${hours}h ${minutes}m`);
  };

  useEffect(() => {
    updateTimeLeft();
  }, []);

  if (loading) {
    return (
      <div className="bg-gradient-to-r from-primary/10 to-accent animate-pulse h-24 rounded-2xl" />
    );
  }

  if (!deal) {
    return null;
  }

  const getDiscountIcon = () => {
    if (deal.discount_type === '2for1') {
      return <Gift className="h-6 w-6" />;
    }
    return <Percent className="h-6 w-6" />;
  };

  const getDiscountText = () => {
    if (deal.discount_type === '2for1') {
      return '2 für 1';
    }
    return `-${deal.discount_value}%`;
  };

  return (
    <section className="py-6" data-testid="daily-deal-banner">
      <div className="container-custom">
        <div 
          className="relative overflow-hidden rounded-2xl"
          style={{
            background: `linear-gradient(135deg, ${deal.badge_color}15 0%, ${deal.badge_color}05 100%)`
          }}
        >
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-5">
            <div 
              className="absolute inset-0"
              style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              }}
            />
          </div>

          <div className="relative flex flex-col md:flex-row items-center justify-between p-6 md:p-8 gap-6">
            {/* Left: Deal Info */}
            <div className="flex items-center gap-4 md:gap-6">
              {/* Badge */}
              <div 
                className="flex-shrink-0 w-16 h-16 md:w-20 md:h-20 rounded-2xl flex items-center justify-center text-white shadow-lg"
                style={{ backgroundColor: deal.badge_color }}
              >
                <span className="text-2xl md:text-3xl font-bold">
                  {deal.discount_type === '2for1' ? '2:1' : `${deal.discount_value}%`}
                </span>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Tag className="h-4 w-4 text-primary" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-primary">
                    {deal.weekday_name} Angebot
                  </span>
                </div>
                <h3 className="text-xl md:text-2xl font-bold text-foreground mb-1">
                  {deal.title}
                </h3>
                <p className="text-sm md:text-base text-muted-foreground">
                  {deal.description}
                </p>
              </div>
            </div>

            {/* Right: Timer & CTA */}
            <div className="flex flex-col items-center md:items-end gap-3">
              {/* Countdown */}
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>Endet in <strong className="text-foreground">{timeLeft}</strong></span>
              </div>

              {/* Badge */}
              <div 
                className="px-4 py-2 rounded-full text-white font-semibold text-sm shadow-md"
                style={{ backgroundColor: deal.badge_color }}
              >
                {deal.badge_text}
              </div>
            </div>
          </div>

          {/* Decorative Image (if available) */}
          {deal.image_url && (
            <div className="absolute -right-10 -bottom-10 w-40 h-40 opacity-20 pointer-events-none hidden lg:block">
              <img 
                src={deal.image_url} 
                alt="" 
                className="w-full h-full object-cover rounded-full"
              />
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default DailyDealBanner;

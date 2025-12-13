import React, { useState, useEffect } from 'react';
import { Star, Trophy, Gift, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

function LoyaltyPoints({ customerEmail }) {
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (customerEmail) {
      loadLoyaltyAccount();
    }
  }, [customerEmail]);

  const loadLoyaltyAccount = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/loyalty/account/${customerEmail}`);
      
      if (response.ok) {
        const data = await response.json();
        setAccount(data);
      }
    } catch (error) {
      console.error('Error loading loyalty account:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!customerEmail) return null;
  if (loading) {
    return (
      <div className="bg-gradient-to-br from-primary/10 to-accent rounded-xl p-6 animate-pulse">
        <div className="h-6 bg-muted rounded w-1/3 mb-2"></div>
        <div className="h-8 bg-muted rounded w-1/2"></div>
      </div>
    );
  }

  if (!account) return null;

  const pointsValue = (account.points * 0.50).toFixed(2);

  return (
    <div className="bg-gradient-to-br from-primary/10 via-accent to-primary/5 rounded-xl p-6 border-2 border-primary/20">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Star className="h-6 w-6 text-primary fill-primary" />
          <h3 className="text-lg font-semibold">Deine Treuepunkte</h3>
        </div>
        <Trophy className="h-5 w-5 text-primary/60" />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-background/50 backdrop-blur-sm rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <Gift className="h-4 w-4 text-primary" />
            <p className="text-xs text-muted-foreground">Verfügbar</p>
          </div>
          <p className="text-2xl font-bold text-primary">{account.points}</p>
          <p className="text-xs text-muted-foreground mt-1">= €{pointsValue}</p>
        </div>

        <div className="bg-background/50 backdrop-blur-sm rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="h-4 w-4 text-green-500" />
            <p className="text-xs text-muted-foreground">Gesamt</p>
          </div>
          <p className="text-2xl font-bold text-foreground">{account.total_earned}</p>
          <p className="text-xs text-muted-foreground mt-1">verdient</p>
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs text-muted-foreground bg-background/30 rounded-lg p-3">
        <Star className="h-4 w-4 text-primary" />
        <p>10€ ausgeben = 1 Punkt sammeln | 1 Punkt = 0,50€ Wert</p>
      </div>

      {account.achievements && account.achievements.length > 0 && (
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground mb-2">
            {account.achievements.length} Achievement{account.achievements.length !== 1 ? 's' : ''} freigeschaltet
          </p>
        </div>
      )}
    </div>
  );
}

export default LoyaltyPoints;

import React, { useState, useEffect } from 'react';
import { Gift, Star, Trophy, Lock, ChevronRight } from 'lucide-react';
import { toast } from 'sonner';
import LoyaltyPoints from '../components/LoyaltyPoints';

function RewardsPage() {
  const [rewards, setRewards] = useState([]);
  const [achievements, setAchievements] = useState([]);
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('rewards'); // 'rewards', 'achievements', 'history'

  const customerEmail = localStorage.getItem('customerEmail');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

      // Load rewards catalog
      const rewardsRes = await fetch(`${backendUrl}/api/loyalty/rewards`);
      if (rewardsRes.ok) {
        const data = await rewardsRes.json();
        setRewards(data);
      }

      // Load achievements
      const achievementsRes = await fetch(`${backendUrl}/api/loyalty/achievements`);
      if (achievementsRes.ok) {
        const data = await achievementsRes.json();
        setAchievements(data);
      }

      // Load account if email exists
      if (customerEmail) {
        const accountRes = await fetch(`${backendUrl}/api/loyalty/account/${customerEmail}`);
        if (accountRes.ok) {
          const data = await accountRes.json();
          setAccount(data);
        }

        const transactionsRes = await fetch(`${backendUrl}/api/loyalty/transactions/${customerEmail}?limit=10`);
        if (transactionsRes.ok) {
          const data = await transactionsRes.json();
          setTransactions(data);
        }
      }
    } catch (error) {
      console.error('Error loading rewards data:', error);
      toast.error('Fehler beim Laden der Belohnungen');
    } finally {
      setLoading(false);
    }
  };

  const canAfford = (pointsNeeded) => {
    if (!account) return false;
    return account.points >= pointsNeeded;
  };

  const isAchievementUnlocked = (achievementId) => {
    if (!account) return false;
    return account.achievements?.includes(achievementId);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background py-12">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="text-muted-foreground mt-4">Lade Belohnungen...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Gift className="h-10 w-10 text-primary" />
            <h1 className="text-4xl font-serif font-bold">ZOZO Belohnungen</h1>
          </div>
          <p className="text-muted-foreground">Sammle Punkte und sichere dir leckere Belohnungen</p>
        </div>

        {/* Loyalty Points Card */}
        {customerEmail ? (
          <div className="mb-8">
            <LoyaltyPoints customerEmail={customerEmail} />
          </div>
        ) : (
          <div className="bg-accent rounded-xl p-6 mb-8 text-center border-2 border-dashed border-border">
            <Lock className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <h3 className="font-semibold mb-2">Melde dich an, um Punkte zu sammeln</h3>
            <p className="text-sm text-muted-foreground">
              Gib einfach deine E-Mail bei der nächsten Bestellung an
            </p>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          <button
            onClick={() => setActiveTab('rewards')}
            className={`px-6 py-3 rounded-lg whitespace-nowrap transition-all ${
              activeTab === 'rewards'
                ? 'bg-primary text-primary-foreground'
                : 'bg-card border border-border hover:border-primary/40'
            }`}
          >
            🎁 Belohnungen
          </button>
          <button
            onClick={() => setActiveTab('achievements')}
            className={`px-6 py-3 rounded-lg whitespace-nowrap transition-all ${
              activeTab === 'achievements'
                ? 'bg-primary text-primary-foreground'
                : 'bg-card border border-border hover:border-primary/40'
            }`}
          >
            🏆 Achievements
          </button>
          {customerEmail && (
            <button
              onClick={() => setActiveTab('history')}
              className={`px-6 py-3 rounded-lg whitespace-nowrap transition-all ${
                activeTab === 'history'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-card border border-border hover:border-primary/40'
              }`}
            >
              📜 Historie
            </button>
          )}
        </div>

        {/* Content */}
        {activeTab === 'rewards' && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Einlösbare Belohnungen</h2>
            <p className="text-muted-foreground mb-6">
              Löse deine Punkte gegen jedes Menü-Item ein. Nutze sie beim Checkout!
            </p>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 stagger-animation">
              {rewards.map((reward) => {
                const affordable = canAfford(reward.points_needed);
                return (
                  <div
                    key={reward.id}
                    className={`bg-card rounded-xl overflow-hidden border-2 transition-all duration-300 ${
                      affordable
                        ? 'border-primary/40 hover:border-primary hover:shadow-lg hover:-translate-y-1 card-interactive'
                        : 'border-border opacity-60'
                    }`}
                  >
                    {reward.image && (
                      <div className="h-40 bg-accent overflow-hidden">
                        <img
                          src={reward.image}
                          alt={reward.name}
                          className="w-full h-full object-cover"
                          loading="lazy"
                        />
                      </div>
                    )}
                    <div className="p-4">
                      <h3 className="font-semibold mb-1">{reward.name}</h3>
                      {reward.description && (
                        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                          {reward.description}
                        </p>
                      )}
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-1 text-primary font-bold">
                            <Star className="h-4 w-4 fill-primary" />
                            <span>{reward.points_needed}</span>
                          </div>
                          <p className="text-xs text-muted-foreground">Punkte</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground">oder</p>
                          <p className="font-semibold">€{reward.price_euro.toFixed(2)}</p>
                        </div>
                      </div>
                      {affordable && (
                        <div className="mt-3 text-xs text-green-500 font-medium flex items-center gap-1">
                          <ChevronRight className="h-3 w-3" />
                          Beim Checkout einlösbar
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === 'achievements' && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Achievements</h2>
            <p className="text-muted-foreground mb-6">
              Schalte Achievements frei und verdiene Bonus-Punkte
            </p>
            <div className="grid sm:grid-cols-2 gap-4">
              {achievements.map((achievement) => {
                const unlocked = isAchievementUnlocked(achievement.id);
                return (
                  <div
                    key={achievement.id}
                    className={`bg-card rounded-xl p-6 border-2 transition-all ${
                      unlocked
                        ? 'border-primary/40 bg-primary/5'
                        : 'border-border'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`text-5xl ${!unlocked && 'grayscale opacity-40'}`}>
                        {achievement.icon}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold">{achievement.name}</h3>
                          {unlocked && (
                            <Trophy className="h-4 w-4 text-primary fill-primary" />
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {achievement.description}
                        </p>
                        <div className="flex items-center gap-1 text-xs">
                          <Star className="h-3 w-3 text-primary" />
                          <span className="text-primary font-semibold">
                            +{achievement.bonus_points} Bonus-Punkte
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Punkte-Historie</h2>
            <div className="space-y-3">
              {transactions.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <p>Noch keine Transaktionen</p>
                </div>
              ) : (
                transactions.map((transaction) => (
                  <div
                    key={transaction.id}
                    className="bg-card rounded-lg p-4 border border-border flex items-center justify-between"
                  >
                    <div>
                      <p className="font-medium">{transaction.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(transaction.created_at).toLocaleDateString('de-DE', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <div className={`font-bold text-lg ${
                      transaction.points > 0 ? 'text-green-500' : 'text-red-500'
                    }`}>
                      {transaction.points > 0 ? '+' : ''}{transaction.points}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default RewardsPage;

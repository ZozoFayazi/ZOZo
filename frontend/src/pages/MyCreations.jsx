import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChefHat, Heart, Share2, ShoppingCart, Plus } from 'lucide-react';
import { toast } from 'sonner';

function MyCreations({ addToCart }) {
  const navigate = useNavigate();
  const [myBurgers, setMyBurgers] = useState([]);
  const [publicBurgers, setPublicBurgers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('mine'); // 'mine' or 'community'

  useEffect(() => {
    loadBurgers();
  }, [tab]);

  const loadBurgers = async () => {
    setLoading(true);
    try {
      const email = localStorage.getItem('lastCustomerEmail');
      
      if (tab === 'mine' && email) {
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/custom-burgers?email=${email}`
        );
        if (response.ok) {
          const data = await response.json();
          setMyBurgers(data);
        }
      } else if (tab === 'community') {
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/custom-burgers?public_only=true`
        );
        if (response.ok) {
          const data = await response.json();
          setPublicBurgers(data.sort((a, b) => b.votes - a.votes));
        }
      }
    } catch (error) {
      console.error('Error loading burgers:', error);
    } finally {
      setLoading(false);
    }
  };

  const voteBurger = async (burgerId) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/custom-burgers/${burgerId}/vote`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        toast.success('Vote gezählt!');
        loadBurgers();
      }
    } catch (error) {
      console.error('Error voting:', error);
      toast.error('Fehler beim Voten');
    }
  };

  const addBurgerToCart = (burger) => {
    addToCart({
      id: burger.id,
      name: burger.name,
      price: burger.price,
      size: null,
      customizations: {
        custom_burger: true,
        bun: burger.bun,
        patty: burger.patty,
        patty_count: burger.patty_count,
        cheese: burger.cheese,
        toppings: burger.toppings,
        sauces: burger.sauces
      }
    });
    toast.success(`"${burger.name}" zum Warenkorb hinzugefügt!`);
  };

  const shareBurger = async (burger) => {
    const shareUrl = `${window.location.origin}/burger/${burger.id}`;
    
    if (navigator.share) {
      await navigator.share({
        title: burger.name,
        text: `Schau dir meinen Custom Burger "${burger.name}" an!`,
        url: shareUrl
      });
    } else {
      navigator.clipboard.writeText(shareUrl);
      toast.success('Link wurde kopiert!');
    }
  };

  const burgers = tab === 'mine' ? myBurgers : publicBurgers;

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container-custom">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-4">
            <ChefHat className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium text-primary">Burger Kreationen</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-serif font-bold mb-2">
            Signature Burgers
          </h1>
          <p className="text-muted-foreground">
            Deine Kreationen und die besten aus der Community
          </p>
        </div>

        {/* Create Button */}
        <div className="text-center mb-8">
          <button
            onClick={() => navigate('/burger-builder')}
            className="btn-primary flex items-center gap-2 mx-auto"
          >
            <Plus className="h-5 w-5" />
            Neuen Burger kreieren
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-border">
          <button
            onClick={() => setTab('mine')}
            className={`px-4 py-2 font-medium transition-colors ${
              tab === 'mine'
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Meine Kreationen
          </button>
          <button
            onClick={() => setTab('community')}
            className={`px-4 py-2 font-medium transition-colors ${
              tab === 'community'
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Community Hits
          </button>
        </div>

        {/* Burgers Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : burgers.length === 0 ? (
          <div className="bg-accent rounded-lg p-12 text-center">
            <ChefHat className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">
              {tab === 'mine' 
                ? 'Du hast noch keine Burger kreiert. Leg los!' 
                : 'Noch keine Community-Kreationen verfügbar'}
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {burgers.map((burger) => (
              <div
                key={burger.id}
                className="bg-card border border-border rounded-xl p-6 hover:border-primary/30 transition-colors"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg mb-1">{burger.name}</h3>
                    {burger.description && (
                      <p className="text-sm text-muted-foreground">{burger.description}</p>
                    )}
                  </div>
                  {tab === 'community' && (
                    <button
                      onClick={() => voteBurger(burger.id)}
                      className="flex items-center gap-1 px-2 py-1 bg-primary/10 hover:bg-primary/20 rounded-lg transition-colors"
                    >
                      <Heart className="h-4 w-4 text-primary" />
                      <span className="text-sm font-medium">{burger.votes}</span>
                    </button>
                  )}
                </div>

                {/* Ingredients */}
                <div className="space-y-2 text-sm mb-4">
                  <p className="text-muted-foreground">
                    {burger.patty_count}x {burger.patty.charAt(0).toUpperCase() + burger.patty.slice(1)} Patty
                  </p>
                  {burger.cheese && (
                    <p className="text-muted-foreground">
                      + {burger.cheese.charAt(0).toUpperCase() + burger.cheese.slice(1)} Käse
                    </p>
                  )}
                  {burger.toppings.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {burger.toppings.map((topping, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 bg-secondary rounded-full text-xs"
                        >
                          {topping}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Price & Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-border">
                  <p className="text-2xl font-bold text-primary">€{burger.price.toFixed(2)}</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => shareBurger(burger)}
                      className="p-2 hover:bg-secondary rounded-lg transition-colors"
                      title="Teilen"
                    >
                      <Share2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => addBurgerToCart(burger)}
                      className="btn-primary px-4 py-2 flex items-center gap-2"
                    >
                      <ShoppingCart className="h-4 w-4" />
                      Bestellen
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default MyCreations;

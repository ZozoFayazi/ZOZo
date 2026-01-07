import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChefHat, Share2, Save, ShoppingCart, Heart, Star } from 'lucide-react';
import { toast } from 'sonner';
import BurgerPreview from '../components/BurgerPreview';

function BurgerBuilder({ addToCart }) {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [burger, setBurger] = useState({
    name: '',
    bun: '',
    patty: '',
    patty_count: 1,
    cheese: null,
    toppings: [],
    sauces: [],
    is_public: false
  });

  const bunOptions = [
    { value: 'brioche', label: 'Brioche Bun', price: 0, emoji: '🍔' },
    { value: 'sesame', label: 'Sesam Bun', price: 0.5, emoji: '🍔' },
    { value: 'whole_wheat', label: 'Vollkorn Bun', price: 0.5, emoji: '🥖' }
  ];

  const pattyOptions = [
    { value: 'beef', label: 'Beef Patty', price: 4.50, emoji: '🥩' },
    { value: 'chicken', label: 'Chicken Patty', price: 4.00, emoji: '🍗' },
    { value: 'veggie', label: 'Veggie Patty', price: 4.00, emoji: '🥬' },
    { value: 'vegan', label: 'Vegan Patty', price: 4.50, emoji: '🌱' }
  ];

  const cheeseOptions = [
    { value: null, label: 'Kein Käse', price: 0, emoji: '❌' },
    { value: 'cheddar', label: 'Cheddar', price: 1.00, emoji: '🧀' },
    { value: 'swiss', label: 'Swiss', price: 1.00, emoji: '🧀' },
    { value: 'blue', label: 'Blauschimmel', price: 1.50, emoji: '🧀' },
    { value: 'vegan', label: 'Veganer Käse', price: 1.50, emoji: '🌱' }
  ];

  const toppingOptions = [
    { value: 'lettuce', label: 'Salat', price: 0.50, emoji: '🥬' },
    { value: 'tomato', label: 'Tomate', price: 0.50, emoji: '🍅' },
    { value: 'onions', label: 'Zwiebeln', price: 0.50, emoji: '🧅' },
    { value: 'pickles', label: 'Gurken', price: 0.50, emoji: '🥒' },
    { value: 'bacon', label: 'Bacon', price: 2.00, emoji: '🥓' },
    { value: 'egg', label: 'Spiegelei', price: 1.50, emoji: '🍳' },
    { value: 'jalapenos', label: 'Jalapeños', price: 0.75, emoji: '🌶️' },
    { value: 'avocado', label: 'Avocado', price: 2.00, emoji: '🥑' }
  ];

  const sauceOptions = [
    { value: 'ketchup', label: 'Ketchup', price: 0, emoji: '🍅' },
    { value: 'mayo', label: 'Mayo', price: 0, emoji: '🥚' },
    { value: 'bbq', label: 'BBQ Sauce', price: 0.50, emoji: '🍖' },
    { value: 'ranch', label: 'Ranch', price: 0.50, emoji: '🥗' },
    { value: 'special', label: 'ZOZO Special', price: 1.00, emoji: '✨' }
  ];

  const calculatePrice = () => {
    let price = 0;
    
    // Bun
    const bunOption = bunOptions.find(b => b.value === burger.bun);
    if (bunOption) price += bunOption.price;
    
    // Patty
    const pattyOption = pattyOptions.find(p => p.value === burger.patty);
    if (pattyOption) price += pattyOption.price * burger.patty_count;
    
    // Cheese
    if (burger.cheese) {
      const cheeseOption = cheeseOptions.find(c => c.value === burger.cheese);
      if (cheeseOption) price += cheeseOption.price;
    }
    
    // Toppings
    burger.toppings.forEach(topping => {
      const toppingOption = toppingOptions.find(t => t.value === topping);
      if (toppingOption) price += toppingOption.price;
    });
    
    // Sauces
    burger.sauces.forEach(sauce => {
      const sauceOption = sauceOptions.find(s => s.value === sauce);
      if (sauceOption) price += sauceOption.price;
    });
    
    return price;
  };

  const toggleTopping = (topping) => {
    if (burger.toppings.includes(topping)) {
      setBurger({ ...burger, toppings: burger.toppings.filter(t => t !== topping) });
    } else {
      setBurger({ ...burger, toppings: [...burger.toppings, topping] });
    }
  };

  const toggleSauce = (sauce) => {
    if (burger.sauces.includes(sauce)) {
      setBurger({ ...burger, sauces: burger.sauces.filter(s => s !== sauce) });
    } else {
      setBurger({ ...burger, sauces: [...burger.sauces, sauce] });
    }
  };

  const canProceed = () => {
    if (step === 1) return burger.bun;
    if (step === 2) return burger.patty;
    if (step === 5) return burger.name.trim();
    return true;
  };

  const saveBurger = async () => {
    try {
      const email = localStorage.getItem('lastCustomerEmail');
      const burgerData = {
        ...burger,
        price: calculatePrice(),
        created_by: email || 'anonymous'
      };

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/custom-burgers`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(burgerData)
        }
      );

      if (response.ok) {
        const saved = await response.json();
        toast.success(`"${burger.name}" wurde gespeichert!`);
        return saved.id;
      }
    } catch (error) {
      console.error('Error saving burger:', error);
      toast.error('Fehler beim Speichern');
    }
  };

  const addToCartAndContinue = async () => {
    const burgerId = await saveBurger();
    
    addToCart({
      id: burgerId || 'custom-' + Date.now(),
      name: burger.name || 'Mein Custom Burger',
      price: calculatePrice(),
      size: null,
      customizations: {
        custom_burger: true,
        ...burger
      }
    });

    toast.success('Burger zum Warenkorb hinzugefügt!');
    navigate('/menu');
  };

  const shareBurger = async () => {
    const burgerId = await saveBurger();
    if (burgerId) {
      const shareUrl = `${window.location.origin}/burger/${burgerId}`;
      
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
    }
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container-custom max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-4">
            <ChefHat className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium text-primary">Burger Builder</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-serif font-bold mb-2">
            Kreiere deinen Signature Burger
          </h1>
          <p className="text-muted-foreground">
            Step {step} von 5 - {['Brötchen', 'Patty', 'Extras', 'Saucen', 'Finalisieren'][step - 1]}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="h-2 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${(step / 5) * 100}%` }}
            />
          </div>
        </div>

        {/* 2-Column Layout: Builder + Preview */}
        <div className="grid lg:grid-cols-[1fr,350px] gap-8 mb-6">
          {/* Left: Step Content */}
          <div className="bg-card border border-border rounded-xl p-6">
          {/* Step 1: Bun Selection */}
          {step === 1 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Wähle dein Brötchen</h2>
              <div className="grid md:grid-cols-3 gap-4">
                {bunOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setBurger({ ...burger, bun: option.value })}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      burger.bun === option.value
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/40'
                    }`}
                  >
                    <div className="text-4xl mb-2">{option.emoji}</div>
                    <p className="font-semibold">{option.label}</p>
                    <p className="text-sm text-muted-foreground">
                      {option.price === 0 ? 'Inklusive' : `+€${option.price.toFixed(2)}`}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Patty Selection */}
          {step === 2 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Wähle dein Patty</h2>
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                {pattyOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setBurger({ ...burger, patty: option.value })}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      burger.patty === option.value
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/40'
                    }`}
                  >
                    <div className="text-4xl mb-2">{option.emoji}</div>
                    <p className="font-semibold">{option.label}</p>
                    <p className="text-sm text-muted-foreground">€{option.price.toFixed(2)}</p>
                  </button>
                ))}
              </div>

              {/* Patty Count */}
              <div className="bg-accent rounded-lg p-4">
                <p className="font-semibold mb-3">Anzahl Patties</p>
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setBurger({ ...burger, patty_count: Math.max(1, burger.patty_count - 1) })}
                    className="btn-secondary px-4 py-2"
                  >
                    −
                  </button>
                  <span className="text-2xl font-bold">{burger.patty_count}</span>
                  <button
                    onClick={() => setBurger({ ...burger, patty_count: Math.min(3, burger.patty_count + 1) })}
                    className="btn-secondary px-4 py-2"
                  >
                    +
                  </button>
                </div>

                {/* Cheese Selection */}
                <div className="mt-6">
                  <p className="font-semibold mb-3">Käse</p>
                  <div className="grid grid-cols-3 gap-2">
                    {cheeseOptions.map((option) => (
                      <button
                        key={option.value || 'none'}
                        onClick={() => setBurger({ ...burger, cheese: option.value })}
                        className={`p-2 rounded-lg border text-sm transition-all ${
                          burger.cheese === option.value
                            ? 'border-primary bg-primary/10'
                            : 'border-border hover:border-primary/40'
                        }`}
                      >
                        <div className="text-2xl mb-1">{option.emoji}</div>
                        <p className="text-xs">{option.label}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Toppings */}
          {step === 3 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Wähle deine Toppings</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {toppingOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => toggleTopping(option.value)}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      burger.toppings.includes(option.value)
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/40'
                    }`}
                  >
                    <div className="text-3xl mb-1">{option.emoji}</div>
                    <p className="text-sm font-semibold">{option.label}</p>
                    <p className="text-xs text-muted-foreground">+€{option.price.toFixed(2)}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 4: Sauces */}
          {step === 4 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Wähle deine Saucen</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {sauceOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => toggleSauce(option.value)}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      burger.sauces.includes(option.value)
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/40'
                    }`}
                  >
                    <div className="text-3xl mb-1">{option.emoji}</div>
                    <p className="text-sm font-semibold">{option.label}</p>
                    <p className="text-xs text-muted-foreground">
                      {option.price === 0 ? 'Gratis' : `+€${option.price.toFixed(2)}`}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 5: Finalize */}
          {step === 5 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Gib deinem Burger einen Namen</h2>
              <input
                type="text"
                value={burger.name}
                onChange={(e) => setBurger({ ...burger, name: e.target.value })}
                placeholder="z.B. Der Ultimative ZOZO"
                className="w-full px-4 py-3 bg-background border-2 border-border rounded-lg focus:border-primary focus:outline-none mb-6"
                maxLength={50}
              />

              {/* Preview */}
              <div className="bg-accent rounded-lg p-6 mb-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Deine Kreation
                </h3>
                <div className="space-y-2 text-sm">
                  <p><span className="text-muted-foreground">Brötchen:</span> {bunOptions.find(b => b.value === burger.bun)?.label}</p>
                  <p><span className="text-muted-foreground">Patty:</span> {burger.patty_count}x {pattyOptions.find(p => p.value === burger.patty)?.label}</p>
                  {burger.cheese && <p><span className="text-muted-foreground">Käse:</span> {cheeseOptions.find(c => c.value === burger.cheese)?.label}</p>}
                  {burger.toppings.length > 0 && (
                    <p><span className="text-muted-foreground">Toppings:</span> {burger.toppings.map(t => toppingOptions.find(o => o.value === t)?.label).join(', ')}</p>
                  )}
                  {burger.sauces.length > 0 && (
                    <p><span className="text-muted-foreground">Saucen:</span> {burger.sauces.map(s => sauceOptions.find(o => o.value === s)?.label).join(', ')}</p>
                  )}
                </div>
              </div>

              {/* Make Public */}
              <label className="flex items-center gap-2 mb-4 cursor-pointer">
                <input
                  type="checkbox"
                  checked={burger.is_public}
                  onChange={(e) => setBurger({ ...burger, is_public: e.target.checked })}
                  className="w-4 h-4"
                />
                <span className="text-sm">Öffentlich machen (andere können deine Kreation sehen & voten)</span>
              </label>
            </div>
          )}
          </div>

          {/* Right: Live Preview */}
          <div className="hidden lg:block">
            <BurgerPreview burger={burger} />
          </div>
        </div>

        {/* Price & Navigation */}
        <div className="flex items-center justify-between">
          <div>
            {step > 1 && (
              <button
                onClick={() => setStep(step - 1)}
                className="btn-secondary"
              >
                Zurück
              </button>
            )}
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Gesamtpreis</p>
              <p className="text-2xl font-bold text-primary">€{calculatePrice().toFixed(2)}</p>
            </div>

            {step < 5 ? (
              <button
                onClick={() => setStep(step + 1)}
                disabled={!canProceed()}
                className="btn-primary disabled:opacity-50"
              >
                Weiter
              </button>
            ) : (
              <div className="flex gap-2">
                <button onClick={shareBurger} className="btn-secondary flex items-center gap-2">
                  <Share2 className="h-4 w-4" />
                  Teilen
                </button>
                <button onClick={addToCartAndContinue} className="btn-primary flex items-center gap-2">
                  <ShoppingCart className="h-4 w-4" />
                  Bestellen
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default BurgerBuilder;

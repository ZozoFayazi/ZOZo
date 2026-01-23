import React, { useState, useMemo, useEffect } from 'react';
import { Helmet } from 'react-helmet';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';
import { ChefHat, Check, ShoppingCart, Edit2 } from 'lucide-react';
import BurgerPreview from '../components/BurgerPreview';

export default function BurgerBuilder({ addToCart, setCartOpen }) {
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Selections
  const [selectedBun, setSelectedBun] = useState(null);
  const [selectedProtein, setSelectedProtein] = useState(null);
  const [selectedCheese, setSelectedCheese] = useState([]);
  const [selectedVeggiesStd, setSelectedVeggiesStd] = useState([]);
  const [selectedVeggiesPremium, setSelectedVeggiesPremium] = useState([]);
  const [selectedExtras, setSelectedExtras] = useState([]);
  const [selectedAvocado, setSelectedAvocado] = useState([]);
  const [selectedSauces, setSelectedSauces] = useState([]);
  
  // Custom name
  const [isEditingName, setIsEditingName] = useState(false);
  const [customName, setCustomName] = useState('');
  
  // Load ingredients from backend
  useEffect(() => {
    loadIngredients();
  }, []);
  
  const loadIngredients = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/burger-builder/ingredients`);
      
      if (!response.ok) throw new Error('Failed to load ingredients');
      
      const data = await response.json();
      setIngredients(data.ingredients || []);
    } catch (error) {
      console.error('Load ingredients error:', error);
      toast.error('Fehler beim Laden der Zutaten');
      setIngredients([]);
    } finally {
      setLoading(false);
    }
  };
  
  // Group ingredients by category
  const ingredientsByCategory = useMemo(() => {
    const grouped = {
      buns: [],
      proteins: [],
      cheese: [],
      veggies_standard: [],
      veggies_premium: [],
      extras: [],
      avocado: [],
      sauces: []
    };
    
    ingredients.forEach(ing => {
      if (grouped[ing.category]) {
        grouped[ing.category].push(ing);
      }
    });
    
    return grouped;
  }, [ingredients]);
  
  // Price calculation
  const totalPrice = useMemo(() => {
    let price = 0;
    
    if (selectedBun) price += selectedBun.price;
    if (selectedProtein) price += selectedProtein.price;
    
    selectedCheese.forEach(cheese => price += cheese.price);
    selectedVeggiesStd.forEach(v => price += v.price);
    selectedVeggiesPremium.forEach(v => price += v.price);
    selectedExtras.forEach(e => price += e.price);
    selectedAvocado.forEach(a => price += a.price);
    
    selectedSauces.forEach((sauce, index) => {
      if (index >= 2) {
        price += sauce.price;
      }
    });
    
    return price;
  }, [selectedBun, selectedProtein, selectedCheese, selectedVeggiesStd, selectedVeggiesPremium, selectedExtras, selectedAvocado, selectedSauces]);
  
  const generatedName = useMemo(() => {
    if (!selectedProtein) return 'Custom Burger';
    return `Custom Burger mit ${selectedProtein.name}`;
  }, [selectedProtein]);
  
  const displayName = customName || generatedName;
  const canAddToCart = selectedBun && selectedProtein;
  
  const previewSelections = useMemo(() => ({
    bun: selectedBun,
    protein: selectedProtein,
    cheese: selectedCheese,
    veggiesStd: selectedVeggiesStd,
    veggiesPremium: selectedVeggiesPremium,
    extras: selectedExtras,
    avocado: selectedAvocado,
    sauces: selectedSauces
  }), [selectedBun, selectedProtein, selectedCheese, selectedVeggiesStd, selectedVeggiesPremium, selectedExtras, selectedAvocado, selectedSauces]);
  
  const handleAddToCart = () => {
    if (!canAddToCart) {
      toast.error('Bitte wähle ein Brötchen und ein Protein!');
      return;
    }
    
    const customizations = [];
    const extras = [];
    
    if (selectedBun) {
      customizations.push(`+ ${selectedBun.name}`);
      extras.push({ name: selectedBun.name, price: selectedBun.price });
    }
    
    if (selectedProtein) {
      customizations.push(`+ ${selectedProtein.name}`);
      extras.push({ name: selectedProtein.name, price: selectedProtein.price });
    }
    
    selectedCheese.forEach(item => {
      customizations.push(`+ ${item.name}`);
      extras.push({ name: item.name, price: item.price });
    });
    
    selectedVeggiesStd.forEach(item => {
      customizations.push(`+ ${item.name}`);
      extras.push({ name: item.name, price: item.price });
    });
    
    selectedVeggiesPremium.forEach(item => {
      customizations.push(`+ ${item.name}`);
      extras.push({ name: item.name, price: item.price });
    });
    
    selectedExtras.forEach(item => {
      customizations.push(`+ ${item.name}`);
      extras.push({ name: item.name, price: item.price });
    });
    
    selectedAvocado.forEach(item => {
      customizations.push(`+ ${item.name}`);
      extras.push({ name: item.name, price: item.price });
    });
    
    selectedSauces.forEach((item, index) => {
      if (index < 2) {
        customizations.push(`+ ${item.name} (kostenlos)`);
      } else {
        customizations.push(`+ ${item.name}`);
      }
      extras.push({ name: item.name, price: index >= 2 ? item.price : 0 });
    });
    
    const burgerItem = {
      menu_item_id: 'custom-burger-builder',
      name: displayName,
      price: totalPrice,
      quantity: 1,
      category: 'burger-builder',
      customizations,
      extras,
      removed_ingredients: [],
      modifiers: {}
    };
    
    addToCart(burgerItem);
    toast.success(`${displayName} zum Warenkorb hinzugefügt! 🍔`);
    
    if (setCartOpen) setCartOpen(true);
  };
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Lädt Burger Builder...</p>
        </div>
      </div>
    );
  }
  
  return (
    <>
      <Helmet>
        <title>Burger Builder | ZOZO Burger - Baue deinen Traumburger</title>
        <meta name="description" content="Erstelle deinen perfekten Burger! Wähle aus Premium-Zutaten: Beef, Chicken, Veggie-Patties, frisches Gemüse, Käse und mehr." />
      </Helmet>
      
      <div className="min-h-screen bg-background py-12" data-testid="burger-builder-page">
        <div className="container-custom max-w-7xl">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-6">
              <ChefHat className="w-10 h-10 text-primary" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">Burger Builder</h1>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Baue deinen perfekten Burger! Wähle deine Lieblingszutaten und kreiere ein einzigartiges Meisterwerk.
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-4 order-first lg:order-last">
              <div className="lg:sticky lg:top-4 space-y-4">
                <BurgerPreview selections={previewSelections} ingredients={ingredients} />
                
                <Card className="border-primary/20 shadow-lg" data-testid="burger-summary">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <h3 className="text-xl font-semibold flex-1">{displayName}</h3>
                        <Button variant="ghost" size="sm" onClick={() => setIsEditingName(!isEditingName)}>
                          <Edit2 className="w-4 h-4" />
                        </Button>
                      </div>
                      
                      {isEditingName && (
                        <Input value={customName} onChange={(e) => setCustomName(e.target.value)} placeholder={generatedName} />
                      )}
                      
                      <div className="flex items-center gap-2 flex-wrap">
                        {!selectedBun && <Badge variant="outline" className="border-destructive/50 text-destructive">Brötchen fehlt</Badge>}
                        {!selectedProtein && <Badge variant="outline" className="border-destructive/50 text-destructive">Protein fehlt</Badge>}
                        {selectedBun && <Badge variant="secondary">✓ Brötchen</Badge>}
                        {selectedProtein && <Badge variant="secondary">✓ Protein</Badge>}
                        {selectedSauces.length > 0 && (
                          <Badge variant="secondary">
                            {selectedSauces.length} Sauce{selectedSauces.length > 1 ? 'n' : ''}
                            {selectedSauces.length > 2 && ` (+${selectedSauces.length - 2} berechnet)`}
                          </Badge>
                        )}
                      </div>
                      
                      <div className="pt-4 border-t">
                        <div className="flex items-baseline justify-between mb-4">
                          <span className="text-sm text-muted-foreground">Gesamtpreis</span>
                          <span className="text-3xl font-bold text-primary" data-testid="total-price">€{totalPrice.toFixed(2)}</span>
                        </div>
                        <Button onClick={handleAddToCart} disabled={!canAddToCart} size="lg" className="w-full">
                          <ShoppingCart className="w-5 h-5 mr-2" />
                          In den Warenkorb
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
            
            <div className="lg:col-span-8 space-y-8">
              <CategorySection title="Brötchen" subtitle="Pflicht - Wähle genau 1" required items={ingredientsByCategory.buns} selected={selectedBun} onSelect={setSelectedBun} singleSelect testId="buns" />
              <CategorySection title="Protein / Patty" subtitle="Pflicht - Wähle genau 1" required items={ingredientsByCategory.proteins} selected={selectedProtein} onSelect={setSelectedProtein} singleSelect testId="proteins" />
              <CategorySection title="Käse" subtitle="Optional - Mehrfachauswahl möglich" items={ingredientsByCategory.cheese} selected={selectedCheese} onSelect={setSelectedCheese} testId="cheese" />
              <CategorySection title="Gemüse Standard" subtitle="Optional - Mehrfachauswahl möglich" items={ingredientsByCategory.veggies_standard} selected={selectedVeggiesStd} onSelect={setSelectedVeggiesStd} testId="veggies-standard" />
              <CategorySection title="Gemüse Premium" subtitle="Optional - Mehrfachauswahl möglich" items={ingredientsByCategory.veggies_premium} selected={selectedVeggiesPremium} onSelect={setSelectedVeggiesPremium} testId="veggies-premium" />
              <CategorySection title="Crunch / Extras" subtitle="Optional - Mehrfachauswahl möglich" items={ingredientsByCategory.extras} selected={selectedExtras} onSelect={setSelectedExtras} testId="extras" />
              <CategorySection title="Avocado" subtitle="Optional - Mehrfachauswahl möglich" items={ingredientsByCategory.avocado} selected={selectedAvocado} onSelect={setSelectedAvocado} testId="avocado" />
              <SaucesSection items={ingredientsByCategory.sauces} selected={selectedSauces} onSelect={setSelectedSauces} />
            </div>
          </div>
          
          <div className="mt-12 text-center lg:hidden">
            <Button onClick={handleAddToCart} disabled={!canAddToCart} size="lg" className="w-full sm:w-auto px-12">
              <ShoppingCart className="w-5 h-5 mr-2" />
              In den Warenkorb für €{totalPrice.toFixed(2)}
            </Button>
            {!canAddToCart && <p className="text-sm text-muted-foreground mt-3">Bitte wähle ein Brötchen und ein Protein</p>}
          </div>
        </div>
      </div>
    </>
  );
}

function CategorySection({ title, subtitle, required, items, selected, onSelect, singleSelect, testId }) {
  const toggleItem = (item) => {
    if (singleSelect) {
      onSelect(selected?.id === item.id ? null : item);
    } else {
      if (selected.find(i => i.id === item.id)) {
        onSelect(selected.filter(i => i.id !== item.id));
      } else {
        onSelect([...selected, item]);
      }
    }
  };
  
  const isSelected = (item) => {
    if (singleSelect) return selected?.id === item.id;
    return selected.find(i => i.id === item.id);
  };
  
  if (!items || items.length === 0) return null;
  
  return (
    <Card data-testid={`category-${testId}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {title}
          {required && <Badge variant="destructive" className="text-xs">Pflicht</Badge>}
        </CardTitle>
        <p className="text-sm text-muted-foreground">{subtitle}</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {items.map(item => {
            const itemSelected = isSelected(item);
            return (
              <button key={item.id} onClick={() => toggleItem(item)} className={`relative p-4 rounded-lg border-2 text-left transition-all ${itemSelected ? 'border-primary bg-primary/5 shadow-md' : 'border-border hover:border-primary/50 hover:bg-accent'}`} data-testid={`item-${item.id}`}>
                {itemSelected && <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-primary flex items-center justify-center"><Check className="w-4 h-4 text-primary-foreground" /></div>}
                {item.image_url && <div className="mb-2"><img src={item.image_url} alt={item.name} className="w-16 h-16 object-contain mx-auto" loading="lazy" /></div>}
                <div className="font-semibold mb-1">{item.name}</div>
                <div className="text-lg font-bold text-primary">€{item.price.toFixed(2)}</div>
              </button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

function SaucesSection({ items, selected, onSelect }) {
  const toggleSauce = (sauce) => {
    if (selected.find(s => s.id === sauce.id)) {
      onSelect(selected.filter(s => s.id !== sauce.id));
    } else {
      onSelect([...selected, sauce]);
    }
  };
  
  const isSauceSelected = (sauce) => selected.find(s => s.id === sauce.id);
  const freeSaucesCount = Math.min(selected.length, 2);
  const paidSaucesCount = Math.max(0, selected.length - 2);
  
  if (!items || items.length === 0) return null;
  
  return (
    <Card data-testid="category-sauces">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Saucen
          <Badge variant="secondary" className="text-xs">{freeSaucesCount}/2 kostenlos{paidSaucesCount > 0 && ` · +${paidSaucesCount} berechnet`}</Badge>
        </CardTitle>
        <p className="text-sm text-muted-foreground">Optional - Erste 2 Saucen kostenlos, ab der 3. wird berechnet</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {items.map((sauce) => {
            const isSelected = isSauceSelected(sauce);
            const sauceIndex = selected.findIndex(s => s.id === sauce.id);
            const isFree = isSelected && sauceIndex < 2;
            return (
              <button key={sauce.id} onClick={() => toggleSauce(sauce)} className={`relative p-4 rounded-lg border-2 text-left transition-all ${isSelected ? 'border-primary bg-primary/5 shadow-md' : 'border-border hover:border-primary/50 hover:bg-accent'}`} data-testid={`sauce-${sauce.id}`}>
                {isSelected && <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-primary flex items-center justify-center"><Check className="w-4 h-4 text-primary-foreground" /></div>}
                {sauce.image_url && <div className="mb-2"><img src={sauce.image_url} alt={sauce.name} className="w-16 h-16 object-contain mx-auto" loading="lazy" /></div>}
                <div className="font-semibold mb-1">{sauce.name}</div>
                <div className={`text-lg font-bold ${isFree ? 'text-green-500' : 'text-primary'}`}>{isFree ? 'Kostenlos' : `€${sauce.price.toFixed(2)}`}</div>
              </button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

import React, { useState, useMemo } from 'react';
import { Helmet } from 'react-helmet';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';
import { ChefHat, Check, ShoppingCart, Edit2 } from 'lucide-react';

// Burger Builder Daten
const BURGER_DATA = {
  buns: [
    { id: 'brioche', name: 'Brioche Bun', price: 1.50 },
    { id: 'semolina', name: 'Semolina Bun', price: 1.50 },
    { id: 'potato', name: 'Potato Bun (Smash-Style)', price: 1.90 }
  ],
  
  proteins: [
    { id: 'beef-125', name: 'Beef Patty 125g', price: 5.90 },
    { id: 'beef-180', name: 'Beef Patty 180g', price: 7.90 },
    { id: 'chicken', name: 'Crunchy Chicken Patty', price: 4.90 },
    { id: 'fish', name: 'Fisch Patty', price: 4.90 },
    { id: 'veggie', name: 'Veggie Patty', price: 4.90 },
    { id: 'nuggets', name: 'Nuggets (4 Stück)', price: 3.90 }
  ],
  
  cheese: [
    { id: 'chester-2', name: 'Chester Käse (2 Scheiben)', price: 1.50 },
    { id: 'chester-3', name: 'Chester Käse (3 Scheiben)', price: 2.00 },
    { id: 'hirten', name: 'Hirtenkäse', price: 2.00 },
    { id: 'grana', name: 'Grana Padano', price: 2.00 }
  ],
  
  veggiesStandard: [
    { id: 'lettuce', name: 'Eisbergsalat', price: 0.50 },
    { id: 'tomato', name: 'Tomate', price: 0.50 },
    { id: 'onions', name: 'Zwiebeln', price: 0.50 },
    { id: 'red-onions', name: 'Rote Zwiebeln', price: 0.50 },
    { id: 'pickles', name: 'Gewürzgurken', price: 0.50 }
  ],
  
  veggiesPremium: [
    { id: 'jalapenos', name: 'Jalapeños', price: 1.00 },
    { id: 'mushrooms', name: 'Champignons', price: 1.50 },
    { id: 'olives', name: 'Oliven', price: 1.50 },
    { id: 'pepperoni', name: 'Peperoni', price: 1.00 },
    { id: 'rucola', name: 'Rucola', price: 1.00 }
  ],
  
  extras: [
    { id: 'fried-onions', name: 'Röstzwiebeln', price: 1.00 },
    { id: 'bacon', name: 'Bacon', price: 2.00 },
    { id: 'egg', name: 'Spiegelei', price: 2.00 },
    { id: 'serrano', name: 'Serrano Schinken', price: 2.50 }
  ],
  
  avocado: [
    { id: 'avocado-slices', name: 'Avocado Slices', price: 2.50 },
    { id: 'guacamole', name: 'Guacamole', price: 2.50 }
  ],
  
  sauces: {
    klassiker: [
      { id: 'ketchup', name: 'Ketchup', price: 0.50 },
      { id: 'mayo', name: 'Mayonnaise', price: 0.50 },
      { id: 'bbq', name: 'BBQ Sauce', price: 0.80 },
      { id: 'sweet-chili', name: 'Sweet Chili Sauce', price: 0.80 }
    ],
    cremig: [
      { id: 'sour-cream', name: 'Sour Creme', price: 0.80 },
      { id: 'garlic', name: 'Knoblauchsauce', price: 0.80 },
      { id: 'remoulade', name: 'Remoulade', price: 0.80 },
      { id: 'hollandaise', name: 'Sauce Hollandaise', price: 0.90 }
    ],
    scharf: [
      { id: 'chili', name: 'Chilisauce', price: 0.80 },
      { id: 'sweet-sour', name: 'Sweet & Sour Sauce', price: 0.80 }
    ]
  }
};

export default function BurgerBuilder({ addToCart, setCartOpen }) {
  const navigate = useNavigate();
  
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
    
    // Sauces: erste 2 kostenlos, ab 3. berechnet
    selectedSauces.forEach((sauce, index) => {
      if (index >= 2) {
        price += sauce.price;
      }
    });
    
    return price;
  }, [selectedBun, selectedProtein, selectedCheese, selectedVeggiesStd, selectedVeggiesPremium, selectedExtras, selectedAvocado, selectedSauces]);
  
  // Generate burger name
  const generatedName = useMemo(() => {
    if (!selectedProtein) return 'Custom Burger';
    return `Custom Burger mit ${selectedProtein.name}`;
  }, [selectedProtein]);
  
  const displayName = customName || generatedName;
  
  // Validation
  const canAddToCart = selectedBun && selectedProtein;
  
  // Handle add to cart
  const handleAddToCart = () => {
    if (!canAddToCart) {
      toast.error('Bitte wähle ein Brötchen und ein Protein!');
      return;
    }
    
    // Build customizations
    const customizations = [];
    
    if (selectedBun) customizations.push(`+ ${selectedBun.name}`);
    if (selectedProtein) customizations.push(`+ ${selectedProtein.name}`);
    
    selectedCheese.forEach(cheese => customizations.push(`+ ${cheese.name}`));
    selectedVeggiesStd.forEach(v => customizations.push(`+ ${v.name}`));
    selectedVeggiesPremium.forEach(v => customizations.push(`+ ${v.name}`));
    selectedExtras.forEach(e => customizations.push(`+ ${e.name}`));
    selectedAvocado.forEach(a => customizations.push(`+ ${a.name}`));
    
    selectedSauces.forEach((sauce, index) => {
      if (index < 2) {
        customizations.push(`+ ${sauce.name} (kostenlos)`);
      } else {
        customizations.push(`+ ${sauce.name}`);
      }
    });
    
    // Build extras array for backend
    const extras = [];
    
    if (selectedBun) extras.push({ name: selectedBun.name, price: selectedBun.price });
    if (selectedProtein) extras.push({ name: selectedProtein.name, price: selectedProtein.price });
    
    selectedCheese.forEach(item => extras.push({ name: item.name, price: item.price }));
    selectedVeggiesStd.forEach(item => extras.push({ name: item.name, price: item.price }));
    selectedVeggiesPremium.forEach(item => extras.push({ name: item.name, price: item.price }));
    selectedExtras.forEach(item => extras.push({ name: item.name, price: item.price }));
    selectedAvocado.forEach(item => extras.push({ name: item.name, price: item.price }));
    
    selectedSauces.forEach((item, index) => {
      extras.push({ 
        name: item.name, 
        price: index >= 2 ? item.price : 0 
      });
    });
    
    const burgerItem = {
      menu_item_id: 'custom-burger-builder',
      name: displayName,
      price: totalPrice,
      quantity: 1,
      category: 'burger-builder',
      customizations: customizations,
      extras: extras,
      removed_ingredients: [],
      modifiers: {}
    };
    
    addToCart(burgerItem);
    toast.success(`${displayName} zum Warenkorb hinzugefügt! 🍔`);
    
    // Open cart drawer
    if (setCartOpen) {
      setCartOpen(true);
    }
  };
  
  return (
    <>
      <Helmet>
        <title>Burger Builder | ZOZO Burger - Baue deinen Traumburger</title>
        <meta name="description" content="Erstelle deinen perfekten Burger! Wähle aus Premium-Zutaten: Beef, Chicken, Veggie-Patties, frisches Gemüse, Käse und mehr." />
      </Helmet>
      
      <div className="min-h-screen bg-background py-12" data-testid="burger-builder-page">
        <div className="container-custom max-w-6xl">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-6">
              <ChefHat className="w-10 h-10 text-primary" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">Burger Builder</h1>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Baue deinen perfekten Burger! Wähle deine Lieblingszutaten und kreiere ein einzigartiges Meisterwerk.
            </p>
          </div>
          
          {/* Live Preview & Price */}
          <Card className="mb-8 sticky top-4 z-10 border-primary/20 shadow-lg" data-testid="burger-summary">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="flex-1 w-full">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">
                      {displayName}
                    </h3>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsEditingName(!isEditingName)}
                      data-testid="edit-name-btn"
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  {isEditingName && (
                    <Input
                      value={customName}
                      onChange={(e) => setCustomName(e.target.value)}
                      placeholder={generatedName}
                      className="max-w-md mb-3"
                      data-testid="custom-name-input"
                    />
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
                </div>
                
                <div className="text-right w-full md:w-auto">
                  <div className="text-sm text-muted-foreground mb-1">Gesamtpreis</div>
                  <div className="text-4xl font-bold text-primary" data-testid="total-price">
                    €{totalPrice.toFixed(2)}
                  </div>
                  <Button
                    onClick={handleAddToCart}
                    disabled={!canAddToCart}
                    size="lg"
                    className="mt-3 w-full md:w-auto"
                    data-testid="add-to-cart-btn"
                  >
                    <ShoppingCart className="w-5 h-5 mr-2" />
                    In den Warenkorb
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Categories */}
          <div className="space-y-8">
            
            {/* Brötchen (Pflicht) */}
            <CategorySection
              title="Brötchen"
              subtitle="Pflicht - Wähle genau 1"
              required
              items={BURGER_DATA.buns}
              selected={selectedBun}
              onSelect={setSelectedBun}
              singleSelect
              testId="buns"
            />
            
            {/* Protein (Pflicht) */}
            <CategorySection
              title="Protein / Patty"
              subtitle="Pflicht - Wähle genau 1"
              required
              items={BURGER_DATA.proteins}
              selected={selectedProtein}
              onSelect={setSelectedProtein}
              singleSelect
              testId="proteins"
            />
            
            {/* Käse */}
            <CategorySection
              title="Käse"
              subtitle="Optional - Mehrfachauswahl möglich"
              items={BURGER_DATA.cheese}
              selected={selectedCheese}
              onSelect={setSelectedCheese}
              testId="cheese"
            />
            
            {/* Gemüse Standard */}
            <CategorySection
              title="Gemüse Standard"
              subtitle="Optional - Mehrfachauswahl möglich"
              items={BURGER_DATA.veggiesStandard}
              selected={selectedVeggiesStd}
              onSelect={setSelectedVeggiesStd}
              testId="veggies-standard"
            />
            
            {/* Gemüse Premium */}
            <CategorySection
              title="Gemüse Premium"
              subtitle="Optional - Mehrfachauswahl möglich"
              items={BURGER_DATA.veggiesPremium}
              selected={selectedVeggiesPremium}
              onSelect={setSelectedVeggiesPremium}
              testId="veggies-premium"
            />
            
            {/* Crunch / Extras */}
            <CategorySection
              title="Crunch / Extras"
              subtitle="Optional - Mehrfachauswahl möglich"
              items={BURGER_DATA.extras}
              selected={selectedExtras}
              onSelect={setSelectedExtras}
              testId="extras"
            />
            
            {/* Avocado */}
            <CategorySection
              title="Avocado"
              subtitle="Optional - Mehrfachauswahl möglich"
              items={BURGER_DATA.avocado}
              selected={selectedAvocado}
              onSelect={setSelectedAvocado}
              testId="avocado"
            />
            
            {/* Sauces */}
            <SaucesSection
              sauces={BURGER_DATA.sauces}
              selected={selectedSauces}
              onSelect={setSelectedSauces}
            />
            
          </div>
          
          {/* Bottom Add to Cart (mobile) */}
          <div className="mt-12 text-center">
            <Button
              onClick={handleAddToCart}
              disabled={!canAddToCart}
              size="lg"
              className="w-full sm:w-auto px-12"
              data-testid="add-to-cart-bottom-btn"
            >
              <ShoppingCart className="w-5 h-5 mr-2" />
              In den Warenkorb für €{totalPrice.toFixed(2)}
            </Button>
            
            {!canAddToCart && (
              <p className="text-sm text-muted-foreground mt-3">
                Bitte wähle ein Brötchen und ein Protein
              </p>
            )}
          </div>
          
        </div>
      </div>
    </>
  );
}

// Category Section Component
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
    if (singleSelect) {
      return selected?.id === item.id;
    }
    return selected.find(i => i.id === item.id);
  };
  
  return (
    <Card data-testid={`category-${testId}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {title}
              {required && <Badge variant="destructive" className="text-xs">Pflicht</Badge>}
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {items.map(item => {
            const itemSelected = isSelected(item);
            
            return (
              <button
                key={item.id}
                onClick={() => toggleItem(item)}
                className={`
                  relative p-4 rounded-lg border-2 text-left transition-all
                  ${itemSelected 
                    ? 'border-primary bg-primary/5 shadow-md' 
                    : 'border-border hover:border-primary/50 hover:bg-accent'
                  }
                `}
                data-testid={`item-${item.id}`}
              >
                {itemSelected && (
                  <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                    <Check className="w-4 h-4 text-primary-foreground" />
                  </div>
                )}
                
                <div className="font-semibold mb-1">{item.name}</div>
                <div className="text-lg font-bold text-primary">
                  €{item.price.toFixed(2)}
                </div>
              </button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

// Sauces Section with subcategories
function SaucesSection({ sauces, selected, onSelect }) {
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
  
  return (
    <Card data-testid="category-sauces">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              Saucen
              <Badge variant="secondary" className="text-xs">
                {freeSaucesCount}/2 kostenlos
                {paidSaucesCount > 0 && ` · +${paidSaucesCount} berechnet`}
              </Badge>
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Optional - Erste 2 Saucen kostenlos, ab der 3. wird berechnet
            </p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        
        {/* Klassiker */}
        <div>
          <h4 className="font-semibold mb-3 text-sm text-muted-foreground">Klassiker</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {sauces.klassiker.map((sauce) => {
              const isSelected = isSauceSelected(sauce);
              const sauceIndex = selected.findIndex(s => s.id === sauce.id);
              const isFree = isSelected && sauceIndex < 2;
              
              return (
                <button
                  key={sauce.id}
                  onClick={() => toggleSauce(sauce)}
                  className={`
                    relative p-4 rounded-lg border-2 text-left transition-all
                    ${isSelected 
                      ? 'border-primary bg-primary/5 shadow-md' 
                      : 'border-border hover:border-primary/50 hover:bg-accent'
                    }
                  `}
                  data-testid={`sauce-${sauce.id}`}
                >
                  {isSelected && (
                    <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                      <Check className="w-4 h-4 text-primary-foreground" />
                    </div>
                  )}
                  
                  <div className="font-semibold mb-1">{sauce.name}</div>
                  <div className={`text-lg font-bold ${isFree ? 'text-green-500' : 'text-primary'}`}>
                    {isFree ? 'Kostenlos' : `€${sauce.price.toFixed(2)}`}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
        
        {/* Cremig */}
        <div>
          <h4 className="font-semibold mb-3 text-sm text-muted-foreground">Cremig</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {sauces.cremig.map((sauce) => {
              const isSelected = isSauceSelected(sauce);
              const sauceIndex = selected.findIndex(s => s.id === sauce.id);
              const isFree = isSelected && sauceIndex < 2;
              
              return (
                <button
                  key={sauce.id}
                  onClick={() => toggleSauce(sauce)}
                  className={`
                    relative p-4 rounded-lg border-2 text-left transition-all
                    ${isSelected 
                      ? 'border-primary bg-primary/5 shadow-md' 
                      : 'border-border hover:border-primary/50 hover:bg-accent'
                    }
                  `}
                  data-testid={`sauce-${sauce.id}`}
                >
                  {isSelected && (
                    <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                      <Check className="w-4 h-4 text-primary-foreground" />
                    </div>
                  )}
                  
                  <div className="font-semibold mb-1">{sauce.name}</div>
                  <div className={`text-lg font-bold ${isFree ? 'text-green-500' : 'text-primary'}`}>
                    {isFree ? 'Kostenlos' : `€${sauce.price.toFixed(2)}`}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
        
        {/* Scharf / Würzig */}
        <div>
          <h4 className="font-semibold mb-3 text-sm text-muted-foreground">Scharf / Würzig</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {sauces.scharf.map((sauce) => {
              const isSelected = isSauceSelected(sauce);
              const sauceIndex = selected.findIndex(s => s.id === sauce.id);
              const isFree = isSelected && sauceIndex < 2;
              
              return (
                <button
                  key={sauce.id}
                  onClick={() => toggleSauce(sauce)}
                  className={`
                    relative p-4 rounded-lg border-2 text-left transition-all
                    ${isSelected 
                      ? 'border-primary bg-primary/5 shadow-md' 
                      : 'border-border hover:border-primary/50 hover:bg-accent'
                    }
                  `}
                  data-testid={`sauce-${sauce.id}`}
                >
                  {isSelected && (
                    <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                      <Check className="w-4 h-4 text-primary-foreground" />
                    </div>
                  )}
                  
                  <div className="font-semibold mb-1">{sauce.name}</div>
                  <div className={`text-lg font-bold ${isFree ? 'text-green-500' : 'text-primary'}`}>
                    {isFree ? 'Kostenlos' : `€${sauce.price.toFixed(2)}`}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
        
      </CardContent>
    </Card>
    
          </div>
        </div>
      </div>
    </>
  );
}

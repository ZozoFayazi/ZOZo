import React from 'react';

function BurgerPreview({ burger }) {
  // Ingredient image mapping
  const getIngredientImage = (ingredient) => {
    const imageMap = {
      // Patties
      'beef': '/ingredients/beef_patty.png',
      'chicken': '/ingredients/chicken_patty.png',
      'veggie': '/ingredients/veggie_patty.png',
      'vegan': '/ingredients/veggie_patty.png',
      
      // Cheese
      'cheddar': '/ingredients/cheese_slice.png',
      'swiss': '/ingredients/cheese_slice.png',
      'blue': '/ingredients/cheese_slice.png',
      'vegan_cheese': '/ingredients/cheese_slice.png',
      
      // Vegetables
      'lettuce': '/ingredients/lettuce.png',
      'tomato': '/ingredients/tomato.png',
      'onions': '/ingredients/onion.png',
      'pickles': '/ingredients/pickle.png',
      
      // Extras
      'bacon': '/ingredients/bacon.png',
      'jalapenos': '/ingredients/jalapeno.png',
      
      // Sauces
      'ketchup': '/ingredients/ketchup_layer.png',
      'mayo': '/ingredients/mayo_layer.png',
      'bbq': '/ingredients/bbq_layer.png',
      'mustard': '/ingredients/mustard_layer.png',
      'ranch': '/ingredients/mayo_layer.png',
      'special': '/ingredients/bbq_layer.png',
    };
    
    return imageMap[ingredient] || null;
  };

  // Build the burger layers array (bottom to top)
  const layers = [];

  // Bottom Bun
  if (burger.bun) {
    layers.push({
      key: 'bottom-bun',
      image: '/ingredients/bun_bottom.png',
      height: 60
    });
  }

  // Sauces (at bottom, after bottom bun)
  if (burger.sauces && burger.sauces.length > 0) {
    burger.sauces.forEach((sauce, idx) => {
      const sauceImage = getIngredientImage(sauce);
      if (sauceImage) {
        layers.push({
          key: `sauce-${idx}`,
          image: sauceImage,
          height: 30
        });
      }
    });
  }

  // Lettuce
  if (burger.toppings && burger.toppings.includes('lettuce')) {
    layers.push({
      key: 'lettuce',
      image: getIngredientImage('lettuce'),
      height: 40
    });
  }

  // Tomato
  if (burger.toppings && burger.toppings.includes('tomato')) {
    layers.push({
      key: 'tomato',
      image: getIngredientImage('tomato'),
      height: 35
    });
  }

  // Onions
  if (burger.toppings && burger.toppings.includes('onions')) {
    layers.push({
      key: 'onions',
      image: getIngredientImage('onions'),
      height: 30
    });
  }

  // Pickles
  if (burger.toppings && burger.toppings.includes('pickles')) {
    layers.push({
      key: 'pickles',
      image: getIngredientImage('pickles'),
      height: 35
    });
  }

  // Cheese
  if (burger.cheese) {
    layers.push({
      key: 'cheese',
      image: getIngredientImage(burger.cheese),
      height: 35
    });
  }

  // Bacon
  if (burger.toppings && burger.toppings.includes('bacon')) {
    layers.push({
      key: 'bacon',
      image: getIngredientImage('bacon'),
      height: 30
    });
  }

  // Jalapeños
  if (burger.toppings && burger.toppings.includes('jalapenos')) {
    layers.push({
      key: 'jalapenos',
      image: getIngredientImage('jalapenos'),
      height: 30
    });
  }

  // Patties (stacked based on count)
  if (burger.patty) {
    const pattyImage = getIngredientImage(burger.patty);
    
    for (let i = 0; i < (burger.patty_count || 1); i++) {
      layers.push({
        key: `patty-${i}`,
        image: pattyImage,
        height: 55
      });
      
      // Add cheese between patties if multiple
      if (i < (burger.patty_count || 1) - 1 && burger.cheese) {
        layers.push({
          key: `cheese-between-${i}`,
          image: getIngredientImage(burger.cheese),
          height: 30
        });
      }
    }
  }

  // Top Bun
  if (burger.bun) {
    layers.push({
      key: 'top-bun',
      image: '/ingredients/bun_top.png',
      height: 70
    });
  }

  return (
    <div className="sticky top-24">
      <div className="bg-gradient-to-b from-accent via-background to-accent rounded-xl p-6 border-2 border-border">
        <h3 className="text-lg font-semibold mb-4 text-center">Live Preview</h3>
        
        {/* Burger Stack */}
        <div className="relative mx-auto" style={{ width: '200px' }}>
          {layers.length > 0 ? (
            <div className="space-y-0.5 transform hover:scale-105 transition-transform duration-300">
              {layers.reverse().map((layer, index) => (
                <div 
                  key={layer.key} 
                  className="animate-fadeIn"
                  style={{ 
                    animationDelay: `${index * 50}ms`,
                    animationFillMode: 'backwards'
                  }}
                >
                  {layer.component}
                </div>
              ))}
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-muted-foreground text-center">
              <div>
                <div className="text-6xl mb-3">🍔</div>
                <p className="text-sm">Wähle Zutaten,<br />um deinen Burger zu sehen</p>
              </div>
            </div>
          )}
        </div>

        {/* Ingredient Count */}
        <div className="mt-6 pt-4 border-t border-border">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="text-muted-foreground">Zutaten:</div>
            <div className="font-semibold text-right">
              {layers.length > 0 ? layers.length : 0}
            </div>
            
            <div className="text-muted-foreground">Preis:</div>
            <div className="font-bold text-primary text-right">
              €{((burger.bun ? 0 : 0) + 
                 (burger.patty ? 4.50 * (burger.patty_count || 1) : 0) +
                 (burger.cheese ? 1.00 : 0) +
                 ((burger.toppings?.length || 0) * 0.50) +
                 ((burger.sauces?.length || 0) * 0.50)
              ).toFixed(2)}
            </div>
          </div>
        </div>
      </div>
      
      {/* Animation styles */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

export default BurgerPreview;

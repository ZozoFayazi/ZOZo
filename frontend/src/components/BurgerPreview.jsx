import React from 'react';

function BurgerPreview({ burger }) {
  // Ingredient visuals (layers stacked from bottom to top)
  const layers = [];

  // Bottom Bun
  if (burger.bun) {
    layers.push({
      key: 'bottom-bun',
      component: (
        <div className="w-full h-8 bg-gradient-to-b from-amber-600 to-amber-700 rounded-b-[50px] border-4 border-amber-800 relative">
          <div className="absolute inset-0 flex items-center justify-center gap-1">
            {burger.bun === 'sesame' && (
              <>
                <div className="w-1.5 h-1.5 bg-amber-200 rounded-full"></div>
                <div className="w-1.5 h-1.5 bg-amber-200 rounded-full"></div>
                <div className="w-1.5 h-1.5 bg-amber-200 rounded-full"></div>
                <div className="w-1.5 h-1.5 bg-amber-200 rounded-full"></div>
              </>
            )}
          </div>
        </div>
      )
    });
  }

  // Sauces (at bottom)
  if (burger.sauces && burger.sauces.length > 0) {
    burger.sauces.forEach((sauce, idx) => {
      const sauceColors = {
        ketchup: 'bg-red-600',
        mayo: 'bg-amber-100',
        bbq: 'bg-amber-900',
        ranch: 'bg-gray-100',
        special: 'bg-yellow-400'
      };
      
      layers.push({
        key: `sauce-${idx}`,
        component: (
          <div className={`w-full h-2 ${sauceColors[sauce] || 'bg-yellow-400'} opacity-80`}></div>
        )
      });
    });
  }

  // Lettuce
  if (burger.toppings && burger.toppings.includes('lettuce')) {
    layers.push({
      key: 'lettuce',
      component: (
        <div className="w-full h-4 bg-gradient-to-b from-green-400 to-green-500 relative overflow-hidden">
          <div className="absolute inset-0 flex">
            <div className="w-1/3 h-full bg-green-500 opacity-50 rounded-tl-full"></div>
            <div className="w-1/3 h-full bg-green-400 opacity-50"></div>
            <div className="w-1/3 h-full bg-green-500 opacity-50 rounded-tr-full"></div>
          </div>
        </div>
      )
    });
  }

  // Tomato
  if (burger.toppings && burger.toppings.includes('tomato')) {
    layers.push({
      key: 'tomato',
      component: (
        <div className="w-full h-3 bg-gradient-to-b from-red-500 to-red-600 border-y border-red-700"></div>
      )
    });
  }

  // Onions
  if (burger.toppings && burger.toppings.includes('onions')) {
    layers.push({
      key: 'onions',
      component: (
        <div className="w-full h-2 bg-gradient-to-b from-purple-200 to-purple-300 opacity-70"></div>
      )
    });
  }

  // Pickles
  if (burger.toppings && burger.toppings.includes('pickles')) {
    layers.push({
      key: 'pickles',
      component: (
        <div className="w-full h-3 bg-gradient-to-b from-green-600 to-green-700 border-y border-green-800"></div>
      )
    });
  }

  // Cheese
  if (burger.cheese) {
    const cheeseColors = {
      cheddar: 'from-orange-400 to-yellow-500',
      swiss: 'from-yellow-200 to-yellow-300',
      blue: 'from-blue-100 to-blue-200',
      vegan: 'from-yellow-300 to-yellow-400'
    };
    
    layers.push({
      key: 'cheese',
      component: (
        <div className={`w-full h-3 bg-gradient-to-b ${cheeseColors[burger.cheese] || 'from-yellow-400 to-orange-500'} transform -skew-y-1`}>
          <div className="w-full h-full opacity-60 bg-gradient-to-r from-transparent via-white to-transparent"></div>
        </div>
      )
    });
  }

  // Bacon
  if (burger.toppings && burger.toppings.includes('bacon')) {
    layers.push({
      key: 'bacon',
      component: (
        <div className="w-full h-2 bg-gradient-to-b from-red-800 to-red-900 relative">
          <div className="absolute inset-0 flex gap-1 px-1">
            <div className="flex-1 h-full bg-pink-400 opacity-40"></div>
            <div className="flex-1 h-full bg-red-900 opacity-60"></div>
            <div className="flex-1 h-full bg-pink-400 opacity-40"></div>
          </div>
        </div>
      )
    });
  }

  // Egg
  if (burger.toppings && burger.toppings.includes('egg')) {
    layers.push({
      key: 'egg',
      component: (
        <div className="w-full h-4 bg-white relative border-y border-gray-200">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 bg-yellow-400 rounded-full"></div>
        </div>
      )
    });
  }

  // Avocado
  if (burger.toppings && burger.toppings.includes('avocado')) {
    layers.push({
      key: 'avocado',
      component: (
        <div className="w-full h-3 bg-gradient-to-b from-green-400 to-green-500"></div>
      )
    });
  }

  // Jalapeños
  if (burger.toppings && burger.toppings.includes('jalapenos')) {
    layers.push({
      key: 'jalapenos',
      component: (
        <div className="w-full h-2 bg-gradient-to-b from-green-600 to-green-700 relative">
          <div className="absolute inset-0 flex justify-around items-center">
            <div className="w-2 h-1 bg-green-700 rounded-full"></div>
            <div className="w-2 h-1 bg-green-700 rounded-full"></div>
            <div className="w-2 h-1 bg-green-700 rounded-full"></div>
          </div>
        </div>
      )
    });
  }

  // Patties (stacked based on count)
  if (burger.patty) {
    const pattyColors = {
      beef: 'from-amber-800 to-amber-900',
      chicken: 'from-amber-200 to-amber-300',
      veggie: 'from-green-700 to-green-800',
      vegan: 'from-green-600 to-green-700'
    };
    
    for (let i = 0; i < (burger.patty_count || 1); i++) {
      layers.push({
        key: `patty-${i}`,
        component: (
          <div className={`w-full h-6 bg-gradient-to-b ${pattyColors[burger.patty] || 'from-amber-800 to-amber-900'} border-y-2 border-amber-950 relative`}>
            <div className="absolute inset-0 flex items-center justify-around px-2">
              <div className="w-2 h-2 bg-amber-950 rounded-full opacity-30"></div>
              <div className="w-2 h-2 bg-amber-950 rounded-full opacity-30"></div>
              <div className="w-2 h-2 bg-amber-950 rounded-full opacity-30"></div>
            </div>
          </div>
        )
      });
      
      // Add cheese between patties if multiple
      if (i < (burger.patty_count || 1) - 1 && burger.cheese) {
        layers.push({
          key: `cheese-between-${i}`,
          component: (
            <div className="w-full h-2 bg-gradient-to-b from-yellow-400 to-orange-500 transform -skew-y-1"></div>
          )
        });
      }
    }
  }

  // Top Bun
  if (burger.bun) {
    layers.push({
      key: 'top-bun',
      component: (
        <div className="w-full h-10 bg-gradient-to-b from-amber-500 to-amber-600 rounded-t-[60px] border-4 border-amber-700 relative">
          <div className="absolute inset-0 flex items-center justify-center gap-2">
            {burger.bun === 'sesame' && (
              <>
                <div className="w-2 h-2 bg-amber-200 rounded-full"></div>
                <div className="w-2 h-2 bg-amber-200 rounded-full"></div>
                <div className="w-2 h-2 bg-amber-200 rounded-full"></div>
                <div className="w-2 h-2 bg-amber-200 rounded-full"></div>
                <div className="w-2 h-2 bg-amber-200 rounded-full"></div>
              </>
            )}
          </div>
          <div className="absolute top-2 left-1/2 -translate-x-1/2 w-8 h-2 bg-amber-400 rounded-full opacity-60"></div>
        </div>
      )
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

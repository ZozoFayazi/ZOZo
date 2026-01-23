import React, { useMemo } from 'react';
import { Card, CardContent } from './ui/card';

/**
 * Live Burger Preview with Layer Stack
 * Shows real ingredient images stacked in correct order
 */
export default function BurgerPreview({ selections, ingredients }) {
  // Build layer stack from selections
  const layers = useMemo(() => {
    const layerList = [];
    
    // Helper to add layers from selected items
    const addLayers = (selectedItems, ingredientCategory) => {
      selectedItems.forEach(selected => {
        // Find ingredient data with image
        const ingredient = ingredients.find(ing => 
          ing.id === selected.id || ing.name === selected.name
        );
        
        if (ingredient && ingredient.image_url) {
          layerList.push({
            id: ingredient.id,
            name: ingredient.name,
            image_url: ingredient.image_url,
            layer_order: ingredient.layer_order,
            layer_group: ingredient.layer_group,
            position: ingredient.position || 'center'
          });
        }
      });
    };
    
    // Add bun bottom (special: also add bun_top at end)
    if (selections.bun) {
      const bunIngredient = ingredients.find(ing => ing.id === selections.bun.id);
      if (bunIngredient && bunIngredient.image_url) {
        // Bottom bun
        layerList.push({
          id: bunIngredient.id + '-bottom',
          name: bunIngredient.name + ' (Bottom)',
          image_url: bunIngredient.image_url,
          layer_order: 10,
          layer_group: 'bun_bottom',
          position: 'full'
        });
        
        // Top bun (added later with layer_order 100)
        layerList.push({
          id: bunIngredient.id + '-top',
          name: bunIngredient.name + ' (Top)',
          image_url: bunIngredient.image_url,
          layer_order: 100,
          layer_group: 'bun_top',
          position: 'full',
          isTopBun: true  // Flag for special rendering if needed
        });
      }
    }
    
    // Add protein
    if (selections.protein) {
      const proteinIngredient = ingredients.find(ing => ing.id === selections.protein.id);
      if (proteinIngredient && proteinIngredient.image_url) {
        layerList.push({
          id: proteinIngredient.id,
          name: proteinIngredient.name,
          image_url: proteinIngredient.image_url,
          layer_order: 50,
          layer_group: 'patty',
          position: 'center'
        });
      }
    }
    
    // Add other selections
    if (selections.cheese) addLayers(selections.cheese, 'cheese');
    if (selections.veggiesStd) addLayers(selections.veggiesStd, 'veggies');
    if (selections.veggiesPremium) addLayers(selections.veggiesPremium, 'veggies');
    if (selections.extras) addLayers(selections.extras, 'extras');
    if (selections.avocado) addLayers(selections.avocado, 'avocado');
    if (selections.sauces) addLayers(selections.sauces, 'sauces');
    
    // Sort by layer_order
    return layerList.sort((a, b) => a.layer_order - b.layer_order);
  }, [selections, ingredients]);
  
  const hasAnySelection = layers.length > 0;
  
  return (
    <Card className="overflow-hidden" data-testid="burger-preview">
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold mb-4">Live Preview</h3>
        
        <div className="relative aspect-square max-w-md mx-auto bg-accent/30 rounded-xl overflow-hidden">
          {!hasAnySelection ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <div className="text-6xl mb-3">🍔</div>
                <p>Wähle Zutaten aus</p>
                <p className="text-sm">um deinen Burger zu bauen</p>
              </div>
            </div>
          ) : (
            <div className="absolute inset-0" style={{ perspective: '1000px' }}>
              {/* Layer Stack */}
              {layers.map((layer, index) => (
                <div
                  key={layer.id}
                  className="absolute inset-0 flex items-center justify-center transition-all duration-300"
                  style={{
                    zIndex: layer.layer_order,
                    transform: `translateZ(${index * 2}px)`,
                  }}
                  data-testid={`layer-${layer.layer_group}`}
                >
                  <img
                    src={layer.image_url}
                    alt={layer.name}
                    className={`
                      max-w-full max-h-full object-contain transition-all duration-300
                      ${layer.position === 'full' ? 'w-full h-full' : ''}
                      ${layer.position === 'center' ? 'w-4/5 h-4/5' : ''}
                    `}
                    loading="lazy"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Layer Count */}
        {hasAnySelection && (
          <div className="mt-4 text-center text-sm text-muted-foreground">
            {layers.length} Layer{layers.length > 1 ? 's' : ''} aktiv
          </div>
        )}
      </CardContent>
    </Card>
  );
}

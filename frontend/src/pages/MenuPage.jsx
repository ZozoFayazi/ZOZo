import React, { useEffect, useState } from 'react';
import { getLocations, getMenu } from '../api';
import { Search, Plus, MapPin, Settings } from 'lucide-react';
import { toast } from 'sonner';
import ProductCustomizer from '../components/ProductCustomizer';
import CategoryUpsellDialog from '../components/CategoryUpsellDialog';
import QuickReorder from '../components/QuickReorder';

// Helper function to build full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  // If it's already a full URL (http/https), return as-is
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  // If it's a local path, prepend /api to route through Kubernetes Ingress to backend
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  // Convert /uploads/... to /api/uploads/...
  if (imageUrl.startsWith('/uploads/')) {
    return `${backendUrl}/api${imageUrl}`;
  }
  return `${backendUrl}${imageUrl}`;
};

function MenuPage({ selectedLocation, setSelectedLocation, addToCart }) {
  const [locations, setLocations] = useState([]);
  const [menu, setMenu] = useState([]);
  const [modifierGroups, setModifierGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [customizerOpen, setCustomizerOpen] = useState(false);
  const [customizingItem, setCustomizingItem] = useState(null);
  const [customizingSize, setCustomizingSize] = useState(null);
  const [upsellDialogOpen, setUpsellDialogOpen] = useState(false);
  const [upsellCategory, setUpsellCategory] = useState(null);

  // Helper function: Check if category should show upsell
  const shouldShowUpsell = (categorySlug) => {
    if (!categorySlug) return false;
    
    const slug = categorySlug.toLowerCase();
    
    // Show upsell ONLY for these categories
    return (
      slug.includes('burger') ||
      slug.includes('pizza') ||
      slug.includes('imbiss') ||
      slug.includes('salat')
    );
  };

  useEffect(() => {
    loadLocationsWithStatus();
  }, []);

  const loadLocationsWithStatus = async () => {
    try {
      const data = await getLocations(true); // Include status
      setLocations(data);
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  };

  useEffect(() => {
    loadLocationsWithStatus();
    loadModifierGroups();
  }, []);

  useEffect(() => {
    if (selectedLocation) {
      loadMenu(selectedLocation.id);
    }
  }, [selectedLocation]);
  
  const loadModifierGroups = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/modifier-groups`);
      const data = await response.json();
      setModifierGroups(data);
    } catch (error) {
      console.error('Error loading modifier groups:', error);
    }
  };

  const loadMenu = async (locationId) => {
    setLoading(true);
    try {
      const data = await getMenu(locationId);
      setMenu(data);
    } catch (error) {
      console.error('Error loading menu:', error);
      toast.error('Fehler beim Laden der Speisekarte');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomize = (item, size = null) => {
    setCustomizingItem(item);
    setCustomizingSize(size);
    setCustomizerOpen(true);
  };

  const handleAddToCart = (item, size = null, customize = false) => {
    if (!selectedLocation) {
      toast.error('Bitte wähle zuerst einen Standort');
      return;
    }

    // If customize is requested, open customizer instead
    if (customize) {
      handleCustomize(item, size);
      return;
    }

    // Normal add to cart (no menu upgrade)
    let price;
    let sizeName;
    
    if (size === 'medium' && item.price_medium) {
      price = item.price_medium;
      sizeName = 'Medium';
    } else if (size === 'large' && item.price_large) {
      price = item.price_large;
      sizeName = 'Groß';
    } else {
      price = item.price_normal || item.price_medium || item.price_large;
      sizeName = null;
    }

    const cartItem = {
      menu_item_id: item.id,
      name: item.name,
      price: price,
      size: sizeName,
      quantity: 1
    };

    addToCart(cartItem);
    toast.success(`${item.name} zum Warenkorb hinzugefügt`);
    
    // Show category upsell for specific categories only
    const category = menu.find(cat => cat.items.some(i => i.id === item.id));
    if (category && shouldShowUpsell(category.slug)) {
      setUpsellCategory(category.name);
      setUpsellDialogOpen(true);
    }
  };

  const filteredMenu = menu.filter(category => {
    if (selectedCategory !== 'all' && category.slug !== selectedCategory) {
      return false;
    }
    
    if (searchQuery) {
      return category.items.some(item =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }
    
    return true;
  }).map(category => ({
    ...category,
    items: searchQuery
      ? category.items.filter(item =>
          item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase()))
        )
      : category.items
  }));

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container-custom">
        {/* No Location Selected Warning */}
        {!selectedLocation && (
          <div className="mb-8 p-6 bg-amber-500/10 border border-amber-500/20 rounded-xl" data-testid="no-location-warning">
            <div className="flex items-start gap-3">
              <MapPin className="h-6 w-6 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-amber-900 dark:text-amber-100 mb-1">
                  Kein Standort ausgewählt
                </h3>
                <p className="text-sm text-amber-800 dark:text-amber-200 mb-3">
                  Bitte wähle einen Standort aus, um die Speisekarte anzuzeigen.
                </p>
                <a
                  href="/standorte"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors text-sm font-medium"
                >
                  <MapPin className="h-4 w-4" />
                  Standort auswählen
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="mb-8 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="heading-2 mb-2">Speisekarte</h1>
              <p className="text-muted-foreground">Wähle deine Favoriten</p>
            </div>

            {/* Location Info (Read-only) with Status */}
            {selectedLocation && (
              <div className="flex items-center gap-3 px-4 py-2 bg-accent rounded-lg border border-border" data-testid="location-info">
                <MapPin className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">
                  {selectedLocation.name.replace('ZOZO Burger ', '')}
                </span>
                {selectedLocation.opening_status && (
                  <span 
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                      selectedLocation.opening_status.is_open 
                        ? 'bg-green-500/10 text-green-500' 
                        : 'bg-red-500/10 text-red-500'
                    }`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${selectedLocation.opening_status.is_open ? 'bg-green-500' : 'bg-red-500'}`} />
                    {selectedLocation.opening_status.is_open ? 'Geöffnet' : 'Geschlossen'}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Search and Filters */}
          {selectedLocation && (
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="relative flex-1" data-testid="menu-search">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Suche nach Gerichten..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Category Tabs */}
              <div className="flex overflow-x-auto gap-2 pb-2 md:pb-0" data-testid="menu-tabs">
                <button
                  onClick={() => setSelectedCategory('all')}
                  className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                    selectedCategory === 'all'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card border border-border hover:border-primary/40'
                  }`}
                >
                  Alle
                </button>
                {menu.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.slug)}
                    className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                      selectedCategory === category.slug
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-card border border-border hover:border-primary/40'
                    }`}
                  >
                    {category.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Quick Reorder */}
        {selectedLocation && <QuickReorder addToCart={addToCart} />}

        {/* Menu Items */}
        {selectedLocation && (
          <>
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p className="text-muted-foreground mt-4">Lade Speisekarte...</p>
              </div>
            ) : filteredMenu.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">Keine Gerichte gefunden</p>
                <button
                  onClick={() => { setSearchQuery(''); setSelectedCategory('all'); }}
                  className="mt-4 text-primary hover:underline"
                >
                  Alle anzeigen
                </button>
              </div>
            ) : (
              <div className="space-y-12">
            {filteredMenu.map((category) => (
              <section key={category.id} className="animate-fade-in">
                <h2 className="text-2xl font-serif font-semibold mb-6 pb-2 border-b border-border">
                  {category.name}
                </h2>
                
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 stagger-animation">
                  {category.items.map((item) => (
                    <div
                      key={item.id}
                      className="group bg-card border border-border rounded-xl overflow-hidden card-interactive hover:border-primary/30"
                      data-testid="menu-item-card"
                    >
                      {/* Image */}
                      {item.image_url && (
                        <div className="aspect-[4/3] overflow-hidden">
                          <img
                            src={getImageUrl(item.image_url)}
                            alt={item.name}
                            loading="lazy"
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          />
                        </div>
                      )}

                      {/* Content */}
                      <div className="p-5 space-y-3">
                        <div>
                          <div className="flex items-start justify-between gap-2">
                            <h3 className="font-semibold text-lg mb-1 flex-1">{item.name}</h3>
                            {/* Customize button for items with modifier groups */}
                            {item.modifier_group_ids && item.modifier_group_ids.length > 0 && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleCustomize(item, item.price_medium ? 'medium' : null);
                                }}
                                className="p-2 hover:bg-primary/10 hover:text-primary rounded-lg transition-colors"
                                title="Anpassen"
                              >
                                <Settings className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                          {item.description && (
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              {item.description}
                            </p>
                          )}
                          {/* Dietary & Allergen Badges */}
                          <div className="flex flex-wrap gap-1 mt-2">
                            {item.is_vegetarian && (
                              <span className="px-2 py-0.5 bg-green-500/10 text-green-700 dark:text-green-400 text-xs rounded-full border border-green-500/20">
                                🌱 Vegetarisch
                              </span>
                            )}
                            {item.is_vegan && (
                              <span className="px-2 py-0.5 bg-green-500/10 text-green-700 dark:text-green-400 text-xs rounded-full border border-green-500/20">
                                🌿 Vegan
                              </span>
                            )}
                            {item.is_spicy && (
                              <span className="px-2 py-0.5 bg-red-500/10 text-red-700 dark:text-red-400 text-xs rounded-full border border-red-500/20">
                                🌶️ Scharf
                              </span>
                            )}
                            {item.allergens && Array.isArray(item.allergens) && item.allergens.length > 0 && (
                              <span className="px-2 py-0.5 bg-orange-500/10 text-orange-700 dark:text-orange-400 text-xs rounded-full border border-orange-500/20">
                                ⚠️ {item.allergens.length} Allergene
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Price and Add to Cart */}
                        {item.price_medium || item.price_large ? (
                          // Multiple sizes
                          <div className="space-y-2">
                            {item.price_medium && (
                              <div className="flex items-center justify-between">
                                <div>
                                  <span className="text-sm text-muted-foreground mr-2">Medium</span>
                                  <span className="font-semibold text-primary">
                                    €{item.price_medium.toFixed(2)}
                                  </span>
                                </div>
                                <button
                                  onClick={() => {
                                    // For burgers, open customizer to select ingredients
                                    if (category.slug === 'burger') {
                                      handleCustomize(item, 'medium');
                                    } else {
                                      handleAddToCart(item, 'medium');
                                    }
                                  }}
                                  className="p-2 bg-primary/10 hover:bg-primary hover:text-primary-foreground rounded-lg transition-colors"
                                  data-testid="add-to-cart-btn"
                                >
                                  <Plus className="h-4 w-4" />
                                </button>
                              </div>
                            )}
                            {item.price_large && (
                              <div className="flex items-center justify-between">
                                <div>
                                  <span className="text-sm text-muted-foreground mr-2">Groß</span>
                                  <span className="font-semibold text-primary">
                                    €{item.price_large.toFixed(2)}
                                  </span>
                                </div>
                                <button
                                  onClick={() => {
                                    // For burgers, open customizer to select ingredients
                                    if (category.slug === 'burger') {
                                      handleCustomize(item, 'large');
                                    } else {
                                      handleAddToCart(item, 'large');
                                    }
                                  }}
                                  className="p-2 bg-primary/10 hover:bg-primary hover:text-primary-foreground rounded-lg transition-colors"
                                  data-testid="add-to-cart-btn"
                                >
                                  <Plus className="h-4 w-4" />
                                </button>
                              </div>
                            )}
                          </div>
                        ) : (
                          // Single price
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-lg text-primary">
                              €{(item.price_normal || 0).toFixed(2)}
                            </span>
                            <button
                              onClick={() => {
                                // For burgers, open customizer to select ingredients
                                if (category.slug === 'burger') {
                                  handleCustomize(item, null);
                                } else {
                                  handleAddToCart(item);
                                }
                              }}
                              className="px-4 py-2 bg-primary/10 hover:bg-primary hover:text-primary-foreground rounded-lg transition-colors font-medium text-sm flex items-center gap-2"
                              data-testid="add-to-cart-btn"
                            >
                              <Plus className="h-4 w-4" />
                              Hinzufügen
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            ))}
              </div>
            )}
          </>
        )}

        {/* Product Customizer */}
        {customizerOpen && customizingItem && (
          <ProductCustomizer
            item={customizingItem}
            size={customizingSize}
            modifierGroups={modifierGroups}
            onAddToCart={(cartItem) => {
              addToCart(cartItem);
              
              // Close customizer
              setCustomizerOpen(false);
              setCustomizingItem(null);
              setCustomizingSize(null);
              
              // Show category upsell for specific categories only
              const category = menu.find(cat => cat.items.some(i => i.id === customizingItem.id));
              if (category && shouldShowUpsell(category.slug)) {
                setUpsellCategory(category.name);
                setUpsellDialogOpen(true);
              }
            }}
            onClose={() => {
              setCustomizerOpen(false);
              setCustomizingItem(null);
              setCustomizingSize(null);
            }}
          />
        )}

        {/* Category Upsell Dialog */}
        {upsellDialogOpen && (
          <CategoryUpsellDialog
            category={upsellCategory}
            onClose={() => {
              setUpsellDialogOpen(false);
              setUpsellCategory(null);
            }}
            onAddUpsell={(upsellItem) => {
              addToCart(upsellItem);
              toast.success(`${upsellItem.name} hinzugefügt`);
            }}
          />
        )}
      </div>
    </div>
  );
}

export default MenuPage;

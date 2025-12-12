import React, { useEffect, useState } from 'react';
import { getLocations, getMenu } from '../api';
import { Search, Plus, MapPin, Settings } from 'lucide-react';
import { toast } from 'sonner';
import ProductCustomizer from '../components/ProductCustomizer';
import MenuUpgradeDialog from '../components/MenuUpgradeDialog';

function MenuPage({ selectedLocation, setSelectedLocation, addToCart }) {
  const [locations, setLocations] = useState([]);
  const [menu, setMenu] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [customizerOpen, setCustomizerOpen] = useState(false);
  const [customizingItem, setCustomizingItem] = useState(null);
  const [customizingSize, setCustomizingSize] = useState(null);
  const [menuUpgradeOpen, setMenuUpgradeOpen] = useState(false);
  const [upgradingItem, setUpgradingItem] = useState(null);

  useEffect(() => {
    loadLocations();
  }, []);

  useEffect(() => {
    if (selectedLocation) {
      loadMenu(selectedLocation.id);
    }
  }, [selectedLocation]);

  const loadLocations = async () => {
    try {
      const data = await getLocations();
      setLocations(data);
      if (data.length > 0 && !selectedLocation) {
        setSelectedLocation(data[0]);
      }
    } catch (error) {
      console.error('Error loading locations:', error);
      toast.error('Fehler beim Laden der Standorte');
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

    // Check if this is a burger that can be upgraded to menu
    if (item.can_upgrade_to_menu && item.menu_upgrade_price) {
      // Store item with size info for upgrade dialog
      const itemWithPrice = {
        ...item,
        price_normal: size === 'medium' && item.price_medium 
          ? item.price_medium 
          : size === 'large' && item.price_large 
          ? item.price_large 
          : item.price_normal || item.price_medium || item.price_large,
        selected_size: size
      };
      setUpgradingItem(itemWithPrice);
      setMenuUpgradeOpen(true);
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
        {/* Header */}
        <div className="mb-8 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="heading-2 mb-2">Speisekarte</h1>
              <p className="text-muted-foreground">Wähle deine Favoriten</p>
            </div>

            {/* Location Selector */}
            {locations.length > 1 && (
              <div className="flex items-center gap-2" data-testid="location-toggle">
                {locations.map((location) => (
                  <button
                    key={location.id}
                    onClick={() => setSelectedLocation(location)}
                    className={`px-4 py-2 rounded-lg border transition-all ${
                      selectedLocation?.id === location.id
                        ? 'bg-primary text-primary-foreground border-primary'
                        : 'bg-card border-border hover:border-primary/40'
                    }`}
                  >
                    <MapPin className="inline h-4 w-4 mr-2" />
                    {location.name.replace('ZOZO Burger ', '')}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Search and Filters */}
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
        </div>

        {/* Menu Items */}
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
                
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {category.items.map((item) => (
                    <div
                      key={item.id}
                      className="group bg-card border border-border rounded-xl overflow-hidden card-hover"
                      data-testid="menu-item-card"
                    >
                      {/* Image */}
                      {item.image_url && (
                        <div className="aspect-[4/3] overflow-hidden">
                          <img
                            src={item.image_url}
                            alt={item.name}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          />
                        </div>
                      )}

                      {/* Content */}
                      <div className="p-5 space-y-3">
                        <div>
                          <div className="flex items-start justify-between gap-2">
                            <h3 className="font-semibold text-lg mb-1 flex-1">{item.name}</h3>
                            {/* Customize button for customizable items (Burger, Pizza, Pasta) */}
                            {(category.slug === 'burger' || category.slug === 'pizza' || category.slug === 'pasta') && (
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
                          {item.allergens && (
                            <p className="text-xs text-muted-foreground/60 mt-1">
                              Allergene: {item.allergens}
                            </p>
                          )}
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
                                  onClick={() => handleAddToCart(item, 'medium')}
                                  className="p-2 bg-primary/10 hover:bg-primary hover:text-primary-foreground rounded-lg transition-colors"
                                  data-testid="add-to-cart-button"
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
                                  onClick={() => handleAddToCart(item, 'large')}
                                  className="p-2 bg-primary/10 hover:bg-primary hover:text-primary-foreground rounded-lg transition-colors"
                                  data-testid="add-to-cart-button"
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
                              onClick={() => handleAddToCart(item)}
                              className="px-4 py-2 bg-primary/10 hover:bg-primary hover:text-primary-foreground rounded-lg transition-colors font-medium text-sm flex items-center gap-2"
                              data-testid="add-to-cart-button"
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

        {/* Product Customizer */}
        {customizerOpen && customizingItem && (
          <ProductCustomizer
            item={customizingItem}
            size={customizingSize}
            onAddToCart={addToCart}
            onClose={() => {
              setCustomizerOpen(false);
              setCustomizingItem(null);
              setCustomizingSize(null);
            }}
          />
        )}
      </div>
    </div>
  );
}

export default MenuPage;

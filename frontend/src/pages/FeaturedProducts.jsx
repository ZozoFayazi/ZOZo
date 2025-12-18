import React, { useState, useEffect } from 'react';
import { Star, Eye, EyeOff, Tag, ArrowUp, ArrowDown } from 'lucide-react';
import { toast } from 'sonner';

// Helper function to build full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  return `${backendUrl}${imageUrl}`;
};

function FeaturedProducts() {
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMenuItems();
  }, []);

  const loadMenuItems = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/menu-items`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (!response.ok) throw new Error('Failed to fetch menu items');

      const data = await response.json();
      // Sort by featured_order
      const sorted = data.sort((a, b) => {
        if (a.is_featured && !b.is_featured) return -1;
        if (!a.is_featured && b.is_featured) return 1;
        return (a.featured_order || 0) - (b.featured_order || 0);
      });
      setMenuItems(sorted);
    } catch (error) {
      console.error('Error loading menu items:', error);
      toast.error('Fehler beim Laden der Produkte');
    } finally {
      setLoading(false);
    }
  };

  const toggleFeatured = async (item) => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/menu-items/${item.id}/featured?is_featured=${!item.is_featured}`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (!response.ok) throw new Error('Failed to update');

      toast.success(item.is_featured ? 'Aus Featured entfernt' : 'Als Featured markiert');
      loadMenuItems();
    } catch (error) {
      console.error('Error updating featured status:', error);
      toast.error('Fehler beim Aktualisieren');
    }
  };

  const updateBadge = async (itemId, badge) => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/menu-items/${itemId}/featured?is_featured=true&badge=${badge || ''}`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (!response.ok) throw new Error('Failed to update badge');

      toast.success('Badge aktualisiert');
      loadMenuItems();
    } catch (error) {
      console.error('Error updating badge:', error);
      toast.error('Fehler beim Aktualisieren');
    }
  };

  const badges = [
    { value: '', label: 'Kein Badge' },
    { value: 'new', label: 'NEU', color: 'bg-blue-500' },
    { value: 'limited', label: 'Nur kurze Zeit', color: 'bg-orange-500' },
    { value: 'bestseller', label: 'Bestseller', color: 'bg-green-500' },
    { value: 'hot', label: 'Hot Deal', color: 'bg-red-500' }
  ];

  const featuredItems = menuItems.filter(item => item.is_featured);
  const otherItems = menuItems.filter(item => !item.is_featured);

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container-custom">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-serif font-bold mb-2">Featured Products</h1>
          <p className="text-sm text-muted-foreground">
            Wähle Produkte aus, die auf der Homepage im Hero-Bereich angezeigt werden sollen
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Featured Items */}
            {featuredItems.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Star className="h-5 w-5 text-primary fill-primary" />
                  Featured Produkte ({featuredItems.length})
                </h2>
                <div className="grid gap-4">
                  {featuredItems.map((item) => (
                    <div
                      key={item.id}
                      className="bg-card border-2 border-primary/50 rounded-lg p-4"
                      data-testid={`featured-item-${item.id}`}
                    >
                      <div className="flex items-start gap-4">
                        {/* Image */}
                        {item.image_url && (
                          <img
                            src={item.image_url}
                            alt={item.name}
                            className="w-20 h-20 object-cover rounded-lg"
                          />
                        )}

                        {/* Info */}
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h3 className="font-semibold">{item.name}</h3>
                              <p className="text-sm text-muted-foreground line-clamp-1">
                                {item.description}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-lg font-bold text-primary">
                                €{(item.price_normal || item.price_medium || 0).toFixed(2)}
                              </p>
                            </div>
                          </div>

                          {/* Badge Selection */}
                          <div className="flex items-center gap-2 mb-3">
                            <Tag className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm text-muted-foreground">Badge:</span>
                            <select
                              value={item.badge || ''}
                              onChange={(e) => updateBadge(item.id, e.target.value)}
                              className="px-3 py-1 text-sm bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                            >
                              {badges.map((badge) => (
                                <option key={badge.value} value={badge.value}>
                                  {badge.label}
                                </option>
                              ))}
                            </select>
                            {item.badge && (
                              <span
                                className={`px-2 py-1 text-xs text-white rounded-full ${
                                  badges.find((b) => b.value === item.badge)?.color || 'bg-gray-500'
                                }`}
                              >
                                {badges.find((b) => b.value === item.badge)?.label}
                              </span>
                            )}
                          </div>

                          {/* Actions */}
                          <button
                            onClick={() => toggleFeatured(item)}
                            className="btn-secondary text-sm flex items-center gap-2"
                          >
                            <EyeOff className="h-4 w-4" />
                            Aus Featured entfernen
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Other Items */}
            <div>
              <h2 className="text-lg font-semibold mb-4">
                Alle Produkte ({otherItems.length})
              </h2>
              <div className="grid gap-3">
                {otherItems.map((item) => (
                  <div
                    key={item.id}
                    className="bg-card border border-border rounded-lg p-4 hover:border-primary/30 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      {/* Image */}
                      {item.image_url && (
                        <img
                          src={item.image_url}
                          alt={item.name}
                          className="w-16 h-16 object-cover rounded-lg"
                        />
                      )}

                      {/* Info */}
                      <div className="flex-1">
                        <h3 className="font-semibold">{item.name}</h3>
                        <p className="text-sm text-muted-foreground line-clamp-1">
                          {item.description}
                        </p>
                      </div>

                      {/* Price & Action */}
                      <div className="text-right">
                        <p className="text-lg font-bold text-primary mb-2">
                          €{(item.price_normal || item.price_medium || 0).toFixed(2)}
                        </p>
                        <button
                          onClick={() => toggleFeatured(item)}
                          className="btn-primary text-sm flex items-center gap-2"
                        >
                          <Eye className="h-4 w-4" />
                          Featured machen
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default FeaturedProducts;

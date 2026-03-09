import React from 'react';

/**
 * ProductBadge Component
 * 
 * Displays dynamic badges for products based on performance metrics
 * 
 * Badge Types:
 * - bestseller: Top selling products (auto)
 * - trending: Fast-growing sales (auto)
 * - new: Recently added products (auto)
 * - chefs_special: Chef recommendations (manual)
 * - limited: Limited time offers (manual)
 * - popular: Popular this week (auto)
 */

const ProductBadge = ({ badge, customText, className = "" }) => {
  // Badge configurations
  const badges = {
    bestseller: {
      text: 'Bestseller',
      color: 'bg-gradient-to-r from-green-500 to-green-600',
      textColor: 'text-white',
      icon: '🏆',
      priority: 1
    },
    trending: {
      text: 'Trending',
      color: 'bg-gradient-to-r from-orange-500 to-red-500',
      textColor: 'text-white',
      icon: '🔥',
      priority: 2
    },
    new: {
      text: 'Neu',
      color: 'bg-gradient-to-r from-blue-500 to-blue-600',
      textColor: 'text-white',
      icon: '🆕',
      priority: 3
    },
    chefs_special: {
      text: "Chef's Special",
      color: 'bg-gradient-to-r from-yellow-500 to-yellow-600',
      textColor: 'text-gray-900',
      icon: '👨‍🍳',
      priority: 2
    },
    limited: {
      text: 'Nur heute',
      color: 'bg-gradient-to-r from-red-600 to-red-700',
      textColor: 'text-white',
      icon: '⏰',
      priority: 1
    },
    popular: {
      text: 'Beliebt',
      color: 'bg-gradient-to-r from-purple-500 to-purple-600',
      textColor: 'text-white',
      icon: '⭐',
      priority: 3
    },
    seasonal: {
      text: 'Saison-Special',
      color: 'bg-gradient-to-r from-pink-500 to-pink-600',
      textColor: 'text-white',
      icon: '🌸',
      priority: 4
    }
  };

  // Get badge configuration
  const badgeConfig = badges[badge];
  
  // If no valid badge, return null
  if (!badgeConfig && !customText) return null;

  // Use custom text if provided
  const displayText = customText || badgeConfig?.text || 'Special';
  const displayColor = badgeConfig?.color || 'bg-gray-500';
  const displayTextColor = badgeConfig?.textColor || 'text-white';
  const displayIcon = badgeConfig?.icon || '✨';

  return (
    <div
      className={`
        inline-flex items-center gap-2 
        ${displayColor} ${displayTextColor}
        px-3 py-1.5 
        rounded-full 
        text-xs font-semibold 
        shadow-lg
        backdrop-blur-sm
        animate-fade-in
        ${className}
      `}
      data-testid={`badge-${badge || 'custom'}`}
    >
      <span className="text-sm" role="img" aria-label={displayText}>
        {displayIcon}
      </span>
      <span>{displayText}</span>
    </div>
  );
};

/**
 * ProductBadges Component
 * 
 * Displays multiple badges with priority ordering
 * Shows max 2 badges per product to avoid clutter
 */
export const ProductBadges = ({ product, className = "", position = "top-right" }) => {
  const badges = [];

  // Collect all applicable badges
  if (product.auto_badge) {
    badges.push({ type: product.auto_badge, priority: product.auto_badge_priority || 10 });
  }
  if (product.manual_badge) {
    badges.push({ type: product.manual_badge, priority: 1 }); // Manual badges have high priority
  }

  // Sort by priority (lower number = higher priority)
  badges.sort((a, b) => a.priority - b.priority);

  // Take max 2 badges
  const displayBadges = badges.slice(0, 2);

  if (displayBadges.length === 0) return null;

  // Position classes
  const positions = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4'
  };

  return (
    <div className={`absolute ${positions[position]} flex flex-col gap-2 z-10 ${className}`}>
      {displayBadges.map((badge, idx) => (
        <ProductBadge key={idx} badge={badge.type} />
      ))}
    </div>
  );
};

/**
 * BadgeFilter Component
 * 
 * Filter products by badge type (for menu page)
 */
export const BadgeFilter = ({ selectedBadge, onSelectBadge, badges = [] }) => {
  const allBadges = [
    { id: 'all', label: 'Alle', icon: '🍔' },
    { id: 'bestseller', label: 'Bestseller', icon: '🏆' },
    { id: 'trending', label: 'Trending', icon: '🔥' },
    { id: 'new', label: 'Neu', icon: '🆕' },
    { id: 'chefs_special', label: \"Chef's Special\", icon: '👨‍🍳' }
  ];

  return (
    <div className="flex gap-2 overflow-x-auto pb-2" data-testid="badge-filter">
      {allBadges.map(badge => (
        <button
          key={badge.id}
          onClick={() => onSelectBadge(badge.id)}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-full
            text-sm font-medium whitespace-nowrap
            transition-all duration-200
            ${selectedBadge === badge.id 
              ? 'bg-red-600 text-white shadow-lg scale-105' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }
          `}
          data-testid={`filter-${badge.id}`}
        >
          <span role="img" aria-label={badge.label}>{badge.icon}</span>
          <span>{badge.label}</span>
        </button>
      ))}
    </div>
  );
};

export default ProductBadge;

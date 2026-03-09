import React, { useState } from 'react';
import { Filter, Leaf, Flame, X } from 'lucide-react';

function MenuFilters({ onFilterChange }) {
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState({
    vegetarian: false,
    vegan: false,
    spicy: false,
    allergens: []
  });

  const allergenOptions = [
    { value: 'gluten', label: 'Gluten' },
    { value: 'milk', label: 'Milch' },
    { value: 'eggs', label: 'Eier' },
    { value: 'nuts', label: 'Nüsse' },
    { value: 'soy', label: 'Soja' },
    { value: 'fish', label: 'Fisch' },
    { value: 'shellfish', label: 'Schalen­tiere' },
    { value: 'sesame', label: 'Sesam' }
  ];

  const toggleFilter = (filterType, value = null) => {
    let newFilters = { ...activeFilters };

    if (filterType === 'allergens' && value) {
      if (newFilters.allergens.includes(value)) {
        newFilters.allergens = newFilters.allergens.filter(a => a !== value);
      } else {
        newFilters.allergens = [...newFilters.allergens, value];
      }
    } else {
      newFilters[filterType] = !newFilters[filterType];
    }

    setActiveFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearAllFilters = () => {
    const emptyFilters = {
      vegetarian: false,
      vegan: false,
      spicy: false,
      allergens: []
    };
    setActiveFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const activeFilterCount = 
    (activeFilters.vegetarian ? 1 : 0) +
    (activeFilters.vegan ? 1 : 0) +
    (activeFilters.spicy ? 1 : 0) +
    activeFilters.allergens.length;

  return (
    <div className="mb-6">
      {/* Filter Toggle Button */}
      <button
        onClick={() => setShowFilters(!showFilters)}
        className="flex items-center gap-2 px-4 py-2 bg-accent border border-border rounded-lg hover:border-primary/40 transition-colors"
        data-testid="filter-toggle"
      >
        <Filter className="h-4 w-4" />
        <span className="text-sm font-medium">Filter</span>
        {activeFilterCount > 0 && (
          <span className="bg-primary text-primary-foreground text-xs px-2 py-0.5 rounded-full">
            {activeFilterCount}
          </span>
        )}
      </button>

      {/* Filter Panel */}
      {showFilters && (
        <div className="mt-3 bg-accent border border-border rounded-lg p-4 space-y-4">
          {/* Dietary Preferences */}
          <div>
            <h4 className="text-sm font-semibold mb-2">Ernährung</h4>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => toggleFilter('vegetarian')}
                className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 transition-all ${
                  activeFilters.vegetarian
                    ? 'bg-green-500/20 text-green-700 dark:text-green-400 border-2 border-green-500'
                    : 'bg-background border border-border hover:border-primary/40'
                }`}
              >
                <Leaf className="h-4 w-4" />
                Vegetarisch
              </button>
              <button
                onClick={() => toggleFilter('vegan')}
                className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 transition-all ${
                  activeFilters.vegan
                    ? 'bg-green-500/20 text-green-700 dark:text-green-400 border-2 border-green-500'
                    : 'bg-background border border-border hover:border-primary/40'
                }`}
              >
                <Leaf className="h-4 w-4" />
                Vegan
              </button>
              <button
                onClick={() => toggleFilter('spicy')}
                className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 transition-all ${
                  activeFilters.spicy
                    ? 'bg-red-500/20 text-red-700 dark:text-red-400 border-2 border-red-500'
                    : 'bg-background border border-border hover:border-primary/40'
                }`}
              >
                <Flame className="h-4 w-4" />
                Scharf
              </button>
            </div>
          </div>

          {/* Allergen Filters */}
          <div>
            <h4 className="text-sm font-semibold mb-2">Ohne Allergene</h4>
            <p className="text-xs text-muted-foreground mb-2">
              Wähle Allergene aus, die du vermeiden möchtest
            </p>
            <div className="flex flex-wrap gap-2">
              {allergenOptions.map((allergen) => (
                <button
                  key={allergen.value}
                  onClick={() => toggleFilter('allergens', allergen.value)}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
                    activeFilters.allergens.includes(allergen.value)
                      ? 'bg-orange-500/20 text-orange-700 dark:text-orange-400 border-2 border-orange-500'
                      : 'bg-background border border-border hover:border-primary/40'
                  }`}
                >
                  {allergen.label}
                </button>
              ))}
            </div>
          </div>

          {/* Clear Filters */}
          {activeFilterCount > 0 && (
            <button
              onClick={clearAllFilters}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 rounded-lg text-sm transition-colors"
            >
              <X className="h-4 w-4" />
              Alle Filter zurücksetzen
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default MenuFilters;

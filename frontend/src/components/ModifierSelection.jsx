import React, { useState, useEffect } from 'react';
import { Label } from './ui/label';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';

/**
 * Modifier Selection Component
 * Shows modifier groups (e.g. Dressing, Pasta Type, Extras)
 */
export function ModifierSelection({ product, modifierGroups, onModifiersChange }) {
  const [selectedModifiers, setSelectedModifiers] = useState({});
  
  // Get modifier groups for this product
  const productModifierGroups = modifierGroups.filter(group => 
    product.modifier_group_ids?.includes(group.id)
  );
  
  // Initialize with defaults
  useEffect(() => {
    const defaults = {};
    productModifierGroups.forEach(group => {
      const defaultOption = group.options.find(opt => opt.default);
      if (defaultOption) {
        defaults[group.id] = defaultOption.name;
      }
    });
    setSelectedModifiers(defaults);
    onModifiersChange?.(defaults);
  }, [product.id]);
  
  const handleModifierChange = (groupId, optionName) => {
    const updated = { ...selectedModifiers, [groupId]: optionName };
    setSelectedModifiers(updated);
    onModifiersChange?.(updated);
  };
  
  if (!productModifierGroups || productModifierGroups.length === 0) {
    return null;
  }
  
  return (
    <div className="space-y-4 mt-4">
      {productModifierGroups.map((group) => (
        <div key={group.id} className="space-y-2">
          <Label className="text-base font-semibold">
            {group.title}
            {group.required && <span className="text-red-500 ml-1">*</span>}
          </Label>
          
          <RadioGroup
            value={selectedModifiers[group.id] || ''}
            onValueChange={(value) => handleModifierChange(group.id, value)}
          >
            {group.options.map((option) => {
              const priceText = option.price > 0 ? ` (+€${option.price.toFixed(2)})` : '';
              
              return (
                <div key={option.name} className="flex items-center space-x-2">
                  <RadioGroupItem value={option.name} id={`${group.id}-${option.name}`} />
                  <Label 
                    htmlFor={`${group.id}-${option.name}`}
                    className="font-normal cursor-pointer"
                  >
                    {option.name}{priceText}
                  </Label>
                </div>
              );
            })}
          </RadioGroup>
        </div>
      ))}
    </div>
  );
}

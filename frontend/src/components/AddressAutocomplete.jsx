import React, { useEffect, useState } from 'react';
import usePlacesAutocomplete, { getGeocode, getLatLng } from 'use-places-autocomplete';
import { Input } from './ui/input';
import { MapPin } from 'lucide-react';

const GOOGLE_MAPS_API_KEY = 'AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8';

/**
 * Google Maps Autocomplete for Address Input
 * 
 * Shows suggestions as user types, auto-fills address fields
 */
export function AddressAutocomplete({ onAddressSelect, initialValue = '', placeholder = 'Straße und Hausnummer' }) {
  const {
    ready,
    value,
    suggestions: { status, data },
    setValue,
    clearSuggestions,
  } = usePlacesAutocomplete({
    requestOptions: {
      componentRestrictions: { country: 'de' }, // Only Germany
    },
    debounce: 300,
  });

  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleSelect = async (description) => {
    setValue(description, false);
    clearSuggestions();
    setShowSuggestions(false);

    try {
      const results = await getGeocode({ address: description });
      const { lat, lng } = await getLatLng(results[0]);
      
      // Parse address components
      const addressComponents = results[0].address_components;
      
      let street = '';
      let houseNumber = '';
      let postalCode = '';
      let city = '';
      
      addressComponents.forEach(component => {
        if (component.types.includes('route')) {
          street = component.long_name;
        }
        if (component.types.includes('street_number')) {
          houseNumber = component.long_name;
        }
        if (component.types.includes('postal_code')) {
          postalCode = component.long_name;
        }
        if (component.types.includes('locality')) {
          city = component.long_name;
        }
      });
      
      const fullAddress = houseNumber ? `${street} ${houseNumber}` : street;
      
      onAddressSelect?.({
        address: fullAddress,
        postalCode,
        city,
        lat,
        lng,
        formatted: description
      });
      
    } catch (error) {
      console.error('Error getting geocode:', error);
    }
  };

  return (
    <div className="relative">
      <div className="relative">
        <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            setShowSuggestions(true);
          }}
          onFocus={() => setShowSuggestions(true)}
          disabled={!ready}
          placeholder={placeholder}
          className="pl-10"
        />
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && status === 'OK' && (
        <div className="absolute z-50 w-full mt-1 bg-card border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {data.map((suggestion) => (
            <button
              key={suggestion.place_id}
              onClick={() => handleSelect(suggestion.description)}
              className="w-full px-4 py-3 text-left hover:bg-secondary transition-colors border-b border-border last:border-0"
            >
              <div className="flex items-start gap-2">
                <MapPin className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium">{suggestion.structured_formatting.main_text}</p>
                  <p className="text-xs text-muted-foreground">
                    {suggestion.structured_formatting.secondary_text}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Load Google Maps Script
export function loadGoogleMapsScript(callback) {
  if (window.google && window.google.maps) {
    callback();
    return;
  }

  const script = document.createElement('script');
  script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=places`;
  script.async = true;
  script.defer = true;
  script.onload = callback;
  document.head.appendChild(script);
}

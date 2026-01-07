import React, { createContext, useContext, useState, useEffect } from 'react';

const FeatureContext = createContext({
  features: {},
  loading: true,
  isFeatureEnabled: () => false,
  refreshFeatures: () => {}
});

export function FeatureProvider({ children }) {
  const [features, setFeatures] = useState({});
  const [loading, setLoading] = useState(true);

  const loadFeatures = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/features`);
      if (response.ok) {
        const data = await response.json();
        setFeatures(data);
      }
    } catch (error) {
      console.error('Error loading features:', error);
      // Default all features to true if API fails
      setFeatures({
        burger_builder: true,
        order_tracking: true,
        daily_deals: true,
        group_orders: true,
        rewards: true,
        reviews: true
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFeatures();
  }, []);

  const isFeatureEnabled = (featureKey) => {
    return features[featureKey] === true;
  };

  const refreshFeatures = () => {
    loadFeatures();
  };

  return (
    <FeatureContext.Provider value={{ features, loading, isFeatureEnabled, refreshFeatures }}>
      {children}
    </FeatureContext.Provider>
  );
}

export function useFeatures() {
  const context = useContext(FeatureContext);
  if (!context) {
    throw new Error('useFeatures must be used within a FeatureProvider');
  }
  return context;
}

export default FeatureContext;

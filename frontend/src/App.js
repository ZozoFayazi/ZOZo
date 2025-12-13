import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import Header from './components/Header';
import Footer from './components/Footer';
import ScrollToTop from './components/ScrollToTop';
import HomePage from './pages/HomePage';
import MenuPage from './pages/MenuPage';
import LocationsPage from './pages/LocationsPage';
import OrderTracking from './pages/OrderTracking';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import LocationSettings from './pages/LocationSettings';
import DealsManagement from './pages/DealsManagement';
import ExpertOrderSettings from './pages/ExpertOrderSettings';
import MenuManagement from './pages/MenuManagement';
import DiscountCodes from './pages/DiscountCodes';
import OrderManagement from './pages/OrderManagement';
import FeaturedProducts from './pages/FeaturedProducts';
import './App.css';

function App() {
  const [cart, setCart] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);

  // Load cart from localStorage
  useEffect(() => {
    const savedCart = localStorage.getItem('zozoCart');
    if (savedCart) {
      try {
        setCart(JSON.parse(savedCart));
      } catch (e) {
        console.error('Error loading cart:', e);
      }
    }
  }, []);

  // Save cart to localStorage
  useEffect(() => {
    localStorage.setItem('zozoCart', JSON.stringify(cart));
  }, [cart]);

  const addToCart = (item) => {
    const existingItemIndex = cart.findIndex(
      (cartItem) => cartItem.menu_item_id === item.menu_item_id && cartItem.size === item.size
    );

    if (existingItemIndex !== -1) {
      const newCart = [...cart];
      newCart[existingItemIndex].quantity += item.quantity;
      setCart(newCart);
    } else {
      setCart([...cart, item]);
    }
  };

  const removeFromCart = (menu_item_id, size) => {
    setCart(cart.filter(item => !(item.menu_item_id === menu_item_id && item.size === size)));
  };

  const updateCartItemQuantity = (menu_item_id, size, quantity) => {
    if (quantity <= 0) {
      removeFromCart(menu_item_id, size);
    } else {
      setCart(cart.map(item =>
        item.menu_item_id === menu_item_id && item.size === size
          ? { ...item, quantity }
          : item
      ));
    }
  };

  const clearCart = () => {
    setCart([]);
    localStorage.removeItem('zozoCart');
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const deliveryFee = cartTotal < 15 ? 2.50 : 0;

  return (
    <Router>
      <div className="min-h-screen bg-background text-foreground">
        <Header
          cart={cart}
          cartTotal={cartTotal}
          removeFromCart={removeFromCart}
          updateCartItemQuantity={updateCartItemQuantity}
          clearCart={clearCart}
          selectedLocation={selectedLocation}
          addToCart={addToCart}
        />
        <Routes>
          <Route
            path="/"
            element={
              <HomePage
                selectedLocation={selectedLocation}
                setSelectedLocation={setSelectedLocation}
              />
            }
          />
          <Route
            path="/menu"
            element={
              <MenuPage
                selectedLocation={selectedLocation}
                setSelectedLocation={setSelectedLocation}
                addToCart={addToCart}
              />
            }
          />
          <Route
            path="/locations"
            element={<LocationsPage setSelectedLocation={setSelectedLocation} />}
          />
          <Route path="/order-tracking" element={<OrderTracking />} />
          <Route path="/admin" element={<AdminLogin />} />
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/settings" element={<LocationSettings />} />
          <Route path="/admin/deals" element={<DealsManagement />} />
          <Route path="/admin/expertorder" element={<ExpertOrderSettings />} />
          <Route path="/admin/menu" element={<MenuManagement />} />
          <Route path="/admin/discount-codes" element={<DiscountCodes />} />
          <Route path="/admin/orders" element={<OrderManagement />} />
          <Route path="/admin/featured" element={<FeaturedProducts />} />
        </Routes>
        <ScrollToTop />
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: 'hsl(var(--card))',
              color: 'hsl(var(--foreground))',
              border: '1px solid hsl(var(--border))',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;

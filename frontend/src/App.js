import React, { useState, useEffect, lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import ErrorBoundary from './components/ErrorBoundary';
import Header from './components/Header';
import Footer from './components/Footer';
import ScrollToTop from './components/ScrollToTop';
import MobileBottomNav from './components/MobileBottomNav';
import { AdminAuthProvider } from './contexts/AdminAuthContext';
import { ProtectedAdminRoute } from './components/ProtectedAdminRoute';
import HomePage from './pages/HomePage';
import MenuPage from './pages/MenuPage';
import './App.css';

// Lazy load non-critical pages
const LocationsPage = lazy(() => import('./pages/LocationsPage'));
const OrderTracking = lazy(() => import('./pages/OrderTracking'));
const BurgerBuilder = lazy(() => import('./pages/BurgerBuilder'));
const MyCreations = lazy(() => import('./pages/MyCreations'));
const AdminLogin = lazy(() => import('./pages/AdminLogin'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));
const LocationSettings = lazy(() => import('./pages/LocationSettings'));
const LocationManagement = lazy(() => import('./pages/LocationManagement'));
const DealsManagement = lazy(() => import('./pages/DealsManagement'));
const ExpertOrderSettings = lazy(() => import('./pages/ExpertOrderSettings'));
const MenuManagement = lazy(() => import('./pages/MenuManagement'));
const ProductManagement = lazy(() => import('./pages/ProductManagement'));
const DiscountCodes = lazy(() => import('./pages/DiscountCodes'));
const OrderManagement = lazy(() => import('./pages/OrderManagement'));
const FeaturedProducts = lazy(() => import('./pages/FeaturedProducts'));
const RewardsPage = lazy(() => import('./pages/RewardsPage'));
const StartGroupOrder = lazy(() => import('./pages/StartGroupOrder'));
const GroupOrderPage = lazy(() => import('./pages/GroupOrderPage'));
const POSSettings = lazy(() => import('./pages/POSSettings'));
const FailedPOSOrders = lazy(() => import('./pages/FailedPOSOrders'));
const LocationDetailPage = lazy(() => import('./pages/LocationDetailPage'));
const SecurityDashboard = lazy(() => import('./pages/SecurityDashboard'));

// Loading component
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-background">
    <div className="text-center space-y-4">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
      <p className="text-muted-foreground">Lädt...</p>
    </div>
  </div>
);

function App() {
  const [cart, setCart] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [cartOpen, setCartOpen] = useState(false);

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
    <ErrorBoundary>
      <AdminAuthProvider>
        <Router>
          <div className="min-h-screen bg-background text-foreground">
          {/* Skip to main content for keyboard users */}
          <a href="#main-content" className="skip-to-main">
            Zum Hauptinhalt springen
          </a>
          
          <Header
          cart={cart}
          cartTotal={cartTotal}
          removeFromCart={removeFromCart}
          updateCartItemQuantity={updateCartItemQuantity}
          clearCart={clearCart}
          selectedLocation={selectedLocation}
          addToCart={addToCart}
          cartOpen={cartOpen}
          setCartOpen={setCartOpen}
        />
        <main id="main-content" role="main">
          <Suspense fallback={<PageLoader />}>
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
            <Route
              path="/standorte"
              element={<LocationsPage setSelectedLocation={setSelectedLocation} />}
            />
            <Route
              path="/standorte/:slug"
              element={<LocationDetailPage setSelectedLocation={setSelectedLocation} />}
            />
            <Route path="/order-tracking" element={<OrderTracking />} />
            <Route path="/burger-builder" element={<BurgerBuilder addToCart={addToCart} />} />
          <Route path="/my-creations" element={<MyCreations addToCart={addToCart} />} />
          <Route path="/rewards" element={<RewardsPage />} />
          <Route path="/start-group-order" element={<StartGroupOrder selectedLocation={selectedLocation} setSelectedLocation={setSelectedLocation} />} />
          <Route path="/group-order/:groupCode" element={<GroupOrderPage addToCart={addToCart} selectedLocation={selectedLocation} />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
          <Route 
            path="/admin/dashboard" 
            element={
              <ProtectedAdminRoute>
                <AdminDashboard />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/locations" 
            element={
              <ProtectedAdminRoute>
                <LocationManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/settings" 
            element={
              <ProtectedAdminRoute requiredPermission="manage_branch_rellingen">
                <LocationSettings />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/deals" 
            element={
              <ProtectedAdminRoute>
                <DealsManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/expertorder" 
            element={
              <ProtectedAdminRoute>
                <ExpertOrderSettings />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/menu" 
            element={
              <ProtectedAdminRoute>
                <ProductManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/discount-codes" 
            element={
              <ProtectedAdminRoute>
                <DiscountCodes />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/orders" 
            element={
              <ProtectedAdminRoute>
                <OrderManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/featured" 
            element={
              <ProtectedAdminRoute>
                <FeaturedProducts />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/pos" 
            element={
              <ProtectedAdminRoute>
                <POSSettings />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/security" 
            element={
              <ProtectedAdminRoute>
                <SecurityDashboard />
              </ProtectedAdminRoute>
            } 
          />
            </Routes>
          </Suspense>
        </main>

        <Footer />
        <ScrollToTop />
        <MobileBottomNav 
          cartItemCount={cart.reduce((sum, item) => sum + item.quantity, 0)}
          onCartClick={() => setCartOpen(true)}
        />
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
      </AdminAuthProvider>
    </ErrorBoundary>
  );
}

export default App;

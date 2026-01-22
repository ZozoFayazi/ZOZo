import React, { useState, useEffect, lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import ErrorBoundary from './components/ErrorBoundary';
import Header from './components/Header';
import Footer from './components/Footer';
import ScrollToTop from './components/ScrollToTop';
import MobileBottomNav from './components/MobileBottomNav';
import CookieBanner from './components/CookieBanner';
import { AdminAuthProvider } from './contexts/AdminAuthContext';
import { FeatureProvider } from './contexts/FeatureContext';
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
const LocationSettings = lazy(() => import('./pages/LocationSettingsV2'));
const LocationManagement = lazy(() => import('./pages/LocationManagement'));
const DealsManagement = lazy(() => import('./pages/DealsManagement'));
const DailyDealsAdmin = lazy(() => import('./pages/DailyDealsAdmin'));
const ExpertOrderSettings = lazy(() => import('./pages/ExpertOrderSettings'));
const MenuManagement = lazy(() => import('./pages/MenuManagement'));
const ProductManagement = lazy(() => import('./pages/ProductManagement'));
const CategoryManagement = lazy(() => import('./pages/CategoryManagement'));
const OpeningHoursManagement = lazy(() => import('./pages/OpeningHoursManagement'));
const TenantOnboardingWizard = lazy(() => import('./pages/TenantOnboardingWizard'));
const TenantsManagement = lazy(() => import('./pages/TenantsManagement'));


const DiscountCodes = lazy(() => import('./pages/DiscountCodes'));
const OrderManagement = lazy(() => import('./pages/OrderManagement'));
const FeaturedProducts = lazy(() => import('./pages/FeaturedProducts'));
const RewardsPage = lazy(() => import('./pages/RewardsPage'));
const StartGroupOrder = lazy(() => import('./pages/StartGroupOrder'));
const GroupOrderPage = lazy(() => import('./pages/GroupOrderPage'));
const POSSettings = lazy(() => import('./pages/POSSettings'));
const FailedPOSOrders = lazy(() => import('./pages/FailedPOSOrders'));
const FailedOrdersQueue = lazy(() => import('./pages/FailedOrdersQueue'));
const AGB = lazy(() => import('./pages/AGB'));
const LocationDetailPage = lazy(() => import('./pages/LocationDetailPage'));
const SecurityDashboard = lazy(() => import('./pages/SecurityDashboard'));
const FeatureToggles = lazy(() => import('./pages/FeatureToggles'));
const Impressum = lazy(() => import('./pages/Impressum'));
const Datenschutz = lazy(() => import('./pages/Datenschutz'));
const Kontakt = lazy(() => import('./pages/Kontakt'));
const Rechtliches = lazy(() => import('./pages/Rechtliches'));
const NewsletterManagement = lazy(() => import('./pages/NewsletterManagement'));
const CampaignManagement = lazy(() => import('./pages/CampaignManagement'));
const CampaignEditor = lazy(() => import('./pages/CampaignEditor'));
const POSItemMapping = lazy(() => import('./pages/POSItemMapping'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Customers = lazy(() => import('./pages/Customers'));
const CustomerDetail = lazy(() => import('./pages/CustomerDetail'));
const Finance = lazy(() => import('./pages/Finance'));

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

  // Load cart and location from localStorage
  useEffect(() => {
    const savedCart = localStorage.getItem('zozoCart');
    if (savedCart) {
      try {
        setCart(JSON.parse(savedCart));
      } catch (e) {
        console.error('Error loading cart:', e);
      }
    }

    const savedLocation = localStorage.getItem('zozoSelectedLocation');
    if (savedLocation) {
      try {
        setSelectedLocation(JSON.parse(savedLocation));
      } catch (e) {
        console.error('Error loading location:', e);
      }
    }
  }, []);

  // Save cart to localStorage
  useEffect(() => {
    localStorage.setItem('zozoCart', JSON.stringify(cart));
  }, [cart]);

  // Save location to localStorage
  useEffect(() => {
    if (selectedLocation) {
      localStorage.setItem('zozoSelectedLocation', JSON.stringify(selectedLocation));
    } else {
      localStorage.removeItem('zozoSelectedLocation');
    }
  }, [selectedLocation]);

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
  const deliveryFee = 0; // Kostenlose Lieferung

  return (
    <ErrorBoundary>
      <AdminAuthProvider>
        <FeatureProvider>
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
          
          {/* Legal Pages */}
          <Route path="/impressum" element={<Impressum />} />
          <Route path="/datenschutz" element={<Datenschutz />} />
          <Route path="/kontakt" element={<Kontakt />} />
          <Route path="/rechtliches" element={<Rechtliches />} />
          <Route path="/agb" element={<AGB />} />
          
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
            path="/admin/analytics" 
            element={
              <ProtectedAdminRoute>
                <Analytics />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/customers" 
            element={
              <ProtectedAdminRoute>
                <Customers />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/customers/:customerId" 
            element={
              <ProtectedAdminRoute>
                <CustomerDetail />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/finance" 
            element={
              <ProtectedAdminRoute>
                <Finance />
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
            path="/admin/products" 
            element={
              <ProtectedAdminRoute>
                <ProductManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/categories" 
            element={
              <ProtectedAdminRoute>
                <CategoryManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/opening-hours" 
            element={
              <ProtectedAdminRoute>
                <OpeningHoursManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/tenants" 
            element={
              <ProtectedAdminRoute requireSuperAdmin>
                <TenantsManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/tenants/new" 
            element={
              <ProtectedAdminRoute requireSuperAdmin>
                <TenantOnboardingWizard />
              </ProtectedAdminRoute>
            } 
          />


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
            path="/admin/daily-deals" 
            element={
              <ProtectedAdminRoute>
                <DailyDealsAdmin />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/features" 
            element={
              <ProtectedAdminRoute>
                <FeatureToggles />
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
            path="/admin/pos/failed-orders" 
            element={
              <ProtectedAdminRoute>
                <FailedOrdersQueue />
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
          <Route 
            path="/admin/newsletter" 
            element={
              <ProtectedAdminRoute>
                <NewsletterManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/newsletter/campaigns" 
            element={
              <ProtectedAdminRoute>
                <CampaignManagement />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/newsletter/campaigns/new" 
            element={
              <ProtectedAdminRoute>
                <CampaignEditor />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/newsletter/campaigns/:id" 
            element={
              <ProtectedAdminRoute>
                <CampaignEditor />
              </ProtectedAdminRoute>
            } 
          />
          <Route 
            path="/admin/pos-mapping" 
            element={
              <ProtectedAdminRoute>
                <POSItemMapping />
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
        <CookieBanner />
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
        </FeatureProvider>
      </AdminAuthProvider>
    </ErrorBoundary>
  );
}

export default App;

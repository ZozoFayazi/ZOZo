import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShoppingCart, Menu, X, MapPin } from 'lucide-react';
import CartDrawer from './CartDrawer';
import QuickReorder from './QuickReorder';

function Header({ cart, cartTotal, removeFromCart, updateCartItemQuantity, clearCart, selectedLocation, addToCart }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const location = useLocation();

  const cartItemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  const isActive = (path) => location.pathname === path;

  return (
    <>
      <header className="sticky top-0 z-50 glass border-b border-border/50">
        <nav className="container-custom">
          <div className="flex items-center justify-between h-18 py-3">
            {/* Logo with Subtle Scale Animation */}
            <Link to="/" className="flex items-center space-x-3 group" data-testid="header-logo">
              <img
                src="https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg"
                alt="ZOZO Burger"
                className="h-12 w-auto group-hover:scale-105 transition-transform"
              />
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link
                to="/"
                className={`text-sm font-medium transition-colors ${
                  isActive('/') ? 'text-primary' : 'text-foreground/80 hover:text-foreground'
                }`}
              >
                Home
              </Link>
              <Link
                to="/menu"
                className={`text-sm font-medium transition-colors ${
                  isActive('/menu') ? 'text-primary' : 'text-foreground/80 hover:text-foreground'
                }`}
              >
                Speisekarte
              </Link>
              <Link
                to="/locations"
                className={`text-sm font-medium transition-colors ${
                  isActive('/locations') ? 'text-primary' : 'text-foreground/80 hover:text-foreground'
                }`}
              >
                Standorte
              </Link>
            </div>

            {/* Right side: Location, Quick Reorder & Cart */}
            <div className="flex items-center space-x-2 md:space-x-4">
              {/* Selected Location Indicator */}
              {selectedLocation && (
                <div className="hidden sm:flex items-center space-x-2 text-xs text-muted-foreground">
                  <MapPin className="h-4 w-4" />
                  <span>{selectedLocation.name.replace('ZOZO Burger ', '')}</span>
                </div>
              )}

              {/* Quick Reorder */}
              <div className="hidden md:block">
                <QuickReorder onReorder={addToCart} />
              </div>

              {/* Cart Button */}
              <button
                onClick={() => setCartOpen(true)}
                className="relative p-2 hover:bg-secondary rounded-lg transition-colors"
                data-testid="cart-open-button"
              >
                <ShoppingCart className="h-5 w-5" />
                {cartItemCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 bg-primary text-primary-foreground text-xs font-medium flex items-center justify-center rounded-full">
                    {cartItemCount}
                  </span>
                )}
              </button>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 hover:bg-secondary rounded-lg transition-colors"
              >
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-border animate-fade-in">
              <div className="flex flex-col space-y-3">
                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-2 text-sm font-medium transition-colors ${
                    isActive('/') ? 'text-primary' : 'text-foreground/80'
                  }`}
                >
                  Home
                </Link>
                <Link
                  to="/menu"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-2 text-sm font-medium transition-colors ${
                    isActive('/menu') ? 'text-primary' : 'text-foreground/80'
                  }`}
                >
                  Speisekarte
                </Link>
                <Link
                  to="/locations"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-2 text-sm font-medium transition-colors ${
                    isActive('/locations') ? 'text-primary' : 'text-foreground/80'
                  }`}
                >
                  Standorte
                </Link>
                {selectedLocation && (
                  <div className="flex items-center space-x-2 py-2 text-xs text-muted-foreground">
                    <MapPin className="h-4 w-4" />
                    <span>{selectedLocation.name}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Cart Drawer */}
      <CartDrawer
        open={cartOpen}
        onClose={() => setCartOpen(false)}
        cart={cart}
        cartTotal={cartTotal}
        removeFromCart={removeFromCart}
        updateCartItemQuantity={updateCartItemQuantity}
        clearCart={clearCart}
        selectedLocation={selectedLocation}
      />
    </>
  );
}

export default Header;

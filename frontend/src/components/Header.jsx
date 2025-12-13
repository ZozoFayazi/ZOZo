import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShoppingCart, Menu, X, MapPin } from 'lucide-react';
import CartDrawer from './CartDrawer';

function Header({ cart, cartTotal, removeFromCart, updateCartItemQuantity, clearCart, selectedLocation }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const location = useLocation();

  const cartItemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  const isActive = (path) => location.pathname === path;

  return (
    <>
      <header className="sticky top-0 z-50 glass border-b border-border/50">
        <nav className="container-custom">
          <div className="flex items-center justify-between h-20 py-4">
            {/* LEFT: Navigation Links */}
            <div className="hidden md:flex items-center space-x-8 flex-1">
              <Link
                to="/"
                className={`text-sm font-medium tracking-wide transition-all hover:text-primary ${
                  isActive('/') ? 'text-primary' : 'text-foreground/70'
                }`}
              >
                HOME
              </Link>
              <Link
                to="/menu"
                className={`text-sm font-medium tracking-wide transition-all hover:text-primary ${
                  isActive('/menu') ? 'text-primary' : 'text-foreground/70'
                }`}
              >
                SPEISEKARTE
              </Link>
              <Link
                to="/order-tracking"
                className={`text-sm font-medium tracking-wide transition-all hover:text-primary ${
                  isActive('/order-tracking') ? 'text-primary' : 'text-foreground/70'
                }`}
              >
                BESTELLSTATUS
              </Link>
              <Link
                to="/burger-builder"
                className={`text-sm font-medium tracking-wide transition-all hover:text-primary ${
                  isActive('/burger-builder') ? 'text-primary' : 'text-foreground/70'
                }`}
              >
                🍔 BURGER BUILDER
              </Link>
            </div>

            {/* CENTER: Logo (Larger & Prominent) */}
            <Link 
              to="/" 
              className="flex items-center justify-center absolute left-1/2 transform -translate-x-1/2 md:relative md:left-auto md:transform-none" 
              data-testid="header-logo"
            >
              <img
                src="https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg"
                alt="ZOZO Burger"
                className="h-14 w-auto hover:scale-105 transition-transform"
              />
            </Link>

            {/* RIGHT: Location & Cart */}
            <div className="hidden md:flex items-center space-x-8 flex-1 justify-end">
              <Link
                to="/locations"
                className={`text-sm font-medium tracking-wide transition-all hover:text-primary ${
                  isActive('/locations') ? 'text-primary' : 'text-foreground/70'
                }`}
              >
                STANDORTE
              </Link>

              {/* Location Badge */}
              {selectedLocation && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-accent rounded-lg border border-border/50">
                  <MapPin className="h-3.5 w-3.5 text-primary" />
                  <span className="text-xs font-medium">{selectedLocation.name.replace('ZOZO Burger ', '')}</span>
                </div>
              )}

              {/* Cart Button - Prominent */}
              <button
                onClick={() => setCartOpen(true)}
                className="relative px-4 py-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg transition-all hover:scale-105 flex items-center gap-2 shadow-lg shadow-primary/20"
                data-testid="cart-open-button"
                aria-label={`Warenkorb öffnen, ${cartItemCount} Artikel`}
              >
                <ShoppingCart className="h-5 w-5" aria-hidden="true" />
                {cartItemCount > 0 && (
                  <span className="font-semibold" aria-label={`${cartItemCount} Artikel im Warenkorb`}>
                    {cartItemCount}
                  </span>
                )}
              </button>
            </div>

            {/* Mobile: Cart & Menu */}
            <div className="md:hidden flex items-center space-x-2 ml-auto">
              {/* Mobile Cart */}
              <button
                onClick={() => setCartOpen(true)}
                className="relative p-3 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg transition-all"
                data-testid="cart-button"
              >
                <ShoppingCart className="h-5 w-5" />
                {cartItemCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 bg-foreground text-background text-xs font-bold flex items-center justify-center rounded-full">
                    {cartItemCount}
                  </span>
                )}
              </button>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-3 hover:bg-secondary rounded-lg transition-colors"
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

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShoppingCart, Menu, X, MapPin } from 'lucide-react';
import CartDrawer from './CartDrawer';

function Header({ cart, cartTotal, removeFromCart, updateCartItemQuantity, clearCart, selectedLocation, cartOpen, setCartOpen }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const cartItemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  const isActive = (path) => location.pathname === path;

  return (
    <>
      <header className="sticky top-0 z-50 glass border-b border-border/50" role="banner">
        <nav className="container-custom" role="navigation" aria-label="Hauptnavigation">
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
              <Link
                to="/rewards"
                className={`text-sm font-medium tracking-wide transition-all hover:text-primary ${
                  isActive('/rewards') ? 'text-primary' : 'text-foreground/70'
                }`}
              >
                🎁 BELOHNUNGEN
              </Link>
            </div>

            {/* CENTER: Logo (Optimized) */}
            <Link 
              to="/" 
              className="flex items-center justify-center absolute left-1/2 transform -translate-x-1/2 md:relative md:left-auto md:transform-none group" 
              data-testid="header-logo"
              aria-label="ZOZO Burger - Zur Startseite"
            >
              <div className="relative">
                {/* Logo with subtle glow effect */}
                <img
                  src="https://customer-assets.emergentagent.com/job_custom-burger-maker/artifacts/crcay6aj_IMG_8154.jpeg"
                  alt="ZOZO Burger"
                  className="h-12 md:h-16 w-auto object-contain transition-all duration-300 group-hover:scale-105 drop-shadow-lg"
                  style={{ filter: 'drop-shadow(0 0 10px rgba(220, 38, 38, 0.2))' }}
                />
              </div>
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
                aria-label={mobileMenuOpen ? "Menü schließen" : "Menü öffnen"}
                aria-expanded={mobileMenuOpen}
                aria-controls="mobile-menu"
              >
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {/* Mobile Menu - Enhanced */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-border animate-slide-up-fade">
              <div className="flex flex-col space-y-1">
                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-3 px-4 text-base font-medium transition-all rounded-lg active:scale-95 ${
                    isActive('/') 
                      ? 'text-primary bg-primary/10' 
                      : 'text-foreground/80 hover:bg-accent active:bg-accent/80'
                  }`}
                >
                  🏠 Home
                </Link>
                <Link
                  to="/menu"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-3 px-4 text-base font-medium transition-all rounded-lg active:scale-95 ${
                    isActive('/menu') 
                      ? 'text-primary bg-primary/10' 
                      : 'text-foreground/80 hover:bg-accent active:bg-accent/80'
                  }`}
                >
                  📋 Speisekarte
                </Link>
                <Link
                  to="/locations"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-3 px-4 text-base font-medium transition-all rounded-lg active:scale-95 ${
                    isActive('/locations') 
                      ? 'text-primary bg-primary/10' 
                      : 'text-foreground/80 hover:bg-accent active:bg-accent/80'
                  }`}
                >
                  📍 Standorte
                </Link>
                <Link
                  to="/order-tracking"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-3 px-4 text-base font-medium transition-all rounded-lg active:scale-95 ${
                    isActive('/order-tracking') 
                      ? 'text-primary bg-primary/10' 
                      : 'text-foreground/80 hover:bg-accent active:bg-accent/80'
                  }`}
                >
                  📦 Bestellstatus
                </Link>
                <Link
                  to="/burger-builder"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-3 px-4 text-base font-medium transition-all rounded-lg active:scale-95 ${
                    isActive('/burger-builder') 
                      ? 'text-primary bg-primary/10' 
                      : 'text-foreground/80 hover:bg-accent active:bg-accent/80'
                  }`}
                >
                  🍔 Burger Builder
                </Link>
                <Link
                  to="/rewards"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-3 px-4 text-base font-medium transition-all rounded-lg active:scale-95 ${
                    isActive('/rewards') 
                      ? 'text-primary bg-primary/10' 
                      : 'text-foreground/80 hover:bg-accent active:bg-accent/80'
                  }`}
                >
                  🎁 Belohnungen
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

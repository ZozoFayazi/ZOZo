import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Menu, Award, ShoppingCart, User } from 'lucide-react';

function MobileBottomNav({ cartItemCount, onCartClick }) {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path;
  };

  // Hide on admin pages
  if (location.pathname.startsWith('/admin')) {
    return null;
  }

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-card/95 backdrop-blur-lg border-t border-border z-40 mobile-bottom-safe">
      <div className="grid grid-cols-5 h-16">
        {/* Home */}
        <Link
          to="/"
          className={`flex flex-col items-center justify-center space-y-1 transition-colors active:scale-95 ${
            isActive('/') ? 'text-primary' : 'text-muted-foreground'
          }`}
        >
          <Home className="h-5 w-5" />
          <span className="text-xs font-medium">Home</span>
        </Link>

        {/* Menu */}
        <Link
          to="/menu"
          className={`flex flex-col items-center justify-center space-y-1 transition-colors active:scale-95 ${
            isActive('/menu') ? 'text-primary' : 'text-muted-foreground'
          }`}
        >
          <Menu className="h-5 w-5" />
          <span className="text-xs font-medium">Menü</span>
        </Link>

        {/* Cart */}
        <button
          onClick={onCartClick}
          className="flex flex-col items-center justify-center space-y-1 text-muted-foreground transition-colors active:scale-95 relative"
        >
          <ShoppingCart className="h-5 w-5" />
          <span className="text-xs font-medium">Warenkorb</span>
          {cartItemCount > 0 && (
            <span className="absolute top-1 right-1/2 translate-x-3 -translate-y-1 h-5 w-5 bg-primary text-primary-foreground text-xs font-bold flex items-center justify-center rounded-full">
              {cartItemCount}
            </span>
          )}
        </button>

        {/* Rewards */}
        <Link
          to="/rewards"
          className={`flex flex-col items-center justify-center space-y-1 transition-colors active:scale-95 ${
            isActive('/rewards') ? 'text-primary' : 'text-muted-foreground'
          }`}
        >
          <Award className="h-5 w-5" />
          <span className="text-xs font-medium">Punkte</span>
        </Link>

        {/* Burger Builder */}
        <Link
          to="/burger-builder"
          className={`flex flex-col items-center justify-center space-y-1 transition-colors active:scale-95 ${
            isActive('/burger-builder') ? 'text-primary' : 'text-muted-foreground'
          }`}
        >
          <div className="text-xl">🍔</div>
          <span className="text-xs font-medium">Builder</span>
        </Link>
      </div>
    </nav>
  );
}

export default MobileBottomNav;

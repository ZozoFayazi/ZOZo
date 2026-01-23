import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { Button } from './ui/button';
import { Sheet, SheetContent, SheetTrigger } from './ui/sheet';
import { 
  LayoutDashboard, 
  MapPin, 
  UtensilsCrossed, 
  ShoppingCart, 
  Percent, 
  Settings, 
  LogOut,
  Menu,
  ChevronLeft,
  ChevronRight,
  Package,
  Cable,
  Shield,
  AlertTriangle,
  Tag,
  Mail,
  BarChart3,
  Users,
  Euro,
  Zap,
  Star
} from 'lucide-react';
import { cn } from '../lib/utils';

const AdminSidebar = () => {
  const location = useLocation();
  const { admin, logout, hasPermission } = useAdminAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const menuItems = [
    {
      title: 'Dashboard',
      icon: LayoutDashboard,
      path: '/admin/dashboard',
      permission: null // All admins
    },
    {
      title: 'Analytics',
      icon: BarChart3,
      path: '/admin/analytics',
      permission: null // All admins
    },
    {
      title: 'Kunden-CRM',
      icon: Users,
      path: '/admin/customers',
      permission: null // All admins
    },
    {
      title: 'Finanz-Management',
      icon: Euro,
      path: '/admin/finance',
      permission: null // All admins
    },
    {
      title: 'Filialen',
      icon: MapPin,
      path: '/admin/locations',
      permission: null // All admins can see their locations
    },
    {
      title: 'Menü',
      icon: UtensilsCrossed,
      path: '/admin/menu',
      permission: null // All admins (but different capabilities)
    },
    {
      title: 'Kategorien',
      icon: Tag,
      path: '/admin/categories',
      permission: 'manage_products' // Only Rellingen + Super Admin
    },
    {
      title: 'Bestellungen',
      icon: ShoppingCart,
      path: '/admin/orders',
      permission: null
    },
    {
      title: 'Bewertungen',
      icon: Star,
      path: '/admin/reviews',
      permission: null
    },
    {
      title: 'Angebote',
      icon: Package,
      path: '/admin/featured',
      permission: 'manage_products' // Only Rellingen + Super Admin
    },
    {
      title: 'Tagesangebote',
      icon: Tag,
      path: '/admin/daily-deals',
      permission: 'manage_products' // Only Rellingen + Super Admin
    },
    {
      title: 'Burger Builder',
      icon: ChefHat,
      path: '/admin/burger-builder',
      permission: 'manage_products'
    },
    {
      title: 'Rabattcodes',
      icon: Percent,
      path: '/admin/discount-codes',
      permission: 'manage_products' // Only Rellingen + Super Admin
    },
    {
      title: 'Newsletter & Marketing',
      icon: Mail,
      path: '/admin/newsletter',
      permission: 'manage_products' // Only Rellingen + Super Admin
    },
    {
      title: 'Email Automation',
      icon: Zap,
      path: '/admin/email-automation',
      permission: 'manage_products' // Only Rellingen + Super Admin
    },
    {
      title: 'POS-System',
      icon: Cable,
      path: '/admin/pos',
      permission: null // All admins can see their POS settings
    },
    {
      title: 'POS Fehler-Queue',
      icon: AlertTriangle,
      path: '/admin/pos/failed-orders',
      permission: null, // All admins can see failed orders from their locations
      badge: true // Will show count badge if there are failed orders
    },
    {
      title: 'Features',
      icon: Settings,
      path: '/admin/features',
      permission: '*' // Super Admin only - Feature Toggle Management
    },
    {
      title: 'Sicherheit',
      icon: Shield,
      path: '/admin/security',
      permission: '*' // Super Admin only
    },
    {
      title: 'Einstellungen',
      icon: Settings,
      path: '/admin/settings',
      permission: 'manage_branch_rellingen' // Only Rellingen + Super Admin
    }
  ];

  // Filter menu items based on permissions
  const visibleMenuItems = menuItems.filter(item => {
    if (!item.permission) return true;
    return hasPermission(item.permission);
  });

  const SidebarContent = ({ mobile = false }) => (
    <div className="flex flex-col h-full bg-card border-r border-border">
      {/* Logo/Header */}
      <div className={cn(
        "flex items-center justify-between p-4 border-b border-border",
        collapsed && !mobile && "justify-center"
      )}>
        {(!collapsed || mobile) && (
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">ZB</span>
            </div>
            <div>
              <h2 className="font-bold text-sm text-foreground">ZOZO Admin</h2>
              <p className="text-xs text-muted-foreground">{admin?.role?.replace('_', ' ')}</p>
            </div>
          </div>
        )}
        {!mobile && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="h-8 w-8"
            data-testid="sidebar-collapse-button"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        )}
      </div>

      {/* Admin Info */}
      {(!collapsed || mobile) && (
        <div className="p-4 border-b border-border bg-muted/30">
          <p className="text-sm font-medium text-foreground">{admin?.name}</p>
          <p className="text-xs text-muted-foreground truncate">{admin?.email}</p>
        </div>
      )}

      {/* Navigation Menu */}
      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        {visibleMenuItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => mobile && setMobileOpen(false)}
              data-testid={`sidebar-menu-${item.path.split('/').pop()}`}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors",
                "hover:bg-accent hover:text-accent-foreground",
                isActive && "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground",
                !isActive && "text-muted-foreground",
                collapsed && !mobile && "justify-center px-2"
              )}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {(!collapsed || mobile) && (
                <span className="text-sm font-medium">{item.title}</span>
              )}
              {isActive && (!collapsed || mobile) && (
                <div className="ml-auto h-1.5 w-1.5 rounded-full bg-primary-foreground" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Logout Button */}
      <div className="p-2 border-t border-border">
        <Button
          variant="ghost"
          onClick={logout}
          data-testid="sidebar-logout-button"
          className={cn(
            "w-full justify-start text-muted-foreground hover:text-foreground",
            collapsed && !mobile && "justify-center px-2"
          )}
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          {(!collapsed || mobile) && (
            <span className="ml-3">Abmelden</span>
          )}
        </Button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside 
        className={cn(
          "hidden lg:flex flex-col fixed left-0 top-0 h-screen bg-card transition-all duration-300 z-40",
          collapsed ? "w-16" : "w-64"
        )}
        data-testid="admin-sidebar-desktop"
      >
        <SidebarContent />
      </aside>

      {/* Mobile Hamburger + Drawer */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-card border-b border-border">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">ZB</span>
            </div>
            <div>
              <h2 className="font-bold text-sm text-foreground">ZOZO Admin</h2>
            </div>
          </div>
          
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button 
                variant="ghost" 
                size="icon"
                data-testid="mobile-menu-button"
              >
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-64">
              <SidebarContent mobile />
            </SheetContent>
          </Sheet>
        </div>
      </div>

      {/* Spacer for mobile */}
      <div className="lg:hidden h-16" />
    </>
  );
};

export default AdminSidebar;

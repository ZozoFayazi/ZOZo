import React from 'react';
import AdminSidebar from './AdminSidebar';
import { cn } from '../lib/utils';

const AdminLayout = ({ children, className }) => {
  return (
    <div className="min-h-screen bg-background">
      <AdminSidebar />
      
      {/* Main Content Area */}
      <main className={cn(
        "lg:ml-64 transition-all duration-300",
        className
      )}>
        {children}
      </main>
    </div>
  );
};

export default AdminLayout;

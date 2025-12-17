import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { Loader2 } from 'lucide-react';

export const ProtectedAdminRoute = ({ children, requiredPermission, requiredBranch }) => {
  const { admin, loading, hasPermission, canAccessBranch } = useAdminAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!admin) {
    return <Navigate to="/admin/login" replace />;
  }

  // Check permission if required
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground mb-2">Zugriff verweigert</h1>
          <p className="text-muted-foreground">
            Sie haben keine Berechtigung für diese Aktion.
          </p>
        </div>
      </div>
    );
  }

  // Check branch access if required
  if (requiredBranch && !canAccessBranch(requiredBranch)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground mb-2">Zugriff verweigert</h1>
          <p className="text-muted-foreground">
            Sie haben keinen Zugriff auf diese Filiale.
          </p>
        </div>
      </div>
    );
  }

  return children;
};

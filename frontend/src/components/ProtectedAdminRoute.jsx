import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { Loader2, Lock, Shield, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import PasswordChangeDialog from './PasswordChangeDialog';
import TwoFactorSetup from './TwoFactorSetup';

export const ProtectedAdminRoute = ({ children, requiredPermission, requiredBranch }) => {
  const { admin, loading, hasPermission, canAccessBranch, mustChangePassword, isSuperAdmin, updateAdminData } = useAdminAuth();
  
  // State for forced dialogs
  const [passwordChangeComplete, setPasswordChangeComplete] = useState(false);
  const [twoFASetupComplete, setTwoFASetupComplete] = useState(false);

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

  // SECURITY CHECK 1: Must Change Password
  // This blocks access until password is changed
  const requiresPasswordChange = mustChangePassword() && !passwordChangeComplete;
  
  if (requiresPasswordChange) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md border-destructive/50" data-testid="forced-password-change-screen">
          <CardHeader className="text-center">
            <div className="mx-auto h-14 w-14 rounded-full bg-destructive/10 flex items-center justify-center mb-4">
              <AlertTriangle className="h-7 w-7 text-destructive" />
            </div>
            <CardTitle className="text-xl">Passwortänderung erforderlich</CardTitle>
            <CardDescription>
              Aus Sicherheitsgründen müssen Sie Ihr Standard-Passwort ändern, bevor Sie fortfahren können.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <PasswordChangeDialog
              open={true}
              onOpenChange={() => {}}
              forced={true}
            />
          </CardContent>
        </Card>
      </div>
    );
  }

  // SECURITY CHECK 2: Super Admin 2FA Setup Required
  // This blocks Super Admins who haven't set up 2FA
  const requiresTwoFASetup = isSuperAdmin() && 
    (admin.require_2fa_setup === true || admin.totp_enabled === false) && 
    !twoFASetupComplete;
  
  if (requiresTwoFASetup) {
    const handleTwoFASuccess = () => {
      setTwoFASetupComplete(true);
      // Update admin data to reflect 2FA is now enabled
      if (updateAdminData) {
        updateAdminData({ totp_enabled: true, require_2fa_setup: false });
      }
    };

    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-lg border-primary/50" data-testid="forced-2fa-setup-screen">
          <CardHeader className="text-center">
            <div className="mx-auto h-14 w-14 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <Shield className="h-7 w-7 text-primary" />
            </div>
            <CardTitle className="text-xl">2FA-Einrichtung erforderlich</CardTitle>
            <CardDescription>
              Als Super Admin müssen Sie die Zwei-Faktor-Authentifizierung aktivieren, um fortzufahren. 
              Dies schützt Ihr Konto vor unbefugtem Zugriff.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <TwoFactorSetup
              open={true}
              onOpenChange={() => {}}
              onSuccess={handleTwoFASuccess}
              forced={true}
            />
          </CardContent>
        </Card>
      </div>
    );
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

import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { Loader2 } from 'lucide-react';
import PasswordChangeDialog from './PasswordChangeDialog';
import TwoFactorSetup from './TwoFactorSetup';

export const ProtectedAdminRoute = ({ children, requiredPermission, requiredBranch }) => {
  const { admin, loading, hasPermission, canAccessBranch, mustChangePassword, isSuperAdmin, updateAdminData } = useAdminAuth();
  
  // State for forced dialogs - these track if user has completed the required action in this session
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
  // This blocks access until password is changed - the dialog itself handles the logout
  const requiresPasswordChange = mustChangePassword() && !passwordChangeComplete;
  
  if (requiresPasswordChange) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4" data-testid="forced-password-change-screen">
        <PasswordChangeDialog
          open={true}
          onOpenChange={() => {}} // Cannot be closed
          forced={true}
        />
      </div>
    );
  }

  // SECURITY CHECK 2: Super Admin 2FA Setup Required
  // This blocks Super Admins who haven't set up 2FA
  // Note: Only enforce if require_2fa_setup is explicitly true from backend
  const requiresTwoFASetup = isSuperAdmin() && 
    admin.require_2fa_setup === true && 
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
      <div className="min-h-screen flex items-center justify-center bg-background p-4" data-testid="forced-2fa-setup-screen">
        <TwoFactorSetup
          open={true}
          onOpenChange={() => {}} // Cannot be closed until complete
          onSuccess={handleTwoFASuccess}
          forced={true}
        />
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

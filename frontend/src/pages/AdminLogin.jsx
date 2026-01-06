import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { toast } from 'sonner';
import { Lock, Mail, Loader2 } from 'lucide-react';
import TwoFactorVerify from '../components/TwoFactorVerify';
import { PasskeyVerifyDialog } from '../components/PasskeyVerifyDialog';
import { PasskeySetupDialog } from '../components/PasskeySetupDialog';

export default function AdminLogin() {
  const navigate = useNavigate();
  const { login } = useAdminAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  // 2FA state (legacy TOTP)
  const [require2FA, setRequire2FA] = useState(false);
  const [tempToken, setTempToken] = useState(null);
  
  // Passkey state
  const [requirePasskey, setRequirePasskey] = useState(false);
  const [requirePasskeySetup, setRequirePasskeySetup] = useState(false);
  const [loginEmail, setLoginEmail] = useState('');

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('Bitte alle Felder ausfüllen');
      return;
    }

    setLoading(true);
    setLoginEmail(email);
    
    try {
      const result = await login(email, password);
      
      // Check if Passkey is required
      if (result.require_passkey || result.admin?.passkey_enabled) {
        setRequirePasskey(true);
        setLoading(false);
        return;
      }
      
      // Check if Passkey setup is required (Super Admin)
      if (result.require_passkey_setup || result.admin?.require_passkey_setup) {
        setRequirePasskeySetup(true);
        setLoading(false);
        return;
      }
      
      // Check if 2FA is required (legacy TOTP - fallback)
      if (result.require_2fa) {
        setTempToken(result.temp_token);
        setRequire2FA(true);
        setLoading(false);
        return;
      }
      
      console.log('Login successful:', result);
      toast.success('Login erfolgreich!');
      
      // Navigate to dashboard
      setTimeout(() => {
        navigate('/admin/dashboard', { replace: true });
      }, 150);
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.message || 'Login fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  };

  // Handle successful 2FA verification
  const handle2FASuccess = async (data) => {
    // Store token and admin data
    sessionStorage.setItem('adminToken', data.access_token);
    sessionStorage.setItem('admin', JSON.stringify(data.admin));
    
    toast.success('Login erfolgreich!');
    
    // Force page reload to update auth context
    window.location.href = '/admin/dashboard';
  };

  // Cancel 2FA and go back to login
  const handle2FACancel = () => {
    setRequire2FA(false);
    setTempToken(null);
    setPassword('');
  };

  // Show 2FA verification screen
  if (require2FA && tempToken) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <TwoFactorVerify
          tempToken={tempToken}
          onSuccess={handle2FASuccess}
          onCancel={handle2FACancel}
          backendUrl={backendUrl}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md border-border" data-testid="admin-login-card">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center mb-4">
            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Lock className="h-6 w-6 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center">
            Admin Login
          </CardTitle>
          <CardDescription className="text-center">
            ZOZO Burger Verwaltung
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-muted-foreground">
                E-Mail
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="admin@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10"
                  disabled={loading}
                  data-testid="admin-login-email"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-muted-foreground">
                Passwort
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10"
                  disabled={loading}
                  data-testid="admin-login-password"
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
              data-testid="admin-login-submit"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Anmelden...
                </>
              ) : (
                'Anmelden'
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-muted-foreground">
              Standard-Passwort: ZozoAdmin2024!
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Bitte nach dem ersten Login ändern
            </p>
          </div>
        </CardContent>
      </Card>
      
      {/* Passkey Verification Dialog */}
      <PasskeyVerifyDialog
        open={requirePasskey}
        email={loginEmail}
        onSuccess={(result) => {
          // Store token and admin data
          localStorage.setItem('adminToken', result.access_token);
          toast.success('Passkey-Authentifizierung erfolgreich!');
          navigate('/admin/dashboard', { replace: true });
        }}
        onBackupCode={() => {
          // Backup code flow handled in PasskeyVerifyDialog
        }}
      />
      
      {/* Passkey Setup Dialog (forced for Super Admin) */}
      <PasskeySetupDialog
        open={requirePasskeySetup}
        onOpenChange={() => {}} // Not closable when required
        onSuccess={() => {
          toast.success('Passkey erfolgreich eingerichtet! Sie können sich jetzt anmelden.');
          setRequirePasskeySetup(false);
          setEmail('');
          setPassword('');
        }}
      />
      
      {/* Legacy 2FA Dialog (TOTP - fallback) */}
      {require2FA && (
        <TwoFactorVerify
          tempToken={tempToken}
          onSuccess={(token) => {
            localStorage.setItem('adminToken', token);
            toast.success('2FA-Verifizierung erfolgreich!');
            navigate('/admin/dashboard', { replace: true });
          }}
          onCancel={() => {
            setRequire2FA(false);
            setTempToken(null);
            setLoading(false);
          }}
        />
      )}
    </div>
  );
}

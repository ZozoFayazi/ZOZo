import React, { useState } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import { Lock, Eye, EyeOff, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';

export const PasswordChangeDialog = ({ open, onOpenChange, forced = false }) => {
  const { token, admin, logout } = useAdminAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Password requirements
  const requirements = [
    { test: (p) => p.length >= 8, label: 'Mindestens 8 Zeichen' },
    { test: (p) => /[A-Z]/.test(p), label: 'Ein Großbuchstabe' },
    { test: (p) => /[a-z]/.test(p), label: 'Ein Kleinbuchstabe' },
    { test: (p) => /[0-9]/.test(p), label: 'Eine Zahl' },
    { test: (p) => /[!@#$%^&*]/.test(p), label: 'Ein Sonderzeichen (!@#$%^&*)' },
  ];

  const allRequirementsMet = requirements.every(req => req.test(newPassword));
  const passwordsMatch = newPassword === confirmPassword && newPassword.length > 0;
  const canSubmit = currentPassword && allRequirementsMet && passwordsMatch;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!canSubmit) {
      setError('Bitte erfüllen Sie alle Anforderungen');
      return;
    }
    
    setSaving(true);
    
    try {
      const response = await fetch(`${backendUrl}/api/admin/security/change-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Fehler beim Ändern des Passworts');
      }

      toast.success('Passwort erfolgreich geändert!');
      
      // Reset form
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      
      // Always logout after password change (JWT rotation makes old token invalid)
      toast.info('Passwort geändert. Bitte melden Sie sich mit Ihrem neuen Passwort an.', {
        duration: 5000
      });
      
      // Wait 1 second then logout
      setTimeout(() => {
        logout();
      }, 1000);
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={forced ? undefined : onOpenChange}>
      <DialogContent 
        className={`sm:max-w-[450px] ${forced ? '[&>button]:hidden' : ''}`}
        data-testid="password-change-dialog"
        onPointerDownOutside={forced ? (e) => e.preventDefault() : undefined}
        onEscapeKeyDown={forced ? (e) => e.preventDefault() : undefined}
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-primary" />
            {forced ? 'Passwort ändern (erforderlich)' : 'Passwort ändern'}
          </DialogTitle>
          <DialogDescription>
            {forced 
              ? 'Aus Sicherheitsgründen müssen Sie Ihr Passwort ändern, bevor Sie fortfahren können.'
              : 'Ändern Sie Ihr Passwort regelmäßig für mehr Sicherheit.'
            }
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Current Password */}
          <div className="space-y-2">
            <Label htmlFor="current-password">Aktuelles Passwort</Label>
            <div className="relative">
              <Input
                id="current-password"
                type={showCurrentPassword ? 'text' : 'password'}
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Aktuelles Passwort eingeben"
                data-testid="current-password-input"
                required
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0"
                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
              >
                {showCurrentPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          {/* New Password */}
          <div className="space-y-2">
            <Label htmlFor="new-password">Neues Passwort</Label>
            <div className="relative">
              <Input
                id="new-password"
                type={showNewPassword ? 'text' : 'password'}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Neues Passwort eingeben"
                data-testid="new-password-input"
                required
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0"
                onClick={() => setShowNewPassword(!showNewPassword)}
              >
                {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>

            {/* Password Requirements */}
            <div className="space-y-1 mt-2">
              {requirements.map((req, idx) => (
                <div 
                  key={idx}
                  className={`flex items-center gap-2 text-xs ${
                    req.test(newPassword) ? 'text-[hsl(var(--success))]' : 'text-muted-foreground'
                  }`}
                >
                  <CheckCircle2 className={`h-3 w-3 ${req.test(newPassword) ? 'opacity-100' : 'opacity-30'}`} />
                  {req.label}
                </div>
              ))}
            </div>
          </div>

          {/* Confirm Password */}
          <div className="space-y-2">
            <Label htmlFor="confirm-password">Passwort bestätigen</Label>
            <Input
              id="confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Neues Passwort wiederholen"
              data-testid="confirm-password-input"
              required
            />
            {confirmPassword && (
              <p className={`text-xs ${passwordsMatch ? 'text-[hsl(var(--success))]' : 'text-[hsl(var(--destructive))]'}`}>
                {passwordsMatch ? '✓ Passwörter stimmen überein' : '✗ Passwörter stimmen nicht überein'}
              </p>
            )}
          </div>

          <DialogFooter className="pt-4">
            {!forced && (
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Abbrechen
              </Button>
            )}
            <Button type="submit" disabled={!canSubmit || saving} data-testid="save-password-button">
              {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
              Passwort ändern
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default PasswordChangeDialog;

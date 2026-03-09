import React, { useState, useEffect } from 'react';
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
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';
import { toast } from 'sonner';
import { 
  Shield, 
  Smartphone, 
  Key, 
  Copy, 
  CheckCircle2, 
  AlertTriangle,
  Loader2,
  QrCode
} from 'lucide-react';

export const TwoFactorSetup = ({ open, onOpenChange, onSuccess, forced = false }) => {
  const { token, admin, updateAdminData } = useAdminAuth();
  const [step, setStep] = useState(1); // 1: Intro, 2: QR Code, 3: Verify, 4: Backup Codes
  const [loading, setLoading] = useState(false);
  const [setupData, setSetupData] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState('');
  const [copiedManualKey, setCopiedManualKey] = useState(false);
  const [copiedBackupCodes, setCopiedBackupCodes] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Start 2FA setup
  const startSetup = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${backendUrl}/api/admin/auth/2fa/setup`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Setup fehlgeschlagen');
      }

      const data = await response.json();
      setSetupData(data);
      setStep(2);
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Confirm setup with verification code
  const confirmSetup = async () => {
    if (verificationCode.length !== 6) {
      setError('Bitte geben Sie einen 6-stelligen Code ein');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${backendUrl}/api/admin/auth/2fa/confirm`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: verificationCode })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Verifizierung fehlgeschlagen');
      }

      toast.success('2FA erfolgreich aktiviert!');
      setStep(4); // Show backup codes
      
      // Update admin data
      if (updateAdminData) {
        updateAdminData({ totp_enabled: true, require_2fa_setup: false });
      }
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Complete setup
  const completeSetup = () => {
    onOpenChange(false);
    if (onSuccess) onSuccess();
  };

  // Copy to clipboard
  const copyToClipboard = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'manual') {
        setCopiedManualKey(true);
        setTimeout(() => setCopiedManualKey(false), 2000);
      } else {
        setCopiedBackupCodes(true);
        setTimeout(() => setCopiedBackupCodes(false), 2000);
      }
      toast.success('Kopiert!');
    } catch (err) {
      toast.error('Kopieren fehlgeschlagen');
    }
  };

  // Reset on close
  useEffect(() => {
    if (!open) {
      setStep(1);
      setSetupData(null);
      setVerificationCode('');
      setError('');
    }
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={forced && step < 4 ? undefined : onOpenChange}>
      <DialogContent 
        className={`sm:max-w-[500px] ${forced && step < 4 ? '[&>button]:hidden' : ''}`}
        data-testid="2fa-setup-dialog"
        onPointerDownOutside={forced && step < 4 ? (e) => e.preventDefault() : undefined}
        onEscapeKeyDown={forced && step < 4 ? (e) => e.preventDefault() : undefined}
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            {step === 1 && 'Zwei-Faktor-Authentifizierung einrichten'}
            {step === 2 && 'QR-Code scannen'}
            {step === 3 && 'Code verifizieren'}
            {step === 4 && 'Backup-Codes speichern'}
          </DialogTitle>
          <DialogDescription>
            {step === 1 && 'Erhöhen Sie die Sicherheit Ihres Kontos mit 2FA.'}
            {step === 2 && 'Scannen Sie den Code mit Ihrer Authenticator-App.'}
            {step === 3 && 'Geben Sie den 6-stelligen Code aus Ihrer App ein.'}
            {step === 4 && 'Speichern Sie diese Codes sicher für den Notfall.'}
          </DialogDescription>
        </DialogHeader>

        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Step 1: Intro */}
        {step === 1 && (
          <div className="space-y-4 py-4">
            <div className="grid gap-4">
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Smartphone className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">Authenticator-App benötigt</p>
                      <p className="text-sm text-muted-foreground">
                        Installieren Sie Google Authenticator, Microsoft Authenticator oder Authy.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Key className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">Backup-Codes erhalten</p>
                      <p className="text-sm text-muted-foreground">
                        Sie erhalten 10 Backup-Codes für den Notfall.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {forced && (
              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription>
                  Als Super Admin ist 2FA für Ihr Konto erforderlich.
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}

        {/* Step 2: QR Code */}
        {step === 2 && setupData && (
          <div className="space-y-4 py-4">
            <div className="flex justify-center">
              <div className="p-4 bg-white rounded-xl">
                <img 
                  src={setupData.qr_code} 
                  alt="QR Code für 2FA" 
                  className="w-48 h-48"
                  data-testid="2fa-qr-code"
                />
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label className="text-muted-foreground text-xs">Manuelle Eingabe</Label>
              <div className="flex items-center gap-2">
                <Input 
                  value={setupData.manual_entry_key} 
                  readOnly 
                  className="font-mono text-sm"
                  data-testid="2fa-manual-key"
                />
                <Button 
                  variant="outline" 
                  size="icon"
                  onClick={() => copyToClipboard(setupData.manual_entry_key, 'manual')}
                >
                  {copiedManualKey ? <CheckCircle2 className="h-4 w-4 text-[hsl(var(--success))]" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Falls der QR-Code nicht funktioniert, geben Sie diesen Schlüssel manuell ein.
              </p>
            </div>
          </div>
        )}

        {/* Step 3: Verify */}
        {step === 3 && (
          <div className="space-y-4 py-4">
            <div className="text-center mb-4">
              <QrCode className="h-12 w-12 mx-auto mb-2 text-primary" />
              <p className="text-sm text-muted-foreground">
                Öffnen Sie Ihre Authenticator-App und geben Sie den angezeigten Code ein.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="verification-code">6-stelliger Code</Label>
              <Input
                id="verification-code"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                className="text-center text-2xl tracking-widest font-mono"
                maxLength={6}
                data-testid="2fa-verification-input"
              />
            </div>
          </div>
        )}

        {/* Step 4: Backup Codes */}
        {step === 4 && setupData && (
          <div className="space-y-4 py-4">
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <strong>Wichtig!</strong> Speichern Sie diese Codes sicher. Sie werden nur einmal angezeigt!
              </AlertDescription>
            </Alert>

            <div className="p-4 bg-muted rounded-lg">
              <div className="grid grid-cols-2 gap-2">
                {setupData.backup_codes.map((code, idx) => (
                  <div key={idx} className="font-mono text-sm bg-background p-2 rounded text-center">
                    {code}
                  </div>
                ))}
              </div>
            </div>

            <Button
              variant="outline"
              className="w-full"
              onClick={() => copyToClipboard(setupData.backup_codes.join('\n'), 'backup')}
            >
              {copiedBackupCodes ? (
                <><CheckCircle2 className="h-4 w-4 mr-2 text-[hsl(var(--success))]" /> Kopiert!</>
              ) : (
                <><Copy className="h-4 w-4 mr-2" /> Alle Codes kopieren</>
              )}
            </Button>

            <p className="text-xs text-muted-foreground text-center">
              Jeder Code kann nur einmal verwendet werden. Bewahren Sie sie sicher auf!
            </p>
          </div>
        )}

        <DialogFooter>
          {step === 1 && (
            <>
              {!forced && (
                <Button variant="outline" onClick={() => onOpenChange(false)}>
                  Abbrechen
                </Button>
              )}
              <Button onClick={startSetup} disabled={loading} data-testid="2fa-start-setup">
                {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                Einrichtung starten
              </Button>
            </>
          )}

          {step === 2 && (
            <>
              <Button variant="outline" onClick={() => setStep(1)}>
                Zurück
              </Button>
              <Button onClick={() => setStep(3)} data-testid="2fa-next-to-verify">
                Weiter zur Verifizierung
              </Button>
            </>
          )}

          {step === 3 && (
            <>
              <Button variant="outline" onClick={() => setStep(2)}>
                Zurück
              </Button>
              <Button 
                onClick={confirmSetup} 
                disabled={loading || verificationCode.length !== 6}
                data-testid="2fa-confirm-setup"
              >
                {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                Bestätigen
              </Button>
            </>
          )}

          {step === 4 && (
            <Button onClick={completeSetup} className="w-full" data-testid="2fa-complete-setup">
              <CheckCircle2 className="h-4 w-4 mr-2" />
              Ich habe die Codes gespeichert
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default TwoFactorSetup;

import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import { Fingerprint, Shield, Download, Copy, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';

/**
 * WebAuthn/Passkey Setup Dialog
 * 
 * Flow:
 * 1. User clicks "Passkey einrichten"
 * 2. Backend generates registration options
 * 3. Browser shows Fingerprint/FaceID prompt
 * 4. Backend verifies and returns backup codes
 * 5. User MUST save backup codes
 */
export function PasskeySetupDialog({ open, onOpenChange, onSuccess }) {
  const [step, setStep] = useState(1); // 1=intro, 2=registering, 3=backup_codes
  const [registering, setRegistering] = useState(false);
  const [backupCodes, setBackupCodes] = useState([]);
  const [deviceName, setDeviceName] = useState('');
  const [error, setError] = useState('');
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  const token = sessionStorage.getItem('adminToken') || localStorage.getItem('adminToken');

  const startRegistration = async () => {
    // This function MUST be called from a button click (user gesture required for iOS Safari)
    setRegistering(true);
    setError('');
    
    try {
      // Step 1: Get registration options from backend
      const optionsResponse = await fetch(
        `${backendUrl}/api/admin/auth/passkey/register-options`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (!optionsResponse.ok) {
        throw new Error('Fehler beim Abrufen der Registrierungsoptionen');
      }
      
      const options = await optionsResponse.json();
      
      // Helper: Decode base64url to Uint8Array
      const base64urlToUint8Array = (base64url) => {
        if (!base64url) return new Uint8Array();
        
        const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
        const padding = '='.repeat((4 - base64.length % 4) % 4);
        const padded = base64 + padding;
        
        try {
          const binary = atob(padded);
          return Uint8Array.from(binary, c => c.charCodeAt(0));
        } catch (e) {
          const binary = atob(base64);
          return Uint8Array.from(binary, c => c.charCodeAt(0));
        }
      };
      
      // Convert base64 strings to Uint8Array
      options.challenge = base64urlToUint8Array(options.challenge);
      options.user.id = base64urlToUint8Array(options.user.id);
      
      // Step 2: Create credential via WebAuthn API
      // IMPORTANT: This MUST be called in response to user gesture for iOS Safari
      setStep(2);
      
      const credential = await navigator.credentials.create({ publicKey: options });
      
      if (!credential) {
        throw new Error('Passkey-Erstellung abgebrochen');
      }
      
      // Step 3: Send credential to backend for verification
      const credentialJSON = {
        id: credential.id,
        rawId: btoa(String.fromCharCode(...new Uint8Array(credential.rawId))),
        type: credential.type,
        response: {
          clientDataJSON: btoa(String.fromCharCode(...new Uint8Array(credential.response.clientDataJSON))),
          attestationObject: btoa(String.fromCharCode(...new Uint8Array(credential.response.attestationObject))),
          transports: credential.response.getTransports ? credential.response.getTransports() : []
        }
      };
      
      const verifyResponse = await fetch(
        `${backendUrl}/api/admin/auth/passkey/register-verify`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            credential: credentialJSON,
            device_name: deviceName || navigator.userAgent.substring(0, 50)
          })
        }
      );
      
      if (!verifyResponse.ok) {
        const data = await verifyResponse.json();
        throw new Error(data.detail || 'Verifizierung fehlgeschlagen');
      }
      
      const result = await verifyResponse.json();
      
      // Step 4: Show backup codes
      setBackupCodes(result.backup_codes);
      setStep(3);
      
      toast.success('Passkey erfolgreich eingerichtet!');
      
    } catch (error) {
      console.error('Passkey registration error:', error);
      setError(error.message || 'Fehler bei der Passkey-Registrierung');
      setStep(1);
    } finally {
      setRegistering(false);
    }
  };

  const downloadBackupCodes = () => {
    const text = backupCodes.join('\n');
    const blob = new Blob([`ZOZO Burger Backup Codes\nGespeichert: ${new Date().toLocaleString('de-DE')}\n\n${text}\n\nBewahren Sie diese Codes sicher auf!`], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'zozo-burger-backup-codes.txt';
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Backup Codes heruntergeladen');
  };

  const copyBackupCodes = () => {
    navigator.clipboard.writeText(backupCodes.join('\n'));
    toast.success('Backup Codes kopiert');
  };

  const confirmBackupCodesSaved = () => {
    onSuccess?.();
    onOpenChange(false);
    setStep(1);
    setBackupCodes([]);
  };

  return (
    <Dialog open={open} onOpenChange={step === 3 ? undefined : onOpenChange}>
      <DialogContent className={`sm:max-w-[500px] ${step === 3 ? '[&>button]:hidden' : ''}`}>
        {/* Step 1: Intro */}
        {step === 1 && (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-2xl">
                <Fingerprint className="h-6 w-6 text-primary" />
                Passkey einrichten
              </DialogTitle>
              <DialogDescription>
                Richten Sie einen Passkey (Fingerabdruck, FaceID, Windows Hello) als sichere Zwei-Faktor-Authentifizierung ein.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 my-4">
              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription>
                  <strong>Sicherer als TOTP:</strong> Passkeys sind phishing-resistent und funktionieren mit Ihrem Fingerabdruck oder Gesichtserkennung.
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label htmlFor="device-name">Geräte-Name (optional)</Label>
                <Input
                  id="device-name"
                  placeholder="z.B. iPhone 14, MacBook Pro"
                  value={deviceName}
                  onChange={(e) => setDeviceName(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Hilft Ihnen, Ihre Passkeys später zu identifizieren
                </p>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Abbrechen
              </Button>
              <Button onClick={startRegistration} disabled={registering}>
                {registering ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Wird eingerichtet...
                  </>
                ) : (
                  <>
                    <Fingerprint className="h-4 w-4 mr-2" />
                    Passkey einrichten
                  </>
                )}
              </Button>
            </DialogFooter>
          </>
        )}

        {/* Step 2: Registering (Browser Prompt) */}
        {step === 2 && (
          <>
            <DialogHeader>
              <DialogTitle>Passkey wird registriert...</DialogTitle>
              <DialogDescription>
                Folgen Sie den Anweisungen Ihres Browsers
              </DialogDescription>
            </DialogHeader>

            <div className="text-center py-8">
              <Fingerprint className="h-16 w-16 text-primary mx-auto animate-pulse mb-4" />
              <p className="text-muted-foreground">
                Verwenden Sie Ihren Fingerabdruck, FaceID oder PIN
              </p>
            </div>
          </>
        )}

        {/* Step 3: Backup Codes */}
        {step === 3 && (
          <>
            <DialogHeader>
              <DialogTitle className="text-2xl text-primary">
                ⚠️ Backup Codes sichern (Pflicht!)
              </DialogTitle>
              <DialogDescription>
                Diese Codes ermöglichen den Zugriff, falls Ihr Gerät nicht verfügbar ist. 
                Jeder Code kann nur EINMAL verwendet werden.
              </DialogDescription>
            </DialogHeader>

            <div className="my-4 space-y-4">
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Speichern Sie diese Codes JETZT!</strong> Sie werden nur einmal angezeigt.
                </AlertDescription>
              </Alert>

              <div className="bg-secondary/50 border-2 border-primary rounded-lg p-4">
                <div className="grid grid-cols-2 gap-2 font-mono text-sm">
                  {backupCodes.map((code, i) => (
                    <div key={i} className="bg-background px-3 py-2 rounded border border-border">
                      {i + 1}. {code}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <Button onClick={downloadBackupCodes} variant="outline" className="flex-1">
                  <Download className="h-4 w-4 mr-2" />
                  Herunterladen
                </Button>
                <Button onClick={copyBackupCodes} variant="outline" className="flex-1">
                  <Copy className="h-4 w-4 mr-2" />
                  Kopieren
                </Button>
              </div>
            </div>

            <DialogFooter>
              <Button onClick={confirmBackupCodesSaved} className="w-full bg-primary">
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Ich habe die Backup Codes gespeichert
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

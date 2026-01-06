import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import { Fingerprint, Key, Loader2, AlertTriangle } from 'lucide-react';

/**
 * Passkey Verification Dialog
 * 
 * Shown after successful password login when passkey is required
 */
export function PasskeyVerifyDialog({ open, email, onSuccess, onBackupCode }) {
  const [verifying, setVerifying] = useState(false);
  const [showBackupCode, setShowBackupCode] = useState(false);
  const [backupCode, setBackupCode] = useState('');
  const [error, setError] = useState('');
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Auto-trigger passkey prompt when dialog opens
  useEffect(() => {
    if (open && !showBackupCode) {
      startPasskeyAuth();
    }
  }, [open]);

  const startPasskeyAuth = async () => {
    setVerifying(true);
    setError('');
    
    try {
      // Step 1: Get authentication options
      const optionsResponse = await fetch(
        `${backendUrl}/api/admin/auth/passkey/login-options?email=${encodeURIComponent(email)}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (!optionsResponse.ok) {
        throw new Error('Fehler beim Abrufen der Login-Optionen');
      }
      
      const options = await optionsResponse.json();
      
      // Convert base64 strings
      options.challenge = Uint8Array.from(atob(options.challenge), c => c.charCodeAt(0));
      
      if (options.allowCredentials) {
        options.allowCredentials = options.allowCredentials.map(cred => ({
          ...cred,
          id: Uint8Array.from(atob(cred.id), c => c.charCodeAt(0))
        }));
      }
      
      // Step 2: Get credential via WebAuthn API
      const credential = await navigator.credentials.get({ publicKey: options });
      
      if (!credential) {
        throw new Error('Passkey-Authentifizierung abgebrochen');
      }
      
      // Step 3: Send credential to backend for verification
      const credentialJSON = {
        id: credential.id,
        rawId: btoa(String.fromCharCode(...new Uint8Array(credential.rawId))),
        type: credential.type,
        response: {
          clientDataJSON: btoa(String.fromCharCode(...new Uint8Array(credential.response.clientDataJSON))),
          authenticatorData: btoa(String.fromCharCode(...new Uint8Array(credential.response.authenticatorData))),
          signature: btoa(String.fromCharCode(...new Uint8Array(credential.response.signature))),
          userHandle: credential.response.userHandle 
            ? btoa(String.fromCharCode(...new Uint8Array(credential.response.userHandle)))
            : null
        }
      };
      
      const verifyResponse = await fetch(
        `${backendUrl}/api/admin/auth/passkey/login-verify?email=${encodeURIComponent(email)}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            credential: credentialJSON
          })
        }
      );
      
      if (!verifyResponse.ok) {
        const data = await verifyResponse.json();
        throw new Error(data.detail || 'Verifizierung fehlgeschlagen');
      }
      
      const result = await verifyResponse.json();
      
      // Success - call parent with token
      toast.success('Passkey-Authentifizierung erfolgreich!');
      onSuccess(result);
      
    } catch (error) {
      console.error('Passkey auth error:', error);
      
      if (error.name === 'NotAllowedError') {
        setError('Passkey-Authentifizierung abgebrochen. Verwenden Sie einen Backup Code oder versuchen Sie es erneut.');
      } else {
        setError(error.message || 'Fehler bei der Passkey-Authentifizierung');
      }
    } finally {
      setVerifying(false);
    }
  };

  const handleBackupCodeSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!backupCode || backupCode.length !== 8) {
      setError('Backup Code muss 8 Zeichen lang sein');
      return;
    }
    
    try {
      const response = await fetch(
        `${backendUrl}/api/admin/auth/passkey/backup-code-login?email=${encodeURIComponent(email)}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            code: backupCode.toUpperCase()
          })
        }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Ungültiger Backup Code');
      }
      
      const result = await response.json();
      
      toast.success(result.message || 'Login mit Backup Code erfolgreich');
      
      if (result.message && result.message.includes('Warnung')) {
        toast.warning(result.message, { duration: 8000 });
      }
      
      onSuccess(result);
      
    } catch (error) {
      setError(error.message || 'Ungültiger Backup Code');
    }
  };

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-[450px] [&>button]:hidden">
        {!showBackupCode ? (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Fingerprint className="h-6 w-6 text-primary" />
                Passkey-Authentifizierung
              </DialogTitle>
              <DialogDescription>
                Bestätigen Sie Ihre Identität mit Ihrem Fingerabdruck, FaceID oder PIN
              </DialogDescription>
            </DialogHeader>

            <div className="py-8">
              {verifying ? (
                <div className="text-center">
                  <Fingerprint className="h-24 w-24 text-primary mx-auto animate-pulse mb-4" />
                  <p className="text-lg font-medium mb-2">Warten auf Passkey...</p>
                  <p className="text-sm text-muted-foreground">
                    Folgen Sie den Anweisungen Ihres Browsers
                  </p>
                </div>
              ) : (
                <div className="text-center">
                  <Fingerprint className="h-24 w-24 text-muted-foreground mx-auto mb-4" />
                  
                  {error && (
                    <Alert variant="destructive" className="mb-4">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}
                  
                  <Button 
                    onClick={startPasskeyAuth} 
                    className="w-full mb-4"
                    disabled={verifying}
                  >
                    <Fingerprint className="h-4 w-4 mr-2" />
                    Erneut versuchen
                  </Button>
                  
                  <Button 
                    onClick={() => setShowBackupCode(true)} 
                    variant="outline"
                    className="w-full"
                  >
                    <Key className="h-4 w-4 mr-2" />
                    Backup Code verwenden
                  </Button>
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Key className="h-6 w-6 text-primary" />
                Backup Code Login
              </DialogTitle>
              <DialogDescription>
                Geben Sie einen Ihrer Backup Codes ein (8 Zeichen)
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleBackupCodeSubmit} className="space-y-4 my-4">
              <div className="space-y-2">
                <Label htmlFor="backup-code">Backup Code</Label>
                <Input
                  id="backup-code"
                  placeholder="ABCD1234"
                  value={backupCode}
                  onChange={(e) => setBackupCode(e.target.value.toUpperCase())}
                  maxLength={8}
                  className="font-mono text-lg tracking-wider"
                  autoFocus
                />
                <p className="text-xs text-muted-foreground">
                  Jeder Code kann nur einmal verwendet werden
                </p>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="flex gap-2">
                <Button 
                  type="button"
                  variant="outline" 
                  onClick={() => setShowBackupCode(false)}
                  className="flex-1"
                >
                  Zurück zu Passkey
                </Button>
                <Button type="submit" className="flex-1">
                  Einloggen
                </Button>
              </div>
            </form>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

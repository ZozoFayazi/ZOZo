import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import { Shield, Loader2, AlertTriangle, Key } from 'lucide-react';

export const TwoFactorVerify = ({ 
  tempToken, 
  onSuccess, 
  onCancel,
  backendUrl 
}) => {
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [useBackupCode, setUseBackupCode] = useState(false);
  const [backupCode, setBackupCode] = useState('');
  const inputRefs = useRef([]);

  // Focus first input on mount
  useEffect(() => {
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, [useBackupCode]);

  // Handle input change for TOTP code
  const handleChange = (index, value) => {
    // Only allow digits
    const digit = value.replace(/\D/g, '').slice(-1);
    
    const newCode = [...code];
    newCode[index] = digit;
    setCode(newCode);
    setError('');

    // Auto-focus next input
    if (digit && index < 5 && inputRefs.current[index + 1]) {
      inputRefs.current[index + 1].focus();
    }

    // Auto-submit when complete
    if (digit && index === 5) {
      const fullCode = newCode.join('');
      if (fullCode.length === 6) {
        setTimeout(() => verify(fullCode), 100);
      }
    }
  };

  // Handle backspace
  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1].focus();
    }
  };

  // Handle paste
  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    
    if (pastedData.length === 6) {
      const newCode = pastedData.split('');
      setCode(newCode);
      inputRefs.current[5].focus();
      setTimeout(() => verify(pastedData), 100);
    }
  };

  // Verify code
  const verify = async (codeToVerify = null) => {
    const finalCode = codeToVerify || (useBackupCode ? backupCode.replace(/-/g, '') : code.join(''));
    
    if (!useBackupCode && finalCode.length !== 6) {
      setError('Bitte geben Sie einen 6-stelligen Code ein');
      return;
    }

    if (useBackupCode && finalCode.length < 8) {
      setError('Bitte geben Sie einen gültigen Backup-Code ein');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${backendUrl}/api/admin/auth/2fa/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          temp_token: tempToken,
          code: finalCode
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Verifizierung fehlgeschlagen');
      }

      toast.success('2FA erfolgreich verifiziert');
      onSuccess(data);
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
      // Reset code on error
      if (!useBackupCode) {
        setCode(['', '', '', '', '', '']);
        inputRefs.current[0]?.focus();
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto" data-testid="2fa-verify-card">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 p-3 rounded-full bg-primary/10 w-fit">
          <Shield className="h-8 w-8 text-primary" />
        </div>
        <CardTitle>Zwei-Faktor-Authentifizierung</CardTitle>
        <CardDescription>
          {useBackupCode 
            ? 'Geben Sie einen Ihrer Backup-Codes ein'
            : 'Geben Sie den Code aus Ihrer Authenticator-App ein'
          }
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {!useBackupCode ? (
          <>
            {/* TOTP Code Input */}
            <div className="space-y-2">
              <Label className="sr-only">Bestätigungscode</Label>
              <div className="flex justify-center gap-2" onPaste={handlePaste}>
                {code.map((digit, index) => (
                  <Input
                    key={index}
                    ref={(el) => inputRefs.current[index] = el}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(index, e)}
                    className="w-12 h-14 text-center text-2xl font-mono"
                    data-testid={`2fa-digit-${index}`}
                    disabled={loading}
                  />
                ))}
              </div>
            </div>

            <p className="text-xs text-muted-foreground text-center">
              Der Code ändert sich alle 30 Sekunden
            </p>
          </>
        ) : (
          <>
            {/* Backup Code Input */}
            <div className="space-y-2">
              <Label htmlFor="backup-code">Backup-Code</Label>
              <Input
                id="backup-code"
                value={backupCode}
                onChange={(e) => {
                  setBackupCode(e.target.value.toUpperCase());
                  setError('');
                }}
                placeholder="XXXX-XXXX"
                className="text-center font-mono text-lg tracking-wider"
                data-testid="2fa-backup-input"
                disabled={loading}
              />
            </div>

            <Button 
              className="w-full" 
              onClick={() => verify()}
              disabled={loading || backupCode.length < 8}
              data-testid="2fa-verify-backup"
            >
              {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
              Mit Backup-Code anmelden
            </Button>
          </>
        )}
      </CardContent>

      <CardFooter className="flex flex-col gap-2">
        <Button
          variant="ghost"
          className="w-full text-sm"
          onClick={() => {
            setUseBackupCode(!useBackupCode);
            setError('');
            setCode(['', '', '', '', '', '']);
            setBackupCode('');
          }}
          data-testid="2fa-toggle-backup"
        >
          <Key className="h-4 w-4 mr-2" />
          {useBackupCode ? 'Authenticator-Code verwenden' : 'Backup-Code verwenden'}
        </Button>

        <Button
          variant="outline"
          className="w-full"
          onClick={onCancel}
          data-testid="2fa-cancel"
        >
          Abbrechen
        </Button>
      </CardFooter>
    </Card>
  );
};

export default TwoFactorVerify;

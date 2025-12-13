import React, { useState } from 'react';
import { Mail, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

function EmailVerification({ email, onVerified }) {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [codeSent, setCodeSent] = useState(false);

  const sendVerificationCode = async () => {
    setSendingCode(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/email/send-verification`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      });

      if (response.ok) {
        setCodeSent(true);
        toast.success('Verifizierungscode wurde gesendet! 📧');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fehler beim Senden des Codes');
      }
    } catch (error) {
      console.error('Error sending verification code:', error);
      toast.error('Fehler beim Senden des Verifizierungscodes');
    } finally {
      setSendingCode(false);
    }
  };

  const verifyCode = async () => {
    if (code.length !== 6) {
      toast.error('Bitte gib einen 6-stelligen Code ein');
      return;
    }

    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/email/verify-code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, code })
      });

      if (response.ok) {
        toast.success('E-Mail erfolgreich verifiziert! ✅');
        if (onVerified) {
          onVerified(email);
        }
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Ungültiger Verifizierungscode');
      }
    } catch (error) {
      console.error('Error verifying code:', error);
      toast.error('Fehler bei der Verifizierung');
    } finally {
      setLoading(false);
    }
  };

  const handleCodeInput = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setCode(value);
  };

  return (
    <div className="bg-primary/5 border-2 border-primary/20 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <Mail className="h-6 w-6 text-primary" />
        <div>
          <h3 className="font-semibold">E-Mail verifizieren</h3>
          <p className="text-sm text-muted-foreground">{email}</p>
        </div>
      </div>

      {!codeSent ? (
        <div>
          <p className="text-sm text-muted-foreground mb-4">
            Um Bestellbestätigungen und Status-Updates zu erhalten, verifiziere bitte deine E-Mail-Adresse.
          </p>
          <button
            onClick={sendVerificationCode}
            disabled={sendingCode}
            className="w-full bg-primary text-primary-foreground px-4 py-3 rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {sendingCode ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Sende Code...
              </>
            ) : (
              <>
                <Mail className="h-4 w-4" />
                Verifizierungscode senden
              </>
            )}
          </button>
        </div>
      ) : (
        <div>
          <p className="text-sm text-muted-foreground mb-4">
            Wir haben dir einen 6-stelligen Code an <strong>{email}</strong> gesendet.
          </p>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Verifizierungscode
              </label>
              <input
                type="text"
                value={code}
                onChange={handleCodeInput}
                placeholder="000000"
                maxLength={6}
                className="w-full px-4 py-3 bg-background border-2 border-border rounded-lg focus:border-primary focus:outline-none text-center text-2xl font-mono tracking-widest"
              />
            </div>

            <button
              onClick={verifyCode}
              disabled={loading || code.length !== 6}
              className="w-full bg-primary text-primary-foreground px-4 py-3 rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Verifiziere...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4" />
                  E-Mail verifizieren
                </>
              )}
            </button>

            <button
              onClick={() => {
                setCodeSent(false);
                setCode('');
              }}
              className="w-full text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Code erneut senden
            </button>
          </div>

          <div className="mt-4 flex items-start gap-2 text-xs text-muted-foreground bg-muted/50 p-3 rounded-lg">
            <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <p>Der Code ist 10 Minuten gültig. Falls du keine E-Mail erhalten hast, prüfe deinen Spam-Ordner.</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default EmailVerification;

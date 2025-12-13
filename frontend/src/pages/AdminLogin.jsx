import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api';
import { toast } from 'sonner';

function AdminLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await login(email, password);
      // Store token with BOTH keys for compatibility
      localStorage.setItem('zozoAuthToken', response.access_token);
      localStorage.setItem('adminToken', response.access_token);
      localStorage.setItem('zozoUser', JSON.stringify(response.user));
      toast.success('Erfolgreich angemeldet');
      navigate('/admin/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      toast.error('Falsche Anmeldedaten');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <img
            src="https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg"
            alt="ZOZO Burger"
            className="h-16 mx-auto mb-4"
          />
          <h1 className="text-2xl font-serif font-semibold mb-2">Admin Login</h1>
          <p className="text-muted-foreground">Melde dich an, um fortzufahren</p>
        </div>

        <div className="bg-card border border-border rounded-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">E-Mail</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="admin@zozoburger.de"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Passwort</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50"
            >
              {loading ? 'Wird angemeldet...' : 'Anmelden'}
            </button>
          </form>

          <div className="mt-6 p-4 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-2">Test-Zugangsdaten:</p>
            <p className="text-xs">Owner: owner@zozoburger.de / owner123</p>
            <p className="text-xs">Rellingen: rellingen@zozoburger.de / rellingen123</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminLogin;

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Send, Save, Eye } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function CampaignEditor() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [segments, setSegments] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    segment: searchParams.get('segment') || 'all',
    template: 'custom'
  });

  const [emailContent, setEmailContent] = useState('');

  useEffect(() => {
    loadSegments();
  }, []);

  const loadSegments = async () => {
    try {
      const token = localStorage.getItem('zozoAuthToken');
      const response = await axios.get(`${API_URL}/api/admin/newsletter/segments`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSegments(response.data.segments || {});
    } catch (error) {
      console.error('Error loading segments:', error);
    }
  };

  const generateTemplate = (templateType) => {
    const templates = {
      discount: `
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #0a0a0a; color: #ffffff;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0a0a0a;">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table width="600" style="max-width: 600px; background-color: #1a1a1a; border-radius: 12px; overflow: hidden;">
          
          <!-- Logo -->
          <tr>
            <td style="padding: 30px 20px; text-align: center;">
              <img src="https://customer-assets.emergentagent.com/job_zozofinal/artifacts/ucrdxkwy_IMG_8154.jpeg" 
                   alt="ZOZO Burger" style="max-width: 100px; height: auto;">
            </td>
          </tr>
          
          <!-- Content -->
          <tr>
            <td style="padding: 40px 30px;">
              <h1 style="color: #dc2626; font-size: 32px; margin: 0 0 20px 0; text-align: center;">
                🔥 Exklusives Angebot!
              </h1>
              <p style="color: #e5e5e5; font-size: 18px; text-align: center; margin: 0 0 30px 0;">
                Nur für kurze Zeit: <strong style="color: #dc2626;">20% Rabatt</strong> auf deine Bestellung!
              </p>
              
              <!-- Discount Code -->
              <div style="background-color: #dc2626; border-radius: 8px; padding: 20px; margin: 0 0 30px 0; text-align: center;">
                <p style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px;">Dein Rabattcode:</p>
                <p style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold; letter-spacing: 2px;">
                  WEEKEND20
                </p>
              </div>
              
              <!-- CTA Button -->
              <div style="text-align: center; margin: 30px 0;">
                <a href="https://zozo-burger.de" 
                   style="display: inline-block; background-color: #dc2626; color: #ffffff; padding: 16px 40px; 
                          border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                  Jetzt bestellen →
                </a>
              </div>
              
              <p style="color: #a0a0a0; font-size: 14px; text-align: center; margin: 30px 0 0 0;">
                Gültig bis: [DATUM EINFÜGEN]
              </p>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding: 20px 30px; background-color: #0a0a0a; text-align: center; border-top: 1px solid #333;">
              <p style="color: #666; font-size: 12px; margin: 0 0 10px 0;">
                ZOZO Burger - Premium Burger, Pizza & Pasta
              </p>
              <p style="color: #666; font-size: 12px; margin: 0;">
                <a href="{{unsubscribe_link}}" style="color: #dc2626; text-decoration: none;">Abmelden</a>
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`,
      
      announcement: `
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #0a0a0a; color: #ffffff;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0a0a0a;">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table width="600" style="max-width: 600px; background-color: #1a1a1a; border-radius: 12px;">
          
          <tr>
            <td style="padding: 30px 20px; text-align: center;">
              <img src="https://customer-assets.emergentagent.com/job_zozofinal/artifacts/ucrdxkwy_IMG_8154.jpeg" 
                   alt="ZOZO Burger" style="max-width: 100px; height: auto;">
            </td>
          </tr>
          
          <tr>
            <td style="padding: 40px 30px;">
              <h1 style="color: #dc2626; font-size: 28px; margin: 0 0 20px 0; text-align: center;">
                📢 Neuigkeiten von ZOZO!
              </h1>
              
              <p style="color: #e5e5e5; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                [DEINE NACHRICHT HIER]
              </p>
              
              <div style="text-align: center; margin: 30px 0;">
                <a href="https://zozo-burger.de" 
                   style="display: inline-block; background-color: #dc2626; color: #ffffff; padding: 16px 40px; 
                          border-radius: 8px; text-decoration: none; font-weight: bold;">
                  Mehr erfahren →
                </a>
              </div>
            </td>
          </tr>
          
          <tr>
            <td style="padding: 20px 30px; background-color: #0a0a0a; text-align: center;">
              <p style="color: #666; font-size: 12px; margin: 0;">
                <a href="{{unsubscribe_link}}" style="color: #dc2626; text-decoration: none;">Abmelden</a>
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`
    };

    return templates[templateType] || '';
  };

  const handleSubmit = async (sendImmediately = false) => {
    if (!formData.title || !formData.subject || !emailContent) {
      toast.error('Bitte fülle alle Pflichtfelder aus');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('zozoAuthToken');
      
      // Create campaign
      const response = await axios.post(
        `${API_URL}/api/admin/newsletter/campaigns`,
        {
          title: formData.title,
          subject: formData.subject,
          html_content: emailContent,
          segment: formData.segment === 'all' ? null : formData.segment
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const campaignId = response.data.campaign_id;
      
      // Send immediately if requested
      if (sendImmediately) {
        await axios.post(
          `${API_URL}/api/admin/newsletter/campaigns/${campaignId}/send`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Kampagne erstellt und gesendet!');
      } else {
        toast.success('Kampagne als Entwurf gespeichert');
      }
      
      navigate('/admin/newsletter/campaigns');
    } catch (error) {
      console.error('Error creating campaign:', error);
      toast.error('Fehler beim Erstellen der Kampagne');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b border-border">
        <div className="container-custom py-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/admin/newsletter/campaigns')}
              className="p-2 hover:bg-secondary rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-serif font-semibold">Neue Kampagne erstellen</h1>
              <p className="text-sm text-muted-foreground">E-Mail Marketing</p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-custom py-8">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Editor */}
          <div className="space-y-6">
            <div className="bg-card border border-border rounded-xl p-6">
              <h2 className="text-lg font-semibold mb-4">Kampagnen-Einstellungen</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Kampagnen-Name (intern)</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    placeholder="z.B. Weekend Special Februar"
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">E-Mail Betreff</label>
                  <input
                    type="text"
                    value={formData.subject}
                    onChange={(e) => setFormData({...formData, subject: e.target.value})}
                    placeholder="z.B. 🍔 20% Rabatt dieses Wochenende!"
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Zielgruppe</label>
                  <select
                    value={formData.segment}
                    onChange={(e) => setFormData({...formData, segment: e.target.value})}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="all">Alle Abonnenten ({segments.all || 0})</option>
                    {Object.entries(segments).filter(([key]) => key !== 'all').map(([segment, count]) => (
                      <option key={segment} value={segment}>
                        {segment.replace(/_/g, ' ')} ({count})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Vorlage</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setEmailContent(generateTemplate('discount'))}
                      className="btn-secondary text-sm py-2"
                    >
                      🎯 Rabatt-Aktion
                    </button>
                    <button
                      onClick={() => setEmailContent(generateTemplate('announcement'))}
                      className="btn-secondary text-sm py-2"
                    >
                      📢 Ankündigung
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
              <h2 className="text-lg font-semibold mb-4">E-Mail HTML Content</h2>
              <textarea
                value={emailContent}
                onChange={(e) => setEmailContent(e.target.value)}
                placeholder="HTML-Code hier einfügen oder Vorlage wählen..."
                rows={20}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Tipp: unsubscribe_link wird automatisch ersetzt
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={() => handleSubmit(false)}
                disabled={loading}
                className="flex-1 btn-secondary flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Save className="h-4 w-4" />
                Als Entwurf speichern
              </button>
              <button
                onClick={() => handleSubmit(true)}
                disabled={loading}
                className="flex-1 btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
                {loading ? 'Sende...' : 'Sofort senden'}
              </button>
            </div>
          </div>

          {/* Preview */}
          <div className="space-y-6">
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Vorschau</h2>
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  className="btn-secondary text-sm flex items-center gap-2"
                >
                  <Eye className="h-4 w-4" />
                  {showPreview ? 'Verbergen' : 'Anzeigen'}
                </button>
              </div>

              {showPreview && emailContent && (
                <div className="border border-border rounded-lg overflow-hidden">
                  <iframe
                    srcDoc={emailContent}
                    style={{ width: '100%', height: '600px', border: 'none' }}
                    title="Email Preview"
                  />
                </div>
              )}
              
              {!emailContent && (
                <p className="text-sm text-muted-foreground text-center py-8">
                  Wähle eine Vorlage oder füge HTML-Code ein
                </p>
              )}
            </div>

            {/* Preview Info */}
            <div className="bg-muted/30 border border-border rounded-xl p-6">
              <h3 className="font-semibold mb-4">📊 Empfänger-Info</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Segment:</span>
                  <span className="font-medium capitalize">{formData.segment.replace(/_/g, ' ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Empfänger:</span>
                  <span className="font-medium">{segments[formData.segment] || 0}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-border">
                  <span className="text-muted-foreground">Betreff:</span>
                  <span className="font-medium">{formData.subject || '-'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CampaignEditor;

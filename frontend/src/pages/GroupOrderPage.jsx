import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Users, Share2, ShoppingCart, Clock, Trash2, Check, Copy } from 'lucide-react';
import { toast } from 'sonner';

function GroupOrderPage({ addToCart, selectedLocation }) {
  const { groupCode } = useParams();
  const navigate = useNavigate();
  
  const [groupOrder, setGroupOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [participantName, setParticipantName] = useState('');
  const [showAddItems, setShowAddItems] = useState(false);
  const [tempCart, setTempCart] = useState([]);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    if (groupCode) {
      loadGroupOrder();
      // Reload every 10 seconds to see new items
      const interval = setInterval(loadGroupOrder, 10000);
      return () => clearInterval(interval);
    }
  }, [groupCode]);

  const loadGroupOrder = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/group-orders/${groupCode}`);
      if (response.ok) {
        const data = await response.json();
        setGroupOrder(data);
      } else {
        toast.error('Gruppenbestellung nicht gefunden');
      }
    } catch (error) {
      console.error('Error loading group order:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyShareLink = () => {
    const shareLink = `${window.location.origin}/group-order/${groupCode}`;
    navigator.clipboard.writeText(shareLink);
    toast.success('Link kopiert! 📋');
  };

  const addItemsToGroup = async () => {
    if (!participantName.trim()) {
      toast.error('Bitte gib deinen Namen ein');
      return;
    }

    if (tempCart.length === 0) {
      toast.error('Füge erst Items zum Warenkorb hinzu');
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/group-orders/${groupCode}/add-items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          participant_name: participantName,
          items: tempCart
        })
      });

      if (response.ok) {
        toast.success(`${participantName}'s Items hinzugefügt! 🎉`);
        setTempCart([]);
        setParticipantName('');
        setShowAddItems(false);
        loadGroupOrder();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fehler beim Hinzufügen');
      }
    } catch (error) {
      console.error('Error adding items:', error);
      toast.error('Fehler beim Hinzufügen');
    }
  };

  const finalizeOrder = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/group-orders/${groupCode}/finalize`, {
        method: 'POST'
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add all group items to main cart
        data.items.forEach(item => addToCart(item));
        
        toast.success('Gruppenbestellung finalisiert! Jetzt zum Checkout.');
        navigate('/menu');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fehler beim Finalisieren');
      }
    } catch (error) {
      console.error('Error finalizing:', error);
      toast.error('Fehler beim Finalisieren');
    }
  };

  const removeItem = async (index) => {
    try {
      const response = await fetch(`${backendUrl}/api/group-orders/${groupCode}/remove-item/${index}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        toast.success('Item entfernt');
        loadGroupOrder();
      }
    } catch (error) {
      console.error('Error removing item:', error);
    }
  };

  const calculateTotal = () => {
    if (!groupOrder) return 0;
    return groupOrder.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  const getTimeRemaining = () => {
    if (!groupOrder || !groupOrder.expires_at) return '';
    const now = new Date();
    // Parse the ISO string - if it ends with 'Z', it's UTC
    const expiresStr = groupOrder.expires_at;
    const expires = new Date(expiresStr);
    const diff = expires.getTime() - now.getTime();
    
    if (diff <= 0) return 'Abgelaufen';
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (hours > 0) {
      return `${hours}h ${remainingMinutes}min verbleibend`;
    }
    return `${minutes} Min verbleibend`;
  };
  
  const checkIsExpired = () => {
    if (!groupOrder) return false;
    if (groupOrder.status === 'expired') return true;
    if (!groupOrder.expires_at) return false;
    
    const now = new Date();
    const expires = new Date(groupOrder.expires_at);
    return now.getTime() > expires.getTime();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Lade Gruppenbestellung...</p>
        </div>
      </div>
    );
  }

  if (!groupOrder) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-muted-foreground">Gruppenbestellung nicht gefunden</p>
        </div>
      </div>
    );
  }

  const isExpired = checkIsExpired();
  const isFinalized = groupOrder.status === 'finalized';

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="bg-gradient-to-br from-primary/10 to-accent rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Users className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-serif font-bold">Gruppenbestellung</h1>
                <p className="text-muted-foreground">Host: {groupOrder.host_name}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-primary">
                {groupCode}
              </div>
              <div className="text-sm text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {getTimeRemaining()}
              </div>
            </div>
          </div>

          {/* Share Button */}
          {!isExpired && !isFinalized && (
            <button
              onClick={copyShareLink}
              className="w-full bg-primary text-primary-foreground py-3 rounded-lg hover:bg-primary/90 transition-colors flex items-center justify-center gap-2"
            >
              <Share2 className="h-4 w-4" />
              Link teilen & Freunde einladen
            </button>
          )}
        </div>

        {/* Status Badges */}
        {isExpired && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6 mb-6 text-center">
            <p className="text-red-500 font-semibold text-lg mb-3">Diese Gruppenbestellung ist abgelaufen</p>
            <p className="text-muted-foreground mb-4">Gruppenbestellungen sind 1 Stunde gültig. Starte eine neue!</p>
            <button
              onClick={() => navigate('/start-group-order')}
              className="bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors font-semibold"
              data-testid="start-new-group-order-btn"
            >
              Neue Gruppenbestellung starten
            </button>
          </div>
        )}

        {isFinalized && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4 mb-6 text-center">
            <p className="text-green-500 font-semibold">Diese Gruppenbestellung wurde finalisiert</p>
          </div>
        )}

        {/* Participants */}
        <div className="bg-card rounded-xl p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            Teilnehmer ({groupOrder.participants?.length || 0})
          </h2>
          <div className="space-y-2">
            {groupOrder.participants?.map((participant, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-accent rounded-lg">
                <span className="font-medium">{participant.name}</span>
                <span className="text-sm text-muted-foreground">
                  {participant.items_added} Item(s)
                </span>
              </div>
            ))}
            {(!groupOrder.participants || groupOrder.participants.length === 0) && (
              <p className="text-center text-muted-foreground py-4">
                Noch keine Teilnehmer. Teile den Link!
              </p>
            )}
          </div>
        </div>

        {/* Items */}
        <div className="bg-card rounded-xl p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <ShoppingCart className="h-5 w-5 text-primary" />
            Bestellung ({groupOrder.items?.length || 0} Items)
          </h2>
          <div className="space-y-3">
            {groupOrder.items?.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-accent rounded-lg">
                <div className="flex-1">
                  <p className="font-medium">{item.name}</p>
                  {item.size && (
                    <p className="text-sm text-muted-foreground">{item.size}</p>
                  )}
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm">
                    {item.quantity}x €{item.price.toFixed(2)}
                  </span>
                  {!isExpired && !isFinalized && (
                    <button
                      onClick={() => removeItem(idx)}
                      className="text-red-500 hover:text-red-600 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
            {(!groupOrder.items || groupOrder.items.length === 0) && (
              <p className="text-center text-muted-foreground py-4">
                Noch keine Items. Füge welche hinzu!
              </p>
            )}
          </div>

          {/* Total */}
          {groupOrder.items && groupOrder.items.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
              <span className="text-lg font-semibold">Gesamt</span>
              <span className="text-2xl font-bold text-primary">
                €{calculateTotal().toFixed(2)}
              </span>
            </div>
          )}
        </div>

        {/* Actions */}
        {!isExpired && !isFinalized && (
          <div className="space-y-3">
            <button
              onClick={() => navigate('/menu')}
              className="w-full bg-accent text-foreground py-4 rounded-lg hover:bg-accent/80 transition-colors font-semibold"
            >
              Items aus Menü hinzufügen
            </button>
            
            <button
              onClick={finalizeOrder}
              disabled={!groupOrder.items || groupOrder.items.length === 0}
              className="w-full bg-primary text-primary-foreground py-4 rounded-lg hover:bg-primary/90 transition-colors font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Check className="h-5 w-5" />
              Bestellung abschließen & zum Checkout
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default GroupOrderPage;

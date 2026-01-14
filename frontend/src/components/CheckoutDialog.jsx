import React, { useState, useEffect } from 'react';
import { X, CheckCircle, MapPin, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { createOrder } from '../api';
import axios from 'axios';
import EmailVerification from './EmailVerification';
import { AddressAutocomplete, loadGoogleMapsScript } from './AddressAutocomplete';
import PayPalCheckout from './PayPalCheckout';
import GPSAddressButton from './GPSAddressButton';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function CheckoutDialog({ open, onClose, cart, cartTotal, deliveryFee, total, selectedLocation, clearCart, onCloseCart }) {
  const [loading, setLoading] = useState(false);
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [orderNumber, setOrderNumber] = useState('');
  const [orderCreated, setOrderCreated] = useState(false);
  const [createdOrderId, setCreatedOrderId] = useState(null);
  const [createdOrderData, setCreatedOrderData] = useState(null);
  const [isPickup, setIsPickup] = useState(() => {
    // Load saved preference from localStorage
    const saved = localStorage.getItem('preferredOrderType');
    return saved === 'pickup';
  });
  const [isScheduled, setIsScheduled] = useState(false);
  const [scheduledDate, setScheduledDate] = useState(() => {
    // Default: Heute
    return new Date().toISOString().split('T')[0];
  });
  const [scheduledTime, setScheduledTime] = useState(() => {
    // Default: In 2 Stunden
    const twoHoursLater = new Date(Date.now() + 2 * 60 * 60 * 1000);
    return twoHoursLater.toTimeString().slice(0, 5);
  });
  const [deliveryCheck, setDeliveryCheck] = useState(null);
  const [checkingDelivery, setCheckingDelivery] = useState(false);
  const [detectedLocation, setDetectedLocation] = useState(null);
  const [loyaltyAccount, setLoyaltyAccount] = useState(null);
  const [pointsToRedeem, setPointsToRedeem] = useState(0);
  const [emailVerified, setEmailVerified] = useState(false);
  const [showEmailVerification, setShowEmailVerification] = useState(false);
  const [mapsLoaded, setMapsLoaded] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    address: '',
    postal_code: '',
    city: '',
    notes: '',
    payment_method: 'paypal' // Default to PayPal
  });
  
  // Load Google Maps on mount
  useEffect(() => {
    if (open) {
      loadGoogleMapsScript(() => {
        setMapsLoaded(true);
      });
    }
  }, [open]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    
    // Load loyalty account and check verification when email changes
    if (e.target.name === 'email' && e.target.value.includes('@')) {
      loadLoyaltyAccount(e.target.value);
      checkEmailVerified(e.target.value);
    }
  };
  
  const loadLoyaltyAccount = async (email) => {
    try {
      const response = await axios.get(`${API_URL}/api/loyalty/account/${email}`);
      if (response.data) {
        setLoyaltyAccount(response.data);
        // Save email to localStorage for rewards page
        localStorage.setItem('customerEmail', email);
      }
    } catch (error) {
      console.error('Error loading loyalty account:', error);
    }
  };
  
  const checkEmailVerified = async (email) => {
    try {
      const response = await axios.get(`${API_URL}/api/email/is-verified/${email}`);
      setEmailVerified(response.data.verified);
      setShowEmailVerification(!response.data.verified);
    } catch (error) {
      console.error('Error checking email verification:', error);
      setShowEmailVerification(true);
    }
  };
  
  const handleEmailVerified = (email) => {
    setEmailVerified(true);
    setShowEmailVerification(false);
    toast.success('E-Mail verifiziert! Du erhältst jetzt Bestellupdates. 📧');
  };
  
  const maxRedeemablePoints = loyaltyAccount ? Math.min(
    loyaltyAccount.points,
    Math.floor(total / 0.50) // Can't redeem more points than the order total allows
  ) : 0;
  
  const pointsDiscount = pointsToRedeem * 0.50;
  const finalTotal = Math.max(0, total - pointsDiscount);

  // Check delivery availability when postal code changes
  useEffect(() => {
    if (formData.postal_code.length === 5) {
      checkDeliveryAvailability(formData.postal_code);
    } else {
      setDeliveryCheck(null);
      setDetectedLocation(null);
    }
  }, [formData.postal_code]);

  const checkDeliveryAvailability = async (postalCode) => {
    setCheckingDelivery(true);
    try {
      const response = await axios.get(`${API_URL}/api/check-delivery-zone?postal_code=${postalCode}`);
      
      setDeliveryCheck(response.data);
      
      if (response.data.available && response.data.location) {
        setDetectedLocation(response.data.location);
        
        // Show success message with fees
        const { min_order_value, delivery_fee, free_delivery_threshold } = response.data;
        toast.success(
          `Lieferung nach ${postalCode} möglich! Mindestbestellwert: €${min_order_value.toFixed(2)}, Lieferkosten: €${delivery_fee.toFixed(2)} (ab €${free_delivery_threshold.toFixed(2)} kostenlos)`
        );
      } else {
        toast.error(response.data.message || 'Lieferung zu dieser PLZ nicht verfügbar');
      }
    } catch (error) {
      console.error('Delivery check error:', error);
    } finally {
      setCheckingDelivery(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Only check delivery for delivery orders
    if (!isPickup) {
      // Check if delivery is available
      if (!deliveryCheck || !deliveryCheck.available) {
        toast.error('Lieferung zu dieser Postleitzahl nicht verfügbar');
        return;
      }
      
      // Check minimum order value
      if (cartTotal < deliveryCheck.min_order_value) {
        toast.error(`Mindestbestellwert von €${deliveryCheck.min_order_value.toFixed(2)} nicht erreicht! Aktuell: €${cartTotal.toFixed(2)}`);
        return;
      }
    }

    setLoading(true);

    try {
      // Use detected location if available, otherwise use selected location
      const locationToUse = detectedLocation || selectedLocation;
      
      const orderData = {
        location_id: locationToUse.id,
        items: cart.map(item => ({
          menu_item_id: item.menu_item_id,
          name: item.name,
          price: item.price,
          size: item.size,
          quantity: item.quantity
        })),
        customer: {
          name: formData.name,
          phone: formData.phone,
          email: formData.email || undefined,
          address: isPickup ? 'Abholung' : formData.address,
          postal_code: isPickup ? '00000' : formData.postal_code,
          city: isPickup ? locationToUse.city || 'Abholung' : formData.city,
          notes: formData.notes || undefined
        },
        payment_method: formData.payment_method,
        points_to_redeem: pointsToRedeem,
        is_pickup: isPickup
      };
      
      // Add scheduled time if selected
      if (isScheduled && scheduledDate && scheduledTime) {
        // Combine date and time, format as ISO string
        const scheduledDateTime = `${scheduledDate}T${scheduledTime}:00`;
        orderData.scheduled_time = scheduledDateTime;
      }

      // CRITICAL CHANGE: For PayPal, do NOT create order yet!
      // PayPal flow: show payment -> after success -> create final order
      if (formData.payment_method === 'paypal') {
        // Just prepare the order data and show PayPal buttons
        setCreatedOrderData(orderData);  // Store for PayPal component
        setOrderCreated(true);
        toast.info('Bitte schließe die Zahlung mit PayPal ab.');
      } else {
        // For cash/card, create order immediately as before
        const response = await createOrder(orderData);
        setOrderNumber(response.order_number);
        setCreatedOrderId(response.id);
        setCreatedOrderData(response);
        setOrderPlaced(true);
        
        // Show points earned notification
        if (response.points_earned) {
          setTimeout(() => {
            toast.success(`🎉 ${response.points_earned} Treuepunkte verdient!`, {
              duration: 5000
            });
          }, 1000);
        }
        
        // Show achievement notifications
        if (response.unlocked_achievements && response.unlocked_achievements.length > 0) {
          setTimeout(() => {
            response.unlocked_achievements.forEach((achievementId, index) => {
              setTimeout(() => {
                toast.success(`🏆 Achievement freigeschaltet: ${achievementId}!`, {
                  duration: 6000
                });
              }, (index + 1) * 1500);
            });
          }, 2000);
        }
        
        clearCart();
        toast.success('Bestellung erfolgreich aufgegeben!');
      }
      
      // Save customer info for quick reorder
      if (formData.email) {
        localStorage.setItem('lastCustomerEmail', formData.email);
      }
      if (formData.phone) {
        localStorage.setItem('lastCustomerPhone', formData.phone);
      }
      
    } catch (error) {
      console.error('Order error:', error);
      const errorMessage = error.response?.data?.detail || 'Fehler bei der Bestellung. Bitte versuche es erneut.';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handlePayPalSuccess = async (paymentData) => {
    // Payment successful - final order NOW created by backend
    setOrderNumber(paymentData.order_number);
    setCreatedOrderId(paymentData.order_id);
    setOrderPlaced(true);
    setOrderCreated(false);
    
    clearCart();
    toast.success('Zahlung erfolgreich! Bestellung wurde an das Restaurant gesendet.');
  };

  const handlePayPalError = (error) => {
    toast.error('PayPal-Zahlung fehlgeschlagen. Bitte versuche es erneut.');
    // Reset to form so user can try again
    setOrderCreated(false);
  };

  const handlePayPalCancel = () => {
    toast.info('Zahlung abgebrochen. Du kannst es erneut versuchen.');
    // Reset to form
    setOrderCreated(false);
  };

  const handleClose = () => {
    setFormData({
      name: '',
      phone: '',
      email: '',
      address: '',
      postal_code: '',
      city: '',
      notes: '',
      payment_method: 'paypal'
    });
    setOrderPlaced(false);
    setOrderCreated(false);
    setCreatedOrderId(null);
    setCreatedOrderData(null);
    setOrderNumber('');
    onClose();
    if (orderPlaced) {
      onCloseCart();
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm animate-fade-in"
        onClick={handleClose}
      />

      {/* Dialog */}
      <div className="relative bg-card border border-border rounded-xl w-full max-w-lg max-h-[90vh] overflow-y-auto animate-scale-in">
        {orderPlaced ? (
          // Success Screen
          <div className="p-8 text-center">
            <CheckCircle className="h-16 w-16 mx-auto mb-4 text-success" />
            <h2 className="heading-2 mb-2">Vielen Dank!</h2>
            <p className="text-muted-foreground mb-4">
              Deine Bestellung wurde erfolgreich aufgegeben.
            </p>
            <div className="bg-background border border-border rounded-lg p-4 mb-6">
              <p className="text-sm text-muted-foreground mb-1">Bestellnummer</p>
              <p className="text-2xl font-bold text-primary">{orderNumber}</p>
            </div>
            <p className="text-sm text-muted-foreground mb-6">
              {isPickup 
                ? 'Du kannst deine Bestellung in ca. 15 Minuten abholen.'
                : 'Du erhältst deine Bestellung in 30-45 Minuten.'}
            </p>
            <button
              onClick={handleClose}
              className="btn-primary w-full"
            >
              Schließen
            </button>
          </div>
        ) : orderCreated && formData.payment_method === 'paypal' ? (
          // PayPal Payment Screen
          <>
            <div className="flex items-center justify-between p-6 border-b border-border">
              <h2 className="text-lg font-semibold">Mit PayPal bezahlen</h2>
              <button
                onClick={handleClose}
                className="p-2 hover:bg-secondary rounded-lg transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Order Summary */}
              <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
                <p className="text-sm text-muted-foreground mb-2">Bestellnummer</p>
                <p className="text-xl font-bold text-primary mb-4">{orderNumber}</p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Zwischensumme</span>
                    <span>€{cartTotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Liefergebühr</span>
                    <span>{deliveryFee === 0 ? 'Kostenlos' : `€${deliveryFee.toFixed(2)}`}</span>
                  </div>
                  {pointsToRedeem > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Punkte-Rabatt</span>
                      <span>-€{pointsDiscount.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-lg font-semibold pt-2 border-t border-border">
                    <span>Gesamt</span>
                    <span className="text-primary">€{finalTotal.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* PayPal Buttons */}
              <div>
                <p className="text-sm text-muted-foreground mb-4 text-center">
                  Klicke auf den PayPal-Button um die Zahlung abzuschließen
                </p>
                <PayPalCheckout
                  locationId={(detectedLocation || selectedLocation)?.id}
                  orderId={createdOrderId}
                  orderNumber={orderNumber}
                  subtotal={cartTotal}
                  deliveryFee={deliveryFee}
                  discount={pointsDiscount}
                  total={finalTotal}
                  onSuccess={handlePayPalSuccess}
                  onError={handlePayPalError}
                />
              </div>

              {/* Cancel Option */}
              <div className="text-center">
                <button
                  onClick={handleClose}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Abbrechen
                </button>
              </div>
            </div>
          </>
        ) : (
          // Checkout Form
          <>
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border">
              <h2 className="text-lg font-semibold">Bestellung abschließen</h2>
              <button
                onClick={handleClose}
                className="p-2 hover:bg-secondary rounded-lg transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {/* Pickup/Delivery Toggle */}
              <div>
                <label className="block text-sm font-medium mb-3">Bestellart *</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setIsPickup(false);
                      localStorage.setItem('preferredOrderType', 'delivery');
                    }}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      !isPickup
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border hover:border-primary/40'
                    }`}
                    data-testid="order-type-delivery"
                  >
                    <p className="font-semibold">🚚 Lieferung</p>
                    <p className="text-xs mt-1 opacity-80">30-45 Min</p>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setIsPickup(true);
                      localStorage.setItem('preferredOrderType', 'pickup');
                    }}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      isPickup
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border hover:border-primary/40'
                    }`}
                    data-testid="order-type-pickup"
                  >
                    <p className="font-semibold">🏪 Abholung</p>
                    <p className="text-xs mt-1 opacity-80">15 Min</p>
                  </button>
                </div>
              </div>

              {/* Zeit-Auswahl: Sofort vs Später */}
              <div>
                <label className="block text-sm font-medium mb-3">Lieferzeit</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setIsScheduled(false)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      !isScheduled
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border hover:border-primary/40'
                    }`}
                    data-testid="time-asap"
                  >
                    <p className="font-semibold">⚡ Sofort</p>
                    <p className="text-xs mt-1 opacity-80">{isPickup ? '15 Min' : '30-45 Min'}</p>
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsScheduled(true)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      isScheduled
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border hover:border-primary/40'
                    }`}
                    data-testid="time-scheduled"
                  >
                    <p className="font-semibold">🕐 Zu einer Zeit</p>
                    <p className="text-xs mt-1 opacity-80">Zeitbestellung</p>
                  </button>
                </div>
              </div>

              {/* Zeitauswahl (nur wenn Zeitbestellung gewählt) */}
              {isScheduled && (
                <div className="bg-primary/5 border border-primary/20 rounded-lg p-4 space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium mb-2 text-muted-foreground">Datum</label>
                      <input
                        type="date"
                        value={scheduledDate}
                        onChange={(e) => setScheduledDate(e.target.value)}
                        min={new Date().toISOString().split('T')[0]}
                        max={new Date(Date.now() + 86400000).toISOString().split('T')[0]}
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                        required={isScheduled}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium mb-2 text-muted-foreground">Uhrzeit</label>
                      <input
                        type="time"
                        value={scheduledTime}
                        onChange={(e) => setScheduledTime(e.target.value)}
                        min="11:00"
                        max="22:30"
                        step="900"
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                        required={isScheduled}
                      />
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Zeitbestellungen nur während der Öffnungszeiten (11:00 - 22:30 Uhr)
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Telefon *</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">E-Mail (optional)</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Email Verification */}
              {formData.email && formData.email.includes('@') && showEmailVerification && (
                <EmailVerification 
                  email={formData.email} 
                  onVerified={handleEmailVerified}
                />
              )}

              {/* Address fields - Only for Delivery */}
              {!isPickup && (
                <>
                  {/* GPS Address Button */}
                  <div>
                    <label className="block text-sm font-medium mb-3">Lieferadresse</label>
                    <p className="text-sm text-muted-foreground mb-3">
                      Damit wir dich zuverlässig finden.
                    </p>
                    
                    <GPSAddressButton
                      onAddressFilled={(address) => {
                        setFormData({
                          ...formData,
                          address: address.street || '',
                          postal_code: address.postal_code || '',
                          city: address.city || ''
                        });
                        
                        // Auto-check delivery
                        if (address.postal_code) {
                          checkDeliveryAvailability(address.postal_code);
                        }
                      }}
                      disabled={loading}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Straße & Hausnummer *</label>
                    {mapsLoaded ? (
                      <AddressAutocomplete
                        initialValue={formData.address}
                        onAddressSelect={(addressData) => {
                          setFormData({
                            ...formData,
                            address: addressData.address,
                            postal_code: addressData.postalCode,
                            city: addressData.city
                          });
                          
                          // Auto-check delivery for this postal code
                          if (addressData.postalCode) {
                            checkDeliveryAvailability(addressData.postalCode);
                          }
                        }}
                        placeholder="Straße und Hausnummer eingeben…"
                      />
                    ) : (
                      <input
                        type="text"
                        name="address"
                        value={formData.address}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="Straße und Hausnummer"
                      />
                    )}
                  </div>
                </>
              )}

              {!isPickup && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">PLZ *</label>
                    <input
                      type="text"
                      name="postal_code"
                      value={formData.postal_code}
                      onChange={handleChange}
                      required
                      maxLength={5}
                      className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="z.B. 25462"
                    />
                    {checkingDelivery && (
                      <p className="text-xs text-muted-foreground mt-1">Prüfe Liefergebiet...</p>
                    )}
                    {deliveryCheck && !deliveryCheck.available && (
                      <div className="mt-2 p-2 bg-destructive/10 border border-destructive/20 rounded text-xs text-destructive flex items-start gap-2">
                        <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                        <span>{deliveryCheck.message}</span>
                      </div>
                    )}
                    {deliveryCheck && deliveryCheck.available && (
                      <div className="mt-2 p-3 bg-primary/10 border border-primary/20 rounded-lg text-xs space-y-1">
                        <div className="flex items-center gap-2 text-primary font-semibold">
                          <CheckCircle className="h-4 w-4" />
                          <span>Lieferung möglich!</span>
                        </div>
                        <div className="text-foreground space-y-0.5 ml-6">
                          <p><span className="font-medium">Standort:</span> {detectedLocation?.name.replace('ZOZO Burger ', '')}</p>
                          <p><span className="font-medium">Mindestbestellwert:</span> €{deliveryCheck.min_order_value.toFixed(2)}</p>
                          <p><span className="font-medium">Lieferkosten:</span> €{deliveryCheck.delivery_fee.toFixed(2)}</p>
                          <p className="text-primary"><span className="font-medium">Gratis ab:</span> €{deliveryCheck.free_delivery_threshold.toFixed(2)}</p>
                        </div>
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Stadt *</label>
                    <input
                      type="text"
                      name="city"
                      value={formData.city}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Anmerkungen (optional)</label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  placeholder="z.B. bitte klingeln"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Zahlungsmethode *</label>
                <div className="space-y-3">
                  {/* PayPal Option */}
                  <label
                    className={`flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      formData.payment_method === 'paypal'
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/40'
                    }`}
                  >
                    <input
                      type="radio"
                      name="payment_method"
                      value="paypal"
                      checked={formData.payment_method === 'paypal'}
                      onChange={handleChange}
                      className="w-4 h-4 text-primary"
                      data-testid="payment-paypal"
                    />
                    <div className="flex-1">
                      <p className="font-medium">PayPal</p>
                      <p className="text-xs text-muted-foreground">Online bezahlen mit PayPal</p>
                    </div>
                  </label>

                  {/* Cash Option */}
                  <label
                    className={`flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      formData.payment_method === 'cash'
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/40'
                    }`}
                  >
                    <input
                      type="radio"
                      name="payment_method"
                      value="cash"
                      checked={formData.payment_method === 'cash'}
                      onChange={handleChange}
                      className="w-4 h-4 text-primary"
                      data-testid="payment-cash"
                    />
                    <div className="flex-1">
                      <p className="font-medium">Barzahlung vor Ort</p>
                      <p className="text-xs text-muted-foreground">Bei Abholung oder Lieferung bar bezahlen</p>
                    </div>
                  </label>

                  {/* Card Option */}
                  <label
                    className={`flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      formData.payment_method === 'card'
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/40'
                    }`}
                  >
                    <input
                      type="radio"
                      name="payment_method"
                      value="card"
                      checked={formData.payment_method === 'card'}
                      onChange={handleChange}
                      className="w-4 h-4 text-primary"
                      data-testid="payment-card"
                    />
                    <div className="flex-1">
                      <p className="font-medium">Kartenzahlung vor Ort</p>
                      <p className="text-xs text-muted-foreground">Bei Abholung oder Lieferung mit Karte bezahlen</p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Loyalty Points Redemption */}
              {loyaltyAccount && loyaltyAccount.points > 0 && (
                <div className="bg-primary/5 border-2 border-primary/20 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="font-semibold text-sm flex items-center gap-2">
                        🎁 Treuepunkte einlösen
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Verfügbar: {loyaltyAccount.points} Punkte (€{(loyaltyAccount.points * 0.50).toFixed(2)})
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <input
                      type="range"
                      min="0"
                      max={maxRedeemablePoints}
                      value={pointsToRedeem}
                      onChange={(e) => setPointsToRedeem(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs">
                      <span>{pointsToRedeem} Punkte</span>
                      <span className="font-semibold text-primary">-€{pointsDiscount.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Summary */}
              <div className="bg-background border border-border rounded-lg p-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Zwischensumme</span>
                  <span>€{cartTotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Liefergebühr</span>
                  <span>{deliveryFee === 0 ? 'Kostenlos' : `€${deliveryFee.toFixed(2)}`}</span>
                </div>
                {pointsToRedeem > 0 && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Punkte-Rabatt ({pointsToRedeem} Punkte)</span>
                    <span>-€{pointsDiscount.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between text-lg font-semibold pt-2 border-t border-border">
                  <span>Gesamt</span>
                  <span className="text-primary">€{finalTotal.toFixed(2)}</span>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full disabled:opacity-50"
              >
                {loading ? 'Wird bearbeitet...' : 'Jetzt bestellen'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

export default CheckoutDialog;

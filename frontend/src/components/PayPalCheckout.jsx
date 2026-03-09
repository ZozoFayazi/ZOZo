import React, { useState, useEffect } from 'react';
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function PayPalCheckout({ 
  locationId,
  orderData,  // Complete order data (items, customer, totals)
  onSuccess, 
  onError,
  onCancel
}) {
  const [clientId, setClientId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch PayPal Client ID for this location
    const fetchClientId = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/paypal/client-id/${locationId}`);
        setClientId(response.data.client_id);
        setLoading(false);
      } catch (error) {
        console.error('Failed to load PayPal:', error);
        setError('PayPal ist für diesen Standort nicht verfügbar');
        setLoading(false);
      }
    };

    if (locationId) {
      fetchClientId();
    }
  }, [locationId]);

  const createOrder = async () => {
    try {
      // Create PayPal order + payment draft (NO final order yet!)
      const response = await axios.post(`${API_URL}/api/paypal/create-order`, {
        location_id: locationId,
        items: orderData.items,
        customer: orderData.customer,
        subtotal: orderData.subtotal,
        delivery_fee: orderData.deliveryFee,
        discount: orderData.discount || 0,
        points_to_redeem: orderData.points_to_redeem || 0,  // Include loyalty points
        total: orderData.total,
        is_pickup: orderData.isPickup || false,
        currency: 'EUR',
        return_url: `${window.location.origin}/order-success`,
        cancel_url: `${window.location.origin}/checkout`
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'PayPal order creation failed');
      }

      // Store payment_draft_id for capture
      window.paypalDraftId = response.data.payment_draft_id;

     } catch (import React, { useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function PayPalCheckout({ 
  locationId, 
  orderData, 
  onSuccess, 
  onError, 
  onCancel 
}) {
  const paypalRef = useRef();
  const [paypalLoaded, setPaypalLoaded] = useState(false);
  const [paypalClientId, setPaypalClientId] = useState(null);

  // Load PayPal client ID from backend
  useEffect(() => {
    const loadPayPalConfig = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/paypal/client-id?location_id=${locationId}`);
        if (response.data.client_id) {
          setPaypalClientId(response.data.client_id);
        }
      } catch (error) {
        console.error('Failed to load PayPal config:', error);
        toast.error('PayPal-Konfiguration konnte nicht geladen werden');
      }
    };
    
    if (locationId) {
      loadPayPalConfig();
    }
  }, [locationId]);

  useEffect(() => {
    if (!paypalClientId || paypalLoaded) return;

    // Load PayPal SDK
    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=${paypalClientId}&currency=EUR&locale=de_DE`;
    script.async = true;
    
    script.onload = () => {
      setPaypalLoaded(true);
    };
    
    document.body.appendChild(script);

    return () => {
      // Cleanup
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [paypalClientId, paypalLoaded]);

  useEffect(() => {
    if (!paypalLoaded || !window.paypal) return;

    // Clear existing buttons
    if (paypalRef.current) {
      paypalRef.current.innerHTML = '';
    }

    window.paypal.Buttons({
      createOrder: async () => {
        try {
          const response = await axios.post(`${API_URL}/api/paypal/create-order`, {
            location_id: locationId,
            items: orderData.items,
            customer: orderData.customer,
            subtotal: orderData.subtotal,
            delivery_fee: orderData.deliveryFee,
            discount: orderData.discount || 0,
            points_to_redeem: orderData.points_to_redeem || 0,
            total: orderData.total,
            is_pickup: orderData.isPickup
          });
          return response.data.paypal_order_id;
        } catch (error) {
          console.error('Create order error:', error);
          
          // Handle Pydantic validation errors properly
          let errorMessage = 'Fehler beim Erstellen der PayPal-Zahlung';
          const detail = error.response?.data?.detail;
          
          if (detail) {
            if (typeof detail === 'string') {
              errorMessage = detail;
            } else if (Array.isArray(detail)) {
              // Pydantic v2 validation errors
              const messages = detail.map(err => err.msg || 'Validierungsfehler').join(', ');
              errorMessage = messages;
            } else if (typeof detail === 'object' && detail.msg) {
              errorMessage = detail.msg;
            }
          }
          
          toast.error(errorMessage);
          throw error;
        }
      },
      onApprove: async (data) => {
        try {
          const response = await axios.post(`${API_URL}/api/paypal/capture-order`, {
            paypal_order_id: data.orderID,
            location_id: locationId
          });
          
          onSuccess(response.data);
        } catch (error) {
          console.error('Capture error:', error);
          toast.error('Zahlung konnte nicht abgeschlossen werden');
          onError(error);
        }
      },
      onCancel: () => {
        onCancel();
      },
      onError: (err) => {
        console.error('PayPal error:', err);
        onError(err);
      },
      style: {
        layout: 'vertical',
        color: 'gold',
        shape: 'rect',
        label: 'paypal',
        height: 45
      }
    }).render(paypalRef.current);
  }, [paypalLoaded, locationId, orderData, onSuccess, onError, onCancel]);

  if (!paypalClientId) {
    return (
      <div className="text-center py-4">
        <p className="text-muted-foreground">PayPal wird geladen...</p>
      </div>
    );
  }

  return (
    <div>
      <div ref={paypalRef} className="min-h-[50px]" />
      {!paypalLoaded && (
        <div className="text-center py-4">
          <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2"></div>
          <p className="text-sm text-muted-foreground">PayPal wird geladen...</p>
        </div>
      )}
    </div>
  );
}

export default PayPalCheckout;error) {
      console.error('Create order error:', error);
      
      let errorMessage = 'Fehler beim Erstellen der PayPal-Zahlung';
      const detail = error.response?.data?.detail;
      
      if (detail) {
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          const messages = detail.map(err => err.msg || 'Validierungsfehler').join(', ');
          errorMessage = messages;
        } else if (typeof detail === 'object' && detail.msg) {
          errorMessage = detail.msg;
        }
      }
      
      toast.error(errorMessage);
      throw error;
    }
  const onApprove = async (data) => {
    try {
      // Capture payment and finalize order
      const response = await axios.post(`${API_URL}/api/paypal/capture-order`, {
        paypal_order_id: data.orderID
      });

      if (response.data.success) {
        toast.success('Zahlung erfolgreich! 💰');
        if (onSuccess) {
          onSuccess(response.data);
        }
      } else {
        throw new Error(response.data.error || 'Payment capture failed');
      }
    } catch (error) {
      console.error('Capture error:', error);
      toast.error('Fehler bei der Zahlungsabwicklung');
      if (onError) {
        onError(error);
      }
    }
  };

  const onCancelHandler = () => {
    toast.info('Zahlung abgebrochen');
    if (onCancel) {
      onCancel();
    }
  };

  const onErrorHandler = (err) => {
    console.error('PayPal error:', err);
    toast.error('Ein Fehler ist bei PayPal aufgetreten');
    if (onError) {
      onError(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-center">
        <p className="text-destructive text-sm">{error}</p>
      </div>
    );
  }

  if (!clientId) {
    return (
      <div className="bg-muted border border-border rounded-lg p-4 text-center">
        <p className="text-muted-foreground text-sm">PayPal ist nicht verfügbar</p>
      </div>
    );
  }

  return (
    <div className="paypal-button-container">
      <PayPalScriptProvider
        options={{
          clientId: clientId,
          currency: 'EUR',
          intent: 'capture'
        }}
      >
        <PayPalButtons
          style={{
            layout: 'vertical',
            color: 'gold',
            shape: 'rect',
            label: 'pay',
            height: 48
          }}
          createOrder={createOrder}
          onApprove={onApprove}
          onCancel={onCancelHandler}
          onError={onErrorHandler}
        />
      </PayPalScriptProvider>
    </div>
  );
}

export default PayPalCheckout;

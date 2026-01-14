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

      return response.data.paypal_order_id;
    } catch (error) {
      console.error('Create order error:', error);
      toast.error('Fehler beim Erstellen der PayPal-Zahlung');
      throw error;
    }
  };

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

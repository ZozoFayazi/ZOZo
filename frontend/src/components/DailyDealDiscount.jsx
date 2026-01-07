import React, { useState, useEffect, useCallback } from 'react';
import { Tag, Gift, Info } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

/**
 * DailyDealDiscount - Zeigt und berechnet den Tagesangebot-Rabatt im Warenkorb
 * 
 * Props:
 * - cartItems: Array der Warenkorb-Items
 * - locationId: ID des ausgewählten Standorts (optional)
 * - onDiscountCalculated: Callback mit dem berechneten Rabatt
 */
function DailyDealDiscount({ cartItems, locationId, onDiscountCalculated }) {
  const [discountInfo, setDiscountInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  const calculateDiscount = useCallback(async () => {
    if (!cartItems || cartItems.length === 0) {
      setDiscountInfo(null);
      if (onDiscountCalculated) {
        onDiscountCalculated(0, null);
      }
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/daily-deal/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: cartItems.map(item => ({
            menu_item_id: item.menu_item_id,
            name: item.name,
            category: item.category || item.category_slug,
            price: item.price,
            quantity: item.quantity,
            size: item.size
          })),
          location_id: locationId
        })
      });

      if (response.ok) {
        const data = await response.json();
        setDiscountInfo(data);
        
        if (onDiscountCalculated) {
          onDiscountCalculated(data.discount_amount || 0, data);
        }
      }
    } catch (error) {
      console.error('Error calculating daily deal discount:', error);
      setDiscountInfo(null);
      if (onDiscountCalculated) {
        onDiscountCalculated(0, null);
      }
    } finally {
      setLoading(false);
    }
  }, [cartItems, locationId, onDiscountCalculated]);

  useEffect(() => {
    // Debounce the calculation
    const timer = setTimeout(() => {
      calculateDiscount();
    }, 300);

    return () => clearTimeout(timer);
  }, [calculateDiscount]);

  // Kein Rabatt verfügbar
  if (!discountInfo || !discountInfo.deal || discountInfo.discount_amount === 0) {
    return null;
  }

  const { deal, discount_amount, discount_details, applicable_items } = discountInfo;

  return (
    <TooltipProvider>
      <div 
        className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-lg p-4 mb-4"
        data-testid="daily-deal-discount"
      >
        <div className="flex items-start justify-between gap-3">
          {/* Left: Info */}
          <div className="flex items-start gap-3">
            <div 
              className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: deal.badge_color || '#4CAF50' }}
            >
              <Gift className="h-5 w-5 text-white" />
            </div>
            
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-semibold text-green-700 dark:text-green-400">
                  {deal.title}
                </h4>
                
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p className="text-sm">{deal.description}</p>
                    {discount_details && discount_details.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-border">
                        <p className="text-xs font-medium mb-1">Rabatt angewendet auf:</p>
                        <ul className="text-xs space-y-0.5">
                          {discount_details.map((detail, idx) => (
                            <li key={idx} className="flex justify-between">
                              <span>
                                {detail.item_name}
                                {detail.item_size && ` (${detail.item_size})`}
                              </span>
                              <span className="text-green-600">-€{detail.discount.toFixed(2)}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </TooltipContent>
                </Tooltip>
              </div>
              
              <p className="text-sm text-muted-foreground">
                {applicable_items.length} {applicable_items.length === 1 ? 'Artikel' : 'Artikel'} im Angebot
              </p>
            </div>
          </div>

          {/* Right: Discount Amount */}
          <div className="text-right">
            <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
              <Tag className="h-4 w-4" />
              <span className="text-lg font-bold">
                -€{discount_amount.toFixed(2)}
              </span>
            </div>
            <span 
              className="text-xs px-2 py-0.5 rounded-full text-white"
              style={{ backgroundColor: deal.badge_color || '#4CAF50' }}
            >
              {deal.badge_text}
            </span>
          </div>
        </div>

        {/* Details (wenn Produkte aufgelistet werden sollen) */}
        {discount_details && discount_details.length > 0 && discount_details.length <= 3 && (
          <div className="mt-3 pt-3 border-t border-green-500/20">
            <div className="flex flex-wrap gap-2">
              {discount_details.map((detail, idx) => (
                <span 
                  key={idx}
                  className="text-xs bg-green-500/10 text-green-700 dark:text-green-400 px-2 py-1 rounded-full"
                >
                  {detail.item_name}: -€{detail.discount.toFixed(2)}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </TooltipProvider>
  );
}

export default DailyDealDiscount;

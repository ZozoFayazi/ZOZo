import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Trophy, TrendingUp } from 'lucide-react';

function TopProductsList({ data, loading = false }) {
  if (loading) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            Top 10 Produkte
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="flex items-center justify-between">
                <div className="h-4 bg-muted animate-pulse rounded w-32"></div>
                <div className="h-4 bg-muted animate-pulse rounded w-16"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            Top 10 Produkte
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Keine Daten verfügbar
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border" data-testid="top-products-list">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Trophy className="h-5 w-5 text-amber-500" />
          Top 10 Produkte
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.map((product, index) => (
            <div 
              key={index} 
              className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
              data-testid={`top-product-${index}`}
            >
              <div className="flex items-center gap-3">
                <div className={`flex items-center justify-center h-8 w-8 rounded-full font-bold text-sm ${
                  index === 0 ? 'bg-amber-500 text-white' :
                  index === 1 ? 'bg-gray-400 text-white' :
                  index === 2 ? 'bg-orange-600 text-white' :
                  'bg-muted text-muted-foreground'
                }`}>
                  {index + 1}
                </div>
                <div>
                  <div className="font-medium text-foreground">{product.name}</div>
                  <div className="text-sm text-muted-foreground">
                    {product.quantity}x verkauft
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-bold text-foreground">€{product.revenue.toFixed(2)}</div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default TopProductsList;

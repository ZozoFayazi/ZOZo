import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Store } from 'lucide-react';

function LocationComparison({ data, loading = false }) {
  if (loading) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Store className="h-5 w-5 text-primary" />
            Filial-Vergleich
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <div className="text-muted-foreground">Lädt...</div>
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
            <Store className="h-5 w-5 text-primary" />
            Filial-Vergleich
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <div className="text-muted-foreground">Keine Daten verfügbar</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border" data-testid="location-comparison">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Store className="h-5 w-5 text-primary" />
          Filial-Vergleich
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.map((location, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium text-foreground">{location.location}</span>
                <span className="text-sm text-muted-foreground">
                  {location.orders} Bestellungen
                </span>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-8 bg-muted rounded-lg overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-primary to-primary/70 flex items-center justify-end px-3"
                    style={{ 
                      width: `${(location.revenue / Math.max(...data.map(d => d.revenue))) * 100}%` 
                    }}
                  >
                    <span className="text-sm font-bold text-primary-foreground">
                      €{location.revenue.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-xs text-muted-foreground">
                Ø Bestellwert: €{location.avg_order_value.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default LocationComparison;

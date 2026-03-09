import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

function MetricCard({ title, value, change, icon: Icon, prefix = '', suffix = '', loading = false }) {
  const getTrendIcon = () => {
    if (!change || change === 0) return <Minus className="h-4 w-4" />;
    return change > 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />;
  };

  const getTrendColor = () => {
    if (!change || change === 0) return 'text-muted-foreground';
    return change > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400';
  };

  if (loading) {
    return (
      <Card className="border-border">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          {Icon && (
            <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Icon className="h-4 w-4 text-primary" />
            </div>
          )}
        </CardHeader>
        <CardContent>
          <div className="h-8 bg-muted animate-pulse rounded w-24 mb-2"></div>
          <div className="h-4 bg-muted animate-pulse rounded w-16"></div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border" data-testid={`metric-card-${title.toLowerCase().replace(/\s+/g, '-')}`}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {Icon && (
          <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Icon className="h-4 w-4 text-primary" />
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-foreground">
          {prefix}{typeof value === 'number' ? value.toLocaleString('de-DE') : value}{suffix}
        </div>
        {change !== undefined && change !== null && (
          <div className={`flex items-center gap-1 text-sm mt-1 ${getTrendColor()}`}>
            {getTrendIcon()}
            <span className="font-medium">
              {Math.abs(change).toFixed(1)}%
            </span>
            <span className="text-muted-foreground">vs. vorherige Periode</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default MetricCard;

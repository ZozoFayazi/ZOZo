import React from 'react';
import { Badge } from './ui/badge';

function RFMBadge({ segment, score }) {
  const getSegmentColor = () => {
    switch (segment) {
      case 'VIP':
        return 'bg-gradient-to-r from-amber-500 to-yellow-500 text-white border-0';
      case 'Active':
        return 'bg-gradient-to-r from-emerald-500 to-green-500 text-white border-0';
      case 'Regular':
        return 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white border-0';
      case 'At-Risk':
        return 'bg-gradient-to-r from-orange-500 to-red-500 text-white border-0';
      case 'Lost':
        return 'bg-gradient-to-r from-gray-600 to-gray-700 text-white border-0';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const getSegmentIcon = () => {
    switch (segment) {
      case 'VIP':
        return '🏆';
      case 'Active':
        return '⭐';
      case 'Regular':
        return '👤';
      case 'At-Risk':
        return '⚠️';
      case 'Lost':
        return '🚫';
      default:
        return '❓';
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Badge className={`${getSegmentColor()} font-semibold px-3 py-1`}>
        <span className="mr-1.5">{getSegmentIcon()}</span>
        {segment}
      </Badge>
      {score && (
        <span className="text-xs text-muted-foreground">RFM: {score}</span>
      )}
    </div>
  );
}

export default RFMBadge;

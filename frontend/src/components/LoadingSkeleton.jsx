import React from 'react';

function LoadingSkeleton({ type = 'card' }) {
  if (type === 'card') {
    return (
      <div className="bg-card border border-border rounded-lg p-4 animate-pulse">
        <div className="aspect-video bg-secondary rounded-lg mb-3" />
        <div className="h-4 bg-secondary rounded w-3/4 mb-2" />
        <div className="h-3 bg-secondary rounded w-1/2" />
      </div>
    );
  }

  if (type === 'list') {
    return (
      <div className="bg-card border border-border rounded-lg p-4 animate-pulse">
        <div className="flex gap-4">
          <div className="w-20 h-20 bg-secondary rounded-lg" />
          <div className="flex-1">
            <div className="h-4 bg-secondary rounded w-2/3 mb-2" />
            <div className="h-3 bg-secondary rounded w-1/2" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 animate-pulse">
      <div className="h-4 bg-secondary rounded w-full" />
      <div className="h-4 bg-secondary rounded w-5/6" />
      <div className="h-4 bg-secondary rounded w-4/6" />
    </div>
  );
}

export default LoadingSkeleton;

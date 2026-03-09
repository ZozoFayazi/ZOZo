import React, { useState, useEffect } from 'react';
import { Star, MessageSquare } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function PublicReviews({ locationId, limit = 5 }) {
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReviews();
    loadStats();
  }, [locationId]);

  const loadReviews = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/reviews/location/${locationId}?limit=${limit}`);
      setReviews(response.data);
    } catch (error) {
      console.error('Error loading reviews:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/reviews/stats/${locationId}`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStars = (rating) => {
    return Array(5).fill(0).map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 inline ${i < Math.round(rating) ? 'fill-amber-500 text-amber-500' : 'text-gray-600'}`}
      />
    ));
  };

  if (loading) return null;

  if (!stats || stats.total_reviews === 0) return null;

  return (
    <div className="py-12">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-foreground mb-4">Kundenbewertungen</h2>
        <div className="flex items-center justify-center gap-2 mb-2">
          {getStars(stats.avg_overall)}
          <span className="text-2xl font-bold ml-2">{stats.avg_overall}/5</span>
        </div>
        <p className="text-muted-foreground">
          Basierend auf {stats.total_reviews} {stats.total_reviews === 1 ? 'Bewertung' : 'Bewertungen'}
        </p>
        <div className="grid grid-cols-3 gap-4 max-w-md mx-auto mt-4 text-sm">
          <div>
            <div className="text-muted-foreground mb-1">🍔 Essen</div>
            <div className="font-bold">{stats.avg_food}/5</div>
          </div>
          <div>
            <div className="text-muted-foreground mb-1">🚚 Lieferung</div>
            <div className="font-bold">{stats.avg_delivery}/5</div>
          </div>
          <div>
            <div className="text-muted-foreground mb-1">💰 Preis</div>
            <div className="font-bold">{stats.avg_value}/5</div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reviews.slice(0, limit).map(review => (
          <Card key={review.review_id} className="border-border">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold">{review.customer_name}</span>
                <div className="flex items-center gap-1">
                  {getStars(review.ratings.overall)}
                  <span className="ml-1 text-sm font-bold">{review.ratings.overall}</span>
                </div>
              </div>
              
              {review.comment && (
                <p className="text-sm text-muted-foreground mb-3">{review.comment}</p>
              )}
              
              {review.tags && review.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {review.tags.map((tag, i) => (
                    <span key={i} className="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              
              <div className="text-xs text-muted-foreground mt-3">
                {new Date(review.created_at).toLocaleDateString('de-DE')}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default PublicReviews;
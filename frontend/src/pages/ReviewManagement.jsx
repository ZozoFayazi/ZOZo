import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Star, Check, X, Eye, MessageSquare } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function ReviewManagement() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadReviews();
  }, [filter]);

  const loadReviews = async () => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('adminToken');
      const params = filter !== 'all' ? { status: filter } : {};
      
      const response = await axios.get(`${API_URL}/api/admin/reviews`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      
      setReviews(response.data);
    } catch (error) {
      console.error('Error loading reviews:', error);
      toast.error('Fehler beim Laden der Bewertungen');
    } finally {
      setLoading(false);
    }
  };

  const moderateReview = async (reviewId, action) => {
    try {
      const token = sessionStorage.getItem('adminToken');
      await axios.patch(
        `${API_URL}/api/admin/reviews/${reviewId}/moderate`,
        { action },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success(action === 'approve' ? 'Bewertung freigegeben' : 'Bewertung abgelehnt');
      loadReviews();
    } catch (error) {
      console.error('Error moderating review:', error);
      toast.error('Fehler bei der Moderation');
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

  return (
    <AdminLayout>
      <div className="min-h-screen bg-background p-4 lg:p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">⭐ Bewertungen</h1>
          <p className="text-muted-foreground">Kundenfeedback verwalten</p>
        </div>

        <div className="flex gap-2 mb-6">
          {['all', 'pending', 'approved', 'rejected'].map(f => (
            <Button
              key={f}
              variant={filter === f ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(f)}
            >
              {f === 'all' ? 'Alle' : f === 'pending' ? 'Ausstehend' : f === 'approved' ? 'Freigegeben' : 'Abgelehnt'}
            </Button>
          ))}
        </div>

        <div className="space-y-4">
          {loading ? (
            <Card className="border-border"><CardContent className="p-12 text-center">Lädt...</CardContent></Card>
          ) : reviews.length === 0 ? (
            <Card className="border-border">
              <CardContent className="p-12 text-center">
                <Star className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">Keine Bewertungen</h3>
                <p className="text-muted-foreground">Es wurden noch keine Bewertungen abgegeben.</p>
              </CardContent>
            </Card>
          ) : (
            reviews.map(review => (
              <Card key={review.review_id} className="border-border">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-semibold text-lg">{review.customer_name}</span>
                        <span className="text-sm text-muted-foreground">#{review.order_id}</span>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {new Date(review.created_at).toLocaleDateString('de-DE', {
                          day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
                        })}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {review.status === 'pending' && (
                        <>
                          <Button size="sm" variant="outline" onClick={() => moderateReview(review.review_id, 'approve')}>
                            <Check className="h-4 w-4 mr-1" /> Freigeben
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => moderateReview(review.review_id, 'reject')}>
                            <X className="h-4 w-4 mr-1" /> Ablehnen
                          </Button>
                        </>
                      )}
                      {review.status === 'approved' && (
                        <span className="px-3 py-1 bg-emerald-500/10 text-emerald-600 rounded-full text-sm">Freigegeben</span>
                      )}
                      {review.status === 'rejected' && (
                        <span className="px-3 py-1 bg-red-500/10 text-red-600 rounded-full text-sm">Abgelehnt</span>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="bg-muted/30 p-3 rounded-lg">
                      <div className="text-xs text-muted-foreground mb-1">🍔 Essen</div>
                      <div className="flex items-center gap-1">
                        {getStars(review.ratings.food)}
                        <span className="ml-2 font-bold">{review.ratings.food}/5</span>
                      </div>
                    </div>
                    <div className="bg-muted/30 p-3 rounded-lg">
                      <div className="text-xs text-muted-foreground mb-1">🚚 Lieferung</div>
                      <div className="flex items-center gap-1">
                        {getStars(review.ratings.delivery)}
                        <span className="ml-2 font-bold">{review.ratings.delivery}/5</span>
                      </div>
                    </div>
                    <div className="bg-muted/30 p-3 rounded-lg">
                      <div className="text-xs text-muted-foreground mb-1">💰 Preis</div>
                      <div className="flex items-center gap-1">
                        {getStars(review.ratings.value)}
                        <span className="ml-2 font-bold">{review.ratings.value}/5</span>
                      </div>
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className="text-2xl font-bold text-foreground flex items-center gap-2">
                      {getStars(review.ratings.overall)}
                      <span className="ml-2">{review.ratings.overall}/5</span>
                    </div>
                  </div>

                  {review.tags && review.tags.length > 0 && (
                    <div className="flex gap-2 mb-3">
                      {review.tags.map((tag, i) => (
                        <span key={i} className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {review.comment && (
                    <div className="bg-muted/30 p-4 rounded-lg border-l-4 border-primary">
                      <MessageSquare className="h-4 w-4 text-muted-foreground inline mr-2" />
                      <span className="text-foreground">{review.comment}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </AdminLayout>
  );
}

export default ReviewManagement;
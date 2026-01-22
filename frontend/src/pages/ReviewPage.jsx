import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Star, Send, Check, UtensilsCrossed, Truck, Euro, Tag } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function ReviewPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const orderId = searchParams.get('order');
  const preRating = parseInt(searchParams.get('rating') || '0');
  
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [reward, setReward] = useState(null);
  
  // Ratings
  const [foodRating, setFoodRating] = useState(preRating || 0);
  const [deliveryRating, setDeliveryRating] = useState(preRating || 0);
  const [valueRating, setValueRating] = useState(preRating || 0);
  
  // Optional fields
  const [comment, setComment] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  
  const quickTags = [
    'Super lecker!',
    'Schnelle Lieferung',
    'Große Portion',
    'Warm angekommen',
    'Freundlicher Fahrer',
    'Gutes Preis-Leistungs-Verhältnis'
  ];
  
  const customerEmail = searchParams.get('email') || '';
  
  const toggleTag = (tag) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };
  
  const handleSubmit = async () => {
    if (foodRating === 0 || deliveryRating === 0 || valueRating === 0) {
      toast.error('Bitte alle Kategorien bewerten');
      return;
    }
    
    if (!orderId || !customerEmail) {
      toast.error('Fehlende Order-Informationen');
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/reviews`, {
        order_id: orderId,
        customer_email: customerEmail,
        food_rating: foodRating,
        delivery_rating: deliveryRating,
        value_rating: valueRating,
        comment: comment || null,
        tags: selectedTags.length > 0 ? selectedTags : null
      });
      
      if (response.data.success) {
        setSubmitted(true);
        setReward(response.data.reward);
        
        const overall = response.data.overall_rating;
        if (overall >= 4.5 && response.data.reward) {
          toast.success(`Danke für deine 5-Sterne-Bewertung! 🎁 Hier ist dein Dankeschön-Code: ${response.data.reward.code}`);
        } else {
          toast.success('Bewertung erfolgreich abgegeben!');
        }
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      toast.error(error.response?.data?.detail || 'Fehler beim Absenden der Bewertung');
    } finally {
      setLoading(false);
    }
  };
  
  const StarRating = ({ rating, setRating, label, icon: Icon, color }) => (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Icon className={`h-5 w-5 ${color}`} />
        <span className="font-semibold text-foreground">{label}</span>
      </div>
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map(star => (
          <button
            key={star}
            onClick={() => setRating(star)}
            className="transition-transform hover:scale-110 focus:outline-none"
            data-testid={`${label.toLowerCase()}-star-${star}`}
          >
            <Star
              className={`h-10 w-10 ${
                star <= rating 
                  ? 'fill-amber-500 text-amber-500' 
                  : 'text-gray-600 hover:text-gray-400'
              }`}
            />
          </button>
        ))}
        <span className="ml-3 text-2xl font-bold text-foreground">{rating}/5</span>
      </div>
    </div>
  );
  
  if (submitted) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="max-w-md w-full border-border">
          <CardContent className="p-8 text-center">
            <div className="h-16 w-16 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
              <Check className="h-8 w-8 text-emerald-600" />
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2">Vielen Dank!</h2>
            <p className="text-muted-foreground mb-6">
              Deine Bewertung wurde erfolgreich abgegeben.
            </p>
            
            {reward && (
              <div className="bg-gradient-to-br from-amber-500 to-orange-600 p-6 rounded-lg mb-6">
                <p className="text-white text-sm mb-2">🎁 Dein Dankeschön-Code:</p>
                <p className="text-white text-3xl font-bold mb-2">{reward.code}</p>
                <p className="text-white text-sm opacity-90">{reward.discount}% Rabatt • Gültig {reward.valid_days} Tage</p>
              </div>
            )}
            
            <Button onClick={() => navigate('/menu')} className="w-full">
              Zurück zur Speisekarte
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <Card className="border-border" data-testid="review-page">
          <CardHeader>
            <CardTitle className="text-2xl text-center">
              Wie war deine Bestellung? ⭐
            </CardTitle>
            <p className="text-center text-muted-foreground">
              Dein Feedback hilft uns besser zu werden!
            </p>
          </CardHeader>
          <CardContent className="p-8">
            <StarRating
              rating={foodRating}
              setRating={setFoodRating}
              label="Essen"
              icon={UtensilsCrossed}
              color="text-red-600"
            />
            
            <StarRating
              rating={deliveryRating}
              setRating={setDeliveryRating}
              label="Lieferung"
              icon={Truck}
              color="text-blue-600"
            />
            
            <StarRating
              rating={valueRating}
              setRating={setValueRating}
              label="Preis-Leistung"
              icon={Euro}
              color="text-emerald-600"
            />
            
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Tag className="h-5 w-5 text-purple-600" />
                <span className="font-semibold text-foreground">Schnell-Tags (optional)</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {quickTags.map(tag => (
                  <button
                    key={tag}
                    onClick={() => toggleTag(tag)}
                    className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                      selectedTags.includes(tag)
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground hover:bg-muted/70'
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="mb-6">
              <label className="block font-semibold text-foreground mb-2">
                Kommentar (optional)
              </label>
              <Textarea
                placeholder="Teile uns deine Erfahrung mit..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={4}
                className="resize-none"
              />
            </div>
            
            {(foodRating >= 4 && deliveryRating >= 4 && valueRating >= 4) && (
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4 mb-6">
                <p className="text-sm text-emerald-600 dark:text-emerald-400">
                  🎁 Bei 5-Sterne-Bewertungen erhältst du automatisch einen 5% Dankeschön-Gutschein!
                </p>
              </div>
            )}
            
            <Button
              onClick={handleSubmit}
              disabled={loading || foodRating === 0 || deliveryRating === 0 || valueRating === 0}
              className="w-full"
              size="lg"
              data-testid="submit-review-button"
            >
              {loading ? (
                <>Wird gesendet...</>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Bewertung absenden
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default ReviewPage;

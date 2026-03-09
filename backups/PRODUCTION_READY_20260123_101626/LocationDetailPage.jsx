import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Separator } from '../components/ui/separator';
import MapPlaceholder from '../components/MapPlaceholder';
import { 
  MapPin, 
  Clock, 
  Phone, 
  Mail, 
  Navigation, 
  Truck, 
  Euro, 
  Star,
  ChevronRight,
  ExternalLink,
  CheckCircle2,
  XCircle
} from 'lucide-react';

// Helper function to build full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  // Convert /uploads/... to /api/uploads/... for Kubernetes Ingress routing
  if (imageUrl.startsWith('/uploads/')) {
    return `${backendUrl}/api${imageUrl}`;
  }
  return `${backendUrl}${imageUrl}`;
};

export default function LocationDetailPage({ setSelectedLocation }) {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    const fetchLocation = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${backendUrl}/api/locations/${slug}?include_menu=true`);
        
        if (!response.ok) {
          if (response.status === 404) {
            setError('Standort nicht gefunden');
          } else {
            throw new Error('Fehler beim Laden');
          }
          return;
        }
        
        const data = await response.json();
        setLocation(data);
      } catch (err) {
        console.error('Error fetching location:', err);
        setError('Fehler beim Laden des Standorts');
      } finally {
        setLoading(false);
      }
    };

    if (slug) {
      fetchLocation();
    }
  }, [slug, backendUrl]);

  const handleOrderHere = () => {
    if (location) {
      setSelectedLocation(location);
      navigate('/menu');
    }
  };

  // Generate JSON-LD Schema
  const generateSchema = () => {
    if (!location) return null;

    const schema = {
      "@context": "https://schema.org",
      "@type": "Restaurant",
      "@id": `${window.location.origin}/standorte/${location.slug}`,
      "name": location.name,
      "alternateName": "ZOZO Burger",
      "image": "https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg",
      "description": location.seo?.meta_description || `ZOZO Burger ${location.city} - Premium Burger, Pizza, Pasta & More`,
      "url": `${window.location.origin}/standorte/${location.slug}`,
      "telephone": location.phone,
      "email": location.email,
      "address": {
        "@type": "PostalAddress",
        "streetAddress": location.address,
        "addressLocality": location.city,
        "postalCode": location.postal_code,
        "addressCountry": "DE"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": location.lat || 0,
        "longitude": location.lng || 0
      },
      "priceRange": "€€",
      "servesCuisine": ["Burger", "Pizza", "Pasta", "Amerikanisch", "Italienisch"],
      "acceptsReservations": "False",
      "paymentAccepted": "Cash, Credit Card, PayPal",
      "currenciesAccepted": "EUR",
      "areaServed": {
        "@type": "GeoCircle",
        "geoMidpoint": {
          "@type": "GeoCoordinates",
          "latitude": location.lat || 0,
          "longitude": location.lng || 0
        },
        "geoRadius": `${location.delivery_info?.radius_km || 5} km`
      },
      "hasMenu": {
        "@type": "Menu",
        "url": `${window.location.origin}/menu`,
        "hasMenuSection": [
          {
            "@type": "MenuSection",
            "name": "Burger",
            "description": "Saftige Premium Burger"
          },
          {
            "@type": "MenuSection", 
            "name": "Pizza",
            "description": "Knusprige Pizza"
          },
          {
            "@type": "MenuSection",
            "name": "Pasta",
            "description": "Italienische Pasta"
          }
        ]
      },
      "openingHoursSpecification": location.formatted_hours?.filter(h => h.is_open).map(h => ({
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": h.day_key.charAt(0).toUpperCase() + h.day_key.slice(1),
        "opens": h.hours.split(' - ')[0],
        "closes": h.hours.split(' - ')[1]
      })) || [],
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.7",
        "reviewCount": "127",
        "bestRating": "5",
        "worstRating": "1"
      }
    };

    return schema;
  };

  // Generate Breadcrumb Schema
  const generateBreadcrumbSchema = () => {
    if (!location) return null;

    return {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "ZOZO Burger",
          "item": window.location.origin
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Standorte",
          "item": `${window.location.origin}/standorte`
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": location.name,
          "item": `${window.location.origin}/standorte/${location.slug}`
        }
      ]
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Lädt Standort...</p>
        </div>
      </div>
    );
  }

  if (error || !location) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-bold text-foreground">Standort nicht gefunden</h1>
          <p className="text-muted-foreground">Der angeforderte Standort existiert nicht.</p>
          <Link to="/standorte">
            <Button>Alle Standorte ansehen</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* SEO Meta Tags & Schema */}
      <Helmet>
        <title>{location.seo?.meta_title}</title>
        <meta name="description" content={location.seo?.meta_description} />
        <meta name="keywords" content={location.seo?.keywords} />
        
        {/* Open Graph */}
        <meta property="og:title" content={location.seo?.meta_title} />
        <meta property="og:description" content={location.seo?.meta_description} />
        <meta property="og:type" content="restaurant" />
        <meta property="og:url" content={`${window.location.origin}/standorte/${location.slug}`} />
        <meta property="og:image" content="https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg" />
        <meta property="og:locale" content="de_DE" />
        
        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={location.seo?.meta_title} />
        <meta name="twitter:description" content={location.seo?.meta_description} />
        
        {/* Geo Tags */}
        <meta name="geo.region" content="DE-SH" />
        <meta name="geo.placename" content={location.city} />
        <meta name="geo.position" content={`${location.lat};${location.lng}`} />
        <meta name="ICBM" content={`${location.lat}, ${location.lng}`} />
        
        {/* Canonical */}
        <link rel="canonical" href={`${window.location.origin}/standorte/${location.slug}`} />
        
        {/* JSON-LD Schema */}
        <script type="application/ld+json">
          {JSON.stringify(generateSchema())}
        </script>
        <script type="application/ld+json">
          {JSON.stringify(generateBreadcrumbSchema())}
        </script>
      </Helmet>

      <div className="min-h-screen bg-background" data-testid="location-detail-page">
        {/* Breadcrumb */}
        <div className="bg-card border-b border-border">
          <div className="container-custom py-3">
            <nav className="flex items-center text-sm text-muted-foreground" aria-label="Breadcrumb">
              <Link to="/" className="hover:text-foreground transition-colors">Start</Link>
              <ChevronRight className="h-4 w-4 mx-2" />
              <Link to="/standorte" className="hover:text-foreground transition-colors">Standorte</Link>
              <ChevronRight className="h-4 w-4 mx-2" />
              <span className="text-foreground font-medium">{location.name}</span>
            </nav>
          </div>
        </div>

        {/* Hero Section with Map */}
        <div className="relative">
          <MapPlaceholder 
            address={location.address}
            city={location.city}
            className="aspect-[21/9] md:aspect-[21/6]"
          />
          
          {/* Overlay Card */}
          <div className="container-custom">
            <div className="relative -mt-16 md:-mt-24 z-10">
              <Card className="max-w-2xl mx-auto lg:mx-0">
                <CardContent className="p-6 md:p-8">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <Badge 
                        className={location.opening_status?.is_open 
                          ? "bg-[hsl(var(--success)/0.12)] text-[hsl(var(--success))] mb-3" 
                          : "bg-[hsl(var(--destructive)/0.12)] text-[hsl(var(--destructive))] mb-3"
                        }
                        data-testid="location-status-badge"
                      >
                        {location.opening_status?.is_open ? (
                          <><CheckCircle2 className="h-3 w-3 mr-1" /> Jetzt geöffnet</>
                        ) : (
                          <><XCircle className="h-3 w-3 mr-1" /> Geschlossen</>
                        )}
                      </Badge>
                      <h1 className="text-2xl md:text-3xl font-serif font-bold text-foreground" data-testid="location-name">
                        {location.name}
                      </h1>
                      <p className="text-muted-foreground mt-1">{location.address}, {location.postal_code} {location.city}</p>
                    </div>
                    <div className="hidden md:block">
                      <div className="h-16 w-16 rounded-xl bg-primary flex items-center justify-center">
                        <span className="text-primary-foreground font-bold text-xl">ZB</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-6 flex flex-wrap gap-3">
                    <Button onClick={handleOrderHere} className="flex-1 md:flex-none" data-testid="order-here-button">
                      <Truck className="h-4 w-4 mr-2" />
                      Jetzt bestellen
                    </Button>
                    {location.phone && (
                      <Button variant="outline" asChild>
                        <a href={`tel:${location.phone}`}>
                          <Phone className="h-4 w-4 mr-2" />
                          Anrufen
                        </a>
                      </Button>
                    )}
                    <Button variant="outline" asChild>
                      <a 
                        href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(location.address + ', ' + location.city)}`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Navigation className="h-4 w-4 mr-2" />
                        Route
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="container-custom py-12">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Left Column - Details */}
            <div className="lg:col-span-2 space-y-8">
              {/* Opening Hours */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-primary" />
                    Öffnungszeiten
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4" data-testid="opening-hours">
                    {location.formatted_hours?.map((hours, idx) => (
                      <div 
                        key={idx}
                        className={`flex justify-between py-2 px-3 rounded-lg ${
                          hours.is_open ? 'bg-muted/30' : 'bg-muted/10 text-muted-foreground'
                        }`}
                      >
                        <span className="font-medium">{hours.day}</span>
                        <span>{hours.hours}</span>
                      </div>
                    ))}
                  </div>
                  {location.opening_status?.next_change && (
                    <p className="text-sm text-muted-foreground mt-4">
                      {location.opening_status?.is_open 
                        ? `Schließt um ${location.opening_status.next_change}`
                        : `Öffnet um ${location.opening_status.next_change}`
                      }
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* Delivery Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Truck className="h-5 w-5 text-primary" />
                    Lieferinformationen
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid sm:grid-cols-3 gap-4" data-testid="delivery-info">
                    <div className="text-center p-4 bg-muted/30 rounded-lg">
                      <Euro className="h-6 w-6 mx-auto mb-2 text-primary" />
                      <p className="text-sm text-muted-foreground">Mindestbestellwert</p>
                      <p className="text-lg font-bold">€{location.delivery_info?.min_order_value?.toFixed(2)}</p>
                    </div>
                    <div className="text-center p-4 bg-muted/30 rounded-lg">
                      <Truck className="h-6 w-6 mx-auto mb-2 text-primary" />
                      <p className="text-sm text-muted-foreground">Liefergebühr</p>
                      <p className="text-lg font-bold">€{location.delivery_info?.delivery_fee?.toFixed(2)}</p>
                    </div>
                    <div className="text-center p-4 bg-muted/30 rounded-lg">
                      <Clock className="h-6 w-6 mx-auto mb-2 text-primary" />
                      <p className="text-sm text-muted-foreground">Lieferzeit</p>
                      <p className="text-lg font-bold">{location.delivery_info?.estimated_time}</p>
                    </div>
                  </div>
                  
                  {location.delivery_info?.postal_codes?.length > 0 && (
                    <div className="mt-6">
                      <p className="text-sm font-medium mb-3">Wir liefern nach:</p>
                      <div className="flex flex-wrap gap-2">
                        {location.delivery_info.postal_codes.slice(0, 10).map((plz, idx) => (
                          <Badge key={idx} variant="secondary">{plz}</Badge>
                        ))}
                        {location.delivery_info.postal_codes.length > 10 && (
                          <Badge variant="outline">+{location.delivery_info.postal_codes.length - 10} weitere</Badge>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Popular Items */}
              {location.popular_items?.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Star className="h-5 w-5 text-primary" />
                      Beliebte Gerichte
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid sm:grid-cols-2 gap-4">
                      {location.popular_items.map((item, idx) => (
                        <div 
                          key={idx}
                          className="flex items-center gap-4 p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                          onClick={handleOrderHere}
                        >
                          {item.image_url && (
                            <img 
                              src={getImageUrl(item.image_url)} 
                              alt={item.name}
                              className="w-16 h-16 rounded-lg object-cover"
                            />
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="font-medium truncate">{item.name}</p>
                            <p className="text-sm text-primary font-bold">
                              ab €{(item.price_normal || item.price_medium)?.toFixed(2)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                    <Button 
                      variant="outline" 
                      className="w-full mt-4"
                      onClick={handleOrderHere}
                    >
                      Zur Speisekarte
                      <ChevronRight className="h-4 w-4 ml-2" />
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Right Column - Contact & CTA */}
            <div className="space-y-6">
              {/* Contact Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-primary" />
                    Kontakt
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-start gap-3">
                    <MapPin className="h-5 w-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium">{location.address}</p>
                      <p className="text-muted-foreground">{location.postal_code} {location.city}</p>
                    </div>
                  </div>
                  
                  {location.phone && (
                    <div className="flex items-center gap-3">
                      <Phone className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                      <a 
                        href={`tel:${location.phone}`} 
                        className="font-medium hover:text-primary transition-colors"
                        data-testid="phone-link"
                      >
                        {location.phone}
                      </a>
                    </div>
                  )}
                  
                  {location.email && (
                    <div className="flex items-center gap-3">
                      <Mail className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                      <a 
                        href={`mailto:${location.email}`}
                        className="font-medium hover:text-primary transition-colors"
                        data-testid="email-link"
                      >
                        {location.email}
                      </a>
                    </div>
                  )}

                  <Separator className="my-4" />

                  {location.google_review_url && (
                    <a 
                      href={location.google_review_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      <Star className="h-4 w-4" />
                      Bewertung auf Google schreiben
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </CardContent>
              </Card>

              {/* CTA Card */}
              <Card className="bg-primary text-primary-foreground">
                <CardContent className="p-6 text-center">
                  <h3 className="text-xl font-serif font-bold mb-2">Hunger?</h3>
                  <p className="text-primary-foreground/80 mb-4">
                    Bestelle jetzt und genieße in {location.delivery_info?.estimated_time || '30-45 Min'}!
                  </p>
                  <Button 
                    variant="secondary" 
                    className="w-full"
                    onClick={handleOrderHere}
                    data-testid="cta-order-button"
                  >
                    <Truck className="h-4 w-4 mr-2" />
                    Jetzt bestellen
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

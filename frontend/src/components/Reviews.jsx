import React from 'react';
import { Star, Quote } from 'lucide-react';

function Reviews() {
  const reviews = [
    {
      id: 1,
      name: 'Sarah M.',
      rating: 5,
      text: 'Die besten Burger in der Umgebung! Immer frisch, saftig und super schnell geliefert. Besonders der ZOZO Classic ist der Hammer!',
      date: '2 Wochen her'
    },
    {
      id: 2,
      name: 'Michael K.',
      rating: 5,
      text: 'Qualität top, Preise fair und die Lieferung war schneller als angekündigt. Die Sweet Potato Fries sind ein Muss!',
      date: '1 Monat her'
    },
    {
      id: 3,
      name: 'Lisa R.',
      rating: 5,
      text: 'Endlich ein Burger-Lieferservice der hält was er verspricht. Die Zutaten schmecken frisch und das Fleisch ist perfekt gebraten.',
      date: '3 Wochen her'
    },
    {
      id: 4,
      name: 'Tom B.',
      rating: 5,
      text: 'Mega lecker! Die veganen Optionen sind überraschend gut. Auch als Nicht-Veganer bestelle ich mir manchmal den Veggie-Burger.',
      date: '1 Woche her'
    }
  ];

  return (
    <section className="py-16 bg-accent/30">
      <div className="container-custom">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-4">
            <Star className="h-4 w-4 text-primary fill-primary" />
            <span className="text-sm font-medium text-primary">4.9 von 5 Sternen</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-serif font-bold mb-3">
            Was unsere Kunden sagen
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Über 1.000 zufriedene Kunden vertrauen auf ZOZO Burger
          </p>
        </div>

        {/* Reviews Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {reviews.map((review) => (
            <div
              key={review.id}
              className="bg-card border border-border rounded-xl p-6 hover:border-primary/30 transition-colors relative"
              data-testid={`review-${review.id}`}
            >
              {/* Quote Icon */}
              <Quote className="absolute top-4 right-4 h-8 w-8 text-primary/10" />

              {/* Rating */}
              <div className="flex items-center gap-1 mb-3">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-4 w-4 ${
                      i < review.rating
                        ? 'text-yellow-500 fill-yellow-500'
                        : 'text-muted-foreground/30'
                    }`}
                  />
                ))}
              </div>

              {/* Review Text */}
              <p className="text-foreground/90 mb-4 leading-relaxed">
                "{review.text}"
              </p>

              {/* Author */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-sm">{review.name}</p>
                  <p className="text-xs text-muted-foreground">Verifizierter Kunde</p>
                </div>
                <span className="text-xs text-muted-foreground">{review.date}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Overall Stats */}
        <div className="mt-12 grid grid-cols-3 gap-8 max-w-3xl mx-auto">
          <div className="text-center">
            <p className="text-3xl font-bold text-primary">1000+</p>
            <p className="text-sm text-muted-foreground mt-1">Bestellungen</p>
          </div>
          <div className="text-center border-x border-border">
            <p className="text-3xl font-bold text-primary">4.9</p>
            <p className="text-sm text-muted-foreground mt-1">Durchschnitt</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-primary">98%</p>
            <p className="text-sm text-muted-foreground mt-1">Weiterempfehlung</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Reviews;

// SEO and Schema.org utilities for ZOZO Burger

export const generateRestaurantSchema = (location) => {
  return {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "name": location.name,
    "image": "https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg",
    "description": "ZOZO Burger - Premium Burger, Pizza, Pasta & More. Frisch zubereitet mit besten Zutaten.",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": location.address,
      "addressLocality": location.city,
      "postalCode": location.postal_code,
      "addressCountry": "DE"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": location.lat,
      "longitude": location.lng
    },
    "telephone": location.phone,
    "email": location.email,
    "servesCuisine": ["Burger", "Pizza", "Pasta", "Fast Food"],
    "priceRange": "€€",
    "openingHoursSpecification": {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
      ],
      "opens": "11:00",
      "closes": "22:45"
    },
    "acceptsReservations": "False",
    "hasMenu": {
      "@type": "Menu",
      "hasMenuSection": [
        {
          "@type": "MenuSection",
          "name": "Burger",
          "description": "Saftige Burger mit frischen Zutaten"
        },
        {
          "@type": "MenuSection",
          "name": "Pizza",
          "description": "Knusprige Pizza mit reichhaltiger Auswahl"
        },
        {
          "@type": "MenuSection",
          "name": "Pasta",
          "description": "Italienische Pasta-Gerichte"
        }
      ]
    }
  };
};

export const generateMenuItemSchema = (item, category) => {
  return {
    "@context": "https://schema.org",
    "@type": "MenuItem",
    "name": item.name,
    "description": item.description || `${item.name} aus der Kategorie ${category}`,
    "offers": {
      "@type": "Offer",
      "price": item.price_normal || item.price_medium,
      "priceCurrency": "EUR"
    },
    "image": item.image_url,
    "menuAddOn": category
  };
};

export const generateOrganizationSchema = () => {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "ZOZO Burger",
    "alternateName": "ZOZO Burger - Burger, Pizza, Pasta & More",
    "url": "https://zozo-fix.preview.emergentagent.com",
    "logo": "https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg",
    "description": "Premium Burger-Lieferservice mit zwei Standorten in Rellingen und Henstedt-Ulzburg. Schnell, heiß & zuverlässig geliefert.",
    "address": [
      {
        "@type": "PostalAddress",
        "streetAddress": "Möwenstraße 2",
        "addressLocality": "Rellingen",
        "postalCode": "25462",
        "addressCountry": "DE"
      },
      {
        "@type": "PostalAddress",
        "streetAddress": "Edisonstraße 11",
        "addressLocality": "Henstedt-Ulzburg",
        "postalCode": "24558",
        "addressCountry": "DE"
      }
    ],
    "sameAs": [
      // Add social media links when available
    ]
  };
};

export const injectStructuredData = (data) => {
  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.text = JSON.stringify(data);
  
  // Remove existing schema script if any
  const existing = document.querySelector('script[type="application/ld+json"]');
  if (existing) {
    existing.remove();
  }
  
  document.head.appendChild(script);
};

export const updateMetaTags = ({ title, description, image, url }) => {
  // Update title
  document.title = title || 'ZOZO Burger - Premium Burger, Pizza, Pasta & More';
  
  // Update meta description
  let metaDescription = document.querySelector('meta[name="description"]');
  if (!metaDescription) {
    metaDescription = document.createElement('meta');
    metaDescription.name = 'description';
    document.head.appendChild(metaDescription);
  }
  metaDescription.content = description || 'Premium Burger, Pizza, Pasta & More. Schnell, heiß & zuverlässig geliefert in Rellingen und Henstedt-Ulzburg.';
  
  // Update Open Graph tags
  const ogTags = [
    { property: 'og:title', content: title || 'ZOZO Burger' },
    { property: 'og:description', content: description || 'Premium Burger, Pizza, Pasta & More' },
    { property: 'og:image', content: image || 'https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg' },
    { property: 'og:url', content: url || window.location.href },
    { property: 'og:type', content: 'website' }
  ];
  
  ogTags.forEach(({ property, content }) => {
    let tag = document.querySelector(`meta[property="${property}"]`);
    if (!tag) {
      tag = document.createElement('meta');
      tag.setAttribute('property', property);
      document.head.appendChild(tag);
    }
    tag.content = content;
  });
};

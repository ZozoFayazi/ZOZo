{
  "brand_meta": {
    "project": "ZOZO Burger",
    "tagline": "BURGER · PIZZA · PASTA & MORE",
    "brand_attributes": ["premium", "bold", "cinematic", "German-local", "fast yet refined"],
    "wow_strategy": "Fuse editorial magazine aesthetics with boutique fashion polish: near-black canvas, high-contrast off‑white type, disciplined red accents, moody food photography, and subtle parallax."
  },
  "palette": {
    "primary_red": "#B00020",
    "primary_red_alt": "#990000",
    "bg_near_black": "#0D0D0F",
    "bg_elevated": "#121214",
    "fg_off_white": "#F5F5F5",
    "fg_muted": "#B6B6B6",
    "border": "#232326",
    "success": "#2FB67B",
    "warning": "#E6A700",
    "error": "#E5484D",
    "accent_warm_gray": "#2A2A2E",
    "accent_coal": "#1A1A1C",
    "gradient_accent": ["#0B0B0C", "#131315", "#0F0F11"],
    "notes": [
      "Red is used only for primary CTAs, prices, active states, and small highlights.",
      "Keep reading areas on solid near‑black. Gradients only for hero/section dividers (<=20% viewport).",
      "Respect GRADIENT RESTRICTION RULE (no purple/pink, no saturated stacks)."
    ]
  },
  "css_design_tokens": {
    "instructions": "Place in /app/frontend/src/index.css under @layer base to override theme tokens. Keep .dark values identical to root for this site (always dark).",
    "root_variables": "@layer base {\n  :root, .dark {\n    --background: 240 6% 4%; /* #0D0D0F */\n    --foreground: 0 0% 96%; /* #F5F5F5 */\n    --card: 240 6% 6%; /* #121214 */\n    --card-foreground: 0 0% 96%;\n    --popover: 240 6% 6%;\n    --popover-foreground: 0 0% 96%;\n    --primary: 351 100% 35%; /* #B00020 */\n    --primary-foreground: 0 0% 98%;\n    --secondary: 240 5% 16%; /* #2A2A2E */\n    --secondary-foreground: 0 0% 96%;\n    --muted: 240 4% 14%; /* #232326 */\n    --muted-foreground: 0 0% 72%; /* #B6B6B6 */\n    --accent: 240 5% 8%;  /* #1A1A1C */\n    --accent-foreground: 0 0% 96%;\n    --destructive: 358 76% 60%; /* #E5484D */\n    --destructive-foreground: 0 0% 98%;\n    --border: 240 5% 14%;\n    --input: 240 5% 14%;\n    --ring: 351 100% 35%; /* red ring for focus */\n    --radius: 0.6rem;\n  }\n}\n",
    "utilities": [
      "Apply subtle noise overlay to large sections: bg-[radial-gradient(60%_120%_at_50%_0%,rgba(255,255,255,0.04),rgba(0,0,0,0))] before:content-[''] before:absolute before:inset-0 before:bg-[url('/noise.png')] before:opacity-20 before:pointer-events-none",
      "Never use transition: all; restrict per-property (colors, opacity, box-shadow)."
    ]
  },
  "typography": {
    "pairing": {
      "headings": "Playfair Display",
      "body_ui": "Chivo"
    },
    "import": "Use Google Fonts. Example in index.html: <link href=\"https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Chivo:wght@300;400;500;700&display=swap\" rel=\"stylesheet\">",
    "tailwind_presets": {
      "classes": {
        "h1": "font-serif text-4xl sm:text-5xl lg:text-6xl tracking-tight leading-[1.1]",
        "h2": "font-serif text-base sm:text-lg font-semibold tracking-wide uppercase text-muted-foreground",
        "body": "font-sans text-base sm:text-sm leading-relaxed text-foreground",
        "eyebrow": "font-sans text-xs tracking-[0.22em] uppercase text-muted-foreground"
      },
      "notes": "Headings use Playfair Display with dramatic tight leading; UI elements use Chivo for clarity and German diacritics."
    }
  },
  "layout_grid": {
    "container": "max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8",
    "grid_system": [
      "Mobile-first. Use 4-col grid on mobile (gap-4), 8-col on md, 12-col on lg.",
      "Hero: split layout with editorial text column (5/12) and parallax image stack (7/12) on lg; single column on mobile.",
      "Menu: bento grid with asymmetric spans: lg:grid-cols-12; feature cards col-span-6, standard items col-span-3-4."
    ],
    "spacing": "Use 2x perceived spacing: section py-16 md:py-24; between blocks gap-10 md:gap-14."
  },
  "page_structure": {
    "routes": ["/", "/menu", "/locations", "/about", "/order", "/admin"],
    "hero": {
      "style": "Dark editorial with cinematic photography, subtle diagonal gradient and noise (<=20% viewport).",
      "content": [
        "Top-left: eyebrow 'Rellingen • Henstedt-Ulzburg'",
        "H1: 'ZOZO BURGER' in Playfair Display",
        "H2 subline: 'BURGER · PIZZA · PASTA & MORE'",
        "Primary CTA: 'Jetzt bestellen' (red) + Secondary: 'Speisekarte ansehen' (ghost)"
      ],
      "micro_interactions": [
        "Parallax on hero images (slight translateY 6–14px)",
        "CTA hover: color/shadow only (no scale beyond 1.02)",
        "Noise overlay fade-in on load"
      ]
    },
    "menu": {
      "filters": ["Tabs: Burger, Pizza, Pasta, Specials", "Search: Command palette", "Location toggle: Rellingen / Henstedt-Ulzburg"],
      "cards": "Large feature cards for hero dishes; standard product cards with imagery, price, spicy/veg badges, add-to-cart.",
      "empty_state": "Muted card with 'Gericht nicht gefunden' and a 'Alle anzeigen' button"
    },
    "locations": {
      "structure": ["Map + address + opening hours", "Delivery zones with tags", "Order CTA per location"],
      "maps": "react-leaflet with dark tiles; fallback to Google Maps embed"
    },
    "about": {
      "story": "Short brand story focused on craft and ingredients; accordion for sourcing and values",
      "media": "Carousel of photography with lazy loading"
    },
    "order_flow": [
      "Step 1: Location select (Sheet or Dialog)",
      "Step 2: Choose items (menu grid)",
      "Step 3: Cart drawer (Sheet right) with upsells",
      "Step 4: Checkout (Dialog or dedicated page)"
    ],
    "admin": [
      "Orders table with tabs (Open, In-Progress, Delivered)",
      "Product management with Dialog forms",
      "Analytics mini-cards and charts (Recharts or D3 minimal)"
    ]
  },
  "components": {
    "header_nav": {
      "use": ["/app/frontend/src/components/ui/navigation-menu.jsx", "/app/frontend/src/components/ui/sheet.jsx", "/app/frontend/src/components/ui/button.jsx"],
      "notes": "Sticky top, backdrop-blur, thin bottom border. Mobile uses Sheet for off-canvas nav.",
      "classes": "sticky top-0 z-50 backdrop-blur supports-[backdrop-filter]:bg-black/30 border-b border-border",
      "data_testid": "header-nav"
    },
    "hero_cta": {
      "use": ["/app/frontend/src/components/ui/button.jsx", "/app/frontend/src/components/ui/badge.jsx"],
      "primary_button": "btn-primary: bg-primary text-primary-foreground rounded-[10px] shadow-[0_6px_28px_rgba(176,0,32,0.35)] hover:bg-[#990000] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background",
      "secondary_button": "btn-ghost: border border-border text-foreground/90 hover:bg-secondary",
      "data_testids": ["hero-primary-cta-button", "hero-secondary-cta-button"]
    },
    "menu_filters": {
      "use": ["/app/frontend/src/components/ui/tabs.jsx", "/app/frontend/src/components/ui/command.jsx", "/app/frontend/src/components/ui/toggle-group.jsx"],
      "pattern": "Tabs for category with underline indicator; Command for fuzzy search; ToggleGroup for location.",
      "data_testids": ["menu-tabs", "menu-search", "location-toggle"]
    },
    "menu_card": {
      "use": ["/app/frontend/src/components/ui/card.jsx", "/app/frontend/src/components/ui/badge.jsx", "/app/frontend/src/components/ui/button.jsx", "/app/frontend/src/components/ui/tooltip.jsx"],
      "layout": "Image top with 3:2 ratio (aspect-ratio), name and short copy, price aligned right, Add button.",
      "classes": "group relative overflow-hidden bg-card border border-border rounded-xl hover:border-primary/40 transition-colors",
      "micro": "On hover: image translate-y-[-2px] brightness-110; badge subtle glow",
      "data_testids": ["menu-item-card", "add-to-cart-button"]
    },
    "cart_drawer": {
      "use": ["/app/frontend/src/components/ui/sheet.jsx", "/app/frontend/src/components/ui/scroll-area.jsx", "/app/frontend/src/components/ui/separator.jsx", "/app/frontend/src/components/ui/button.jsx", "/app/frontend/src/components/ui/input.jsx", "/app/frontend/src/components/ui/sonner.jsx"],
      "pattern": "Right-aligned Sheet with line items, quantity steppers, voucher input, subtotal, delivery note.",
      "data_testids": ["cart-open-button", "cart-sheet", "checkout-button"]
    },
    "locations_block": {
      "use": ["/app/frontend/src/components/ui/card.jsx", "/app/frontend/src/components/ui/button.jsx"],
      "pattern": "Two cards with map embeds; CTA per location.",
      "data_testids": ["rellingen-card", "henstedt-card", "map-embed"]
    },
    "about_media": {
      "use": ["/app/frontend/src/components/ui/carousel.jsx", "/app/frontend/src/components/ui/accordion.jsx"],
      "data_testids": ["about-carousel", "about-accordion"]
    },
    "admin_tables": {
      "use": ["/app/frontend/src/components/ui/table.jsx", "/app/frontend/src/components/ui/tabs.jsx", "/app/frontend/src/components/ui/select.jsx", "/app/frontend/src/components/ui/popover.jsx", "/app/frontend/src/components/ui/calendar.jsx", "/app/frontend/src/components/ui/dialog.jsx", "/app/frontend/src/components/ui/toast.jsx"],
      "data_testids": ["orders-table", "orders-status-tabs", "product-dialog"]
    },
    "feedback": {
      "use": ["/app/frontend/src/components/ui/sonner.jsx", "/app/frontend/src/components/ui/skeleton.jsx", "/app/frontend/src/components/ui/progress.jsx"],
      "notes": "Use sonner for toasts; skeletons for image/card loading; progress during order placement.",
      "data_testids": ["toast-success", "toast-error", "loading-skeleton"]
    }
  },
  "micro_interactions_and_motion": {
    "lib": "framer-motion",
    "install": "npm i framer-motion @studio-freight/lenis",
    "principles": [
      "Entrance: fade + 12–24px translate over 420–560ms, ease-out",
      "Hover: subtle lift (translate-y-[-2px]) and shadow/brightness shift; avoid aggressive scale",
      "Parallax: use small ranges (6–14px) for hero layers with Lenis smooth scroll",
      "Focus states: 2px red ring with ring-offset for all actionable elements"
    ],
    "example_jsx": "// Hero image motion snippet (use .jsx)\nimport { motion } from 'framer-motion'\n\nexport const ParallaxImage = ({ src, alt }) => (\n  <motion.img\n    src={src}\n    alt={alt}\n    className=\"rounded-xl shadow-2xl\"\n    initial={{ opacity: 0, y: 16 }}\n    animate={{ opacity: 1, y: 0 }}\n    transition={{ duration: 0.56, ease: 'easeOut' }}\n    whileHover={{ y: -2, filter: 'brightness(1.05)' }}\n  />\n)\n"
  },
  "navigation_and_ctas": {
    "primary_cta_label": "Jetzt bestellen",
    "secondary_cta_label": "Speisekarte ansehen",
    "nav_items": [
      {"label": "Menu", "href": "/menu"},
      {"label": "Standorte", "href": "/locations"},
      {"label": "Über uns", "href": "/about"},
      {"label": "Kontakt", "href": "/#contact"}
    ],
    "testing_ids": ["nav-menu-link", "nav-standorte-link", "nav-ueber-link", "nav-kontakt-link", "nav-cart-button"]
  },
  "accessibility_and_seo": {
    "a11y": [
      "WCAG AA contrast on all text; test red on black with at least 4.5:1",
      "Keyboard: all menus/dialogs/sheets must trap focus and be escapable",
      "ARIA labels for cart, search, and map embeds; alt text for all images",
      "Reduced motion: respect prefers-reduced-motion (disable parallax)"
    ],
    "seo": [
      "Semantic landmarks: header, nav, main, section, footer",
      "H1 only on hero, structured H2s for sections",
      "JSON-LD: Restaurant + LocalBusiness for both locations",
      "Optimized <img> with width/height and loading=lazy"
    ]
  },
  "testing_attributes": {
    "rule": "All interactive and key informational elements must include data-testid in kebab-case describing role.",
    "examples": [
      "data-testid=\"menu-search-input\"",
      "data-testid=\"rellingen-order-cta-button\"",
      "data-testid=\"cart-line-item-qty-increase\"",
      "data-testid=\"checkout-confirmation-text\""
    ]
  },
  "images_and_media": {
    "logo": "https://customer-assets.emergentagent.com/job_premium-zozo/artifacts/jd98ser0_IMG_8154.jpeg",
    "hero_notes": "Use one large burger image + stacked pizza/pasta thumbnails for parity. Keep images moody against black. Compress with next-gen formats.",
    "image_urls": [
      {
        "category": "hero-burger",
        "description": "Cinematic stacked cheeseburger on dark background",
        "url": "https://images.unsplash.com/photo-1603508102983-99b101395d1a?auto=format&q=85"
      },
      {
        "category": "feature-burger",
        "description": "Black-bun burger with bacon, glossy reflection",
        "url": "https://images.unsplash.com/photo-1582196016295-f8c8bd4b3a99?auto=format&q=85"
      },
      {
        "category": "pizza",
        "description": "Pizza being sliced on dark table, dramatic light",
        "url": "https://images.unsplash.com/photo-1616141032335-7e6b413f93ec?auto=format&q=85"
      },
      {
        "category": "pizza-oven",
        "description": "Pizza in oven, low light, warm contrast",
        "url": "https://images.unsplash.com/photo-1609281038144-726352964256?auto=format&q=85"
      }
    ],
    "placement": [
      {"section": "hero", "use": "hero-burger"},
      {"section": "menu-specials", "use": "feature-burger"},
      {"section": "menu-pizza", "use": "pizza"},
      {"section": "about-carousel", "use": "pizza-oven"}
    ]
  },
  "component_path": {
    "button": "/app/frontend/src/components/ui/button.jsx",
    "card": "/app/frontend/src/components/ui/card.jsx",
    "tabs": "/app/frontend/src/components/ui/tabs.jsx",
    "command": "/app/frontend/src/components/ui/command.jsx",
    "badge": "/app/frontend/src/components/ui/badge.jsx",
    "sheet": "/app/frontend/src/components/ui/sheet.jsx",
    "navigation_menu": "/app/frontend/src/components/ui/navigation-menu.jsx",
    "accordion": "/app/frontend/src/components/ui/accordion.jsx",
    "carousel": "/app/frontend/src/components/ui/carousel.jsx",
    "table": "/app/frontend/src/components/ui/table.jsx",
    "select": "/app/frontend/src/components/ui/select.jsx",
    "dialog": "/app/frontend/src/components/ui/dialog.jsx",
    "toast": "/app/frontend/src/components/ui/toast.jsx",
    "sonner": "/app/frontend/src/components/ui/sonner.jsx",
    "calendar": "/app/frontend/src/components/ui/calendar.jsx",
    "skeleton": "/app/frontend/src/components/ui/skeleton.jsx",
    "progress": "/app/frontend/src/components/ui/progress.jsx",
    "tooltip": "/app/frontend/src/components/ui/tooltip.jsx",
    "input": "/app/frontend/src/components/ui/input.jsx",
    "separator": "/app/frontend/src/components/ui/separator.jsx",
    "scroll_area": "/app/frontend/src/components/ui/scroll-area.jsx"
  },
  "example_components_js": {
    "Header.jsx": "import React from 'react'\nimport { Button } from './components/ui/button'\nimport { NavigationMenu } from './components/ui/navigation-menu'\n\nexport const Header = () => {\n  return (\n    <header className=\"sticky top-0 z-50 border-b border-border bg-background/70 backdrop-blur\" data-testid=\"header-nav\">\n      <div className=\"max-w-[1200px] mx-auto px-4 h-16 flex items-center justify-between\">\n        <a href=\"/\" className=\"flex items-center gap-3\" data-testid=\"brand-home-link\">\n          <img src=\"/logo.svg\" alt=\"ZOZO Burger\" className=\"h-7 w-auto\" />\n        </a>\n        <nav className=\"hidden md:flex items-center gap-6\">\n          <a href=\"/menu\" className=\"text-sm hover:text-primary\" data-testid=\"nav-menu-link\">Menu</a>\n          <a href=\"/locations\" className=\"text-sm hover:text-primary\" data-testid=\"nav-standorte-link\">Standorte</a>\n          <a href=\"/about\" className=\"text-sm hover:text-primary\" data-testid=\"nav-ueber-link\">Über uns</a>\n          <a href=\"/#contact\" className=\"text-sm hover:text-primary\" data-testid=\"nav-kontakt-link\">Kontakt</a>\n        </nav>\n        <Button className=\"bg-primary hover:bg-[#990000]\" data-testid=\"nav-cart-button\">Warenkorb</Button>\n      </div>\n    </header>\n  )\n}\n",
    "MenuCard.jsx": "import React from 'react'\nimport { Card, CardContent } from './components/ui/card'\nimport { Button } from './components/ui/button'\nimport { Badge } from './components/ui/badge'\n\nexport const MenuCard = ({ item, onAdd }) => {\n  return (\n    <Card className=\"group overflow-hidden bg-card border border-border rounded-xl hover:border-primary/40 transition-colors\" data-testid=\"menu-item-card\">\n      <div className=\"aspect-[3/2] overflow-hidden\">\n        <img src={item.image} alt={item.name} className=\"h-full w-full object-cover group-hover:brightness-110 transition-[filter] duration-300\"/>\n      </div>\n      <CardContent className=\"p-4\">\n        <div className=\"flex items-start justify-between\">\n          <div>\n            <h3 className=\"font-serif text-lg leading-tight\">{item.name}</h3>\n            <p className=\"text-sm text-muted-foreground mt-1\">{item.description}</p>\n            <div className=\"mt-2 flex gap-2\">\n              {item.spicy && <Badge variant=\"secondary\">Scharf</Badge>}\n              {item.veg && <Badge variant=\"secondary\">Vegetarisch</Badge>}\n            </div>\n          </div>\n          <span className=\"text-foreground font-medium\">€{item.price}</span>\n        </div>\n        <Button\n          onClick={() => onAdd(item)}\n          className=\"mt-4 w-full bg-primary hover:bg-[#990000]\"\n          data-testid=\"add-to-cart-button\"\n        >Hinzufügen</Button>\n      </CardContent>\n    </Card>\n  )\n}\n",
    "CartDrawer.jsx": "import React from 'react'\nimport { Sheet, SheetContent } from './components/ui/sheet'\nimport { Button } from './components/ui/button'\nimport { Separator } from './components/ui/separator'\nimport { ScrollArea } from './components/ui/scroll-area'\n\nexport const CartDrawer = ({ open, onOpenChange, items, onCheckout }) => {\n  const subtotal = items.reduce((s, it) => s + it.price * it.qty, 0)\n  return (\n    <Sheet open={open} onOpenChange={onOpenChange}>\n      <SheetContent side=\"right\" className=\"w-[420px] max-w-[100vw]\" data-testid=\"cart-sheet\">\n        <h3 className=\"font-serif text-xl\">Warenkorb</h3>\n        <Separator className=\"my-4\"/>\n        <ScrollArea className=\"h-[60vh]\">\n          <ul className=\"space-y-4\">\n            {items.map((it) => (\n              <li key={it.id} className=\"flex justify-between items-start\">\n                <div>\n                  <p className=\"font-medium\">{it.name} × {it.qty}</p>\n                  <p className=\"text-sm text-muted-foreground\">€{it.price.toFixed(2)}</p>\n                </div>\n                <div className=\"text-right\">€{(it.price * it.qty).toFixed(2)}</div>\n              </li>\n            ))}\n          </ul>\n        </ScrollArea>\n        <Separator className=\"my-4\"/>\n        <div className=\"flex items-center justify-between\">\n          <span className=\"text-muted-foreground\">Zwischensumme</span>\n          <span className=\"font-semibold\">€{subtotal.toFixed(2)}</span>\n        </div>\n        <Button className=\"mt-4 w-full bg-primary hover:bg-[#990000]\" onClick={onCheckout} data-testid=\"checkout-button\">Zur Kasse</Button>\n      </SheetContent>\n    </Sheet>\n  )\n}\n"
  },
  "libraries": {
    "install_commands": [
      "npm i framer-motion @studio-freight/lenis",
      "npm i react-leaflet leaflet",
      "npm i recharts"
    ],
    "map_usage_note": "For react-leaflet, include leaflet CSS in index.html. Use dark tiles (e.g., https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png). Provide <noscript> Google Maps link as fallback.",
    "charts_usage_note": "Use Recharts for admin KPIs: tiny area/line charts with muted grid lines; avoid heavy animations."
  },
  "gradient_and_texture": {
    "allowed": "Only section backgrounds. Example: bg-[radial-gradient(100%_80%_at_50%_0%,#131315,rgba(19,19,21,0))] with a noise overlay.",
    "forbidden": "No saturated purple/pink/blue stacks; never on text blocks; do not exceed 20% viewport coverage; never on small UI elements."
  },
  "buttons_guideline": {
    "style": "Luxury / Elegant",
    "radius": "10px",
    "shadow": "0 6px 28px rgba(176,0,32,0.35)",
    "variants": {
      "primary": "bg-primary text-primary-foreground hover:bg-[#990000] focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
      "secondary": "border border-border text-foreground/90 hover:bg-secondary",
      "ghost": "text-foreground/80 hover:bg-secondary/60"
    },
    "sizes": {"sm": "h-9 px-4", "md": "h-11 px-6", "lg": "h-12 px-8"}
  },
  "unified_spacing_and_shadows": {
    "section_padding": "py-16 md:py-24",
    "card_radius": "rounded-xl",
    "shadow_elevations": {
      "low": "shadow-[0_4px_16px_rgba(0,0,0,0.25)]",
      "med": "shadow-[0_10px_30px_rgba(0,0,0,0.35)]",
      "glow_red": "shadow-[0_6px_28px_rgba(176,0,32,0.35)]"
    }
  },
  "instructions_to_main_agent": [
    "1) Update /app/frontend/src/index.css tokens with css_design_tokens.root_variables (keep @layer).",
    "2) Add Google Fonts link tags for Playfair Display and Chivo to index.html and set tailwind font-family mapping (font-serif to Playfair, font-sans to Chivo).",
    "3) Build Header.jsx, Hero.jsx, MenuCard.jsx, CartDrawer.jsx using provided scaffolds and shadcn components only (no native selects/alerts).",
    "4) Implement hero layout: editorial left column + ParallaxImage stack right. Respect gradient_and_texture rules.",
    "5) Menu page: Tabs + Command search + responsive bento grid. Ensure every interactive item has data-testid.",
    "6) Locations page: two cards with react-leaflet maps and clear CTAs per location.",
    "7) About page: Carousel + Accordion storytelling.",
    "8) Order flow: use Sheet as cart drawer and Dialog for checkout; use Sonner for success/error messages.",
    "9) Admin: Table + Tabs + Select + Calendar filters; Sonner for operations.",
    "10) Motion: add framer-motion entrance and hover animations. Do not use transition: all; specify properties.",
    "11) Accessibility: focus-visible states, aria labels, reduced motion fallback (disable parallax).",
    "12) Performance: compress images, lazy-load non-critical sections, prefetch menu images on hover.",
    "13) SEO: semantic headings, JSON-LD for each location, title/meta per page.",
    "14) Enforce gradient restriction + dark premium palette."
  ],
  "general_ui_ux_design_guidelines_raw": "- You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals."
}

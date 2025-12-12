{
  "version": "1.0",
  "project": "ZOZO Burger – Million‑Dollar Dark Premium Redesign",
  "brand_attributes": [
    "cinematic",
    "premium",
    "bold",
    "edgy",
    "trustworthy",
    "fast"
  ],
  "design_personality": {
    "fusion_style": "Luxury Brutalism x Glassmorphism x Cinematic Depth",
    "explanation": "Use a raw, high-contrast grid and oversized type (brutalist cues), layered with frosted-glass surfaces for cards, modals and nav. Add cinematic light falloffs, subtle radial glows, and parallax depth using existing .glass, .gradient-bg, .card-tilt, and noise overlays."
  },
  "color_system": {
    "base_tokens_hsl": {
      "--background": "240 6% 4%",
      "--foreground": "0 0% 96%",
      "--card": "240 6% 6%",
      "--card-foreground": "0 0% 96%",
      "--popover": "240 6% 6%",
      "--popover-foreground": "0 0% 96%",
      "--primary": "351 100% 35%",
      "--primary-foreground": "0 0% 98%",
      "--secondary": "240 5% 16%",
      "--secondary-foreground": "0 0% 96%",
      "--muted": "240 4% 14%",
      "--muted-foreground": "0 0% 72%",
      "--accent": "240 5% 8%",
      "--accent-foreground": "0 0% 96%",
      "--destructive": "358 76% 60%",
      "--destructive-foreground": "0 0% 98%",
      "--border": "240 5% 14%",
      "--input": "240 5% 14%",
      "--ring": "351 100% 35%",
      "--radius": "0.6rem"
    },
    "semantic": {
      "info": "210 92% 56%",
      "success": "152 63% 43%",
      "warning": "38 92% 58%",
      "highlight": "351 100% 42%",
      "gold_accent": "44 92% 60%"
    },
    "usage": {
      "primary": "Brand crimson (HSL 351/100/35) for CTAs, price badges, active states.",
      "secondary": "Panels, headers, and nav backgrounds.",
      "accent": "Backdrops behind glass panels; use with noise overlay.",
      "muted": "Dividers, lines, and quiet UI.",
      "gold_accent": "Subtle luxury hint for details (tiny borders, icons) only."
    },
    "contrast": "Minimum 4.5:1 for text; buttons must meet AA."
  },
  "gradients": {
    "allowed": [
      "Hero radial background glow using brand crimson at 10–15% opacity over dark charcoal",
      "Section separators as very subtle diagonal washes (opacity < 0.12)",
      "Large decorative shapes only (no text areas)"
    ],
    "prohibited": [
      "Any dark/saturated gradient combos like purple→pink, green→blue, red→pink",
      "Gradients on small UI (<100px) or text-heavy blocks",
      "Gradient logos, testimonials, or footer backgrounds",
      ">20% viewport gradient coverage"
    ],
    "enforcement": "If a gradient risks readability or exceeds 20% viewport, replace with solid tokens and keep noise overlay for richness."
  },
  "typography": {
    "fonts": {
      "display_serif": "'Playfair Display', Georgia, serif",
      "body_sans": "'Chivo', system-ui, -apple-system, sans-serif",
      "numeric_alt": "'Space Grotesk', ui-sans-serif, system-ui"
    },
    "load_via_google": [
      "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&display=swap",
      "https://fonts.googleapis.com/css2?family=Chivo:wght@400;500;600;700&display=swap",
      "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&display=swap"
    ],
    "scale": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl",
      "h2": "text-base sm:text-lg",
      "body": "text-sm sm:text-base",
      "small": "text-xs sm:text-sm"
    },
    "usage": {
      "h1": "Use heading-1 utility from App.css on hero titles.",
      "h2": "Use heading-2 for section leads and category headers.",
      "numerals": "Use Space Grotesk for prices and counts via font-[\'Space_Grotesk\'] if added, otherwise keep Chivo."
    }
  },
  "tokens": {
    "elevations": {
      "e-0": "shadow-none",
      "e-1": "shadow-[0_2px_10px_rgba(0,0,0,0.25)]",
      "e-2": "shadow-[0_8px_30px_rgba(0,0,0,0.35)]",
      "e-3": "shadow-[0_16px_60px_rgba(0,0,0,0.45)]"
    },
    "radii": {
      "sm": "0.5rem",
      "md": "0.6rem",
      "lg": "1rem",
      "xl": "1.25rem"
    },
    "spacing": "Use 1.5x–2x default Tailwind spacing relative to typical app UIs. Section padding: py-14 md:py-20; card gap: gap-6 md:gap-8; grid gutters: gap-x-6 gap-y-10."
  },
  "layout_grid": {
    "mobile_first": true,
    "containers": {
      "default": "container-custom",
      "full_bleed": "w-full"
    },
    "hero": {
      "structure": "grid grid-cols-1 lg:grid-cols-12 gap-8 items-center",
      "left": "lg:col-span-6 space-y-5",
      "right": "lg:col-span-6"
    },
    "menu_bento": {
      "structure": "grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4 md:gap-6",
      "card": "glass card-tilt gradient-border p-4 sm:p-5"
    },
    "product_grid": {
      "structure": "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8",
      "card": "glass-light border rounded-xl overflow-hidden hover:border-primary/40 transition-colors"
    },
    "checkout": {
      "structure": "grid grid-cols-1 lg:grid-cols-3 gap-8",
      "form": "lg:col-span-2",
      "summary": "lg:col-span-1"
    }
  },
  "buttons": {
    "style": "Luxury / Elegant",
    "radius": "8–12px",
    "variants": {
      "primary": "btn-primary glow-primary",
      "secondary": "btn-secondary",
      "ghost": "px-4 py-3 rounded-xl border border-transparent text-muted-foreground hover:text-foreground hover:border-border transition-colors"
    },
    "sizes": {
      "sm": "px-4 py-2 text-sm",
      "md": "px-6 py-3 text-base",
      "lg": "px-8 py-4 text-base"
    },
    "focus": "ring-2 ring-[hsl(var(--ring))] ring-offset-2 ring-offset-[hsl(var(--background))]",
    "accessibility": "All buttons must include a data-testid that describes action, e.g., data-testid=\"add-to-cart-button\"."
  },
  "components": {
    "navigation": {
      "paths": [
        "./components/ui/navigation-menu",
        "./components/ui/drawer",
        "./components/ui/button\n"
      ],
      "pattern": "Split branding left, actions (Location, Order Type, Cart) right. Mobile: Drawer opens a glass sheet with large targets.",
      "classes": "sticky top-0 z-40 backdrop-blur-xl glass border-b",
      "micro": [
        "Logo subtle scale-in on load (animate-scale-in)",
        "Underline reveal on hover with border-primary/50"
      ],
      "testing": [
        "data-testid=\"nav-logo-link\"",
        "data-testid=\"nav-location-button\"",
        "data-testid=\"nav-cart-button\""
      ]
    },
    "hero": {
      "content": "Oversized headline, short subcopy, primary CTA, and supporting CTA. Right side: parallax food photography in .parallax-wrapper with noise overlay.",
      "classes": "relative gradient-bg noise-overlay py-16 sm:py-20 lg:py-28",
      "testing": [
        "data-testid=\"hero-title\"",
        "data-testid=\"hero-primary-cta-button\"",
        "data-testid=\"hero-secondary-cta-button\""
      ]
    },
    "menu_categories_bento": {
      "paths": [
        "./components/ui/card",
        "./components/ui/tabs",
        "./components/ui/badge"
      ],
      "pattern": "Bento grid of categories: Burger, Pizza, Pasta, Sides, Salads, Desserts. Each card shows photograph overlay with glass label; hover lifts (card-tilt).",
      "testing": [
        "data-testid=\"category-card-burger\"",
        "data-testid=\"category-card-pizza\"",
        "data-testid=\"category-card-pasta\""
      ]
    },
    "product_card": {
      "paths": ["./components/ui/card", "./components/ui/button", "./components/ui/badge"],
      "pattern": "Image top with image-overlay, title + description, price on right, Add button.",
      "testing": [
        "data-testid=\"product-card\"",
        "data-testid=\"product-add-button\"",
        "data-testid=\"product-price\""
      ]
    },
    "customizer": {
      "paths": [
        "./components/ui/dialog",
        "./components/ui/radio-group",
        "./components/ui/slider",
        "./components/ui/select",
        "./components/ui/checkbox",
        "./components/ui/tabs",
        "./components/ui/scroll-area"
      ],
      "pattern": "Dialog with tabs (Bun, Patty, Cheese, Extras, Menu Upgrade). Radio and checkbox groups; sliders for heat/sauce. Summary footer with sticky glass bar for price and Add to cart.",
      "testing": [
        "data-testid=\"customizer-dialog\"",
        "data-testid=\"customizer-tab-bun\"",
        "data-testid=\"customizer-add-to-cart-button\""
      ]
    },
    "cart": {
      "paths": ["./components/ui/sheet", "./components/ui/button", "./components/ui/scroll-area"],
      "pattern": "Right Sheet shows items with quantity controls, price breakdown, delivery fee, promo code input, Checkout button.",
      "testing": [
        "data-testid=\"cart-sheet\"",
        "data-testid=\"cart-checkout-button\""
      ]
    },
    "checkout": {
      "paths": [
        "./components/ui/form",
        "./components/ui/input",
        "./components/ui/select",
        "./components/ui/radio-group",
        "./components/ui/calendar",
        "./components/ui/textarea",
        "./components/ui/sonner"
      ],
      "pattern": "Multi-step form (Address → Delivery Time → Payment). Use shadcn Calendar when scheduling. Show live summary card.",
      "testing": [
        "data-testid=\"checkout-form\"",
        "data-testid=\"checkout-submit-button\"",
        "data-testid=\"payment-method-radio\""
      ]
    },
    "toasts": {
      "paths": ["./components/ui/sonner"],
      "usage": "Use for add-to-cart success, errors, and network retry."
    }
  },
  "microinteractions_and_motion": {
    "library": "framer-motion",
    "principles": [
      "Entrance: 250–600ms, bezier (0.16, 1, 0.3, 1)",
      "Hover: 120–200ms, subtle lift and shadow",
      "Press: 80ms depress, scale 0.98",
      "Scroll: mild parallax on hero imagery",
      "No universal transition: only per element (color, opacity, shadow)"
    ],
    "examples": {
      "fade_and_lift": "<motion.div initial={{opacity:0, y:24}} whileInView={{opacity:1, y:0}} viewport={{ once: true, amount: 0.4 }} transition={{ duration: 0.6, ease: [0.16,1,0.3,1] }} />",
      "hover_lift": "className=\"card-tilt\" plus whileHover={{ y: -6, scale: 1.02 }}"
    }
  },
  "accessibility": {
    "focus": "Use focus-visible rings; maintain 4.5:1 contrast.",
    "touch_targets": ">= 44x44px on mobile",
    "reduced_motion": "Respect prefers-reduced-motion; disable parallax and heavy animations",
    "screen_reader": "Use aria-labels for buttons/icons; images require alt text"
  },
  "libraries_and_setup": {
    "install": [
      "npm i framer-motion",
      "npm i lenis --save  # optional smooth scroll",
      "npm i @react-three/fiber @react-three/drei three --save  # optional 3D hero asset"
    ],
    "usage_notes": [
      "Prefer framer-motion for controlled entrance/hover. Limit Three.js to one lightweight scene if used.",
      "Use ./components/ui/sonner for toasts (already present)."
    ]
  },
  "example_code_snippets": {
    "hero_section.jsx": "import React from 'react';\nimport { Button } from './components/ui/button';\nimport { motion } from 'framer-motion';\n\nexport default function Hero() {\n  return (\n    <section className=\"relative gradient-bg noise-overlay\" aria-label=\"ZOZO Burger hero\">\n      <div className=\"container-custom py-16 sm:py-20 lg:py-28\">\n        <div className=\"grid grid-cols-1 lg:grid-cols-12 gap-8 items-center\">\n          <div className=\"lg:col-span-6 space-y-5\">\n            <p className=\"eyebrow\">Rellingen • Henstedt-Ulzburg</p>\n            <h1 className=\"heading-1\" data-testid=\"hero-title\">Burgers that hit different.</h1>\n            <p className=\"text-base text-muted-foreground max-w-xl\">Crafted buns, flame-kissed patties, and cinematic flavors. Order now for delivery or pickup.</p>\n            <div className=\"flex items-center gap-3\">\n              <Button className=\"btn-primary glow-primary\" data-testid=\"hero-primary-cta-button\">Order Now</Button>\n              <Button variant=\"outline\" className=\"btn-secondary\" data-testid=\"hero-secondary-cta-button\">Explore Menu</Button>\n            </div>\n          </div>\n\n          <div className=\"lg:col-span-6\">\n            <div className=\"parallax-wrapper rounded-2xl overflow-hidden border border-white/5\">\n              <motion.img\n                initial={{ scale: 1.02, opacity: 0 }}\n                animate={{ scale: 1, opacity: 1 }}\n                transition={{ duration: 0.8, ease: [0.16,1,0.3,1] }}\n                src=\"REPLACE_WITH_HERO_BURGER_URL\"\n                alt=\"Signature burger on dark background\"\n                className=\"parallax-image w-full h-full object-cover\"\n                data-testid=\"hero-image\"\n              />\n            </div>\n          </div>\n        </div>\n      </div>\n    </section>\n  );\n}",
    "menu_card.jsx": "import React from 'react';\nimport { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';\nimport { Button } from './components/ui/button';\n\nexport function ProductCard({ product }) {\n  return (\n    <Card className=\"glass-light border rounded-xl overflow-hidden\" data-testid=\"product-card\">\n      <div className=\"image-overlay\">\n        <img src={product.image} alt={product.name} className=\"w-full h-48 object-cover\" />\n      </div>\n      <CardHeader className=\"flex flex-row items-start justify-between p-5\">\n        <CardTitle className=\"text-lg font-semibold\">{product.name}</CardTitle>\n        <span className=\"text-foreground font-semibold\" data-testid=\"product-price\">€{product.price}</span>\n      </CardHeader>\n      <CardContent className=\"p-5 pt-0\">\n        <p className=\"text-sm text-muted-foreground line-clamp-2\">{product.description}</p>\n        <div className=\"mt-4\">\n          <Button className=\"btn-primary w-full\" data-testid=\"product-add-button\">Customize & Add</Button>\n        </div>\n      </CardContent>\n    </Card>\n  );\n}",
    "customizer_dialog.jsx": "import React from 'react';\nimport { Dialog, DialogContent, DialogHeader, DialogTitle } from './components/ui/dialog';\nimport { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs';\nimport { RadioGroup, RadioGroupItem } from './components/ui/radio-group';\nimport { Checkbox } from './components/ui/checkbox';\nimport { Slider } from './components/ui/slider';\nimport { ScrollArea } from './components/ui/scroll-area';\nimport { Button } from './components/ui/button';\n\nexport function CustomizerDialog({ open, onOpenChange }) {\n  return (\n    <Dialog open={open} onOpenChange={onOpenChange}>\n      <DialogContent className=\"glass max-w-2xl\" data-testid=\"customizer-dialog\">\n        <DialogHeader>\n          <DialogTitle>Build your Burger</DialogTitle>\n        </DialogHeader>\n        <Tabs defaultValue=\"bun\" className=\"mt-2\">\n          <TabsList>\n            <TabsTrigger value=\"bun\" data-testid=\"customizer-tab-bun\">Bun</TabsTrigger>\n            <TabsTrigger value=\"patty\">Patty</TabsTrigger>\n            <TabsTrigger value=\"extras\">Extras</TabsTrigger>\n            <TabsTrigger value=\"menu\">Menu</TabsTrigger>\n          </TabsList>\n\n          <TabsContent value=\"bun\">\n            <RadioGroup defaultValue=\"brioche\" className=\"grid grid-cols-2 gap-3 mt-4\">\n              <label className=\"flex items-center gap-2 border rounded-lg p-3\">\n                <RadioGroupItem value=\"brioche\" />\n                <span>Brioche</span>\n              </label>\n              <label className=\"flex items-center gap-2 border rounded-lg p-3\">\n                <RadioGroupItem value=\"glutenfree\" />\n                <span>Gluten Free</span>\n              </label>\n            </RadioGroup>\n          </TabsContent>\n\n          <TabsContent value=\"extras\">\n            <ScrollArea className=\"h-56 mt-4\">\n              <label className=\"flex items-center gap-2 py-2\">\n                <Checkbox />\n                <span>Double Cheese</span>\n              </label>\n              <label className=\"flex items-center gap-2 py-2\">\n                <Checkbox />\n                <span>Crispy Bacon</span>\n              </label>\n              <div className=\"mt-4\">\n                <p className=\"text-sm text-muted-foreground\">Heat</p>\n                <Slider defaultValue={[20]} max={100} step={10} />\n              </div>\n            </ScrollArea>\n          </TabsContent>\n        </Tabs>\n\n        <div className=\"sticky bottom-0 mt-4 -mx-6 px-6 py-4 glass-light border-t backdrop-blur\">\n          <div className=\"flex items-center justify-between\">\n            <span className=\"font-semibold\">€12.90</span>\n            <Button className=\"btn-primary\" data-testid=\"customizer-add-to-cart-button\">Add to cart</Button>\n          </div>\n        </div>\n      </DialogContent>\n    </Dialog>\n  );\n}",
    "cart_sheet.jsx": "import React from 'react';\nimport { Sheet, SheetContent, SheetHeader, SheetTitle } from './components/ui/sheet';\nimport { ScrollArea } from './components/ui/scroll-area';\nimport { Button } from './components/ui/button';\n\nexport function CartSheet({ open, onOpenChange, items = [] }) {\n  return (\n    <Sheet open={open} onOpenChange={onOpenChange}>\n      <SheetContent side=\"right\" className=\"glass w-[420px] max-w-full\" data-testid=\"cart-sheet\">\n        <SheetHeader>\n          <SheetTitle>Your order</SheetTitle>\n        </SheetHeader>\n        <ScrollArea className=\"h-[60vh] mt-4\">\n          {items.length === 0 ? (\n            <p className=\"text-muted-foreground\">Your cart is empty.</p>\n          ) : (\n            <ul className=\"space-y-4\">\n              {items.map((it) => (\n                <li key={it.id} className=\"flex items-center justify-between\">\n                  <div>\n                    <p className=\"font-medium\">{it.name}</p>\n                    <p className=\"text-sm text-muted-foreground\">x{it.qty}</p>\n                  </div>\n                  <span>€{(it.price * it.qty).toFixed(2)}</span>\n                </li>\n              ))}\n            </ul>\n          )}\n        </ScrollArea>\n        <div className=\"mt-6\">\n          <Button className=\"btn-primary w-full\" data-testid=\"cart-checkout-button\">Checkout</Button>\n        </div>\n      </SheetContent>\n    </Sheet>\n  );\n}",
    "toast_usage.js": "import { Toaster, toast } from './components/ui/sonner';\n\nexport function AppToaster() {\n  return <Toaster richColors position=\"top-right\" />;\n}\n\nexport function notifyAdded(name) {\n  toast.success(`${name} added to cart`, { duration: 1800 });\n}"
  },
  "testing_ids_policy": {
    "rule": "All interactive and key informational elements MUST include data-testid using kebab-case describing the element's role.",
    "examples": [
      "data-testid=\"nav-cart-button\"",
      "data-testid=\"menu-category-tabs\"",
      "data-testid=\"product-add-button\"",
      "data-testid=\"checkout-submit-button\"",
      "data-testid=\"error-message\""
    ]
  },
  "image_urls": [
    {
      "category": "hero",
      "use": "Primary hero burger image (right column parallax)",
      "url": "https://images.unsplash.com/photo-1634737119182-4d09e1305ba7?crop=entropy&cs=srgb&fm=jpg&q=85",
      "alt": "Signature burger with knife on dark background"
    },
    {
      "category": "burger-feature",
      "use": "Category tile or promo banner",
      "url": "https://images.unsplash.com/photo-1603508102983-99b101395d1a?crop=entropy&cs=srgb&fm=jpg&q=85",
      "alt": "Burger close-up on dark surface"
    },
    {
      "category": "pizza-category",
      "use": "Pizza category tile",
      "url": "https://images.unsplash.com/photo-1612040906977-1110aa1bdb6f?crop=entropy&cs=srgb&fm=jpg&q=85",
      "alt": "Black dough pizza on black plate"
    },
    {
      "category": "pizza-alt",
      "use": "Secondary pizza banner",
      "url": "https://images.unsplash.com/photo-1624900183034-338974e68033?crop=entropy&cs=srgb&fm=jpg&q=85",
      "alt": "Rustic pizza with greens on dark"
    },
    {
      "category": "pasta-category",
      "use": "Pasta category tile",
      "url": "https://images.unsplash.com/photo-1532939624-3af1308db9a5?crop=entropy&cs=srgb&fm=jpg&q=85",
      "alt": "Pasta twirled on fork over dark background"
    }
  ],
  "component_path": {
    "button": "./components/ui/button",
    "card": "./components/ui/card",
    "tabs": "./components/ui/tabs",
    "badge": "./components/ui/badge",
    "dialog": "./components/ui/dialog",
    "radio_group": "./components/ui/radio-group",
    "slider": "./components/ui/slider",
    "select": "./components/ui/select",
    "checkbox": "./components/ui/checkbox",
    "scroll_area": "./components/ui/scroll-area",
    "sheet": "./components/ui/sheet",
    "form": "./components/ui/form",
    "input": "./components/ui/input",
    "textarea": "./components/ui/textarea",
    "calendar": "./components/ui/calendar",
    "navigation_menu": "./components/ui/navigation-menu",
    "sonner": "./components/ui/sonner"
  },
  "instructions_to_main_agent": [
    "Keep the dark premium palette from index.css. Do not globally center the app container. Use container-custom for widths.",
    "Use shadcn components only for interactive primitives (no raw HTML dropdowns, menus, toasts, calendars).",
    "Adhere to gradient restriction: use only subtle hero/section background washes (<=20% viewport).",
    "Every actionable element must receive data-testid reflecting its role.",
    "Adopt the provided grid/layouts and spacing. Mobile-first first, then enhance on md/lg.",
    "Animate entrances with framer-motion and existing App.css animation utilities. Avoid transition: all; animate specific properties only.",
    "Use .glass and .glass-light surfaces for hero panels, cards, nav, drawers. Combine with .noise-overlay for richness.",
    "Cart lives in a right Sheet. Checkout is a 2/3 + 1/3 grid on desktop.",
    "Use Calendar in checkout when scheduling delivery/pickup.",
    "Include <AppToaster/> at App root and use toast.success/info/error for feedback.",
    "Images: use the provided URLs for hero and category tiles. Keep alt text descriptive."
  ]
}


<General UI UX Design Guidelines>  
    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms
    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text
   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json

 **GRADIENT RESTRICTION RULE**
NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc
NEVER use dark gradients for logo, testimonial, footer etc
NEVER let gradients cover more than 20% of the viewport.
NEVER apply gradients to text-heavy content or reading areas.
NEVER use gradients on small UI elements (<100px width).
NEVER stack multiple gradient layers in the same viewport.

**ENFORCEMENT RULE:**
    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors

**How and where to use:**
   • Section backgrounds (not content backgrounds)
   • Hero section header content. Eg: dark to light to dark color
   • Decorative overlays and accent elements only
   • Hero section with 2-3 mild color
   • Gradients creation can be done for any angle say horizontal, vertical or diagonal

- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**

</Font Guidelines>

- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. 
   
- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.

- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.
   
- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly
    Eg: - if it implies playful/energetic, choose a colorful scheme
           - if it implies monochrome/minimal, choose a black–white/neutral scheme

**Component Reuse:**
	- Prioritize using pre-existing components from src/components/ui when applicable
	- Create new components that match the style and conventions of existing components when needed
	- Examine existing components to understand the project's component patterns before creating new ones

**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component

**Best Practices:**
	- Use Shadcn/UI as the primary component library for consistency and accessibility
	- Import path: ./components/[component-name]

**Export Conventions:**
	- Components MUST use named exports (export const ComponentName = ...)
	- Pages MUST use default exports (export default function PageName() {...})

**Toasts:**
  - Use `sonner` for toasts" 
  - Sonner component are located in `/app/src/components/ui/sonner.tsx`

Use 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.
</General UI UX Design Guidelines>
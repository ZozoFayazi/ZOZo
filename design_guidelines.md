{
  "project": {
    "name": "ZOZO Burger — Final Design Polish",
    "brand_attributes": ["premium", "bold", "emotional", "refined", "confident", "fast"],
    "audience": ["burger lovers", "families", "late-night diners", "foodies in Rellingen & Henstedt-Ulzburg"],
    "app_type": "Premium dark-theme food delivery with ordering, loyalty, and admin dashboards",
    "success_actions": ["fast order start from hero CTA", "location selection clarity", "smooth cart & checkout", "loyalty engagement", "reorder in < 2 taps"]
  },

  "color_system": {
    "tokens_hsl": {
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
    "aux_tokens": {
      "--elev-1": "0 4px 16px rgba(0,0,0,0.35)",
      "--elev-2": "0 10px 30px rgba(0,0,0,0.45)",
      "--elev-3": "0 16px 48px rgba(0,0,0,0.55)",
      "--ring-focus": "0 0 0 2px hsl(var(--ring)), 0 0 0 4px hsl(var(--background))",
      "--btn-radius": "0.75rem",
      "--container-max": "1200px",
      "--space": "clamp(16px, 2.6vw, 28px)"
    },
    "usage": {
      "backgrounds": ["use background = hsl(var(--background))", "cards/popovers use hsl(var(--card))"],
      "accenting": ["primary reserved for actions, price highlights, small dividers", "avoid painting large surfaces solid red"],
      "status": {
        "success": "142 70% 45%",
        "warning": "40 95% 50%",
        "info": "210 90% 60%"
      }
    }
  },

  "gradients_and_texture": {
    "allowed": [
      "hero background: radial-gradient with subtle primary tints on dark",
      "section separators: very light vignette using rgba(176,0,32,0.06)",
      "decorative overlays only (never content blocks)"
    ],
    "samples_css": {
      ".zozo-hero-bg": "background: radial-gradient(circle at 20% 50%, rgba(176,0,32,0.15) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(176,0,32,0.10) 0%, transparent 50%), hsl(var(--background));",
      ".zozo-noise": "position: relative;\n}\n.zozo-noise::before{content:'';position:absolute;inset:0;opacity:.03;pointer-events:none;miz-blend-mode:overlay;background-image:url(data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='3' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E);" 
    },
    "restrictions": {
      "never_use": ["purple→pink", "blue→purple", "green→blue", "red→pink", "stacked multiple gradient layers in same viewport"],
      "coverage_limit": "Gradients must not exceed 20% of viewport. If they do or affect readability, fallback to solid colors per Enforcement Rule.",
      "small_ui": "No gradients on elements <100px width"
    }
  },

  "typography": {
    "fonts": {
      "headings_serif": "Playfair Display",
      "body_sans": "Chivo",
      "numeric": "Space Grotesk"
    },
    "import": {
      "google_fonts_links": [
        "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700;800&display=swap",
        "https://fonts.googleapis.com/css2?family=Chivo:wght@300;400;500;700&display=swap",
        "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap"
      ],
      "preconnect": ["https://fonts.googleapis.com", "https://fonts.gstatic.com"]
    },
    "scale": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl (hero used at text-7xl/8xl is acceptable for impact)",
      "h2": "text-base md:text-lg",
      "body": "text-base (mobile text-sm)",
      "small": "text-sm/text-xs"
    },
    "utility_classes": {
      ".heading-1": "font-serif tracking-tight leading-[1.05] font-bold",
      ".heading-2": "font-serif tracking-tight leading-[1.15] font-semibold",
      ".eyebrow": "font-sans text-xs uppercase tracking-[0.25em] text-muted-foreground",
      ".font-numeric": "font-[Space Grotesk] [font-feature-settings:'tnum'_'lnum']"
    }
  },

  "layout_and_grid": {
    "container": "max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8",
    "grid_system": [
      "mobile-first single column",
      "md: 6–12 column mental model using Tailwind utilities",
      "critical sections: hero split 1/1 on mobile, 1/1 then 1/1/ content stack; lg: 2 columns"
    ],
    "spacing": {
      "section_y": "py-16 md:py-24",
      "stack_y": "space-y-6 sm:space-y-8",
      "cards_gap": "gap-6 md:gap-8"
    },
    "mobile_priority_fixes": [
      "Ensure CTAs occupy full width on <640px (w-full) with min-h-[48px]",
      "Carousel nav buttons: increase hit area to min-w-[44px] min-h-[44px] with aria-labels",
      "Locations cards: stack details with text-sm and increased line-height for legibility",
      "Header: keep cart icon sticky and accessible (position: sticky; top:0) if not already"
    ]
  },

  "components": {
    "component_path": [
      "./components/ui/button.jsx",
      "./components/ui/card.jsx",
      "./components/ui/carousel.jsx",
      "./components/ui/dialog.jsx",
      "./components/ui/drawer.jsx",
      "./components/ui/checkbox.jsx",
      "./components/ui/select.jsx",
      "./components/ui/input.jsx",
      "./components/ui/textarea.jsx",
      "./components/ui/tabs.jsx",
      "./components/ui/sheet.jsx",
      "./components/ui/sonner.jsx",
      "./components/ui/toaster.jsx",
      "./components/ui/calendar.jsx",
      "./components/ui/tooltip.jsx",
      "./components/ui/progress.jsx",
      "./components/ui/table.jsx"
    ],
    "styles_and_states": {
      "buttons": {
        "brand": "Professional / Corporate variant",
        "radius": "--btn-radius",
        "variants": {
          "primary": "bg-primary text-primary-foreground hover:bg-[#990000] focus-visible:ring-2 focus-visible:ring-ring",
          "secondary": "border-2 border-border bg-transparent text-foreground hover:bg-secondary/50 hover:border-primary/50",
          "ghost": "text-foreground/80 hover:text-foreground hover:bg-muted/30"
        },
        "sizes": {"sm": "px-3 py-2 text-sm", "md": "px-5 py-3", "lg": "px-8 py-4"},
        "motion": "Use transform-only transitions, no universal transition: specify [background-color, box-shadow, transform]"
      },
      "cards": "glass / glass-premium on dark, use .card-tilt hover for depth",
      "inputs": "border-input bg-background focus-visible:ring-2 ring-offset-2 text-base min-h-[44px]",
      "menus": "use dropdown-menu.jsx with data-testid on trigger and items"
    },
    "accessibility_and_testids": {
      "rule": "All interactive and key informational elements MUST include data-testid (kebab-case role-based).",
      "examples": [
        "data-testid=\"hero-primary-cta-button\"",
        "data-testid=\"menu-category-filter-select\"",
        "data-testid=\"cart-open-button\"",
        "data-testid=\"checkout-submit-button\"",
        "data-testid=\"order-tracking-status-text\"",
        "data-testid=\"loyalty-points-balance\""
      ]
    }
  },

  "micro_interactions_and_motion": {
    "lib": "Framer Motion",
    "install": ["npm i framer-motion"],
    "principles": [
      "Entrance: fade+slide up 12–24px, 300–500ms, 40ms stagger",
      "Hover: elevate with shadow and scale(1.02), timing 200–250ms",
      "Press: scale(0.98) and reduce shadow",
      "Transitions: never use transition: all; specify only needed properties"
    ],
    "snippets": {
      "button_js": "import { motion } from 'framer-motion';\nexport const MotionButton = ({ className = '', ...props }) => (\n  <motion.button\n    whileHover={{ scale: 1.02 }}\n    whileTap={{ scale: 0.98 }}\n    transition={{ type: 'spring', stiffness: 400, damping: 30 }}\n    className={className}\n    {...props}\n  />\n);",
      "stagger_container_js": "import { motion } from 'framer-motion';\nexport const FadeStagger = ({ children, className='' }) => (\n  <motion.div\n    initial=\"hidden\"\n    whileInView=\"show\"\n    viewport={{ once: true, margin: '-80px' }}\n    variants={{ hidden: {}, show: { transition: { staggerChildren: 0.06 } } }}\n    className={className}\n  >{children}</motion.div>\n);\n\nexport const FadeItem = ({ children, className='' }) => (\n  <motion.div variants={{ hidden: { opacity: 0, y: 18 }, show: { opacity: 1, y: 0 } }} className={className}>{children}</motion.div>\n);"
    },
    "embla_enhancements": {
      "autoplay_hint": "Use embla-carousel-autoplay for slow hero cycling",
      "progress_parallax": "translate image based on scroll progress for slight parallax (2–4%)"
    }
  },

  "accessibility": {
    "focus": "Use focus-visible ring tokens, maintain :focus-visible on buttons, links, inputs",
    "contrast": "Text vs background contrast >= 4.5:1. Avoid red on dark for long texts; reserve primary to accents",
    "targets": "Tap targets >= 44x44px",
    "aria": [
      "Carousel: role='region' aria-roledescription='carousel', buttons with aria-label Prev/Next",
      "Live regions for Order Status updates", 
      "Inputs labelled via label.jsx and aria-describedby for errors"
    ],
    "keyboard": "All dialogs, drawers, menus, and sheets must trap focus and close on Escape (already handled by shadcn)"
  },

  "performance": {
    "images": [
      "Use width/height attributes and loading='lazy' for non-hero images (already present).",
      "Hero: eager load 1st image only, others lazy.",
      "Prefer w=1200 quality=80 WebP if backend supports transformations"
    ],
    "fonts": [
      "Preconnect & swap; preload heading weights if CLS appears"
    ],
    "css_js": [
      "Replace transition-all utilities with specific properties only",
      "Move heavy backdrop-filter (glass) off mobile where possible (reduce blur to 12–16px)",
      "Use will-change: transform on hover scale elements only"
    ],
    "bundling": [
      "Code-split admin routes if heavy", 
      "Tree-shake lucide-react to icon-level imports"
    ]
  },

  "final_polish_checklist": [
    "Replace any 'transition-all' with 'transition-[background-color,box-shadow,transform]'",
    "Verify hero gradient area < 20% viewport (reduce radius or opacity if exceeded)",
    "CTAs: ensure data-testid and visible focus state",
    "Carousel arrows: aria-label, data-testid, and min 44px touch size",
    "Locations card: ensure text-sm line-height 1.6 for addresses",
    "Add slight parallax to hero image (scale 1.04 on hover, Embla progress offset)",
    "Loyalty points: animate number change with framer-motion",
    "Toast confirmations via ./components/ui/sonner.jsx for actions (add data-testid on toasts via content wrapper)",
    "Reduce mobile glass blur and shadows to improve paint times",
    "Audit with Lighthouse (LCP, CLS, TBT) — target 90+ on mobile"
  ],

  "code_mod_suggestions": {
    "buttons_css_replacement": {
      "context": ".btn-primary and .btn-secondary in /app/frontend/src/App.css currently use Tailwind 'transition-all'. Replace with explicit transitions.",
      "replace": [
        {
          "selector": ".btn-primary",
          "from": "@apply transition-all duration-300 ease-out;",
          "to": "@apply transition-[background-color,box-shadow,transform] duration-300 ease-out;"
        },
        {
          "selector": ".btn-secondary",
          "from": "@apply transition-all duration-300 ease-out;",
          "to": "@apply transition-[background-color,border-color,transform] duration-300 ease-out;"
        }
      ]
    },
    "carousel_nav": "Add data-testid=\"carousel-prev-button\" and data-testid=\"carousel-next-button\" on Embla nav buttons and aria-labels",
    "testid_policy": "Apply data-testid to all interactive components using role-based kebab-case naming"
  },

  "images_urls": [
    {
      "category": "hero_burger",
      "description": "Premium burger close-up on dark background with moody lighting",
      "alt": "Saftiger Premium-Burger im Dunkeln",
      "url": "https://images.unsplash.com/photo-1603508102983-99b101395d1a?auto=format&fit=crop&w=1600&q=85"
    },
    {
      "category": "handheld_burger",
      "description": "Hand holding gourmet burger against black backdrop",
      "alt": "Hand hält Gourmet-Burger",
      "url": "https://images.unsplash.com/photo-1654009782508-b3c526a36120?auto=format&fit=crop&w=1600&q=85"
    },
    {
      "category": "fries_smoky",
      "description": "Smoky french fries on black plate, dramatic light",
      "alt": "Rauchige Pommes auf schwarzem Teller",
      "url": "https://images.unsplash.com/photo-1541592391523-5ae8c2c88d10?auto=format&fit=crop&w=1400&q=85"
    },
    {
      "category": "fries_close",
      "description": "Fries with steam in dark scene",
      "alt": "Pommes mit Dampf im Dunkeln",
      "url": "https://images.unsplash.com/photo-1633945488417-99e20befb278?auto=format&fit=crop&w=1400&q=85"
    }
  ],

  "pages_specific": {
    "HomePage.jsx": {
      "hero": {
        "bg_classes": "noise-overlay bg-gradient-to-br from-background via-accent/30 to-background",
        "cta_primary": "btn-primary w-full sm:w-auto data-testid=hero-primary-cta-button",
        "parallax": "Add slight scale on hover and Embla progress-based translateY for hero image container"
      },
      "featured_categories": {
        "card": "group rounded-xl bg-card border border-border overflow-hidden hover:shadow-[var(--elev-2)] transition-[box-shadow,transform] duration-300 hover:-translate-y-0.5",
        "image": "object-cover group-hover:scale-105 transition-transform duration-300"
      },
      "locations": {
        "card": "bg-card border border-border rounded-xl p-6 md:p-8 space-y-4",
        "status_pill": "rounded-full text-xs font-semibold px-3 py-1.5",
        "actions": "btn-primary flex-1 and btn-secondary px-6",
        "testids": ["rellingen-card", "henstedt-card", "order-{slug}", "route-{slug}"]
      }
    },
    "BurgerBuilder.jsx": {
      "notes": [
        "Use ./components/ui/slider.jsx for quantities",
        "Ingredient chips via ./components/ui/badge.jsx with motion hover",
        "Add data-testid like ingredient-add-button-<name>"
      ]
    },
    "CheckoutDialog.jsx": {
      "notes": [
        "Use ./components/ui/dialog.jsx with proper aria and focus",
        "All inputs with data-testid and associated labels"
      ]
    },
    "OrderTracking.jsx": {
      "notes": [
        "Use ./components/ui/progress.jsx",
        "Announce step changes via aria-live=polite",
        "data-testid=order-tracking-progress"
      ]
    }
  },

  "install_and_integrations": {
    "libraries": [
      {"name": "framer-motion", "install": "npm i framer-motion", "usage": "Hover, entrance, counters"},
      {"name": "embla-carousel-autoplay", "install": "npm i embla-carousel-autoplay", "usage": "Hero carousel slow autoplay"},
      {"name": "recharts", "install": "npm i recharts", "usage": "Admin dashboards simple charts"}
    ],
    "toasts": {
      "path": "./components/ui/sonner.jsx",
      "usage": "import { Toaster, toast } from './components/ui/sonner'; add <Toaster richColors /> once; toast.success('Zum Warenkorb hinzugefügt', {id:'cart-add', 'data-testid':'toast-cart-add'})"
    }
  },

  "accessibility_testing": {
    "data_testid_policy": "All interactive and key informational elements MUST include data-testid (kebab-case role-based)",
    "linting": ["Run ESLint for .js/.jsx", "Check a11y with axe DevTools"],
    "screen_reader": ["Ensure buttons are real <button> elements", "Add aria-labels for icon-only controls"]
  },

  "instructions_to_main_agent": [
    "1) Replace transition-all utilities in App.css with explicit transition property lists as specified.",
    "2) Add aria-label and data-testid to Embla nav buttons; ensure min 44px size.",
    "3) Implement Framer Motion wrappers (MotionButton, FadeStagger/FadeItem) and use on hero, category cards, loyalty counters.",
    "4) Limit gradient usage to hero/header sections only; verify coverage < 20% viewport.",
    "5) Ensure all buttons/links/inputs have data-testid attributes using role-based kebab-case.",
    "6) Reduce mobile blur from 32px to 16px for .glass-premium where used inside scrollable views.",
    "7) Preconnect & load fonts with display=swap; test CLS.",
    "8) Run Lighthouse and address any LCP/CLS/TBT issues; compress images if needed.",
    "9) Keep container widths to --container-max and increase vertical whitespace by 1.5x on mobile.",
    "10) Use shadcn components from ./components/ui only for dropdowns, calendar, toasts, popovers, dialogs (no native fallbacks)."
  ],

  "general_ui_ux_guidelines": "- You must not apply universal transition. Eg: transition: all. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n- You must not center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n- NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use FontAwesome cdn or lucid-react library already installed in the package.json\n\n GRADIENT RESTRICTION RULE\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\nENFORCEMENT RULE:\n    • Id gradient area exceeds 20% of viewport OR affects readability, THEN use solid colors\n\nHow and where to use:\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, do not use purple color. Use color like light green, ocean blue, peach orange etc\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\nComponent Reuse:\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\nIMPORTANT: Do not use HTML based component like dropdown, calendar, toast etc. You MUST always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\nBest Practices:\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\nExport Conventions:\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\nToasts:\n  - Use sonner for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals."}

{
  "project": {
    "name": "ZOZO Burger — Admin Extensions Design System",
    "app_type": "Professional dark admin dashboard (desktop-first, mobile-ready)",
    "brand_alignment": "Keep premium dark with warm red accents; emphasize clarity and data legibility",
    "modules": [
      "Location Management",
      "Roles & Permissions (RBAC)",
      "POS Integration Settings",
      "System & Security (Audit, 2FA, Backups, Rate Limiting)",
      "Extended Dashboard Home"
    ],
    "success_actions": [
      "Add/edit a branch in < 2 steps",
      "Assign role/permissions without confusion",
      "Validate POS connection safely with clear status",
      "Investigate events via Audit Log filters quickly",
      "Monitor multi-branch KPIs at a glance"
    ]
  },

  "admin_color_system": {
    "tokens_hsl": {
      "--background": "240 6% 4%",
      "--foreground": "0 0% 96%",
      "--card": "240 6% 6%",
      "--card-foreground": "0 0% 96%",
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
      "--ring": "351 100% 35%",
      "--success": "142 70% 45%",
      "--warning": "40 95% 50%",
      "--info": "210 90% 60%",
      "--radius": "0.6rem"
    },
    "usage": {
      "status": {
        "ok": "use hsl(var(--success)) for checkmarks, positive badges",
        "error": "use hsl(var(--destructive)) for failing states",
        "warn": "use hsl(var(--warning)) for queued/attention states",
        "info": "use hsl(var(--info)) for neutral connectivity/info"
      },
      "data_surfaces": [
        "Tables on bg-card with subtle borders and zebra hover",
        "Metrics cards on bg-card with thin border and soft shadow"
      ],
      "avoid": [
        "No large red surfaces for content backgrounds",
        "No gradients on tables or dense content"
      ]
    },
    "helpers_css": {
      "add_to_index_css": "@layer utilities {\n  .text-success{color:hsl(var(--success));}\n  .text-warning{color:hsl(var(--warning));}\n  .text-info{color:hsl(var(--info));}\n  .bg-success-soft{background-color:hsl(var(--success)/0.12);}\n  .bg-warning-soft{background-color:hsl(var(--warning)/0.12);}\n  .bg-info-soft{background-color:hsl(var(--info)/0.12);}\n  .border-success{border-color:hsl(var(--success));}\n  .border-warning{border-color:hsl(var(--warning));}\n  .border-info{border-color:hsl(var(--info));}\n}\n",
      "code_mod": "Replace usages like text-success or bg-success/10 with arbitrary values if utilities are not added: text-[hsl(var(--success))] bg-[hsl(var(--success)/0.12)] border-[hsl(var(--success))]"
    }
  },

  "typography": {
    "fonts": {
      "headings": "Playfair Display",
      "body": "Chivo",
      "numeric": "Space Grotesk"
    },
    "scale": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl",
      "h2": "text-base md:text-lg",
      "body": "text-base (mobile text-sm)",
      "small": "text-sm"
    }
  },

  "component_path": [
    "./components/ui/button.jsx",
    "./components/ui/card.jsx",
    "./components/ui/table.jsx",
    "./components/ui/tabs.jsx",
    "./components/ui/select.jsx",
    "./components/ui/checkbox.jsx",
    "./components/ui/switch.jsx",
    "./components/ui/dialog.jsx",
    "./components/ui/popover.jsx",
    "./components/ui/command.jsx",
    "./components/ui/input.jsx",
    "./components/ui/textarea.jsx",
    "./components/ui/tooltip.jsx",
    "./components/ui/progress.jsx",
    "./components/ui/sonner.jsx",
    "./components/ui/calendar.jsx",
    "./components/ui/scroll-area.jsx",
    "./components/ui/pagination.jsx",
    "./components/ui/separator.jsx",
    "./components/ui/badge.jsx"
  ],

  "layout_and_grid": {
    "page": "Desktop first 12-col mental model with container-custom; mobile stacks",
    "forms": [
      "Use 2-column grid on md+ (md:grid-cols-2 gap-6) with sticky action bar",
      "Group fields in Cards with headings, description text-sm, and helper text"
    ],
    "tables": {
      "density": "default row py-3 md:py-3.5; compact mode available",
      "header": "bg-muted/30 text-xs uppercase tracking-wide text-muted-foreground",
      "row": "hover:bg-muted/20 transition-colors",
      "zebra": "optional: odd:bg-card even:bg-accent/30"
    }
  },

  "module_patterns": {
    "Location Management": {
      "screen_structure": [
        "Header: title + Add Location button",
        "Grid of Location Cards (md:grid-cols-2 lg:grid-cols-3)",
        "Each card: name, address, status pill (Active/Inactive), quick actions"
      ],
      "components": [
        "Card for branch summary",
        "Dialog for Add/Edit",
        "Tabs within dialog: Details | Delivery Area | Hours",
        "Select, Input, Switch, Checkbox, Command+Popover for multi",
        "Table inside Hours tab with weekday rows"
      ],
      "delivery_area": {
        "modes": ["Radius (km)", "Postal codes"],
        "ui": [
          "Mode Switch (Tabs)",
          "Radius Slider + numeric Input",
          "Postal Codes as token chips using Command list + Badge with remove"
        ]
      },
      "hours_editor": "Table rows: Mon–Sun; open switch; Start/End time selects (15-min steps); Duplicate to next; Closed state",
      "testids": [
        "locations-add-button",
        "location-card-<id>",
        "location-status-pill",
        "hours-save-button",
        "delivery-mode-tabs",
        "postalcode-add-input"
      ]
    },

    "Roles & Permissions": {
      "screen_structure": [
        "Admin list with search and role filters",
        "Add Admin dialog (email, role, branch assignment)",
        "Permission matrix tab (roles x permissions)"
      ],
      "patterns": [
        "Use Table for admins; Badge for role; Switch for active",
        "Matrix: Table with left column permission, columns per role; Checkbox cells; Sticky first column"
      ],
      "testids": [
        "rbac-add-admin-button",
        "rbac-role-filter-select",
        "rbac-permission-checkbox-<permission>-<role>",
        "rbac-assign-branches-popover"
      ]
    },

    "POS Integration Settings": {
      "screen_structure": [
        "Integration selector (Expert Order, Cash-X)",
        "Environment toggle (Test/Live) with warning when Live",
        "Credentials card (host, merchant id, username, secret masked)",
        "Connection status chip + Test Connection button",
        "Sync Logs table"
      ],
      "security": [
        "Mask secrets by default; reveal behind confirmation dialog",
        "Copy action requires extra confirm; only last 4 chars visible",
        "Audit events for reveal/copy/test"
      ],
      "testids": [
        "pos-vendor-select",
        "pos-env-toggle",
        "pos-secret-reveal-button",
        "pos-test-connection-button",
        "pos-connection-status-chip",
        "pos-sync-logs-table"
      ]
    },

    "System & Security": {
      "audit_log": {
        "filters": [
          "Date range (Calendar)",
          "Actor, Action type, Result, Integration/Branch",
          "Free text search"
        ],
        "table": "Timestamp | Actor | Action | Target | Result | IP (masked) | Details (expand)",
        "export": "CSV/JSON with confirmation; log export event"
      },
      "two_fa": {
        "flow": "Tabs/Steps: Choose method -> Configure -> Verify & backup codes",
        "totp": "QR code, masked secret, 6-digit verify, backup codes download once"
      },
      "backups": "Cards: Last backup time, size, retention, next run; Restore button with confirm dialog",
      "rate_limiting": {
        "overview": "Summary KPIs + policy list table",
        "edit": "Drawer/Dialog with scope, limit, burst, window; Dry-run toggle; chart preview",
        "charts": "Use Recharts Line/Area for requests & throttles"
      },
      "testids": [
        "audit-filter-actor-input",
        "audit-date-range",
        "audit-export-button",
        "2fa-start-button",
        "backup-run-now-button",
        "ratelimit-policy-edit-button"
      ]
    },

    "Extended Dashboard Home": {
      "layout": [
        "Top KPI cards (Today, Week, Month, Revenue)",
        "Branch switcher for Super-Admin",
        "Live orders stream (scroll area)",
        "Multi-branch revenue chart"
      ],
      "components": [
        "Card, Select, Table, ScrollArea, Progress, Tooltip",
        "Recharts Area/Bar chart"
      ],
      "testids": [
        "dashboard-branch-switcher",
        "dashboard-kpi-card-today",
        "dashboard-live-orders-table",
        "dashboard-revenue-chart"
      ]
    }
  },

  "tables_styling": {
    "wrapper": "bg-card border border-border rounded-xl overflow-hidden",
    "thead": "bg-muted/30 border-b border-border",
    "th": "px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider",
    "td": "px-6 py-3 align-middle",
    "row": "hover:bg-muted/20 transition-[background-color]",
    "empty_state": "px-6 py-12 text-center text-muted-foreground"
  },

  "forms_styling": {
    "field": "space-y-1.5",
    "label": "text-sm text-muted-foreground",
    "input": "bg-background border border-input rounded-md px-3 py-2 min-h-[40px] focus-visible:ring-2 focus-visible:ring-primary",
    "hint": "text-xs text-muted-foreground/80",
    "error": "text-xs text-[hsl(var(--destructive))]",
    "actions_bar": "sticky bottom-0 bg-card/80 backdrop-blur border-t border-border px-4 py-3 flex justify-end gap-2"
  },

  "motion": {
    "lib": "framer-motion",
    "install": "npm i framer-motion",
    "principles": [
      "Entrance: fade+slide up 16px, 280–400ms, 40ms stagger",
      "Hover: subtle lift (scale 1.01) on cards/buttons",
      "Form submit: disable + spinner + success toast",
      "Never use transition: all; specify [background-color, box-shadow, transform]"
    ],
    "snippets": {
      "motion_button_js": "import { motion } from 'framer-motion';\nexport const MotionButton = ({ className='', ...props }) => (\n  <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} transition={{ type:'spring', stiffness:380, damping:26 }} className={className} {...props} />\n);"
    }
  },

  "charts": {
    "lib": "recharts",
    "install": "npm i recharts",
    "area_chart_example_js": "import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';\nexport const RevenueArea = ({ data }) => (\n  <div className=\"h-64\" data-testid=\"dashboard-revenue-chart\">\n    <ResponsiveContainer width=\"100%\" height=\"100%\">\n      <AreaChart data={data}>\n        <defs>\n          <linearGradient id=\"rev\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\">\n            <stop offset=\"0%\" stopColor=\"#B00020\" stopOpacity={0.35} />\n            <stop offset=\"100%\" stopColor=\"#B00020\" stopOpacity={0} />\n          </linearGradient>\n        </defs>\n        <XAxis dataKey=\"label\" stroke=\"#8b8b8b\" tick={{ fill:'#B6B6B6', fontSize:12 }} />\n        <YAxis stroke=\"#8b8b8b\" tick={{ fill:'#B6B6B6', fontSize:12 }} />\n        <Tooltip contentStyle={{ background:'hsl(240 6% 6%)', border:'1px solid hsl(240 5% 14%)', color:'#F5F5F5' }} />\n        <Area type=\"monotone\" dataKey=\"value\" stroke=\"#B00020\" fill=\"url(#rev)\" strokeWidth={2} />\n      </AreaChart>\n    </ResponsiveContainer>\n  </div>\n);"
  },

  "accessibility": {
    "focus": "Use focus-visible rings (already configured)",
    "contrast": "Maintain >= 4.5:1 for text; avoid red for long body text",
    "targets": ">= 44x44px interactive targets",
    "aria": [
      "Give icon-only controls aria-labels",
      "Announce POS connection results via aria-live=polite",
      "Wizard steps should have role=tablist with active tab indication"
    ]
  },

  "testid_policy": {
    "rule": "All interactive and key informational elements MUST include data-testid (kebab-case, role-based)",
    "examples": [
      "locations-add-button",
      "rbac-permission-checkbox-manage-orders-admin",
      "pos-test-connection-button",
      "audit-export-button",
      "dashboard-branch-switcher"
    ]
  },

  "code_mod_suggestions": [
    "Add --success/--warning/--info tokens to :root in index.css (see admin_color_system.tokens_hsl)",
    "Either add utilities (helpers_css.add_to_index_css) or replace 'text-success'/'bg-success/10' with arbitrary hsl() classes",
    "Ensure all status badges use text-[hsl(var(--success))] etc. with appropriate soft backgrounds"
  ],

  "image_urls": [
    {
      "category": "admin_brand_header",
      "description": "Small brand lockup for admin header if needed",
      "alt": "ZOZO brand mark",
      "url": "https://images.unsplash.com/photo-1542831371-d531d36971e6?auto=format&fit=crop&w=1200&q=80"
    }
  ],

  "instructions_to_main_agent": [
    "Implement the five modules using shadcn/ui only; no native dropdowns/calendar",
    "Add success/warning/info tokens and optional utilities in index.css",
    "Replace any 'transition-all' with specific transition properties",
    "Add data-testid to every button, link, input, select, menu item, badge carrying state text",
    "Use Dialog + Tabs for Location Add/Edit; include Delivery Area (radius slider + postal code chips) and Hours table",
    "Build RBAC matrix using Table + Checkbox with sticky first column",
    "In POS Settings, gate secret reveal/copy behind Dialog; emit toasts via ./components/ui/sonner.jsx",
    "Create Audit Log filters row (Calendar date range + Selects + Input) and expandable row details",
    "Add Recharts for revenue and rate-limit previews; keep gradients subtle per restriction rule",
    "Keep gradient areas <20% viewport and never on dense tables or forms"
  ],

  "general_ui_ux_guidelines": "- You must not apply universal transition. Eg: transition: all. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n- You must not center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n- NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals."
}

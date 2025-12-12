# ZOZO Burger Ordering Platform — Plan

Preview URL: https://burger-dialog-ux.preview.emergentagent.com

## 1) Objectives (North Star)
- Build a dark, premium, high-conversion website with a custom multi-location ordering system.
- Each location (Rellingen, Henstedt-Ulzburg) operates independently with its own dashboard and menu.
- Smooth mobile-first UX, stunning visuals, and SEO/GEO dominance for both locations.
- Architecture ready for future ExpertOrder POS integration without refactor.

## 2) Architecture Overview
- Stack: React (frontend, shadcn/ui), FastAPI (backend), MongoDB.
- Routing: Frontend → Backend via REACT_APP_BACKEND_URL + "/api"; Backend binds 0.0.0.0:8001.
- Data model (initial):
  - Location { _id, name, slug, address, cityPostal, coords, hours, phone, socials }
  - Category { _id, location_id, name, slug, order }
  - MenuItem { _id, location_id, category_id, name, desc, price, image_url, tags, active }
  - Order { _id, location_id, items[{menu_item_id, name, price, qty}], subtotal, fees, total, customer{name, phone, address, notes}, status, created_at }
  - AdminUser { _id, email, password_hash, location_id, role }
- POS integration (later): Dedicated adapter layer + webhook endpoints to keep core isolated.

## 3) Phases

### Phase 1 — Core POC (Required)
Goal: Prove the end-to-end multi-location ordering flow works reliably before full build.

Scope:
- Seed DB with both locations + minimal categories + ~6 demo items per location.
- Core APIs (minimal auth bypass for POC):
  - GET /api/locations
  - GET /api/menu?location_id=... (returns categories + items)
  - POST /api/orders (payload: location_id, cart items, customer info) → returns order_id
  - GET /api/admin/orders?location_id=...&token=POC_TOKEN
  - PATCH /api/admin/orders/:id/status?token=POC_TOKEN
- Minimal React screens to validate flow: location picker → menu list (filter by category) → cart → checkout → confirmation.
- Type-safe totals calculation on backend; persist Order.

Test Core (single Python test script test_core.py):
- Seed data.
- Simulate user: choose location, fetch menu, add 2 items, checkout → verify order saved with correct total and location.
- Simulate admin: list orders by location; update order status; verify change.
- Fix until script passes.

Design placeholder:
- Dark theme, red accents (from logo), large hero CTA.

Phase 1 User Stories:
1. As a visitor, I can select Rellingen or Henstedt-Ulzburg and only see that location’s menu.
2. As a visitor, I can add items to a cart and see the total update instantly.
3. As a visitor, I can submit a checkout form and receive an on-screen confirmation with order number.
4. As a location operator (POC), I can fetch new orders for my location and change status to "accepted".
5. As a location operator (POC), I can see only my location’s orders (no cross-location leakage).

Deliverables:
- Working core endpoints, minimal UI, passing test_core.py report.

### Phase 2 — Full App Development (Comprehensive)
Goal: Ship the complete site and dashboards with wow-factor design and SEO.

Frontend (Customer Site):
- Pages: Home (hero + CTA), Menu (filterable), Locations (map + details), Individual Location page, About, Reviews, Contact, Blog/News.
- Location-aware ordering: pick location or auto-persist last selection; cart and checkout tied to location.
- Animations: subtle parallax in hero, micro-interactions on add-to-cart, smooth transitions.
- Images: high-impact food imagery (initially via curated stock/URL fields; file upload optional v1).
- Maps: Google Maps embed per location (no API key needed for embed, switchable later).
- Accessibility, keyboard navigation, and mobile-first layout.

Backend (APIs & Logic):
- Menu CRUD (per location), Categories CRUD.
- Orders: list/filter by status/location; state transitions (new → accepted → preparing → out_for_delivery → completed/cancelled).
- Admin authentication (JWT, email/password), roles: owner (all), manager (single location).
- Image handling: accept image_url; optional local upload endpoint storing under /app/backend/uploads with secure file names.
- SEO endpoints: JSON-LD generators for Restaurant, Menu, OpeningHours, Reviews.
- Settings: opening hours (11:00–22:45), contact info, social links.

Admin Dashboards (React routes under /admin):
- Auth screens (login/reset placeholder).
- Dashboard home: Today’s orders, quick actions.
- Menu Manager: categories, items with images, price, availability.
- Orders Manager: real-time-like polling (15s) or server-sent events in later iteration.
- Location Settings: address, hours, map preview, social links.

SEO & GEO:
- Meta titles/descriptions per page and per location.
- JSON-LD: LocalBusiness (2 locations), Menu, OpeningHoursSpecification, AggregateRating (with customer reviews section).
- Fast Core Web Vitals: image optimization, route-based code splitting, prefetch critical assets.
- Content blocks optimized for AI retrieval (clear headings, structured data, FAQs).

Design System:
- shadcn/ui + custom dark theme; typography scale for premium look; consistent spacing.
- Integrate uploaded logo; red (#990000–#B00020) as accent; off-white text on near-black background.

ExpertOrder readiness (not implemented):
- Abstraction layer (pos_adapter.py) with interfaces create_order, update_status, sync_menu.
- Webhook route placeholders disabled in v1.

Testing & Quality:
- ESLint & Ruff lint passes.
- End-to-end tests via testing_agent_v3 on key flows (skip camera/drag-drop).
- Manual visual QA on mobile and desktop; verify images render and error states are clear.

Phase 2 User Stories:
1. As a hungry user, I land on a cinematic hero and can start an order in 1 click.
2. As a user, I can filter the menu by Burgers/Pizza/Pasta and quickly add items.
3. As a user, I can switch locations and see a different menu without losing my cart context.
4. As a user, I can review my cart, enter delivery info, and place an order with immediate feedback.
5. As a manager, I can log in, edit my location’s menu, and see changes live on the site.
6. As a manager, I can view new orders, change status, and filter by state.
7. As a marketer, I can publish a short Blog/News post with SEO-friendly meta and it appears on the site.
8. As a user, I can view location pages with address, map, hours, and CTA to order now.
9. As a user, I can read customer reviews and see ratings structured for Google.
10. As a user, I experience smooth, premium animations without performance lag on mobile.

Deliverables:
- Complete customer site + admin dashboards; robust APIs; SEO artifacts; design-polished UI.

## 4) Implementation Steps (Execution Path)
- Phase 1
  1. Model schemas + seed script
  2. Minimal endpoints + totals calc
  3. Minimal React flow (picker → menu → cart → checkout)
  4. test_core.py covering create/list/update orders; fix until green
- Phase 2
  5. Call design_agent → apply guidelines
  6. Backend: full CRUD + JWT + JSON-LD + uploads(optional)
  7. Frontend: full pages, animations, admin routes
  8. SEO tuning + sitemap + robots.txt
  9. End-to-end testing via testing_agent_v3; fix all issues

## 5) Next Actions (from you)
- Provide current menu (items, prices, descriptions, categories, image URLs if available).
- Provide social links and contact phone(s) per location.
- Confirm any delivery areas/fees logic (flat fee vs. distance-based; initial v1 can be flat).

## 6) Success Criteria
- Phase 1: Scripted POC passes; orders persist with correct totals; location isolation proven.
- Phase 2: Users can place orders end-to-end; managers can manage menu and orders; pages are fast and visually stunning; JSON-LD validated by Google Rich Results; Core Web Vitals within target; no critical issues in testing report.

## 7) Notes
- No payment processing in v1; cash/card-on-delivery copy used at checkout (editable).
- Maps via Google embed (no key). ExpertOrder integration staged for a later phase.
- All interactive elements will include data-testid attributes for automated tests.

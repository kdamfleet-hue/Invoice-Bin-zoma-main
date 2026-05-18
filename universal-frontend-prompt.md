You are a senior Frontend Engineer and Design Systems Architect. Your mission is to perform a **complete audit and upgrade** of the current project located in the project directory.

---

## 🔍 PHASE 1 — FULL PROJECT AUDIT

Start by thoroughly scanning the entire project:
- Read every page, component, layout, and global style file
- Identify every data-fetching pattern (useEffect, fetch, axios, etc.)
- Identify every loading state — note where spinners, blank screens, or layout shifts occur
- Identify every mutation (form submit, button action, delete, update) — note if UI waits for server response
- Identify any stale cache or Client-Side Cache Staleness issues
- Check for any desync bugs (UI showing old data after mutation)
- Check if there is any real-time mechanism (WebSocket, SSE, polling)
- Audit the background — note if any page lacks a texture layer
- Audit the color system — note if dark ONYX theme is consistent across all pages
- Audit animation consistency — note jarring transitions, abrupt mounts/unmounts, missing enter/exit animations
- After scanning, produce a **full audit report** listing every issue found, grouped by category

---

## 🏗️ PHASE 2 — COMPLETE UPGRADE PLAN & IMPLEMENTATION

After the audit, implement ALL of the following across every page and component in the project:

---
### 2. 🌿 TOPOGRAPHIC BACKGROUND TEXTURE — EVERY PAGE

Create a global animated topographic contour texture. Requirements:

**SVG Pattern:**
- Pure SVG `<pattern>` element — organic, amoeba-like flowing curves using cubic `C` and quadratic `Q` bezier commands only (NO straight lines, NO grids)
- Lines must feel like a fingerprint or elevation map — tight swirling clusters + long sweeping curves
- Stroke: `rgba(255,255,255,0.035)` to `0.06`, stroke-width: 1.5–2px, rounded caps
- Tile seamlessly: pattern size ~400×300, paths must enter/exit at edges smoothly
- Apply as `position: fixed`, `inset: 0`, `z-index: 0`, `pointer-events: none` in root layout

**Animation (Motion One — latest):**
- Install: `motion` from `"motion"` package (Motion One, NOT Framer Motion)
- Animate `strokeDashoffset` on all contour paths — slow infinite drift (30–50s loop, `easing: "linear"`)
- Add a secondary `scale` breathing pulse on swirl clusters (1.0 → 1.015 → 1.0, 8s loop)
- GPU-accelerated only: use `transform` and `opacity` — never animate `width/height/top/left`

**Card Texture:**
- Apply the same SVG pattern as a texture layer inside every card/surface
- Use `mix-blend-mode: overlay` at `opacity: 0.04` so it's felt as depth, not seen
- Combine with `backdrop-filter: blur(12px)` + `background: rgba(255,255,255,0.03)` for glass effect

**Performance:**
- Use `will-change: transform` on animated SVG groups
- Pause animation when `prefers-reduced-motion: reduce` is set
- SVG must be inline in layout (not an img/background-image) for animation access
### 1. 🌑 DARK ONYX THEME — GLOBAL CONSISTENCY
- Base background: `#0a0a0a` (true near-black Onyx)
- Surface cards: `#111111` / `#141414`
- Borders: `rgba(255,255,255,0.06)`
- Text primary: `#f0f0f0`, secondary: `#888`, muted: `#555`
- Accent: a single glowing color (e.g. `#7c3aed` purple or `#0ea5e9` cyan — choose what fits the brand)
- Apply consistently via CSS custom properties / Tailwind config across ALL pages

---

### 2. 🌿 TOPOGRAPHIC BACKGROUND TEXTURE — EVERY PAGE
Create a global background SVG texture inspired by topographic contour maps — organic flowing curved lines, subtle, layered on top of the Onyx base. Requirements:
- Pure SVG or CSS-based (no image files, must be lightweight)
- Flowing, organic, amoeba-like curves (NOT straight lines or grids)
- Very low opacity (opacity: 0.03 to 0.06) so it's felt but not seen
- Use a `<pattern>` element with a path of hand-crafted organic wavy curves
- Tile seamlessly across the full viewport
- Apply as a fixed `position: fixed` full-screen layer behind all content on every page via the root layout
- Must work on both wide and narrow screens without visible tiling seams
- Example SVG path feel: meandering contour lines like a fingerprint or topographic mountain map

---

### 3. ⚡ TANSTACK QUERY v5 — ELIMINATE ALL STALE UI & DESYNC

Replace every manual `useEffect` + `fetch`/`axios` data fetching pattern with **TanStack Query v5**:
```tsimport { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

Rules to follow for EVERY query:
- Set `staleTime: 0` for real-time-sensitive data, `staleTime: 30_000` for stable data
- Set `refetchOnWindowFocus: true` on the QueryClient globally
- Set `refetchOnReconnect: true`
- Use `queryClient.invalidateQueries({ queryKey: [...] })` inside every `onSettled` callback after mutations — NOT `onSuccess` (to handle both success and error)
- Never let a mutation leave a stale cache behind

For EVERY mutation (form submit, delete, update, toggle):
Implement **full Optimistic UI** with cache rollback:
```tsuseMutation({
mutationFn: ...,
onMutate: async (newData) => {
await queryClient.cancelQueries({ queryKey: ['resource'] })
const previous = queryClient.getQueryData(['resource'])
queryClient.setQueryData(['resource'], (old) => /* apply optimistic update */)
return { previous }
},
onError: (err, variables, context) => {
queryClient.setQueryData(['resource'], context.previous)
},
onSettled: () => {
queryClient.invalidateQueries({ queryKey: ['resource'] })
}
})

---

### 4. 💀 SKELETON SCREENS — REPLACE ALL SPINNERS/BLANK STATES

Every data-dependent UI area must show a **skeleton screen** while loading, not a spinner:

- Use `shadcn/ui` Skeleton component OR build custom pulse skeletons
- The skeleton must **exactly match the shape and layout** of the real content (same height, same column count, same card structure)
- Add subtle shimmer/pulse animation: `animate-pulse` with the Onyx palette
- Apply to: all list views, all cards, all dashboards, all user profile sections, all tables

Example pattern:
```tsxif (isLoading) return <ArticleCardSkeleton />  // mirrors real ArticleCard layout

---

### 5. 🔄 PROGRESS BAR ILLUSION — PAGE TRANSITIONS & MUTATIONS

Install and configure **`next-nprogress-bar`** (for Next.js) or build a custom top progress bar:

- Show a slim (2–3px) glowing progress bar at the very top of the viewport
- Trigger it on: route changes, long-running mutations, file uploads, any async operation > 200ms
- Color: match accent color with a subtle glow/box-shadow
- Use the **psychological illusion technique**: start fast (0→30% in 100ms), then slow down (30→70% over 1–2s), complete instantly when done
- Never show a progress bar for operations under 150ms (debounce it)

---

### 6. 🎞️ MOTION — SMOOTH ANIMATIONS EVERYWHERE

Use **`motion`** (Framer Motion) for all enter/exit/layout animations:

**Page transitions:**
```tsx<motion.div
initial={{ opacity: 0, y: 8 }}
animate={{ opacity: 1, y: 0 }}
exit={{ opacity: 0, y: -8 }}
transition={{ duration: 0.2, ease: 'easeOut' }}



**List items (stagger children):**
```tsxconst container = { hidden: {}, show: { transition: { staggerChildren: 0.04 } } }
const item = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }

**Modal/Dialog:**
- Enter: scale from 0.95 + fade in
- Exit: scale to 0.95 + fade out

**Skeleton → Content transition:**
- When data arrives, animate content in with opacity + slight translateY

**Micro-interactions:**
- Buttons: `whileTap={{ scale: 0.97 }}`
- Cards: `whileHover={{ y: -2, boxShadow: '0 8px 30px rgba(0,0,0,0.4)' }}`
- All with `transition={{ type: 'spring', stiffness: 400, damping: 30 }}`

Apply `<AnimatePresence mode="wait">` around all conditional renders.

---

### 7. 🔴 REAL-TIME UPDATES

For any data that changes server-side (notifications, stats, feeds, status):
- Add `refetchInterval: 10_000` on relevant queries (polling as baseline)
- If WebSockets/SSE are available in the backend: connect them and call `queryClient.setQueryData(...)` directly when server push arrives
- Show a subtle "live" indicator dot (pulsing green dot) next to real-time data sections

---

### 8. 🌊 ADDITIONAL ADVANCED UX FEATURES

**Stale-while-revalidate indicator:**
- When TanStack Query is background-refetching, show a tiny spinning indicator (not a full loader) in the corner of the section being refreshed

**Error boundaries with recovery:**
- Wrap every major section in an `<ErrorBoundary>` that shows a styled retry button, not a blank crash

**Empty states:**
- Every list/table must have a designed empty state component (not just blank space)
- Include subtle icon + message + CTA

**Intersection Observer lazy loading:**
- Images and heavy components below the fold should lazy load using `useInView` from `motion`

**Focus management:**
- After modal opens, focus first interactive element
- After modal closes, return focus to trigger element

**Toast notifications (Sonner):**
- Install `sonner` for toast notifications
- Show success/error toasts after every mutation
- Style to match Onyx theme: dark background, colored left border

---

### 9. ⚡ PERFORMANCE

- Add `React.memo` to all pure components that receive stable props
- Add `useMemo` / `useCallback` where expensive computations or callbacks are passed to children
- Ensure no waterfall fetches — use `Promise.all` or TanStack parallel queries where multiple independent requests happen
- Lazy load all route pages with `next/dynamic` or `React.lazy` + `Suspense`
- All images must use `next/image` with `priority` on above-fold, `loading="lazy"` on below-fold

---

## 📋 DELIVERABLES

After implementation:
1. Summary of everything that was changed
2. List of all files modified
3. Any dependencies that need to be installed (`npm install ...`)
4. Any breaking changes or migration notes

---

## ⚠️ CONSTRAINTS

- Do NOT change the core business logic or routing structure
- Do NOT break existing API endpoints or data contracts
- Keep bundle size lean — do not add bloated dependencies
- Prefer CSS/SVG solutions over image assets
- Every change must be production-ready — no `console.log`, no TODO comments left behind
- TypeScript strict mode must remain satisfied

Begin now with Phase 1 — scan the full project and produce the audit report before writing any code.


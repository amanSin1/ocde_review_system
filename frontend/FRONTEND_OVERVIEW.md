# Frontend (React, Vite, Tailwind, Chakra UI)

This directory contains the single-page frontend for the Code Review System.

## Summary
- Framework: React 18 (functional components + hooks)
- Bundler / dev server: Vite
- Styling: Tailwind CSS + Chakra UI
- Icons: lucide-react
- Animations: framer-motion (optional usage)
- Routing: react-router-dom

## Quick start

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

## Build / preview

```bash
npm run build
npm run preview
```

## Scripts (from package.json)
- `dev` — start Vite dev server (defaults to port 3000)
- `build` — build production bundle
- `preview` — locally preview the built bundle

## Key files and structure
- `index.html` — app entry HTML
- `src/main.jsx` — root mount, ChakraProvider, BrowserRouter
- `src/AppNew.jsx` — main application shell and view routing
- `src/services/api.js` — central API helper and exported endpoint functions
- `src/utils/auth.js` — localStorage helpers for `token` and `user`, and `auth-changed` events
- `src/styles.css` — tailwind entry
- `tailwind.config.cjs` / `postcss.config.js` — Tailwind/PostCSS configuration
- `src/components/` — UI components grouped by feature (auth, layout, notifications, submissions)

## Primary tech details
- React 18, JSX modules
- Vite for fast dev/build (ESM)
- Tailwind CSS for utility-first styling; Tailwind is configured in `tailwind.config.cjs` and loaded via `src/styles.css`.
- Chakra UI used for provider-level theming (`ChakraProvider` in `src/main.jsx`) — components still use Tailwind classes for layout and utilities.

## Dependencies (high-level)
- `react`, `react-dom`, `react-router-dom`
- `@chakra-ui/react`, `@emotion/react`, `@emotion/styled`
- `tailwindcss`, `postcss`, `autoprefixer` (dev)
- `lucide-react`, `framer-motion`, optional `react-icons` / `prism-react-renderer`

## API & backend integration
- The app's network helper is `src/services/api.js`.
- Endpoints used (mapped functions):
  - `loginAPI` -> POST `/api/auth/login` (stores `access_token` in localStorage `token` and `user` in `user`)
  - `registerAPI` -> POST `/api/auth/register`
  - `fetchSubmissionsAPI` -> GET `/api/submissions`
  - `fetchSubmissionAPI(id)` -> GET `/api/submissions/:id`
  - `createSubmissionAPI` -> POST `/api/submissions`
  - `updateSubmissionAPI(id)` -> PUT `/api/submissions/:id`
  - `deleteSubmissionAPI(id)` -> DELETE `/api/submissions/:id`
  - `createReviewAPI` -> POST `/api/reviews`
  - `fetchNotificationsAPI` -> GET `/api/notifications`

- Currently `src/services/api.js` sets `API_BASE` to `http://localhost:8000` by default. To use an environment variable, change the file to use `import.meta.env.VITE_API_BASE || 'http://localhost:8000'`.

## Authentication flow
- `loginAPI` stores `access_token` in `localStorage.token` and `user` in `localStorage.user`.
- `getUser()` reads `localStorage.user` and `getToken()` reads `localStorage.token` in `src/utils/auth.js`.
- The app listens to a custom `auth-changed` window event to update top-level UI when login/logout occurs.

## UI / Components overview
- `src/AppNew.jsx` — orchestrates top-level views and notifications; controls which view is visible: login, register, submissions, create, detail, notifications.
- `src/components/layout/Navbar.jsx` — top navigation bar, shows user info and unread notifications count.
- `src/components/auth/LoginView.jsx` & `RegisterView.jsx` — forms to authenticate and register users.
- `src/components/submissions/*` — list, create form, and detail page for code submissions and reviews.
- `src/components/notifications/NotificationsView.jsx` — lists notifications and manages read state via localStorage.

## Styling & theming notes
- Tailwind is used throughout for utility classes. `src/styles.css` imports Tailwind base/components/utilities.
- ChakraProvider is included at app root so Chakra components can be used where desired.

## Environment & CORS
- Dev server runs on port 3000; backend expected on port 8000 (CORS must allow it).
- To change API base in dev/production, either edit `src/services/api.js` or implement `VITE_API_BASE` usage and start Vite with `VITE_API_BASE=https://api.example.com npm run dev`.

## Notes for answering questions
- Where is API configured? — `src/services/api.js` (`API_BASE` constant)
- How is auth handled? — `src/utils/auth.js` (localStorage + `auth-changed` event)
- How to run locally? — `npm install` then `npm run dev` inside `frontend`
- Build/CI? — `npm run build` produces production assets via Vite

## Suggested small improvements
- Use `import.meta.env.VITE_API_BASE` in `src/services/api.js` for configurable API base.
- Move `API_BASE` into a single env-driven config to avoid editing source for different environments.
- Add a README section for common debugging steps (CORS, tokens, backend routes).

---

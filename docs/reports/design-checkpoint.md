# Website design checkpoint

**Scope:** React/TypeScript seven-route shell and styleguide, before generated research observations were published. Captured on 2026-10-08 with Playwright Chromium 1.64.0 at 1366×900 desktop and 390×900 mobile widths. The styleguide contains no research result values.

| Mode | Desktop | Mobile |
|---|---|---|
| Light | [design-light-desktop.png](screenshots/design-light-desktop.png) | [design-light-mobile.png](screenshots/design-light-mobile.png) |
| Dark | [design-dark-desktop.png](screenshots/design-dark-desktop.png) | [design-dark-mobile.png](screenshots/design-dark-mobile.png) |

The design uses Source Serif 4 for reading text and Public Sans for controls and figures, packaged with the frontend so rendering does not depend on a remote font service. Light and dark tokens keep research surfaces neutral. Warm/cool colors are reserved for supplied CCT when present; red marks invalid or excluded states. The desktop side rail follows the seven-page reading order, and the mobile rail becomes visible top navigation. Appearance offers persistent Light, Dark and System modes, including live response to system color-scheme changes.

The first browser pass found two usability issues: the mobile appearance select lost its accessible label when the desktop label was hidden, and the skip link did not focus the main region. The select now has its own accessible name and the main region accepts skip-link focus. A later all-route pass exposed a 390 px overflow from a grid item's minimum content width; the reading and figure columns now permit shrinkage while wide data tables scroll inside their own containers. Room comparison checkboxes use native checkbox dimensions instead of the global field height. Playwright tests cover these behaviors, keyboard panning, reduced motion and theme persistence.

The site uses Vite 6.3.6 with Node 22.22.1, React 18.3.1 and Playwright 1.64.0, pinned in `frontend/pnpm-lock.yaml`. Vite's documented Node minimum is compatible with the host; Playwright 1.64 supports Ubuntu 26.04, whereas the initial 1.58 install did not. The image derivative script uses Sharp for 60 browser-sized WebP assets from 30 preserved Lumion renders. Square over/under sources use the top eye as an explicitly inferred presentation extraction; no orientation convention is asserted. The renderer script records the source path and extraction choice in `data/renders/manifest.json`.

This checkpoint assesses layout and controls only. Final screenshots with real generated research products, API states and complete route checks belong in [phase-8.md](phase-8.md).

# Website implementation and browser review

**Date:** 2026-10-08. **Scope:** the seven-route React site, its static research products, and the experimental FastAPI simulator. The 14 final screenshots below were captured from the real generated exports at 1366×900 in Light and 390×900 in Dark. Test-only synthetic records are confined to `frontend/tests/fixtures.ts`.

| Route | Light desktop | Dark mobile |
|---|---|---|
| The study | [Screenshot](screenshots/final-study-light-desktop.png) | [Screenshot](screenshots/final-study-dark-mobile.png) |
| Rooms | [Screenshot](screenshots/final-rooms-light-desktop.png) | [Screenshot](screenshots/final-rooms-dark-mobile.png) |
| Signals | [Screenshot](screenshots/final-signals-light-desktop.png) | [Screenshot](screenshots/final-signals-dark-mobile.png) |
| Affect | [Screenshot](screenshots/final-affect-light-desktop.png) | [Screenshot](screenshots/final-affect-dark-mobile.png) |
| People | [Screenshot](screenshots/final-people-light-desktop.png) | [Screenshot](screenshots/final-people-dark-mobile.png) |
| Room simulator | [Screenshot](screenshots/final-simulator-light-desktop.png) | [Screenshot](screenshots/final-simulator-dark-mobile.png) |
| Model report | [Screenshot](screenshots/final-model-light-desktop.png) | [Screenshot](screenshots/final-model-dark-mobile.png) |

The research bundle is copied to the site only after its SHA-256 matches `artifacts/results/manifest.json`; the Signals product receives the same check and its 160 trial IDs must match the bundle. The bundle is 260,067 bytes and contains trial metadata without waveform arrays. The 7,570,745-byte browser Signals product loads only on the Signals route; the full-rate 40 MB processing evidence is not sent to the browser. Browser traces use anti-aliased 100 Hz display sampling with 400 samples over four seconds; captions distinguish that from the conditional 500 Hz analytical scenario and the still-unverified acquisition rate. The build validates the bundle with Zod in the browser and the API client types are generated from the current OpenAPI file.

The generated products report 160 trials. Complete descriptive fusion contains 14 trial positions from two people: Experiment 2 has 4 from one person and Experiment 3 has 10 from one person. Another 96 trial positions use partial-modality fusion and are labelled separately in the study and affect views. The Signals page distinguishes 160 operational EEG feature records, 71 available heart-rate values, and 18 primary RMSSD values; its RMSSD availability flag is not presented as blanket ECG validity. These are protocol-conditional features, not artifact-free recordings. The model is labelled `not_better_than_baseline`: held-out-room mean MAE is 0.4304 versus 0.4099 for the median baseline on constructed coordinates. The simulator calls the fitted API and shows this weak status, support, limitations, and the distinction between target-proximity Neuro-Score and confidence.

Chromium review covered every route at 1366 px and 390 px in both themes, Light/Dark/System persistence, keyboard navigation and panorama/massing sliders, reduced-motion preference, room filters and comparison, sparse-data and missing-export states, signal QC and trace modes, affect/people cohorts, API-offline errors, and a real fitted API prediction and optimization through the UI. The live API check used a user-entered target and confirmed `not_better_than_baseline` in the response; it did not assume a specific predicted affect or claim a design recommendation. The static research pages were also checked with `/v1/*` offline.

The design review corrected a mobile appearance control without an accessible name, an unfocusable skip-link target, a 390 px grid overflow, oversized native checkboxes, and ambiguous signal availability labels. Wide tables scroll within their containers. Theme token contrast against the page background is at least 13.79:1 for primary light text and 15.20:1 for primary dark text; muted text is 5.95:1 and 9.21:1 respectively. The lowest tested colored text pair is the light warm token at 4.73:1. These checks cover defined token pairs, not every possible graphic or third-party browser rendering. Screenshots show readable routes without horizontal page overflow; the accessible data tables provide chart values for non-visual inspection.

Validation commands from `frontend/`:

```sh
PA_REQUIRE_RESEARCH_EXPORT=1 corepack pnpm build
CI=1 PA_LIVE_API_TEST=1 PA_API_URL=http://127.0.0.1:8001 LD_LIBRARY_PATH=/tmp/pa-browser-libs/root/usr/lib/x86_64-linux-gnu corepack pnpm test
```

The backend was started freshly from an isolated no-dev environment with `UV_PROJECT_ENVIRONMENT=/tmp/pa-backend-deploy-env uv run --frozen --no-dev uvicorn pa.api.app:app --host 127.0.0.1 --port 8001` from `backend/`. `/v1/health` reported `ready=true` and `not_better_than_baseline` after the final backend pipeline run. The final CI-mode full browser run passed 18 tests in 41.9 seconds. A Vite production preview returned HTTP 200 and correct JSON/WebP content types for `/research/bundle.json`, `/research/signals.json`, `/rooms/Rm_001-preview.webp`, plus HTML for `/model`. The site links original source images to their preserved repository paths on the feature branch; those public links require a post-push check once the branch exists remotely.

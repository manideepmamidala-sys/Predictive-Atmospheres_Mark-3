---
type: memory
description: "Seven-page React research atlas, accessible themes and figures, static research data, and experimental simulator API use."
---
# Website Architecture

**Domain**: architecture

## Overview

`frontend/src/` is a React, Vite and TypeScript research atlas with The study, Rooms, Signals, Affect, People, Room simulator and Model report routes. It presents generated evidence through a responsive reading layout, room imagery, comparison views, signal traces and accessible chart alternatives. The [platform](/architecture/platform.md) produces its data.

## Requirements

### Research and live-data boundaries

The research routes read schema-validated static products from `artifacts/results/`. A small joined bundle serves shared views; the larger Signals product loads on its route. Product hashes are checked when staged for a production build. Only experimental prediction and optimization require the `/v1` API. If that service is unavailable, static research remains readable and the simulator reports unavailability without fabricating output.

### Navigation, themes and evidence

React Router provides deep links to seven routes. Light, Dark and System themes share design tokens and persist user preference. Layouts support desktop and mobile, keyboard interaction and reduced motion. Figures carry method and source context, units and sample counts where applicable. Experiment and participant filters, explicit missing states, comfort as a separate construct, partial versus complete affect categories, and weak-model status remain visible in the interface.

Room previews are derived WebP presentation images from preserved Lumion renders; the original images remain source-accessible. Top-eye extraction from stacked stereo images is a documented inference, not source-verified viewing convention.

## Design Decisions

### Static research products with a narrow live API

**Decision**: Serve the seven-route research narrative from generated JSON and use the API for simulator actions only.
**Why**: The atlas can show reproducible evidence even when a free-tier API is asleep or unavailable.
**Rejected**: Making research pages depend on live computation, which would make archived results and basic reading depend on service readiness.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Dual-theme evidence display

**Decision**: Use shared tokens and Light, Dark and System preferences for routes, figures and controls.
**Why**: Scientific plots, tables and source distinctions need readable contrast across device sizes and user settings.
**Rejected**: A single dark cinematic presentation that does not serve the complete research atlas accessibly.
*Introduced by*: 261008-ymhz-research-platform-rebuild

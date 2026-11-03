# Accessibility verification record

The target is WCAG 2.2 Level AA. **No conformance claim is made.** Automated tools can detect only part of WCAG, and the manual reviews that cover the rest have not been done. This page lists what was checked, how, and with what result, and what remains unchecked.

Run on 2026-11-03 against a local build of the docs-platform branch (232 pages plus the home page), served over `http://127.0.0.1`, using Playwright's headless Chromium 141 and axe-core 4.11.0. Where noted, the live site at <https://onnxscibroccoli.github.io/bank-it-operations-lab/> (deployed from main `30e0a83`) was also checked.

## Automated checks that ran

| Check | How | Result |
|---|---|---|
| axe rules tagged wcag2a, wcag2aa, wcag21aa, wcag22aa | [browser.mjs](../../scripts/docs/tests/browser.mjs) on every page | 233 pages, 0 violations |
| axe "needs review" items | same run | `color-contrast` incomplete on 2 archived pages (`docs/management/project-checkpoint.md`, `evidence/incident/INTEGRATION-NOTES.md`). axe reported "Element content contains only non-text characters" in table cells. Reviewed: symbol-only cells in default text colour |
| Skip link | scripted keyboard | First Tab focuses "Skip to content". Enter moves focus to `main` |
| Search keyboard path | scripted keyboard | Query, Subject, Status, Depth level, Search button and first result are reached in order |
| Site search from any page | scripted | The header form on a content page submits to the home page and returns results |
| Navigation | scripted, 7 hub pages | 8 primary links on each page. Exactly one has `aria-current="page"` |
| Reflow (1.4.10) | 320 px viewport | No horizontal page overflow on the home page and 7 hub pages |
| Text spacing (1.4.12) | injected WCAG spacing values at 320 px, 13 pages | No horizontal overflow |
| Resize text (1.4.4) | root font size 200% at 640 px, 13 pages | No horizontal overflow |
| Forced colours | `forced-colors: active` emulation and axe, 8 pages | 0 violations. Visual appearance was not inspected |
| Search failure state | index request blocked | Status message announces the failure and points to the catalog |
| Contrast of declared colours | computed from [style.css](../../scripts/docs/style.css) | Body text 14.55:1, links 7.59:1 (6.77:1 in the status panel), button text 8.14:1, focus outline 7.83:1, form borders 5.82:1, table borders 4.01:1 |
| Heading-anchor links | `test_internal_heading_anchors_resolve` | Every internal `#fragment` link resolves to an element id |
| Live site | browser.mjs against GitHub Pages | Search and keyboard checks passed. The axe run stopped at `pages/.github/pull_request_template.html`, which returns 404 on the live site. The dot-github fix addresses this. The live axe run has not been repeated after redeployment |

There is only one colour theme. The site has no dark mode, so "all themes" means the light theme plus forced-colours emulation.

## Not verified

- Keyboard use by a person, including focus visibility on every control and **Focus Not Obscured (2.4.11)**. Only the scripted paths above ran.
- Screen readers: NVDA, JAWS, VoiceOver and TalkBack have not been used. `browser.mjs` records `manualScreenReader: NOT RUN`.
- Real browser zoom to 400% and mobile OS text scaling. The checks above approximate them.
- Visual inspection in Windows High Contrast or other forced-colour themes.
- Contrast of the browser's own default focus ring and of states axe cannot compute (hover, visited links).
- **Target Size (2.5.8)** beyond what axe's `target-size` rule detects. Primary links set a 44 px minimum height, but their width is not measured.
- Cognitive accessibility and plain-language review. Pages are written for progressive depth but have not been tested with readers.
- **Mermaid diagrams.** `inventory/ARCHITECTURE.md` contains ten Mermaid diagrams. The site shows them as source text, and they have no written equivalent beyond node names.
- Firefox and Safari. Only Chromium was used.
- Accessible Authentication (3.3.8) and Redundant Entry (3.3.7) do not apply: the site has no sign-in and no multi-step forms.

## How to repeat

Follow [Reproduce the portal](development.md#reproduce-the-portal), then run `node scripts/docs/tests/browser.mjs` with the local server running. Results are written to `dist/docs/accessibility-report.json`. The CI workflow runs the same script on every pull request.

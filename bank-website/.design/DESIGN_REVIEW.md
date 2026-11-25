# Design Review: Demo Bank landing + PIN flow

Reviewed against: no DESIGN_BRIEF.md existed; used `design-system/demo-bank/MASTER.md` (ui-ux-pro-max) and the request ("user-friendly, modern, simple").
Philosophy: calm fintech minimalism, navy/green, IBM Plex Sans, light default + OS dark mode.

## Screenshots Captured (headless Edge, OS in dark mode)

| Screenshot | Viewport |
|---|---|
| `screenshots/review-home-desktop-1280.png` | 1280x800 |
| `screenshots/review-home-tablet-768.png` | 768x1024 |
| `screenshots/review-home-mobile-375.png` | 375 (iframe; headless Edge clamps window width) |

NOT captured: PIN dialog, error state, result screen, light mode. Headless capture cannot click; the browser MCP was disconnected. Check these by hand.

## Must Fix
None found in code or captured screens.

## Should Fix
1. **Unverified states**: dialog (open/error/loading) and result page for Low/Medium/High were only tested through the API, not seen. Open http://localhost:5173 and click through the three demo PINs.
2. **Light mode unseen**: tokens are defined (`src/index.css`); contrast was reasoned (brand #15803d on white ≈ 5:1), not measured.
3. **Currency**: dataset amounts have no currency, so the UI shows bare numbers. Add a currency once the business decides.

## Could Improve
- Hero preview card is decorative sample data (aria-hidden). Fine for a demo; replace with real imagery later.
- No manual theme toggle (follows OS only).

## What Works Well
- One primary CTA per view; hierarchy is clear on desktop.
- Risk is never colour-only: icon + word + position bar.
- Native `<dialog>` gives focus trap, Esc, backdrop. PIN input auto-uppercases, strips invalid chars, shows 0/7 counter, inline `role="alert"` error, 44px+ targets, reduced-motion respected.
- Language is decision-support, never approve/reject.

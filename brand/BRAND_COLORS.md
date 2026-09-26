# NextPlane Brand Colors + Logo (CANONICAL)

Pulled from the actual logo on nextplane.us. **Use these everywhere.**

## Colors

| Name | Hex | RGB | Use |
|---|---|---|---|
| **Navy** | `#0F2A3F` | rgb(15, 42, 63) | Primary brand color. Backgrounds, text on light bg, primary fill |
| **Off-white** | `#F6F9FA` | rgb(246, 249, 250) | Light surfaces. Text on dark bg |
| **Cyan** | `#25C5CB` | rgb(37, 197, 203) | Accent. Highlights, CTAs, primary interactive elements |
| **Pure white** | `#FFFFFF` | rgb(255, 255, 255) | Pure text on dark backgrounds |

That's it. Three colors plus white. The amber (`#FFB300`) I was using earlier was wrong — purge it from any future deliverable.

## Logo

The logo is a compass/dial with a cyan needle pointer.

- `nextplane_logo.svg` — adaptive (uses prefers-color-scheme — dark needle on light, white needle on dark)
- `nextplane_logo_for_dark_bg.svg` — needle is white/cyan, ring is white
- `nextplane_logo_for_light_bg.svg` — needle is navy/cyan, ring is navy

Pre-rasterized PNGs at 200, 400, 800, 1600px in both modes.

## Logo construction (for re-rendering)

If you need to redraw it in Python or another tool, the structure is:

- Outer ring: circle, no fill, stroke `#0F2A3F` (or `#F6F9FA` for dark bg), stroke-width 5/120 of viewport
- Tick marks at top (N), bottom (S), left (W), right (E)
- The top tick is a small filled circle in cyan `#25C5CB` instead of a rectangle (indicates N)
- Compass needle: rotated ~22° clockwise
  - Top half of needle: cyan triangles (full opacity left half, 0.85 opacity right half)
  - Bottom half of needle: navy/white triangles (matching color of ring)
- Center dot: small filled circle, same color as ring

## When to use which version

- **Dark backgrounds** (navy, black, dark photo): use `for_dark_bg` PNG
- **Light backgrounds** (white, off-white, light photo): use `for_light_bg` PNG
- **Adaptive contexts** (web, where prefers-color-scheme is respected): use the SVG `nextplane_logo.svg`

## Tagline pairings

The logo can stand alone (compass mark) or be paired with the NEXTPLANE wordmark.

- Profile pic / favicon contexts: logo only
- Banner / hero contexts: logo + wordmark + tagline ("The aircraft history report.")

## Do not modify

Do not invent new colors. Do not rotate, recolor, or stylize the logo. Do not pair it with amber (we don't use amber). Do not use a different compass orientation.

# Evidence and acceptance

Choose checks for the intended component and backend; not every component needs every optional effect.

## Optical output

Use a grid, readable text and asymmetric corner marks, plus realistic content. Compare with blur-only at identical size, crop, tint and DPR. Check scene displacement near curvature, detail in the flat body, transparent outside pixels, directional light, correct foreground orientation and premultiplied alpha. Test translated surfaces and noninteger DPI. Inspect final host clipping and overlays as well as exported shader pixels.

For a confirmed opaque colored rail, check its alpha and settled RGB separately from the glass thumb. A stronger optical effect must come from displaced samples at matched geometry. For an overflowing lens, inspect pixels outside the rail and layout; the reference's protruding shoulders must survive the host's clips.

## Interaction invariants

| Intended behavior | Observable check |
| --- | --- |
| Fixed local pull | Grabbed edge bends; far corners/opposite edge and body texture stay fixed; no whole-card affine transform; text/layout coordinates unchanged |
| Tethered component | Whole surface and foreground travel together within configured gain/limits; release returns to original coordinates |
| Guided switch tap | At rest, rise at the original end before travel; stay expanded through arrival; shrink at the destination; mirror this for the opposite direction |
| Held glass switch | Direct drag previews in both directions; rail color follows the chosen timing at the confirmed opacity; boolean commits once on release; cancel restores |
| Demo/host parity | The same short tap uses the same phase order, start pose, destination and color policy in the reference and destination; compare at normal speed |
| Moving lens | Continuous input-driven position and directional deformation; slow/fast drags differ where intended |
| Sustained hold | Local pull retains its field; tether velocity strain settles while pressed lift remains; idle frames stop |
| Reversal/re-grab | Preserve state/velocity; do not instantly relocate an existing local field |
| Release/cancel | Converge to rest; clear capture/listeners; no unintended business commit |
| Elastic recoil | Observable overshoot/reversal at the grabbed edge, with sufficient paint space; tuning a spring is insufficient if the native host clips it |
| Nested controls | One native button click; editing/selection, scrolling and keyboard remain usable |
| Reduced motion | Record effective app/system settings; reset active deformation and pending tap phases; retain usable state feedback |

A globally sheared rectangle can keep its centroid while looking displaced. A local bulge may change the silhouette centroid without moving the body. Compare designated stable edges/body regions, not only the centroid.

`scripts/compare_regions.py` compares stable and changing regions in equal-sized captures. Choose regions from the interaction contract. It requires Pillow and does not replace visual inspection.

## Evidence scope

- Unit/spring tests establish state behavior.
- GPU targets establish optical output on that renderer.
- Model-driven captures establish integration/layout, not pointer delivery.
- UI Automation Invoke establishes semantic activation, not press/drag/release routing.
- Real input plus a current visible-window capture establishes native interaction/composition for that run.

Warm shaders and scene/image resources before timed captures. Verify every expected output is fresh. Record backend, viewport, DPI, build mode, input method and limits. Native automation must check foreground, unlocked desktop and pointer/button state. Release the mouse at its current location: helper defaults that move to (0,0) can change windows and invalidate the trace. If another input interrupts a trace, discard it rather than labeling the image as the intended phase.

Inspect rest, held motion and settled states, plus reversal/cancel when supported. Performance and cross-backend parity need separate measurements. Do not generatively retouch verification screenshots or treat stale window captures as current GPU evidence.

For a guided switch, capture the same tap in the demo and host at rest, initial lift, middle travel, arrival and settled state. Record the physical pointer-up and the single native state commit separately from the optical finish. Repeat in the opposite direction and re-grab during motion. A speed adjustment should shorten the guided gesture without deleting a phase or accelerating direct dragging. Use the user's accepted baseline for the pace; do not infer it from slow-motion or enlarged playback.

## Transfer checks for this skill

- Fixed native card with nested buttons: local pull, child input ownership, and stable far-edge tests; reject whole-card skew even with a fixed center.
- Flutter moving navigation lens: preserve callbacks/keyboard/cancel while allowing intended position motion; do not impose card anchoring.
- Web panel over DOM/video: establish source/capture support; identify CSS blur as fallback when arbitrary refraction is unavailable.
- Custom curved shape: derive deformation/normals from its actual field/path; adapt rectangular nearest-edge assumptions.
- Motion-only feedback such as "keep the green": preserve the approved resting colors and opacity while tuning deformation/refraction.
- "Make App B look like this App A demo": identify App A as the reference and App B as the destination; change only the requested component and dimensions of behavior.
- "Try it on this page first": keep the implementation in QA until promotion is authorized; then carry the latest approved behavior into the named hosts.

# Scene, coordinates and composition

## Keep a coordinate ledger

Name these spaces explicitly: host layout coordinates, scene/capture coordinates, texture pixels, shader logical units and final presentation pixels. Record capture origin, overflow, scale/DPR and transforms. Translate a component into its source scene, then apply the correct pixel scale; do not fit a captured bitmap to layout width without checking the capture extent.

Some capture APIs include overflowing descendants. The bitmap can be wider/taller than the element's layout, with transparent padding. Treating the bitmap width as the layout width squeezes this padding into the surface and produces black bands, stretched wallpaper or displaced sampling. Preserve the capture's native pixels-per-unit ratio, including after downsampling.

Test a translated component at non-100% DPI with text and unequal corner marks. A centered grid alone hides offsets, mirror inversions and origin mistakes. Do not flip every backend's textures to fix a problem observed on only one backend.

## Exclude feedback; describe freshness

Capture a separate background subtree or explicit scene texture. If capture includes the lens, its border or foreground, each frame samples the previous glass and can create trails/double images. Decide whether foreground is crisp above glass or in a separately sampled layer.

Cached decorative scenes can update on size, theme, image load and explicit invalidation. Scrolling/background animation requires a live source or corresponding invalidation. Platform views, video and WebViews may not appear in an ordinary UI raster capture. Document that boundary instead of claiming all screen content is captured.

## Clear material is a composition property

Trace all painted layers when the user sees white/opaque fill:

- Control/template Background and parent backgrounds.
- Fallback wash opacity and successful-render transition.
- Selected, hover, pressed and disabled native state overlays.
- Borders that stay static while the shader changes shape.
- Pre-multiplied alpha, opaque offscreen clears and out-of-source pixels.

Tint is absorption/color; blur is scattering. An opaque white wash plus blur does not become clear glass by adding highlights. Conversely, a clear material can still have intentional mild frost; choose from the user's reference. Preserve readable foreground and opaque accessibility fallbacks.

## Paint bounds and resource ownership

Compute worst-case displacement plus antialiasing/filter support, and reserve that draw area independently of layout and hit testing. Inspect ancestor clips and rounded containers in the actual host. A texture export can show correct overflow that is later clipped by the visible control.

Share scene uploads and reuse effect graphs. Bound both scene and output texture dimensions/area. Avoid encoding, readback and upload on every animation frame. Handle resize, source replacement, theme/DPI changes and device loss. Guard asynchronous captures against obsolete revisions and disposal; stop invalidation loops at rest. Profile the actual backend rather than inferring performance from a small animation amplitude.

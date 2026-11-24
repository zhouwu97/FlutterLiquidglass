---
name: flutter-liquid-glass
description: Build and debug refractive liquid glass materials and elastic interactions for UI components in Flutter, WinUI, web and other shader-capable hosts. Use for glass cards, buttons, lenses, toolbars, navigation and custom shapes; adapt rendering and gestures to the actual platform.
---

# Liquid glass materials and interaction

The invocation name is retained for compatibility. The workflow applies beyond Flutter. Implement the user's component and interaction; the example's product layout, artwork, dimensions and settings are not requirements. A skill cannot establish support for an untested backend: verify capability in the destination host.

## Establish the component contract

Inspect the host's visual tree, scene source, layout constraints, theme, input ownership and business callbacks. Identify which visible surfaces share the material and which inner controls must retain their native behavior. Read the user's reference shader, scene capture and motion code together when available, record the revision, and retain relevant licenses.

Choose these independently from the request and existing host:

| Decision | Examples |
| --- | --- |
| Geometry | Capsule, rounded rectangle, asymmetric corners, custom SDF/path |
| Transmission | Clear detail, intentional frost, subtle colored absorption |
| Foreground | Crisp text above glass, or content intentionally refracted inside it |
| Interaction | Fixed local pull, tethered component that returns home, moving lens, semantic selection, button press, passive panel |
| Scene | Live application content, explicit decorative scene, or platform backdrop |

When an optical or interaction assumption is uncertain, validate a small isolated demo using the actual host renderer before integrating. Respect a requested demo → test → host → publish sequence. Reusing the shader alone does not validate the host's layering or event routing.

## Select motion before writing transforms

Read [interaction-models.md](references/interaction-models.md) for the selected mode.

- **Fixed card/button pulled in place:** localize deformation near the grabbed edge. Leave the body, distant corners, opposite edge and foreground fixed. A fixed center plus whole-card scale/skew can still look like sliding; center-only tests are insufficient.
- **Tethered component:** move foreground and surface together, return position targets to the resting location on release, and preserve spring velocity. Tune pointer gain/travel independently of damping and curvature; do not turn a prior fixed-position preference into a universal rule.
- **Draggable lens:** position follows input with continuous spring state; velocity and lag may drive stretch and bend.
- **Selection indicator:** keep visual motion ownership separate from selected business state. Preserve the host's commit phase, keyboard navigation and cancellation behavior.
- **Button/passive panel:** keep native activation and hit testing. Do not attach navigation or drag-to-select semantics just because the example has them.

Update spring targets rather than restarting tweens on each pointer event. Preserve state and velocity on release, reversal and re-grab; bound frame delta and integration steps. Stop scheduling when settled, including when a sustained pull is held still. A mouse button's held value is activation, not measured force. Reduced motion must stop deformation while leaving understandable interaction feedback.

## Build one optical surface

Capture the actual scene behind the component without the component itself. Derive coverage, normals, optical thickness, scene displacement and directional lighting from the same deformed field. Separate blur from tint; reducing opacity alone cannot create refraction. Keep dispersion and highlights restrained, and preserve premultiplied alpha at the boundary.

Treat the whole composited control as the material: template backgrounds, fallback washes, native selected/hover fills, ancestor clips and static borders can conceal an otherwise correct shader. Hide fallback fills only after capture and shader drawing succeed. A shader image that looks transparent is not proof that the visible control is transparent.

Read [rendering-and-coordinates.md](references/rendering-and-coordinates.md) when implementing capture, DPI conversion or deformation. Read only the relevant sections of [platform-notes.md](references/platform-notes.md) for Flutter, WinUI or another backend. Verify current platform APIs against primary documentation when porting.

Preserve native controls and accessibility above the optical layer. Assign each pointer to one interaction owner; parent cards should not intercept child buttons, editing, selection or scrolling. Provide paint overflow for the maximum deformation without expanding hit targets or shifting layout. Keep decoration outside accessibility traversal. Do not invent missing artwork: inspect the original asset and adapt its layout to the user's chosen framing.

## Control capture and resource lifetime

Share scene textures across surfaces where valid. Capture on scene invalidation and separate that from optical animation. A cached wallpaper is acceptable when that is the intended source; it does not represent live WebView/video/DOM content. Bound texture size and optical padding. Avoid CPU readback, PNG encoding and texture upload in the animation loop. Dispose surfaces, listeners and timers; recover from resize/theme/DPI/device changes. Optional sensors stop in the background.

Offer an honest fallback when source capture or the shader is unavailable. Distinguish clear/frosted refraction, backdrop-only blur and solid accessibility fallback. Do not use a DWM or renderer-internal hook without evaluating its version constraints and necessity for the host.

## Verify the result in three layers

Use [acceptance.md](references/acceptance.md) for observable checks and evidence.

1. **Motion:** hold, release, reversal, re-grab, cancellation, pointer ownership and multiple refresh rates; assert the chosen interaction contract.
2. **GPU pixels:** patterned scene and asymmetric text; check displacement versus blur-only, alpha, padding, lighting and coordinate transforms. For local pull, compare untouched edges and body pixels, not only the centroid.
3. **Visible native control:** real press/move/release, child button clicks, text input/selection, scrolling, keyboard, themes, resizing and fallbacks. Verify the captured window is current, visible and unobscured. A model-driven capture or UI Automation Invoke does not establish pointer routing.

Keep screenshots and traces from the current build and record their capture method. Warm resources before phase captures. Locked desktops, occluded windows, unsupported external textures and stale window capture must be reported as limits, not replaced by a simulated success. Never fabricate or generatively retouch verification screenshots.

## Optional worked examples

- [reference-model.md](references/reference-model.md): equations and uniform layout for the original Flutter navigation lens; its coefficients and selected-item behavior are example-specific.
- `assets/reference_flutter/`: optional runnable Flutter source bundle. Create a separate Flutter project and overlay this bundle to explore it; do not overwrite a business project wholesale.
- [WinUI example](https://github.com/zhouwu97/FlutterLiquidglass/tree/main/examples/winui-liquid-glass): independent Direct2D demo, tethered component and moving-lens models, GPU probes and native input capture script. Read its build requirements before copying.

Adapt these pieces to the requested shape and interaction. Publishing remains within the user's requested destination and scope; installing this skill does not authorize external actions.

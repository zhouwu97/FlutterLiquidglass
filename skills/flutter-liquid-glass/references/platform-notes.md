# Backend notes

Read only the platform section relevant to the host. Flutter/WinUI notes below come from implemented examples; the web/native mapping is a starting point that still needs target-specific validation.

## Flutter

- A `Paint.shader` path with explicit scene and optional foreground samplers can avoid dependence on unsupported `ImageFilter.shader` paths. Match Dart uniform setters and GLSL declarations.
- Set capture boundaries for the actual Scaffold/Stack/safe-area arrangement; include wallpaper behind transparent content. Do not force a bottom-navigation layout onto unrelated components.
- Offscreen orientation corrections are backend-specific. The reference corrects its OpenGLES path, not CanvasKit globally. Confirm with readable asymmetric content on the destination renderer.
- Prefer GPU image capture and reuse; CPU PNG conversion in the drag loop creates lag. Native platform views/external textures require separate verification.
- After switching integration-test/debug/release modes, allow plugin registration regeneration; blindly passing `--no-pub` caused stale registrant state in the tested Flutter setup. Do not force that build sequence on an unrelated stable build.

## WinUI 3 / Win2D / Direct2D

- Build the effect graph in one pixel coordinate space. In this port, complex shader samplers failed with `D2DERR_INVALID_GRAPH_CONFIGURATION` when implicit DPI compensation entered the graph. Rendering to a 96-DPI target sized in physical pixels, then presenting once in XAML DIP, avoided that failure. Validate scaling and transforms rather than hardcoding DPI to hide it.
- `RenderTargetBitmap` can contain overflowing descendants. Save its actual dimensions and XamlRoot rasterization scale. A GPU-downsampled source still needs the original pixel-to-DIP mapping.
- Composition backdrop blur is a useful fallback; it is not displaced scene sampling. Report shader readiness only after successful scene capture and drawing. Dispose CanvasControl resources with the visual tree.
- Observe native routed input with one owner per component. Preserve native ButtonBase capture and Click; do not capture touch that should scroll, or selectable text/child controls. Make decorations hit-test invisible and reserve draw overflow separately.
- In the tested WinUI control, `Grid.CornerRadius` on the optical host clipped outward deformation even with negative child margins. Use a separate material geometry property such as `SurfaceCorners`; leave the host's corner clipping unset. Compare outside-layout pixels in the visible window, because a GPU target can look correct while the host cuts off every outward bulge.
- A frame exported from CanvasRenderTarget proves shader output, not final XAML compositing. `PrintWindow` returned a stale solid fallback even while the visible window showed GPU glass. Use a current visible-window capture for host evidence; check foreground, occlusion, unlocked desktop and freshness.
- Moving the cursor with `SetCursorPos` alone left captured WinUI pointer coordinates stale in this environment. Inject a real move event for automation and verify both received input and visible shape change; correct cursor coordinates alone do not establish routing.
- The standalone demo must call its generated `App.InitializeComponent()` and package the required XAML dictionaries, PRI, fonts/images and runtime dependencies. Starting from a packaged host can affect `ms-appx` resource identity; in this environment shell activation of the executable isolated the demo correctly. Diagnose before applying that workaround elsewhere.
- When moving externally linked assets into the project tree, check SDK default Content inclusion. Adding the same local image again with `Include` produced duplicate PRI entries; `Update` configured the existing item correctly. Audit `.gitignore`: ignored manifests can make a local build succeed but a clean clone fail.

## Web and other native hosts

Separate portable optics/motion from the capture adapter. For web, CSS backdrop blur alone does not provide arbitrary refractive displacement. WebGL/WebGPU/canvas shaders need a usable, permitted scene texture; ordinary DOM, video and cross-origin sources have different capture/security constraints. Do not promise transparent access to everything behind an element.

For other native APIs, map the same contract to their capture/composition/shader facilities: scene source, coordinate transform, shape field, material, motion, hit testing and lifecycle. Verify current official APIs, external texture support, GPU limits and accessibility behavior. If the platform lacks a needed capability, provide and identify a fallback or a scoped experimental prototype; do not label untested ports complete.

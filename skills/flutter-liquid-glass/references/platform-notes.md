# Backend notes

Read only the platform section relevant to the host. Flutter/WinUI notes below come from implemented examples; the web/native mapping is a starting point that still needs target-specific validation.

## Flutter

- A `Paint.shader` path with explicit scene and optional foreground samplers can avoid dependence on unsupported `ImageFilter.shader` paths. Match Dart uniform setters and GLSL declarations.
- Set capture boundaries for the actual Scaffold/Stack/safe-area arrangement; include wallpaper behind transparent content. Do not force a bottom-navigation layout onto unrelated components.
- Offscreen orientation corrections are backend-specific. The reference corrects its OpenGLES path, not CanvasKit globally. Confirm with readable asymmetric content on the destination renderer.
- Prefer GPU image capture and reuse; CPU PNG conversion in the drag loop creates lag. Native platform views/external textures require separate verification.
- After switching integration-test/debug/release modes, allow plugin registration regeneration; blindly passing `--no-pub` caused stale registrant state in the tested Flutter setup. Do not force that build sequence on an unrelated stable build.
- For a switch, keep native gesture displacement and the optical preview in agreement; the example uses `DragStartBehavior.down`. Give vertical scroll cancellation to the parent and leave persistence to the native callback. The [switch reference](switch-model.md) has a different sampler/uniform layout from navigation.

## WinUI 3 / Win2D / Direct2D

- ComputeSharp vector operators are shader intrinsics; do not use them for CPU uniform arithmetic. In the native renderer, dividing a `Float4` by lift produced a zero inverse matrix, removing normals, refraction and rim lighting while a standalone shader probe still passed. Compute scalars/System.Numerics first, construct the uniform last, and inspect actual native constants/output as well as probe output.
- On dark glass, a pointer glint, press shadow, tint and blur can combine into a visible oval wash. Identify each layer with matched clear/control renders; keep surface-edge lighting separate from interior lighting so a requested clear lens can disable the latter. A model that is transparent over a pale scene may still look foggy over a dark navigation background.

- Build the effect graph in one pixel coordinate space. In this port, complex shader samplers failed with `D2DERR_INVALID_GRAPH_CONFIGURATION` when implicit DPI compensation entered the graph. Rendering to a 96-DPI target sized in physical pixels, then presenting once in XAML DIP, avoided that failure. Validate scaling and transforms rather than hardcoding DPI to hide it.
- `RenderTargetBitmap` can contain overflowing descendants. Save its actual dimensions and XamlRoot rasterization scale. A GPU-downsampled source still needs the original pixel-to-DIP mapping.
- Composition backdrop blur is a useful fallback; it is not displaced scene sampling. Report shader readiness only after successful scene capture and drawing. Dispose CanvasControl resources with the visual tree.
- Observe native routed input with one owner per component. Preserve native ButtonBase capture and Click; do not capture touch that should scroll, or selectable text/child controls. Make decorations hit-test invisible and reserve draw overflow separately.
- In the tested WinUI control, `Grid.CornerRadius` on the optical host clipped outward deformation even with negative child margins. Use a separate material geometry property such as `SurfaceCorners`; leave the host's corner clipping unset. Compare outside-layout pixels in the visible window, because a GPU target can look correct while the host cuts off every outward bulge.
- A frame exported from CanvasRenderTarget proves shader output, not final XAML compositing. `PrintWindow` returned a stale solid fallback even while the visible window showed GPU glass. Use a current visible-window capture for host evidence; check foreground, occlusion, unlocked desktop and freshness.
- Moving the cursor with `SetCursorPos` alone left captured WinUI pointer coordinates stale in this environment. Inject a real move event for automation and verify both received input and visible shape change; correct cursor coordinates alone do not establish routing.
- The standalone demo must call its generated `App.InitializeComponent()` and package the required XAML dictionaries, PRI, fonts/images and runtime dependencies. Starting from a packaged host can affect `ms-appx` resource identity; in this environment shell activation of the executable isolated the demo correctly. Diagnose before applying that workaround elsewhere.
- When moving externally linked assets into the project tree, check SDK default Content inclusion. Adding the same local image again with `Include` produced duplicate PRI entries; `Update` configured the existing item correctly. Audit `.gitignore`: ignored manifests can make a local build succeed but a clean clone fail.

## Diagnosing demo/host differences

Compare the same physical gesture first: a short tap, held drag or keyboard activation. Read effective reduced-motion and system-effects settings, enabled/busy state, shader/capture readiness and the resolved template/material mode before changing spring or optical parameters. A demo's autoplay may exercise a different path from a real host tap. Inspect the event/controller path and actual uniforms when one works and the other does not.

Keep scoped test overrides separate from saved user preferences and restore temporary changes. When another workflow is using a simulator or moving its page, use an independent instance or wait for access within the authorized scope. Treat interrupted or stale captures as invalid evidence. Before concluding that a published demo differs, check the deployed commit and refresh stale page assets; restore temporary browser cache/debug overrides.

## Web and other native hosts

Separate portable optics/motion from the capture adapter. For web, CSS backdrop blur alone does not provide arbitrary refractive displacement. WebGL/WebGPU/canvas shaders need a usable, permitted scene texture; ordinary DOM, video and cross-origin sources have different capture/security constraints. Do not promise transparent access to everything behind an element.

For other native APIs, map the same contract to their capture/composition/shader facilities: scene source, coordinate transform, shape field, material, motion, hit testing and lifecycle. Verify current official APIs, external texture support, GPU limits and accessibility behavior. If the platform lacks a needed capability, provide and identify a fallback or a scoped experimental prototype; do not label untested ports complete.

## Updating the skill and examples

Use the tested repository demo as the source for `assets/reference_flutter`. Refresh the whole mapped bundle so its navigation, switch, shaders, tests and licenses do not become an undocumented second implementation. The [sync helper](../scripts/sync_skill.py) uses Python 3.10+ and the standard library. It checks by default; `--write` explicitly copies changed or missing package files. It preserves extra destination files and refuses overlapping source/destination paths.

From the demo repository root:

```sh
python skills/flutter-liquid-glass/scripts/sync_skill.py --demo-root .
python skills/flutter-liquid-glass/scripts/sync_skill.py --demo-root . --write
```

To check or update an installed copy, invoke the helper from the authoritative package and provide the actual installed skill directory:

```sh
python skills/flutter-liquid-glass/scripts/sync_skill.py --install-to /path/to/skills/flutter-liquid-glass
python skills/flutter-liquid-glass/scripts/sync_skill.py --install-to /path/to/skills/flutter-liquid-glass --write
```

After a write, repeat the check without `--write`. Verify the loaded package path and new widget/shader assets; a successful repository push does not update a separate installed copy. Structural skill validation checks packaging/frontmatter only. Use the tap, color, destination and QA-promotion scenarios in [acceptance.md](acceptance.md) to evaluate decisions, and run the bundled Flutter tests when its source changes.

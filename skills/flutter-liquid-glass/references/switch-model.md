# Switch gestures and the current reference

Use this reference for boolean switches. A command button retains Click/Command semantics; navigation retains selection semantics. Determine the actual component and destination before copying either behavior.

## Choose the requested behavior

Treat appearance, optics and interaction as separate choices. A motion/refraction adjustment preserves confirmed resting geometry, colors and opacity. When the user requests the demo's appearance in another app, apply those choices to that named destination. A reference screenshot does not change which project is being edited.

For the guided tap used by the current example:

| Input | Visual behavior | Semantic behavior |
| --- | --- | --- |
| Short tap at rest | Rise at the original end, travel while expanded, shrink after arrival; mirror for the opposite direction | Native pointer-up commits once; optical completion does not commit again |
| Held horizontal drag | Follow pointer targets with continuous springs; stop/reverse without resetting velocity | Preview only until release; resolve the endpoint once |
| Re-grab during a tap/recoil | Continue from the visible pose and velocity | New pointer owns the gesture; do not replay stale callbacks |
| Cancel or vertical scroll takeover | Return to the prior semantic state and clear optical tracking | No new commit; parent scrolling remains usable |
| Keyboard or accessibility toggle | Preserve the host's focus, activation and announcements | Native activation owns the single state change; pointer-pressure choreography is optional |
| Reduced motion, disabled or unavailable optics | Use understandable native/static feedback; cancel pending deformation | Keep native state, disabled and failure behavior |

For a tap, physical pointer-up and the optical release are different events. Do not immediately collapse the lens while asking its position to travel. Track the gesture's elapsed hold so a long hold does not repeat the initial lift. Keep the automatic journey in the same motion owner used by real taps; an autoplay-only animation does not establish demo/host parity. Preserve the host's existing persistence, busy state and failure recovery.

Changing tap pace should preserve the three phases and their smooth transitions. Direct manipulation still follows real pointer time. If the user requests another tap model, follow that contract; the guided model is not mandatory for every platform switch.

## Approved example settings

The implementation snapshot is [FlutterLiquidglass 392b27e](https://github.com/zhouwu97/FlutterLiquidglass/tree/392b27ec0e42626d2c7c03d7ba8491419c491aac). These are this example's settings, not universal design requirements:

| Setting | Example value or policy |
| --- | --- |
| Rail | 56 × 30 logical pixels / DIP |
| Ordinary thumb | 30 × 24, white |
| Settled held thumb | Approximately 52 × 32; transient spring strain/overshoot can be larger |
| Endpoint travel | 20 logical pixels / DIP |
| Containment | The enlarged lens can protrude outside the rail; reserve paint space for its maximum shape |
| On rail | Opaque `#2AD34D` |
| Off rail | Light `#CFCBD3`, dark `#5B586A` |
| Color timing | Start a short RGB transition after the visible thumb crosses the midpoint; a pointer target alone does not change the rail |
| Guided pace | Motion clock × 1.15 after the accepted pace adjustment; manual drag keeps real time |

At this size, a 32-high held lens cannot fit inside a 30-high rail. Forcing containment changes the approved geometry and hides the clear shoulders. Position, scale, mask, normals and refraction must use the same deformed shape; inspect host clips as well as shader pixels. Retain the ordinary thumb until the optical path has actually drawn successfully.

The rail and the lens have different material roles. Preserve the opaque rail when strengthening its refraction. Composite the current rail into the independent background source, then sample that composite through the lens. Check the outside shoulders against a patterned background; reducing the rail's opacity is not an optical-strength adjustment. Use host colors when adapting motion alone, and reference colors when the requested appearance requires them.

The current controller uses a .14 model-second lift window, .28 target-travel interval, and spring-driven arrival before optical release. The 1.15 clock rate compresses the guided gesture; these intervals are not a fixed total duration. A real hold counts toward the lift. Quick re-grabs and repeated taps must not teleport the visible lens to an endpoint.

## Implementation entry points

- Flutter [switch widget](../assets/reference_flutter/lib/widgets/liquid_glass/liquid_glass_switch.dart): real Switch input, keyboard, semantics and native commit above the optical painter.
- Flutter [dynamics](../assets/reference_flutter/lib/widgets/liquid_glass/liquid_glass_dynamics.dart): `grab`, `dragTo`, `tapTo`, `releaseTo` and `snapTo`.
- Flutter [scene capture](../assets/reference_flutter/lib/widgets/liquid_glass/liquid_glass_scene.dart): independent background, optional background composition and local capture bounds. Do not choose an ancestor containing the switch as its source.
- Flutter [shader](../assets/reference_flutter/shaders/liquid_glass_switch.frag), [motion tests](../assets/reference_flutter/test/liquid_motion_test.dart) and [GPU tests](../assets/reference_flutter/test/liquid_optics_test.dart).
- Windows [shared control/model/template](https://github.com/zhouwu97/FlutterLiquidglass/tree/392b27ec0e42626d2c7c03d7ba8491419c491aac/examples/winui-liquid-glass/src/Demo) and [standalone switch preview](https://github.com/zhouwu97/FlutterLiquidglass/tree/392b27ec0e42626d2c7c03d7ba8491419c491aac/examples/winui-liquid-glass/src/SwitchDemo). Include `SwitchTrackShader`, `LiquidLensPreset`, `GlassToggle.xaml` and its merged dictionary; sharing only the controller is incomplete.

In Flutter, retain the native drag's initial displacement (`DragStartBehavior.down` in this example) so its release decision matches the optical preview. In WinUI, native ToggleSwitch is sealed; the example uses a Control with TogglePattern and IsOn/Toggled. Preserve each destination's native hit area, event ownership and cancellation behavior.

## Flutter switch shader contract

This contract belongs only to `liquid_glass_switch.frag`: **23 scalar floats and one sampler**. Navigation uses a separate 29-float/two-sampler contract in [reference-model.md](reference-model.md). WinUI's managed shader constants use their own declaration.

| Float index | Meaning |
| --- | --- |
| 0–1 | Painter size |
| 2–5 | Capture rectangle in painter-local logical coordinates |
| 6–7 | Lens center |
| 8–9 | Lens half-size |
| 10–11 | Pointer/light position |
| 12 | Press activation |
| 13 | Stretch |
| 14–15 | Bend |
| 16 | Motion energy |
| 17 | Comparison mode |
| 18 | DPR |
| 19 | Sheen |
| 20–22 | Current rail RGB |

Sampler 0 is the background excluding the switch. The shader composites the rail before refracting it. Change Dart setters and GLSL declarations together; validate the OpenGLES-specific Y correction on that backend without applying it to CanvasKit. Use the [acceptance checks](acceptance.md) for matched geometry, color preservation and real short-tap/drag verification in both demo and host.

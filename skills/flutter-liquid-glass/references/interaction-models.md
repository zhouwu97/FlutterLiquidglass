# Interaction models

## Fixed surface with a local pull

Use when the user says the card stays in place and only deforms. Separate a stable layout/body from an elastic influence field near the grabbed edge. Do not translate the host, scale its content, shear the full rectangle or reuse a moving navigation lens's transform. These all can look like relocation despite an unchanged center.

One implementation:

1. Keep the pointer's initial position. Project it to the nearest relevant boundary to locate an influence anchor; keep this anchor stable throughout the hold.
2. Map pointer displacement to a bounded pull vector with a saturating response, then spring each vector component. Bound it by the available paint margin and by the field's radius to avoid folded edges.
3. In the field's local coordinates, evaluate a smooth, compact-support weight around the anchor. Multiply by a boundary mask that vanishes in the body. Apply the inverse displacement only inside this support before evaluating the original shape SDF.
4. Compute coverage, numerical/analytic normal, refraction and highlights from that result. Keep scene mapping in host coordinates so the whole texture does not slide.
5. On release/cancel, target zero pull and preserve velocity. On re-grab during recoil, avoid instantly relocating an existing nonzero field: interpolate its influence anchor or keep a decaying old field while starting the new one.

For a rounded rectangle, an example support is `q = saturate(1 - dot(p-anchor,p-anchor)/radius²)` followed by `q²(3-2q)`. An interior mask can depend on normalized distance toward the boundary. General paths need a boundary-distance/nearest-point equivalent; do not pretend a rectangular mask fits every shape.

Local bulging can legitimately change the silhouette's area centroid. Test that the body's reference position, untouched corners/edge segments and foreground remain fixed. A centroid-only invariant rejects useful local deformation while accepting a globally skewed card.

The example uses bounded vector springs and a 28-DIP paint margin; these values are tied to its amplitude and geometry. Recalculate for the destination shape, touch size, scale and DPI. Do not turn that margin into layout padding or a larger clickable region.

Tune press response and recoil separately from movement. A fixed local surface still needs an understandable initial press and visible settling; in the WinUI example a small outward press bulge and underdamped pull springs produce that response without moving the body. Check sign reversal/overshoot in the released field, and verify it survives host clipping. Merely lowering damping cannot repair a clipped optical layer.

## Tethered component that returns to rest

Use when the requested reference includes temporary travel of the whole component. Move surface and crisp foreground with one centered affine pose. Position/press springs drive velocity strain and lag bend; on release target position and pressure back to zero without discarding velocity. A held pointer that stops moving should stop strain/bend while retaining a slight pressed lift.

Pointer gain and travel limit are host choices. The studied design-systems controller uses panel/button limits 75/18; the WinUI host was tuned to 12/4 DIP with gain 0.18 after user feedback. These are examples, not universal requirements. Compare against a pinned reference trajectory before changing the solver to compensate for a scale preference.

If the host already applies the affine stretch, the shader must not repeat it in the SDF. Use inverse-transpose for world normals and the inverse affine linear part to map world optical displacement back to local texture coordinates. Keep scene sampling anchored in source coordinates so the background does not travel with the component. Bend still deforms the local SDF. Preserve original transforms and account for the host's transform origin.

Use root/scene pointer coordinates for travel, not coordinates inside the already moving element. Ignore capture-loss bubbling from a former/child owner. A true drag should suppress native release activation while taps and keyboard commands remain native; test the actual host because transferring capture alone did not cancel a WinUI Button click reliably. Restore any temporary native state after the current routed release event, and on cancellation/unload.

## Moving lens or draggable object

Position is part of the intended interaction. Maintain position, pressure/activation, stretch and bend as continuous state. Derive directional strain from velocity and bending from lag/force. Use an inverse stretch matrix in the SDF and optional reciprocal cross-axis compensation. Do not apply this full-object transform to a fixed local-pull card.

Targets change at pointer events; springs integrate elapsed time. Clamp long frame delta and substep rather than integrating a huge missed interval. Preserve velocity through reversal and release. Include slow drag, fast drag, stop, re-grab, cancellation and multi-pointer ownership in tests. Hardware pressure is optional.

## Navigation and buttons

Keep host state and visual state separate. A navigation spring may continue after a commit; parent page animations must not overwrite its current position. Keyboard and accessibility activation should preserve the host's normal semantics.

For native buttons, observe handled input without stealing native capture or replacing Click/Command. A parent surface must recognize a child interactive owner and abstain. Exclude editing controls, scrollbars and selection handles as appropriate. Watch release/cancel/capture-lost outside the original bounds; unload and reduced-motion transitions must clear tracking and restore the rest state.

One optical layer owns each control. A separate generic button-scale animation combined with shader deformation can move the foreground and double the response. Use static color/opacity feedback for reduced motion and solid fallbacks.

## Switch taps and direct dragging

A switch can rest as an ordinary solid thumb and become a glass lens during interaction. Keep visual preview separate from the saved boolean. Direct dragging follows the pointer with spring inertia; release resolves the destination once, and cancellation returns to the prior state. A short tap can continue its optical gesture after physical pointer-up: rise at the current resting end, travel while expanded, then shrink at the destination. Re-grabbing an unfinished tap starts from the current pose and preserves velocity. The host's native callback owns state commit; the remaining optical phases do not commit again.

Choose rail color timing and containment from the requested reference. Permit overflow when its enlarged lens extends beyond the rail, reserving paint space and checking ancestor clips; constrain it only when containment is part of the selected design. Keep rail opacity, color transition, lens transmission and motion independent. The current example changes color after the visible thumb crosses the midpoint and permits overflow; details and optional parameters are in [switch-model.md](switch-model.md). Warm optical resources before hiding the solid thumb, and retain it until successful shader drawing.

Preserve the host toggle's accessibility pattern, name, state announcements, keyboard focus/space/arrows and disabled behavior. WinUI ToggleSwitch is sealed; use an adapter/template when possible or a Control with explicit TogglePattern peer and IsOn/Toggled semantics. Parent card gestures must exclude it. A prototype that changes model state is insufficient: verify actual pointer drag in both directions, intermediate track color, no premature settings write, cancel, keyboard and automation.

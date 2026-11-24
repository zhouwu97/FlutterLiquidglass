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

## Moving lens or draggable object

Position is part of the intended interaction. Maintain position, pressure/activation, stretch and bend as continuous state. Derive directional strain from velocity and bending from lag/force. Use an inverse stretch matrix in the SDF and optional reciprocal cross-axis compensation. Do not apply this full-object transform to a fixed local-pull card.

Targets change at pointer events; springs integrate elapsed time. Clamp long frame delta and substep rather than integrating a huge missed interval. Preserve velocity through reversal and release. Include slow drag, fast drag, stop, re-grab, cancellation and multi-pointer ownership in tests. Hardware pressure is optional.

## Navigation and buttons

Keep host state and visual state separate. A navigation spring may continue after a commit; parent page animations must not overwrite its current position. Keyboard and accessibility activation should preserve the host's normal semantics.

For native buttons, observe handled input without stealing native capture or replacing Click/Command. A parent surface must recognize a child interactive owner and abstain. Exclude editing controls, scrollbars and selection handles as appropriate. Watch release/cancel/capture-lost outside the original bounds; unload and reduced-motion transitions must clear tracking and restore the rest state.

One optical layer owns each control. A separate generic button-scale animation combined with shader deformation can move the foreground and double the response. Use static color/opacity feedback for reduced motion and solid fallbacks.

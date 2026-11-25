import 'package:bottom_nav_demo/main.dart';
import 'package:bottom_nav_demo/widgets/liquid_glass/liquid_glass_renderer.dart';
import 'package:bottom_nav_demo/widgets/liquid_glass/liquid_glass_dynamics.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:bottom_nav_demo/widgets/liquid_glass/liquid_glass_scene.dart';
import 'package:bottom_nav_demo/widgets/liquid_glass/liquid_glass_switch.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  for (final fps in [30, 60, 120]) {
    for (final on in [false, true]) {
      testWidgets('tap rises, travels and releases in order $fps fps on=$on', (
        tester,
      ) async {
        final motion = LiquidGlassDynamics(vsync: tester, index: on ? 1 : 0)
          ..configure(20);
        addTearDown(motion.dispose);
        motion.grab();
        motion.tapTo(on ? 0 : 1);
        var lifted = false, arrived = false, shrank = false;
        var previous = 0.0;
        for (var i = 0; i < fps * 2; i++) {
          motion.advance(1 / fps);
          final travel = on ? 1 - motion.position : motion.position;
          expect(travel, greaterThanOrEqualTo(previous - .001));
          if (travel < .02 && motion.pressure >= .8) lifted = true;
          if (travel > .94 && motion.pressure >= .9) arrived = true;
          if (arrived && motion.pressure < .5) {
            expect(travel, greaterThan(.97));
            shrank = true;
          }
          previous = travel;
        }
        expect(lifted && arrived && shrank, isTrue);
        expect(motion.isMoving, isFalse);
        expect(motion.pressure, 0);
      });
    }
  }

  testWidgets(
    'trial switch keeps native commit, keyboard and disabled semantics',
    (tester) async {
      final source = LiquidGlassSceneSource();
      addTearDown(source.dispose);
      var value = false, enabled = true, changes = 0;
      late StateSetter rebuild;
      await tester.pumpWidget(
        MaterialApp(
          home: StatefulBuilder(
            builder: (context, setState) {
              rebuild = setState;
              return Scaffold(
                body: Center(
                  child: LiquidGlassSwitch(
                    label: 'trial switch',
                    source: source,
                    value: value,
                    onChanged: enabled
                        ? (next) => setState(() {
                            value = next;
                            changes++;
                          })
                        : null,
                  ),
                ),
              );
            },
          ),
        ),
      );
      final control = find.byType(LiquidGlassSwitch);
      final gesture = await tester.startGesture(tester.getCenter(control));
      await tester.pump(const Duration(milliseconds: 300));
      expect(changes, 0);
      await gesture.moveBy(const Offset(35, 0));
      await tester.pump(const Duration(milliseconds: 200));
      expect(changes, 0);
      await gesture.up();
      await tester.pumpAndSettle();
      expect(value, isTrue);
      expect(changes, 1);
      await tester.sendKeyEvent(LogicalKeyboardKey.tab);
      await tester.sendKeyEvent(LogicalKeyboardKey.space);
      await tester.pumpAndSettle();
      expect(value, isFalse);
      expect(changes, 2);
      rebuild(() => enabled = false);
      await tester.pumpAndSettle();
      await tester.tap(control);
      await tester.pumpAndSettle();
      expect(changes, 2);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox());
    },
  );

  testWidgets(
    'unavailable scene retains native fallback and vertical scroll cancels preview',
    (tester) async {
      final source = LiquidGlassSceneSource();
      final scroll = ScrollController();
      addTearDown(source.dispose);
      addTearDown(scroll.dispose);
      var changes = 0;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ListView(
              controller: scroll,
              children: [
                const SizedBox(height: 180),
                Center(
                  child: LiquidGlassSwitch(
                    label: 'trial switch',
                    source: source,
                    value: false,
                    onChanged: (_) => changes++,
                  ),
                ),
                const SizedBox(height: 1200),
              ],
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      final control = find.byType(LiquidGlassSwitch);
      final native = find.descendant(
        of: control,
        matching: find.byType(Switch),
      );
      final opacity = find.ancestor(of: native, matching: find.byType(Opacity));
      expect(tester.widget<Opacity>(opacity.first).opacity, 1);
      final cancel = await tester.startGesture(tester.getCenter(control));
      await tester.pump(const Duration(milliseconds: 120));
      await cancel.cancel();
      await tester.pumpAndSettle();
      expect(changes, 0);
      await tester.drag(control, const Offset(0, -90));
      await tester.pumpAndSettle();
      expect(scroll.offset, greaterThan(0));
      expect(changes, 0);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox());
    },
  );

  testWidgets(
    'same distance at different speeds produces different optical deformation',
    (tester) async {
      List<double> drag(double duration, {double hz = 120}) {
        final motion = LiquidGlassDynamics(vsync: tester)..configure(70);
        motion.grab();
        motion.advance(.5);
        var maxStretch = 0.0, maxBend = 0.0;
        final count = (duration * hz).round();
        for (var i = 1; i <= count; i++) {
          motion.dragTo(2.5 * i / count);
          motion.advance(1 / hz);
          if (motion.stretch > maxStretch) maxStretch = motion.stretch;
          if (motion.bend.dx > maxBend) maxBend = motion.bend.dx;
        }
        motion.dispose();
        return [maxStretch, maxBend];
      }

      final slow = drag(1.8), fast = drag(.18), sixtyHz = drag(.18, hz: 60);
      expect(fast[0], greaterThan(slow[0] * 2));
      expect(fast[1], greaterThan(slow[1] * 2));
      expect((fast[0] - sixtyHz[0]).abs(), lessThan(.025));
      final soft = LiquidGlassDynamics(vsync: tester)..grab(pressure: .65);
      final hard = LiquidGlassDynamics(vsync: tester)..grab(pressure: 1.16);
      soft.advance(1);
      hard.advance(1);
      expect(hard.pressure - soft.pressure, greaterThan(.45));
      soft.dispose();
      hard.dispose();
    },
  );

  testWidgets(
    'drag stretches, reverses and relaxes without lifting the finger',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      await tester.pumpWidget(const NavigationDemo());
      final dock = tester.getRect(
        find.byKey(const ValueKey('bottom-nav-floating-dock')),
      );
      final start = tester.getCenter(
        find.byKey(const ValueKey('bottom-nav-selection')),
      );
      LiquidGlassRenderer optics() =>
          tester.widget(find.byType(LiquidGlassRenderer));
      final gesture = await tester.startGesture(start);
      await tester.pump();
      for (var i = 0; i < 18; i++) {
        await tester.pump(const Duration(milliseconds: 16));
      }
      for (var i = 1; i <= 12; i++) {
        await gesture.moveTo(start + Offset(i * 17, -14));
        await tester.pump(const Duration(milliseconds: 16));
      }
      expect(optics().bend.dx, greaterThan(3));
      expect(optics().stretch, greaterThan(.12));
      expect(optics().lens.center.dx, lessThan(start.dx + 204 - dock.left));
      // A held pointer is not a continuing force once the spring has caught up.
      await tester.pumpAndSettle();
      expect(optics().bend.distance, lessThan(.01));
      expect(optics().stretch.abs(), lessThan(.01));
      for (var i = 1; i <= 10; i++) {
        await gesture.moveTo(start + Offset(204 - i * 16, 10));
        await tester.pump(const Duration(milliseconds: 16));
      }
      expect(optics().bend.dx, lessThan(-2));
      await gesture.up();
      await tester.pumpAndSettle();
      expect(optics().bend.distance, lessThan(.01));
      expect(optics().press, lessThan(.001));
      expect(tester.takeException(), isNull);
      expect(tester.binding.hasScheduledFrame, isFalse);
    },
  );
}

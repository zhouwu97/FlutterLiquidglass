import 'package:bottom_nav_demo/main.dart';
import 'package:bottom_nav_demo/widgets/liquid_glass/liquid_glass_runtime.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('native scene, held lens, scroll and dark mode', (tester) async {
    await tester.pumpWidget(const NavigationDemo());
    await tester.pumpAndSettle();
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      await binding.convertFlutterSurfaceToImage();
      await tester.pumpAndSettle();
    }
    expect(liquidGlassRuntimeStatus.value.tier, LiquidGlassTier.a);
    await binding.takeScreenshot('android-light');
    await tester.tap(find.text('网格背景'));
    await tester.tap(find.text('清透材质'));
    await tester.pumpAndSettle();
    final selection = find.byKey(const ValueKey('bottom-nav-selection'));
    final gesture = await tester.startGesture(tester.getCenter(selection));
    await tester.pump();
    for (var i = 0; i < 18; i++) {
      await tester.pump(const Duration(milliseconds: 16));
    }
    expect(tester.getSize(selection).height, greaterThan(72));
    await binding.takeScreenshot('android-pressed');
    final dock = tester.getRect(
      find.byKey(const ValueKey('bottom-nav-floating-dock')),
    );
    await gesture.moveTo(Offset(dock.center.dx, dock.center.dy));
    await tester.pump(const Duration(milliseconds: 100));
    await binding.takeScreenshot('android-drag');
    await gesture.up();
    await tester.pumpAndSettle();
    expect(
      tester
          .widget<Text>(find.byKey(const ValueKey('current-page-title')))
          .data,
      '课表',
    );
    await tester.tap(find.byTooltip('切换深色模式'));
    await tester.pumpAndSettle();
    await binding.takeScreenshot('android-dark');
    await tester.drag(find.byType(CustomScrollView), const Offset(0, -320));
    await tester.pumpAndSettle();
    await binding.takeScreenshot('android-scroll');
    expect(tester.takeException(), isNull);
  });
}

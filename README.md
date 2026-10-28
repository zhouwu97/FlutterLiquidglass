# Flutter 液态玻璃底部导航

五入口导航，使用真实背景纹理与图标纹理进行 GPU 合成。主界面保留液态、悬浮、普通三种样式，新增网格、清透材质和「仅模糊对照」，便于验证折射，而不是仅观察透明度。

## 对照来源

- [LocationSpoofer / AndroidFloatingBottomBar.kt](https://github.com/TaoCultivator/LocationSpoofer/blob/44e1ce221e47499b973fb1a1400fe8e45c9403a8/app-ui/src/main/java/com/vincenthzr/locationspoofer/ui/liquid/AndroidFloatingBottomBar.kt)：导航结构、尺寸、合成次序、按压与回弹。
- [LocationSpoofer / Lens.kt](https://github.com/TaoCultivator/LocationSpoofer/blob/44e1ce221e47499b973fb1a1400fe8e45c9403a8/app-ui/src/main/java/com/vincenthzr/locationspoofer/ui/liquid/Lens.kt)：圆弧截面折射、深度法线与七通道色散。
- [design-systems / renderer.js](https://github.com/ruiqichenbiec/design-systems/blob/7a424c93b9be13cf835b91ea67495fec2ec0584e/lens/lab/design-system/internal/renderer.js)：采样实际场景、Fresnel 边光、双向高光与焦散。[交互演示](https://ruiqichenbiec.github.io/design-systems/lens/lens-showcase-standalone.html)。
- [design-systems / jelly.js](https://github.com/ruiqichenbiec/design-systems/blob/7a424c93b9be13cf835b91ea67495fec2ec0584e/lens/lab/design-system/internal/jelly.js) 与 [jelly-physics.js](https://github.com/ruiqichenbiec/design-systems/blob/7a424c93b9be13cf835b91ea67495fec2ec0584e/lens/lab/design-system/internal/jelly-physics.js)：直接移植速度拉伸、受力弯曲、体积补偿和释放阻尼方程。

这两个参考不是同一套光学模型。这里以 LocationSpoofer 的底栏为结构与折射基准，吸收 Lens 的边光处理；没有宣称与两者同时逐像素相同。

| Before | After | Why |
| --- | --- | --- |
| 静止时底座也关闭折射 | 底座始终开启 24px 高度 / 24px 位移的折射带 | 对齐原生参考的常态玻璃 |
| ImageFilter.shader 不支持时只剩 blur | Paint.shader 显式绑定背景和图标纹理 | CanvasKit 和 Impeller 使用同一合成路径 |
| 正向位移、背景滤镜之上再画图标 | 向内折射；图标作为第二层纹理参与透镜采样 | 避免「背景变形，图标浮在玻璃上」 |
| 统一乘 0.65，图标仅缩放 1.04 | 56→78px 胶囊膨胀，内容 1→1.2 | 保留参考的按压体积变化 |
| 两套坐标、裁剪和高光绘制 | 同一 SDF 同时决定轮廓、法线、折射和高光 | 避免边缘错位、接缝和双图标 |
| 拖动时刚性平移、固定放大 | 六个持续积分的弹簧驱动位置、按压、速度拉伸和双轴弯曲 | 慢拖、快甩、换向、急停会产生不同形变 |
| 纯色占位页面 | 可滚动卡片、网格与模糊对照 | 能直接检查背景是否真的弯折 |

## 渲染与交互

1. `LiquidGlassScene` 将页面单独放入背景图层，导航始终不进入自身采样。
2. 只捕获导航周围额外 48px 的区域，DPR 上限为 2；使用 GPU 的 `toImageSync`，没有 PNG 编码、CPU 像素读回或异步截图追帧。
3. 背景模糊一次（默认 6px），与静态缓存的两行图标/文字图集合成底座。
4. 选中透镜采样上述合成结果：按压时 10px 折射带、14px 向内位移、0.5 色散、深度法线；默认静止态为参考中的低对比选中底色。
5. 同一套经过逆矩阵和弯曲场变形的 SDF 生成轮廓、法线、折射、边光和接触阴影。OpenGLES 对两张离屏纹理做 Y 翻转修正，CanvasKit 不翻转。
6. 拖动位置连续，松手提交页面并弹簧吸附；支持中途重新抓取、边界阻尼、取消、多指保护、外部切页、键盘 Home/End/方向键和独立无障碍动作。
7. Android 用少量 Kotlin 接收本地重力传感器，驱动高光方向；材质、导航和动画仍全部在 Flutter。传感器缺失时使用指针光源，后台注销监听。减少动态效果时关闭位移装饰和按压膨胀，保留导航能力。

渲染只随现有帧刷新；没有定时器或永不停歇的采样循环。页面中的 PlatformView（原生地图、WebView）、视频外部纹理等仍受 Flutter 离屏栅格化能力限制，需要在实际宿主中验证。当前示例全部为 Flutter 内容。

### 速度与力度如何驱动动画

`LiquidGlassDynamics` 沿用参考的受力式 `a = (target - value) * stiffness - velocity * damping`，每步不超过 1/180 秒。位置刚度 260，按住时阻尼 22，释放时 17；速度越大，`stretch.target = min(speed / 2400, .25)` 越大，再经过 230/15 的弹簧。沿速度方向拉伸，垂直方向取倒数压缩，保持面积。弯曲目标是 `clamp((target - value) * .12, -11, 11)`，经过 190/14 的独立弹簧，进入 shader 的 `p -= bend * (1 - q²) * .7`。

每次指针移动只更新目标，不重置运动速度。停止拖动时速度自行衰减，松手和换向时保留动量，因此不存在固定时长的“甩动动画”。参考的强度默认 .7，这里使用 1，以适应较小的导航组件；按压尺寸仍采用 LocationSpoofer 的 56→78px。参考的布尔按压扩展为设备可用时的归一化压力；鼠标和固定压力的触屏使用普通按住值 1，不声称能测量其真实按压力。减少动态效果时直接到达目标。

## 接入

```dart
import 'widgets/bottom_nav.dart';
import 'widgets/liquid_glass/liquid_glass_scene.dart';

// 放在 Scaffold.body 中。background 应覆盖整个导航后方，包含滚动内容。
LiquidGlassScene(
  background: pageContent,
  overlay: Align(
    alignment: Alignment.bottomCenter,
    child: BottomNav(
      currentIndex: index,
      onTap: (value) => setState(() => index = value),
      style: BottomNavStyle.liquidGlass,
      badges: const {1: true},
      // glassBlur: 1.5, glassTint: .20, // 可选清透材质
      // compareGlass: true, // 关闭折射、高光，保留同样的 blur/tint
    ),
  ),
)
```

正常/悬浮样式无需背景容器；液态样式缺少 `LiquidGlassScene` 或 shader 加载失败时会显示基础导航，并通过运行状态明确报告降级。`LiquidGlassRuntimeStatus.tier == a` 只在成功捕获和绘制后设置。

## 运行与验证

```sh
flutter pub get
flutter run -d chrome
flutter run -d emulator-5584
flutter analyze
flutter test
flutter drive --driver=test_driver/verification_driver.dart --target=integration_test/navigation_test.dart -d emulator-5584
flutter build apk --release
```

`flutter devices` 可查看本机设备 ID。测试覆盖导航、取消与多指、减少动态效果、键盘、深色/大字体、外部切页；运动测试比较同一距离的快慢拖动、60/120Hz、不同压力、停手和反向拖动。光学测试比较 shader 输出像素，检查折射位移、左右形变轮廓、透明边界和 DPR。场景测试验证按压尺寸、滚动采样和静止时不自行调度帧。截图输出到 `build/verification/`，Android 集成测试另外记录设备端浅色、按压、拖动、深色和滚动状态。构建、测试应顺序执行；在 debug 集成测试与 release 之间切换时使用上面的完整命令，不加 `--no-pub`，以重新生成对应模式的插件注册信息（Flutter 3.41.8）。

五个入口仍为演示页面，未接业务。跨 GPU 的像素级完全一致和物理手机的帧率，需要针对目标设备单独验收；模拟器 debug 模式不作为帧率结论。

## 代码与许可

- `lib/widgets/liquid_bottom_nav.dart`：手势、连续位置、可中断弹簧、语义。
- `lib/widgets/liquid_glass/liquid_glass_dynamics.dart`：移植的六弹簧运动模型、速度和受力到光学形变的映射。
- `lib/widgets/liquid_glass/liquid_glass_scene.dart`：独立背景和局部 GPU 捕获。
- `lib/widgets/liquid_glass/liquid_glass_renderer.dart`：纹理生命周期、图集、shader 调用。
- `shaders/liquid_glass.frag`：底座与选中透镜的完整光学合成。
- `android/.../MainActivity.kt`：重力感应桥接。

原有普通/悬浮导航及主题保留 [SYLUlive MIT 许可](licenses/SYLUlive-MIT.txt)。修改后的光学算法保留 [AndroidLiquidGlass Apache-2.0](licenses/AndroidLiquidGlass-Apache-2.0.txt) 及 [design-systems MIT](licenses/design-systems-MIT.txt) 署名。Noto Sans CJK SC 字体遵循 [SIL OFL](licenses/NotoSansCJK-OFL.txt)。LocationSpoofer 只取底栏/透镜参考，不包含任何定位修改功能。

## 迁移复盘与复用

[完整替换 SYLUlive 的复盘](docs/liquid-glass-retrospective.md)说明最初效果僵硬的原因、业务接入边界及验证结果。[flutter-liquid-glass skill](skills/flutter-liquid-glass/SKILL.md)记录可复用的运动、采样和验收方法。

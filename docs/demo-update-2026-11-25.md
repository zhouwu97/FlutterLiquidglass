# 开关与按钮 Demo 更新（2026-11-25）

基准提交：`a37134be646771512854a5d4570bb819f125da58`。本次只同步独立示例、光学组件、测试和说明，不包含业务账号、接口、设置文件或本地构建物。

## 行为

- Flutter 网页增加绿色／灰色胶囊开关，普通滑块为白色扁圆形。独立背景源排除开关自身，轨道保持不透明颜色并参与折射。
- 轻点先在原端鼓起，再平滑移动，到另一端收回。点击播放为初调版的 1.15 倍速度，保持三阶段顺序；真实拖动不加速，状态只在松手时提交一次。
- Windows 增加独立放大开关项目，浅色、深色、实际尺寸和四倍预览直接链接综合 Demo 中的组件、模板、模型和 shader。`scripts/run.ps1 -Switch` 构建并启动它。
- 综合 Windows Demo 的按钮采用同款透镜光学，按住显示玻璃，松手恢复；保留文字编辑、键盘、轻点单次触发和拖动取消。
- Flutter 可复用资源包同步相同示例和组件；WinUI CI 同时构建两个入口。

## 本地验证

| 检查 | 结果 |
| --- | --- |
| `flutter analyze lib test` | 无问题 |
| `flutter test --reporter expanded` | 21 项通过 |
| `flutter build web --release --base-href /FlutterLiquidglass/ --no-web-resources-cdn --no-wasm-dry-run` | 通过 |
| `dotnet test tests/LiquidGlass.Tests.csproj -c Release` | 58 项通过 |
| 两个 WinUI 项目 Release 自包含发布构建 | 通过 |
| `dotnet run --project tools/GlassProbe/GlassProbe.csproj -c Release -- build/gpu` | 36 项 GPU 检查通过 |

Windows 首次独立构建发现遗漏共用的 `LiquidLensPreset`，补齐源文件后重新构建通过。原内联旧开关模板已移出 `Glass.xaml`，统一使用 `GlassToggle.xaml`，避免复用时套用旧尺寸。

原生窗口采用 Windows 11、WinUI 3 / Win2D / Direct2D、约 114.6% DPI，通过 OS 鼠标、键盘与 UIA 状态读取验证。放大 Demo 双向轻点录制 72 帧；综合 Demo 验证双向预览、松手提交、Esc 取消、键盘及 UIA。相同按住轮廓的开关折射／关闭折射平均像素差为 11.50，按钮差为 3.74。按钮正常松手只触发一次，拖动抑制激活，减少动画和输入框选择正常。

放大预览按实际内容高度布局，修复较高 DPI 下「放大查看」文字被裁切。更新该截图时首次前置状态校验发现预览已开启，拒绝该次捕获；明确恢复独立 Demo 的关闭状态后重新捕获，并还原原状态。没有将失败捕获当作验收证据。

网页使用本地 Release 构建及真实浏览器指针，验证默认宽度与 430×932 手机布局、浅色／深色、Space 键、按住拖动不提前提交及松手切换。浏览器未记录 error 级日志。截图位于 `docs/images/demo-switch-*.jpg`，Windows 实际按住截图为 `docs/images/winui-switch-preview.png`。截图未经生成式处理。

原始窗口录制、状态数据与 GPU 探针输出在 `examples/winui-liquid-glass/build/`，不提交构建目录。跨 GPU 一致性、物理手机帧率和 iOS 仍需对应设备验证。GitHub Actions 与 Pages 的结果以本次推送后对应提交的实际运行结果为准。

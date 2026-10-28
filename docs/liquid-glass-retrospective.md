# 2026-10-28 液态玻璃底栏替换与复盘

## Changed

用户最终要求整套采用已验收的 Flutter 演示底栏，不保留旧底栏。此次将其完整接入 SYLUlive：440px 最大宽度、16px 横向留白、蓝色选中态、五个图标、玻璃底座与透镜、实时背景/图标折射、速度拉伸、受力弯曲和释放回弹。底栏默认高画质、强度 1；旧普通/悬浮模式不会恢复旧外观。设置页移除旧样式选项，预览直接使用真实组件。

新材质使用独立的 bottom_nav_performance_mode_v2 和 bottom_nav_animation_intensity_v2 偏好。升级首帧使用新默认值，之后用户主动调整的性能/强度仍持久化。旧样式 setter 保留兼容签名但统一映射到液态玻璃。高性能模式保留完整折射，只将运动强度预设为 35%；高画质预设为 100%；自动按设备使用 35% / 65% / 100%。切换模式会恢复对应预设，也可再用滑块微调并持久化。

首页采用 LiquidGlassScope + LiquidGlassBackground，将壁纸与业务内容一起捕获，排除底栏本身；保持 Scaffold 的安全区、键盘和悬浮按钮布局。玻璃在拖动/回弹期间拥有视觉位置，防止首页转场 notifier 反向覆盖弹簧。宽屏继续采用响应式侧栏，切换断点保留页面状态，不再由旧底栏样式决定宽屏布局。

用户明确指定了截图中的蓝色与液态运动，因此该组件局部采用演示色和连续弹簧，属于本次任务明确授权的设计例外；没有改全局品牌色或全局 AppMotion。

## 为什么一开始效果不对

1. 最初按静态外观拆解了透明度、模糊、高光和位移，没有完整追踪参考中的 jelly.js、jelly-physics.js、optical-motion.js。结果是胶囊整体移动或固定缩放，慢拖、快甩、反向时轮廓相近，看起来硬。
2. 真实效果需要连续速度、指针与透镜的位移差驱动拉伸和双轴弯曲。现在将反向拉伸矩阵和弯曲作用到同一个 SDF，覆盖边界、法线、折射和高光一起变化；释放不清空动量。
3. 早期 ImageFilter.shader 路径在部分后端降级，只剩模糊。现改成 Paint.shader 显式绑定场景与图标纹理，完成捕获和绘制之后才报告完整材质状态。
4. 背景和前景必须一起参与折射；单独在玻璃上再画普通图标会显得浮在表面。坐标、采样留白和 Android OpenGLES 离屏纹理方向也需要一致。
5. 仅检查组件存在或 shader 字符串不能验证液态效果。现在测试实际像素位移、左右变形轮廓、DPR，以及不同速度/压力/帧率下的运动差异。
6. 演示通过不等于业务接入完成：原项目壁纸在全局容器中，首页还会写视觉位置。直接复制文件会漏采壁纸、造成两个动画控制源相互干扰，因此同步改了采样边界和状态归属。

这不是 Flutter 无法实现，而是最初对参考的运动与光学耦合拆解不完整。当前普通鼠标或不支持压力的触屏不伪造“真实力度”；使用速度和滞后形成受力观感，硬件有有效压力数据时再纳入。

## Preserved

五个入口对应的业务页面、登录守卫、角标、页面状态、启动目标、深层页面恢复、系统减少动态效果与无障碍操作保持可用。其他已存在的未提交业务改动保持原样，不纳入本次提交。未修改依赖版本、服务端接口、正式发布配置或版本号。

## Tests

Flutter 3.41.8 / Dart 3.11.5，Windows。

- 46 项相关测试通过：底栏交互/像素/运动/控制器、设置预览和偏好迁移、真实首页导航与深层页面恢复、主题加载/壁纸/字体设置。
- 液态组件、设置、ThemeProvider 和相关测试静态分析通过；HomeScreen 本次新增问题已清除，原有 1 条 unused_element warning 与 6 条 info 未扩大范围修复。
- 浅色、深色、大字体、拖动截图已人工检查；截图位于 client/build/verification/，不替换跨平台正式 golden。
- Android arm64 release 编译结果见本报告末尾验证记录；属于本地编译检查，不等于已执行正式发布的 CI、安全、服务端兼容性门禁。

复现：在 client 目录运行 flutter test test/widgets/bottom_nav_liquid_glass_test.dart test/widgets/liquid_glass_motion_test.dart test/widgets/liquid_glass_v6_test.dart test/widgets/bottom_nav_controller_test.dart test/screens/settings/bottom_navigation_settings_screen_test.dart test/root_navigation_gesture_test.dart test/theme_provider_sync_load_test.dart test/theme_provider_background_mode_test.dart test/theme_provider_font_size_test.dart test/theme_provider_retired_wallpaper_test.dart；然后 flutter build apk --release --target-platform android-arm64。

## Design QA

P0/P1：本次检查未发现导航阻断、重复提交、状态丢失、捕获自反馈或布局溢出。
P2：模拟器与 widget 像素测试不能替代各型号实体手机的 GPU/续航验收；跨后端不宣称逐像素相同。
P3：高性能/自动模式均保留完整材质。仅后端不支持 shader、加载失败或缺少采样容器时降级，并明确标记运行状态。

## Deferred

实体手机帧率、功耗与真实压力传感器验证；全项目既有分析债务；与本次无关的后台/上传/安全功能改动。工作区原本存在其他未提交改动，本地整包编译包含这些现场文件，本次 Git 提交只包含底栏相关路径。

## 参考与复用

- design-systems: https://github.com/ruiqichenbiec/design-systems/tree/7a424c93b9be13cf835b91ea67495fec2ec0584e
- LocationSpoofer: https://github.com/TaoCultivator/LocationSpoofer/tree/44e1ce221e47499b973fb1a1400fe8e45c9403a8
- 演示仓库: https://github.com/zhouwu97/-Liquid-Glass
- 可复用 skill: ../skills/flutter-liquid-glass/SKILL.md；已安装到本机 Codex skills，并通过 quick_validate.py。保留两份上游算法许可证于 client/licenses/。

## 后续按压与清透修正（2026-10-28）

按下未选中入口时立即将透镜移入该入口并激活按压态，随后跟随手指；松手提交一次导航，取消则回到原页面。已到位的透镜持续持有视觉位置，直到新的明确外部选页或手势，避免父页面旧 tween 将其拉回。

按压过程中降低预模糊和着色遮罩，保留折射、色散与边光；清透对照使用 blur 0 / tint 0.06，与普通材质建立明确差异。真实 QA 输出像素差异测试通过，但尚未重新打包到 Android 复核，不能据此宣称设备上已经达到最终观感。

本轮目标项目 23 项交互、像素与首页导航回归通过；演示项目 12 项测试通过；修改文件静态分析无问题。按用户要求未重新打包、未提交、未推送；现有 APK 和静态网页仍是此前构建产物。

# 演示域名配置

目标地址：https://flutter-liquid-glass-demo.goldenridge10.site/

此域名已添加到现有 Sites 站点，当前状态为 `pending`，HTTPS 证书状态为 `initializing`。需要域名管理员在 `goldenridge10.site` 的 DNS 控制台添加以下记录。名称按相对于根域名的形式列出；如果控制台要求完整域名，请在名称末尾补上 `.goldenridge10.site`。

| 类型 | 名称 | 值 |
| --- | --- | --- |
| CNAME | `flutter-liquid-glass-demo` | `custom-domains.chatgpt.site.` |
| TXT | `_openai-site-verification.flutter-liquid-glass-demo` | `openai-site-verification=XEmuhAjkp42kCwI95GH5BZasZFFzNOwsSKUX7H6ORwY` |
| TXT | `_cf-custom-hostname.flutter-liquid-glass-demo` | `d35a6fa9-23c7-4067-bfbc-2dbb8428311e` |

等待 DNS 传播、域名验证和 HTTPS 证书签发完成后，检查新地址能否正常打开。当前尚未验证新域名可用。

原站点继续提供服务：https://flutter-liquid-glass-demo.goldenridge10.chatgpt.site/

# Skill: 移动端设备模拟测试

## 触发条件
用户说"测试移动端"、"移动端适配"、"手机预览"、"iOS 测试"、"Android 测试"或类似表述。

## 前置条件
- Playwright MCP 已连接（`plugin:playwright:playwright`）
- 或 `scripts/mobile-test.js` 可用

## 执行步骤

### 方案 A: 使用 Playwright MCP（快速检查）
1. 使用 `browser_resize` 工具设置移动端视口：
   - iPhone 15 Pro Max: 430x932
   - Pixel 9 Pro: 412x915
   - iPad Pro: 1024x1366
2. 使用 `browser_snapshot` 截图检查布局
3. 检查：触摸目标大小、文字溢出、水平滚动

### 方案 B: 使用脚本（批量测试）
```bash
# 单设备测试
node scripts/mobile-test.js https://example.com iphone-15-pro-max

# 多设备批量测试
for device in iphone-15-pro-max pixel-9-pro ipad-pro; do
  node scripts/mobile-test.js https://example.com "$device"
done
```

### 检查清单
- [ ] 视口 meta 标签是否正确设置
- [ ] 触摸目标是否 >= 44px（iOS 规范）
- [ ] 无水平滚动溢出
- [ ] 字体大小在移动端可读（>= 16px）
- [ ] 表单/输入框在移动端可用

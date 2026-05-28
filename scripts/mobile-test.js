// ============================================================
// 移动端设备模拟测试脚本
// 基于 Playwright 的设备描述 API
// 用法: node mobile-test.js <url> [device_name]
// 默认设备: iPhone 15 Pro Max
// ============================================================
const { chromium } = require('playwright');

const DEVICES = {
  'iphone-15-pro-max': { viewport: { width: 430, height: 932 }, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1', hasTouch: true, isMobile: true },
  'iphone-se': { viewport: { width: 375, height: 667 }, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1', hasTouch: true, isMobile: true },
  'pixel-9-pro': { viewport: { width: 412, height: 915 }, userAgent: 'Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.0 Mobile Safari/537.36', hasTouch: true, isMobile: true },
  'galaxy-s24': { viewport: { width: 360, height: 780 }, userAgent: 'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.0 Mobile Safari/537.36', hasTouch: true, isMobile: true },
  'ipad-pro': { viewport: { width: 1024, height: 1366 }, userAgent: 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1', hasTouch: true, isMobile: true },
};

const url = process.argv[2];
const deviceName = process.argv[3] || 'iphone-15-pro-max';
const outputDir = process.argv[4] || './mobile-screenshots';

if (!url) {
  console.error('用法: node mobile-test.js <url> [device_name] [output_dir]');
  console.error('设备: ' + Object.keys(DEVICES).join(', '));
  process.exit(1);
}

const device = DEVICES[deviceName];
if (!device) {
  console.error(`未知设备: ${deviceName}`);
  console.error('可用设备: ' + Object.keys(DEVICES).join(', '));
  process.exit(1);
}

(async () => {
  const fs = require('fs');
  const path = require('path');
  fs.mkdirSync(outputDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: device.viewport,
    userAgent: device.userAgent,
    hasTouch: device.hasTouch,
    isMobile: device.isMobile,
  });
  const page = await context.newPage();

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const prefix = `${deviceName}-${timestamp}`;

  console.log(`[${deviceName}] 加载: ${url}`);
  console.log(`[${deviceName}] 视口: ${device.viewport.width}x${device.viewport.height}`);

  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    console.log(`[${deviceName}] 页面加载完成`);

    // 全页截图
    await page.screenshot({ path: path.join(outputDir, `${prefix}-fullpage.png`), fullPage: true });
    console.log(`[${deviceName}] 全页截图已保存`);

    // 视口截图
    await page.screenshot({ path: path.join(outputDir, `${prefix}-viewport.png`), fullPage: false });
    console.log(`[${deviceName}] 视口截图已保存`);

    // 提取关键信息
    const info = await page.evaluate(() => ({
      title: document.title,
      metaViewport: document.querySelector('meta[name=viewport]')?.content || '未设置',
      touchTargets: document.querySelectorAll('a, button, input, select, textarea').length,
      fontSize: getComputedStyle(document.body).fontSize,
      overflowX: document.body.scrollWidth > document.body.clientWidth ? '存在水平滚动' : '正常',
    }));
    console.log(`[${deviceName}] 标题: ${info.title}`);
    console.log(`[${deviceName}] Viewport meta: ${info.metaViewport}`);
    console.log(`[${deviceName}] 可交互元素: ${info.touchTargets}`);
    console.log(`[${deviceName}] 水平溢出: ${info.overflowX}`);

    // 保存页面信息
    fs.writeFileSync(path.join(outputDir, `${prefix}-info.json`), JSON.stringify(info, null, 2));

  } catch (err) {
    console.error(`[${deviceName}] 错误: ${err.message}`);
  }

  await browser.close();
  console.log(`[${deviceName}] 完成`);
})();

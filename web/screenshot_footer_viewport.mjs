import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);
await page.screenshot({ path: '../docs/tangkapan/footer_ponsel_390px_viewport.png', fullPage: false });
console.log('Selesai');
await browser.close();

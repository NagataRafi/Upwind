// Cek pindah wilayah ke Kalteng (FR-W1) dan tangkap layar desktop
import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 844 } });
await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
await page.locator('button', { hasText: 'Kalteng' }).first().click();
await page.waitForTimeout(2500);
await page.screenshot({ path: '../docs/tangkapan/kalteng_normal_desktop_1440px.png', fullPage: true });
console.log('Selesai kalteng');
await browser.close();

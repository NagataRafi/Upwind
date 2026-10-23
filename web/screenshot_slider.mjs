// Cek FR-W9: klik tengah slider waktu, bingkai harus berganti (waktu Waktu Bingkai berubah)
import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 844 } });
await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);
const before = await page.locator('text=Waktu Bingkai').first().textContent();
const box = await page.locator('input[type="range"]').first().boundingBox();
await page.mouse.click(box.x + box.width * 0.5, box.y + box.height / 2);
await page.waitForTimeout(2000);
const after = await page.locator('text=Waktu Bingkai').first().textContent();
console.log('Sebelum:', before, '| Sesudah:', after, '| Berubah:', before !== after);
await page.screenshot({ path: '../docs/tangkapan/interaksi_slider_waktu_desktop_1440px.png', fullPage: false });
await browser.close();

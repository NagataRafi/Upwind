// Cek interaksi: perbarui dengan CSS file id, klik baris Hulu Asap dan periksa lapisan filter
import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 844 } });
await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);
// FR-W6: klik baris HP-02 -> peta harus menyorot (marker bawa reaksi, tangkap layar)
await page.locator('button, [role="button"], div.cursor-pointer', { hasText: 'HP-02' }).first().click();
await page.waitForTimeout(800);
await page.screenshot({ path: '../docs/tangkapan/interaksi_sorot_hotspot_desktop_1440px.png', fullPage: false });
// FR-W3: buka kontrol lapisan, nyalakan Ketidakpastian, tangkap layar
await page.locator('button', { hasText: /Lapisan|Kontrol/i }).first().click();
await page.waitForTimeout(400);
const sw = page.locator('text=Ketidakpastian Model').first();
await sw.click();
await page.waitForTimeout(800);
await page.screenshot({ path: '../docs/tangkapan/interaksi_ketidakpastian_desktop_1440px.png', fullPage: false });
console.log('Selesai interaksi');
await browser.close();

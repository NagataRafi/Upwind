import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 844 } });
await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);
const slider = page.locator('input[type="range"]').first();
// pindah ke idx 1 (awan tebal), 3 (poor), 2 (motion unavailable / after_gap moderate)
for (const [n, name] of [[1, 'awan_tebal'], [3, 'poor'], [2, 'moderate_motion_unavail']]) {
  await slider.focus();
  let cur = await slider.inputValue();
  // walk: gunakan change via evaluate set value event biar pasti per indeks
  await slider.evaluate((el, v) => {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(el, String(v));
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }, n);
  await page.waitForTimeout(1800);
  const t = await page.locator('text=Waktu Bingkai').first().textContent();
  console.log(name, t);
  await page.screenshot({ path: `../docs/tangkapan/frame_${name}_desktop_1440px.png`, fullPage: false });
}
// kembali ke normal lalu matikan mask sekarang
await slider.focus();
await slider.evaluate((el) => {
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  setter.call(el, el.max);
  el.dispatchEvent(new Event('input', { bubbles: true }));
});
await page.waitForTimeout(1200);
await page.locator('button', { hasText: /Lapisan|Kontrol/i }).first().click();
await page.waitForTimeout(400);
await page.locator('text=Mask Asap Karhutla').first().click();
await page.waitForTimeout(700);
await page.screenshot({ path: '../docs/tangkapan/mask_off_desktop_1440px.png', fullPage: false });
console.log('Selesai berlapis');
await browser.close();

import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 844 } });
await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
await page.waitForTimeout(1800);
const slider = page.locator('input[type="range"]').first();
for (const [v, name] of [[6, 'moderate_gap'], [5, 'uncomputable']]) {
  await slider.evaluate((el, vv) => {
    const st = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    st.call(el, String(vv));
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }, v);
  await page.waitForTimeout(1500);
  console.log(name, await page.locator('text=Waktu Bingkai').first().textContent());
  await page.screenshot({ path: `../docs/tangkapan/frame_${name}_desktop_1440px.png`, fullPage: false });
}
console.log('Selesai');
await browser.close();

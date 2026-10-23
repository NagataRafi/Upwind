import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 844 } });
const reqs = [];
page.on('request', (r) => { if (r.url().includes('/data/')) reqs.push(r.url()); });
await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
await page.waitForTimeout(2000);
const initial = reqs.length;
await page.locator('input[type="range"]').first().evaluate((el) => {
  const st = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  st.call(el, '4');
  el.dispatchEvent(new Event('input', { bubbles: true }));
});
await page.waitForTimeout(2500);
const second = reqs.slice(initial);
console.log('permintaan awal:', initial);
console.log('permintaan geser:', JSON.stringify(second, null, 1));
await browser.close();

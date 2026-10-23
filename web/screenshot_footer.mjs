// Cek footer atribusi FR-W14 di ponsel dan desktop
import { chromium } from 'playwright';
const browser = await chromium.launch();
for (const label of [['ponsel', 390], ['desktop', 1440]]) {
  const page = await browser.newPage({ viewport: { width: label[1], height: 844 } });
  await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `../docs/tangkapan/footer_${label[0]}_${label[1]}px.png`, fullPage: true });
  await page.close();
}
console.log('Selesai footer');
await browser.close();

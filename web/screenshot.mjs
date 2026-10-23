// Ambil tangkapan layar dasbor Upwind untuk peraga FR-W (mata: ponsel 390px, desktop 1440px).
// Pemakaian: node screenshot.mjs <skenario: normal|stale|night>
// Data pada ../DATA harus sudah diganti ke skenario itu sebelum memanggil.
import { chromium } from 'playwright';

const scenario = process.argv[2] || 'normal';
const outDir = '../docs/tangkapan/';
const url = 'http://localhost:3000/';

const browser = await chromium.launch();
for (const [label, width] of [['ponsel', 390], ['desktop', 1440]]) {
  const page = await browser.newPage({ viewport: { width, height: 844 } });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${outDir}dashboard_${scenario}_${label}_${width}px.png`, fullPage: true });

  // Halaman Tentang (klik tombol bila ada)
  const btn = page.locator('button', { hasText: /tentang/i }).first();
  if (await btn.count().catch(() => 0)) {
    await btn.click();
    await page.waitForTimeout(600);
    await page.screenshot({ path: `${outDir}tentang_${scenario}_${label}_${width}px.png`, fullPage: true });
    await page.keyboard.press('Escape');
    if (scenario === 'normal' && label === 'ponsel') {} // modal punya tombol tutup
    await page.waitForTimeout(300);
  }
  await page.close();
}
console.log(`Selesai: ${scenario}`);
await browser.close();

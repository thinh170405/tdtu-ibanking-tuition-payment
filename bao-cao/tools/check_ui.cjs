const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' });
  for (const width of [1440, 390]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
    await page.goto('http://localhost:5173/');
    await page.getByRole('button', { name: 'Đăng nhập' }).click();
    await page.getByText('Số dư khả dụng').waitFor();
    await page.getByPlaceholder('Nhập 8 chữ số').fill('52600005');
    await page.locator('.tuition').waitFor();
    await page.screenshot({ path: path.join(__dirname, `../tmp/ui-${width}.png`), fullPage: true });
    console.log(`ui-${width}: rendered`);
    await page.close();
  }
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });

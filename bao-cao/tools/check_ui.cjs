const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' });
  for (const width of [1440, 390]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
    await page.goto('http://localhost:5173/');
    await page.getByRole('button', { name: 'Đăng nhập' }).click();
    await page.getByText('Số dư khả dụng').waitFor();
    await page.waitForFunction(() => document.querySelector('.dashboard-intro h1')?.textContent?.includes('Nguyễn Văn An'));
    await page.screenshot({ path: path.join(__dirname, `../tmp/dashboard-${width}.png`), fullPage: true });
    await page.getByRole('button', { name: /Đến trang thanh toán/ }).click();
    if (!page.url().endsWith('/tuition-payment')) throw new Error('Payment route was not opened');
    await page.getByPlaceholder('Nhập 8 chữ số').fill('52600005');
    await page.locator('.tuition').waitFor();
    await page.screenshot({ path: path.join(__dirname, `../tmp/ui-${width}.png`), fullPage: true });
    await page.reload();
    await page.getByPlaceholder('Nhập 8 chữ số').waitFor();
    await page.getByRole('button', { name: 'Tổng quan' }).click();
    if (!page.url().endsWith('/')) throw new Error('Dashboard route was not opened');
    console.log(`ui-${width}: rendered`);
    await page.close();
  }
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });

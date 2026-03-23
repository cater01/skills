#!/usr/bin/env node
/** Render poster PNG from payload.json + HTML template using Puppeteer.

Usage:
  node scripts/render_poster.js --payload payload.json --template templates/poster.html --out poster.png

Notes:
- Requires Node.js and puppeteer.
- If puppeteer is missing, install in the skill folder:
    npm init -y
    npm i puppeteer
*/

const fs = require('fs');
const path = require('path');

function arg(name, defVal = null) {
  const idx = process.argv.indexOf(name);
  if (idx === -1) return defVal;
  return process.argv[idx + 1];
}

async function main() {
  const payloadPath = arg('--payload');
  const templatePath = arg('--template');
  const outPath = arg('--out');

  if (!payloadPath || !templatePath || !outPath) {
    console.error('Missing args. Need --payload --template --out');
    process.exit(2);
  }

  let puppeteer;
  try {
    puppeteer = require('puppeteer');
  } catch (e) {
    console.error('puppeteer not installed. Run: npm i puppeteer');
    process.exit(3);
  }

  const payload = JSON.parse(fs.readFileSync(payloadPath, 'utf8'));
  const html = fs.readFileSync(templatePath, 'utf8');

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  // Force viewport to template size
  await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 2 });

  await page.setContent(html, { waitUntil: 'networkidle0' });
  await page.evaluate((p) => { window.__PAYLOAD__ = p; }, payload);

  // Re-run inline script by reloading with payload present
  await page.evaluate(() => {
    // Trigger a soft refresh of DOM bindings by dispatching a custom event
    window.dispatchEvent(new Event('payload-ready'));
  });

  // Some templates render immediately; give a short tick
  await page.waitForTimeout(200);

  // Screenshot the root container for exact crop
  const root = await page.$('#root');
  if (!root) {
    console.error('Template missing #root element');
    process.exit(4);
  }
  await root.screenshot({ path: outPath });

  await browser.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

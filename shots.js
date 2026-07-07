// Screenshot Website pages at desktop + mobile -> build/
const path = require('path');
const fs = require('fs');
const puppeteer = require(path.resolve(__dirname, '../Platform/node_modules/puppeteer-core'));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PAGES = [['home', 'index.html'], ['news', 'news.html'], ['blog', 'blog.html'],
  ['privacy', 'privacy-policy.html'], ['terms', 'terms-of-service.html'],
  ...['what-my-policy-survey-says-about-ontario-right-now',
      'alto-should-be-just-the-beginning-of-ontarios-high-speed-rail-network',
      'an-ontario-budget-for-decline-war-in-iran',
      'a-billion-here-a-billion-there',
      'poorer-than-alabama----what-the-gdp-per-capita-debate-is-really-about',
      'hamilton-speech-university-funding-changes-and-other-thoughts',
      'liberal-leadership-timelines-are-out']
    .map((s, i) => [`post${i + 1}-${s.slice(0, 24)}`, `blog/${s}.html`])];
const VIEWS = [['desktop', 1440, 900], ['mobile', 390, 844]];

(async () => {
  fs.mkdirSync(path.resolve(__dirname, 'build'), { recursive: true });
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new',
    args: ['--no-sandbox', '--allow-file-access-from-files', '--font-render-hinting=none'] });
  const page = await browser.newPage();
  for (const [vname, w, h] of VIEWS) {
    await page.setViewport({ width: w, height: h, deviceScaleFactor: 1 });
    for (const [name, file] of PAGES) {
      await page.goto('file://' + path.resolve(__dirname, file), { waitUntil: 'networkidle0' });
      await page.evaluate(async () => {
        await new Promise(res => {
          let y = 0;
          const step = () => {
            y += 800; window.scrollTo(0, y);
            if (y < document.body.scrollHeight) setTimeout(step, 60);
            else { window.scrollTo(0, 0); setTimeout(res, 250); }
          };
          step();
        });
      });
      await page.screenshot({ path: path.resolve(__dirname, `build/${name}-${vname}.png`), fullPage: true });
    }
  }
  console.log('done');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });

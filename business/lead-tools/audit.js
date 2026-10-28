// Проверка сайтов: node audit.js sites.json audit.json
const { chromium, devices } = require('playwright');
const fs = require('fs');
const [, , inFile, outFile] = process.argv;
const sites = JSON.parse(fs.readFileSync(inFile, 'utf8'));
const out = fs.existsSync(outFile) ? JSON.parse(fs.readFileSync(outFile, 'utf8')) : {};

const BUILDERS = [
  ['Tilda', /tildacdn|tilda\.ws|t-records/i], ['Wix', /wixstatic|wix\.com|_wixCIDX/i], ['Taplink', /taplink/i],
  ['uCoz', /ucoz|narod\.ru|usite/i], ['WordPress', /wp-content|wp-includes/i], ['Nethouse', /nethouse/i],
  ['Flexbe', /flexbe/i], ['LPmotor', /lpmotor/i], ['Mobirise', /mobirise/i], ['Craftum', /craftum/i],
  ['Битрикс', /bitrix/i], ['Joomla', /joomla/i], ['Яндекс Бизнес', /business\.site|ya\.cc|yandex\.ru\/sprav/i],
  ['Google Sites', /sites\.google/i], ['Setka/Сайт за 5 минут', /a5\.ru|ukit|umi\.ru/i],
];
const TEMPLATE = /(Страница барбершопа или парикмахерской|lorem ipsum|ваш заголовок|заголовок блока|название компании|ваша компания|example\.com|Здесь будет|текст для примера|Добавьте описание)/i;
const PARKED = /(Доменное имя[^\n]{0,60}прода[её]тся|SigmaParking|припаркован|Domain has been assigned|домен продаётся|домен продается|this domain is for sale|domain is parked|сайт заблокирован|срок регистрации домена истек|account suspended|сайт временно недоступен|website is under construction|сайт в разработке)/i;

async function auditOne(browser, url) {
  const res = { url, ok: false };
  const ctx = await browser.newContext({ ...devices['iPhone 13'], ignoreHTTPSErrors: false });
  const page = await ctx.newPage();
  let bytes = 0, requests = 0, failed = 0;
  const consoleErrors = [];
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Network.enable');
  cdp.on('Network.loadingFinished', (e) => { bytes += e.encodedDataLength || 0; requests += 1; });
  page.on('requestfailed', () => { failed += 1; });
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text().slice(0, 120)); });
  const t0 = Date.now();
  try {
    const target = url.replace(/^http:\/\//i, 'https://');
    res.tried = target;
    const resp = await page.goto(target, { waitUntil: 'load', timeout: 45000 });
    res.loadMs = Date.now() - t0;
    res.status = resp ? resp.status() : 0;
    res.finalUrl = page.url();
    await page.waitForTimeout(1500);
    let info;
    try { info = await page.evaluate(() => {
      const html = document.documentElement.outerHTML;
      const text = document.body ? document.body.innerText : '';
      const vp = document.querySelector('meta[name="viewport"]');
      const years = (text.match(/(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–—]\s*)?(\d{4})/gi) || [])
        .map((s) => Number((s.match(/(\d{4})(?!.*\d{4})/) || [])[1])).filter(Boolean);
      const imgs = [...document.images];
      const bigImgs = imgs.filter((i) => i.naturalWidth > 2500).length;
      return {
        title: document.title.slice(0, 120),
        viewport: vp ? vp.content : '',
        overflow: document.documentElement.scrollWidth - window.innerWidth,
        textLen: text.length,
        tel: !!document.querySelector('a[href^="tel:"]'),
        booking: /(yclients|dikidi|n\d+\.yclients|w\d+\.yclients|sonline|arnica|easyweek|bookon|zapis)/i.test(html),
        form: !!document.querySelector('form'),
        years, bigImgs, imgCount: imgs.length,
        emails: [...new Set((html.match(/[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[a-z]{2,}/gi) || []))]
          .filter((e) => !/\.(png|jpe?g|gif|svg|webp)$/i.test(e) && !/(sentry|wixpress|example|domain\.|tildacdn|yandex\.ru\/|@2x|@3x)/i.test(e)).slice(0, 5),
        smallText: (() => { const ps = [...document.querySelectorAll('p, li, a, span')].slice(0, 200); const small = ps.filter((e) => e.innerText && e.innerText.trim().length > 20 && parseFloat(getComputedStyle(e).fontSize) < 12).length; return small; })(),
        html: html.slice(0, 400000),
        text: text.slice(0, 20000),
      };
    }); } catch (e) {
      const h = await page.content();
      const t = h.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<[^>]+>/g, ' ');
      info = { title: '', viewport: (h.match(/name=["']viewport["'][^>]*content=["']([^"']+)/i) || [, ''])[1], overflow: 0, textLen: t.trim().length,
        tel: /href=["']tel:/i.test(h), booking: /(yclients|dikidi|sonline|easyweek)/i.test(h), form: /<form/i.test(h), years: [], bigImgs: 0, imgCount: 0,
        emails: [...new Set(h.match(/[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[a-z]{2,}/gi) || [])].filter((e) => !/\.(png|jpe?g|svg|webp)$/i.test(e)).slice(0, 5), smallText: 0, html: h.slice(0, 400000), text: t.slice(0, 20000) };
    }
    res.title = info.title; res.viewport = info.viewport; res.overflow = info.overflow; res.textLen = info.textLen;
    res.tel = info.tel; res.booking = info.booking; res.form = info.form; res.years = info.years; res.bigImgs = info.bigImgs;
    res.imgCount = info.imgCount; res.emails = info.emails; res.smallText = info.smallText;
    res.builder = (BUILDERS.find(([, re]) => re.test(info.html + ' ' + res.finalUrl)) || [''])[0];
    res.template = (info.text.match(TEMPLATE) || [''])[0];
    res.parked = (info.text.match(PARKED) || [''])[0];
    res.bytes = bytes; res.requests = requests; res.failed = failed; res.consoleErrors = consoleErrors.length;
    res.https = res.finalUrl.startsWith('https://');
    res.ok = true;
    const shot = 'shots/' + new URL(res.finalUrl).hostname.replace(/[^\w.-]/g, '_') + '.jpg';
    await page.screenshot({ path: shot, type: 'jpeg', quality: 55 });
    res.shot = shot;
  } catch (e) {
    res.error = String(e.message || e).split('\n')[0].slice(0, 160);
    res.loadMs = Date.now() - t0;
  }
  await ctx.close();
  return res;
}

(async () => {
  fs.mkdirSync('shots', { recursive: true });
  const browser = await chromium.launch();
  const todo = sites.filter((u) => !out[u]);
  let i = 0;
  async function worker() {
    while (i < todo.length) {
      const u = todo[i++];
      out[u] = await auditOne(browser, u);
      if (Object.keys(out).length % 10 === 0) { fs.writeFileSync(outFile, JSON.stringify(out)); console.log(Object.keys(out).length, '/', sites.length); }
    }
  }
  await Promise.all([worker(), worker(), worker(), worker()]);
  fs.writeFileSync(outFile, JSON.stringify(out, null, 1));
  await browser.close();
  console.log('done', Object.keys(out).length);
})();

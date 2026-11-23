// Verify account routing and preview isolation without loading GoatCounter.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../js/analytics.js'), 'utf8');

// Deployments may serve the source tree directly. Every script linked as a
// classic script must parse in that mode, not just after Webpack bundles it.
for (const directory of ['js', 'dist/js']) {
  for (const file of ['app.js', 'analytics.js']) {
    const target = path.join(__dirname, '..', directory, file);
    assert.doesNotThrow(() => new vm.Script(fs.readFileSync(target, 'utf8'), { filename: target }));
  }
}

function preview(url, canonical, flagged = false) {
  const scripts = [];
  const window = { location: new URL(url), __WEDDINGS_PREVIEW__: flagged };
  const document = {
    querySelector: () => canonical ? { href: canonical } : null,
    createElement: () => ({ dataset: {} }),
    head: { append: script => scripts.push(script) },
  };
  const context = vm.createContext({ window, document, URL });
  vm.runInContext(source, context);
  return { window, scripts, context };
}

for (const url of [
  'http://localhost:8081/fi/', 'http://127.0.0.1:8011/fi/',
  'http://[::1]:8011/fi/', 'http://192.168.1.2/fi/',
  'https://preview.netlify.app/fi/',
]) {
  const result = preview(url, 'https://sondermomentsphotography.com/fi/');
  assert.equal(result.scripts.length, 0, `Tracking must remain off on ${url}`);
  assert.equal(result.window.goatcounter, undefined);
}
assert.equal(preview('https://sondermomentsphotography.com/fi/', null, true).scripts.length, 0);

for (const host of ['sondermomentsphotography.com', 'www.sondermomentsphotography.com']) {
  const result = preview(`https://${host}/fi/index.html?email=test@example.test#contact`,
    'https://sondermomentsphotography.com/fi/');
  assert.equal(result.scripts.length, 1);
  assert.equal(result.scripts[0].dataset.goatcounter, 'https://sondermoments.goatcounter.com/count');
  assert.equal(result.scripts[0].src, 'https://gc.zgo.at/count.js');
  assert.equal(result.scripts[0].async, true);
  assert.equal(result.window.goatcounter.path(), 'sondermomentsphotography.com/fi/');
  vm.runInContext(source, result.context);
  assert.equal(result.scripts.length, 1, 'Load the tracker only once');
}
assert.equal(preview('https://sondermomentsphotography.com/en/?private=test#contact').window.goatcounter.path(),
  'sondermomentsphotography.com/en/');
console.log('PASS: GoatCounter account, hostname-prefixed canonical paths, query exclusion and preview isolation; no live analytics sent.');

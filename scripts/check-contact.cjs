// Run the entire unbundled app as a classic script. EmailJS is a local mock:
// these checks must never submit a real inquiry or generate live analytics.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../js/app.js'), 'utf8');

async function check(hostname, reject = false) {
  let handler;
  const sent = [];
  let resets = 0;
  const button = { disabled: false };
  const status = {
    textContent: '',
    replaceChildren(...nodes) { this.textContent = nodes.join(''); },
    append(node) { this.textContent += node.textContent; },
  };
  const values = { name: 'Test sender', email: 'test@example.test', phone: '',
    date: '', location: '', service: 'photography', message: 'Mock only' };
  const form = {
    addEventListener: (event, fn) => { if (event === 'submit') handler = fn; },
    querySelector: selector => selector === '#service'
      ? { selectedOptions: [{ textContent: 'Valokuvaus' }] } : button,
    reset: () => { resets += 1; },
  };
  const document = {
    documentElement: { lang: 'fi' }, body: { dataset: { page: 'films' } },
    querySelectorAll: () => [],
    querySelector: selector => ({ '#contactForm': form, '#form-status': status }[selector] || null),
    addEventListener() {}, createTextNode: text => text, createElement: () => ({}),
  };
  const window = {
    location: { hostname }, matchMedia: () => ({ addEventListener() {} }),
    emailjs: { send: async (service, template, data) => {
      sent.push({ service, template, data });
      if (reject) throw new Error('Mock failure');
    } },
  };
  vm.runInNewContext(source, {
    window, document,
    FormData: class { constructor() { return new Map(Object.entries(values)); } },
  });
  assert.equal(typeof handler, 'function', 'The full classic app must register the form handler');
  let prevented = false;
  await handler({ preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  if (hostname === 'localhost') {
    assert.equal(sent.length, 0);
    assert.match(status.textContent, /ei lähetetty/);
  } else {
    assert.equal(sent.length, 1);
    assert.equal(sent[0].service, 'service_spddklr');
    assert.equal(sent[0].template, 'template_4cj282g');
    for (const key of ['name', 'email', 'phone', 'date', 'location', 'service']) {
      assert.equal(sent[0].data[key], values[key]);
    }
    assert.match(sent[0].data.message, /Mock only/);
    assert.equal(resets, reject ? 0 : 1);
    assert.match(status.textContent, reject ? /Lähetys ei onnistunut/ : /vastaanotti/);
    assert.equal(button.disabled, false);
  }
}
(async () => {
  await check('localhost');
  await check('sondermomentsphotography.com');
  await check('sondermomentsphotography.com', true);
  console.log('PASS: Full unbundled app registers the contact handler; mock success/failure and local-send protection verified.');
})().catch(error => { console.error(error); process.exitCode = 1; });

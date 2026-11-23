/* Shared Sonder Moments account, with distinct Weddings page paths. */
(() => {
  const productionHosts = ['sondermomentsphotography.com', 'www.sondermomentsphotography.com'];
  if (!productionHosts.includes(window.location.hostname) || window.__WEDDINGS_PREVIEW__ || window.goatcounter) return;

  // Canonical paths combine legacy URLs, exclude queries/fragments, and avoid
  // merging /en/ and other common paths with the other Sonder Moments sites.
  const canonical = document.querySelector('link[rel="canonical"]');
  const page = new URL(canonical?.href || window.location.href);
  window.goatcounter = {
    path: () => `sondermomentsphotography.com${page.pathname}`,
  };
  const script = document.createElement('script');
  script.dataset.goatcounter = 'https://sondermoments.goatcounter.com/count';
  script.async = true;
  script.src = 'https://gc.zgo.at/count.js';
  document.head.append(script);
})();

/* Shared behavior; all page content is present in the generated HTML. */
const language = document.documentElement.lang;
const fi = language === 'fi';

// Open full, uncropped photographs on demand without loading a gallery library.
const photoLinks = Array.from(document.querySelectorAll('a[data-photo]'));
if (photoLinks.length) {
  const galleryLinks = photoLinks.filter(link => link.closest('.gallery-grid'));
  const photos = Array.from(new Map([...galleryLinks, ...photoLinks].map(link => [link.href, link])).values());
  const viewer = document.createElement('dialog');
  viewer.className = 'photo-viewer';
  viewer.setAttribute('aria-label', fi ? 'Kuvagalleria' : 'Photo gallery');
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'photo-close';
  close.textContent = '×';
  close.setAttribute('aria-label', fi ? 'Sulje kuva' : 'Close photo');
  const previous = document.createElement('button');
  previous.type = 'button';
  previous.className = 'photo-previous';
  previous.textContent = '←';
  previous.setAttribute('aria-label', fi ? 'Edellinen kuva' : 'Previous photo');
  const next = document.createElement('button');
  next.type = 'button';
  next.className = 'photo-next';
  next.textContent = '→';
  next.setAttribute('aria-label', fi ? 'Seuraava kuva' : 'Next photo');
  const figure = document.createElement('figure');
  const enlarged = document.createElement('img');
  enlarged.decoding = 'async';
  figure.append(enlarged);
  const caption = document.createElement('p');
  caption.className = 'photo-caption';
  caption.setAttribute('aria-live', 'polite');
  let current = 0;
  let opener;
  function showPhoto(index) {
    current = (index + photos.length) % photos.length;
    const link = photos[current];
    enlarged.src = link.href;
    enlarged.alt = link.querySelector('img').alt;
    caption.textContent = enlarged.alt;
  }
  photoLinks.forEach(link => link.addEventListener('click', event => {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    showPhoto(photos.findIndex(photo => photo.href === link.href));
    viewer.showModal();
    document.body.classList.add('photo-viewer-open');
    close.focus();
  }));
  close.addEventListener('click', () => viewer.close());
  previous.addEventListener('click', () => showPhoto(current - 1));
  next.addEventListener('click', () => showPhoto(current + 1));
  viewer.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      showPhoto(current + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  viewer.addEventListener('click', event => { if (event.target === viewer) viewer.close(); });
  viewer.addEventListener('close', () => {
    document.body.classList.remove('photo-viewer-open');
    enlarged.removeAttribute('src');
    opener?.focus({ preventScroll: true });
  });
  viewer.append(close, previous, next, figure, caption);
  document.body.append(viewer);
}

// This silent showreel has no audio track. Use controls without a volume button,
// retaining native controls as the no-JavaScript fallback.
const showreel = document.querySelector('#showreel');
if (showreel) {
  const player = showreel.parentElement;
  player.classList.add('showreel-player');
  const controls = document.createElement('div');
  controls.className = 'showreel-controls';
  const overlay = document.createElement('button');
  overlay.type = 'button';
  overlay.className = 'showreel-play-overlay';
  overlay.textContent = '▶';
  overlay.setAttribute('aria-label', fi ? 'Toista esittelyvideo' : 'Play intro video');
  const play = document.createElement('button');
  play.type = 'button';
  const seek = document.createElement('input');
  seek.type = 'range';
  seek.min = '0';
  seek.max = '100';
  seek.step = '0.1';
  seek.value = '0';
  seek.setAttribute('aria-label', fi ? 'Videon kohta' : 'Video position');
  const time = document.createElement('span');
  time.className = 'showreel-time';
  const fullscreen = document.createElement('button');
  fullscreen.type = 'button';
  fullscreen.textContent = '⛶';
  fullscreen.setAttribute('aria-label', fi ? 'Koko näyttö' : 'Full screen');
  fullscreen.hidden = !player.requestFullscreen;
  const touchScreen = window.matchMedia('(max-width: 600px), (hover: none), (pointer: coarse)');
  let touchControls = false;
  let hideControlsTimer;
  function hideControls() {
    clearTimeout(hideControlsTimer);
    player.classList.remove('is-controls-visible');
  }
  function revealControls() {
    clearTimeout(hideControlsTimer);
    player.classList.add('is-controls-visible');
    if (!showreel.paused) hideControlsTimer = setTimeout(hideControls, 3000);
  }
  showreel.addEventListener('click', event => {
    if (!touchScreen.matches && event.pointerType !== 'touch') return;
    touchControls = true;
    if (showreel.paused) {
      showreel.play().catch(syncShowreel);
      revealControls();
    } else if (player.classList.contains('is-controls-visible')) hideControls();
    else revealControls();
  });
  controls.addEventListener('pointerdown', () => clearTimeout(hideControlsTimer));
  controls.addEventListener('pointerup', () => { if (touchControls) revealControls(); });
  document.addEventListener('pointerdown', event => {
    if (!player.contains(event.target)) hideControls();
  });
  showreel.addEventListener('play', () => { if (touchControls) revealControls(); });
  showreel.addEventListener('pause', () => { if (touchControls) revealControls(); });
  showreel.addEventListener('ended', () => { if (touchControls) revealControls(); });
  const stamp = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
  function syncShowreel() {
    const duration = Number.isFinite(showreel.duration) ? showreel.duration : 0;
    play.textContent = showreel.paused ? '▶' : 'Ⅱ';
    overlay.hidden = !showreel.paused;
    play.setAttribute('aria-label', showreel.paused ? (fi ? 'Toista video' : 'Play video') : (fi ? 'Keskeytä video' : 'Pause video'));
    seek.disabled = !duration;
    seek.value = duration ? String(showreel.currentTime / duration * 100) : '0';
    seek.setAttribute('aria-valuetext', `${stamp(showreel.currentTime)} / ${stamp(duration)}`);
    time.textContent = `${stamp(showreel.currentTime)} / ${stamp(duration)}`;
  }
  play.addEventListener('click', () => {
    if (showreel.paused) showreel.play().catch(syncShowreel);
    else showreel.pause();
  });
  overlay.addEventListener('click', event => {
    touchControls = touchScreen.matches || event.pointerType === 'touch';
    if (overlay.matches(':focus-visible')) play.focus();
    showreel.play().catch(syncShowreel);
    if (touchControls) revealControls();
  });
  seek.addEventListener('input', () => {
    if (Number.isFinite(showreel.duration)) showreel.currentTime = Number(seek.value) / 100 * showreel.duration;
  });
  fullscreen.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement === player) await document.exitFullscreen();
      else await player.requestFullscreen();
    } catch { /* Keep playback available if fullscreen is unavailable. */ }
  });
  ['play', 'pause', 'ended', 'timeupdate', 'loadedmetadata', 'durationchange', 'emptied'].forEach(event => showreel.addEventListener(event, syncShowreel));
  controls.append(play, seek, time, fullscreen);
  player.append(overlay, controls);
  showreel.controls = false;
  showreel.muted = true;
  syncShowreel();
}

// Keep inline films as lightweight thumbnails until the visitor presses play.
// Autoplay permission makes that first click start the newly created player.
// Dedicated watch pages retain their eager iframe for video discoverability.
document.querySelectorAll('.inline-video-preview').forEach(preview => {
  preview.addEventListener('click', () => {
    const player = document.createElement('iframe');
    player.src = `${preview.dataset.videoSrc}&autoplay=1`;
    player.title = preview.dataset.videoTitle;
    player.width = '1280';
    player.height = '720';
    player.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    player.referrerPolicy = 'strict-origin-when-cross-origin';
    player.allowFullscreen = true;
    preview.replaceWith(player);
    player.focus();
  }, { once: true });
});

const menuButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
function closeMenu() {
  nav?.classList.remove('is-open');
  menuButton?.setAttribute('aria-expanded', 'false');
}
menuButton?.addEventListener('click', () => {
  const open = nav.classList.toggle('is-open');
  menuButton.setAttribute('aria-expanded', String(open));
});
nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuButton.focus();
  }
});
window.matchMedia('(min-width: 851px)').addEventListener('change', event => {
  if (event.matches) closeMenu();
});

// Earlier portfolio anchors continue to take visitors to their dedicated page.
if (document.body.dataset.page === 'home') {
  const destinations = fi
    ? { '#photos': '/fi/haavalokuvaus/', '#videography': '/fi/haavideot/', '#youtube-videos': '/fi/haavideot/#portfolio' }
    : { '#photos': '/en/wedding-photography/', '#videography': '/en/wedding-films/', '#youtube-videos': '/en/wedding-films/#portfolio' };
  const destination = destinations[window.location.hash];
  if (destination) window.location.replace(destination);
}

const form = document.querySelector('#contactForm');
form?.addEventListener('submit', async event => {
  event.preventDefault();
  const status = document.querySelector('#form-status');
  const submit = form.querySelector('button[type="submit"]');
  // Preview QA cannot send a real inquiry to the business.
  if (['localhost', '127.0.0.1', '::1', '[::1]'].includes(window.location.hostname) || window.__WEDDINGS_PREVIEW__) {
    status.textContent = fi ? 'Esikatselu: viestiä ei lähetetty.' : 'Preview: your message has not been sent.';
    return;
  }
  submit.disabled = true;
  status.textContent = fi ? 'Lähetetään…' : 'Sending…';
  try {
    if (!window.emailjs) {
      await new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js';
        script.onload = resolve;
        script.onerror = () => { script.remove(); reject(new Error('Email service unavailable')); };
        document.head.append(script);
      });
      window.emailjs.init({ publicKey: 'v8iVtYyC3WfmgXb_M' });
    }
    // Existing EmailJS template consumes message, so include the selected service there too.
    const data = Object.fromEntries(new FormData(form));
    const service = form.querySelector('#service').selectedOptions[0].textContent;
    data.message = `${fi ? 'Palvelu' : 'Service'}: ${service}\n\n${data.message}`;
    await window.emailjs.send('service_spddklr', 'template_4cj282g', data);
    status.textContent = fi ? 'Kiitos! Viestipalvelu vastaanotti viestisi.' : 'Thank you! The message service has accepted your inquiry.';
    form.reset();
  } catch {
    status.replaceChildren(document.createTextNode(fi ? 'Lähetys ei onnistunut. Lähetä viesti osoitteeseen ' : 'Your message could not be sent. Please email '));
    const email = document.createElement('a');
    email.href = 'mailto:info@sondermomentsphotography.com';
    email.textContent = 'info@sondermomentsphotography.com';
    status.append(email);
  } finally {
    submit.disabled = false;
  }
});

// Enhance the service field while retaining its native value and no-JS fallback.
document.querySelectorAll('.field select').forEach(select => {
  const field = select.closest('.field');
  const label = field.querySelector('label');
  const wrapper = document.createElement('div');
  wrapper.className = 'service-select';
  const trigger = document.createElement('button');
  trigger.type = 'button';
  trigger.id = `${select.id}-trigger`;
  trigger.className = 'service-select-trigger';
  trigger.setAttribute('role', 'combobox');
  trigger.setAttribute('aria-haspopup', 'listbox');
  trigger.setAttribute('aria-expanded', 'false');
  const menu = document.createElement('div');
  menu.id = `${select.id}-options`;
  menu.className = 'service-select-menu';
  menu.setAttribute('role', 'listbox');
  menu.hidden = true;
  trigger.setAttribute('aria-controls', menu.id);
  label.id = `${select.id}-label`;
  trigger.setAttribute('aria-labelledby', `${label.id} ${trigger.id}`);
  menu.setAttribute('aria-labelledby', label.id);
  const options = Array.from(select.options).map((option, index) => {
    const item = document.createElement('div');
    item.id = `${select.id}-option-${index}`;
    item.className = 'service-select-option';
    item.setAttribute('role', 'option');
    item.textContent = option.textContent;
    menu.append(item);
    return item;
  });
  let activeIndex = select.selectedIndex;
  let search = '';
  let lastKeyTime = 0;
  const isOpen = () => !menu.hidden;
  function highlight(index) {
    activeIndex = index;
    options.forEach((item, i) => item.classList.toggle('is-active', i === index));
    trigger.setAttribute('aria-activedescendant', options[index].id);
  }
  function sync() {
    trigger.textContent = select.selectedOptions[0].textContent;
    options.forEach((item, i) => item.setAttribute('aria-selected', String(i === select.selectedIndex)));
  }
  function close() {
    menu.hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
    trigger.removeAttribute('aria-activedescendant');
  }
  function open() {
    menu.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');
    highlight(select.selectedIndex);
  }
  function choose(index) {
    select.selectedIndex = index;
    select.dispatchEvent(new Event('change', { bubbles: true }));
    close();
    trigger.focus();
  }
  trigger.addEventListener('click', () => isOpen() ? close() : open());
  trigger.addEventListener('keydown', event => {
    if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      if (!isOpen()) { open(); return; }
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? options.length - 1 : (activeIndex + (event.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length;
      highlight(next);
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (isOpen()) choose(activeIndex); else open();
    } else if (event.key === 'Escape') {
      event.preventDefault();
      close();
    } else if (event.key === 'Tab') {
      close();
    } else if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
      event.preventDefault();
      search = Date.now() - lastKeyTime > 700 ? event.key : search + event.key;
      lastKeyTime = Date.now();
      if (!isOpen()) open();
      const match = options.findIndex(item => item.textContent.toLocaleLowerCase(language).startsWith(search.toLocaleLowerCase(language)));
      if (match >= 0) highlight(match);
    }
  });
  options.forEach((item, index) => {
    item.addEventListener('click', () => choose(index));
    item.addEventListener('pointermove', () => highlight(index));
  });
  document.addEventListener('click', event => { if (!wrapper.contains(event.target)) close(); });
  select.addEventListener('change', sync);
  select.form?.addEventListener('reset', () => queueMicrotask(() => { sync(); close(); }));
  wrapper.append(trigger, menu);
  select.after(wrapper);
  select.hidden = true;
  label.htmlFor = trigger.id;
  sync();
});

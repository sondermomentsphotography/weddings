# Weddings project context

Owner-confirmed requirements, 2026-11-05:

Current analytics implementation, 2026-11-23: GoatCounter pageviews added at the owner's request to the shared sondermoments.goatcounter.com account. Follows Sonder Moments Media's hostname-prefixed paths, using each Weddings page's canonical path (e.g. sondermomentsphotography.com/fi/haavideot/) so common paths do not merge with the other sites. js/analytics.js loads count.js asynchronously only on the production Weddings hosts; localhost, preview domains and __WEDDINGS_PREVIEW__ are excluded. Paths omit queries/fragments. No form contents or custom conversion events are sent. Mock tests verify routing, duplicate-load prevention and preview exclusions; no live analytics were generated. Build and tests pass. Deployment and actual account receipt remain unverified; older statements that no analytics are implemented are superseded by this local implementation.

Deployment compatibility correction, 2026-11-23: the owner reported the live page failing with “Cannot use import statement outside a module” at app.js:2. The analytics module import was valid in the Webpack build but broke directly served source HTML, preventing all app behavior including the EmailJS submit handler. Removed the import; all generated pages now load analytics.js and app.js as separate deferred classic scripts, and the build copies analytics.js explicitly. Added regression checks for source/build classic parsing and complete unbundled-app contact-handler registration, mock EmailJS success/failure, and localhost protection. Build and tests pass. Local fix requires redeployment; actual inbox delivery has not been verified and no real test email was sent.

- Business: Sonder Moments Weddings, Sirle; wedding photography and cinematic wedding films in Helsinki, across Finland and Europe. Existing contact: info@sondermomentsphotography.com / +358 40 485 9969. Existing copy says based in Kirkkonummi; no current physical studio address confirmed.
- Keep complete Finnish and English versions, with distinct photography and film pages on the same domain. Existing /en/ and /fi/ remain homepages. No second domain is requested.
- Match the local Tinderkuvaus and Boudoir Studio design family while keeping Weddings white. Use the original photographs, films and personal voice; preserve most original copy.
- Owner-approved starting prices: photography €895 (corrected by the owner on 2026-11-23) and full-day films €2,595, both including 25.5% VAT. Do not apply VAT a second time. Old downloadable PDFs still contain historical pricing and are excluded from current page links.
- Keep the three existing films: Tytherington, Upton Barn & Walled Garden, St Austell/Cornwall.
- Add upcoming longer films for Terwa, Fiskars, Suomenlinna, Hirvenhaara and Seurasaari. The latest clarification specifies these five alongside the existing three, superseding the initial estimate of six new films.
- Add upcoming 30–60 second reels for Terwa, Seurasaari and Fiskars. Repeat existing footage as labelled placeholders until actual assets arrive. Current placeholder showreel is not cropped or falsely described as the finished reel.
- Marketing skill source: all 27 standalone packages copied from ../boudoirstudio/.agents/skills, including the requested Corey Haines influencer-marketing skill. Each imported skill preserves its licence and UPSTREAM.md where provided. These adapted packages are pinned to upstream commit 88c79f6528a9347420e57ceb1fff9a60de651768 (reviewed in source project 2026-11-03). This is reuse of the source project's reviewed version, not an automatic update to upstream main.

## Current video update — 2026-11-22

The owner requested the channel's seven latest public uploads to replace all previous placeholder slots. The latest-first channel Videos list was checked in a browser. The actual selection supersedes the initial five-location plan: four longer films (Seurasaaren Juhlatalo, Valley Side Barn, The Terwa and Suomenlinna) and three short films (Terwa wedding party, bridal inspiration at Solo Sokos Hotel Pier 4 and Suomenlinna trailer). Keep the three original UK films as well. Fiskars and Hirvenhaara footage was not among these seven; do not label another film as either location.

All seven selected sources, titles, timestamps, runtimes and thumbnails were read from YouTube's public pages and DOM metadata. Records are in `youtube-video-sources.json`; `content/films.json` contains the bilingual website copy. YouTube's stated ISO runtimes are used rather than the player's rounded last-second display. Upload dates are publication dates, not wedding dates. The Pier 4 film is presented as bridal inspiration; do not imply it is a documented client wedding.

The implementation adds seven useful watch pages in each language, each centred on one eager-loading player without a click gate. Each has distinct titles and descriptions, self-canonicals, reciprocal hreflang, visible original publication date/runtime, a VideoObject with verified values, related films where appropriate, and an inquiry path. The main sitemap includes 14 matching video entries. Existing personal copy, prices, introductory loop and the original three films are retained. No placeholders remain in the current film collection.

These changes are local until deployed. No YouTube titles, descriptions or account settings were changed. No Search Console connection or indexing/ranking result is established. Public YouTube captions were not used to fabricate a transcript, wedding date, couple identity or venue details.

## Evidence and outstanding assets

No Search Console, keyword-volume, ranking or booking results were supplied. Separate service pages, canonicals, reciprocal hreflang, truthful schema and a sitemap improve discoverability; they do not establish ranking gains. Preserve publication consent for real client work.

For future videos, verify the actual video IDs, title/description, publication permission, upload dates and duration before adding watch pages or metadata. Do not create duplicate location pages purely to add keywords. Updated pricing brochures are a separate outstanding asset; do not present historical PDFs as current offers.

Official guidance consulted:
- https://developers.google.com/search/docs/appearance/video
- https://developers.google.com/search/docs/specialty/international/localized-versions

## Editing and preview

`content/copy.json` preserves the original long-form copy for careful reuse. `content/films.json` holds film slots, sources and placeholder flags. `content/pricing.json` holds confirmed totals. `scripts/build-pages.py` renders pages and sitemap; production Webpack copies pages, fonts, media and legacy downloads. `npm run build` then `npm test` checks the deployable artifact.

Run a local static preview from `dist` using `python3 -m http.server 8000 --bind 127.0.0.1 --directory dist`. The contact handler blocks real email transmission on localhost. The existing EmailJS public configuration is retained, and the selected service is included in the message. Live inbox delivery has not been tested.


### Validation on 2026-11-22

- `npm run build` and `npm test` passed for all 20 generated pages. Checks cover seven distinct new video IDs, original three films, single-video watch pages, verified metadata, reciprocal languages, links and all 14 video sitemap entries. Existing large media assets still produce Webpack size warnings.
- Local browser checks confirmed the Seurasaari embedded player, matching English/Finnish switching and responsive layout. Sampled the Finnish collection, Finnish Pier 4 page and English Terwa reel at 390 px with no horizontal overflow or completed-but-broken images.
- Google Rich Results Test code mode was run on the generated English Seurasaari watch page. It detected one valid VideoObject with the expected title, source player, thumbnail, timestamp and duration. Record: `video-validation-2026-11-22.json`. This is a representative code test, not a live URL/indexing test or validation of every page in Google. The overall tool also reported a separate non-critical local-business item warning; the video item itself had no reported issues.


### Landing-page design preferences

The owner requested a shorter hero heading without “Teidän ihmisenne” (and the matching English line), the longer Terwa film as the 02 / wedding-film feature, symmetrical service cards with shared alignment, and a modern service dropdown. The service cards now share grid rows and 16:9 media frames. The dropdown has a styled, keyboard-operable menu backed by the native form value and a no-JavaScript native-select fallback. These shared layout/form changes apply in both languages.


### Service-area wording

The owner prefers the wider Helsinki metropolitan service area in prominent service-area lines. Use “Helsinki ja pääkaupunkiseutu · Koko Suomi ja Eurooppa” on the Finnish homepage (Europe added at the owner’s request on 2026-11-23), with the English equivalent “Helsinki metropolitan area · All of Finland & Europe”. Shared contact sections also use the metropolitan service area. This describes where services are offered, not a studio address. Helsinki remains the concrete city in relevant service titles. No keyword-volume comparison or ranking improvement from this wording change has been established.


### Video interaction update

The video collection heading is now “Tunne kaikki uudelleen.” / “Feel it all again.” Inline films (the three original collection films and the homepage Terwa feature) render their YouTube iframes directly instead of using a click-to-load thumbnail button. This removes the extra loading click; lazy loading remains for offscreen players, and watch pages retain eager players. One-click playback was verified locally on the original Tytherington film.

All generated embeds share the same inline/caption settings. The site does not force captions on. YouTube's documented caption policy uses viewer preferences by default and only documents forcing captions on, so the website cannot guarantee subtitles will always be off. The browser test still showed a music caption with saved caption preferences. Do not report complete caption removal as verified. No caption tracks or settings on the YouTube account were changed. Reference: https://developers.google.com/youtube/player_parameters#cc_load_policy

### YouTube loading refinement — 2026-11-22

At the owner's request, homepage and collection embeds now defer their YouTube URL until an IntersectionObserver detects the player within 300 px of the viewport. This supersedes relying solely on native iframe lazy loading, which fetched the homepage player during the initial performance audit. The old site's click-to-create technique was inspected; the new version delays the same third-party player request without restoring an extra loading click. Dedicated watch pages retain their eager, discoverable iframe. No-JavaScript visitors receive native lazy-loading iframe fallbacks.

Local browser checks verified that the Finnish homepage and collection players initially have no src, that scrolling near them attaches the URL, and that one click starts Terwa playback (elapsed time advanced and the Pause control appeared). The English Terwa watch page retains its eager player. Production build and all 20-page checks pass. No new speed score or live deployment is claimed for this change.


### Portfolio priority

Finnish customers are the main audience. Put the longer Terwa film first as the large leading film, followed by Seurasaaren Juhlatalo and Suomenlinna. The short-film group also starts with Terwa. Keep UK weddings in the later England section and Valley Side Barn as the last film on the collection page. Venue navigation also puts Terwa first and Valley Side Barn last. Apply the same hierarchy in both languages; preserve all video watch URLs and metadata.


Portfolio placement clarification: Valley Side Barn belongs in the main four-film collection, after Terwa, Seurasaaren Juhlatalo and Suomenlinna. It retains its dedicated watch page. The original three films remain in the later section. This supersedes the earlier instruction to put Valley Side Barn at the very end of the page. The main collection uses a symmetrical two-by-two grid.


### Mobile intro sources restored — 2026-11-22

The owner pointed out the existing mobile intro files. The original homepage used wedding-reel-mobile-phone.webm for widths up to 420 px, wedding-reel-mobile.webm up to 600 px, and show-reel-mobile.mp4 as the mobile fallback. The redesign had omitted those WebM sources. Restored the original order in the shared generator for both homepages, preserving autoplay, muted looping and no controls. ffprobe confirms the phone WebM is 420×236 (3,965,252 bytes), the larger mobile WebM is 600×338 (6,529,868 bytes), and the MP4 fallback is 854×480 (6,194,445 bytes), all approximately 32.5 seconds. The phone file is smaller; the 600 px WebM is not smaller than the MP4. A new local Lighthouse run verified the phone WebM is selected and no YouTube request is made on initial homepage load.

Post-change local mobile Lighthouse samples (same Python localhost server and simulated mobile setup as the earlier audit): homepage performance 66, 82, 89, median 82; LCP 3.5, 4.1, 3.3 seconds; initial transfer approximately 3.3–3.8 MB. The first full-category run scored 100 accessibility, best practices and SEO. Film collection performance 86 (previous single run 88), LCP 2.9 seconds (previous 3.6), no initial YouTube requests. Scores vary materially between runs and are not production or real-user results. Build and all 20-page checks pass. Audit JSON evidence is in /private/tmp/weddings-after-home-{1,2,3}.json and /private/tmp/weddings-after-films.json.

### Equivalent old-page comparison — 2026-11-22

To investigate the owner's question about the old page's higher score, exported HEAD into an isolated /private/tmp/weddings-original-audit checkout and served it with the same Python local server type. One mobile Lighthouse run scored 99, LCP 1.6 s, TBT 40 ms, and 7,865 KiB transferred. Evidence: /private/tmp/weddings-old-local-1.json. This demonstrates the gap is not explained by different hosting alone. The old page's LCP candidate is the large p#main-text paragraph; the new page's candidate is video.intro-video. Both select wedding-reel-mobile-phone.webm. The redesign's LCP measures video/poster appearance rather than the old page's quickly rendered text. New-page processing delays also reduce the score; their exact cause is not yet established. Do not claim the older page is slower on the basis of total transferred bytes or dismiss the measured gap as hosting differences.

### Old-style inline YouTube loading restored — 2026-11-22

The owner clarified that the original page did not load YouTube player scripts/styles before a click. Replaced the interim viewport observer with thumbnail buttons on homepages and original collection films, matching the old technique. The click creates an iframe with autoplay=1 and explicit autoplay permission, so it starts playback without a second click. Dedicated watch pages retain their eager iframe and no-JavaScript inline fallbacks remain available. Thumbnail images can load before interaction; the YouTube player cannot.

Browser verification: scrolling to the Finnish homepage Terwa thumbnail leaves zero iframes; one click creates the player and shows Pause (playing). English collection initially has three thumbnails and zero iframes. Build and all 20-page checks pass. Screenshot: /private/tmp/weddings-click-to-play.png. This supersedes the 300 px observer behavior above. Request-log comparison found 9 YouTube requests (~1,043,934 bytes) in the original 58-point audit and zero in all three later 66/82/89-point homepage audits. Therefore the remaining initial score gap cannot be attributed to YouTube requests in those later runs. No new performance score is claimed for this click-only refinement.

### Intro poster bottleneck fixed — 2026-11-22

Controlled tests on temporary copies isolated the remaining score gap: old homepage 98 / LCP 1.6 s; current homepage 86 / 4.1 s; removing JavaScript 88 / 3.9 s; disabling autoplay 87 / 4.1 s; replacing video with the same large poster as an image 87 / 4.0 s; removing heading balancing 87 / 4.1 s. Removing the poster produced 100 twice but changed the LCP candidate to the heading. Keeping video and autoplay with a 420×236 compressed poster produced 99 / 2.0 s, both with and without explicit preload. The large poster, rather than content volume or current YouTube requests, explained most of this controlled score gap. Evidence: /private/tmp/weddings-speed-isolation/results/summary.json.

Owner authorised the fix. Added img/wedding-intro-poster.webp (14,794 bytes, down from 257,832) and changed the shared homepage and film-service templates to use it in both languages. Original image retained for existing URLs. Playback, mobile video sources, no-control autoplay loop and one-click YouTube behavior are preserved. No design/layout or content changes.

Build and all 20-page production checks pass. Browser confirmed the new poster URL and active muted, looping autoplay without controls; screenshot /private/tmp/weddings-poster-fixed.png. Fresh local simulated mobile Lighthouse homepage scores: 93, 99, 99 (median 99), LCP 1.96, 1.89, 1.45 s. Film collection: 98, LCP 1.82 s. Audit files: /private/tmp/weddings-poster-fixed/results/. These are local lab results, not deployed or real-user measurements.

### Watch-page stories removed — 2026-11-23

The owner requested removal of the written story section on all 14 wedding-video watch pages, pending their own copy. The shared watch template no longer renders the description/story block or its heading. Videos, titles, publication metadata, related-film links, service navigation and contact sections remain. Existing story drafts remain in content/films.json for reference only; do not restore them without the owner's request. Page and video descriptions remain in search/social metadata.

### Silent intro controls — 2026-11-23

The owner requested removal of the sound button from the 32-second intro. ffprobe confirms show-reel-small.mp4 has no audio stream. The film collection's #showreel now uses lightweight, bilingual play/pause, seek/time and fullscreen controls without volume controls; native controls remain the no-JavaScript fallback. The homepage's autoplaying, muted loop remains control-free. Local browser checks verified playback, seeking to the end and back, pause and fullscreen entry/exit. Screenshot: /private/tmp/weddings-silent-controls.png. Build and all 20-page checks pass. No new speed measurement is claimed for this controls change.

The owner subsequently requested hover-only controls for the silent intro. On hover-capable fine-pointer devices they now fade in on player hover or keyboard focus within it, and are hidden otherwise. The owner subsequently requested hidden mobile controls too; see the mobile overlay behavior below. Local browser verified hidden opacity 0, hover opacity 1, and keyboard focus revealing the controls. Build and all checks pass. Screenshot: /private/tmp/weddings-controls-hidden.png.

### Mobile intro play overlay — 2026-11-23

The owner requested hidden controls on mobile and a clear play overlay. The silent showreel now shows a central play button while paused on all devices. At mobile widths (up to 600 px) or on coarse/no-hover input, the control bar is hidden initially. Tapping the overlay starts playback in one gesture and reveals controls; controls auto-hide after three seconds of playback. Tapping the playing video toggles the controls; tapping outside hides them. Desktop hover and keyboard focus still reveal controls. No sound button or gray letterboxing is added. Local browser testing at 390 px verified initial hidden controls and visible overlay, one-tap playback with overlay hidden, timed hiding, tap-to-reveal, and paused overlay. Temporary viewport override was reset. Build and all 20-page checks pass. Screenshot: /private/tmp/weddings-mobile-play-overlay.png.

### Enlarged wedding photographs — 2026-11-23

Photography gallery images and the photography hero image now open a native dialog viewer in both languages. It shows the full uncropped WebP, with previous/next buttons, arrow-key navigation, Escape/close and focus returned to the clicked photograph. Duplicate hero/gallery sources share one gallery entry. White background and square controls match Weddings. Image links remain usable without JavaScript; enlarged photos load only when selected. Browser checks verified opening, next/previous, Escape and focus/scroll restoration, mobile portrait sizing at 390 px, and English hero opening. Build and all 20-page checks pass. Screenshot: /private/tmp/weddings-photo-viewer.png.

### Structured service areas — 2026-11-23

Owner requested alignment of areaServed with actual coverage. content/service-areas.json now supplies the same five areas to Organization on all 20 pages and Service on the four photography/film pages: Helsinki (City), Helsinki metropolitan area / Pääkaupunkiseutu (Place), Southern Finland / Etelä-Suomi (Place), Finland / Suomi (Country), Europe / Eurooppa (Continent). Southern Finland is a geographical Place, not a current administrative province. This describes travel coverage, not branches or studio addresses. Generated JSON verification confirmed consistency across all 24 business/service records; build and all 20-page checks pass. No live deployment, indexing change or ranking result claimed.

### Video-first homepage positioning — 2026-11-25

Owner authorised putting wedding films before photography in homepage positioning. Shared header navigation now lists films before photography on all pages; both homepages lead with films in titles, search/social descriptions, the hero service line and introductory wording. Homepage service cards are reordered in the generated HTML, with Terwa films before photography on desktop and mobile. Photography-page titles/copy retain their own service focus. The first film CTA was already primary and remains so. Local browser verified equal media and heading alignment after the card swap; build and all checks pass, including classic-script and mock contact/analytics checks. No ranking improvement claimed. Screenshot: /private/tmp/weddings-video-first.png.

### Preferred homepage search image — 2026-11-25

Owner reported Google showing a Terwa party thumbnail for the homepage and requested the homepage wedding photograph instead. Both homepages now identify img/wedding-couple-kissing.webp (1000×667, couple under the veil) through WebPage.primaryImageOfPage as an ImageObject and matching og:image/Twitter image metadata, with dimensions and localized descriptions. The visible homepage and film thumbnails are unchanged; watch pages retain their actual film-specific thumbnails. Build and checks pass; generated-image metadata checked in both languages. This supplies a preference, not control over Google’s automated selection. Requires deployment and recrawling; no live search-result change is verified.

# Sonder Moments Weddings

White, bilingual wedding photography and film site in the Sonder Moments design family.

```sh
npm run build
npm test
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open http://localhost:8000/en/ or http://localhost:8000/fi/.

Edit `scripts/build-pages.py` for shared markup and `css/weddings.css` for styling. Pages in `en/` and `fi/` and `sitemap.xml` are generated. Edit the original copy in `content/copy.json`, films in `content/films.json`, and VAT-inclusive starting prices in `content/pricing.json`, then rebuild. The existing PDF brochures are archived assets with old prices and are not advertised on the updated site.

The film collection now retains the three original films and features the seven latest channel uploads observed on 2026-11-22: four longer films and three short films. Each has an English and Finnish watch page, generated from `content/films.json`, with a prominent embedded player, verified VideoObject metadata, reciprocal language links and a video sitemap entry.

To add a published film, supply its YouTube `source` ID, bilingual `slug`, `title`, `description` and `story`, plus a verified `uploadDate`, ISO `duration` and stable `thumbnailUrl`. Add longer films to `featured`, short films to `reels`, and optional related-video IDs to `related`. Keep evidence in `marketing-context/youtube-video-sources.json`. Page descriptions and metadata must describe the actual footage; publication dates are not wedding dates. Rebuild and run the production checks after editing.

The landing intro stays muted, autoplaying and looping without hover controls. New watch pages use ordinary playback controls and do not autoplay. Search visibility requires deployment and indexing; local validation does not establish rankings or rich-result eligibility.

See `marketing-context/project.md` for owner decisions and `.agents/skills/` for the 27 reusable marketing packages copied from Boudoir Studio. Those skills retain their source records and licences and are discoverable on the next turn. They do not connect third-party services.

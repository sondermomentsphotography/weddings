#!/usr/bin/env python3
"""Check the actual production artifact, including links, language pairs and pricing."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
from datetime import datetime
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
BASE = 'https://sondermomentsphotography.com'

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.tags=[]; self.scripts=[]; self.script=None; self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs); self.tags.append((tag,attrs))
        if tag=='script' and attrs.get('type')=='application/ld+json': self.script=''
    def handle_data(self, data):
        if self.script is not None: self.script+=data
    def handle_endtag(self, tag):
        if tag=='script' and self.script is not None: self.scripts.append(json.loads(self.script)); self.script=None
    def find(self, tag, **attrs):
        return [a for t,a in self.tags if t==tag and all(a.get(k)==v for k,v in attrs.items())]

assert DIST.exists(), 'Run npm run build first'
files=[p for lang in ['en','fi'] for p in (DIST/lang).rglob('index.html')]
assert len(files)==20, f'Expected 6 service pages + 14 video watch pages, got {len(files)}'
media=json.loads((ROOT/'content/films.json').read_text())
films=media['featured']+media['reels']
assert len(films)==7 and len({f['source'] for f in films})==7
assert set(media['selection']['latestUploadIds'])=={f['source'] for f in films}
assert {f['source'] for f in media['existing']}=={'tAc2xctW__k','4GEdmqcDUhM','wIo0nIzf4nw'}
watch_paths={'/'+lang+'/'+('wedding-films' if lang=='en' else 'haavideot')+'/'+f['slug'][lang]+'/': (lang,f) for lang in ['en','fi'] for f in films}
seen_titles=set()
pages={}
for path in files:
    source=path.read_text(); page=Page(source); pages[path]=page
    relative='/' + str(path.relative_to(DIST).parent) + '/'
    title=re.search(r'<title>(.*?)</title>',source,re.S).group(1)
    assert title not in seen_titles, f'{relative}: duplicate page title'
    seen_titles.add(title)
    assert len(page.find('h1'))==1, f'{relative}: expected one h1'
    assert page.find('link',rel='canonical',href=BASE+relative), f'{relative}: wrong canonical'
    assert page.find('meta',name='description'), f'{relative}: no description'
    assert page.find('meta',name='robots',content='index,follow')
    assert page.scripts and page.scripts[0]['@graph'], f'{relative}: invalid schema'
    for script in ['app.js', 'analytics.js']:
        assert page.find('script',src='/js/'+script), f'{relative}: missing {script}'
    assert len(page.find('link',rel='alternate'))==3
    ids=[a['id'] for _,a in page.tags if 'id' in a]
    assert len(ids)==len(set(ids)), f'{relative}: duplicate IDs'
    for tag,attrs in page.tags:
        for key in ['href','src','poster']:
            value=attrs.get(key,'')
            if not value or value.startswith(('mailto:','tel:','https://')): continue
            parsed=urlsplit(value)
            target=DIST / unquote(parsed.path).lstrip('/') if parsed.path else path
            if target.is_dir(): target=target/'index.html'
            assert target.exists(), f'{relative}: missing {value}'
            if parsed.fragment and target.suffix=='.html':
                assert parsed.fragment in [a.get('id') for _,a in Page(target.read_text()).tags], f'{relative}: missing anchor {value}'
        if tag=='img': assert 'alt' in attrs and attrs.get('loading'), f'{relative}: image accessibility/loading'
    fields=[a for tag,a in page.tags if tag in ['input','select','textarea']]
    for field in fields: assert page.find('label',**{'for':field['id']}), f'{relative}: unlabeled form field'
    assert not page.find('input',name='date',value='2027-01-01'), 'Fabricated wedding date'
    assert not re.search(r'€\s*(?:1450|2000)|(?:1450|2000)\s*euro',source), 'Old price in active page'
    assert 'AggregateRating' not in source, 'Unverified aggregate rating'
    assert '/download/' not in source, 'Outdated brochure pricing linked'
    for alternate in page.find('link',rel='alternate'):
        if alternate['hreflang']=='x-default':continue
        other=DIST/alternate['href'].removeprefix(BASE).lstrip('/')/'index.html'
        assert Page(other.read_text()).find('link',rel='alternate',href=BASE+relative), 'Language pair is not reciprocal'
    if relative in ['/en/wedding-films/', '/fi/haavideot/']:
        assert len(page.find('iframe'))==3, 'Keep no-JavaScript fallbacks for the 3 original films'
        assert len(page.find('a',**{'class':'film-player film-watch-link'}))==7, 'Link all 7 new uploads'
        assert len(page.find('video'))==1, 'Only the existing showreel is a local video'
        assert 'VideoObject' not in source, 'Video markup belongs on the individual watch pages'
        assert 'placeholder' not in source.lower() and 'Tulossa' not in source, 'Remove placeholder messaging'
        assert 'Fiskars' not in source and 'Hirvenhaara' not in source, 'Do not retain mismatched venue labels'
    if relative in watch_paths:
        lang,film=watch_paths[relative]
        videos=[item for item in page.scripts[0]['@graph'] if item['@type']=='VideoObject']
        assert len(videos)==1, 'One primary video per watch page'
        video=videos[0]
        assert video['name']==film['title'][lang] and video['description']==film['description'][lang]
        assert video['uploadDate']==film['uploadDate'] and video['duration']==film['duration']
        datetime.fromisoformat(video['uploadDate'])
        assert re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',video['duration'])
        assert video['thumbnailUrl']==[film['thumbnailUrl']]
        assert video['embedUrl']=='https://www.youtube-nocookie.com/embed/'+film['source']
        assert 'contentUrl' not in video, 'Do not use a YouTube watch URL as a raw video file URL'
        players=page.find('iframe')
        assert len(players)==1 and players[0]['src']==video['embedUrl']+'?rel=0&cc_load_policy=0&playsinline=1'
        assert players[0]['loading']=='eager', 'The primary player must load without clicking'
        assert film['description'][lang] in source
        assert page.find('meta',property='og:image',content=film['thumbnailUrl'])
        assert not page.find('section',**{'class':'section watch-story'}), 'Stories are removed pending owner-written copy'
    if relative in ['/en/','/fi/']:
        intro=page.find('video',**{'class':'intro-video'})
        assert len(intro)==1 and 'controls' not in intro[0]
        assert all(key in intro[0] for key in ['autoplay','muted','loop','playsinline'])
    if relative in ['/en/','/fi/','/en/wedding-films/','/fi/haavideot/']:
        deferred=page.find('button',**{'class':'inline-video-preview'})
        assert len(deferred)==(1 if relative in ['/en/','/fi/'] else 3)
        assert all('src' not in a for a in deferred), 'Inline players must not load before play is clicked'
        assert {a['data-video-src'] for a in deferred}=={a['src'] for a in page.find('iframe',**{'class':'video-fallback'})}, 'Keep working no-JavaScript players'
    if 'photography/' in relative or 'haavalokuvaus/' in relative:
        assert len(page.find('figure',**{'class':'gallery-item'}))==12
sitemap=ET.parse(DIST/'sitemap.xml')
urls=[el.text for el in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(urls)==20 and len(set(urls))==20
for url in urls: assert (DIST/url.removeprefix(BASE).lstrip('/')/'index.html').exists()
assert (DIST/'js/app.js').exists() and (DIST/'fonts/italiana-latin.woff2').exists()
video_ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','v':'http://www.google.com/schemas/sitemap-video/1.1'}
entries=[entry for entry in sitemap.findall('s:url',video_ns) if entry.find('v:video',video_ns) is not None]
assert len(entries)==14, 'Every watch page needs a video sitemap entry'
for entry in entries:
    url=entry.find('s:loc',video_ns).text
    lang,film=watch_paths[url.removeprefix(BASE)]
    video=entry.find('v:video',video_ns)
    assert video.find('v:title',video_ns).text==film['title'][lang]
    assert video.find('v:description',video_ns).text==film['description'][lang]
    assert video.find('v:thumbnail_loc',video_ns).text==film['thumbnailUrl']
    assert video.find('v:publication_date',video_ns).text==film['uploadDate']
    assert video.find('v:player_loc',video_ns).text=='https://www.youtube-nocookie.com/embed/'+film['source']
print('PASS: 20 bilingual production pages, 7 verified uploads + 3 originals, 14 watch pages with matching video metadata and sitemap entries, internal links/anchors, reciprocal languages, pricing, forms, galleries and looping intro.')

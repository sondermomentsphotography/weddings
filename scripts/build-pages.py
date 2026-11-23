#!/usr/bin/env python3
"""Generate crawlable bilingual pages from shared templates and preserved copy."""
from pathlib import Path
import html
import json
import re
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://sondermomentsphotography.com'
COPY = json.loads((ROOT / 'content/copy.json').read_text())
DIMENSIONS = json.loads((ROOT / 'content/image-dimensions.json').read_text())
MEDIA = json.loads((ROOT / 'content/films.json').read_text())
PRICES = json.loads((ROOT / 'content/pricing.json').read_text())
SERVICE_AREAS = json.loads((ROOT / 'content/service-areas.json').read_text())
ROUTES = {'en': {'home': '/en/', 'photography': '/en/wedding-photography/', 'films': '/en/wedding-films/'}, 'fi': {'home': '/fi/', 'photography': '/fi/haavalokuvaus/', 'films': '/fi/haavideot/'}}

def e(s): return html.escape(str(s), quote=True)
def text(lang, en, fi): return fi if lang == 'fi' else en
def image(name, alt, eager=False, cls='', enlarge=False):
    width, height = DIMENSIONS[name]
    priority = ' fetchpriority="high"' if eager else ''
    markup = f'<img src="/img/{name}.webp" alt="{e(alt)}" class="{cls}" width="{width}" height="{height}" loading="{"eager" if eager else "lazy"}" decoding="async"{priority}>'
    return f'<a class="photo-open" href="/img/{name}.webp" data-photo aria-haspopup="dialog">{markup}</a>' if enlarge else markup
def embed_player(source, title, eager=False):
    # Do not force captions on; YouTube may still honor a viewer's saved preference.
    url = f'https://www.youtube-nocookie.com/embed/{source}?rel=0&cc_load_policy=0&playsinline=1'
    attributes = f'width="1280" height="720" title="{e(title)}" referrerpolicy="strict-origin-when-cross-origin" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen'
    if eager:
        # The primary video on a watch page must be discoverable without JavaScript.
        return f'<iframe src="{e(url)}" {attributes} loading="eager"></iframe>'
    # Like the original site, request YouTube's player only on a play click.
    # JavaScript adds autoplay so that the same click also starts playback.
    return f'''<button type="button" class="inline-video-preview" data-video-src="{e(url)}" data-video-title="{e(title)}" aria-label="{e(title)}"><img src="https://i.ytimg.com/vi/{e(source)}/hqdefault.jpg" alt="" width="480" height="360" loading="lazy" decoding="async"><span class="play-circle" aria-hidden="true">▶</span></button><noscript><style>.inline-video-preview{{display:none}}</style><iframe class="video-fallback" src="{e(url)}" {attributes} loading="lazy"></iframe></noscript>'''

def paragraphs(value):
    return ''.join(f'<p>{p.strip()}</p>' for p in re.split(r'(?:<br\s*/?>\s*){2}', value) if p.strip())
def button(url, label, secondary=False):
    return f'<a class="button{" button-outline" if secondary else ""}" href="{url}">{label} <span aria-hidden="true">↗</span></a>'
def price(lang, kind):
    return f'{PRICES[kind]["total"]:,}'.replace(',', ' ') + ' €' if lang == 'fi' else '€' + f'{PRICES[kind]["total"]:,}'

def header(lang, page, alternate=None):
    r = ROUTES[lang]
    other = 'fi' if lang == 'en' else 'en'
    labels = {'home': text(lang,'Home','Etusivu'), 'photography': text(lang,'Photography','Valokuvaus'), 'films': text(lang,'Wedding films','Häävideot')}
    links = ''.join(f'<a href="{r[k]}"'+(' aria-current="page"' if k == page else '')+f'>{v}</a>' for k,v in labels.items())
    return f'''<a class="skip" href="#main">{text(lang,'Skip to content','Siirry sisältöön')}</a>
<header class="site-header"><div class="shell header-inner">
<a class="brand" href="{r['home']}" aria-label="Sonder Moments Weddings"><span class="brand-name">Sonder Moments</span><span class="brand-signature">Weddings · by Sirle</span></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="navigation">{text(lang,'Menu','Valikko')} <span aria-hidden="true">☰</span></button>
<nav id="navigation" class="nav" aria-label="{text(lang,'Main navigation','Päävalikko')}">{links}<a href="{r['home']}#about-me">{text(lang,'Meet Sirle','Sirle')}</a><a class="nav-contact" href="#contact">{text(lang,'Let’s talk','Ota yhteyttä')} ↗</a>
<a class="language" href="{alternate or ROUTES[other][page]}" lang="{other}" hreflang="{other}" aria-label="{text(lang,'Vaihda suomeksi','Switch to English')}">{other.upper()}</a></nav></div></header>'''

def contact(lang, page):
    labels = text(lang, ['Your names','Email','Phone (optional)','Wedding date (optional)','Wedding location (optional)','Tell me about your day'], ['Nimenne','Sähköposti','Puhelin (vapaaehtoinen)','Hääpäivä (vapaaehtoinen)','Hääpaikka (vapaaehtoinen)','Kerro hääpäivästänne'])
    fields = ''
    for name,typ,label in zip(['name','email','phone','date','location'],['text','email','tel','date','text'],labels):
        fields += f'<div class="field"><label for="{name}">{label}</label><input id="{name}" name="{name}" type="{typ}"'+(' required' if name in ['name','email'] else '')+(f' autocomplete="{dict(name="name",email="email",phone="tel")[name]}"' if name in ['name','email','phone'] else '')+'></div>'
    selection = ''.join(f'<option value="{k}"'+(' selected' if k == page else '')+f'>{v}</option>' for k,v in [('both',text(lang,'Photography & films','Valokuvaus ja häävideot')),('photography',text(lang,'Photography','Valokuvaus')),('films',text(lang,'Wedding films','Häävideot'))])
    return f'''<section class="section contact-section" id="contact"><div class="shell contact-grid"><div>
<p class="eyebrow">{text(lang,'Your story starts here','Teidän tarinanne alkaa tästä')}</p><h2>{text(lang,'Let’s create something<br><em>truly magical.</em>','Luodaan yhdessä<br><em>jotain unohtumatonta.</em>')}</h2>
<p>{text(lang,'I offer full photography and videography services and would love to hear from you. Tell me your date, your plans, and a little about the two of you.','Tarjoan kattavia valokuvaus- ja videokuvauspalveluita, ja olisi hienoa kuulla teistä. Kertokaa hääpäivästänne, suunnitelmistanne ja hieman itsestänne.')}</p>
<a class="contact-link" href="mailto:info@sondermomentsphotography.com">info@sondermomentsphotography.com</a><a class="contact-link" href="tel:+358404859969">+358 40 485 9969</a>
<p class="small">{text(lang,'Helsinki metropolitan area · Across Finland & Europe','Helsinki ja pääkaupunkiseutu · Koko Suomi ja Eurooppa')}</p></div>
<form id="contactForm" class="contact-form"><div class="form-grid">{fields}<div class="field"><label for="service">{text(lang,'I’m interested in','Olen kiinnostunut')}</label><select id="service" name="service">{selection}</select></div></div>
<div class="field"><label for="message">{labels[-1]}</label><textarea id="message" name="message" rows="5" required></textarea></div>
<p class="small">{text(lang,'Your details are used to respond to your inquiry. This message is an inquiry; your booking is agreed separately.','Tietojanne käytetään yhteydenottoonne vastaamiseen. Viesti on tiedustelu; varauksesta sovitaan erikseen.')}</p>
<button type="submit" class="button">{text(lang,'Send your message','Lähetä viesti')} <span aria-hidden="true">↗</span></button><p id="form-status" role="status" aria-live="polite"></p></form></div></section>'''

def footer(lang):
    r=ROUTES[lang]
    return f'''<footer class="footer"><div class="shell footer-top"><a class="brand" href="{r['home']}"><span class="brand-name">Sonder Moments</span><span class="brand-signature">Weddings · by Sirle</span></a><p>{text(lang,'The romance. The chaos. The moments in between.','Romantiikka. Juhlat. Kaikki niiden väliltä.')}</p><div class="footer-social"><a href="https://www.instagram.com/sondermomentsweddings/">Instagram ↗</a><a href="https://www.youtube.com/@SonderMomentsWeddings">YouTube ↗</a></div></div><div class="shell footer-family"><p class="eyebrow">{text(lang,'More from Sonder Moments','Muut Sonder Moments -sivustot')}</p><nav class="footer-family-links" aria-label="{text(lang,'Other Sonder Moments websites','Muut Sonder Moments -sivustot')}"><a href="https://boudoirstudio.fi/" target="_blank" rel="noopener">Boudoir Studio <span aria-hidden="true">↗</span></a><a href="https://media.sondermomentsphotography.com/" target="_blank" rel="noopener">Sonder Moments Media <span aria-hidden="true">↗</span></a><a href="https://tinderkuvaus.fi/" target="_blank" rel="noopener">Tinderkuvaus <span aria-hidden="true">↗</span></a></nav></div><div class="shell footer-bottom"><span>© Sonder Moments Weddings</span><div><a href="{r['photography']}">{text(lang,'Wedding photography','Häävalokuvaus')}</a><a href="{r['films']}">{text(lang,'Wedding films','Häävideot')}</a><a href="/en/" lang="en">EN</a><a href="/fi/" lang="fi">FI</a></div></div></footer>'''

def reviews(lang, kind='home'):
    names = [('review1','Bethany Scott'),('review2','Shaden Sawaya')] if kind == 'films' else [('review3','Emma Eaton'),('review1','Bethany Scott')]
    # Verbatim excerpts from the reviews already published in the original site.
    return f'''<section class="section testimonials"><div class="shell"><p class="eyebrow">{text(lang,'Kind words','Asiakkaiden sanoin')}</p><h2>{text(lang,'Memories to <em>come back to.</em>','Muistoja, joihin <em>palata.</em>')}</h2><div class="quote-grid">'''+''.join(f'<figure class="quote"><span class="quote-mark" aria-hidden="true">“</span><blockquote>{COPY[lang][key]}</blockquote><figcaption>{name}</figcaption></figure>' for key,name in names)+ '</div></div></section>'

def published_films():
    return MEDIA['featured'] + MEDIA['reels']

def film_path(lang, film):
    return ROUTES[lang]['films'] + film['slug'][lang] + '/'

def runtime(film):
    match = re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', film['duration'])
    hours, minutes, seconds = [int(n or 0) for n in match.groups()]
    return f'{hours}:{minutes:02d}:{seconds:02d}' if hours else f'{minutes}:{seconds:02d}'

def locations(lang):
    films_by_id = {film['source']: film for film in published_films()}
    links = ''.join(f'<li><a href="{film_path(lang, films_by_id[item["source"]])}">{e(item["name"])}<span aria-hidden="true">↗</span></a></li>' for item in MEDIA['locations'])
    return f'''<section class="section locations"><div class="shell split"><div><p class="eyebrow">{text(lang,'Find your setting','Löydä juhlanne tunnelma')}</p><h2>{text(lang,'Different places.<br><em>Your kind of day.</em>','Erilaisia paikkoja.<br><em>Oman näköinen päivä.</em>')}</h2></div><div><p>{text(lang,'A wedding party at The Terwa, a ferry ride to Seurasaari, a celebration in Suomenlinna, an English countryside wedding and bridal inspiration in Helsinki. Explore the films by their setting.','The Terwan hääjuhla, lauttamatka Seurasaareen, häät Suomenlinnassa, juhlat Englannin maaseudulla ja morsiusunelmia Helsingissä. Tutustu videoihin kuvauspaikan mukaan.')}</p><ul class="location-list">{links}</ul></div></div></section>'''

def home(lang):
    r=ROUTES[lang]
    intro = re.split(r'(?:<br\s*/?>\s*){2}',COPY[lang]['intro'])
    terwa = next(film for film in MEDIA['featured'] if film['source'] == 'XGbWo8vvK0E')
    return f'''<main id="main"><section class="hero shell"><div class="hero-heading"><div><p class="eyebrow">{text(lang,'Wedding photography & films · Finland & beyond','Häävalokuvaus ja häävideot · Suomi ja Eurooppa')}</p><h1>{text(lang,'Your day.<br><em>Your kind of magic.</em>','Teidän päivänne.<br><em>Teidän tarinanne.</em>')}</h1></div><div class="hero-aside"><p>{text(lang,'The laughter, the happy tears, the dodgy dance moves. Wedding photography and cinematic films that feel like you.','Nauru, onnenkyyneleet ja unohtumattomat tanssiliikkeet. Häävalokuvaus ja elokuvalliset häävideot, jotka tuntuvat teiltä.')}</p><p class="small">{text(lang,'Helsinki metropolitan area · All of Finland & Europe','Helsinki ja pääkaupunkiseutu · Koko Suomi ja Eurooppa')}</p>{button(r['films'],text(lang,'Explore the films','Katso häävideot'))}{button(r['photography'],text(lang,'See the photographs','Katso hääkuvat'),True)}</div></div><figure class="hero-image"><video class="intro-video" aria-label="{text(lang,'Sonder Moments wedding intro film','Sonder Momentsin häävideokooste')}" autoplay muted loop playsinline preload="metadata" poster="/img/wedding-intro-poster.webp"><source src="/img/wedding-reel-mobile-phone.webm" type="video/webm" media="(max-width: 420px)"><source src="/img/wedding-reel-mobile.webm" type="video/webm" media="(max-width: 600px)"><source src="/img/show-reel-mobile.mp4" type="video/mp4" media="(max-width: 600px)"><source src="/img/wedding-reel.webm" type="video/webm"><source src="/img/show-reel-small.mp4" type="video/mp4"><a href="/img/show-reel-small.mp4">{text(lang,'Watch the intro film','Katso esittelyvideo')}</a></video><figcaption><span>Sonder Moments Weddings</span><span>{text(lang,'Honest moments. Beautifully told.','Aitoja hetkiä. Kauniisti kerrottuna.')}</span></figcaption></figure></section>
<section class="section intro"><div class="shell split"><div><p class="eyebrow">{text(lang,'A relaxed, story-driven approach','Rennosti, teidän tarinanne mukaan')}</p><h2>{text(lang,'Your wedding bestie.<br><em>With a camera.</em>','Hääpäivänne ystävä.<br><em>Kamera kädessä.</em>')}</h2></div><div class="prose">{paragraphs(intro[0])}<details class="story-more"><summary>{text(lang,'A little more about my approach','Lisää kuvaustavastani')}</summary>{paragraphs('<br><br>'.join(intro[1:]))}</details></div></div></section>
<section class="section services" id="photos"><div class="shell"><div class="section-heading"><p class="eyebrow">{text(lang,'Two ways to relive it all','Kaksi tapaa palata tunnelmaan')}</p><h2>{text(lang,'The feeling <em>stays.</em>','Tunne <em>säilyy.</em>')}</h2></div><div class="service-grid"><article class="service-card"><a href="{r['photography']}" class="service-image">{image('wedding-couple-kissing',text(lang,'Newlyweds sharing a kiss','Hääparin suudelma'))}</a><div class="card-meta"><span>{text(lang,'Photography','Valokuvaus')}</span><span>{text(lang,'From','Alkaen')} {price(lang,'photography')}</span></div><h3>{text(lang,'Love, without the awkward posing.','Rakkautta ilman jäykkiä poseerauksia.')}</h3><p>{text(lang,'Fun little prompts, genuine smiles, and gorgeous, frame-it-this-instant images. Let’s capture your day in a way that’s totally, brilliantly you.','Hauskoja vinkkejä, aitoja hymyjä ja kuvia, jotka haluatte kehystää heti. Tallennetaan teidän päivänne juuri teidän näköisellä tavalla.')}</p><a class="text-link" href="{r['photography']}">{text(lang,'Explore wedding photography','Tutustu häävalokuvaukseen')} ↗</a></article>
<article class="service-card" id="videography"><div class="service-image film-player">{embed_player(terwa['source'],terwa['title'][lang])}</div><div class="card-meta"><span>{text(lang,'Wedding films','Häävideot')}</span><span>{text(lang,'From','Alkaen')} {price(lang,'films')}</span></div><h3>{text(lang,'All the best bits. All the feels.','Kaikki parhaat hetket. Kaikki tunteet.')}</h3><p>{text(lang,'A cinematic, story-driven mini-movie filled with the laughter, the love, and just the right amount of chaos that made your day unforgettable.','Elokuvallinen, tarinallinen häävideo, joka on täynnä naurua, rakkautta ja juuri sopivasti sitä kaaosta, joka teki päivästänne unohtumattoman.')}</p><a class="text-link" href="{film_path(lang,terwa)}">{text(lang,'Watch the Terwa wedding film','Katso The Terwan häävideo')} ↗</a></article></div><p class="small vat-note">{text(lang,'Starting prices include 25.5% VAT.','Alkaen-hinnat sisältävät arvonlisäveron 25,5 %.')}</p></div></section>
{about(lang)}{reviews(lang)}{contact(lang,'home')}</main>'''

def about(lang):
    value=COPY[lang]['about']
    # Keep the personal story; remove stale relative dates and unconfirmed studio location.
    if lang == 'en':
        value=value.replace('Eight years later, and I can honestly say', 'I can honestly say').replace('I’ve recently returned to Finland and launched my business here—so, exciting new chapter!', 'I returned to Finland and launched my business here.').replace('have my photographic studio in Helsinki and ', '')
    else:
        value=value.replace('Kahdeksan vuotta myöhemmin', 'Tänäkin päivänä').replace('olen hiljattain palannut Suomeen ja perustanut tänne oman yritykseni – uusi ja jännittävä luku elämässäni!', 'palasin Suomeen ja perustin tänne oman yritykseni.').replace(' ja minulla on valokuvausstudio Helsingissä', '')
    return f'''<section class="section about" id="about-me"><div class="shell about-grid"><figure>{image('web-size-sirle',text(lang,'Sirle, the photographer and filmmaker behind Sonder Moments','Sirle, Sonder Momentsin valokuvaaja ja videokuvaaja'))}<figcaption>Sirle / Sonder Moments</figcaption></figure><div><p class="eyebrow">{text(lang,'The woman behind the camera','Nainen kameran takana')}</p><h2>{text(lang,'Hi, <em>I’m Sirle.</em>','Hei, <em>olen Sirle.</em>')}</h2><div class="prose">{paragraphs(value)}</div><a class="text-link" href="#contact">{text(lang,'Let’s talk about your day','Jutellaan hääpäivästänne')} ↗</a></div></div></section>'''

def service_hero(lang,kind):
    photo=kind=='photography'
    r=ROUTES[lang]
    h1=text(lang,'Wedding photography<br><em>that feels like you.</em>','Häävalokuvaus,<br><em>joka tuntuu teiltä.</em>') if photo else text(lang,'Your wedding.<br><em>A film to feel.</em>','Teidän häänne.<br><em>Elokuvana.</em>')
    desc=text(lang,'Let’s make your love shine, without the awkward posing. Natural, relaxed wedding photography in Helsinki and across Finland.','Ikuistetaan teidän rakkautenne ilman kömpelöitä poseerauksia. Luonnollinen ja rento häävalokuvaus Helsingissä ja koko Suomessa.') if photo else text(lang,'The laughter, the tears, the dodgy dance moves. Cinematic, story-driven wedding films in Helsinki, Finland and across Europe.','Nauru, kyyneleet ja unohtumattomat tanssiliikkeet. Elokuvalliset, tarinalliset häävideot Helsingissä, koko Suomessa ja Euroopassa.')
    media=image('wedding-couple-kissing-outside',text(lang,'A wedding couple kissing outdoors','Hääpari suutelee ulkona'),True,enlarge=True) if photo else f'''<video id="showreel" aria-label="{text(lang,'Sonder Moments wedding showreel','Sonder Momentsin häävideokooste')}" controls playsinline preload="metadata" poster="/img/wedding-intro-poster.webp"><source src="/img/show-reel-small.mp4" type="video/mp4"><a href="/img/show-reel-small.mp4">{text(lang,'Watch the wedding showreel','Katso häävideokooste')}</a></video>'''
    return f'''<section class="service-hero shell"><nav class="breadcrumb" aria-label="{text(lang,'Breadcrumb','Murupolku')}"><a href="{r['home']}">{text(lang,'Home','Etusivu')}</a><span aria-hidden="true">/</span><span>{text(lang,'Wedding photography','Häävalokuvaus') if photo else text(lang,'Wedding films','Häävideot')}</span></nav><div class="service-hero-grid"><div><p class="eyebrow">{text(lang,'Helsinki · Finland · Europe','Helsinki · Suomi · Eurooppa')}</p><h1>{h1}</h1><p class="lead">{desc}</p><div class="hero-actions">{button('#portfolio',text(lang,'See the photographs','Katso hääkuvat') if photo else text(lang,'Watch the films','Katso hääelokuvat'))}{button('#pricing',text(lang,'Explore pricing','Tutustu hintoihin'),True)}</div><p class="small">{text(lang,'From','Alkaen')} {price(lang,kind)} · {text(lang,'including 25.5% VAT','sis. alv 25,5 %')}</p></div><figure class="service-hero-image">{media}</figure></div></section>'''

def pricing(lang,kind):
    photo=kind=='photography'
    r=ROUTES[lang]
    desc=text(lang,'Every couple is different. Some of you are all about the grand romance, some of you are big on the party vibes, and some of you just want to get to the cake cutting as quickly as possible.','Jokainen pari on oman näköinen. Jotkut teistä rakastavat suurta romantiikkaa, toiset haluavat juhlatunnelmaa, ja kolmannet vain haluavat päästä kakunleikkaukseen mahdollisimman nopeasti.')
    return f'''<section class="section pricing" id="pricing"><div class="shell split"><div><p class="eyebrow">{text(lang,'Your day, your way','Teidän päivänne, teidän tavallanne')}</p><h2>{text(lang,'Beautiful memories.<br><em>Clear starting prices.</em>','Kauniita muistoja.<br><em>Selkeä alkaen-hinta.</em>')}</h2><p>{desc}</p></div><div class="price-card"><p class="eyebrow">{text(lang,'Wedding photography','Häävalokuvaus') if photo else text(lang,'Wedding films','Häävideot')}</p><p class="price-label">{text(lang,'Wedding day coverage from','Hääpäivän kuvaus alkaen') if photo else text(lang,'Full-day wedding film packages from','Koko päivän häävideopaketit alkaen')}</p><p class="price">{price(lang,kind)}</p><p class="small">{text(lang,'Includes 25.5% VAT','Sisältää arvonlisäveron 25,5 %')}</p><p>{text(lang,'Get in touch for package details and a quote for your wedding day.','Ottakaa yhteyttä, niin saatte lisätietoja paketeista ja tarjouksen omalle hääpäivällenne.')}</p>{button('#contact',text(lang,'Ask about your date','Kysy hääpäivänne kuvausta'))}</div></div></section>'''

def gallery(lang):
    names=['wedding-couple-kissing','bridesmaids-getting-ready','wedding-couple-outdoors','bride-in-dress','wedding-couple-outside','wedding-couple-walking','wedding-couple-kissing-outside','groom-and-friends','wedding-ceremony','wedding-guests-partying','groom-and-best-man','wedding-guests']
    en=['A wedding couple sharing a kiss','Bridesmaids getting ready together','Wedding portraits in an orchard','A bride in her wedding dress','Newlyweds outside their wedding venue','A couple walking together on their wedding day','A kiss outdoors on the wedding day','The groom and his friends','The wedding ceremony','Wedding guests on the dance floor','The groom with his best man','Guests celebrating the wedding']
    fi=['Hääparin suudelma','Kaasot valmistautuvat yhdessä','Hääpotretit omenatarhassa','Morsian hääpuvussaan','Hääpari juhlatilan ulkopuolella','Hääpari kävelee yhdessä','Hääpäivän suudelma ulkona','Sulhanen ystävineen','Vihkiseremonia','Häävieraat tanssilattialla','Sulhanen ja bestman','Häävieraat juhlimassa']
    cards=''.join(f'<figure class="gallery-item">{image(name,text(lang,en[i],fi[i]),enlarge=True)}</figure>' for i,name in enumerate(names))
    return f'''<section class="section gallery-section" id="portfolio"><div class="shell"><div class="section-heading"><p class="eyebrow">{text(lang,'A few favourite moments','Muutamia suosikkihetkiä')}</p><h2>{text(lang,'The romance. The chaos.<br><em>All of you.</em>','Romantiikka. Juhlat.<br><em>Juuri te.</em>')}</h2></div><div class="gallery-grid">{cards}</div></div></section>'''

def film_card(lang, film, reel=False):
    title = film['title'][lang]
    source = film['source']
    label = text(lang,'Short wedding film','Lyhyt häävideo') if reel else text(lang,'Wedding film','Hääelokuva')
    if film.get('slug'):
        path = film_path(lang, film)
        player = f'''<a class="film-player film-watch-link" href="{path}" aria-label="{e(text(lang,'Watch: ','Katso: ')+title)}"><img src="{e(film['thumbnailUrl'])}" width="1280" height="720" alt="{e(text(lang,'Video thumbnail: ','Videon esikatselukuva: ')+title)}" loading="lazy" decoding="async"><span class="play-circle" aria-hidden="true">▶</span><span class="play-caption">{text(lang,'Watch film','Katso video')}</span></a>'''
        note = e(film['description'][lang])
        heading = f'<a href="{path}">{e(title)}</a>'
        more = f'<a class="text-link" href="{path}">{text(lang,"Watch the film and story","Katso video ja tarina")} ↗</a>'
        label += ' · ' + runtime(film)
    else:
        player = f'<div class="film-player">{embed_player(source,title)}</div>'
        note = text(lang,'A wedding story by Sonder Moments.','Sonder Momentsin kuvaama häätarina.')
        heading = e(title)
        more = ''
    return f'<article class="film-card{" reel-card" if reel else ""}">{player}<p class="card-label">{label}</p><h3>{heading}</h3><p class="small">{note}</p>{more}</article>'

def films(lang):
    featured = ''.join(film_card(lang, film) for film in MEDIA['featured'])
    existing = ''.join(film_card(lang, film) for film in MEDIA['existing'])
    reels = ''.join(film_card(lang, film, True) for film in MEDIA['reels'])
    return f'''<section class="section films-section" id="portfolio"><div class="shell"><div class="section-heading"><p class="eyebrow">{text(lang,'Wedding films from Finland & England','Häävideoita Suomesta ja Englannista')}</p><h2>{text(lang,'<em>Feel it all again.</em>','<em>Tunne kaikki uudelleen.</em>')}</h2><p>{text(lang,'Explore the wedding films from The Terwa, Seurasaaren Juhlatalo, Suomenlinna and Valley Side Barn. Each film has its own story, with a little of the laughter, love and party that made the day.','Tutustu häävideoihin The Terwasta, Seurasaaren Juhlatalolta, Suomenlinnasta ja Valley Side Barnista. Jokainen elokuva kertoo oman tarinansa päivän naurusta, rakkaudesta ja juhlatunnelmasta.')}</p></div><div class="film-grid featured-film-grid">{featured}</div></div></section>
<section class="section reels-section" id="short-films"><div class="shell"><div class="section-heading"><p class="eyebrow">{text(lang,'A little burst of everything','Pieni pala koko tunnelmaa')}</p><h2>{text(lang,'Short films.<br><em>Big feelings.</em>','Lyhyet videot.<br><em>Suuret tunteet.</em>')}</h2><p>{text(lang,'A wedding party at The Terwa, bridal inspiration at Solo Sokos Hotel Pier 4 and a Suomenlinna wedding trailer. Three short films, each under a minute.','The Terwan hääreivit, morsiusunelmia Solo Sokos Hotel Pier 4:ssä ja häätraileri Suomenlinnasta. Kolme lyhyttä videota, jokainen alle minuutin.')}</p></div><div class="reels-grid">{reels}</div></div></section>
{locations(lang)}<section class="section earlier-films"><div class="shell"><div class="section-heading"><p class="eyebrow">{text(lang,'Wedding films from England','Häävideoita Englannista')}</p><h2>{text(lang,'Stories to <em>come back to.</em>','Tarinoita, joihin <em>palata.</em>')}</h2></div><div class="film-grid">{existing}</div></div></section>'''

def watch_body(lang, film):
    title = e(film['title'][lang])
    short = film['kind'] == 'reel'
    label = text(lang,'Short wedding film','Lyhyt häävideo') if short else text(lang,'Wedding film','Hääelokuva')
    date = film['uploadDate'][:10]
    date_label = datetime.fromisoformat(date).strftime('%d.%m.%Y' if lang == 'fi' else '%d %b %Y')
    related_ids = film.get('related', [])
    related = [other for other in published_films() if other['source'] in related_ids]
    related_markup = ''
    if related:
        links = ''.join(f'<a class="text-link" href="{film_path(lang, other)}">{e(other["title"][lang])} ↗</a>' for other in related)
        if all(other['kind'] == 'film' for other in related):
            related_heading = text(lang, 'Watch the longer version', 'Katso pidempi versio')
        else:
            related_heading = text(lang, 'Watch the shorter version', 'Katso lyhyempi versio')
        related_markup = f'<aside class="related-film shell"><h2>{related_heading}</h2>{links}</aside>'
    return f'''<main id="main"><section class="watch-hero shell"><nav class="breadcrumb" aria-label="{text(lang,'Breadcrumb','Murupolku')}"><a href="{ROUTES[lang]['home']}">{text(lang,'Home','Etusivu')}</a><span aria-hidden="true">/</span><a href="{ROUTES[lang]['films']}">{text(lang,'Wedding films','Häävideot')}</a><span aria-hidden="true">/</span><span>{e(film['venue'])}</span></nav><p class="eyebrow">{label} · {runtime(film)} · {e(film['place'][lang])}</p><h1>{title}</h1><div class="film-player watch-player">{embed_player(film['source'],film['title'][lang],eager=True)}</div><div class="watch-meta"><span>{text(lang,'Published on YouTube','Julkaistu YouTubessa')} <time datetime="{date}">{date_label}</time></span></div></section>{related_markup}<section class="cross-link shell"><p class="eyebrow">{text(lang,'Your own wedding story','Teidän oma häätarinanne')}</p><h2>{text(lang,'Shall we tell <em>your story?</em>','Kerrotaanko seuraavaksi <em>teidän tarinanne?</em>')}</h2><p>{text(lang,'I create relaxed, cinematic wedding films in Finland and across Europe. Tell me about your date, your plans and the two of you.','Kuvaan rentoja, elokuvallisia häävideoita Suomessa ja Euroopassa. Kertokaa hääpäivästänne, suunnitelmistanne ja teistä kahdesta.')}</p><div class="watch-actions">{button(ROUTES[lang]['films'],text(lang,'Wedding films & pricing','Häävideot ja hinnat'),True)}</div></section>{contact(lang,'films')}</main>'''

def service(lang,kind):
    value=COPY[lang]['photography' if kind=='photography' else 'films']
    # Price and brochure calls-to-action are maintained in one dedicated pricing block.
    chunks=re.split(r'(?:<br\s*/?>\s*){2}',value)
    if kind=='photography':
        chunks=chunks[:4]
    else:
        # Retain the story and description, omit unsupported regret-ranking claims and stale brochure pricing.
        chunks=[chunks[i] for i in [1,3,4,5] if i<len(chunks)]
    title=text(lang,'Let’s make your love shine.','Ikuistetaan teidän rakkautenne.') if kind=='photography' else text(lang,'Your story, told in a little movie.','Teidän tarinanne pienenä elokuvana.')
    # Avoid duplicating the opening headline within the body.
    if chunks and len(chunks[0])<110: chunks=chunks[1:]
    intro=f'<section class="section service-story"><div class="shell split"><div><p class="eyebrow">{text(lang,"The way I see it","Minun tapani kuvata")}</p><h2>{title}</h2></div><div class="prose">{paragraphs("<br><br>".join(chunks))}</div></div></section>'
    cross=ROUTES[lang]['films' if kind=='photography' else 'photography']
    crosslabel=text(lang,'Discover wedding films','Tutustu häävideoihin') if kind=='photography' else text(lang,'Discover wedding photography','Tutustu häävalokuvaukseen')
    return f'<main id="main">{service_hero(lang,kind)}{gallery(lang) if kind=="photography" else films(lang)}{intro}{pricing(lang,kind)}{reviews(lang,kind)}<section class="cross-link shell"><p class="eyebrow">{text(lang,"More of your story","Lisää teidän tarinaanne")}</p><h2>{text(lang,"Another way to <em>remember.</em>","Toinen tapa <em>muistaa.</em>")}</h2>{button(cross,crosslabel,True)}</section>{contact(lang,kind)}</main>'

def document(lang,page,body,film=None):
    photo=page=='photography'
    title=text(lang,'Wedding Photography & Films in Helsinki | Sonder Moments','Häävalokuvaus ja häävideot Helsinki | Sonder Moments') if page=='home' else (text(lang,'Wedding Photographer Helsinki, Finland | Sonder Moments','Häävalokuvaaja Helsinki | Sonder Moments') if photo else text(lang,'Wedding Videographer Helsinki, Finland | Sonder Moments','Häävideokuvaaja Helsinki | Sonder Moments'))
    description=text(lang,'Natural wedding photography and cinematic films by Sirle in Helsinki and across Finland. Relaxed guidance, real moments. Explore the work and ask about your date.','Luonnollinen häävalokuvaus ja elokuvalliset häävideot Helsingissä ja koko Suomessa. Sirlen rento ohjaus ja aidot hetket. Tutustu ja kysy kuvausta.') if page=='home' else (text(lang,'Relaxed, documentary wedding photography in Helsinki and across Finland. Natural smiles and real moments with Sirle. From €1,895 including VAT.','Rentoa, dokumentaarista häävalokuvausta Helsingissä ja koko Suomessa. Aitoja hymyjä ja hetkiä Sirlen kanssa. Häävalokuvaus alkaen 1 895 €, sis. alv.') if photo else text(lang,'Cinematic wedding films in Helsinki, Finland and Europe. Watch Sirle’s wedding films and discover the story-driven approach. From €2,595 including VAT.','Elokuvalliset häävideot Helsingissä, Suomessa ja Euroopassa. Katso Sirlen hääelokuvia ja tutustu tarinalliseen kuvaustapaan. Alkaen 2 595 €, sis. alv.'))
    if page in ['photography', 'films']:
        description = description.replace('€1,895', price(lang, 'photography')).replace('1 895 €', price(lang, 'photography')).replace('€2,595', price(lang, 'films')).replace('2 595 €', price(lang, 'films'))
    if film:
        title = film['title'][lang] + ' | Sonder Moments'
        description = film['description'][lang]
    path = film_path(lang, film) if film else ROUTES[lang][page]
    url = BASE + path
    share_image = film['thumbnailUrl'] if film else BASE + '/img/wedding-couple-outdoors.jpg'
    schema={'@context':'https://schema.org','@graph':[{'@type':'Organization','@id':BASE+'/#business','name':'Sonder Moments Weddings','url':BASE,'areaServed':SERVICE_AREAS,'telephone':'+358404859969','email':'info@sondermomentsphotography.com','sameAs':['https://www.instagram.com/sondermomentsweddings/','https://www.youtube.com/@SonderMomentsWeddings']},{'@type':'WebPage','@id':url+'#page','url':url,'name':title,'description':description,'inLanguage':lang,'publisher':{'@id':BASE+'/#business'}}]}
    if page!='home' and not film:
        schema['@graph'].append({'@type':'Service','name':text(lang,'Wedding photography','Häävalokuvaus') if photo else text(lang,'Wedding videography','Häävideokuvaus'),'url':url,'provider':{'@id':BASE+'/#business'},'areaServed':SERVICE_AREAS,'offers':{'@type':'Offer','price':PRICES[page]['total'],'priceCurrency':'EUR','url':url+'#pricing','priceSpecification':{'@type':'PriceSpecification','price':PRICES[page]['total'],'priceCurrency':'EUR','valueAddedTaxIncluded':True}}})
        schema['@graph'].append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':text(lang,'Home','Etusivu'),'item':BASE+ROUTES[lang]['home']},{'@type':'ListItem','position':2,'name':title.split('|')[0].strip(),'item':url}]})
    if film:
        video_id = url + '#video'
        schema['@graph'][1]['mainEntity'] = {'@id': video_id}
        schema['@graph'].append({'@type':'VideoObject', '@id':video_id, 'name':film['title'][lang], 'description':film['description'][lang], 'thumbnailUrl':[film['thumbnailUrl']], 'uploadDate':film['uploadDate'], 'duration':film['duration'], 'embedUrl':'https://www.youtube-nocookie.com/embed/'+film['source'], 'url':url, 'publisher':{'@id':BASE+'/#business'}, 'mainEntityOfPage':{'@id':url+'#page'}})
        schema['@graph'].append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':text(lang,'Home','Etusivu'),'item':BASE+ROUTES[lang]['home']},{'@type':'ListItem','position':2,'name':text(lang,'Wedding films','Häävideot'),'item':BASE+ROUTES[lang]['films']},{'@type':'ListItem','position':3,'name':film['title'][lang],'item':url}]})
    language_paths = {other: film_path(other, film) if film else ROUTES[other][page] for other in ['en','fi']}
    alternates=''.join(f'<link rel="alternate" hreflang="{other}" href="{BASE+language_paths[other]}">' for other in ['en','fi'])
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#ffffff"><meta name="robots" content="index,follow"><link rel="canonical" href="{url}">{alternates}<link rel="alternate" hreflang="x-default" href="{BASE+language_paths['en']}"><meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{e(share_image)}"><meta property="og:locale" content="{text(lang,'en_GB','fi_FI')}"><meta property="og:site_name" content="Sonder Moments Weddings"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon_32x32.png"><link rel="manifest" href="/site.webmanifest"><link rel="preload" href="/fonts/italiana-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/css/weddings.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script><script src="/js/app.js" defer></script></head><body data-page="{page}">{header(lang,page,language_paths['fi' if lang == 'en' else 'en'])}{body}{footer(lang)}</body></html>'''

for lang in ['en','fi']:
    for page, path in ROUTES[lang].items():
        target = ROOT / path.strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document(lang, page, home(lang) if page=='home' else service(lang,page)).replace('><', '>\n<')+'\n')
    for film in published_films():
        target = ROOT / film_path(lang, film).strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document(lang, 'films', watch_body(lang,film), film).replace('><', '>\n<')+'\n')

urls = [BASE+path for routes in ROUTES.values() for path in routes.values()]
urls += [BASE+film_path(lang, film) for lang in ['en','fi'] for film in published_films()]
video_entries = ''
for lang in ['en','fi']:
    for film in published_films():
        video_entries += f'''  <url><loc>{xml_escape(BASE+film_path(lang,film))}</loc><video:video><video:thumbnail_loc>{xml_escape(film['thumbnailUrl'])}</video:thumbnail_loc><video:title>{xml_escape(film['title'][lang])}</video:title><video:description>{xml_escape(film['description'][lang])}</video:description><video:player_loc>https://www.youtube-nocookie.com/embed/{film['source']}</video:player_loc><video:publication_date>{film['uploadDate']}</video:publication_date></video:video></url>\n'''
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n'+''.join(f'  <url><loc>{url}</loc></url>\n' for url in urls[:6])+video_entries+'</urlset>\n')
print(f'Generated {len(urls)} bilingual pages and sitemap with 14 video entries.')

"""Baut die gemeinsame Website von TCM Zentrum München und TCM Tuina Massage.

Alle Seiten teilen Kopfzeile, Navigation, Fußbereich und Stylesheet.
Aufruf:  python3 build_site.py <Zielordner> <Quellordner mit tuina_*.html>

Interne Links werden als Pfade ab der Wurzel geschrieben und am Ende in relative
Pfade umgerechnet. So läuft die Seite unter einer eigenen Domain genauso wie in
einem Unterordner (z. B. GitHub Pages).
"""
import hashlib, pathlib, re, sys

OUT = pathlib.Path(sys.argv[1])
SRC = pathlib.Path(sys.argv[2])
# Kennung aus dem Inhalt von Stylesheet und Skript: Browser laden nach jeder Änderung die neue Fassung.
VER = hashlib.sha1(b"".join((OUT / "assets" / f).read_bytes() for f in ("style.css", "main.js"))).hexdigest()[:8]
SITE = "https://tcm-tuina-massage.de"
IMG = "/assets/img/"

TUINA_TEL, TUINA_TEL_TXT = "+4915157834602", "0151 578 346 02"
TCM_TEL, TCM_TEL_TXT = "+498928807280", "089 28 80 72 80"
TUINA_MAIL, TCM_MAIL = "info@tcm-tuina-massage.de", "zentrum@tcm-muenchen.com"
BOOK_URL = "https://app.cituro.com/booking/tcm-tuina-massage"
MAPS = "https://www.google.de/maps/place/48.14502562430879N+11.57844559690281E"
MAPS_BERG = "https://www.google.de/maps/search/Grafstra%C3%9Fe+26,+82335+Berg"

MENU_ICON = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="6" cy="12" r="2.2"/><circle cx="12" cy="12" r="2.2"/><circle cx="18" cy="12" r="2.2"/></svg>'
CLOSE_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg>'

# Bildnachweise (alle Bilder der Website, im Impressum vollständig aufgeführt)
CREDITS = [
    ("Tuina-Tafel der Handfläche", "Chinesischer Holzschnitt, Qing-Zeit", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=36079960"),
    ("Tuina-Tafel des Handrückens", "Chinesischer Holzschnitt, Qing-Zeit", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=36079994"),
    ("Tuina-Tafel für Handfläche und Unterarm", "Chinesischer Holzschnitt, Qing-Zeit", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=36079980"),
    ("Neun Kreisbewegungen, Tafel 3", "Chinesischer Holzschnitt", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=36094253"),
    ("Bronzefigur zur Akupunktur, Seitenansicht", "Chinesischer Holzschnitt", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=36075837"),
    ("Moxibustion, „Auf dem Bambuspferd reiten“", "Chinesischer Holzschnitt", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=36080266"),
    ("Erstausgabe des Bencao Gangmu, 1590", "Chinesischer Druck", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=33926795"),
    ("Schröpfgefäß", "Chinesischer Holzschnitt", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=36093623"),
    ("Tasten des Pulses am Handgelenk, 1817", "Chinesischer Holzschnitt", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=36064806"),
    ("Shennong", "Chinesischer Holzschnitt nach Gan Bozong", "Wellcome Collection, CC BY 4.0", "https://commons.wikimedia.org/w/index.php?curid=33926676"),
    ("Sitzender Fuxi", "Ma Lin, um 1230, Nationales Palastmuseum Taipeh", "gemeinfrei", "https://commons.wikimedia.org/w/index.php?curid=8921316"),
    ("Odeonsplatz, München", "Foto: Guido Radig", "CC BY-SA 4.0", "https://commons.wikimedia.org/w/index.php?curid=81074693"),
    ("Theatinerkirche, München", "Foto: Wilfredor", "CC0", "https://commons.wikimedia.org/wiki/File:Exterior_of_Theatinerkirche,_Munich.jpg"),
    ("Ludwigstraße im Winter", "Foto: SuPich", "CC0", "https://commons.wikimedia.org/w/index.php?curid=160784165"),
    ("Salondampfer bei Schloss Berg am Starnberger See", "Postkarte von Ottmar Zieher, um 1900", "gemeinfrei", "https://commons.wikimedia.org/w/index.php?curid=64822839"),
    ("U-Bahn-Ankunft am Odeonsplatz", "Video: Chris Light, Vorschaubild aus dem Video", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:Arrival_odenplatz_19-05-23_557.ogv"),
]
LIC = {"CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/deed.de",
       "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/deed.de",
       "CC0": "https://creativecommons.org/publicdomain/zero/1.0/deed.de"}

def lic(text):
    k = next((k for k in LIC if k in text), None)
    return text.replace(k, f'<a href="{LIC[k]}" rel="license noopener">{k}</a>') if k else text

# Zwei Bereiche einer Website: TCM Zentrum und Tuina-Massage
SECTIONS = {
    "tuina": dict(logo="tuina-logo.svg", name="TCM Tuina Massage", sub="im TCM Zentrum München",
                  home="/", tel=TUINA_TEL, tel_txt=TUINA_TEL_TXT, anfahrt="/#anfahrt",
                  glyphs=("推", "拿"), word="Tuina am<br>Odeonsplatz"),
    "zentrum": dict(logo="tcm-zentrum-logo.png", name="TCM Zentrum München", sub="am Odeonsplatz",
                    home="/zentrum/", tel=TCM_TEL, tel_txt=TCM_TEL_TXT, anfahrt="/zentrum/#standorte",
                    glyphs=("中", "医"), word="TCM Zentrum<br>München"),
}

def glyph(ch, cls):
    return f'<svg class="glyph {cls}" viewBox="0 0 100 100" aria-hidden="true"><text x="50" y="50" text-anchor="middle" dominant-baseline="central">{ch}</text></svg>'

def book(label="Termin buchen", cls="btn", dialog=True, href="/booking/"):
    return f'<a class="{cls}" href="{href}"{" data-booking" if dialog else ""}>{label}</a>'

def cta(sec, current, cls="btn"):
    """Hauptknopf in Kopf und Fuß: Tuina öffnet die Online-Buchung, TCM-Termine gibt es telefonisch."""
    if current == "kolleg":
        return f'<a class="{cls}" href="#kurse">Kursangebot</a>'
    if sec == "zentrum":
        return book("Termin vereinbaren", cls, dialog=False, href="/booking/#tcm-termin")
    if current == "booking":
        return book("Tuina online buchen", cls)
    return book("Termin buchen", cls)

def head(sec, current):
    s = SECTIONS[sec]
    cur = lambda k: ' aria-current="page"' if k == current else ""
    anfahrt = "#anfahrt" if current == "booking" else s["anfahrt"]
    anfahrt_label = "Standorte und Anfahrt" if sec == "zentrum" else "Zeiten und Anfahrt"
    return f'''<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="site-head">
  <a class="mark" href="{s["home"]}" aria-label="{s["name"]}, Startseite">
    <img src="{IMG}{s["logo"]}" alt="" width="44" height="44">
    <span>{s["name"]}<small>{s["sub"]}</small></span>
  </a>
  <nav class="head-links" aria-label="Hauptnavigation">
    <a href="/zentrum/"{cur("zentrum")}>Zentrum</a>
    <a href="/tcm/"{cur("tcm")}>TCM</a>
    <a href="/"{cur("tuina")}>Tuina</a>
    <a href="/tcm-kolleg/"{cur("kolleg")}>Kolleg</a>
    <a href="{anfahrt}">Anfahrt</a>
  </nav>
  <a class="head-tel" href="tel:{s["tel"]}">{s["tel_txt"]}</a>
  {cta(sec, current)}
  <details class="menu">
    <summary aria-label="Menü">{MENU_ICON}</summary>
    <nav class="menu-panel" aria-label="Menü">
      <a href="/zentrum/"{cur("zentrum")}>TCM Zentrum München</a>
      <a href="/tcm/"{cur("tcm")}>TCM-Therapie</a>
      <a href="/"{cur("tuina")}>Tuina-Massage</a>
      <a href="/tcm-kolleg/"{cur("kolleg")}>TCM Kolleg</a>
      <span class="sep"></span>
      <a href="/#preise">Preise Tuina-Massage</a>
      <a href="/#fragen">Fragen zur Tuina-Massage</a>
      <a href="{anfahrt}">{anfahrt_label}</a>
      <a href="/booking/"{cur("booking")}>Termin buchen</a>
      <a href="tel:{TUINA_TEL}">Tuina-Massage: {TUINA_TEL_TXT}</a>
      <a href="tel:{TCM_TEL}">TCM-Therapie: {TCM_TEL_TXT}</a>
      <span class="sep"></span>
      <a href="/impressum/"{cur("impressum")}>Impressum</a>
      <a href="/datenschutz/"{cur("datenschutz")}>Datenschutz</a>
    </nav>
  </details>
</header>'''

def foot(sec, current):
    s = SECTIONS[sec]
    g1, g2 = s["glyphs"]
    return f'''<footer class="site-foot">
  <div class="foot-top">
  <div class="foot-mark" aria-hidden="true">
    <span class="m-tui">{glyph(g1, "g-tui")}</span><span class="m-na">{glyph(g2, "g-na")}</span>
  </div>
  <p class="foot-word">{s["word"].replace("<br>", " ")}</p>
  </div>
  <div class="foot-cols">
    <div class="foot-col"><b>TCM Zentrum</b><a href="/zentrum/">Zentrum</a><a href="/tcm/">TCM-Therapie</a><a href="/tcm-kolleg/">TCM Kolleg</a></div>
    <div class="foot-col"><b>Tuina-Massage</b><a href="/">Was ist Tuina?</a><a href="/#preise">Preise</a><a href="/#fragen">Häufige Fragen</a></div>
    <div class="foot-col"><b>Besuch</b><a href="/booking/">Termin buchen</a><a href="{"#anfahrt" if current == "booking" else s["anfahrt"]}">Anfahrt</a><a href="{MAPS}" rel="noopener">Google Maps</a></div>
    <div class="foot-col"><b>Rechtliches</b><a href="/impressum/">Impressum</a><a href="/datenschutz/">Datenschutz</a><a href="/impressum/#bildnachweise">Bildnachweise</a></div>
    <div class="foot-addr">TCM Zentrum München<br>Ludwigstraße 11, 80539 München<br>TCM-Therapie <a href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a>Tuina-Massage <a href="tel:{TUINA_TEL}">{TUINA_TEL_TXT}</a></div>
  </div>
  <p class="credits">Bilder: Wellcome Collection, Nationales Palastmuseum Taipeh und Wikimedia Commons, einzeln aufgeführt in den <a href="/impressum/#bildnachweise">Bildnachweisen</a>.</p>
  <div class="foot-last"><span>© 2026 TCM Zentrum München</span>{cta(sec, current, "btn btn-light")}</div>
</footer>

<dialog class="booking" id="booking" aria-labelledby="booking-title">
  <div class="booking-inner">
    <div class="booking-bar">
      <div><b id="booking-title">Tuina-Massage online buchen</b><small>Lieber telefonisch? <a href="tel:{TUINA_TEL}">{TUINA_TEL_TXT}</a></small><small>Buchungssystem der cituro GmbH, siehe <a href="/datenschutz/#buchung">Datenschutzerklärung</a></small></div>
      <button class="booking-close" type="button" data-booking-close aria-label="Schließen">{CLOSE_ICON}</button>
    </div>
    <p class="booking-pick" aria-live="polite" hidden></p>
    <iframe title="Online-Terminbuchung TCM Tuina Massage" data-src="{BOOK_URL}"></iframe>
  </div>
</dialog>
<script src="/assets/main.js?v={VER}" defer></script>'''

def rel_links(html, path):
    depth = path.count("/")
    pre = "../" * depth
    def rel(m):
        attr, url = m.group(1), m.group(2)
        if url == "/":
            return f'{attr}="{pre or "./"}"'
        if url.startswith("/#"):
            return f'{attr}="{pre}{url[1:]}"' if depth else f'{attr}="{url[1:]}"'
        return f'{attr}="{pre}{url[1:]}"'
    return re.sub(r'\b(href|src|poster|data-src)="(/(?!/)[^"]*)"', rel, html)

NBSP = " "

def nbsp(html):
    """Geschützte Leerzeichen, damit Zahl und Einheit nicht auf zwei Zeilen landen."""
    html = re.sub(r"(\d) (Minuten|Meter|Uhr|Wochen|Wochenenden|Stunden|Jahre|€)", rf"\1{NBSP}\2", html)
    return re.sub(r"(?<!\w)(§|Art\.|Abs\.|Nr\.|lit\.) (\d|[a-z]\b)", rf"\1{NBSP}\2", html)

# Auf der Fehlerseite stimmen relative Pfade nicht, weil sie unter jeder Adresse erscheint.
# Ein kleines Skript setzt deshalb die Basisadresse: auf github.io der Projektordner, sonst die Wurzel.
BASE_SCRIPT = """<script>document.write('<base href="' + (location.hostname.endsWith('github.io') ? '/' + location.pathname.split('/')[1] + '/' : '/') + '">');</script>"""

def page(path, sec, current, title, desc, body, canonical, extra="", index=True, relative_body=False):
    robots = "" if index else '\n<meta name="robots" content="noindex, follow">'
    s = SECTIONS[sec]
    base = "\n" + BASE_SCRIPT if path == "404.html" else ""
    canon = f'\n<link rel="canonical" href="{canonical}">' if canonical else ""
    og_url = f'\n<meta property="og:url" content="{canonical}">' if canonical else ""
    top = f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">{base}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">{robots}{canon}
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}{IMG}odeonsplatz.jpg">
<meta property="og:type" content="website">{og_url}
<meta property="og:locale" content="de_DE">
<meta name="theme-color" content="#eef0f1">
<link rel="icon" href="{IMG}{s["logo"]}">
<link rel="preload" href="/assets/fonts/bricolage-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css?v={VER}">{extra}
</head>
<body>
{head(sec, current)}
<main id="inhalt">
'''
    bottom = f'''
</main>
{foot(sec, current)}
</body>
</html>
'''
    if relative_body:
        html = rel_links(top, path) + body + rel_links(bottom, path)
    else:
        html = rel_links(top + body + bottom, path)
    html = nbsp(html)
    f = OUT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding="utf-8")

def redirect(path, target, label):
    depth = path.count("/")
    url = "../" * depth + target.lstrip("/")
    f = OUT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{label}</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={url}">
</head>
<body><p><a href="{url}">Weiter zu: {label}</a></p></body>
</html>
''', encoding="utf-8")

def pic(file, alt, pos="50% 50%"):
    return f'<span class="inline-pic"><img src="{IMG}{file}" alt="{alt}" width="80" height="80" style="object-position:{pos}" loading="lazy" decoding="async"></span>'

DISCLAIMER = "Die Methoden der Traditionellen Chinesischen Medizin sind schulmedizinisch nicht anerkannt, ihre Wirkung ist wissenschaftlich nicht belegt. Sie ersetzen keine ärztliche Untersuchung oder Behandlung. Bei akuten oder ernsthaften Beschwerden wenden Sie sich bitte zuerst an Ihre Ärztin oder Ihren Arzt."

# ---------------------------------------------------------------- Tuina (bestehende Inhalte)
tuina_index = (SRC / "tuina_index.html").read_text(encoding="utf-8")
tuina_jsonld = "\n" + (SRC / "tuina_jsonld.html").read_text(encoding="utf-8")
page("index.html", "tuina", "tuina", "Tuina-Massage München am Odeonsplatz | TCM Zentrum München",
     "Chinesische Tuina-Massage bei Frau Li am Odeonsplatz, Ludwigstraße 11. 30 bis 90 Minuten ab 60 €, auch sonntags. Online oder telefonisch buchen.",
     tuina_index, f"{SITE}/", extra=tuina_jsonld, relative_body=True)

tuina_booking = (SRC / "tuina_booking.html").read_text(encoding="utf-8")
page("booking/index.html", "tuina", "booking", "Termin buchen | TCM Zentrum und Tuina-Massage am Odeonsplatz",
     "Termin für eine Tuina-Massage oder eine TCM-Therapie am Odeonsplatz in München: Tuina online, telefonisch oder per E-Mail, TCM-Therapie telefonisch.",
     tuina_booking, f"{SITE}/booking/", relative_body=True)

# ---------------------------------------------------------------- Zentrum: Startseite
ZENTRUM_LD = f'''
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "MedicalBusiness",
  "name": "TCM Zentrum München, Zentrum für Chinesische Medizin",
  "url": "{SITE}/zentrum/",
  "logo": "{SITE}{IMG}tcm-zentrum-logo.png",
  "image": "{SITE}{IMG}zhongwen-zhang.jpg",
  "telephone": "+49 89 28807280",
  "faxNumber": "+49 89 28807270",
  "email": "{TCM_MAIL}",
  "address": [
    {{ "@type": "PostalAddress", "streetAddress": "Ludwigstraße 11", "postalCode": "80539", "addressLocality": "München", "addressCountry": "DE" }},
    {{ "@type": "PostalAddress", "streetAddress": "Grafstraße 26", "postalCode": "82335", "addressLocality": "Berg", "addressCountry": "DE" }}
  ],
  "founder": {{ "@type": "Person", "name": "Zhongwen Zhang", "jobTitle": "Heilpraktiker" }}
}}
</script>'''

def svc(name, text, href=None, label=None):
    link = f' <a href="{href}">{label}</a>' if href else ""
    return f'<li class="svc"><h3>{name}</h3><p>{text}{link}</p></li>'

WAY_MUC = f'''<p><b>U-Bahn U3, U4, U5, U6</b>Haltestelle Odeonsplatz. Auf der linken Straßenseite Richtung Siegestor, je nach Ausgang 80 bis 180 Meter.</p>
          <p><b>Bus 100, Museumslinie</b>Haltestelle Von-der-Tann-Straße. In Richtung Odeonsplatz hält der Bus direkt am Eingang.</p>
          <p><b>Tram 19</b>Haltestelle Theatinerstraße, dann etwa 500 Meter zu Fuß über Theatinerstraße und Odeonsplatz Richtung Siegestor, linke Straßenseite.</p>'''

zentrum_body = f'''
  <section class="hero" aria-labelledby="titel">
    <div class="hero-text">
      <h1 id="titel">TCM Zentrum am Odeonsplatz</h1>
      <p>Akupunktur und chinesische Kräuter bei Zhongwen Zhang, Tuina-Massage bei Frau Li, in der Ludwigstraße 11 in München.</p>
      {cta("zentrum", "zentrum")}
    </div>
    <div class="orbs">
      <div class="orb orb-tui">{glyph("中", "g-tui")}</div>
      <div class="orb orb-na">{glyph("医", "g-na")}</div>
      <p class="orb-key"><span class="han" lang="zh">中医</span> zhōngyī heißt Chinesische Medizin.</p>
    </div>
  </section>

  <section class="statement" aria-label="Über das Zentrum">
    <p data-reveal><span>Seit 1990 praktiziert Zhongwen Zhang {pic("zhongwen-zhang.jpg", "Porträt von Zhongwen Zhang", "50% 30%")} Chinesische Medizin in Deutschland, mit Nadel {pic("akupunktur-bronzefigur.jpg", "Historische Akupunkturfigur", "50% 25%")}, Kräutern {pic("bencao-gangmu-1590.jpg", "Seite aus dem Bencao Gangmu von 1590", "50% 40%")} und Händen.</span></p>
  </section>

  <section class="panel" aria-labelledby="zhang">
    <h2 id="zhang">Zhongwen Zhang,<br>Heilpraktiker</h2>
    <div class="panel-text" data-reveal>
      <div>
        <h3>Ausbildung</h3>
        <ul class="points">
          <li>Studium der Traditionellen Chinesischen Medizin in Chengdu, VR China</li>
          <li>Promotion in Akupunktur und Tuina bei Prof. Luo Yungfen</li>
          <li>Heilpraktiker in Deutschland</li>
        </ul>
      </div>
      <div>
        <h3>Zwei Kulturen</h3>
        <p>Studiert hat Zhongwen Zhang in Chengdu, seit 1988 lebt er in Deutschland. Diese Erfahrung in beiden Kulturen prägt seine Arbeit: Er verbindet die medizinische und die philosophische Seite der TCM mit dem Alltag in Europa.</p>
        <p class="note">Privatleistung, Abrechnung nach der Gebührenordnung für Heilpraktiker (GebüH). Mehr zu Kosten und Erstattung auf der Seite <a href="/tcm/#start">TCM-Therapie</a>.</p>
      </div>
      <a class="btn btn-light" href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a>
    </div>
    <div class="chart portrait">
      <img src="{IMG}zhongwen-zhang.jpg" alt="Porträt von Zhongwen Zhang im weißen Hemd" width="1200" height="1025" loading="lazy" decoding="async">
    </div>
    <p class="chart-caption">Zhongwen Zhang leitet das TCM Zentrum München und das TCM Kolleg.</p>
  </section>

  <section class="services" aria-labelledby="leistungen">
    <h2 id="leistungen">Was wir anbieten</h2>
    <ul class="svc-list" data-reveal>
      {svc("Zungen- und Pulsdiagnose", "Der Ausgangspunkt jeder Behandlung in der TCM. Danach entsteht Ihr individueller Therapieplan.")}
      {svc("Akupunktur", "Feine Nadeln an ausgewählten Punkten der Meridiane. Die Akupunktur einer Körperseite dauert etwa 25 Minuten, eine Ganzkörperakupunktur von vorne und hinten etwa 55 Minuten.")}
      {svc("Chinesische Kräuter", "Eine Rezeptur aus 10 bis 20 Heilkräutern, als Tee zubereitet und im Verlauf der Therapie angepasst.")}
      {svc("Tuina-Massage", "Chinesische Massage bei Frau Li, 30 bis 90 Minuten, auch online buchbar.", "/", "Zur Tuina-Massage")}
      {svc("Moxibustion", "Erwärmung von Akupunkturpunkten mit getrocknetem Beifußkraut. In China gehören Nadel und Moxa als „Zhenjiu“ zusammen.")}
      {svc("Schröpfen", "Schröpfgläser mit Unterdruck auf der Haut, eine überlieferte Methode der TCM.")}
      {svc("Ernährungsberatung", "Empfehlungen zur Ernährung nach den Regeln der TCM, abgestimmt auf Ihre Diagnose.")}
      {svc("Qigong", "Ruhige Bewegungs- und Atemübungen in Einzelstunden, die Sie zu Hause allein weiterführen können.")}
    </ul>
    <p class="price-foot"><a href="/tcm/">Alle Behandlungsmethoden ausführlich</a></p>
  </section>

  <section class="steps" aria-labelledby="ablauf">
    <h2 id="ablauf">So beginnt Ihre Therapie</h2>
    <ol class="step-list" data-reveal>
      <li><h3>Diagnose</h3><p>Sie vereinbaren telefonisch einen ersten Termin. Zhongwen Zhang fragt nach Ihren Beschwerden, sieht sich Ihre Zunge an und tastet den Puls.</p></li>
      <li><h3>Therapieplan</h3><p>Danach erstellt Zhongwen Zhang Ihren individuellen Therapieplan.</p></li>
      <li><h3>Behandlung</h3><p>Intensive Behandlungen umfassen meist 12 Akupunkturtermine über 4 bis 6 Wochen, oft zusammen mit Heilkräutern. Den genauen Verlauf bestimmt Ihre Diagnose.</p></li>
      <li><h3>Ernährung</h3><p>Parallel dazu erhalten Sie eine Ernährungsberatung nach den Regeln der TCM.</p></li>
    </ol>
  </section>

  <figure class="band">
    <img src="{IMG}odeonsplatz.jpg" alt="Der Odeonsplatz in München mit Feldherrnhalle und Theatinerkirche an einem Sommertag" width="1800" height="880" loading="lazy" decoding="async">
  </figure>
  <p class="price-foot band-note">Der Odeonsplatz mit Feldherrnhalle und Theatinerkirche. Das Zentrum liegt ein paar Schritte weiter in der Ludwigstraße 11.</p>

  <section class="visit places" id="standorte" aria-labelledby="standorte-titel">
    <h2 id="standorte-titel">Zwei Standorte</h2>
    <div class="rows" data-reveal>
      <a href="{MAPS}" rel="noopener">Ludwigstraße 11, 80539 München</a>
      <a href="{MAPS_BERG}" rel="noopener">Grafstraße 26, 82335 Berg</a>
      <a href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a>
      <a href="mailto:{TCM_MAIL}">{TCM_MAIL}</a>
    </div>
    <div class="way">
      <div class="way-text" data-reveal>
        <h3>Am Odeonsplatz in München</h3>
        <figure class="clip">
          <video autoplay muted loop playsinline preload="metadata" poster="{IMG}ubahn-odeonsplatz.jpg" width="854" height="480" aria-label="Eine U-Bahn fährt in den Bahnhof Odeonsplatz ein">
            <source src="{IMG}ubahn-odeonsplatz.webm" type="video/webm">
          </video>
          <figcaption>Ankunft am U-Bahnhof Odeonsplatz</figcaption>
        </figure>
        {WAY_MUC}
        <p>Termine für die TCM-Therapie telefonisch unter <a href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a>.</p>
      </div>
      <div class="way-text berg" data-reveal>
        <h3>In Berg am Starnberger See</h3>
        <figure class="clip"><img src="{IMG}berg-starnberger-see.jpg" alt="Historische Postkarte: Dampfer vor Schloss Berg am Starnberger See" width="1800" height="1142" loading="lazy" decoding="async"><figcaption>Schloss Berg auf einer Postkarte um 1900</figcaption></figure>
        <p><b>S-Bahn S6 bis Starnberg</b>Von dort etwa 15 Minuten mit dem Taxi oder mit dem Bus X970 Richtung Bad Tölz bis Haltestelle Berg, Grafstraße.</p>
        <p><b>S-Bahn S6 bis Starnberg Nord</b>Weiter mit dem Bus 971 Richtung Münsing bis Haltestelle Berg, Grafstraße.</p>
        <p><b>S-Bahn S7 bis Wolfratshausen</b>Weiter mit dem Bus X970 Richtung Starnberg bis Haltestelle Berg, Grafstraße.</p>
        <p>Termine in Berg vereinbaren Sie ebenfalls unter <a href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a>. Tuina-Massagen gibt es nur am Odeonsplatz.</p>
      </div>
    </div>
  </section>

  <section class="download" aria-labelledby="anrufen">
    <div class="download-inner" data-reveal>
      <div class="dl-pic"><img src="{IMG}shennong-holzschnitt.jpg" alt="Holzschnitt von Shennong, dem legendären Begründer der Kräuterkunde" width="933" height="1400" loading="lazy" decoding="async"></div>
      <h2 id="anrufen">Erst einmal anrufen</h2>
      <p>Am Telefon besprechen wir Ihr Anliegen und vereinbaren den Termin zur Zungen- und Pulsdiagnose, in München oder in Berg.</p>
      <a class="btn btn-light" href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a>
    </div>
    <p class="disclaimer-line">{DISCLAIMER}</p>
  </section>
'''
page("zentrum/index.html", "zentrum", "zentrum", "TCM Zentrum München | Akupunktur am Odeonsplatz",
     "Akupunktur, chinesische Kräuter und Moxibustion bei Zhongwen Zhang, Heilpraktiker, am Odeonsplatz in München und in Berg. Tuina-Massage bei Frau Li.",
     zentrum_body, f"{SITE}/zentrum/", extra=ZENTRUM_LD)

# ---------------------------------------------------------------- TCM Therapie
def method(name, text, img=None, alt="", pos="50% 40%"):
    pic_html = f'<div class="m-pic"><img src="{IMG}{img}" alt="{alt}" width="933" height="1400" style="object-position:{pos}" loading="lazy" decoding="async"></div>' if img else '<div class="m-pic m-empty" aria-hidden="true"></div>'
    return f'<article class="method">{pic_html}<div><h3>{name}</h3><p>{text}</p></div></article>'

tcm_body = f'''
  <section class="page-top">
    <div class="orb-small" aria-hidden="true"></div><div class="orb-small" aria-hidden="true"></div>
    <h1>TCM-Therapie</h1>
    <p>Traditionelle Chinesische Medizin ist eine über drei Jahrtausende gewachsene Heilkunde. Als ganzheitliche Medizin will sie die Schulmedizin ergänzen, nicht ersetzen. Im TCM Zentrum München behandelt Heilpraktiker Zhongwen Zhang.</p>
  </section>

  <section class="methods" aria-labelledby="methoden">
    <h2 id="methoden">Behandlungsmethoden</h2>
    <div class="method-list" data-reveal>
      {method("Zungen- und Pulsdiagnose", "Die Grundlage aller weiteren Therapien. Zunge und Puls geben nach der Lehre der TCM Auskunft über den Zustand des ganzen Menschen und über die Ursachen von Beschwerden.", "pulsdiagnose-holzschnitt.jpg", "Holzschnitt von 1817: Tasten des Pulses am Handgelenk", "50% 30%")}
      {method("Akupunktur", "Die TCM kennt 361 Punkte auf 14 Hauptmeridianen. In jeder Sitzung werden individuell ausgewählte Punkte genadelt. Nach der Vorstellung der TCM soll das die körpereigene Regulierung anregen. Die Akupunktur einer Körperseite dauert etwa 25 Minuten, eine Ganzkörperakupunktur von vorne und hinten etwa 55 Minuten.", "akupunktur-bronzefigur.jpg", "Holzschnitt einer Bronzefigur mit Akupunkturpunkten", "50% 30%")}
      {method("Chinesische Heilkräuter", "Aus über 1.000 gebräuchlichen Heilkräutern stellt Zhongwen Zhang 10 bis 20 für Ihre Rezeptur zusammen und dosiert sie. Die Mischung trinken Sie etwa zwei Wochen lang täglich als Tee, dann passt er die Rezeptur neu an.", "bencao-gangmu-1590.jpg", "Seite aus dem Kräuterbuch Bencao Gangmu von 1590", "50% 45%")}
      {method("Moxibustion", "Getrocknetes Beifußkraut erwärmt ausgewählte Akupunkturpunkte. In China werden Nadel und Moxa unter dem Begriff „Zhenjiu“ zusammengefasst.", "moxibustion-holzschnitt.jpg", "Holzschnitt einer Moxibustion-Behandlung am Rücken", "50% 40%")}
      {method("Schröpfen", "Vakuumgläser werden auf die Haut gesetzt. Schröpfen gehört zu den ältesten überlieferten Methoden der chinesischen Medizin.", "schroepfglas-holzschnitt.jpg", "Holzschnitt eines chinesischen Schröpfgefäßes", "40% 45%")}
      {method("Tuina-Massage", "Tui und Na, Schieben und Greifen, sind die beiden Haupthandgriffe dieser Massage. Sie wird bei uns von Frau Li angeboten.", "tuina-tafel-handflaeche.jpg", "Historische Tuina-Tafel einer Handfläche", "50% 42%")}
      {method("Ernährungsberatung", "Nach der Zungen- und Pulsdiagnose empfehlen wir Nahrungsmittel, die zu Ihrem Körperzustand passen, und raten von ungünstigen ab.", "shennong-holzschnitt.jpg", "Holzschnitt von Shennong, dem legendären Begründer der Kräuterkunde", "50% 35%")}
      {method("Qigong", "Ruhige Bewegungs- und Atemübungen aus der chinesischen Tradition. In Einzelstunden lernen Sie Übungen, die Sie zu Hause allein weiterführen können.", "holzschnitt-selbstmassage.jpg", "Chinesischer Holzschnitt einer Übung mit beiden Händen", "50% 45%")}
    </div>
    <p class="price-foot"><a href="/">Zur Tuina-Massage bei Frau Li</a></p>
  </section>

  <section class="philo" aria-labelledby="philosophie">
    <figure class="philo-pic" data-reveal>
      <img src="{IMG}fuxi-ma-lin.jpg" alt="Gemälde von Ma Lin: der sitzende Fuxi, um 1230" width="647" height="1400" loading="lazy" decoding="async">
      <figcaption>Fuxi, nach der Überlieferung erster Kaiser und Philosoph Chinas. Gemälde von Ma Lin, um 1230.</figcaption>
    </figure>
    <div class="philo-text" data-reveal>
      <h2 id="philosophie">Sowohl als auch</h2>
      <p>Yin und Yang stehen in der TCM für zwei Kräfte, die sich ergänzen: „sowohl als auch“ statt „entweder oder“. Gemeint ist das Gleichgewicht der Kräfte in der Natur und in uns selbst. Der zweite Grundsatz lautet „Hilfe zur Selbsthilfe“: Die Behandlung setzt auf die eigenen Kräfte des Körpers.</p>
      <blockquote><p>„Wenn es eilt, behandelt man das Symptom, sonst behandelt man die Ursache.“</p><footer>Therapieprinzip der TCM</footer></blockquote>
      <p>Die Weltgesundheitsorganisation versteht Gesundheit als Zustand vollständigen körperlichen, geistigen und sozialen Wohlergehens, nicht nur als Fehlen von Krankheit. Ganz in diesem Sinn achtet die TCM auf das Befinden, nicht nur auf Befunde.</p>
      <div class="bagua"><img src="{IMG}bagua.jpg" alt="Yin-Yang-Zeichen umgeben von den acht Trigrammen" width="659" height="645" loading="lazy" decoding="async"></div>
      <p class="note-dark">Leibniz sah in den Zeichen des Fuxi den „Ursprung der Dinge aus der Einheit und aus dem Nichts“ und erkannte darin seine dyadische Arithmetik wieder.</p>
    </div>
  </section>

  <section class="download" aria-labelledby="start">
    <div class="download-inner" data-reveal>
      <h2 id="start">Termin zur Diagnose</h2>
      <p>Ihre Therapie beginnt mit einer Zungen- und Pulsdiagnose bei Zhongwen Zhang. Termine in München und in Berg vereinbaren Sie telefonisch.</p>
      <p>Die Behandlungen sind Privatleistungen und werden nach der Gebührenordnung für Heilpraktiker (GebüH) abgerechnet. Gesetzliche Krankenkassen übernehmen sie grundsätzlich nicht, private Kranken- und Zusatzversicherungen sowie die Beihilfe erstatten je nach Vertrag einen Teil. Bitte klären Sie das vor Beginn der Therapie mit Ihrer Versicherung. Bezahlt wird direkt nach jeder Behandlung, bar oder mit EC-Karte.</p>
      <a class="btn btn-light" href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a>
    </div>
    <p class="disclaimer-line">{DISCLAIMER}</p>
  </section>
'''
page("tcm/index.html", "zentrum", "tcm", "TCM-Therapie | TCM Zentrum München am Odeonsplatz",
     "Akupunktur, chinesische Heilkräuter, Moxibustion, Schröpfen, Tuina, Ernährungsberatung und Qigong im TCM Zentrum München am Odeonsplatz.",
     tcm_body, f"{SITE}/tcm/")

# ---------------------------------------------------------------- TCM Kolleg
def course(cls, name, price, lines, cta_href, cta):
    items = "".join(f"<li>{l}</li>" for l in lines)
    return f'''<div class="tile {cls}">
        <div class="tile-body">
          <span class="name">{name}</span>
          <span class="amount">{price}</span>
          <ul class="course-lines">{items}</ul>
        </div>
        <a class="tile-btn" href="{cta_href}">{cta}</a>
      </div>'''

kolleg_body = f'''
  <section class="page-top kolleg-top">
    <img class="kolleg-logo" src="{IMG}tcm-zentrum-logo.png" alt="" width="250" height="250">
    <h1>TCM Kolleg München</h1>
    <p class="han han-line" lang="zh">慕尼黑中医学院</p>
    <p>Akupunktur und Chinesische Medizin lernen bei Zhongwen Zhang: Philosophie, Diagnostik und Behandlungstechniken der TCM.</p>
    <a class="btn" href="#kurse">Kurse und Preise</a>
  </section>

  <section class="statement" aria-label="Über das Kolleg">
    <p data-reveal><span>Das Kolleg setzt auf praxisnahe Lehre {pic("akupunktur-bronzefigur.jpg", "Historische Akupunkturfigur", "50% 25%")}, vom Grundwissen bis zur Anwendung in der Praxis, gelehrt von Zhongwen Zhang {pic("zhongwen-zhang.jpg", "Porträt von Zhongwen Zhang", "50% 30%")}.</span></p>
  </section>

  <section class="panel" aria-labelledby="leitung">
    <h2 id="leitung">Schulleiter und<br>Dozent</h2>
    <div class="panel-text" data-reveal>
      <div>
        <h3>Zhongwen Zhang</h3>
        <ul class="points">
          <li>Studium der Traditionellen Chinesischen Medizin in Chengdu, VR China</li>
          <li>Heilpraktiker in Deutschland</li>
        </ul>
        <p style="margin-top:14px">Er lebt seit 1988 in Deutschland und praktiziert hier seit 1990 Chinesische Medizin. Aus über 35 Jahren Berufserfahrung und dem Studium der alten Klassiker hat er eigene Behandlungsmethoden entwickelt.</p>
      </div>
      <div>
        <h3>Warum er unterrichtet</h3>
        <p>Am Kolleg gibt Zhongwen Zhang sein Fachwissen und seine eigenen Methoden weiter. Sie lernen die TCM in Deutschland, aber aus erster Hand: bei jemandem, der sie in Chengdu studiert hat und seit 1990 hier praktiziert.</p>
      </div>
    </div>
    <div class="chart portrait">
      <img src="{IMG}zhongwen-zhang.jpg" alt="Porträt von Zhongwen Zhang im weißen Hemd" width="1200" height="1025" loading="lazy" decoding="async">
    </div>
  </section>

  <section class="philo" aria-labelledby="lehre">
    <figure class="philo-pic" data-reveal>
      <img src="{IMG}fuxi-ma-lin.jpg" alt="Gemälde von Ma Lin: der sitzende Fuxi, um 1230" width="647" height="1400" loading="lazy" decoding="async">
      <figcaption>Fuxi, dem die Trigramme von Yin und Yang zugeschrieben werden.</figcaption>
    </figure>
    <div class="philo-text" data-reveal>
      <h2 id="lehre">Was wir lehren</h2>
      <p>Im Spezialkurs lernen Sie die Chenwei-Akupunktur, in der zweijährigen Ausbildung die Grundlagen der TCM von der Diagnostik bis zur Kräuterheilkunde. Den theoretischen Rahmen bilden Yin und Yang. Zhongwen Zhang erklärt sie über Leibniz, der in den Zeichen des Fuxi sein Zahlensystem aus 0 und 1 wiedererkannte.</p>
      <h3>Eigene Lehrinhalte</h3>
      <ul class="points dark">
        <li><span>Chenwei-Akupunktur (<span class="han" lang="zh">谶纬针法</span>): Zu den klassischen senkrechten Meridianen kommen waagerechte Meridiane, die Zhongwen Zhang entwickelt hat</span></li>
        <li>Qi und Meridiane, erklärt über die Verbindung von Fuxi und Leibniz</li>
        <li>Von taoistischer Philosophie inspirierte Arbeit mit den Faszien</li>
      </ul>
      <div class="bagua"><img src="{IMG}bagua.jpg" alt="Yin-Yang-Zeichen umgeben von den acht Trigrammen" width="659" height="645" loading="lazy" decoding="async"></div>
    </div>
  </section>

  <section class="prices" id="kurse" aria-labelledby="kurse-titel">
    <div class="price-row courses" data-reveal>
      <div class="price-head">
        <h2 id="kurse-titel">Kursangebot</h2>
        <p>Für Ärztinnen und Ärzte, Heilpraktikerinnen und Heilpraktiker und ärztliches Assistenzpersonal. Nadeln setzen dürfen in Deutschland nur Ärzte und Heilpraktiker. In der Physiotherapie und zur Selbstbehandlung arbeiten Sie mit den Fingern.</p>
      </div>
      {course("t30", "Kennenlernvortrag", "kostenlos", ["Das Kolleg stellt sich vor: Philosophie, Lehrinhalte und Dozent", "Der Vortrag findet regelmäßig statt"], f"tel:{TCM_TEL}", "Termin erfragen")}
      {course("t60", "Spezialkurs Chenwei-Akupunktur", "299 € pro Wochenende", ["Klassische senkrechte und neue waagerechte Meridiane", "3 Wochenenden zu je 14 Stunden, im Abstand von 2 bis 3 Wochen", "Samstag 9:00 bis 12:30 und 13:30 bis 17:30 Uhr", "Sonntag 9:00 bis 13:00 und 13:30 bis 16:00 Uhr", "Alle drei Wochenenden 897 €, bei Einmalzahlung 747 €", "Vorkenntnisse sind nicht zwingend nötig"], f"mailto:{TCM_MAIL}?subject=Anmeldung%20Spezialkurs%20Chenwei-Akupunktur&amp;body=Name%3A%20%0D%0ATelefon%3A%20%0D%0ABeruf%3A%20%0D%0AGew%C3%BCnschter%20Kurstermin%3A%20", "Anmelden per E-Mail")}
      {course("t90", "Zweijährige Ausbildung", "Preis auf Anfrage", ["Im Anschluss an den Spezialkurs", "Kultureller Hintergrund der TCM", "Ausführliche Diagnostik", "Meridianlehre und Akupunkturpunkte", "Kräuterheilkunde und die wichtigsten Rezepturen"], f"mailto:{TCM_MAIL}?subject=Anfrage%20zweij%C3%A4hrige%20Ausbildung", "Per E-Mail anfragen")}
    </div>
    <p class="price-foot"><span>Preise pro Person. Die nächsten Kurstermine nennen wir Ihnen gern per E-Mail an <a href="mailto:{TCM_MAIL}">{TCM_MAIL}</a> oder unter <a href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a>.</span></p>
  </section>
'''
page("tcm-kolleg/index.html", "zentrum", "kolleg", "TCM Kolleg München | Akupunktur und TCM lernen",
     "TCM Kolleg München: Spezialkurs Chenwei-Akupunktur und zweijährige Ausbildung in Traditioneller Chinesischer Medizin bei Zhongwen Zhang am Odeonsplatz.",
     kolleg_body, f"{SITE}/tcm-kolleg/")

# ---------------------------------------------------------------- Rechtliches (gemeinsam)
def legal(title, inner):
    return f'''
  <section class="page-top">
    <div class="orb-small" aria-hidden="true"></div><div class="orb-small" aria-hidden="true"></div>
    <h1>{title}</h1>
  </section>
  <div class="legal"><div class="legal-body" data-reveal>
{inner}
  </div></div>
'''

credit_list = "\n".join(f'      <li><a href="{u}" rel="noopener">{t}</a>, {w}, {lic(l)}</li>' for t, w, l, u in CREDITS)

impressum = legal("Impressum", f'''
    <p>Dieses Impressum gilt für die Websites tcm-muenchen.com und tcm-tuina-massage.de.</p>
    <h2>Angaben gemäß § 5 DDG</h2>
    <address>TCM Zentrum München, Zentrum für Chinesische Medizin, und TCM Kolleg München<br>Inhaber: Zhongwen Zhang, Heilpraktiker<br>Ludwigstraße 11 (am Odeonsplatz)<br>80539 München<br>Deutschland</address>
    <h2>Kontakt</h2>
    <p>Telefon: <a href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a><br>Telefax: 089 28 80 72 70<br>E-Mail: <a href="mailto:{TCM_MAIL}">{TCM_MAIL}</a><br>Terminvereinbarung Tuina-Massage: <a href="tel:{TUINA_TEL}">{TUINA_TEL_TXT}</a>, <a href="mailto:{TUINA_MAIL}">{TUINA_MAIL}</a></p>
    <h2>Berufsbezeichnung und berufsrechtliche Regelungen</h2>
    <p>Berufsbezeichnung: Heilpraktiker (verliehen in der Bundesrepublik Deutschland)</p>
    <p>Es gelten das Heilpraktikergesetz und die Erste Durchführungsverordnung zum Heilpraktikergesetz, einsehbar unter <a href="https://www.gesetze-im-internet.de/heilprg/" rel="noopener">gesetze-im-internet.de/heilprg</a>.</p>
    <h2>Zuständige Aufsichtsbehörde</h2>
    <p>Gesundheitsamt München<br>Mariahilfplatz 17, 81541 München</p>
    <h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2>
    <p>Zhongwen Zhang, Anschrift wie oben</p>
    <h2>Verbraucherstreitbeilegung</h2>
    <p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
    <h2>Haftung für Inhalte</h2>
    <p>Als Diensteanbieter sind wir für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Wir sind jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Sobald uns eine konkrete Rechtsverletzung bekannt wird, entfernen wir die betreffenden Inhalte umgehend.</p>
    <h2>Haftung für Links</h2>
    <p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Für diese fremden Inhalte ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zu diesem Zeitpunkt nicht erkennbar. Werden uns Rechtsverletzungen bekannt, entfernen wir derartige Links umgehend.</p>
    <h2>Urheberrecht</h2>
    <p>Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechts bedürfen der schriftlichen Zustimmung des Rechteinhabers.</p>
    <h2 id="bildnachweise">Bildnachweise</h2>
    <p>Logos, das Porträt von Zhongwen Zhang und die Grafik mit Yin-Yang-Zeichen und Trigrammen: TCM Zentrum München. Alle weiteren Bilder:</p>
    <ul>
{credit_list}
    </ul>
    <p>Schriften: Bricolage Grotesque und Noto Serif SC, beide unter der SIL Open Font License 1.1.</p>''')
page("impressum/index.html", "zentrum", "impressum", "Impressum | TCM Zentrum München",
     "Impressum von TCM Zentrum München und TCM Tuina Massage am Odeonsplatz.",
     impressum, f"{SITE}/impressum/", index=False)

datenschutz = legal("Datenschutz", f'''
    <p>Diese Datenschutzerklärung gilt für die Websites tcm-muenchen.com und tcm-tuina-massage.de. Wir informieren Sie darüber, welche personenbezogenen Daten wir beim Besuch der Websites und bei der Terminvereinbarung verarbeiten, zu welchem Zweck und auf welcher Rechtsgrundlage.</p>
    <h2>1. Verantwortlicher</h2>
    <address>TCM Zentrum München, Zentrum für Chinesische Medizin<br>Inhaber: Zhongwen Zhang, Heilpraktiker<br>Ludwigstraße 11, 80539 München<br>Telefon: <a href="tel:{TCM_TEL}">{TCM_TEL_TXT}</a><br>E-Mail: <a href="mailto:{TCM_MAIL}">{TCM_MAIL}</a></address>
    <h2>2. Das Wichtigste in Kürze</h2>
    <ul>
      <li>Die Websites setzen keine Cookies und verwenden keine Analyse- oder Werbedienste.</li>
      <li>Schriften, Bilder, Videos und Skripte werden zusammen mit der Website ausgeliefert. Es werden keine Inhalte von Drittanbietern wie Google Fonts nachgeladen.</li>
      <li>Das Online-Buchungssystem der cituro GmbH für Tuina-Massagen wird erst geladen, wenn Sie selbst die Online-Buchung öffnen, zum Beispiel über „Termin buchen“ oder „Online buchen“.</li>
    </ul>
    <h2>3. Aufruf der Websites und Server-Logdateien</h2>
    <p>Die Websites werden über GitHub Pages bereitgestellt, einen Dienst der GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA. Beim Aufruf übermittelt Ihr Browser automatisch Daten an die Server von GitHub, insbesondere IP-Adresse, Datum und Uhrzeit des Zugriffs, aufgerufene Seite, Referrer-URL sowie Browsertyp und Betriebssystem. GitHub speichert diese Daten in Server-Logdateien, um die Websites auszuliefern und vor Missbrauch zu schützen.</p>
    <p>Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Unser berechtigtes Interesse liegt in einer sicheren und zuverlässigen Bereitstellung der Websites. Dabei können Daten in die USA übermittelt werden. Die Übermittlung stützt sich auf den Angemessenheitsbeschluss der EU-Kommission zum EU-US Data Privacy Framework (Art. 45 DSGVO), nach dem GitHub, Inc. zertifiziert ist. Wie lange GitHub die Logdaten speichert, legt GitHub selbst fest. Einzelheiten stehen in der <a href="https://docs.github.com/de/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener">Datenschutzerklärung von GitHub</a>.</p>
    <h2>4. Kontakt per Telefon oder E-Mail</h2>
    <p>Wenn Sie uns anrufen oder eine E-Mail schreiben, verarbeiten wir Ihre Angaben (zum Beispiel Name, Telefonnummer, E-Mail-Adresse und Inhalt der Anfrage), um Ihre Anfrage zu beantworten, einen Termin zu vereinbaren oder Ihre Anmeldung zu einem Kurs zu bearbeiten. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO.</p>
    <p>Teilen Sie uns dabei von sich aus Angaben zu Ihrer Gesundheit mit, verarbeiten wir diese mit Ihrer ausdrücklichen Einwilligung nur zur Vorbereitung Ihres Termins (Art. 9 Abs. 2 lit. a DSGVO). Sie können die Einwilligung jederzeit für die Zukunft widerrufen.</p>
    <p>Wir löschen Ihre Angaben, sobald sie für diese Zwecke nicht mehr erforderlich sind und keine gesetzlichen Aufbewahrungspflichten entgegenstehen.</p>
    <h2 id="buchung">5. Online-Terminbuchung über cituro</h2>
    <p>Für die Online-Terminbuchung von Tuina-Massagen nutzen wir das Buchungssystem der cituro GmbH, Peter-Dörfler-Straße 30, 86199 Augsburg, Deutschland. Das Buchungssystem wird in einem Fenster der Website eingebunden, aber erst geladen, wenn Sie selbst die Online-Buchung öffnen, zum Beispiel über „Termin buchen“, „Online buchen“ oder einen der Preisknöpfe. Vorher werden keine Daten an cituro übertragen.</p>
    <p>Mit dem Laden des Buchungssystems wird Ihre IP-Adresse an cituro übermittelt. Bei einer Buchung verarbeitet cituro außerdem die Daten, die Sie dort eingeben, etwa Name, Kontaktdaten, gewünschte Leistung und Termin. cituro kann dabei technisch notwendige Cookies oder ähnliche Technologien einsetzen, die für die von Ihnen gewünschte Buchung erforderlich sind (§ 25 Abs. 2 Nr. 2 TDDDG).</p>
    <p>Die Verarbeitung dient der Vereinbarung Ihres Termins. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO. cituro verarbeitet die Daten als Auftragsverarbeiter in unserem Auftrag (Art. 28 DSGVO). Weitere Informationen finden Sie in der <a href="https://www.cituro.com/datenschutz" rel="noopener">Datenschutzerklärung von cituro</a>.</p>
    <p>Wenn Sie das Online-Buchungssystem nicht nutzen möchten, können Sie Ihren Termin jederzeit telefonisch oder per E-Mail vereinbaren.</p>
    <h2>6. Links zu anderen Websites</h2>
    <p>Die Websites enthalten Links, zum Beispiel zu Google Maps und zu Wikimedia Commons. Erst wenn Sie einen solchen Link anklicken, werden Daten an den jeweiligen Anbieter übertragen. Für die dortige Verarbeitung ist der jeweilige Anbieter verantwortlich.</p>
    <h2>7. Ihre Rechte</h2>
    <p>Sie haben gegenüber uns folgende Rechte hinsichtlich Ihrer personenbezogenen Daten:</p>
    <ul>
      <li>Auskunft (Art. 15 DSGVO)</li>
      <li>Berichtigung (Art. 16 DSGVO)</li>
      <li>Löschung (Art. 17 DSGVO)</li>
      <li>Einschränkung der Verarbeitung (Art. 18 DSGVO)</li>
      <li>Datenübertragbarkeit (Art. 20 DSGVO)</li>
      <li>Widerruf einer Einwilligung mit Wirkung für die Zukunft (Art. 7 Abs. 3 DSGVO)</li>
    </ul>
    <p>Wenden Sie sich dazu einfach an die oben genannten Kontaktdaten.</p>
    <h2>8. Widerspruchsrecht</h2>
    <p>Soweit wir Daten auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO verarbeiten, können Sie aus Gründen, die sich aus Ihrer besonderen Situation ergeben, jederzeit widersprechen (Art. 21 DSGVO).</p>
    <p>Sie haben außerdem das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren. Zuständig für uns ist das Bayerische Landesamt für Datenschutzaufsicht (BayLDA), Promenade 18, 91522 Ansbach, <a href="https://www.lda.bayern.de" rel="noopener">www.lda.bayern.de</a>.</p>
    <h2>9. Pflicht zur Bereitstellung</h2>
    <p>Sie sind nicht verpflichtet, uns personenbezogene Daten bereitzustellen. Ohne Kontakt- und Termindaten können wir jedoch keinen Termin mit Ihnen vereinbaren.</p>
    <p>Stand: Oktober 2026</p>''')
page("datenschutz/index.html", "zentrum", "datenschutz", "Datenschutz | TCM Zentrum München",
     "Datenschutzerklärung von TCM Zentrum München und TCM Tuina Massage.",
     datenschutz, f"{SITE}/datenschutz/", index=False)

# ---------------------------------------------------------------- alte Adressen von tcm-muenchen.com
redirect("impressum-und-datenschutz/index.html", "/impressum/", "Impressum und Datenschutz")
redirect("tuina-massage/index.html", "/", "Tuina-Massage")

# Fehlerseite für unbekannte Adressen, etwa alte Links der früheren Websites
page("404.html", "zentrum", "404", "Seite nicht gefunden | TCM Zentrum München",
     "Diese Seite gibt es nicht mehr.", f'''
  <section class="page-top">
    <div class="orb-small" aria-hidden="true"></div><div class="orb-small" aria-hidden="true"></div>
    <h1>Seite nicht gefunden</h1>
    <p>Diese Adresse gibt es nicht mehr, vielleicht stammt sie noch von unserer früheren Website. Hier geht es weiter:</p>
  </section>
  <div class="legal"><div class="legal-body">
    <ul class="points dark">
      <li><a href="/zentrum/">TCM Zentrum München</a></li>
      <li><a href="/tcm/">TCM-Therapie</a></li>
      <li><a href="/">Tuina-Massage bei Frau Li</a></li>
      <li><a href="/tcm-kolleg/">TCM Kolleg München</a></li>
      <li><a href="/booking/">Termin buchen</a></li>
    </ul>
  </div></div>
''', None, index=False)

(OUT / "sitemap.xml").write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{SITE}/</loc><lastmod>2026-10-21</lastmod></url>
  <url><loc>{SITE}/booking/</loc><lastmod>2026-10-21</lastmod></url>
  <url><loc>{SITE}/zentrum/</loc><lastmod>2026-10-21</lastmod></url>
  <url><loc>{SITE}/tcm/</loc><lastmod>2026-10-21</lastmod></url>
  <url><loc>{SITE}/tcm-kolleg/</loc><lastmod>2026-10-21</lastmod></url>
</urlset>
''', encoding="utf-8")
print("ok")

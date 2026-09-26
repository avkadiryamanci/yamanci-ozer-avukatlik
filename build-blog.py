"""Generate the static blog, preserving the existing site's header and footer."""
from pathlib import Path
from datetime import date
import json, html, re, shutil

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
SITE_URL = 'https://yamanciozerhukuk.com'
SOCIAL_IMAGE = SITE_URL + '/assets/amblem-lacivert.jpeg'
ANALYTICS_SNIPPET = '<!-- Cloudflare Web Analytics --><script type="module" src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token":"2c5a28515a254cbbb4a0c2259c450d6d"}\'></script><!-- End Cloudflare Web Analytics -->'
DIST.mkdir(exist_ok=True)
(DIST / 'blog').mkdir(exist_ok=True)
shutil.copytree(ROOT / 'assets' / 'assets', DIST / 'assets', dirs_exist_ok=True)
for asset in ('style.css', 'blog.css', 'navigation.js', 'contact-form.js'):
    shutil.copy2(ROOT / asset, DIST / asset)

articles = json.loads((ROOT / 'articles.json').read_text(encoding='utf-8'))
sources = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
esc = html.escape
home = (DIST / 'index.html').read_text(encoding='utf-8')
home = home.replace(
    '<span class="initials" aria-hidden="true">MG</span>',
    '<img class="team-photo" src="/assets/gorkem-mehmet-gunes.png" alt="Av. Görkem Mehmet Güneş" width="85" height="100" loading="lazy">',
)
team_photos = {
    'KY': ('kadir-yamanci.jpeg', 'Av. Arb. Kadir Yamancı'),
    'FÖ': ('ferdi-ozer.jpeg', 'Av. Arb. Ferdi Özer'),
    'HÖ': ('hasan-ozer.jpeg', 'Stj. Av. Hasan Özer'),
    'BÇ': ('bensu-coban.jpeg', 'Av. Bensu Çoban'),
    'MS': ('meryem-sevimli.jpeg', 'Av. Meryem Sevimli'),
    'SK': ('songul-karakaya.jpeg', 'Songül Karakaya'),
}
for initials, (filename, person_name) in team_photos.items():
    home = home.replace(
        f'<span class="initials" aria-hidden="true">{initials}</span>',
        f'<img class="team-photo" src="/assets/{filename}" alt="{person_name}" width="85" height="100" loading="lazy">',
    )
home = re.sub(r'<script type="application/ld\+json">.*?</script>', '', home, flags=re.S)
if '<a href="/blog/">Blog</a>' not in home:
    home = home.replace('<a href="#iletisim">İletişim</a>', '<a href="/blog/">Blog</a><a href="#iletisim">İletişim</a>')
head = home.split('</head>')[0] + '</head>'
head = head.replace('href="style.css"', 'href="/style.css"')
head = re.sub(r'<link rel="stylesheet" href="/blog\.css">', '', head)
head = head.replace('</head>', '<link rel="stylesheet" href="/blog.css"></head>')
header = re.search(r'<header>.*?</header>', home, re.S).group()
footer = re.search(r'<footer>.*?</footer>', home, re.S).group()
script = re.search(r'<script>.*?</script>', home, re.S).group()
def absolutize(part):
    part = part.replace('src="assets/', 'src="/assets/')
    return re.sub(r'href="#([^\"]*)"', lambda m: 'href="/' + ('#' + m[1] if m[1] else '') + '"', part)
header, footer = absolutize(header), absolutize(footer)
header = header.replace('<a href="/blog/">Blog</a>', '<a href="/blog/" aria-current="page">Blog</a>')
def seo_tags(title, description, path, page_type='website'):
    canonical = SITE_URL + path
    return (
        '<link rel="canonical" href="'+esc(canonical, quote=True)+'">'
        '<meta name="robots" content="index,follow,max-image-preview:large">'
        '<meta property="og:locale" content="tr_TR">'
        '<meta property="og:type" content="'+page_type+'">'
        '<meta property="og:site_name" content="Yamancı | Özer Avukatlık & Arabuluculuk">'
        '<meta property="og:title" content="'+esc(title, quote=True)+'">'
        '<meta property="og:description" content="'+esc(description, quote=True)+'">'
        '<meta property="og:url" content="'+esc(canonical, quote=True)+'">'
        '<meta property="og:image" content="'+SOCIAL_IMAGE+'">'
        '<meta name="twitter:card" content="summary_large_image">'
        '<meta name="twitter:title" content="'+esc(title, quote=True)+'">'
        '<meta name="twitter:description" content="'+esc(description, quote=True)+'">'
        '<meta name="twitter:image" content="'+SOCIAL_IMAGE+'">'
    )

def page(title, description, body, path, schema=None, page_type='website'):
    h = re.sub(r'<title>.*?</title>', '<title>' + esc(title) + ' | Yamancı Özer</title>', head)
    h = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="'+esc(description, quote=True)+'">', h)
    h = re.sub(r'<link rel="canonical"[^>]*>|<meta name="robots"[^>]*>|<meta property="og:[^"]+"[^>]*>|<meta name="twitter:[^"]+"[^>]*>', '', h)
    h = h.replace('</head>', seo_tags(title + ' | Yamancı Özer', description, path, page_type)+'</head>')
    if schema:
        h = h.replace('</head>', '<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
    return h+'<body class="blog-page"><a class="skip" href="#icerik">İçeriğe geç</a>'+header+'<main id="icerik">'+body+'</main>'+footer+script+ANALYTICS_SNIPPET+'</body></html>'
def card(a, compact=False):
    return '<article class="blog-card"><p class="category">'+esc(a['category'])+'</p><h3><a href="/blog/'+a['slug']+'/">'+esc(a['title'])+'</a></h3><p class="card-summary">'+esc(a['summary'])+'</p><div class="card-bottom"><p>'+esc(a['author'])+'</p><span aria-hidden="true">↗</span></div></article>'
def tr_date(iso_date):
    months = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
    year, month, day = map(int, iso_date.split('-'))
    return f'{day} {months[month-1]} {year}'

author_count = len({a['author'] for a in articles})
intro = '<section class="blog-intro"><a class="back-link" href="/">Ana sayfa</a><p class="eyebrow">BLOG / HUKUKİ YAZILAR</p><h1>Hukuki bilgi.<br><em>Açık bir perspektif.</em></h1><p>Çalışma alanlarımızdan değerlendirmeler ve kentsel dönüşüm sürecine ilişkin yazılar.</p><div class="blog-stats"><span>'+str(len(articles))+' hukuki yazı</span><span>'+str(author_count)+' yazar</span><span>Güncel hukuki kaynaklar</span></div></section>'
guide = '<section class="blog-section guide-section" aria-labelledby="guide-title"><div class="blog-section-head"><div><p class="eyebrow">ÖZEL DOSYA</p><h2 id="guide-title">Kentsel dönüşüm rehberi</h2></div><p>Av. Arb. Kadir Yamancı<br>Malikler için altı temel konu</p></div><div class="blog-grid">'+''.join(card(a) for a in articles if a.get('guide'))+'</div></section>'
others = '<section class="blog-section" aria-labelledby="other-title"><div class="blog-section-head"><div><p class="eyebrow">ÇALIŞMA ALANLARIMIZDAN</p><h2 id="other-title">Hukuki değerlendirmeler</h2></div><p>Avukatlarımızın ve stajyer avukatımızın yazıları</p></div><div class="blog-grid">'+''.join(card(a) for a in articles if not a.get('guide'))+'</div></section>'
blog_schema = {'@context':'https://schema.org','@type':'Blog','name':'Yamancı Özer Hukuk Blogu','url':SITE_URL+'/blog/','inLanguage':'tr-TR','publisher':{'@type':'LegalService','name':'Yamancı | Özer Avukatlık & Arabuluculuk','url':SITE_URL}}
(DIST/'blog/index.html').write_text(page('Blog — Hukuki Yazılar', 'Yamancı Özer ekibinden '+str(len(articles))+' hukuki yazı: kentsel dönüşüm, gayrimenkul, ticaret, sözleşmeler, kira, aile, miras ve icra hukuku.', intro+guide+others, '/blog/', blog_schema), encoding='utf-8')
for a in articles:
    path = DIST/'blog'/a['slug']; path.mkdir(parents=True, exist_ok=True)
    published = a.get('datePublished', '2026-09-24')
    body = '<div class="article-wrap"><nav class="breadcrumbs" aria-label="İçerik yolu"><a href="/">Ana sayfa</a><span aria-hidden="true">/</span><a href="/blog/">Blog</a><span aria-hidden="true">/</span><span>'+esc(a['category'])+'</span></nav><div class="article-heading"><p class="category">'+esc(a['category'])+'</p><h1>'+esc(a['title'])+'</h1><p class="article-summary">'+esc(a['summary'])+'</p><div class="article-meta"><span>'+esc(a['author'])+'</span><time datetime="'+published+'">'+tr_date(published)+'</time><span>Okuma süresi: yaklaşık 5 dakika</span></div></div><div class="article-layout"><aside class="article-toc" aria-label="Bu yazıda"><p>BU YAZIDA</p><ol>'+''.join('<li><a href="#bolum-'+str(i)+'">'+esc(s[0])+'</a></li>' for i,s in enumerate(a['sections'],1))+'</ol></aside><article class="article-body">'
    body += ''.join('<section id="bolum-'+str(i)+'"><h2>'+esc(s[0])+'</h2><p>'+esc(s[1])+'</p></section>' for i,s in enumerate(a['sections'],1))
    if a.get('faq'):
        body += '<section class="article-faq" aria-labelledby="faq-title"><h2 id="faq-title">Sık sorulan sorular</h2>'+''.join('<details><summary>'+esc(q)+'</summary><p>'+esc(answer)+'</p></details>' for q,answer in a['faq'])+'</section>'
    body += '<aside class="author-box"><p class="eyebrow">YAZAR</p><h2>'+esc(a['author'])+'</h2><p>Yamancı | Özer Avukatlık & Arabuluculuk ekibinin hukuki değerlendirmesidir. İçerik, genel bilgilendirme amacıyla ve yayımlanma tarihindeki mevzuat esas alınarak hazırlanmıştır.</p><a href="/#ekip">Ekibimizi inceleyin →</a></aside>'
    body += '<div class="article-sources"><h2>Kaynaklar ve hukuki dayanak</h2>'
    if a.get('guide'):
        body += '<p>Bu yazı, Av. Arb. Kadir Yamancı’nın “Kentsel Dönüşüm Süreci ve Malikler İçin Tam Kapsamlı Bilgilendirme Metni” başlıklı rehberindeki konular esas alınarak hazırlanmıştır.</p>'
    body += '<ul>'+''.join('<li><a href="'+esc(sources[k]['url'], quote=True)+'" target="_blank" rel="noopener noreferrer">'+esc(sources[k]['label'])+' ↗</a></li>' for k in a['sources'])+'</ul><p class="legal-note">Bu yazı genel bilgilendirme amaçlıdır. Somut uyuşmazlığın belgeleri, işlem tarihi ve uygulanacak güncel mevzuat birlikte değerlendirilmelidir.</p></div></article></div>'
    related = [b for b in articles if b['category']==a['category'] and b['slug']!=a['slug']][:2]
    if len(related) < 2:
        related += [b for b in articles if b['author']==a['author'] and b['slug']!=a['slug'] and b not in related][:(2-len(related))]
    body += '<section class="article-related"><h2>İlgili hukuki yazılar</h2><div class="blog-grid">'+''.join(card(b) for b in related)+'</div></section></div>'
    article_url = SITE_URL+'/blog/'+a['slug']+'/'
    article_schema = {'@type':'BlogPosting','headline':a['title'],'description':a['summary'],'url':article_url,'mainEntityOfPage':article_url,'image':SOCIAL_IMAGE,'author':{'@type':'Person','name':a['author'],'url':SITE_URL+'/#ekip'},'publisher':{'@type':'LegalService','name':'Yamancı | Özer Avukatlık & Arabuluculuk','url':SITE_URL,'logo':{'@type':'ImageObject','url':SOCIAL_IMAGE}},'datePublished':published,'dateModified':'2026-09-25','inLanguage':'tr-TR','articleSection':a['category']}
    breadcrumb_schema = {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Ana sayfa','item':SITE_URL+'/'},{'@type':'ListItem','position':2,'name':'Blog','item':SITE_URL+'/blog/'},{'@type':'ListItem','position':3,'name':a['title'],'item':article_url}]}
    graph = [article_schema, breadcrumb_schema]
    if a.get('faq'):
        graph.append({'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':answer}} for q,answer in a['faq']]})
    schema = {'@context':'https://schema.org','@graph':graph}
    (path/'index.html').write_text(page(a['title'], a['summary'], body, '/blog/'+a['slug']+'/', schema, 'article'), encoding='utf-8')
teaser_articles = [articles[0], articles[-3], articles[-1]]
teaser = '<section id="blog" class="section home-blog"><div class="section-head"><div><p class="eyebrow">05 / BLOG</p><h2>Hukuki yazılar.</h2></div><a class="blog-all" href="/blog/">Tüm yazıları inceleyin <span aria-hidden="true">↗</span></a></div><div class="blog-grid">'+''.join(card(a) for a in teaser_articles)+'</div></section>'
if '<section id="blog"' in home:
    home = re.sub(r'<section id="blog".*?</section>', teaser, home, flags=re.S)
else:
    home = home.replace('<section id="iletisim"', teaser+'\n<section id="iletisim"')
home = home.replace('05 / İLETİŞİM', '06 / İLETİŞİM')
if 'href="/blog.css"' not in home:
    home = home.replace('</head>', '<link rel="stylesheet" href="/blog.css">\n</head>')
home_description = 'Yamancı | Özer Avukatlık & Arabuluculuk; İstanbul Başakşehir’de avukatlık, hukuki danışmanlık, dava ve icra takibi ile arabuluculuk hizmetleri sunar.'
home = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="'+esc(home_description, quote=True)+'">', home)
home = re.sub(r'<link rel="canonical"[^>]*>|<meta name="robots"[^>]*>|<meta property="og:[^"]+"[^>]*>|<meta name="twitter:[^"]+"[^>]*>', '', home)
home_schema = {'@context':'https://schema.org','@type':'LegalService','name':'Yamancı | Özer Avukatlık & Arabuluculuk','url':SITE_URL,'image':SOCIAL_IMAGE,'email':'info@yamanciozerhukuk.com','telephone':'+90 212 813 27 96','address':{'@type':'PostalAddress','streetAddress':'İkitelli OSB Mahallesi, Süleyman Demirel Bulvarı, İstmall AVM, Kat: 2, Daire: 199','addressLocality':'Başakşehir','addressRegion':'İstanbul','addressCountry':'TR'},'areaServed':'TR','knowsLanguage':'tr'}
home = home.replace('</head>', seo_tags('Yamancı | Özer — Avukatlık & Arabuluculuk', home_description, '/')+'<script type="application/ld+json">'+json.dumps(home_schema, ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
home = re.sub(r'<!-- Cloudflare Web Analytics -->.*?<!-- End Cloudflare Web Analytics -->', '', home, flags=re.S)
home = home.replace('</body>', ANALYTICS_SNIPPET+'</body>')
(DIST/'index.html').write_text(home, encoding='utf-8')

today = date.today().isoformat()
urls = [SITE_URL+'/', SITE_URL+'/blog/'] + [SITE_URL+'/blog/'+a['slug']+'/' for a in articles]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('  <url><loc>'+esc(url)+'</loc><lastmod>'+today+'</lastmod></url>\n' for url in urls) + '</urlset>\n'
(DIST/'sitemap.xml').write_text(sitemap, encoding='utf-8')
(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+SITE_URL+'/sitemap.xml\n', encoding='utf-8')
print(f'Generated {len(articles)} articles and blog index; updated home navigation and blog section.')

"""Generate the static blog, preserving the existing site's header and footer."""
from pathlib import Path
from datetime import date
import json, html, re, shutil

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
SITE_URL = 'https://yamanciozerhukuk.com'
SOCIAL_IMAGE = SITE_URL + '/assets/amblem-lacivert.jpeg'
DIST.mkdir(exist_ok=True)
(DIST / 'blog').mkdir(exist_ok=True)
shutil.copytree(ROOT / 'assets' / 'assets', DIST / 'assets', dirs_exist_ok=True)
for asset in ('style.css', 'blog.css', 'navigation.js'):
    shutil.copy2(ROOT / asset, DIST / asset)

articles = json.loads((ROOT / 'articles.json').read_text(encoding='utf-8'))
sources = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
esc = html.escape
home = (DIST / 'index.html').read_text(encoding='utf-8')
if '<a href="/blog/">Blog</a>' not in home:
    home = home.replace('<a href="#iletisim">İletişim</a>', '<a href="/blog/">Blog</a><a href="#iletisim">İletişim</a>')
head = home.split('</head>')[0] + '</head>'
head = head.replace('href="style.css"', 'href="/style.css"')
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
    return h+'<body class="blog-page"><a class="skip" href="#icerik">İçeriğe geç</a>'+header+'<main id="icerik">'+body+'</main>'+footer+script+'</body></html>'
def card(a, compact=False):
    return '<article class="blog-card"><p class="category">'+esc(a['category'])+'</p><h3><a href="/blog/'+a['slug']+'/">'+esc(a['title'])+'</a></h3><p class="card-summary">'+esc(a['summary'])+'</p><div class="card-bottom"><p>'+esc(a['author'])+'</p><span aria-hidden="true">↗</span></div></article>'
intro = '<section class="blog-intro"><a class="back-link" href="/">Ana sayfa</a><p class="eyebrow">BLOG / HUKUKİ YAZILAR</p><h1>Hukuki bilgi.<br><em>Açık bir perspektif.</em></h1><p>Çalışma alanlarımızdan değerlendirmeler ve kentsel dönüşüm sürecine ilişkin yazılar.</p><div class="blog-stats"><span>18 hukuki yazı</span><span>6 yazar</span><span>Eylül 2026</span></div></section>'
guide = '<section class="blog-section guide-section" aria-labelledby="guide-title"><div class="blog-section-head"><div><p class="eyebrow">ÖZEL DOSYA</p><h2 id="guide-title">Kentsel dönüşüm rehberi</h2></div><p>Av. Arb. Kadir Yamancı<br>Malikler için altı temel konu</p></div><div class="blog-grid">'+''.join(card(a) for a in articles if a.get('guide'))+'</div></section>'
others = '<section class="blog-section" aria-labelledby="other-title"><div class="blog-section-head"><div><p class="eyebrow">ÇALIŞMA ALANLARIMIZDAN</p><h2 id="other-title">Hukuki değerlendirmeler</h2></div><p>Avukatlarımızın ve stajyer avukatımızın yazıları</p></div><div class="blog-grid">'+''.join(card(a) for a in articles if not a.get('guide'))+'</div></section>'
blog_schema = {'@context':'https://schema.org','@type':'Blog','name':'Yamancı Özer Hukuk Blogu','url':SITE_URL+'/blog/','inLanguage':'tr-TR','publisher':{'@type':'LegalService','name':'Yamancı | Özer Avukatlık & Arabuluculuk','url':SITE_URL}}
(DIST/'blog/index.html').write_text(page('Blog — Hukuki Yazılar', 'Yamancı Özer ekibinden 18 hukuki yazı: kentsel dönüşüm, gayrimenkul, ticaret, sözleşmeler, kira, aile, miras ve icra hukuku.', intro+guide+others, '/blog/', blog_schema), encoding='utf-8')
for a in articles:
    path = DIST/'blog'/a['slug']; path.mkdir(parents=True, exist_ok=True)
    body = '<div class="article-wrap"><div class="article-heading"><a class="back-link" href="/blog/">← Tüm yazılar</a><p class="category">'+esc(a['category'])+'</p><h1>'+esc(a['title'])+'</h1><p class="article-summary">'+esc(a['summary'])+'</p><div class="article-meta"><span>'+esc(a['author'])+'</span><time datetime="2026-09-24">24 Eylül 2026</time></div></div><div class="article-layout"><aside class="article-toc" aria-label="Bu yazıda"><p>BU YAZIDA</p><ol>'+''.join('<li><a href="#bolum-'+str(i)+'">'+esc(s[0])+'</a></li>' for i,s in enumerate(a['sections'],1))+'</ol></aside><article class="article-body">'
    body += ''.join('<section id="bolum-'+str(i)+'"><h2>'+esc(s[0])+'</h2><p>'+esc(s[1])+'</p></section>' for i,s in enumerate(a['sections'],1))
    body += '<div class="article-sources"><h2>Kaynaklar ve hukuki dayanak</h2>'
    if a.get('guide'):
        body += '<p>Bu yazı, Av. Arb. Kadir Yamancı’nın “Kentsel Dönüşüm Süreci ve Malikler İçin Tam Kapsamlı Bilgilendirme Metni” başlıklı rehberindeki konular esas alınarak hazırlanmıştır.</p>'
    body += '<ul>'+''.join('<li><a href="'+esc(sources[k]['url'], quote=True)+'" target="_blank" rel="noopener noreferrer">'+esc(sources[k]['label'])+' ↗</a></li>' for k in a['sources'])+'</ul><p class="legal-note">Bu yazı genel bilgilendirme amaçlıdır. Somut uyuşmazlığın belgeleri, işlem tarihi ve uygulanacak güncel mevzuat birlikte değerlendirilmelidir.</p></div></article></div>'
    related = [b for b in articles if b['author']==a['author'] and b['slug']!=a['slug']][:2]
    body += '<section class="article-related"><h2>Yazarın diğer yazıları</h2><div class="blog-grid">'+''.join(card(b) for b in related)+'</div></section></div>'
    article_url = SITE_URL+'/blog/'+a['slug']+'/'
    schema = {'@context':'https://schema.org','@type':'BlogPosting','headline':a['title'],'description':a['summary'],'url':article_url,'mainEntityOfPage':article_url,'image':SOCIAL_IMAGE,'author':{'@type':'Person','name':a['author']},'publisher':{'@type':'LegalService','name':'Yamancı | Özer Avukatlık & Arabuluculuk','url':SITE_URL},'datePublished':'2026-09-24','dateModified':'2026-09-25','inLanguage':'tr-TR','articleSection':a['category']}
    (path/'index.html').write_text(page(a['title'], a['summary'], body, '/blog/'+a['slug']+'/', schema, 'article'), encoding='utf-8')
teaser = '<section id="blog" class="section home-blog"><div class="section-head"><div><p class="eyebrow">05 / BLOG</p><h2>Hukuki yazılar.</h2></div><a class="blog-all" href="/blog/">Tüm yazıları inceleyin <span aria-hidden="true">↗</span></a></div><div class="blog-grid">'+''.join(card(articles[i]) for i in [0,8,12])+'</div></section>'
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
home_schema = {'@context':'https://schema.org','@type':'LegalService','name':'Yamancı | Özer Avukatlık & Arabuluculuk','url':SITE_URL,'image':SOCIAL_IMAGE,'email':'yönetim@yamanciozerhukuk.com','address':{'@type':'PostalAddress','streetAddress':'İkitelli OSB Mahallesi, Süleyman Demirel Bulvarı, İstmall AVM, Kat: 2, Daire: 199','addressLocality':'Başakşehir','addressRegion':'İstanbul','addressCountry':'TR'},'areaServed':'TR','knowsLanguage':'tr'}
home = home.replace('</head>', seo_tags('Yamancı | Özer — Avukatlık & Arabuluculuk', home_description, '/')+'<script type="application/ld+json">'+json.dumps(home_schema, ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
(DIST/'index.html').write_text(home, encoding='utf-8')

today = date.today().isoformat()
urls = [SITE_URL+'/', SITE_URL+'/blog/'] + [SITE_URL+'/blog/'+a['slug']+'/' for a in articles]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('  <url><loc>'+esc(url)+'</loc><lastmod>'+today+'</lastmod></url>\n' for url in urls) + '</urlset>\n'
(DIST/'sitemap.xml').write_text(sitemap, encoding='utf-8')
(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+SITE_URL+'/sitemap.xml\n', encoding='utf-8')
print(f'Generated {len(articles)} articles and blog index; updated home navigation and blog section.')

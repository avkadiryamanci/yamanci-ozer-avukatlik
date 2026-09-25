"""Generate the static blog, preserving the existing site's header and footer."""
from pathlib import Path
import json, html, re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
articles = json.loads((ROOT / 'content/articles.json').read_text())
sources = json.loads((ROOT / 'content/sources.json').read_text())
esc = html.escape
home = (DIST / 'index.html').read_text()
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
def page(title, description, body, schema=None):
    h = re.sub(r'<title>.*?</title>', '<title>' + esc(title) + ' | Yamancı Özer</title>', head)
    h = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="'+esc(description, quote=True)+'">', h)
    if schema:
        h = h.replace('</head>', '<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
    return h+'<body class="blog-page"><a class="skip" href="#icerik">İçeriğe geç</a>'+header+'<main id="icerik">'+body+'</main>'+footer+script+'</body></html>'
def card(a, compact=False):
    return '<article class="blog-card"><p class="category">'+esc(a['category'])+'</p><h3><a href="/blog/'+a['slug']+'/">'+esc(a['title'])+'</a></h3><p class="card-summary">'+esc(a['summary'])+'</p><div class="card-bottom"><p>'+esc(a['author'])+'</p><span aria-hidden="true">↗</span></div></article>'
intro = '<section class="blog-intro"><a class="back-link" href="/">Ana sayfa</a><p class="eyebrow">BLOG / HUKUKİ YAZILAR</p><h1>Hukuki bilgi.<br><em>Açık bir perspektif.</em></h1><p>Çalışma alanlarımızdan değerlendirmeler ve kentsel dönüşüm sürecine ilişkin yazılar.</p><div class="blog-stats"><span>18 hukuki yazı</span><span>6 yazar</span><span>Eylül 2026</span></div></section>'
guide = '<section class="blog-section guide-section" aria-labelledby="guide-title"><div class="blog-section-head"><div><p class="eyebrow">ÖZEL DOSYA</p><h2 id="guide-title">Kentsel dönüşüm rehberi</h2></div><p>Av. Arb. Kadir Yamancı<br>Malikler için altı temel konu</p></div><div class="blog-grid">'+''.join(card(a) for a in articles if a.get('guide'))+'</div></section>'
others = '<section class="blog-section" aria-labelledby="other-title"><div class="blog-section-head"><div><p class="eyebrow">ÇALIŞMA ALANLARIMIZDAN</p><h2 id="other-title">Hukuki değerlendirmeler</h2></div><p>Avukatlarımızın ve stajyer avukatımızın yazıları</p></div><div class="blog-grid">'+''.join(card(a) for a in articles if not a.get('guide'))+'</div></section>'
(DIST/'blog/index.html').write_text(page('Blog — Hukuki Yazılar', 'Yamancı Özer ekibinden 18 hukuki yazı: kentsel dönüşüm, gayrimenkul, ticaret, sözleşmeler, kira, aile, miras ve icra hukuku.', intro+guide+others))
for a in articles:
    path = DIST/'blog'/a['slug']; path.mkdir(exist_ok=True)
    body = '<div class="article-wrap"><div class="article-heading"><a class="back-link" href="/blog/">← Tüm yazılar</a><p class="category">'+esc(a['category'])+'</p><h1>'+esc(a['title'])+'</h1><p class="article-summary">'+esc(a['summary'])+'</p><div class="article-meta"><span>'+esc(a['author'])+'</span><time datetime="2026-09-24">24 Eylül 2026</time></div></div><div class="article-layout"><aside class="article-toc" aria-label="Bu yazıda"><p>BU YAZIDA</p><ol>'+''.join('<li><a href="#bolum-'+str(i)+'">'+esc(s[0])+'</a></li>' for i,s in enumerate(a['sections'],1))+'</ol></aside><article class="article-body">'
    body += ''.join('<section id="bolum-'+str(i)+'"><h2>'+esc(s[0])+'</h2><p>'+esc(s[1])+'</p></section>' for i,s in enumerate(a['sections'],1))
    body += '<div class="article-sources"><h2>Kaynaklar ve hukuki dayanak</h2>'
    if a.get('guide'):
        body += '<p>Bu yazı, Av. Arb. Kadir Yamancı’nın “Kentsel Dönüşüm Süreci ve Malikler İçin Tam Kapsamlı Bilgilendirme Metni” başlıklı rehberindeki konular esas alınarak hazırlanmıştır.</p>'
    body += '<ul>'+''.join('<li><a href="'+esc(sources[k]['url'], quote=True)+'" target="_blank" rel="noopener noreferrer">'+esc(sources[k]['label'])+' ↗</a></li>' for k in a['sources'])+'</ul><p class="legal-note">Bu yazı genel bilgilendirme amaçlıdır. Somut uyuşmazlığın belgeleri, işlem tarihi ve uygulanacak güncel mevzuat birlikte değerlendirilmelidir.</p></div></article></div>'
    related = [b for b in articles if b['author']==a['author'] and b['slug']!=a['slug']][:2]
    body += '<section class="article-related"><h2>Yazarın diğer yazıları</h2><div class="blog-grid">'+''.join(card(b) for b in related)+'</div></section></div>'
    schema = {'@context':'https://schema.org','@type':'BlogPosting','headline':a['title'],'description':a['summary'],'author':{'@type':'Person','name':a['author']},'datePublished':'2026-09-24','inLanguage':'tr-TR','articleSection':a['category']}
    (path/'index.html').write_text(page(a['title'], a['summary'], body, schema))
teaser = '<section id="blog" class="section home-blog"><div class="section-head"><div><p class="eyebrow">05 / BLOG</p><h2>Hukuki yazılar.</h2></div><a class="blog-all" href="/blog/">Tüm yazıları inceleyin <span aria-hidden="true">↗</span></a></div><div class="blog-grid">'+''.join(card(articles[i]) for i in [0,8,12])+'</div></section>'
if '<section id="blog"' in home:
    home = re.sub(r'<section id="blog".*?</section>', teaser, home, flags=re.S)
else:
    home = home.replace('<section id="iletisim"', teaser+'\n<section id="iletisim"')
home = home.replace('05 / İLETİŞİM', '06 / İLETİŞİM')
if 'href="/blog.css"' not in home:
    home = home.replace('</head>', '<link rel="stylesheet" href="/blog.css">\n</head>')
(DIST/'index.html').write_text(home)
print(f'Generated {len(articles)} articles and blog index; updated home navigation and blog section.')

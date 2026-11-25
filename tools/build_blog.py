"""Build the blog Worker (one Worker, one blog per brand, chosen by hostname).
Usage: python3 tools/build_blog.py  -> writes build/blog_routes.json (served by tools/blog_worker.js, deployed once as Worker "infosoft-blog")
Articles: blog/<brand>/<YYYY-MM-DD>-<slug>.md with YAML front matter (title, description, slug, lang, date)."""
import os, json, glob, html, re, yaml, markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANDS = {
 "vetario": dict(host="blog.vetario.ca", name="Vetario", site="https://vetario.ca", lang="sq",
                 bg="#0E2A2F", fg="#F4F8F7", accent="#3DD6B5", blog="Blogu i Vetario",
                 tagline="Këshilla për klinikat veterinare në Kosovë dhe Shqipëri", cta="Vizitoni vetario.ca", more="Lexo më shumë"),
 "invall": dict(host="blog.invall.ca", name="Invall", site="https://invall.ca", lang="sq",
                bg="#F5F3EE", fg="#14213D", accent="#FCA311", blog="Blogu i Invall",
                tagline="Fatura, oferta dhe menaxhimi i biznesit, thjesht", cta="Provo 14 ditë falas në invall.ca", more="Lexo më shumë"),
 "ontexi": dict(host="blog.canada.infosofttech.ca", name="Ontexi", site="https://canada.infosofttech.ca", lang="en",
                bg="#1F2933", fg="#F7F7F2", accent="#FFC233", blog="Ontexi Blog",
                tagline="Practical tips for Canadian construction businesses", cta="Visit canada.infosofttech.ca", more="Read more"),
 "tapline": dict(host="blog.tapline.ca", name="Tapline", site="https://tapline.ca", lang="en",
                 bg="#1B1410", fg="#FBF3E4", accent="#F2A541", blog="Tapline Blog",
                 tagline="Running a Canadian brewery, made simpler", cta="Get started at tapline.ca", more="Read more"),
 "winery": dict(host="winery-blog.infosofttech.ca", name="Winery Suite", site="https://winery.infosofttech.ca", lang="en",
                bg="#3A0F1E", fg="#FBF1F3", accent="#E8B4C0", blog="Winery Suite Blog",
                tagline="Ideas for running a modern winery", cta="Start your 90-day free trial", more="Read more"),
}

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:%(bg)s;color:%(fg)s;line-height:1.65}
a{color:inherit}
header{border-bottom:1px solid color-mix(in srgb,%(fg)s 15%%,transparent)}
.bar{max-width:820px;margin:0 auto;padding:18px 20px;display:flex;justify-content:space-between;align-items:center;gap:12px}
.logo{font-weight:800;font-size:22px;text-decoration:none;display:flex;gap:10px;align-items:center}
.logo i{width:14px;height:14px;border-radius:4px;background:%(accent)s;display:inline-block}
nav{white-space:nowrap;flex:none}nav a{text-decoration:none;font-weight:600;margin-left:18px;font-size:15px}
@media(max-width:480px){.logo{font-size:18px}nav a.home{display:none}}
.btn{background:%(accent)s;color:%(bg)s;padding:10px 16px;border-radius:10px}
main{max-width:820px;margin:0 auto;padding:40px 20px 80px}
h1{font-size:clamp(30px,5vw,44px);line-height:1.15;letter-spacing:-1px;margin-bottom:12px}
h2{font-size:26px;margin:36px 0 10px}h3{font-size:20px;margin:24px 0 8px}
p,ul,ol{margin:12px 0;font-size:18px}ul,ol{padding-left:24px}li{margin:6px 0}
.lead{opacity:.8;font-size:19px}
.meta{opacity:.6;font-size:14px;margin-bottom:28px}
.card{display:block;text-decoration:none;padding:24px;border-radius:16px;margin:18px 0;background:color-mix(in srgb,%(fg)s 7%%,transparent)}
.card h2{margin:0 0 8px;font-size:24px}.card p{margin:0;opacity:.8;font-size:17px}
.cta{margin-top:48px;padding:28px;border-radius:16px;background:%(accent)s;color:%(bg)s;text-align:center}
.cta a{font-weight:800;font-size:20px;text-decoration:none}
footer{text-align:center;opacity:.6;font-size:14px;padding:30px 20px}"""


def page(b, title, desc, canonical, body, jsonld):
    return f"""<!doctype html><html lang="{b['lang']}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}"><meta property="og:type" content="website">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<style>{CSS % b}</style></head><body>
<header><div class="bar"><a class="logo" href="/"><i></i>{b['blog']}</a>
<nav><a class="home" href="/">Blog</a><a class="btn" href="{b['site']}">{b['name']} →</a></nav></div></header>
<main>{body}</main><footer>© Infosoft Technology · <a href="{b['site']}">{b['site'].replace('https://','')}</a></footer></body></html>"""


def build():
    routes = {}
    for key, b in BRANDS.items():
        base = f"https://{b['host']}"
        posts = []
        for f in sorted(glob.glob(f"{ROOT}/blog/{key}/*.md"), reverse=True):
            raw = open(f, encoding="utf-8").read()
            _, fm, md = raw.split("---", 2)
            meta = yaml.safe_load(fm)
            # drop the markdown H1; the template renders the title
            md = re.sub(r"^\s*# .*\n", "", md, count=1)
            posts.append(dict(meta, body=markdown.markdown(md, extensions=["extra"])))
        r = {}
        cards = "".join(f'<a class="card" href="/{p["slug"]}"><h2>{html.escape(p["title"])}</h2>'
                        f'<p>{html.escape(p["description"])}</p></a>' for p in posts)
        r["/"] = page(b, f"{b['blog']} | {b['tagline']}", b["tagline"], base + "/",
                      f"<h1>{b['blog']}</h1><p class='lead'>{b['tagline']}</p>{cards}"
                      f"<div class='cta'><a href='{b['site']}'>{b['cta']} →</a></div>",
                      {"@context": "https://schema.org", "@type": "Blog", "name": b["blog"], "url": base + "/",
                       "inLanguage": b["lang"], "publisher": {"@type": "Organization", "name": "Infosoft Technology", "url": b["site"]}})
        for p in posts:
            url = f"{base}/{p['slug']}"
            ld = {"@context": "https://schema.org", "@graph": [
                {"@type": "BlogPosting", "headline": p["title"], "description": p["description"], "datePublished": str(p["date"]),
                 "inLanguage": b["lang"], "mainEntityOfPage": url, "author": {"@type": "Organization", "name": b["name"]},
                 "publisher": {"@type": "Organization", "name": "Infosoft Technology", "url": b["site"]}},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": b["name"], "item": b["site"]},
                    {"@type": "ListItem", "position": 2, "name": "Blog", "item": base + "/"},
                    {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]}]}
            r["/" + p["slug"]] = page(b, f"{p['title']} | {b['name']}", p["description"], url,
                                      f"<h1>{html.escape(p['title'])}</h1><div class='meta'>{p['date']} · {b['name']}</div>{p['body']}"
                                      f"<div class='cta'><a href='{b['site']}'>{b['cta']} →</a></div>", ld)
        urls = [base + "/"] + [f"{base}/{p['slug']}" for p in posts]
        r["/sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                             + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>")
        r["/robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
        routes[b["host"]] = r
    os.makedirs(f"{ROOT}/build", exist_ok=True)
    data = json.dumps(routes, ensure_ascii=False)
    open(f"{ROOT}/build/blog_routes.json", "w", encoding="utf-8").write(data)
    print("hosts:", {h: len(r) - 3 for h, r in routes.items()}, "bytes:", len(data))


if __name__ == "__main__":
    build()

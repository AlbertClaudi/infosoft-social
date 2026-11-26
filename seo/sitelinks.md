# Sitelinks: technical SEO for all 5 sites

Google decides on sitelinks itself. These steps give it a clear site structure.

## 1. Main pages (same for every site)
Clear navigation menu in the header, with these pages and unique titles:
- `/` Home
- `/features` (or `/vecorite` for Vetario/Invall)
- `/pricing` (or `/cmimet`)
- `/blog`
- `/contact` (or `/kontakt`)
- `/demo` or `/login` if it exists

Every page: one unique `<title>`, one `<h1>`, a `<meta name="description">`, and `<link rel="canonical">`.

## 2. robots.txt
```
User-agent: *
Allow: /
Sitemap: https://<domain>/sitemap.xml
```

## 3. sitemap.xml
List home, main pages and every blog post (`/blog/<slug>`), with `<lastmod>`.

## 4. JSON-LD on the home page (replace NAME / URL / LANG)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {"@type": "Organization", "name": "Infosoft Technology", "url": "https://URL",
     "sameAs": ["https://www.instagram.com/infosoftechnology"]},
    {"@type": "WebSite", "name": "NAME", "url": "https://URL", "inLanguage": "LANG"},
    {"@type": "SoftwareApplication", "name": "NAME", "applicationCategory": "BusinessApplication",
     "operatingSystem": "Web", "url": "https://URL"}
  ]
}
</script>
```
Add `offers` only where the price is confirmed in BRANDS.md (TapLine CA$29/mo, Winery Suite CA$30/mo).

Blog posts: `BlogPosting` + `BreadcrumbList` (Home > Blog > Post).

## 5. Google Search Console (Albert)
1. search.google.com/search-console → Add property → Domain → each domain.
2. Verify with the DNS TXT record in Cloudflare DNS.
3. Sitemaps → submit `https://<domain>/sitemap.xml`.
4. Repeat for Bing Webmaster Tools (it can import from Search Console).

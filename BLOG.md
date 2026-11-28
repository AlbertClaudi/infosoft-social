# Blogs – Infosoft Technology

One Cloudflare Worker, **infosoft-blog**, serves all six blogs. It reads `build/blog_routes.json` from GitHub main (cache about 10 min), so a new article goes live with a push. No redeploy is needed.

| Brand | Blog URL | Language | Main site |
|---|---|---|---|
| Vetario | https://blog.vetario.ca | Albanian | vetario.ca |
| Invall | https://blog.invall.ca | Albanian | invall.ca |
| Ontexi | https://blog.canada.infosofttech.ca | English | canada.infosofttech.ca |
| TapLine | https://blog.tapline.ca | English | tapline.ca |
| Winery Suite | https://blog.winery.infosofttech.ca | English | winery.infosofttech.ca |
| Elirin | https://blog.elirin.ca | English | elirin.ca |

## Weekly routine (1 article per brand per week)
1. Brand facts come only from BRANDS.md. Never invent features, prices, customers, statistics or claims.
2. Write one new article per brand: `blog/<brand>/<YYYY-MM-DD>-<slug>.md` with front matter `title, description, slug, lang, brand, site, date, keywords`. Use the date of the day it is written (not a future date).
3. 600–900 words, practical and educational (a how-to, a checklist, or a common problem for that industry). The product is mentioned only in the final section, with a link to the main site. Albanian for Vetario and Invall, English for the others (Ontexi, TapLine, Winery Suite, Elirin).
4. Choose a topic and keywords not already covered: check existing files in `blog/<brand>/`.
5. Run `python3 tools/build_blog.py`, commit and push to main.
6. The worker code lives in `tools/blog_worker.js`. Change it only when the routing must change, and redeploy it through the Cloudflare API connector.

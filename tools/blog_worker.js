// Cloudflare Worker "infosoft-blog": serves blog.<brand> hosts from build/blog_routes.json on GitHub main.
// New articles go live by pushing to main (cached up to 10 min); no redeploy needed.
const SRC = 'https://raw.githubusercontent.com/AlbertClaudi/infosoft-social/main/build/blog_routes.json';
export default { async fetch(req) {
  const u = new URL(req.url);
  if (u.hostname.startsWith('www.')) return Response.redirect('https://' + u.hostname.slice(4) + u.pathname, 301);
  const res = await fetch(SRC, { cf: { cacheTtl: 600, cacheEverything: true } });
  if (!res.ok) return new Response('Temporarily unavailable', { status: 503 });
  const site = (await res.json())[u.hostname];
  if (!site) return new Response('Not found', { status: 404 });
  const p = u.pathname.replace(/\/+$/, '') || '/';
  const body = site[p];
  if (!body) return new Response(site['/'], { status: 404, headers: { 'content-type': 'text/html; charset=utf-8' } });
  const type = p.endsWith('.xml') ? 'application/xml' : p.endsWith('.txt') ? 'text/plain' : 'text/html';
  return new Response(body, { headers: { 'content-type': type + '; charset=utf-8', 'cache-control': 'public, max-age=600' } });
} };

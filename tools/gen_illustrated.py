"""Render 1080x1080 Instagram posts with brand illustrations.
Usage: python3 gen_illustrated.py OUT_DIR [brand ...]
Edit POSTS below for new headlines; ILLUS holds the SVG art per brand."""
import asyncio, sys, os
from playwright.async_api import async_playwright

CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1080px;font-family:'Inter',sans-serif;background:%(bg)s;color:%(fg)s;position:relative;overflow:hidden}
.art{position:absolute;right:-10px;bottom:-10px;width:620px;height:620px}
.glow{position:absolute;right:-120px;bottom:-120px;width:760px;height:760px;border-radius:50%%;background:%(accent)s;opacity:.13}
.wrap{position:absolute;left:80px;top:80px;bottom:80px;width:600px;display:flex;flex-direction:column}
.brand{font-family:'Inter Display','Inter';font-weight:800;font-size:44px;letter-spacing:-1px;display:flex;align-items:center;gap:16px}
.dot{width:22px;height:22px;border-radius:6px;background:%(accent)s}
.tag{margin-top:56px;align-self:flex-start;background:%(accent)s;color:%(tagfg)s;font-weight:700;font-size:25px;padding:12px 24px;border-radius:999px}
h1{font-family:'Inter Display','Inter';font-weight:800;font-size:%(h1size)s;line-height:1.03;letter-spacing:-2.5px;margin-top:30px}
ul{list-style:none;margin-top:38px;display:flex;flex-direction:column;gap:14px}
li{font-size:28px;font-weight:500;display:flex;gap:14px;align-items:center}
li:before{content:'';width:12px;height:12px;border-radius:50%%;background:%(accent)s;flex:none}
.foot{margin-top:auto}
.url{font-size:32px;font-weight:700;background:%(fg)s;color:%(bg)s;display:inline-block;padding:16px 28px;border-radius:14px}"""

ILLUS = {
"tapline": """<svg viewBox="0 0 620 620" xmlns="http://www.w3.org/2000/svg">
<!-- keg -->
<g transform="translate(330,250)">
 <rect x="0" y="0" width="220" height="300" rx="26" fill="#9AA3AD"/>
 <rect x="0" y="40" width="220" height="16" fill="#6E7781"/><rect x="0" y="244" width="220" height="16" fill="#6E7781"/>
 <rect x="18" y="70" width="26" height="160" rx="13" fill="#C9D0D6" opacity=".7"/>
 <rect x="85" y="-22" width="50" height="26" rx="6" fill="#6E7781"/>
</g>
<!-- hops -->
<g transform="translate(300,110)">
 <path d="M60 0 C40 20 40 40 60 50 C80 40 80 20 60 0Z" fill="#7CB342"/>
 <path d="M60 30 C30 50 30 80 60 95 C90 80 90 50 60 30Z" fill="#8BC34A"/>
 <path d="M60 70 C35 90 35 120 60 135 C85 120 85 90 60 70Z" fill="#7CB342"/>
 <path d="M60 0 q20 -30 55 -25" stroke="#558B2F" stroke-width="6" fill="none"/>
 <path d="M115 -25 c25 -5 40 15 30 30 c-20 5 -35 -10 -30 -30z" fill="#689F38"/>
</g>
<!-- pint 1 -->
<g transform="translate(70,250)">
 <path d="M0 40 L150 40 L132 330 L18 330 Z" fill="#F2A541"/>
 <path d="M0 40 L150 40 L146 100 L4 100 Z" fill="#E08E1B" opacity=".35"/>
 <ellipse cx="75" cy="40" rx="78" ry="16" fill="#FFF6E5"/>
 <circle cx="20" cy="30" r="26" fill="#FFF6E5"/><circle cx="60" cy="18" r="30" fill="#FFF6E5"/><circle cx="105" cy="22" r="28" fill="#FFF6E5"/><circle cx="138" cy="34" r="22" fill="#FFF6E5"/>
 <circle cx="50" cy="180" r="6" fill="#FFE3B0"/><circle cx="90" cy="230" r="5" fill="#FFE3B0"/><circle cx="70" cy="280" r="7" fill="#FFE3B0"/><circle cx="105" cy="150" r="4" fill="#FFE3B0"/>
 <rect x="22" y="70" width="14" height="230" rx="7" fill="#fff" opacity=".25"/>
</g>
<!-- pint 2 (dark) -->
<g transform="translate(210,330)">
 <path d="M0 30 L120 30 L106 260 L14 260 Z" fill="#5B2C0E"/>
 <ellipse cx="60" cy="30" rx="62" ry="13" fill="#F3E2C4"/>
 <circle cx="18" cy="22" r="20" fill="#F3E2C4"/><circle cx="55" cy="12" r="24" fill="#F3E2C4"/><circle cx="95" cy="18" r="21" fill="#F3E2C4"/>
 <rect x="18" y="55" width="11" height="180" rx="6" fill="#fff" opacity=".18"/>
</g>
</svg>""",

"winery": """<svg viewBox="0 0 620 620" xmlns="http://www.w3.org/2000/svg">
<!-- bottle -->
<g transform="translate(330,60)">
 <rect x="62" y="0" width="56" height="40" rx="6" fill="#B0254A"/>
 <path d="M66 40 L114 40 L114 150 C170 180 180 220 180 260 L180 520 Q180 540 160 540 L20 540 Q0 540 0 520 L0 260 C0 220 10 180 66 150 Z" fill="#1E5A3A"/>
 <rect x="20" y="300" width="140" height="150" rx="8" fill="#F6EBDD"/>
 <rect x="45" y="335" width="90" height="10" rx="5" fill="#7A1630"/><rect x="55" y="360" width="70" height="8" rx="4" fill="#7A1630" opacity=".6"/>
 <circle cx="90" cy="405" r="22" fill="none" stroke="#7A1630" stroke-width="5"/>
 <rect x="22" y="190" width="14" height="300" rx="7" fill="#fff" opacity=".18"/>
</g>
<!-- glass -->
<g transform="translate(110,230)">
 <path d="M0 0 L170 0 C175 120 140 190 85 195 C30 190 -5 120 0 0Z" fill="#FFFFFF" opacity=".22"/>
 <path d="M6 70 L164 70 C160 150 130 188 85 192 C40 188 10 150 6 70Z" fill="#B0254A"/>
 <ellipse cx="85" cy="70" rx="79" ry="12" fill="#C93A61"/>
 <rect x="78" y="194" width="14" height="140" fill="#FFFFFF" opacity=".35"/>
 <ellipse cx="85" cy="340" rx="70" ry="14" fill="#FFFFFF" opacity=".35"/>
</g>
<!-- grapes -->
<g transform="translate(150,70) scale(.85)">
 <path d="M95 -30 q10 -30 40 -30" stroke="#6B8E23" stroke-width="7" fill="none"/>
 <path d="M135 -60 c30 -10 55 10 45 35 c-25 8 -50 -10 -45 -35z" fill="#7BA23F"/>
 <g fill="#6A1B4D"><circle cx="60" cy="0" r="24"/><circle cx="105" cy="0" r="24"/><circle cx="150" cy="0" r="24"/>
 <circle cx="82" cy="40" r="24"/><circle cx="128" cy="40" r="24"/><circle cx="105" cy="80" r="24"/></g>
 <g fill="#fff" opacity=".3"><circle cx="52" cy="-8" r="6"/><circle cx="97" cy="-8" r="6"/><circle cx="74" cy="32" r="6"/></g>
</g>
</svg>""",

"vetario": """<svg viewBox="0 0 620 620" xmlns="http://www.w3.org/2000/svg">
<!-- clipboard / patient record -->
<g transform="translate(330,70) rotate(6)">
 <rect width="230" height="300" rx="20" fill="#F4F8F7"/>
 <rect x="70" y="-18" width="90" height="40" rx="10" fill="#3DD6B5"/>
 <circle cx="60" cy="80" r="26" fill="#3DD6B5" opacity=".35"/>
 <g fill="#B8C7C4"><rect x="100" y="66" width="100" height="12" rx="6"/><rect x="100" y="88" width="70" height="10" rx="5"/>
 <rect x="30" y="140" width="170" height="12" rx="6"/><rect x="30" y="170" width="170" height="12" rx="6"/><rect x="30" y="200" width="120" height="12" rx="6"/></g>
 <path d="M30 255 L70 255 L85 230 L105 275 L120 245 L200 245" stroke="#E2445C" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</g>
<!-- cat -->
<g transform="translate(70,200)">
 <path d="M40 150 L20 20 L120 95 Z" fill="#6B6F7A"/><path d="M300 150 L320 20 L220 95 Z" fill="#6B6F7A"/>
 <path d="M50 120 L38 50 L100 98 Z" fill="#F2A9B6"/><path d="M290 120 L302 50 L240 98 Z" fill="#F2A9B6"/>
 <ellipse cx="170" cy="210" rx="160" ry="140" fill="#8A8F9A"/>
 <ellipse cx="170" cy="270" rx="80" ry="58" fill="#D9DCE1"/>
 <ellipse cx="115" cy="190" rx="20" ry="26" fill="#C9E86B"/><ellipse cx="225" cy="190" rx="20" ry="26" fill="#C9E86B"/>
 <ellipse cx="115" cy="192" rx="7" ry="20" fill="#1B1B1B"/><ellipse cx="225" cy="192" rx="7" ry="20" fill="#1B1B1B"/>
 <path d="M158 242 L182 242 L170 256 Z" fill="#E86F7E"/>
 <path d="M170 256 v12 M170 268 q-18 16 -34 2 M170 268 q18 16 34 2" stroke="#1B1B1B" stroke-width="5" fill="none" stroke-linecap="round"/>
 <g stroke="#F4F8F7" stroke-width="4" stroke-linecap="round"><line x1="60" y1="250" x2="0" y2="240"/><line x1="60" y1="265" x2="5" y2="275"/><line x1="280" y1="250" x2="340" y2="240"/><line x1="280" y1="265" x2="335" y2="275"/></g>
</g>
<!-- paw prints -->
<g fill="#3DD6B5" opacity=".8">
 <g transform="translate(420,470)"><ellipse cx="30" cy="40" rx="24" ry="20"/><circle cx="8" cy="12" r="9"/><circle cx="24" cy="2" r="9"/><circle cx="40" cy="2" r="9"/><circle cx="54" cy="14" r="9"/></g>
 <g transform="translate(500,545) scale(.75)"><ellipse cx="30" cy="40" rx="24" ry="20"/><circle cx="8" cy="12" r="9"/><circle cx="24" cy="2" r="9"/><circle cx="40" cy="2" r="9"/><circle cx="54" cy="14" r="9"/></g>
</g>
<!-- vet cross badge -->
<g transform="translate(40,60)">
 <circle cx="55" cy="55" r="55" fill="#E2445C"/>
 <rect x="44" y="22" width="22" height="66" rx="5" fill="#fff"/><rect x="22" y="44" width="66" height="22" rx="5" fill="#fff"/>
</g>
</svg>""",

"invall": """<svg viewBox="0 0 620 620" xmlns="http://www.w3.org/2000/svg">
<!-- bank building -->
<g transform="translate(300,60)">
 <path d="M0 90 L140 10 L280 90 Z" fill="#14213D"/>
 <rect x="10" y="90" width="260" height="22" fill="#14213D"/>
 <g fill="#E5DED0"><rect x="30" y="120" width="34" height="150"/><rect x="92" y="120" width="34" height="150"/><rect x="154" y="120" width="34" height="150"/><rect x="216" y="120" width="34" height="150"/></g>
 <rect x="0" y="270" width="280" height="26" rx="4" fill="#14213D"/>
 <circle cx="140" cy="58" r="16" fill="#FCA311"/>
</g>
<!-- payment card -->
<g transform="translate(60,250) rotate(-8)">
 <rect width="330" height="200" rx="24" fill="#2A6FDB"/>
 <rect x="0" y="40" width="330" height="40" fill="#14213D"/>
 <rect x="30" y="110" width="56" height="42" rx="8" fill="#FCA311"/>
 <g fill="#fff" opacity=".85"><rect x="110" y="120" width="60" height="12" rx="6"/><rect x="180" y="120" width="60" height="12" rx="6"/><rect x="30" y="168" width="140" height="10" rx="5"/></g>
</g>
<!-- coin stack -->
<g transform="translate(400,400)">
 <g fill="#F0A800"><ellipse cx="80" cy="170" rx="80" ry="22"/><rect x="0" y="40" width="160" height="130"/></g>
 <g fill="#FCA311"><ellipse cx="80" cy="40" rx="80" ry="22"/></g>
 <g stroke="#14213D" stroke-width="3" opacity=".35"><line x1="0" y1="80" x2="160" y2="80"/><line x1="0" y1="120" x2="160" y2="120"/></g>
 <text x="80" y="53" text-anchor="middle" font-family="Inter" font-weight="800" font-size="34" fill="#14213D">€</text>
</g>
<!-- pie chart -->
<g transform="translate(130,500)">
 <circle cx="0" cy="0" r="85" fill="#14213D"/>
 <path d="M0 0 L0 -85 A85 85 0 0 1 80 28 Z" fill="#FCA311"/>
 <path d="M0 0 L80 28 A85 85 0 0 1 -30 80 Z" fill="#2BB673"/>
 <circle cx="0" cy="0" r="34" fill="#F5F3EE"/>
</g>
</svg>""",

"ontexi": """<svg viewBox="0 0 620 620" xmlns="http://www.w3.org/2000/svg">
<!-- brick wall -->
<g fill="#C8553D">
 <rect x="20" y="470" width="120" height="44" rx="4"/><rect x="146" y="470" width="120" height="44" rx="4"/><rect x="272" y="470" width="120" height="44" rx="4"/><rect x="398" y="470" width="120" height="44" rx="4"/>
 <rect x="-40" y="520" width="120" height="44" rx="4"/><rect x="86" y="520" width="120" height="44" rx="4"/><rect x="212" y="520" width="120" height="44" rx="4"/><rect x="338" y="520" width="120" height="44" rx="4"/><rect x="464" y="520" width="120" height="44" rx="4"/>
 <rect x="20" y="570" width="120" height="44" rx="4"/><rect x="146" y="570" width="120" height="44" rx="4"/><rect x="272" y="570" width="120" height="44" rx="4"/><rect x="398" y="570" width="120" height="44" rx="4"/>
</g>
<!-- big clock -->
<g transform="translate(180,40)">
 <circle cx="130" cy="130" r="130" fill="#F7F7F2"/>
 <circle cx="130" cy="130" r="110" fill="none" stroke="#FFC233" stroke-width="10"/>
 <g fill="#1F2933"><rect x="125" y="34" width="10" height="22" rx="3"/><rect x="125" y="204" width="10" height="22" rx="3"/><rect x="34" y="125" width="22" height="10" rx="3"/><rect x="204" y="125" width="22" height="10" rx="3"/></g>
 <line x1="130" y1="130" x2="130" y2="66" stroke="#1F2933" stroke-width="10" stroke-linecap="round"/>
 <line x1="130" y1="130" x2="180" y2="155" stroke="#E2445C" stroke-width="7" stroke-linecap="round"/>
 <circle cx="130" cy="130" r="12" fill="#1F2933"/>
</g>
<!-- hard hat on wall -->
<g transform="translate(320,330) scale(.8)">
 <path d="M30 120 C30 40 90 0 160 0 C230 0 290 40 290 120 Z" fill="#FFC233"/>
 <rect x="0" y="115" width="330" height="34" rx="17" fill="#F0A800"/>
 <rect x="140" y="-6" width="40" height="126" rx="12" fill="#F0A800"/>
</g>
<!-- hammer -->
<g transform="translate(70,300) rotate(-30 80 80)">
 <rect x="70" y="40" width="22" height="150" rx="8" fill="#8D5B3A"/>
 <path d="M30 20 L130 20 L130 56 L30 56 Q10 38 30 20Z" fill="#9AA3AD"/>
</g>
<!-- traffic cone -->
<g transform="translate(40,330)">
 <path d="M55 0 L85 0 L120 130 L20 130 Z" fill="#FF7A1A"/>
 <path d="M44 42 L96 42 L104 72 L36 72 Z" fill="#F7F7F2"/>
 <rect x="0" y="126" width="140" height="16" rx="5" fill="#E2611A"/>
</g>
</svg>""",
}

POSTS = {
 "vetario": dict(bg="#0E2A2F",fg="#F4F8F7",accent="#3DD6B5",tagfg="#0E2A2F",name="Vetario",
   tag="Kosovë & Shqipëri",
   head="Çdo pacient.<br>Çdo vizitë.<br>Në një vend.", h1size="66px",
   items=["Historiku mjekësor","Klientët & kafshët","Terminet","Fatura & raporte"], url="vetario.ca"),
 "invall": dict(bg="#F5F3EE",fg="#14213D",accent="#FCA311",tagfg="#14213D",name="Invall",
   tag="14 ditë provë FALAS",
   head="Pagesat,<br>banka & pagat<br>nën kontroll.",
   items=["Pagesa online","Banka & shpenzimet","Pagat & TVSH","Portali i klientit"], url="invall.ca"),
 "ontexi": dict(bg="#1F2933",fg="#F7F7F2",accent="#FFC233",tagfg="#1F2933",name="Ontexi",
   tag="For Canadian construction",
   head="Clock in.<br>Clock out.<br>Get building.",
   items=["Employee time tracking","Clock in / clock out","All-in-one management"], url="canada.infosofttech.ca"),
 "tapline": dict(bg="#1B1410",fg="#FBF3E4",accent="#F2A541",tagfg="#1B1410",name="Tapline",
   tag="For Canadian breweries",
   head="From brew<br>to delivery.<br>One platform.",
   items=["Staff","Production","Deliveries","CA$29/mo · CA$290/yr"], url="tapline.ca"),
 "winery": dict(bg="#3A0F1E",fg="#FBF1F3",accent="#E8B4C0",tagfg="#3A0F1E",name="Winery Suite",
   tag="90-DAY FREE TRIAL",
   head="Run your<br>winery from<br>one dashboard.",
   items=["All-in-one suite","Made in Canada","CA$30/mo · CA$300/yr"], url="winery.infosofttech.ca"),
}

HTML = """<html><head><style>%(css)s</style></head><body>
<div class="glow"></div><div class="art">%(art)s</div>
<div class="wrap"><div class="brand"><span class="dot"></span>%(name)s</div>
<div class="tag">%(tag)s</div><h1>%(head)s</h1><ul>%(items)s</ul>
<div class="foot"><div class="url">%(url)s →</div></div></div></body></html>"""

async def main(out, brands):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width":1080,"height":1080})
        for k in brands:
            v = dict(POSTS[k]); v.setdefault("h1size","76px"); v["css"] = CSS % v; v["art"] = ILLUS[k]
            v["items"] = "".join(f"<li>{i}</li>" for i in v["items"])
            await pg.set_content(HTML % v)
            await pg.screenshot(path=f"{out}/{k}.png")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2:] or list(POSTS)))

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
<!-- tap tower -->
<g transform="translate(400,40)">
 <rect x="20" y="0" width="140" height="44" rx="12" fill="#9AA3AD"/>
 <rect x="70" y="44" width="40" height="190" fill="#6E7781"/>
 <g><rect x="34" y="60" width="18" height="70" rx="8" fill="#F2A541"/><rect x="38" y="128" width="10" height="34" fill="#C9D0D6"/></g>
 <g><rect x="128" y="60" width="18" height="70" rx="8" fill="#7CB342"/><rect x="132" y="128" width="10" height="34" fill="#C9D0D6"/></g>
 <rect x="0" y="230" width="180" height="20" rx="6" fill="#6E7781"/>
 <rect x="40" y="162" width="6" height="70" fill="#F2A541" opacity=".9"/>
</g>
<!-- pint under tap -->
<g transform="translate(395,290)">
 <path d="M0 30 L110 30 L98 230 L12 230 Z" fill="#F2A541"/>
 <ellipse cx="55" cy="30" rx="57" ry="12" fill="#FFF6E5"/>
 <circle cx="18" cy="22" r="18" fill="#FFF6E5"/><circle cx="52" cy="12" r="22" fill="#FFF6E5"/><circle cx="88" cy="20" r="19" fill="#FFF6E5"/>
 <circle cx="40" cy="140" r="5" fill="#FFE3B0"/><circle cx="70" cy="180" r="4" fill="#FFE3B0"/><circle cx="58" cy="100" r="5" fill="#FFE3B0"/>
 <rect x="16" y="50" width="10" height="160" rx="5" fill="#fff" opacity=".25"/>
</g>
<!-- delivery van with kegs -->
<g transform="translate(20,330)">
 <rect x="0" y="40" width="250" height="150" rx="16" fill="#FBF3E4"/>
 <path d="M250 80 L320 80 L360 130 L360 190 L250 190 Z" fill="#F2A541"/>
 <path d="M262 92 L314 92 L342 128 L262 128 Z" fill="#1B1410" opacity=".55"/>
 <g transform="translate(30,70)"><rect width="56" height="80" rx="10" fill="#9AA3AD"/><rect y="14" width="56" height="7" fill="#6E7781"/><rect y="58" width="56" height="7" fill="#6E7781"/></g>
 <g transform="translate(100,70)"><rect width="56" height="80" rx="10" fill="#9AA3AD"/><rect y="14" width="56" height="7" fill="#6E7781"/><rect y="58" width="56" height="7" fill="#6E7781"/></g>
 <g transform="translate(170,70)"><rect width="56" height="80" rx="10" fill="#9AA3AD"/><rect y="14" width="56" height="7" fill="#6E7781"/><rect y="58" width="56" height="7" fill="#6E7781"/></g>
 <circle cx="70" cy="196" r="32" fill="#2A211B"/><circle cx="70" cy="196" r="13" fill="#9AA3AD"/>
 <circle cx="295" cy="196" r="32" fill="#2A211B"/><circle cx="295" cy="196" r="13" fill="#9AA3AD"/>
 <g stroke="#F2A541" stroke-width="7" stroke-linecap="round" opacity=".7"><line x1="-30" y1="80" x2="-70" y2="80"/><line x1="-20" y1="120" x2="-80" y2="120"/></g>
</g>
<!-- hops -->
<g transform="translate(90,70)">
 <path d="M60 0 C40 20 40 40 60 50 C80 40 80 20 60 0Z" fill="#7CB342"/>
 <path d="M60 30 C30 50 30 80 60 95 C90 80 90 50 60 30Z" fill="#8BC34A"/>
 <path d="M60 70 C35 90 35 120 60 135 C85 120 85 90 60 70Z" fill="#7CB342"/>
 <path d="M60 0 q20 -30 55 -25" stroke="#558B2F" stroke-width="6" fill="none"/>
 <path d="M115 -25 c25 -5 40 15 30 30 c-20 5 -35 -10 -30 -30z" fill="#689F38"/>
</g>
<g transform="translate(230,130) scale(.6)">
 <path d="M60 0 C40 20 40 40 60 50 C80 40 80 20 60 0Z" fill="#8BC34A"/>
 <path d="M60 30 C30 50 30 80 60 95 C90 80 90 50 60 30Z" fill="#7CB342"/>
 <path d="M60 70 C35 90 35 120 60 135 C85 120 85 90 60 70Z" fill="#8BC34A"/>
</g>
</svg>""",

"winery": """<svg viewBox="0 0 620 620" xmlns="http://www.w3.org/2000/svg">
<!-- sun + vineyard hills -->
<circle cx="470" cy="110" r="70" fill="#E8B4C0" opacity=".85"/>
<defs><clipPath id="hillclip"><circle cx="310" cy="330" r="270"/></clipPath></defs>
<g clip-path="url(#hillclip)">
<path d="M0 300 Q160 200 330 270 T620 240 L620 400 L0 400 Z" fill="#2F6B45"/>
<path d="M0 340 Q200 270 400 320 T620 300 L620 420 L0 420 Z" fill="#1E5A3A"/>
<g stroke="#7BA23F" stroke-width="6" stroke-linecap="round" opacity=".8">
 <line x1="60" y1="300" x2="20" y2="380"/><line x1="140" y1="285" x2="120" y2="380"/><line x1="220" y1="285" x2="220" y2="380"/><line x1="300" y1="292" x2="320" y2="380"/><line x1="380" y1="300" x2="420" y2="380"/><line x1="460" y1="292" x2="520" y2="380"/>
</g>
</g>
<!-- barrels -->
<g transform="translate(40,390)">
 <ellipse cx="110" cy="110" rx="110" ry="100" fill="#8D5B3A"/>
 <ellipse cx="110" cy="110" rx="70" ry="64" fill="#A56B44"/>
 <ellipse cx="110" cy="110" rx="30" ry="27" fill="#6B4228"/>
 <g fill="none" stroke="#4A2E1C" stroke-width="8"><ellipse cx="110" cy="110" rx="100" ry="92"/></g>
</g>
<g transform="translate(250,410)">
 <ellipse cx="100" cy="100" rx="100" ry="92" fill="#7A4E32"/>
 <ellipse cx="100" cy="100" rx="62" ry="58" fill="#96603D"/>
 <ellipse cx="100" cy="100" rx="26" ry="24" fill="#5E3A24"/>
 <g fill="none" stroke="#4A2E1C" stroke-width="8"><ellipse cx="100" cy="100" rx="90" ry="84"/></g>
</g>
<!-- glass -->
<g transform="translate(450,300)">
 <path d="M0 0 L120 0 C124 90 100 140 60 144 C20 140 -4 90 0 0Z" fill="#FFFFFF" opacity=".25"/>
 <path d="M4 50 L116 50 C112 110 92 140 60 142 C28 140 8 110 4 50Z" fill="#B0254A"/>
 <ellipse cx="60" cy="50" rx="56" ry="9" fill="#C93A61"/>
 <rect x="54" y="144" width="12" height="120" fill="#FFFFFF" opacity=".4"/>
 <ellipse cx="60" cy="268" rx="52" ry="11" fill="#FFFFFF" opacity=".4"/>
</g>
<!-- grape bunch -->
<g transform="translate(60,70) scale(.75)">
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
 "tapline": dict(bg="#1B1410",fg="#FBF3E4",accent="#F2A541",tagfg="#1B1410",name="TapLine",
   tag="CA$29/mo · CA$290/yr",
   head="Pour more.<br>Juggle less.<br>One platform.",
   items=["Staff in one place","Production on track","Deliveries organized","Built for breweries"], url="tapline.ca"),
 "winery": dict(bg="#3A0F1E",fg="#FBF1F3",accent="#E8B4C0",tagfg="#3A0F1E",name="Winery Suite",
   tag="Try it free for 90 days",
   head="Your winery.<br>One suite.<br>90 days free.",
   items=["All-in-one platform","Made for wineries","Then CA$30/month","or CA$300/year"], url="winery.infosofttech.ca"),
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

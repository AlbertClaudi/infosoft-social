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
<!-- dog -->
<g transform="translate(120,140)">
 <ellipse cx="60" cy="120" rx="55" ry="115" fill="#8D5B3A" transform="rotate(18 60 120)"/>
 <ellipse cx="320" cy="120" rx="55" ry="115" fill="#8D5B3A" transform="rotate(-18 320 120)"/>
 <ellipse cx="190" cy="200" rx="160" ry="170" fill="#D9A066"/>
 <ellipse cx="190" cy="290" rx="95" ry="75" fill="#F3DDBF"/>
 <circle cx="130" cy="180" r="20" fill="#1B1B1B"/><circle cx="250" cy="180" r="20" fill="#1B1B1B"/>
 <circle cx="137" cy="173" r="7" fill="#fff"/><circle cx="257" cy="173" r="7" fill="#fff"/>
 <ellipse cx="190" cy="252" rx="34" ry="24" fill="#1B1B1B"/>
 <path d="M190 276 L190 300 M190 300 q-28 22 -50 0 M190 300 q28 22 50 0" stroke="#1B1B1B" stroke-width="7" fill="none" stroke-linecap="round"/>
 <path d="M178 318 q12 30 24 0 z" fill="#E86F7E"/>
</g>
<!-- stethoscope -->
<g fill="none" stroke="#3DD6B5" stroke-width="14" stroke-linecap="round">
 <path d="M180 470 C180 560 300 590 330 520 C350 470 420 470 440 520"/>
</g>
<circle cx="440" cy="540" r="34" fill="#3DD6B5"/><circle cx="440" cy="540" r="16" fill="#0E2A2F"/>
<!-- medical badge -->
<g transform="translate(470,80)">
 <circle cx="60" cy="60" r="60" fill="#F4F8F7"/>
 <rect x="48" y="25" width="24" height="70" rx="5" fill="#E2445C"/><rect x="25" y="48" width="70" height="24" rx="5" fill="#E2445C"/>
</g>

</svg>""",

"invall": """<svg viewBox="0 0 620 620" xmlns="http://www.w3.org/2000/svg">
<!-- back doc -->
<g transform="translate(250,90) rotate(8)">
 <rect width="280" height="370" rx="20" fill="#E5DED0"/>
</g>
<!-- invoice -->
<g transform="translate(150,110) rotate(-4)">
 <rect width="300" height="400" rx="20" fill="#FFFFFF" stroke="#14213D" stroke-width="4"/>
 <rect x="30" y="30" width="120" height="22" rx="6" fill="#14213D"/>
 <rect x="200" y="30" width="70" height="22" rx="6" fill="#FCA311"/>
 <g fill="#C9CED8"><rect x="30" y="90" width="240" height="12" rx="6"/><rect x="30" y="120" width="180" height="12" rx="6"/>
 <rect x="30" y="170" width="240" height="12" rx="6"/><rect x="30" y="200" width="240" height="12" rx="6"/><rect x="30" y="230" width="240" height="12" rx="6"/></g>
 <line x1="30" y1="270" x2="270" y2="270" stroke="#14213D" stroke-width="3"/>
 <rect x="160" y="290" width="110" height="26" rx="6" fill="#14213D"/>
 <path d="M30 360 c20 -30 40 10 60 -10 s30 -20 50 0 s20 10 40 -5" stroke="#2A6FDB" stroke-width="5" fill="none" stroke-linecap="round"/>
</g>
<!-- check badge -->
<g transform="translate(430,370)">
 <circle cx="60" cy="60" r="60" fill="#2BB673"/>
 <path d="M32 62 L52 82 L90 40" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</g>
<!-- bar chart -->
<g transform="translate(60,470)">
 <rect x="0" y="0" width="230" height="130" rx="18" fill="#14213D"/>
 <rect x="30" y="70" width="30" height="40" rx="5" fill="#FCA311"/><rect x="80" y="45" width="30" height="65" rx="5" fill="#FCA311"/>
 <rect x="130" y="55" width="30" height="55" rx="5" fill="#FCA311"/><rect x="180" y="25" width="30" height="85" rx="5" fill="#FCA311"/>
</g>
<!-- euro coin -->
<g transform="translate(470,160)"><circle cx="45" cy="45" r="45" fill="#FCA311"/>
<text x="45" y="62" text-anchor="middle" font-family="Inter" font-weight="800" font-size="50" fill="#14213D">€</text></g>
</svg>""",

"ontexi": """<svg viewBox="0 0 620 620" xmlns="http://www.w3.org/2000/svg">
<!-- crane -->
<g transform="translate(0,70)"><g stroke="#FFC233" stroke-width="10" fill="none">
 <line x1="420" y1="40" x2="420" y2="600"/><line x1="460" y1="40" x2="460" y2="600"/>
 <path d="M420 80 L460 120 L420 160 L460 200 L420 240 L460 280 L420 320 L460 360 L420 400 L460 440 L420 480 L460 520 L420 560"/>
 <line x1="160" y1="40" x2="600" y2="40"/><line x1="160" y1="70" x2="600" y2="70"/>
 <path d="M200 40 L230 70 L260 40 L290 70 L320 40 L350 70 L380 40"/>
 <line x1="220" y1="70" x2="220" y2="190" stroke-width="5"/>
</g>
<rect x="190" y="190" width="60" height="40" rx="4" fill="#FFC233"/></g>
<!-- clock -->
<g transform="translate(70,180)">
 <circle cx="110" cy="110" r="110" fill="#F7F7F2"/>
 <circle cx="110" cy="110" r="92" fill="none" stroke="#1F2933" stroke-width="6"/>
 <g fill="#1F2933"><rect x="106" y="28" width="8" height="18" rx="3"/><rect x="106" y="174" width="8" height="18" rx="3"/><rect x="28" y="106" width="18" height="8" rx="3"/><rect x="174" y="106" width="18" height="8" rx="3"/></g>
 <line x1="110" y1="110" x2="110" y2="55" stroke="#1F2933" stroke-width="9" stroke-linecap="round"/>
 <line x1="110" y1="110" x2="155" y2="130" stroke="#E2445C" stroke-width="7" stroke-linecap="round"/>
 <circle cx="110" cy="110" r="10" fill="#1F2933"/>
</g>
<!-- hard hat -->
<g transform="translate(60,420)">
 <path d="M30 120 C30 40 90 0 160 0 C230 0 290 40 290 120 Z" fill="#FFC233"/>
 <rect x="0" y="115" width="330" height="34" rx="17" fill="#F0A800"/>
 <rect x="140" y="-6" width="40" height="126" rx="12" fill="#F0A800"/>
</g>
<!-- bricks -->
<g transform="translate(330,520)" fill="#C8553D">
 <rect x="0" y="0" width="80" height="36" rx="4"/><rect x="86" y="0" width="80" height="36" rx="4"/>
 <rect x="-40" y="42" width="80" height="36" rx="4"/><rect x="46" y="42" width="80" height="36" rx="4"/><rect x="132" y="42" width="80" height="36" rx="4"/>
</g>
</svg>""",
}

POSTS = {
 "vetario": dict(bg="#0E2A2F",fg="#F4F8F7",accent="#3DD6B5",tagfg="#0E2A2F",name="Vetario",
   tag="Për klinikat veterinare",
   head="Më shumë kohë<br>për pacientët<br>me 4 këmbë.", h1size="66px",
   items=["Kartela & historiku mjekësor","Terminet","Faturimi","Raportet"], url="vetario.ca"),
 "invall": dict(bg="#F5F3EE",fg="#14213D",accent="#FCA311",tagfg="#14213D",name="Invall",
   tag="14 ditë provë FALAS",
   head="Faturat dhe<br>ofertat, gati<br>për nënshkrim.",
   items=["Fatura & oferta me email","Nënshkrim online","Stoku, pagat & TVSH","Raporte"], url="invall.ca"),
 "ontexi": dict(bg="#1F2933",fg="#F7F7F2",accent="#FFC233",tagfg="#1F2933",name="Ontexi",
   tag="For Canadian construction",
   head="Your crew.<br>Your jobs.<br>One platform.",
   items=["Clock in / clock out","All-in-one management","Made in Canada"], url="canada.infosofttech.ca"),
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

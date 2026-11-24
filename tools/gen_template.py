import asyncio
from playwright.async_api import async_playwright

BASE = """<html><head><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1080px;font-family:'Inter',sans-serif;background:%(bg)s;color:%(fg)s;position:relative;overflow:hidden}
.blob{position:absolute;border-radius:50%%;background:%(accent)s;opacity:.18}
.wrap{position:absolute;inset:80px;display:flex;flex-direction:column}
.brand{font-family:'Inter Display','Inter';font-weight:800;font-size:44px;letter-spacing:-1px;display:flex;align-items:center;gap:16px}
.dot{width:22px;height:22px;border-radius:6px;background:%(accent)s}
.tag{margin-top:70px;display:inline-block;align-self:flex-start;background:%(accent)s;color:%(tagfg)s;font-weight:700;font-size:26px;padding:12px 24px;border-radius:999px}
h1{font-family:'Inter Display','Inter';font-weight:800;font-size:82px;line-height:1.02;letter-spacing:-2.5px;margin-top:34px}
ul{list-style:none;margin-top:46px;display:grid;grid-template-columns:1fr 1fr;gap:18px 30px}
li{font-size:29px;font-weight:500;display:flex;gap:14px;align-items:center;opacity:.92}
li:before{content:'';width:12px;height:12px;border-radius:50%%;background:%(accent)s;flex:none}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end}
.url{font-size:34px;font-weight:700}
.cta{background:%(fg)s;color:%(bg)s;font-weight:700;font-size:28px;padding:20px 34px;border-radius:16px}
</style></head><body>
<div class="blob" style="width:700px;height:700px;right:-260px;top:-260px"></div>
<div class="blob" style="width:380px;height:380px;right:120px;bottom:-200px"></div>
<div class="wrap">
<div class="brand"><span class="dot"></span>%(name)s</div>
<div class="tag">%(tag)s</div>
<h1>%(head)s</h1>
<ul>%(items)s</ul>
<div class="foot"><div class="url">%(url)s</div><div class="cta">%(cta)s</div></div>
</div></body></html>"""

posts = {
 "vetario": dict(bg="#0E2A2F",fg="#F4F8F7",accent="#3DD6B5",tagfg="#0E2A2F",name="Vetario",
   tag="Për klinikat veterinare · Kosovë & Shqipëri",
   head="Klinika juaj,<br>e organizuar<br>në një vend.",
   items=["Kartela e pacientëve","Historiku mjekësor","Terminet","Faturimi","Klientët","Raportet"],
   url="vetario.ca",cta="Provojeni sot →"),
 "invall": dict(bg="#F5F3EE",fg="#14213D",accent="#FCA311",tagfg="#14213D",name="Invall",
   tag="14 ditë provë FALAS",
   head="Faturat, ofertat<br>dhe projektet.<br>Të gjitha në Invall.",
   items=["Fatura & oferta","Nënshkrim me email","Stoku & shpenzimet","Pagat & TVSH","Pagesa online","Raporte"],
   url="invall.ca",cta="Fillo falas →"),
 "tapline": dict(bg="#1B1410",fg="#FBF3E4",accent="#F2A541",tagfg="#1B1410",name="Tapline",
   tag="Built for brewery owners",
   head="Pour more beer.<br>Do less<br>admin.",
   items=["All-in-one platform","Made in Canada","CA$29 / month","or CA$290 / year"],
   url="tapline.ca",cta="See how →"),
 "ontexi": dict(bg="#1F2933",fg="#F7F7F2",accent="#FFC233",tagfg="#1F2933",name="Ontexi",
   tag="For Canadian construction businesses",
   head="Build more.<br>Chase paperwork<br>less.",
   items=["All-in-one platform","Made in Canada","Cloud-based","For contractors"],
   url="canada.infosofttech.ca",cta="Learn more →"),
 "winery": dict(bg="#3A0F1E",fg="#FBF1F3",accent="#E8B4C0",tagfg="#3A0F1E",name="Winery Suite",
   tag="90-DAY FREE TRIAL",
   head="Run your winery<br>from one<br>dashboard.",
   items=["All-in-one suite","Made in Canada","CA$30 / month","or CA$300 / year"],
   url="winery.infosofttech.ca",cta="Start free →"),
}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width":1080,"height":1080})
        for k,v in posts.items():
            v=dict(v); v["items"]="".join(f"<li>{i}</li>" for i in v["items"])
            await pg.set_content(BASE % v)
            await pg.screenshot(path=f"{k}.png")
        await b.close()
asyncio.run(main())

"""Make a 1080x1920 animated video with music for Reels + Stories.
Usage: python3 make_reel.py OUT_DIR brand [brand ...]
Uses POSTS and ILLUS from gen_illustrated.py (edit headlines there)."""
import asyncio, sys, os, subprocess, random
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(__file__))
from gen_illustrated import POSTS, ILLUS

SECS, FPS = 12, 30
MOOD = {"tapline": "bright", "winery": "calm", "vetario": "warm", "invall": "bright", "ontexi": "warm"}

CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;font-family:'Inter',sans-serif;background:%(bg)s;color:%(fg)s;position:relative;overflow:hidden}
@keyframes up{from{opacity:0;transform:translateY(60px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{0%%{opacity:0;transform:scale(.6)}70%%{opacity:1;transform:scale(1.04)}100%%{opacity:1;transform:scale(1)}}
@keyframes float{0%%,100%%{transform:translateY(0)}50%%{transform:translateY(-18px)}}
@keyframes rise{from{transform:translateY(0);opacity:0}15%%{opacity:.7}to{transform:translateY(-1500px);opacity:0}}
@keyframes pulse{0%%,100%%{transform:scale(1)}50%%{transform:scale(1.06)}}
@keyframes glow{0%%,100%%{transform:scale(1);opacity:.13}50%%{transform:scale(1.08);opacity:.2}}
@keyframes spin{to{transform:rotate(360deg)}}
.a{opacity:0;animation-fill-mode:both}
.glow{position:absolute;left:50%%;top:1180px;width:900px;height:900px;margin:-450px 0 0 -450px;border-radius:50%%;background:%(accent)s;animation:glow 4s ease-in-out infinite}
.p{position:absolute;bottom:-40px;border-radius:50%%;background:%(accent)s;animation:rise linear infinite}
.top{position:absolute;left:90px;right:90px;top:230px}
.brand{font-family:'Inter Display','Inter';font-weight:800;font-size:56px;letter-spacing:-1px;display:flex;align-items:center;gap:18px;animation:fade .6s .2s both}
.dot{width:26px;height:26px;border-radius:7px;background:%(accent)s}
.tag{display:inline-block;margin-top:36px;background:%(accent)s;color:%(tagfg)s;font-weight:700;font-size:32px;padding:14px 30px;border-radius:999px;animation:up .6s .5s both}
h1{font-family:'Inter Display','Inter';font-weight:800;font-size:96px;line-height:1.02;letter-spacing:-3px;margin-top:30px}
h1 span{display:block;animation:up .7s both}
.artwrap{position:absolute;left:50%%;top:720px;width:780px;height:780px;margin-left:-390px;animation:pop .9s 6.3s both}
.art{width:100%%;height:100%%;animation:float 4s 7.2s ease-in-out infinite}
.art svg{width:100%%;height:100%%}
.hand{animation:spin 6s linear infinite}
ul{position:absolute;left:90px;right:90px;top:900px;list-style:none;display:flex;flex-direction:column;gap:24px;align-items:flex-start}
li{font-size:48px;font-weight:700;background:%(fg)s;color:%(bg)s;padding:14px 26px;border-radius:16px;animation:up .5s both;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.cta{position:absolute;left:0;right:0;top:1530px;text-align:center;animation:up .6s 7.2s both}
.cta div{display:inline-block;font-size:44px;font-weight:800;background:%(accent)s;color:%(tagfg)s;padding:24px 44px;border-radius:22px;animation:pulse 1.6s 7.8s ease-in-out infinite}"""

def build(k):
    v = dict(POSTS[k])
    v.setdefault("h1size", "96px")
    lines = v["head"].split("<br>")
    h1 = "".join(f'<span style="animation-delay:{0.8+i*0.25:.2f}s">{l}</span>' for i, l in enumerate(lines))
    # features appear over the art area, one by one, then fade out to reveal the art
    items = "".join(f'<li style="animation-delay:{2.0+i*0.55:.2f}s">{t}</li>' for i, t in enumerate(v["items"]))
    rnd = random.Random(k)
    parts = "".join(
        f'<div class="p" style="left:{rnd.randint(0,1040)}px;width:{s}px;height:{s}px;animation-duration:{rnd.uniform(7,12):.1f}s;animation-delay:-{rnd.uniform(0,10):.1f}s"></div>'
        for s in [rnd.randint(8, 22) for _ in range(22)])
    art = ILLUS[k].replace('stroke="#E2445C" stroke-width="7"', 'class="hand" style="transform-box:fill-box;transform-origin:0 0" stroke="#E2445C" stroke-width="7"')
    css = CSS % v
    return f"""<html><head><style>{css}
ul{{animation:fade .5s 5.6s reverse both}}</style></head><body>
<div class="glow"></div>{parts}
<div class="top"><div class="brand"><span class="dot"></span>{v['name']}</div>
<div class="tag">{v['tag']}</div><h1>{h1}</h1></div>
<div class="artwrap"><div class="art">{art}</div></div>
<ul>{items}</ul>
<div class="cta"><div>{v['url']} →</div></div>
</body></html>"""

async def render(k, out):
    frames = f"/tmp/frames_{k}"; os.makedirs(frames, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(build(k)); await pg.wait_for_timeout(300)
        for f in range(SECS*FPS):
            t = f*1000/FPS
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={t}}})")
            await pg.screenshot(path=f"{frames}/{f:04d}.jpg", type="jpeg", quality=92)
        await b.close()
    wav = f"/tmp/{k}.wav"
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "music.py"), wav, str(SECS), MOOD.get(k, "warm"), str(sum(map(ord, k)) % 7)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{frames}/%04d.jpg", "-i", wav,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", f"{out}/{k}.mp4"], check=True)
    # cover image for reels (frame at 6s)
    subprocess.run(["cp", f"{frames}/{9*FPS:04d}.jpg", f"{out}/{k}_cover.jpg"], check=True)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for k in sys.argv[2:]:
        asyncio.run(render(k, out)); print("done", k)

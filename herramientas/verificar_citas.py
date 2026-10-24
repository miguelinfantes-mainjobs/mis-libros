import re,sys
from playwright.sync_api import sync_playwright
B="file:///workspace/libros-site/docs/libros/"
with sync_playwright() as p:
    br=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"]); pg=br.new_page(viewport={"width":1280,"height":900})
    for lid in sys.argv[1:]:
        qs=[re.sub(r"\s+\[FAVORITA[^\]]*\]\s*$","",m[2]) for l in open(f"libros/{lid}/citas.txt",encoding="utf-8").read().splitlines() if (m:=re.match(r"^(\d+)\. (.*)$",l))]
        pg.goto(B+lid+"/index.html"); pg.click("text=Abrir todo")
        a=sum(q in pg.locator("#v-mapa").inner_text() for q in qs)
        pg.screenshot(path=f"/workspace/visual/libros-{lid}-mapa.png",full_page=True)
        pg.click("[data-vista=tarjetas]"); t=sum(q in pg.locator("#v-tarjetas").inner_text() for q in qs)
        pg.screenshot(path=f"/workspace/visual/libros-{lid}-tarjetas.png",full_page=True)
        print(f"{lid}: mapa {a}/{len(qs)} · tarjetas {t}/{len(qs)}")

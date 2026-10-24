import sys
from playwright.sync_api import sync_playwright
lid=sys.argv[1]; U=sys.argv[2] if len(sys.argv)>2 else f"file:///workspace/libros-site/docs/libros/{lid}/bygga/index.html"
qs=[l for l in open(f"libros/{lid}/citas.txt",encoding="utf-8").read().splitlines() if l.strip()]
V="/workspace/visual/libros-bygga-"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    for nombre,vp in [("escritorio",{"width":1440,"height":1000}),("movil",{"width":390,"height":844})]:
        pg=b.new_page(viewport=vp,device_scale_factor=2 if nombre=="movil" else 1); pg.goto(U); pg.wait_for_timeout(700)
        N=pg.locator(".paso").count(); vistas=set()
        tot=pg.locator("#pasos").text_content(); print(nombre,"citas en página (todos los pasos):",sum(q in tot for q in qs),"/",len(qs))
        pg.screenshot(path=f"{V}{nombre}-paso1.png",full_page=True)
        for k in range(N):
            vistas.add(pg.locator(".paso.activo").get_attribute("data-i")); txt=pg.locator(".paso.activo").inner_text()
            for q in qs:
                if q in txt: vistas.add(q)
            if k==5: pg.wait_for_timeout(700); pg.screenshot(path=f"{V}{nombre}-paso6.png",full_page=True)
            if k<N-1: pg.keyboard.press("ArrowRight") if k%2 else pg.click("#sig"); pg.wait_for_timeout(250)
        print(nombre,"pasos recorridos:",len([v for v in vistas if len(v)<3]),"/",N,"· citas vistas en pantalla:",sum(q in vistas for q in qs),"/",len(qs),"· texto barra:",pg.inner_text("#pasoN"),"· confeti:",pg.locator("#confeti i").count())
        pg.wait_for_timeout(600); pg.screenshot(path=f"{V}{nombre}-final.png",full_page=True)
        pg.keyboard.press("ArrowLeft"); pg.wait_for_timeout(300); print(nombre,"← vuelve a:",pg.inner_text("#pasoN"))
        print(nombre,"fuente Inter cargada:",pg.evaluate("document.fonts.check('900 40px InterV')"))
    b.close()

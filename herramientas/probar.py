import re
from playwright.sync_api import sync_playwright
B="file:///workspace/libros-site/docs/"; V="/workspace/visual/"
raw=open("libros/la-parabola-de-los-talentos/citas.txt",encoding="utf-8").read().splitlines()
qs=[re.sub(r"\s+\[FAVORITA[^\]]*\]\s*$","",m[2]) for l in raw if (m:=re.match(r"^(\d+)\. (.*)$",l))]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"]); pg=b.new_page(viewport={"width":1280,"height":900})
    pg.goto(B+"index.html"); pg.screenshot(path=V+"libros-index.png",full_page=True)
    pg.goto(B+"libros/la-parabola-de-los-talentos/index.html")
    vis=lambda: pg.locator(".mapa .hoja:visible").count()
    print("hojas visibles inicio:",vis()); pg.screenshot(path=V+"libros-mapa-cerrado.png",full_page=True)
    r=pg.locator(".nodo.rama").nth(6); r.click(); print("tras abrir rama Destino:",vis(),r.get_attribute("aria-expanded"))
    pg.screenshot(path=V+"libros-mapa-rama-abierta.png",full_page=True)
    r.click(); print("tras cerrarla:",vis(),r.get_attribute("aria-expanded"))
    pg.click("text=Abrir todo"); print("abrir todo:",vis()); pg.screenshot(path=V+"libros-mapa-todo.png",full_page=True)
    txt=pg.locator("#v-mapa").inner_text(); print("citas en mapa (texto renderizado):",sum(q in txt for q in qs),"/",len(qs))
    pg.click("text=Cerrar todo"); print("cerrar todo:",vis())
    pg.click("[data-vista=tarjetas]"); txt=pg.locator("#v-tarjetas").inner_text()
    print("citas en tarjetas:",sum(q in txt for q in qs),"/",len(qs)); pg.screenshot(path=V+"libros-tarjetas.png",full_page=True)
    pg.goto(B+"libros/parentesco/index.html"); pg.click("text=Abrir todo"); pg.screenshot(path=V+"libros-ficha-parentesco.png",full_page=True)
    for h in ["ficha.png","ficha.pdf"]: import os; print(h, os.path.getsize("docs/libros/parentesco/"+h))
    b.close()

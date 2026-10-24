"""Importa una vez el material de /workspace/bookbot a libros/<id>/ (libro.json + archivos).
Uso: python3 herramientas/importar_bookbot.py [/workspace/bookbot]"""
import json, re, shutil, sys, subprocess
from pathlib import Path
from bs4 import BeautifulSoup
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/bookbot")
DST = Path(__file__).resolve().parent.parent / "libros"
PNG = {"ad":"al-despertar.png","dp":"desolacion-paz.png","et":"estacion-transito.png","gi":"glandula-icaro.png",
 "guasch":"en-las-manos-paraiso-quema.png","ia":"i-am-ai.png","mbt":"mujer-borde-tiempo.png","mk":"mankind.png",
 "op":"oficina-premoniciones.png","pa":"parentesco.png","rc":"revuelta-copistas.png","sa":"secuestros-americanos.png",
 "uc":"ultimo-contrato.png","vivo":"el-vivo.png","personotecnia":"personotecnia.png"}
def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",s).strip("-")
def pdf(html, out):
    subprocess.run(["google-chrome","--headless","--no-sandbox","--no-pdf-header-footer",f"--print-to-pdf={out}",f"file://{html}"],capture_output=True,timeout=90)
def card(code, f):
    soup = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
    t = lambda sel: (soup.select_one(sel).get_text(" ", strip=True) if soup.select_one(sel) else "")
    title = t("h1"); d = DST / slug(title); d.mkdir(parents=True, exist_ok=True)
    img = soup.select_one(".hero img")["src"]; shutil.copy(SRC/img, d/("portada"+Path(img).suffix))
    shutil.copy(SRC/PNG[code], d/"ficha.png"); shutil.copy(f, d/"ficha.html")
    shutil.copy(SRC/img, d/img)  # para que ficha.html siga viendo su portada
    pdf(d/"ficha.html", d/"ficha.pdf")
    secs = []
    for c in soup.select(".card"):
        h = c.find("h3"); 
        if not h: continue
        h.extract(); sc = c.select_one(".score")
        score = sc.get_text(strip=True) if sc else None
        if sc: sc.extract()
        items = [li.get_text(" ", strip=True) for li in c.find_all("li")] or [p.get_text(" ", strip=True) for p in c.find_all("p")] or [c.get_text(" ", strip=True)]
        secs.append({"titulo": h.get_text(strip=True), "puntos": [i for i in items if i], **({"nota": score} if score else {})})
    stats = [{"valor": s.b.get_text(strip=True) if s.b else "", "texto": s.small.get_text(" ", strip=True) if s.small else ""} for s in soup.select(".stat")]
    book = {"titulo": title, "subtitulo": t(".sub"), "autor": t(".auth"),
            "etiquetas": [s.get_text(strip=True) for s in soup.select(".tags span")],
            "portada": "portada"+Path(img).suffix, "datos": stats, "secciones": secs,
            "descargas": {"ficha_png": "ficha.png", "ficha_pdf": "ficha.pdf"}}
    (d/"libro.json").write_text(json.dumps(book, ensure_ascii=False, indent=1), encoding="utf-8"); print("ok", d.name)
for code in PNG:
    card(code, SRC/("card.html" if code=="personotecnia" else f"card-{code}.html"))
# Subrayados (Talentos): se guardan los datos y el txt literal tal cual
s = json.loads((SRC/"subrayados-talentos.json").read_text(encoding="utf-8"))
d = DST / slug(s["title"]); d.mkdir(parents=True, exist_ok=True)
shutil.copy(SRC/s["cover"], d/"portada.jpg"); shutil.copy(SRC/"subrayados-talentos-literal.txt", d/"citas.txt")
shutil.copy(SRC/"subrayados-talentos.png", d/"subrayados.png"); shutil.copy(SRC/"subrayados-talentos.pdf", d/"subrayados.pdf")
book = {"titulo": s["title"], "subtitulo": s["meta"], "autor": s["author"], "etiquetas": s.get("you_chips", []),
        "portada": "portada.jpg", "datos": [], "secciones": [{"titulo": "Lo que subrayas", "puntos": [s["you_text"]]}],
        "descargas": {"subrayados_png": "subrayados.png", "subrayados_pdf": "subrayados.pdf"},
        "subrayados": {"archivo_citas": "citas.txt", "nucleo": s["center"], "nucleo_sub": s["center_sub"],
            "hilo": s["flow"], "favorita": s["favorite"], "ramas": s["branches"], "pie": s["foot"]}}
(d/"libro.json").write_text(json.dumps(book, ensure_ascii=False, indent=1), encoding="utf-8"); print("ok", d.name)

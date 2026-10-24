"""Importa/actualiza un libro de subrayados de BookBot. Uso: python3 herramientas/importar_subrayados.py <nombre>  (p.ej. sembrador)
Lee /workspace/bookbot/subrayados-<nombre>.{json,png,pdf} y subrayados-<nombre>-literal.txt."""
import json, re, shutil, sys, unicodedata
from pathlib import Path
SRC = Path("/workspace/bookbot"); n = sys.argv[1]
DST = Path(__file__).resolve().parent.parent / "libros"
slug = lambda s: re.sub(r"[^a-z0-9]+","-",unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()).strip("-")
s = json.loads((SRC/f"subrayados-{n}.json").read_text(encoding="utf-8"))
d = DST/slug(s["title"]); d.mkdir(parents=True, exist_ok=True)
ext = Path(s["cover"]).suffix; shutil.copy(SRC/s["cover"], d/("portada"+ext))
shutil.copy(SRC/f"subrayados-{n}-literal.txt", d/"citas.txt")
shutil.copy(SRC/f"subrayados-{n}.png", d/"subrayados.png"); shutil.copy(SRC/f"subrayados-{n}.pdf", d/"subrayados.pdf")
obras = []
if s.get("works"):
    (d/"obras").mkdir(exist_ok=True)
    for i, w in enumerate(s["works"]["items"]):
        dst = ""
        if w.get("cover") and (SRC/w["cover"]).is_file():
            c = Path(w["cover"]); dst = f"obras/{i:02d}{c.suffix}"; shutil.copy(SRC/c, d/dst)
        obras.append({**w, "cover": dst})
book = {"titulo": s["title"], "subtitulo": s["meta"], "autor": s["author"], "etiquetas": s.get("you_chips", []),
 "portada": "portada"+ext, "datos": [], "secciones": [{"titulo": "Lo que subrayas", "puntos": [s["you_text"]]}],
 "descargas": {"subrayados_png": "subrayados.png", "subrayados_pdf": "subrayados.pdf"},
 "subrayados": {"archivo_citas": "citas.txt", "nucleo": s["center"], "nucleo_sub": s["center_sub"], "hilo": s["flow"],
   "favorita": int(s["favorite"]), "ramas": s["branches"], "pie": s["foot"]},
 **({"obras": {"titulo": s["works"]["title"], "nota": s["works"].get("note",""), "items": obras}} if obras else {})}
(d/"libro.json").write_text(json.dumps(book, ensure_ascii=False, indent=1), encoding="utf-8"); print("ok", d.name)

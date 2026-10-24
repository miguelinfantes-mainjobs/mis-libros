"""Construye la web estática en docs/ a partir de libros/<id>/libro.json.
Añadir un libro: crea libros/<id>/ con libro.json (+ portada, PNG/PDF) y ejecuta: python3 build.py
Citas: se leen de 'archivo_citas' (líneas 'N. texto') y se insertan LITERALES; el build falla si alguna no aparece idéntica."""
import json, re, shutil, html, sys
from pathlib import Path
R = Path(__file__).resolve().parent; L = R/"libros"; D = R/"docs"
E = lambda s: html.escape(str(s), quote=True)
MARCA = re.compile(r"\s+\[FAVORITA[^\]]*\]\s*$")  # anotación interna, no forma parte de la cita
def citas(p):
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(\d+)\. (.*)$", line)
        if m: out[int(m[1])] = MARCA.sub("", m[2])
    return out
CSS = (R/"plantilla"/"estilo.css").read_text(encoding="utf-8"); JS = (R/"plantilla"/"mapa.js").read_text(encoding="utf-8")
def page(title, body, depth):
    up = "../"*depth
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title><link rel="stylesheet" href="{up}estilo.css"></head><body><div class="wrap">{body}</div><script src="{up}mapa.js"></script></body></html>'
def nodo(label, hijos, cls="", abierto=False, extra=""):
    if not hijos: return f'<li><div class="hoja {cls}">{label}</div></li>'
    return f'<li class="{"abierto" if abierto else ""}"><button class="nodo {cls}" aria-expanded="{str(abierto).lower()}">{label}<span class="n">{len(hijos)}</span></button><ul>{"".join(hijos)}</ul>{extra}</li>'
def build():
    if D.exists(): shutil.rmtree(D)
    D.mkdir(); (D/"estilo.css").write_text(CSS, encoding="utf-8"); (D/"mapa.js").write_text(JS, encoding="utf-8")
    libros, esperadas = [], {}
    for d in sorted(p for p in L.iterdir() if (p/"libro.json").exists()):
        b = json.loads((d/"libro.json").read_text(encoding="utf-8")); b["id"] = d.name
        shutil.copytree(d, D/"libros"/d.name); libros.append(b)
        hero = f'<a class="volver" href="../../index.html">← Todos los libros</a><div class="hero"><img src="{E(b["portada"])}" alt=""><div><h1>{E(b["titulo"])}</h1><div class="sub">{E(b["subtitulo"])}</div><div class="auth">{E(b["autor"])}</div><div class="tags">{"".join(f"<span>{E(t)}</span>" for t in b["etiquetas"])}</div></div></div>'
        desc = '<div class="desc">' + "".join(f'<a class="btn" href="{E(v)}" download>⬇ {E(k.replace("_"," ").replace("ficha","Ficha").replace("subrayados","Subrayados").upper() if False else ({"ficha_png":"Ficha PNG","ficha_pdf":"Ficha PDF","subrayados_png":"Subrayados PNG","subrayados_pdf":"Subrayados PDF"}.get(k,k)))}</a>' for k,v in b["descargas"].items()) + '</div>'
        # Mapa
        ramas = []
        s = b.get("subrayados")
        if s:
            cs = citas(d/s["archivo_citas"]); esperadas[d.name] = cs
            hilo = [h[0] for h in s["hilo"]]
            for r in s["ramas"]:
                qs = [nodo(f'<span class="cita{" fav" if q==s["favorita"] else ""}">{"★ " if q==s["favorita"] else ""}{E(cs[q])}</span>', []) for q in r["quotes"]]
                tag = f'<small>{E(r["tag"])}</small>'
                ramas.append(nodo(f'{E(r["title"])} {tag}', qs, "rama"+(" nucleo" if r["flow"] is None else "")))
            centro = f'{E(s["nucleo"])}'
            hilo_html = '<div class="hilo">' + '<span class="fl">→</span>'.join(f'<span class="paso"><b>{i+1}</b>{E(h[0])}<small>{E(h[1])}</small></span>' for i,h in enumerate(s["hilo"])) + '</div>'
            fav = f'<div class="favq"><div class="lab">★ Tu favorita</div><q>{E(cs[s["favorita"]])}</q></div>'
            tarjetas = hilo_html + fav + "".join(f'<section class="sec"><h2>{E(r["title"])} <small>{E(r["tag"])}</small></h2><div class="cols">' + "".join(f'<blockquote class="q{" fav" if q==s["favorita"] else ""}"><span class="num">{q}</span>{E(cs[q])}</blockquote>' for q in r["quotes"]) + '</div></section>' for r in s["ramas"])
        else:
            centro = E(b["titulo"]); hilo_html = ""
            tarjetas = '<div class="grid">' + "".join(f'<div class="stat"><b>{E(x["valor"])}</b><small>{E(x["texto"])}</small></div>' for x in b["datos"]) + '</div>' + "".join(f'<section class="card"><h3>{E(c["titulo"])}{f" · {E(c.get("nota"))}" if c.get("nota") else ""}</h3>' + "".join(f"<p>{E(p)}</p>" for p in c["puntos"]) + '</section>' for c in b["secciones"])
        for c in b["secciones"]:
            et = E(c["titulo"]) + (f' <small>{E(c["nota"])}</small>' if c.get("nota") else "")
            ramas.append(nodo(et, [nodo(f'<span class="txt">{E(p)}</span>', []) for p in c["puntos"]], "rama sec"))
        if b["datos"]:
            ramas.append(nodo("Datos", [nodo(f'<b>{E(x["valor"])}</b> <span class="txt">{E(x["texto"])}</span>', []) for x in b["datos"]], "rama sec"))
        o = b.get("obras"); obras_html = ""
        if o:
            def ob(w):
                img = f'<img src="{E(w["cover"])}" alt="">' if w.get("cover") else ""
                url = f'<a href="{E(w["url"])}" target="_blank" rel="noopener">{E(w.get("url_label") or "Ver")}</a>' if w.get("url") else ""
                return f'<div class="obra">{img}<div><b>{E(w["title"])}</b> <span class="est">{E(w.get("me",""))}</span><small>{E(w.get("orig",""))} · {E(w.get("es",""))}</small><p>{E(w.get("line",""))}</p>{url}</div></div>'
            ramas.append(nodo(E(o["titulo"]), [f'<li>{ob(w)}</li>' for w in o["items"]], "rama sec"))
            obras_html = f'<section class="sec"><h2>{E(o["titulo"])}</h2><div class="obras">' + "".join(ob(w) for w in o["items"]) + f'</div><p class="nota">{E(o["nota"])}</p></section>'
        if s: tarjetas += obras_html
        mapa = f'<div class="controles"><button data-accion="abrir">Abrir todo</button><button data-accion="cerrar">Cerrar todo</button></div><ul class="mapa"><li class="abierto raiz"><button class="nodo centro" aria-expanded="true">{centro}</button><ul>{"".join(ramas)}</ul></li></ul>'
        body = hero + desc + '<div class="pestanas"><button class="activa" data-vista="mapa">🧠 Mapa</button><button data-vista="tarjetas">🃏 Tarjetas</button></div>' + f'<div class="vista" id="v-mapa">{hilo_html if s else ""}{mapa}</div><div class="vista oculto" id="v-tarjetas">{tarjetas}</div>'
        (D/"libros"/d.name/"index.html").write_text(page(b["titulo"], body, 2), encoding="utf-8")
    idx = '<h1 class="tit">Mis libros</h1><p class="lead">Fichas y mapas de subrayados de Miguel</p><div class="estante">' + "".join(f'<a class="libro" href="libros/{b["id"]}/index.html"><img src="libros/{b["id"]}/{E(b["portada"])}" alt=""><b>{E(b["titulo"])}</b><small>{E(b["autor"])}</small>{"<span class=chip>Subrayados</span>" if b.get("subrayados") else ""}</a>' for b in libros) + '</div>'
    (D/"index.html").write_text(page("Mis libros", idx, 0), encoding="utf-8"); (D/".nojekyll").write_text("")
    # Verificación de citas literales
    fallos = 0
    for lid, cs in esperadas.items():
        txt = html.unescape((D/"libros"/lid/"index.html").read_text(encoding="utf-8"))
        for n, q in cs.items():
            if q not in txt: fallos += 1; print(f"FALTA cita {n} en {lid}")
        print(f"{lid}: {len(cs)-fallos}/{len(cs)} citas literales OK")
    print(f"{len(libros)} libros generados en {D}")
    if fallos: sys.exit(1)
build()

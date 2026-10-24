"""Variante «bygga» (manual de instrucciones tipo bento) de un libro de subrayados.
Se activa creando libros/<id>/bygga.json ({"escenas": [...], "ideas": [...]} opcional). Genera docs/libros/<id>/bygga/index.html."""
import html, json, math, shutil
from pathlib import Path
E = lambda s: html.escape(str(s), quote=True)
C, S = math.cos(math.pi/6), math.sin(math.pi/6)
PTS = []
def P(x, y, z, k=22, ox=200, oy=150):
    PTS.append((ox + (x - y)*C*k, oy + (x + y)*S*k - z*k)); return (ox + (x - y)*C*k, oy + (x + y)*S*k - z*k)
def poly(pts, fill="#fff"): return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a,b in pts)}" fill="{fill}"/>'
def caja(x, y, z, w, d, h, top="#fff"):
    v = lambda a,b,c: P(x+a, y+b, z+c)
    return (poly([v(0,0,h),v(w,0,h),v(w,d,h),v(0,d,h)], top) +
            poly([v(w,0,0),v(w,d,0),v(w,d,h),v(w,0,h)]) + poly([v(0,d,0),v(w,d,0),v(w,d,h),v(0,d,h)]))
def linea(a, b): (x1,y1),(x2,y2) = P(*a), P(*b); return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
def circ(p, r, fill="#fff"): x,y = P(*p); return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>'
def suelo():
    n = len(PTS); r = poly([P(-1.8,-1.8,0),P(4,-1.8,0),P(4,4,0),P(-1.8,4,0)], "none"); del PTS[n:]; return r
Y = "#FFCC00"
ESCENAS = {
 "libros": lambda: suelo()+caja(-1,-1,0,4,3,.6)+caja(-.6,-.8,.6,3.4,2.6,.5,Y)+caja(-1,-1,1.1,4,3,.6)+caja(.2,-.4,1.7,2.4,1.8,.08)+linea((1.4,-.4,1.78),(1.4,1.4,1.78)),
 "idea": lambda: suelo()+caja(0,0,0,2,2,1)+caja(.6,.6,1,.8,.8,.6)+circ((1,1,3.1),30,Y)+"".join(linea((1+1.6*math.cos(a),1+1.6*math.sin(a),3.1),(1+2.3*math.cos(a),1+2.3*math.sin(a),3.1)) for a in [i*math.pi/4 for i in range(8)]),
 "escritorio": lambda: suelo()+caja(-1,0,0,.3,.3,1.6)+caja(3,0,0,.3,.3,1.6)+caja(-1,2,0,.3,.3,1.6)+caja(3,2,0,.3,.3,1.6)+caja(-1.2,-.2,1.6,4.7,2.8,.25)+caja(0,.5,1.85,1.8,1.3,.05,Y)+caja(2.3,.6,1.85,.15,1.2,.15),
 "escalera": lambda: suelo()+"".join(caja(0,i*.9,0,2.5,.9,3.2-i*.8) for i in range(4))+caja(.9,3.4,0,.3,.3,.9)+circ((1.05,3.55,1.25),5,Y),
 "dos": lambda: suelo()+caja(-1.5,0,0,1.6,1.6,1.6)+caja(2,0,0,1.6,1.6,1.6,Y)+circ((.9,.8,2.6),26,"none")+linea((.4,1.3,2.0),(-.1,1.8,1.4)),
 "robot": lambda: suelo()+caja(.3,.3,0,.4,.4,1)+caja(1.3,.3,0,.4,.4,1)+caja(0,0,1,2,1.2,1.6)+caja(.4,.1,2.6,1.2,1,1,Y)+linea((1,.6,3.6),(1,.6,4.3))+circ((1,.6,4.4),5,"#000"),
 "marte": lambda: suelo()+circ((2,2,1.6),48,"#fff")+caja(-1.5,-1,0,.8,.8,2.2)+poly([P(-1.5,-1,2.2),P(-.7,-1,2.2),P(-1.1,-.6,3.2)])+linea((3,-1,0),(3,-1,2.6))+poly([P(3,-1,2.6),P(3,.2,2.3),P(3,-1,2.0)],Y),
 "fin": lambda: suelo()+caja(0,0,0,2.4,2.4,.6)+caja(.4,.4,.6,1.6,1.6,.6)+caja(.8,.8,1.2,.8,.8,.6,Y)+linea((1.2,1.2,1.8),(1.2,1.2,3))+poly([P(1.2,1.2,3),P(1.2,2.2,2.7),P(1.2,1.2,2.4)],Y),
}
def svg(nombre, sid):
    PTS.clear(); g = ESCENAS[nombre]()
    xs, ys = [p[0] for p in PTS], [p[1] for p in PTS]; pad = 60
    x0, y0, w, h = min(xs)-pad, min(ys)-pad, max(xs)-min(xs)+2*pad, max(ys)-min(ys)+2*pad
    svg.centro = ((min(xs)+max(xs))/2, min(ys) + (max(ys)-min(ys))*0.38)
    return f'<svg viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}" class="iso" role="img" aria-hidden="true"><g id="{sid}" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">{g}</g></svg>'
def lupa(sid, etiqueta, fav=False, cx=200, cy=110):
    return (f'<div class="lupa{" fav" if fav else ""}"><svg viewBox="0 0 120 120"><defs><clipPath id="c{sid}"><circle cx="60" cy="60" r="56"/></clipPath></defs>'
            f'<g clip-path="url(#c{sid})"><rect width="120" height="120" fill="#fff"/><use href="#{sid}" transform="translate({60-cx*2.2} {60-cy*2.2}) scale(2.2)"/></g>'
            f'<circle cx="60" cy="60" r="56" fill="none" stroke="#111" stroke-width="2"/></svg><span>{E(etiqueta)}</span></div>')
def generar(d, b, cs, notas, out, raiz):
    cfg = json.loads((d/"bygga.json").read_text(encoding="utf-8")); s = b["subrayados"]; fav = s["favorita"]
    L_ = lambda q: q if isinstance(q, list) else [q]
    ramas = s["ramas"]; obras = b.get("obras"); N = len(ramas) + 1
    out.mkdir(parents=True, exist_ok=True)
    (out/"fuentes").mkdir(exist_ok=True); shutil.copy(raiz/"plantilla"/"fuentes"/"Inter.ttf", out/"fuentes"/"Inter.ttf")
    shutil.copy(raiz/"plantilla"/"fuentes"/"LICENCIA-Inter.txt", out/"fuentes"/"LICENCIA-Inter.txt")
    pasos = []
    for i, r in enumerate(ramas):
        sid = f"e{i}"; esc = cfg["escenas"][i]; tiene_fav = any(fav in L_(q) for q in r["quotes"])
        items = "".join(
            f'<li{" class=fav id=favorita" if fav in L_(q) else ""}><span class="pnum">nº {"+".join(map(str, L_(q)))}</span>'
            + "".join(f'<q>{E(cs[k])}</q>' for k in L_(q))
            + "".join(f'<span class="nota"><b>Tu nota</b>{E(notas[k])}</span>' for k in L_(q) if k in notas)
            + ('<span class="favtag">★ Tu favorita</span>' if fav in L_(q) else "") + '</li>' for q in r["quotes"])
        ilu = svg(esc, sid); cx, cy = svg.centro
        lupas = lupa(sid, f"★ Favorita · nº {fav}" if tiene_fav else r.get("label", r["tag"]).capitalize(), tiene_fav, cx, cy)
        pasos.append(f'''<section class="paso" data-i="{i}"><div class="izq tarjeta"><div class="num">{i+1:02d}</div><div class="kick">{E(r["tag"])}</div>{ilu}{lupas}</div>
<div class="der"><div class="tarjeta"><div class="kick">Paso {i+1}</div><h2>{E(r["title"])}</h2><p class="idea">{E(r.get("label",""))}</p></div>
<div class="tarjeta"><h3>Necesitas <span class="cuenta">{sum(len(L_(q)) for q in r["quotes"])}</span></h3><ul class="nec">{items}</ul></div>
<button class="pill negra siguiente">Hecho, siguiente →</button></div></section>''')
    bento = ""
    if obras:
        bento = '<div class="bento">' + "".join(f'<a class="tarjeta obra{" grande" if j==0 else ""}" href="{E(w.get("url",""))}" target="_blank" rel="noopener">' + (f'<img src="../{E(w["cover"])}" alt="">' if w.get("cover") else "") + f'<b>{E(w["title"])}</b><small>{E(w.get("es",""))}</small><span class="est">{E(w.get("me",""))}</span></a>' for j, w in enumerate(obras["items"])) + '</div>'
    pasos.append(f'''<section class="paso final" data-i="{N-1}"><div class="izq tarjeta"><div class="num">{N:02d}</div><div class="kick">Terminado</div>{svg("fin","efin")}</div>
<div class="der"><div class="tarjeta"><div class="kick">Paso {N}</div><h2>Listo.</h2><p class="idea">{E(b["secciones"][0]["puntos"][0]) if b.get("secciones") else ""}</p>
<div class="desc"><a class="pill negra" href="../subrayados.png" download>⬇ PNG</a> <a class="pill negra" href="../subrayados.pdf" download>⬇ PDF</a> <a class="pill" href="../index.html">Ver mapa clásico</a></div></div></div>
<div class="ancho"><h2 class="sub">{E(obras["titulo"]) if obras else ""}</h2>{bento}</div></section>''')
    pag = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(b["titulo"])} · manual</title><style>{(raiz/"plantilla"/"bygga.css").read_text(encoding="utf-8")}</style></head><body>
<header class="barra"><a href="../index.html" class="atras">←</a><div class="tt"><b>{E(b["titulo"])}</b> <span>{E(b["autor"])}</span></div><div class="prog"><span id="pasoN">Paso 1 de {N}</span><div class="pista"><i id="pbar"></i></div></div></header>
<div class="portada tarjeta"><img src="../{E(b["portada"])}" alt=""><div><div class="kick">Manual de instrucciones · {len(cs)} subrayados</div><h1>{E(s["nucleo"])}</h1></div></div>
<main id="pasos">{"".join(pasos)}</main>
<nav class="flot"><button id="ant" aria-label="Anterior">←</button><span id="pn">1/{N}</span><button id="sig" aria-label="Siguiente">→</button></nav>
<div id="confeti" aria-hidden="true"></div>
<script>{(raiz/"plantilla"/"bygga.js").read_text(encoding="utf-8")}</script></body></html>'''
    (out/"index.html").write_text(pag, encoding="utf-8")

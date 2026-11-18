#!/usr/bin/env python3
"""Genera il sito delle associazioni a partire dai file in _dati/.

Uso: python3 _strumenti/genera.py   (dalla cartella principale del sito)

_dati/associazioni.json   elenco delle associazioni (una scheda per ciascuna)
_dati/notizie/*.json      una notizia per file: AAAA-MM-GG-titolo.json
_dati/impostazioni.json   prototipo sì/no

Il programma riscrive index.html, come-partecipare.html e le cartelle
delle associazioni. Non va modificato a mano nessun file .html.
"""
import json, html, re, shutil
from pathlib import Path
from datetime import date

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "_dati"
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]
SITO = "https://associazioni.comune.castellanza.va.it/"
COMUNE = "https://www.comune.castellanza.va.it/"
NOME_SITO = "Notizie dalle associazioni"

e = html.escape


def data_it(s):
    d = date.fromisoformat(s)
    g = "1°" if d.day == 1 else str(d.day)
    return f"{g} {MESI[d.month - 1]} {d.year}"


def carica():
    imp = json.loads((DATI / "impostazioni.json").read_text(encoding="utf-8"))
    ass = json.loads((DATI / "associazioni.json").read_text(encoding="utf-8"))
    notizie = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((DATI / "notizie").glob("*.json"))]
    per = {a["slug"]: [] for a in ass}
    for n in notizie:
        if n["associazione"] not in per:
            raise SystemExit(f"Notizia {n['slug']}: associazione sconosciuta {n['associazione']}")
        per[n["associazione"]].append(n)
    for lista in per.values():
        lista.sort(key=lambda n: n["data"], reverse=True)
    ass.sort(key=lambda a: (not a.get("esempio"), a["nome"].lower()))
    return imp, ass, per


# ---------------------------------------------------------------- pezzi comuni

WAI = """<!-- Web Analytics Italia (Matomo) - sito "Siti tematici Comune", codice valido per tutti i sottodomini tematici.
     Conta le visite solo sul dominio del Comune, non nelle anteprime. -->
<script>
if (/\\.comune\\.castellanza\\.va\\.it$/.test(location.hostname)) {
  var _paq = window._paq = window._paq || [];
  _paq.push(['disableCookies']);
  _paq.push(['setDocumentTitle', document.domain + ' / ' + document.title]);
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u="https://ingestion.webanalytics.italia.it/";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '47578']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  })();
}
</script>
<!-- End Matomo Code -->"""


def pagina(rel, titolo, descrizione, corpo, imp, briciole=None, home=False):
    bozza = ""
    if imp.get("prototipo"):
        bozza = ('<div class="avviso-prototipo" role="note"><strong>Prototipo per la valutazione interna.</strong> '
                 "I dati delle associazioni vengono dal sito del Comune; le notizie dell'«Associazione di esempio» sono dimostrative.</div>")
    nav = ""
    if briciole:
        voci = "".join(
            f'<li><a href="{e(h)}">{e(t)}</a></li>' if h else f'<li aria-current="page">{e(t)}</li>'
            for t, h in briciole)
        nav = f'<nav class="briciole" aria-label="Percorso"><ol>{voci}</ol></nav>'
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)}</title>
<meta name="description" content="{e(descrizione)}">
<link rel="stylesheet" href="{rel}stile.css">
<link rel="icon" href="{rel}img/loghi/stemma-castellanza.png">
{WAI}
</head>
<body>
<a class="salta" href="#contenuto">Vai al contenuto</a>
{bozza}
<div class="fascia-ente"><div class="contenitore"><a href="{COMUNE}">Città di Castellanza</a></div></div>
<header class="testata"><div class="contenitore">
  <a class="marchio" href="{rel}index.html">
    <img src="{rel}img/loghi/stemma-castellanza.png" alt="" width="44" height="62">
    <div><span class="ente">Città di Castellanza</span>{"<h1 class=\"nome-sito\">" if home else "<span class=\"nome-sito\">"}{NOME_SITO}{"</h1>" if home else "</span>"}</div>
  </a>
  <nav class="menu" aria-label="Menu principale"><ul>
    <li><a href="{rel}index.html#notizie">Le news</a></li>
    <li><a href="{rel}index.html#associazioni">Le associazioni</a></li>
    <li><a href="{rel}come-partecipare.html">Come partecipare</a></li>
  </ul></nav>
</div></header>
<main id="contenuto">
<div class="contenitore">{nav}</div>
{corpo}
</main>
<footer class="piede"><div class="contenitore">
  <div class="ente-piede">
    <img src="{rel}img/loghi/stemma-castellanza.png" alt="Stemma della Città di Castellanza" width="52" height="73">
    <div>
      <p><strong>Città di Castellanza</strong></p>
      <p>Viale Rimembranze 4, 21053 Castellanza (VA)</p>
      <p><a href="{COMUNE}amministrazione/uffici/">Contatti degli uffici comunali</a></p>
    </div>
  </div>
  <div class="link-piede">
    <p><a href="{COMUNE}">Sito del Comune</a></p>
    <p><a href="{rel}come-partecipare.html">Sei un'associazione? Come partecipare</a></p>
    <p><a href="{COMUNE}info-e-contatti/privacy/privacy/">Informativa privacy</a> · <a href="{COMUNE}info-e-contatti/privacy/cookies/">Cookie</a> · <a href="{COMUNE}info-e-contatti/privacy/note-legali/">Note legali</a></p>
  </div>
  <p class="nota-cookie">Questo sito non usa cookie. Le visite sono conteggiate in forma anonima con Web Analytics Italia, la piattaforma statistica di AgID per la pubblica amministrazione. I contenuti delle notizie sono forniti dalle associazioni e pubblicati a cura dell'Ufficio Stampa e Comunicazione del Comune.</p>
</div></footer>
</body>
</html>
"""


def avatar(a, rel, classe="avatar"):
    if a.get("logo"):
        return f'<span class="{classe} con-logo"><img src="{rel}{e(a["logo"])}" alt=""></span>'
    lunga = " lunga" if len(a["sigla"]) > 3 else ""
    return f'<span class="{classe}{lunga}" aria-hidden="true">{e(a["sigla"])}</span>'


def file_notizia(n):
    return f'{n["data"]}-{n["slug"]}.html'


def articolo(n, rel, livello="h2"):
    parti = [f'<article class="notizia">',
             f'<p class="data-notizia"><time datetime="{n["data"]}">{data_it(n["data"])}</time></p>',
             f'<{livello} class="titolo-notizia">{e(n["titolo"])}</{livello}>',
             f'<p class="sommario">{e(n["sommario"])}</p>']
    if n.get("immagine"):
        parti.append(f'<figure class="foto"><img src="{rel}{e(n["immagine"]["file"])}" alt="{e(n["immagine"].get("alt", ""))}" width="1200" height="675">'
                     + (f'<figcaption>{e(n["immagine"]["didascalia"])}</figcaption>' if n["immagine"].get("didascalia") else "")
                     + '</figure>')
    if n.get("evento"):
        ev = n["evento"]
        righe = "".join(f"<dt>{k}</dt><dd>{e(ev[c])}</dd>" for k, c in (("Quando", "quando"), ("Dove", "dove")) if ev.get(c))
        parti.append(f'<dl class="evento">{righe}</dl>')
    parti.append('<div class="testo">' + "".join(f"<p>{e(p)}</p>" for p in n["testo"]) + "</div>")
    parti.append("</article>")
    return "\n".join(parti)


def elenco_notizie(lista, corrente=None):
    voci = []
    for n in lista:
        if corrente and n["slug"] == corrente["slug"] and n["data"] == corrente["data"]:
            continue
        voci.append(f'<li><time datetime="{n["data"]}">{data_it(n["data"])}</time>'
                    f'<a href="{file_notizia(n)}">{e(n["titolo"])}</a></li>')
    return f'<ul class="archivio">{"".join(voci)}</ul>' if voci else ""


def scheda_contatti(a):
    c = a.get("contatti", {})
    righe = []
    if c.get("referente"): righe.append(("Referente", e(c["referente"])))
    if c.get("sede"): righe.append(("Sede", e(c["sede"])))
    if c.get("email"): righe.append(("Email", f'<a href="mailto:{e(c["email"])}">{e(c["email"])}</a>'))
    if c.get("telefono"): righe.append(("Telefono", e(c["telefono"])))
    if c.get("sito"): righe.append(("Sito", f'<a href="{e(c["sito"])}">{e(re.sub(r"^https?://", "", c["sito"]).rstrip("/"))}</a>'))
    social = [f'<a href="{e(c[s])}">{t}</a>' for s, t in (("facebook", "Facebook"), ("instagram", "Instagram")) if c.get(s)]
    if social: righe.append(("Social", " · ".join(social)))
    if a.get("scheda_comune"): righe.append(("Sul sito del Comune", f'<a href="{e(a["scheda_comune"])}">Scheda dell\'associazione</a>'))
    if not righe:
        return ""
    return ('<aside class="contatti" aria-labelledby="t-contatti"><h2 id="t-contatti">Contatti</h2><dl>'
            + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in righe) + "</dl></aside>")


# ---------------------------------------------------------------- pagine

def home(imp, ass, per):
    nome_di = {x["slug"]: x for x in ass}
    tutte = sorted((n for lista in per.values() for n in lista), key=lambda n: n["data"], reverse=True)
    voci = []
    for n in tutte:
        a = nome_di[n["associazione"]]
        voci.append(f'''<li><article class="lancio">
  <p class="fonte"><a href="{a["slug"]}/index.html">{e(a["nome"])}</a> · <time datetime="{n["data"]}">{data_it(n["data"])}</time></p>
  <h3><a href="{a["slug"]}/{file_notizia(n)}">{e(n["titolo"])}</a></h3>
  <p class="sommario-lancio">{e(n["sommario"])}</p>
</article></li>''')
    notizie = (f'<ol class="lanci">{"".join(voci)}</ol>' if voci else '<p class="vuoto">Non ci sono ancora notizie pubblicate.</p>')
    blocchi = "".join(
        f'<li><a class="box" href="{a["slug"]}/index.html">{avatar(a, "", "avatar piccolo")}<span>{e(a["nome"])}</span></a></li>'
        for a in ass)
    corpo = f'''<section class="apertura"><div class="contenitore">
  <p class="introduzione">Le associazioni che animano la vita di Castellanza raccontano qui le loro attività, gli appuntamenti e le iniziative aperte ai cittadini.</p>
</div></section>
<section class="notizie" id="notizie" aria-labelledby="t-notizie"><div class="contenitore">
  <h2 id="t-notizie" class="titolo-sezione">Tutte le news</h2>
  {notizie}
</div></section>
<section class="indice-ass" id="associazioni" aria-labelledby="t-ass"><div class="contenitore">
  <h2 id="t-ass" class="titolo-sezione">Le associazioni</h2>
  <ul class="boxes">{blocchi}</ul>
</div></section>
<section class="invito"><div class="contenitore">
  <h2>Fai parte di un'associazione di Castellanza?</h2>
  <p>Puoi segnalare all'Ufficio Stampa e Comunicazione del Comune le notizie e gli appuntamenti da pubblicare su questo sito.</p>
  <p><a class="pulsante" href="come-partecipare.html">Scopri come partecipare</a></p>
</div></section>'''
    return pagina("", f"{NOME_SITO} | Città di Castellanza",
                  "Le notizie e gli appuntamenti delle associazioni di Castellanza.", corpo, imp, home=True)


def pagina_associazione(imp, a, lista):
    rel = "../"
    if lista:
        ult = lista[0]
        principale = (f'<section class="ultima-notizia" aria-label="Ultima notizia"><p class="etichetta">Ultima notizia</p>'
                      f'{articolo(ult, rel)}<p class="link-notizia"><a href="{file_notizia(ult)}">Pagina della notizia</a></p></section>')
        altre = elenco_notizie(lista[1:])
        archivio = (f'<section class="altre" aria-labelledby="t-altre"><h2 id="t-altre">Notizie precedenti</h2>{altre}</section>' if altre else "")
    else:
        principale = '<p class="vuoto">Questa associazione non ha ancora pubblicato notizie.</p>'
        archivio = ""
    corpo = f'''<section class="intestazione-ass"><div class="contenitore">
  {avatar(a, rel, "avatar grande")}
  <div><p class="ambito">{e(a["ambito"])}</p><h1>{e(a["nome"])}</h1><p class="descrizione">{e(a["descrizione"])}</p></div>
</div></section>
<div class="contenitore colonne">
  <div class="principale">{principale}{archivio}</div>
  {scheda_contatti(a)}
</div>'''
    return pagina(rel, f'{a["nome"]} | {NOME_SITO}', a["descrizione"], corpo, imp,
                  [("Home", rel + "index.html"), (a["nome"], None)])


def pagina_notizia(imp, a, n, lista):
    rel = "../"
    altre = elenco_notizie(lista, corrente=n)
    corpo = f'''<div class="contenitore colonne">
  <div class="principale">
    <p class="di-chi">{avatar(a, rel, "avatar piccolo")}<a href="index.html">{e(a["nome"])}</a></p>
    {articolo(n, rel, "h1")}
    {f'<section class="altre" aria-labelledby="t-altre"><h2 id="t-altre">Altre notizie di questa associazione</h2>{altre}</section>' if altre else ""}
  </div>
  {scheda_contatti(a)}
</div>'''
    return pagina(rel, f'{n["titolo"]} | {NOME_SITO}', n["sommario"], corpo, imp,
                  [("Home", rel + "index.html"), (a["nome"], "index.html"), (n["titolo"], None)])


def come_partecipare(imp):
    corpo = '''<div class="contenitore stretta">
<h1>Come partecipare</h1>
<div class="testo">
<p>Questo sito raccoglie le notizie delle associazioni attive a Castellanza. Ogni associazione ha una propria pagina con una breve presentazione, i contatti e l'archivio delle notizie pubblicate.</p>
<p>Per segnalare una notizia o un appuntamento, l'associazione compila il modulo online. L'Ufficio Stampa e Comunicazione del Comune riceve la segnalazione, la verifica e cura la pubblicazione.</p>
<p class="segnaposto">Qui andranno il collegamento al modulo e le regole di pubblicazione.</p>
</div>
</div>'''
    return pagina("", f"Come partecipare | {NOME_SITO}",
                  "Come segnalare le notizie delle associazioni di Castellanza.", corpo, imp,
                  [("Home", "index.html"), ("Come partecipare", None)])


def main():
    imp, ass, per = carica()
    for a in ass:  # ripulisce e rigenera le cartelle delle associazioni
        d = RADICE / a["slug"]
        if d.exists():
            shutil.rmtree(d)
        d.mkdir()
        (d / "index.html").write_text(pagina_associazione(imp, a, per[a["slug"]]), encoding="utf-8")
        for n in per[a["slug"]]:
            (d / file_notizia(n)).write_text(pagina_notizia(imp, a, n, per[a["slug"]]), encoding="utf-8")
    (RADICE / "index.html").write_text(home(imp, ass, per), encoding="utf-8")
    (RADICE / "come-partecipare.html").write_text(come_partecipare(imp), encoding="utf-8")
    tot = sum(len(v) for v in per.values())
    print(f"Generate {len(ass)} associazioni e {tot} notizie.")


if __name__ == "__main__":
    main()

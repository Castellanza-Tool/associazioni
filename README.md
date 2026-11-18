# Associazioni del territorio – Città di Castellanza

Sito pubblicato con GitHub Pages su associazioni.comune.castellanza.va.it (file CNAME).

Le pagine .html si generano dai dati, non si modificano a mano:

- `_dati/associazioni.json` – schede delle associazioni
- `_dati/notizie/AAAA-MM-GG-titolo.json` – una notizia per file
- `_dati/impostazioni.json` – `"prototipo": true` mostra la fascia gialla di prova
- `img/notizie/` – foto delle notizie, già compresse (circa 150 KB)

Dopo ogni modifica: `python3 _strumenti/genera.py`, poi commit e push.

Statistiche: Web Analytics Italia, sito "Siti tematici Comune" (ID 47578), senza cookie.

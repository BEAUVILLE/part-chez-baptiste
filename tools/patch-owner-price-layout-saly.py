from pathlib import Path

path=Path('gestion.html')
s=path.read_text(encoding='utf-8')
marker='DIGIY SALY OWNER PRICE LAYOUT V3'
if marker in s:
    print('Layout propriétaire V3 déjà présent.')
    raise SystemExit(0)

old='.day{aspect-ratio:1/1;border:1px solid transparent;border-radius:12px;background:#fff;display:grid;place-items:center;font-weight:900;cursor:pointer;position:relative;color:#13231c}'
new='.day{aspect-ratio:1/1;border:1px solid transparent;border-radius:12px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-weight:900;cursor:pointer;position:relative;color:#13231c}/* DIGIY SALY OWNER PRICE LAYOUT V3 */'
if old not in s:
    raise SystemExit('CSS .day propriétaire Saly attendu introuvable')
s=s.replace(old,new,1)
path.write_text(s,encoding='utf-8')
print('Layout propriétaire V3 posé : jour et tarif séparés.')

from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')
marker='DIGIY SALY SPECIAL PRICE RANGE V3'
if marker in s:
    print('Logique prix spécial V3 déjà présente.')
    raise SystemExit(0)

old='''    function estimatePrice(n){
      if(!n) return 0;
      // Un prix spécial saisi par le propriétaire devient prioritaire pour les nuits concernées.
      if(selectedStart && selectedEnd && MASTER_PRICES.size){
        let total=0;
        for(let d=new Date(selectedStart); d<selectedEnd; d=addDays(d,1)){
          total+=priceForIso(iso(d));
        }
        return total;
      }
      // Sans prix spécial, conserver les forfaits commerciaux Saly existants.
      let remaining=n,total=0;
      const months=Math.floor(remaining/30);total+=months*PRICE_MONTH;remaining%=30;
      const weeks=Math.floor(remaining/7);total+=weeks*PRICE_WEEK;remaining%=7;
      total+=remaining*PRICE_NIGHT;
      return total;
    }'''

new='''    // DIGIY SALY SPECIAL PRICE RANGE V3 — un prix spécial n'affecte que la période qui le contient.
    function estimatePrice(n){
      if(!n) return 0;
      if(selectedStart && selectedEnd){
        let nightlyTotal=0;
        let hasOverrideInStay=false;
        for(let d=new Date(selectedStart); d<selectedEnd; d=addDays(d,1)){
          const day=iso(d);
          if(MASTER_PRICES.has(day)) hasOverrideInStay=true;
          nightlyTotal+=priceForIso(day);
        }
        if(hasOverrideInStay) return nightlyTotal;
      }
      // Aucune date spéciale dans ce séjour : conserver exactement les forfaits Saly existants.
      let remaining=n,total=0;
      const months=Math.floor(remaining/30);total+=months*PRICE_MONTH;remaining%=30;
      const weeks=Math.floor(remaining/7);total+=weeks*PRICE_WEEK;remaining%=7;
      total+=remaining*PRICE_NIGHT;
      return total;
    }'''

if old not in s:
    raise SystemExit('estimatePrice V2 attendu introuvable')
s=s.replace(old,new,1)
path.write_text(s,encoding='utf-8')
print('Prix spécial limité à la période concernée ; forfaits semaine/mois préservés ailleurs.')

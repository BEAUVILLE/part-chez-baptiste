from pathlib import Path
import re

# CHEZ BAPTISTE SALY — raccordement au moteur MASTER LOC validé sur Sarlat.
# Le design Saly et les forfaits semaine/mois sont conservés.

index_path = Path('index.html')
owner_path = Path('gestion.html')
index = index_path.read_text(encoding='utf-8')
owner = owner_path.read_text(encoding='utf-8')

if 'DIGIY SALY MASTER LOC V2' not in index:
    old_constants = '''    const OWNER_WA = "221771342889";
    const MAX_GUESTS = 4;
    const PRICE_NIGHT = 30000;
    const PRICE_WEEK = 175000;
    const PRICE_MONTH = 550000;

    const SUPABASE_URL = "https://wesqmwjjtsefyjnluosj.supabase.co";
    const SUPABASE_KEY = "sb_publishable_tGHItRgeWDmGjnd0CK1DVQ_BIep4Ug3";
    const MASTER_UNIT_ID = "ae44152a-0e11-4c7e-8834-d5ff872b2fbd";
    const masterDb = window.supabase ? window.supabase.createClient(
      SUPABASE_URL,
      SUPABASE_KEY,
      {auth:{persistSession:false,autoRefreshToken:false,detectSessionInUrl:false}}
    ) : null;

    // Même source que la gestion propriétaire : absence de ligne = LIBRE.
    const MASTER_STATES = new Map();'''
    new_constants = '''    const OWNER_WA = "221771342889";
    const MAX_GUESTS = 4;
    let PRICE_NIGHT = 30000;
    const PRICE_WEEK = 175000;
    const PRICE_MONTH = 550000;

    const SUPABASE_URL = "https://wesqmwjjtsefyjnluosj.supabase.co";
    const SUPABASE_KEY = "sb_publishable_tGHItRgeWDmGjnd0CK1DVQ_BIep4Ug3";
    const MASTER_UNIT_ID = "ae44152a-0e11-4c7e-8834-d5ff872b2fbd";

    // DIGIY SALY MASTER LOC V2 — absence de ligne calendrier = LIBRE.
    // États + tarifs publics passent par REST natif du navigateur, sans dépendre du SDK/CDN.
    const MASTER_STATES = new Map();
    const MASTER_PRICES = new Map();'''
    if old_constants not in index:
        raise SystemExit('Bloc constantes public Saly introuvable')
    index = index.replace(old_constants, new_constants, 1)

    old_estimate = '''    function estimatePrice(n){
      let remaining=n,total=0;
      const months=Math.floor(remaining/30);total+=months*PRICE_MONTH;remaining%=30;
      const weeks=Math.floor(remaining/7);total+=weeks*PRICE_WEEK;remaining%=7;
      total+=remaining*PRICE_NIGHT;
      return total;
    }'''
    new_estimate = '''    function estimatePrice(n){
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
    if old_estimate not in index:
        raise SystemExit('Fonction estimatePrice public Saly introuvable')
    index = index.replace(old_estimate, new_estimate, 1)

    old_state = '''    function masterState(date){
      return MASTER_STATES.get(iso(date)) || "";
    }'''
    new_state = '''    function masterState(date){
      return MASTER_STATES.get(iso(date)) || "";
    }

    function priceForIso(day){
      const value = MASTER_PRICES.has(day) ? Number(MASTER_PRICES.get(day)) : Number(PRICE_NIGHT);
      return Number.isFinite(value) && value >= 0 ? value : Number(PRICE_NIGHT) || 0;
    }'''
    if old_state not in index:
        raise SystemExit('masterState public Saly introuvable')
    index = index.replace(old_state, new_state, 1)

    old_day = '''        html+=`<button class="${classes}" type="button" data-date="${iso(date)}" ${disabled?'disabled':''}>${d}</button>`;'''
    new_day = '''        const dateIso=iso(date);
        const priceHtml=!disabled ? `<small style="display:block;font-size:9px;line-height:1;font-weight:950;margin-top:2px;white-space:nowrap">${money(priceForIso(dateIso))}</small>` : '';
        html+=`<button class="${classes}" type="button" data-date="${dateIso}" ${disabled?'disabled':''}><span>${d}</span>${priceHtml}</button>`;'''
    if old_day not in index:
        raise SystemExit('Rendu jour public Saly introuvable')
    index = index.replace(old_day, new_day, 1)

    pattern = re.compile(r'''    async function loadMasterCalendar\(\)\{.*?\n    \}\n\n    let saved='fr';''', re.S)
    replacement = '''    function refreshPublicBasePrice(){
      const main=document.querySelector('.main-price');
      if(main) main.innerHTML=`${money(PRICE_NIGHT)} <small data-i18n="perNight">${t('perNight')}</small>`;
      const mobile=document.querySelector('.mobile-price');
      if(mobile) mobile.innerHTML=`${money(PRICE_NIGHT)}<small data-i18n="mobilePerNight">${t('mobilePerNight')}</small>`;
    }

    async function restRows(table, params){
      const response=await fetch(SUPABASE_URL+'/rest/v1/'+table+'?'+params.toString(),{
        method:'GET',
        headers:{apikey:SUPABASE_KEY,Accept:'application/json'},
        cache:'no-store'
      });
      if(!response.ok) throw new Error('HTTP '+response.status+' '+(await response.text()));
      const rows=await response.json();
      return Array.isArray(rows)?rows:[];
    }

    async function loadMasterCalendar(){
      const from=iso(today());
      const to=iso(addMonths(startOfMonth(today()),18));

      // 1) États : priorité absolue, indépendants des prix.
      try{
        const stateParams=new URLSearchParams({select:'day,status',unit_id:'eq.'+MASTER_UNIT_ID,day:'gte.'+from,order:'day.asc'});
        stateParams.append('day','lt.'+to);
        const rows=await restRows('digiy_loc_master_unit_calendar',stateParams);
        MASTER_STATES.clear();
        rows.forEach(row=>{
          if(row&&row.day&&(row.status==='occupied'||row.status==='closed')) MASTER_STATES.set(row.day,row.status);
        });
        renderCalendar();
        updateDates();
      }catch(error){
        console.warn('[CHEZ BAPTISTE SALY] Calendrier MASTER REST indisponible :',error);
      }

      // 2) Tarifs : même route REST, sans jamais bloquer les états.
      try{
        const unitParams=new URLSearchParams({select:'base_price,price_currency',id:'eq.'+MASTER_UNIT_ID,limit:'1'});
        const priceParams=new URLSearchParams({select:'day,price_override',unit_id:'eq.'+MASTER_UNIT_ID,day:'gte.'+from,order:'day.asc'});
        priceParams.append('day','lt.'+to);
        const [unitRows,priceRows]=await Promise.all([
          restRows('digiy_loc_master_units',unitParams),
          restRows('digiy_loc_master_unit_prices',priceParams)
        ]);
        const unit=unitRows[0]||null;
        const liveBase=Number(unit&&unit.base_price);
        if(Number.isFinite(liveBase)&&liveBase>=0) PRICE_NIGHT=liveBase;
        MASTER_PRICES.clear();
        priceRows.forEach(row=>{
          const value=Number(row&&row.price_override);
          if(row&&row.day&&Number.isFinite(value)&&value>=0) MASTER_PRICES.set(row.day,value);
        });
        refreshPublicBasePrice();
        renderCalendar();
        updateDates();
      }catch(error){
        console.warn('[CHEZ BAPTISTE SALY] Tarifs MASTER REST indisponibles :',error);
        refreshPublicBasePrice();
      }
    }

    let saved='fr';'''
    index2, count = pattern.subn(replacement, index, count=1)
    if count != 1:
        raise SystemExit('loadMasterCalendar public Saly introuvable')
    index = index2

# ===== GESTION PROPRIÉTAIRE =====
if 'DIGIY SALY OWNER MASTER V2' not in owner:
    owner = owner.replace(
        '.sessionbar button{border:0;background:#fff;border-radius:999px;padding:7px 11px;font-weight:900;cursor:pointer}',
        '.sessionbar button{border:0;background:#fff;border-radius:999px;padding:7px 11px;font-weight:900;cursor:pointer}.pricing{margin-top:14px;padding:14px;border:1px solid #c9dfd4;border-radius:18px;background:#f8fcfa}.pricing-title{font-weight:1000;font-size:15px}.pricing-note{margin:5px 0 0;color:#5d7167;font-size:12px;font-weight:750;line-height:1.45}.price-grid{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:end}.price-current{margin-top:8px;font-size:12px;font-weight:950;color:#087452}.price-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.day-price{display:block;font-size:8px;font-weight:1000;line-height:1;margin-top:2px}',
        1
    )
    owner = owner.replace(
        '<p class="muted">Votre calendrier public reste en lecture seule. Connectez-vous pour rendre une date disponible, occupée ou fermée.</p>',
        '<p class="muted">Votre calendrier public reste en lecture seule. Connectez-vous pour gérer Libre / Occupé / Fermé et vos tarifs.</p>',
        1
    )
    owner = owner.replace(
        '<p class="muted">Cliquez une date pour la sélectionner. Cliquez une seconde date pour sélectionner toute la période. Puis choisissez son état.</p>',
        '<p class="muted">Cliquez une date puis, si besoin, une seconde date pour une période. Ensuite choisissez son état ou son tarif.</p>',
        1
    )

    unit_anchor = '''    <div class="field hidden" id="unitField">
      <label for="unitSelect">Hébergement / chambre</label>
      <select id="unitSelect"></select>
    </div>

    <div class="calendar">'''
    unit_repl = '''    <div class="field hidden" id="unitField">
      <label for="unitSelect">Hébergement / chambre</label>
      <select id="unitSelect"></select>
    </div>

    <div class="pricing">
      <div class="pricing-title">💰 Tarif de base</div>
      <p class="pricing-note">Tarif public par nuit lorsqu’aucun prix spécial n’est défini.</p>
      <div class="price-grid">
        <div class="field"><label for="basePrice">Tarif de base / nuit</label><input id="basePrice" type="number" min="0" step="1" inputmode="numeric" placeholder="30000"></div>
        <button class="btn dark" id="saveBasePrice" type="button">Enregistrer le tarif de base</button>
      </div>
      <div class="price-current" id="basePriceInfo"></div>
    </div>

    <div class="calendar">'''
    if unit_anchor not in owner:
        raise SystemExit('Ancre tarif base gestion Saly introuvable')
    owner = owner.replace(unit_anchor, unit_repl, 1)

    state_anchor = '''    <div class="state-actions">
      <button class="freeBtn" id="makeAvailable" type="button">🟢 Disponible</button>
      <button class="occBtn" id="makeOccupied" type="button">🔴 Occupé</button>
      <button class="closeBtn" id="makeClosed" type="button">⚫ Fermé</button>
    </div>
    <p class="status" id="saveStatus" aria-live="polite"></p>'''
    state_repl = '''    <div class="state-actions">
      <button class="freeBtn" id="makeAvailable" type="button">🟢 Disponible</button>
      <button class="occBtn" id="makeOccupied" type="button">🔴 Occupé</button>
      <button class="closeBtn" id="makeClosed" type="button">⚫ Fermé</button>
    </div>
    <div class="pricing">
      <div class="pricing-title">🏷️ Prix de la sélection</div>
      <p class="pricing-note">Un prix spécial remplace le tarif de base uniquement pour les dates sélectionnées.</p>
      <div class="price-grid">
        <div class="field"><label for="specialPrice">Prix spécial / nuit</label><input id="specialPrice" type="number" min="0" step="1" inputmode="numeric" placeholder="Ex. 35000"></div>
        <button class="btn primary" id="applySpecialPrice" type="button">Appliquer ce prix</button>
      </div>
      <div class="price-actions"><button class="btn ghost" id="clearSpecialPrice" type="button">↩ Revenir au tarif de base</button></div>
    </div>
    <p class="status" id="saveStatus" aria-live="polite"></p>'''
    if state_anchor not in owner:
        raise SystemExit('Ancre prix sélection gestion Saly introuvable')
    owner = owner.replace(state_anchor, state_repl, 1)

    owner = owner.replace(
        "  const SITE_SLUG = 'saly-chez-baptiste';",
        "  const SITE_SLUG = 'saly-chez-baptiste';\n  // DIGIY SALY OWNER MASTER V2 — même moteur de données que Sarlat.",
        1
    )
    owner = owner.replace(
        '  let siteId=null, units=[], unitId=null, current=new Date(), states=new Map(), start=null, end=null;',
        "  let siteId=null, units=[], unitId=null, current=new Date(), states=new Map(), prices=new Map(), basePrice=30000, currency='XOF', start=null, end=null;",
        1
    )
    owner = owner.replace(
        "      .select('id,slug,display_name,unit_type,sort_order')",
        "      .select('id,slug,display_name,unit_type,sort_order,base_price,price_currency')",
        1
    )

    show_anchor = "  function showLogin(){managerPanel.classList.add('hidden');loginPanel.classList.remove('hidden');}"
    show_repl = show_anchor + "\n  function currentUnit(){return units.find(u=>u.id===unitId)||null;}\n  function money(value){const n=Number(value);return Number.isFinite(n)?n.toLocaleString('fr-FR',{maximumFractionDigits:0})+' '+(currency==='XOF'?'FCFA':currency):'—';}\n  function syncBase(){const u=currentUnit();basePrice=Number(u&&u.base_price!=null?u.base_price:30000);currency=(u&&u.price_currency)||'XOF';$('basePrice').value=basePrice;$('basePriceInfo').textContent='Tarif de base actuel : '+money(basePrice);}" 
    if show_anchor not in owner:
        raise SystemExit('Ancre helpers gestion Saly introuvable')
    owner = owner.replace(show_anchor, show_repl, 1)

    owner = owner.replace(
        "    $('unitField').classList.toggle('hidden',units.length<2);\n    setMsg(loginStatus,'');\n    showManager(session.user.email||'propriétaire');\n    await loadStates();",
        "    $('unitField').classList.toggle('hidden',units.length<2);\n    syncBase();\n    setMsg(loginStatus,'');\n    showManager(session.user.email||'propriétaire');\n    await loadData();",
        1
    )

    load_pattern = re.compile(r'''  async function loadStates\(\)\{.*?\n  \}\n\n  function resetSelection''', re.S)
    load_repl = '''  async function loadData(){
    if(!unitId)return;
    const from=iso(new Date(today().getFullYear(),today().getMonth(),1,12));

    const stateResult=await db.from('digiy_loc_master_unit_calendar').select('day,status').eq('unit_id',unitId).gte('day',from).order('day');
    if(stateResult.error){setMsg(saveStatus,'⚠️ Lecture calendrier impossible : '+stateResult.error.message,true);return;}
    states=new Map((stateResult.data||[]).map(r=>[r.day,r.status]));

    const priceResult=await db.from('digiy_loc_master_unit_prices').select('day,price_override').eq('unit_id',unitId).gte('day',from).order('day');
    if(priceResult.error){
      prices=new Map();
      setMsg(saveStatus,'⚠️ États chargés, tarifs spéciaux indisponibles : '+priceResult.error.message,true);
      return;
    }
    prices=new Map((priceResult.data||[]).map(r=>[r.day,Number(r.price_override)]));
  }

  function resetSelection'''
    owner2,count=load_pattern.subn(load_repl,owner,count=1)
    if count!=1:
        raise SystemExit('loadStates gestion Saly introuvable')
    owner=owner2

    old_render = "      b.type='button';b.className='day';b.textContent=d;b.dataset.date=key;"
    new_render = "      b.type='button';b.className='day';b.dataset.date=key;const dayPrice=prices.has(key)?prices.get(key):basePrice;b.innerHTML='<span>'+d+'</span><small class=\"day-price\">'+money(dayPrice)+'</small>';"
    if old_render not in owner:
        raise SystemExit('Rendu jour gestion Saly introuvable')
    owner=owner.replace(old_render,new_render,1)

    apply_pattern=re.compile(r'''  async function applyState\(status\)\{.*?\n  \}\n\n  \$\('sendCode'\)''',re.S)
    apply_repl='''  async function applyState(status){
    const dates=selectedDates();
    if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
    if(!unitId)return setMsg(saveStatus,'⚠️ Aucun hébergement sélectionné.',true);
    const buttons=[$('makeAvailable'),$('makeOccupied'),$('makeClosed')].filter(Boolean);
    buttons.forEach(button=>button.disabled=true);
    setMsg(saveStatus,'Enregistrement…');
    try{
      const {data,error}=await db.rpc('digiy_loc_set_unit_calendar_state_v2',{p_unit_id:unitId,p_days:dates,p_status:status});
      if(error)return setMsg(saveStatus,'⚠️ Enregistrement refusé : '+error.message,true);
      const returned=Array.isArray(data)?data.map(row=>String(row.day||row)):[];
      if(returned.length && !dates.every(day=>returned.includes(day))) return setMsg(saveStatus,'⚠️ Réponse incomplète du calendrier.',true);

      const {data:verifyRows,error:verifyError}=await db.from('digiy_loc_master_unit_calendar').select('day,status').eq('unit_id',unitId).in('day',dates);
      if(verifyError)return setMsg(saveStatus,'⚠️ Relecture du statut impossible : '+verifyError.message,true);
      const verifyMap=new Map((verifyRows||[]).map(row=>[String(row.day),row.status]));
      const persisted=status==='available'?dates.every(day=>!verifyMap.has(day)):dates.every(day=>verifyMap.get(day)===status);
      if(!persisted)return setMsg(saveStatus,'⚠️ État non retrouvé après relecture. Aucun faux succès affiché.',true);

      if(status==='available')dates.forEach(day=>states.delete(day));else dates.forEach(day=>states.set(day,status));
      const label=status==='available'?'Disponible':status==='occupied'?'Occupé':'Fermé';
      resetSelection();render();
      setMsg(saveStatus,'✓ '+label+' confirmé en base sur '+dates.length+(dates.length===1?' date.':' dates.'));
      const payload={type:'calendar-changed',unitId,dates,status,ts:Date.now()};
      try{const channel=new BroadcastChannel('digiy-loc-saly');channel.postMessage(payload);channel.close();}catch(_e){}
      try{localStorage.setItem('digiy-loc-saly-sync',JSON.stringify(payload));}catch(_e){}
    }finally{buttons.forEach(button=>button.disabled=false);}
  }

  async function saveBasePrice(){
    const value=Number(String($('basePrice').value).replace(',','.'));
    if(!Number.isFinite(value)||value<0)return setMsg(saveStatus,'⚠️ Tarif de base invalide.',true);
    const {data,error}=await db.from('digiy_loc_master_units').update({base_price:value,price_currency:'XOF',updated_at:new Date().toISOString()}).eq('id',unitId).select('id,base_price,price_currency').maybeSingle();
    if(error||!data)return setMsg(saveStatus,'⚠️ Tarif de base non enregistré'+(error?' : '+error.message:''),true);
    const u=currentUnit();u.base_price=Number(data.base_price);u.price_currency=data.price_currency||'XOF';syncBase();render();setMsg(saveStatus,'✓ Tarif de base enregistré : '+money(basePrice)+'.');
  }

  async function applySpecialPrice(){
    const dates=selectedDates();if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
    const value=Number(String($('specialPrice').value).replace(',','.'));if(!Number.isFinite(value)||value<0)return setMsg(saveStatus,'⚠️ Prix spécial invalide.',true);
    const rows=dates.map(day=>({unit_id:unitId,day,price_override:value,updated_at:new Date().toISOString()}));
    const {data,error}=await db.from('digiy_loc_master_unit_prices').upsert(rows,{onConflict:'unit_id,day'}).select('day,price_override');
    if(error||!data||data.length!==dates.length)return setMsg(saveStatus,'⚠️ Prix non enregistré'+(error?' : '+error.message:''),true);
    data.forEach(r=>prices.set(r.day,Number(r.price_override)));render();setMsg(saveStatus,'✓ Prix enregistré : '+money(value)+'.');
  }

  async function clearSpecialPrice(){
    const dates=selectedDates();if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
    const {error}=await db.from('digiy_loc_master_unit_prices').delete().eq('unit_id',unitId).in('day',dates);
    if(error)return setMsg(saveStatus,'⚠️ Retour tarif de base refusé : '+error.message,true);
    dates.forEach(day=>prices.delete(day));render();setMsg(saveStatus,'✓ Tarif de base rétabli sur la sélection.');
  }

  let resyncBusy=false;
  async function resyncOwner(){if(resyncBusy||!unitId||managerPanel.classList.contains('hidden'))return;resyncBusy=true;try{await loadData();render();}finally{resyncBusy=false;}}
  window.addEventListener('focus',resyncOwner);
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')resyncOwner();});

  $('sendCode')'''
    owner2,count=apply_pattern.subn(apply_repl,owner,count=1)
    if count!=1:
        raise SystemExit('applyState gestion Saly introuvable')
    owner=owner2

    old_events = "  $('unitSelect').addEventListener('change',async event=>{unitId=event.target.value;states.clear();resetSelection();setMsg(saveStatus,'');await loadStates();render();});"
    new_events = "  $('unitSelect').addEventListener('change',async event=>{unitId=event.target.value;states.clear();prices.clear();resetSelection();setMsg(saveStatus,'');syncBase();await loadData();render();});"
    if old_events not in owner:
        raise SystemExit('Event unitSelect gestion Saly introuvable')
    owner=owner.replace(old_events,new_events,1)
    owner=owner.replace(
        "  $('makeClosed').addEventListener('click',()=>applyState('closed'));",
        "  $('makeClosed').addEventListener('click',()=>applyState('closed'));\n  $('saveBasePrice').addEventListener('click',saveBasePrice);\n  $('applySpecialPrice').addEventListener('click',applySpecialPrice);\n  $('clearSpecialPrice').addEventListener('click',clearSpecialPrice);",
        1
    )
    owner=owner.replace(
        "states.clear();resetSelection();$('unitSelect').innerHTML='';",
        "states.clear();prices.clear();resetSelection();$('unitSelect').innerHTML='';",
        1
    )

index_path.write_text(index,encoding='utf-8')
owner_path.write_text(owner,encoding='utf-8')
print('Chez Baptiste Saly raccordé au MASTER LOC : états + tarifs + gestion propriétaire.')

from pathlib import Path

path=Path('gestion.html')
s=path.read_text(encoding='utf-8')
marker='DIGIY SALY PRIVATE RESERVATIONS V1'
if marker in s:
    print('Réservations privées V1 déjà présentes.')
    raise SystemExit(0)

# CSS
old_css='.price-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.day-price{display:block;font-size:8px;font-weight:1000;line-height:1;margin-top:2px}'
new_css='''.price-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.day-price{display:block;font-size:8px;font-weight:1000;line-height:1;margin-top:2px}.reservation-box{margin-top:16px;padding:15px;border:1px solid #c9dfd4;border-radius:18px;background:#fff}.reservation-box h3{margin:0 0 5px;font-size:18px}.reservation-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.reservation-grid .wide{grid-column:1/-1}.reservation-box textarea{width:100%;min-height:82px;resize:vertical;border:1px solid #bdd5c9;border-radius:14px;padding:12px;font:inherit}.reservation-list{display:grid;gap:9px;margin-top:12px}.reservation-card{padding:12px;border:1px solid #d7e7df;border-radius:15px;background:#f8fcfa}.reservation-card strong{display:block;font-size:15px}.reservation-meta{margin-top:4px;color:#5d7167;font-size:12px;font-weight:750;line-height:1.45}.reservation-note{margin-top:6px;font-size:12px;line-height:1.45;color:#354a40}.reservation-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}.reservation-actions a{display:inline-flex;align-items:center;justify-content:center;min-height:38px;padding:7px 11px;border-radius:999px;text-decoration:none;font-size:12px;font-weight:950}.sms-action{background:#e7f1ff;color:#174b86}.wa-action{background:#def7e9;color:#17633e}.guest-mark{font-size:9px;line-height:1}.empty-reservations{color:#5d7167;font-size:12px;font-weight:750;padding:9px 0}/* DIGIY SALY PRIVATE RESERVATIONS V1 */'''
if old_css not in s:
    raise SystemExit('Ancre CSS réservations introuvable')
s=s.replace(old_css,new_css,1)
s=s.replace('@media(max-width:560px){.state-actions{grid-template-columns:1fr}', '@media(max-width:560px){.reservation-grid{grid-template-columns:1fr}.reservation-grid .wide{grid-column:auto}.state-actions{grid-template-columns:1fr}',1)
s=s.replace('button,input,select{font:inherit}', 'button,input,select,textarea{font:inherit}',1)

# HTML private reservation block
anchor='''    <div class="pricing">
      <div class="pricing-title">🏷️ Prix de la sélection</div>
      <p class="pricing-note">Un prix spécial remplace le tarif de base uniquement pour les dates sélectionnées.</p>
      <div class="price-grid">
        <div class="field"><label for="specialPrice">Prix spécial / nuit</label><input id="specialPrice" type="number" min="0" step="1" inputmode="numeric" placeholder="Ex. 35000"></div>
        <button class="btn primary" id="applySpecialPrice" type="button">Appliquer ce prix</button>
      </div>
      <div class="price-actions"><button class="btn ghost" id="clearSpecialPrice" type="button">↩ Revenir au tarif de base</button></div>
    </div>
    <p class="status" id="saveStatus" aria-live="polite"></p>'''
replacement='''    <div class="pricing">
      <div class="pricing-title">🏷️ Prix de la sélection</div>
      <p class="pricing-note">Un prix spécial remplace le tarif de base uniquement pour les dates sélectionnées.</p>
      <div class="price-grid">
        <div class="field"><label for="specialPrice">Prix spécial / nuit</label><input id="specialPrice" type="number" min="0" step="1" inputmode="numeric" placeholder="Ex. 35000"></div>
        <button class="btn primary" id="applySpecialPrice" type="button">Appliquer ce prix</button>
      </div>
      <div class="price-actions"><button class="btn ghost" id="clearSpecialPrice" type="button">↩ Revenir au tarif de base</button></div>
    </div>

    <div class="reservation-box">
      <h3>👤 Réservation privée</h3>
      <p class="pricing-note">Sélectionnez la ou les dates dans le calendrier, puis rattachez le client. Ces informations restent visibles uniquement dans votre accès propriétaire.</p>
      <div class="reservation-grid">
        <div class="field"><label for="guestName">Nom du client</label><input id="guestName" type="text" autocomplete="name" placeholder="Nom et prénom"></div>
        <div class="field"><label for="guestPhone">Téléphone</label><input id="guestPhone" type="tel" autocomplete="tel" placeholder="+221… / +33…"></div>
        <div class="field"><label for="reservationSource">Provenance</label><select id="reservationSource"><option value="Booking.com">Booking.com</option><option value="Airbnb">Airbnb</option><option value="WhatsApp">WhatsApp</option><option value="Direct">Direct</option><option value="Autre">Autre</option></select></div>
        <div class="field"><label>Dates</label><input id="reservationDates" type="text" readonly placeholder="Sélectionnez dans le calendrier"></div>
        <div class="field wide"><label for="reservationNote">Note privée · facultatif</label><textarea id="reservationNote" placeholder="Heure d’arrivée, demande particulière, référence…"></textarea></div>
      </div>
      <button class="btn dark" id="saveReservation" type="button" style="margin-top:10px">🔒 Enregistrer la réservation</button>
    </div>

    <div class="reservation-box">
      <h3>📒 Réservations à venir</h3>
      <p class="pricing-note">Nom et téléphone ne quittent jamais l’espace propriétaire.</p>
      <div class="reservation-list" id="reservationList"></div>
    </div>

    <p class="status" id="saveStatus" aria-live="polite"></p>'''
if anchor not in s:
    raise SystemExit('Ancre HTML réservation introuvable')
s=s.replace(anchor,replacement,1)

# JS state
old_state="  let siteId=null, units=[], unitId=null, current=new Date(), states=new Map(), prices=new Map(), basePrice=30000, currency='XOF', start=null, end=null;"
new_state="  let siteId=null, units=[], unitId=null, current=new Date(), states=new Map(), prices=new Map(), reservations=[], basePrice=30000, currency='XOF', start=null, end=null;"
if old_state not in s:
    raise SystemExit('État JS gestion introuvable')
s=s.replace(old_state,new_state,1)

# Selection label also feeds reservation dates
old_update="""  function updateSelection(){
    if(!start)return $('selectionLabel').textContent='Sélection : aucune date';
    $('selectionLabel').textContent=end&&iso(end)!==iso(start)?'Sélection : '+fmt(start)+' → '+fmt(end):'Sélection : '+fmt(start);
  }"""
new_update="""  function updateSelection(){
    const datesInput=$('reservationDates');
    if(!start){$('selectionLabel').textContent='Sélection : aucune date';if(datesInput)datesInput.value='';return;}
    const label=end&&iso(end)!==iso(start)?fmt(start)+' → '+fmt(end):fmt(start);
    $('selectionLabel').textContent='Sélection : '+label;
    if(datesInput)datesInput.value=label;
  }"""
if old_update not in s:
    raise SystemExit('updateSelection introuvable')
s=s.replace(old_update,new_update,1)

# loadData reservations after pricing, without blocking calendar
old_load="""    const priceResult=await db.from('digiy_loc_master_unit_prices').select('day,price_override').eq('unit_id',unitId).gte('day',from).order('day');
    if(priceResult.error){
      prices=new Map();
      setMsg(saveStatus,'⚠️ États chargés, tarifs spéciaux indisponibles : '+priceResult.error.message,true);
      return;
    }
    prices=new Map((priceResult.data||[]).map(r=>[r.day,Number(r.price_override)]));
  }"""
new_load="""    const priceResult=await db.from('digiy_loc_master_unit_prices').select('day,price_override').eq('unit_id',unitId).gte('day',from).order('day');
    if(priceResult.error){
      prices=new Map();
      console.warn('[SALY OWNER] Tarifs spéciaux indisponibles',priceResult.error);
    }else{
      prices=new Map((priceResult.data||[]).map(r=>[r.day,Number(r.price_override)]));
    }

    const reservationResult=await db.from('digiy_loc_master_reservations')
      .select('id,unit_id,guest_name,guest_phone,source,start_day,end_day,note,created_at')
      .eq('unit_id',unitId)
      .gte('end_day',iso(today()))
      .order('start_day');
    if(reservationResult.error){
      reservations=[];
      console.warn('[SALY OWNER] Réservations privées indisponibles',reservationResult.error);
    }else{
      reservations=reservationResult.data||[];
    }
    renderReservations();
  }"""
if old_load not in s:
    raise SystemExit('loadData pricing introuvable')
s=s.replace(old_load,new_load,1)

# Day marker when reservation details exist
old_day="""      b.type='button';b.className='day';b.dataset.date=key;const dayPrice=prices.has(key)?prices.get(key):basePrice;b.innerHTML='<span>'+d+'</span><small class=\"day-price\">'+money(dayPrice)+'</small>';"""
new_day="""      b.type='button';b.className='day';b.dataset.date=key;const dayPrice=prices.has(key)?prices.get(key):basePrice;const booking=reservations.find(r=>key>=r.start_day&&key<=r.end_day);b.innerHTML='<span>'+d+'</span><small class=\"day-price\">'+money(dayPrice)+'</small>'+(booking?'<small class=\"guest-mark\">👤</small>':'');if(booking)b.title=booking.guest_name+' · '+booking.guest_phone;"""
if old_day not in s:
    raise SystemExit('Rendu jour gestion introuvable')
s=s.replace(old_day,new_day,1)

# Insert private reservation renderer before applyState
apply_anchor='''  async function applyState(status){'''
functions='''  function reservationMessage(r){
    const dates=r.start_day===r.end_day?r.start_day:(r.start_day+' au '+r.end_day);
    return 'Bonjour '+r.guest_name+', concernant votre séjour Chez Baptiste Saly du '+dates+', je vous contacte pour vous transmettre des informations complémentaires.';
  }

  function renderReservations(){
    const box=$('reservationList');if(!box)return;
    box.innerHTML='';
    if(!reservations.length){const empty=document.createElement('div');empty.className='empty-reservations';empty.textContent='Aucune fiche client enregistrée à venir.';box.appendChild(empty);return;}
    reservations.forEach(r=>{
      const card=document.createElement('article');card.className='reservation-card';
      const name=document.createElement('strong');name.textContent='👤 '+r.guest_name;card.appendChild(name);
      const meta=document.createElement('div');meta.className='reservation-meta';meta.textContent=(r.start_day===r.end_day?r.start_day:r.start_day+' → '+r.end_day)+' · '+r.guest_phone+(r.source?' · '+r.source:'');card.appendChild(meta);
      if(r.note){const note=document.createElement('div');note.className='reservation-note';note.textContent=r.note;card.appendChild(note);}
      const actions=document.createElement('div');actions.className='reservation-actions';
      const sms=document.createElement('a');sms.className='sms-action';sms.textContent='📩 SMS';sms.href='sms:'+r.guest_phone+'?body='+encodeURIComponent(reservationMessage(r));actions.appendChild(sms);
      const digits=String(r.guest_phone||'').replace(/\\D/g,'');
      if(digits){const wa=document.createElement('a');wa.className='wa-action';wa.textContent='💬 WhatsApp';wa.href='https://wa.me/'+digits+'?text='+encodeURIComponent(reservationMessage(r));wa.target='_blank';wa.rel='noopener';actions.appendChild(wa);}
      card.appendChild(actions);box.appendChild(card);
    });
  }

  async function savePrivateReservation(){
    const dates=selectedDates();
    if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez d’abord une date ou une période.',true);
    const guestName=$('guestName').value.trim(),guestPhone=$('guestPhone').value.trim();
    if(!guestName)return setMsg(saveStatus,'⚠️ Indiquez le nom du client.',true);
    if(!guestPhone)return setMsg(saveStatus,'⚠️ Indiquez le téléphone du client.',true);
    const button=$('saveReservation');button.disabled=true;setMsg(saveStatus,'Enregistrement de la réservation…');
    try{
      const {data,error}=await db.rpc('digiy_loc_master_save_reservation_v1',{
        p_unit_id:unitId,p_start_day:dates[0],p_end_day:dates[dates.length-1],p_guest_name:guestName,p_guest_phone:guestPhone,p_source:$('reservationSource').value,p_note:$('reservationNote').value.trim()||null
      });
      if(error)return setMsg(saveStatus,'⚠️ Réservation non enregistrée : '+error.message,true);
      if(!data||!data.length)return setMsg(saveStatus,'⚠️ Réservation non retrouvée après écriture.',true);
      await loadData();
      resetSelection();render();renderReservations();
      $('guestName').value='';$('guestPhone').value='';$('reservationNote').value='';
      setMsg(saveStatus,'✓ Réservation privée enregistrée et dates confirmées Occupé.');
    }finally{button.disabled=false;}
  }

'''
if apply_anchor not in s:
    raise SystemExit('applyState anchor introuvable')
s=s.replace(apply_anchor,functions+apply_anchor,1)

# Events + unit switching/logout cleanup
s=s.replace("  $('clearSpecialPrice').addEventListener('click',clearSpecialPrice);", "  $('clearSpecialPrice').addEventListener('click',clearSpecialPrice);\n  $('saveReservation').addEventListener('click',savePrivateReservation);",1)
s=s.replace("states.clear();prices.clear();resetSelection();setMsg(saveStatus,'');syncBase();await loadData();render();", "states.clear();prices.clear();reservations=[];resetSelection();setMsg(saveStatus,'');syncBase();await loadData();render();renderReservations();",1)
s=s.replace("states.clear();prices.clear();resetSelection();$('unitSelect').innerHTML='';", "states.clear();prices.clear();reservations=[];resetSelection();$('unitSelect').innerHTML='';",1)

path.write_text(s,encoding='utf-8')
print('Réservations privées Saly : nom, téléphone, source, note, SMS et WhatsApp posés côté propriétaire.')

/* CHEZ BAPTISTE SALY — navigation compacte + MASTER LOC universel */
(function(){
  'use strict';
  if(window.__DIGIY_SALY_MOBILE_COMPACT__) return;
  window.__DIGIY_SALY_MOBILE_COMPACT__=true;

  var SUPABASE_URL='https://wesqmwjjtsefyjnluosj.supabase.co';
  var SUPABASE_KEY='sb_publishable_tGHItRgeWDmGjnd0CK1DVQ_BIep4Ug3';
  var UNIT_ID='ae44152a-0e11-4c7e-8834-d5ff872b2fbd';
  var AUTO_REFRESH_MS=10000;
  var states=new Map();
  var applying=false;
  var mq=window.matchMedia('(max-width:620px)');

  function localTodayISO(){
    var n=new Date();
    return n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0');
  }

  function currentLang(){
    return (document.documentElement.lang||'fr').slice(0,2).toLowerCase();
  }

  function copy(){
    var all={
      fr:{info:'Infos',payment:'Paiement',whatsapp:'WhatsApp',owner:'Accès propriétaire',free:'Disponible',occupied:'Occupé',closed:'Fermé',live:'Disponibilités en direct',none:'Aucune période occupée ou fermée à venir.'},
      en:{info:'Info',payment:'Payment',whatsapp:'WhatsApp',owner:'Owner access',free:'Available',occupied:'Occupied',closed:'Closed',live:'Live availability',none:'No upcoming occupied or closed period.'},
      es:{info:'Infos',payment:'Pago',whatsapp:'WhatsApp',owner:'Acceso propietario',free:'Disponible',occupied:'Ocupado',closed:'Cerrado',live:'Disponibilidad en directo',none:'No hay periodos ocupados o cerrados próximos.'},
      pt:{info:'Infos',payment:'Pagamento',whatsapp:'WhatsApp',owner:'Acesso proprietário',free:'Disponível',occupied:'Ocupado',closed:'Fechado',live:'Disponibilidade em direto',none:'Nenhum período ocupado ou fechado próximo.'},
      it:{info:'Info',payment:'Pagamento',whatsapp:'WhatsApp',owner:'Accesso proprietario',free:'Disponibile',occupied:'Occupato',closed:'Chiuso',live:'Disponibilità in tempo reale',none:'Nessun periodo occupato o chiuso in arrivo.'},
      de:{info:'Infos',payment:'Zahlung',whatsapp:'WhatsApp',owner:'Eigentümerzugang',free:'Verfügbar',occupied:'Belegt',closed:'Geschlossen',live:'Live-Verfügbarkeit',none:'Keine kommenden belegten oder geschlossenen Zeiträume.'},
      nl:{info:'Info',payment:'Betaling',whatsapp:'WhatsApp',owner:'Eigenaarslogin',free:'Beschikbaar',occupied:'Bezet',closed:'Gesloten',live:'Live beschikbaarheid',none:'Geen komende bezette of gesloten periodes.'},
      ar:{info:'معلومات',payment:'الدفع',whatsapp:'واتساب',owner:'دخول المالك',free:'متاح',occupied:'مشغول',closed:'مغلق',live:'التوفر المباشر',none:'لا توجد فترات مشغولة أو مغلقة قادمة.'}
    };
    return all[currentLang()]||all.fr;
  }

  function labels(){
    var t=copy();
    return {info:t.info,payment:t.payment,whatsapp:t.whatsapp};
  }

  function locale(){
    var map={fr:'fr-FR',en:'en-GB',es:'es-ES',pt:'pt-PT',it:'it-IT',de:'de-DE',nl:'nl-NL',ar:'ar'};
    return map[currentLang()]||'fr-FR';
  }

  function parseISO(s){
    var p=s.split('-').map(Number);
    return new Date(p[0],p[1]-1,p[2],12);
  }

  function formatDate(s){
    return parseISO(s).toLocaleDateString(locale(),{day:'numeric',month:'short',year:'numeric'});
  }

  function groupStates(){
    var rows=Array.from(states.entries()).filter(function(row){return row[0]>=localTodayISO();}).sort(function(a,b){return a[0].localeCompare(b[0]);});
    var out=[];
    rows.forEach(function(row){
      var day=row[0],status=row[1],last=out[out.length-1];
      if(last&&last.status===status){
        var next=parseISO(last.end);next.setDate(next.getDate()+1);
        var nextISO=next.getFullYear()+'-'+String(next.getMonth()+1).padStart(2,'0')+'-'+String(next.getDate()).padStart(2,'0');
        if(nextISO===day){last.end=day;return;}
      }
      out.push({start:day,end:day,status:status});
    });
    return out;
  }

  function injectMasterStyles(){
    if(document.getElementById('digiyMasterLocStyles')) return;
    var style=document.createElement('style');
    style.id='digiyMasterLocStyles';
    style.textContent='\
      .digiy-owner-access{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-height:40px;padding:0 10px;border-radius:12px;border:1px solid #c8ddd2;background:#fff;color:#05593f;text-decoration:none;font-size:11px;font-weight:950;white-space:nowrap}\
      .digiy-loc-legend{margin:9px 16px 2px;padding:9px 11px;border-radius:13px;background:#f5faf7;border:1px solid #d7e7df;color:#405047;font-size:11px;font-weight:850;display:flex;align-items:center;gap:10px;flex-wrap:wrap}\
      .digiy-loc-legend strong{color:#05593f;margin-right:auto}.digiy-loc-dot{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:4px;vertical-align:-1px}.digiy-loc-dot.free{background:#dff3e6;border:1px solid #8cc9a1}.digiy-loc-dot.occupied{background:#ef4444}.digiy-loc-dot.closed{background:#343a37}\
      .day.loc-occupied{background:#fde5e2!important;color:#a3231d!important;text-decoration:line-through;border-radius:12px}.day.loc-closed{background:#343a37!important;color:#fff!important;text-decoration:none;border-radius:12px;opacity:.92!important}\
      .blocked-list .digiy-state-line{display:block;margin-top:5px}.blocked-list .digiy-state-dot{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:5px}.blocked-list .digiy-state-dot.occupied{background:#ef4444}.blocked-list .digiy-state-dot.closed{background:#343a37}\
      @media(max-width:620px){.digiy-owner-access{width:40px;min-width:40px;padding:0;font-size:17px}.digiy-owner-access span{display:none}}';
    document.head.appendChild(style);
  }

  function injectOwnerAccess(){
    if(document.querySelector('.digiy-owner-access')) return;
    var top=document.querySelector('.topbar');
    if(!top) return;
    var a=document.createElement('a');
    a.className='digiy-owner-access';
    a.href='./gestion.html';
    a.rel='nofollow';
    a.innerHTML='🔐 <span></span>';
    a.querySelector('span').textContent=copy().owner;
    a.setAttribute('aria-label',copy().owner);
    top.appendChild(a);
  }

  function injectLegend(){
    var nav=document.querySelector('.calendar-nav');
    if(!nav||document.getElementById('digiyLocLegend')) return;
    var t=copy(),legend=document.createElement('div');
    legend.id='digiyLocLegend';legend.className='digiy-loc-legend';
    legend.innerHTML='<strong>'+t.live+'</strong><span><i class="digiy-loc-dot free"></i>'+t.free+'</span><span><i class="digiy-loc-dot occupied"></i>'+t.occupied+'</span><span><i class="digiy-loc-dot closed"></i>'+t.closed+'</span>';
    nav.insertAdjacentElement('afterend',legend);
  }

  function updateBlockedList(){
    var list=document.querySelector('.blocked-list');
    if(!list) return;
    var t=copy(),groups=groupStates();
    if(!groups.length){list.innerHTML='<strong>'+t.live+'</strong><br>'+t.none;return;}
    list.innerHTML='<strong>'+t.live+'</strong>';
    groups.forEach(function(g){
      var line=document.createElement('span');line.className='digiy-state-line';
      var label=g.start===g.end?formatDate(g.start):formatDate(g.start)+' → '+formatDate(g.end);
      line.innerHTML='<i class="digiy-state-dot '+g.status+'"></i><b>'+(g.status==='closed'?t.closed:t.occupied)+'</b> · '+label;
      list.appendChild(line);
    });
  }

  function rangeInvalid(){
    var start=document.querySelector('#calendarMonths .day.range-start[data-date]');
    var end=document.querySelector('#calendarMonths .day.range-end[data-date]');
    if(!start) return false;
    var a=start.dataset.date,b=end?end.dataset.date:a;
    return Array.from(states.keys()).some(function(day){return day>=a&&day<=b&&day>=localTodayISO();});
  }

  function syncConfirm(){
    var btn=document.getElementById('calendarConfirm');
    if(!btn) return;
    var bad=rangeInvalid();
    btn.disabled=bad;
    btn.title=bad?(copy().occupied+' / '+copy().closed):'';
  }

  function applyStates(){
    if(applying) return;
    applying=true;
    try{
      document.querySelectorAll('#calendarMonths .day[data-date]').forEach(function(day){
        var key=day.dataset.date,state=states.get(key)||null;
        day.classList.remove('loc-occupied','loc-closed');
        day.removeAttribute('data-loc-status');
        if(key>=localTodayISO()){
          if(state){
            day.disabled=true;
            day.classList.add('blocked','disabled',state==='closed'?'loc-closed':'loc-occupied');
            day.dataset.locStatus=state;
            day.title=state==='closed'?copy().closed:copy().occupied;
          }else{
            day.disabled=false;
            day.classList.remove('blocked','disabled');
            day.title='';
          }
        }
      });
      injectLegend();
      updateBlockedList();
      syncConfirm();
    }finally{applying=false;}
  }

  async function fetchStates(){
    var params=new URLSearchParams();
    params.append('unit_id','eq.'+UNIT_ID);
    params.append('day','gte.'+localTodayISO());
    params.append('select','day,status');
    params.append('order','day.asc');
    try{
      var response=await fetch(SUPABASE_URL+'/rest/v1/digiy_loc_master_unit_calendar?'+params.toString(),{
        headers:{apikey:SUPABASE_KEY,Accept:'application/json'},cache:'no-store'
      });
      if(!response.ok) throw new Error('HTTP '+response.status);
      var rows=await response.json();
      states=new Map((rows||[]).map(function(row){return [row.day,row.status];}));
      applyStates();
    }catch(error){
      console.warn('DIGIY LOC Saly : lecture Supabase indisponible',error);
    }
  }

  function watchCalendar(){
    var months=document.getElementById('calendarMonths');
    if(!months||months.dataset.masterLocWatch==='1') return;
    months.dataset.masterLocWatch='1';
    new MutationObserver(function(){setTimeout(applyStates,0);}).observe(months,{childList:true,subtree:true});
    var confirm=document.getElementById('calendarConfirm');
    if(confirm) confirm.addEventListener('click',function(event){if(rangeInvalid()){event.preventDefault();event.stopImmediatePropagation();}},true);
  }

  function syncLanguage(){
    var owner=document.querySelector('.digiy-owner-access span');
    if(owner) owner.textContent=copy().owner;
    var access=document.querySelector('.digiy-owner-access');
    if(access) access.setAttribute('aria-label',copy().owner);
    var legend=document.getElementById('digiyLocLegend');
    if(legend){legend.remove();injectLegend();}
    applyStates();
  }

  function initMasterLoc(){
    injectMasterStyles();
    injectOwnerAccess();
    watchCalendar();
    fetchStates();
    new MutationObserver(syncLanguage).observe(document.documentElement,{attributes:true,attributeFilter:['lang','dir']});
    window.addEventListener('focus',fetchStates);
    document.addEventListener('visibilitychange',function(){if(!document.hidden)fetchStates();});
    window.setInterval(function(){if(!document.hidden)fetchStates();},AUTO_REFRESH_MS);
  }

  function foldCards(){
    var cards=document.querySelectorAll('.compact-grid .compact-card');
    cards.forEach(function(card,index){
      if(card.classList.contains('mobile-fold')) return;
      var heading=card.querySelector('h2');
      if(!heading) return;
      card.classList.add('mobile-fold');
      card.id=index===0?'mobile-info':'mobile-payment';
      var toggle=document.createElement('button');toggle.type='button';toggle.className='mobile-fold-toggle';toggle.setAttribute('aria-expanded','false');
      var title=document.createElement('span');title.textContent=heading.textContent;if(heading.hasAttribute('data-i18n'))title.setAttribute('data-i18n',heading.getAttribute('data-i18n'));toggle.appendChild(title);
      var body=document.createElement('div');body.className='mobile-fold-body';body.hidden=true;
      Array.prototype.slice.call(card.children).forEach(function(child){if(child!==heading)body.appendChild(child);});
      card.innerHTML='';card.appendChild(toggle);card.appendChild(body);
      toggle.addEventListener('click',function(){var open=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',open?'false':'true');body.hidden=open;});
    });
  }

  function openFold(id){
    var card=document.getElementById(id);if(!card)return;
    var toggle=card.querySelector('.mobile-fold-toggle'),body=card.querySelector('.mobile-fold-body');
    if(toggle&&body){toggle.setAttribute('aria-expanded','true');body.hidden=false;}
    card.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function rebuildBar(){
    var bar=document.querySelector('.mobile-bar'),dateBtn=document.getElementById('mobileDateBtn');
    if(!bar||!dateBtn||bar.dataset.compactReady==='1')return;
    bar.dataset.compactReady='1';bar.innerHTML='';bar.appendChild(dateBtn);
    function make(action){var button=document.createElement('button');button.type='button';button.dataset.mobileAction=action;return button;}
    var info=make('info'),payment=make('payment'),whatsapp=make('whatsapp');bar.appendChild(info);bar.appendChild(payment);bar.appendChild(whatsapp);
    info.addEventListener('click',function(){openFold('mobile-info');});payment.addEventListener('click',function(){openFold('mobile-payment');});
    whatsapp.addEventListener('click',function(){var link=document.getElementById('bookingWhatsApp');if(link&&link.href)window.open(link.href,'_blank','noopener');});
    function sync(){var l=labels();info.textContent=l.info;payment.textContent=l.payment;whatsapp.textContent=l.whatsapp;}
    sync();new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  }

  function initMobile(){
    if(!mq.matches)return;
    document.body.classList.add('mobile-compact-active');
    foldCards();rebuildBar();
  }

  function init(){initMasterLoc();initMobile();}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();

/* Chez Baptiste Saly — la vidéo reste dans l'univers DIGIYLYFE pour conserver les retours visibles. */
(function(){
  'use strict';
  function routeVideoThroughDigiy(){
    var link=document.querySelector('a.video-action');
    if(!link)return;
    link.href='https://part-chez-baptiste.digiylyfe.com/video.html';
    link.removeAttribute('target');
    link.removeAttribute('rel');
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',routeVideoThroughDigiy,{once:true});else routeVideoThroughDigiy();
})();

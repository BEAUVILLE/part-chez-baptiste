/* CHEZ BAPTISTE SALY — navigation mobile compacte */
(function(){
  'use strict';
  if(window.__DIGIY_SALY_MOBILE_COMPACT__) return;
  window.__DIGIY_SALY_MOBILE_COMPACT__=true;

  var mq=window.matchMedia('(max-width:620px)');

  function currentLang(){
    return (document.documentElement.lang||'fr').slice(0,2)==='en'?'en':'fr';
  }

  function labels(){
    return currentLang()==='en'
      ? {info:'Info',payment:'Payment',whatsapp:'WhatsApp'}
      : {info:'Infos',payment:'Paiement',whatsapp:'WhatsApp'};
  }

  function foldCards(){
    var cards=document.querySelectorAll('.compact-grid .compact-card');
    cards.forEach(function(card,index){
      if(card.classList.contains('mobile-fold')) return;
      var heading=card.querySelector('h2');
      if(!heading) return;

      card.classList.add('mobile-fold');
      card.id=index===0?'mobile-info':'mobile-payment';

      var toggle=document.createElement('button');
      toggle.type='button';
      toggle.className='mobile-fold-toggle';
      toggle.setAttribute('aria-expanded','false');

      var title=document.createElement('span');
      title.textContent=heading.textContent;
      if(heading.hasAttribute('data-i18n')){
        title.setAttribute('data-i18n',heading.getAttribute('data-i18n'));
      }
      toggle.appendChild(title);

      var body=document.createElement('div');
      body.className='mobile-fold-body';
      body.hidden=true;

      Array.prototype.slice.call(card.children).forEach(function(child){
        if(child!==heading) body.appendChild(child);
      });

      card.innerHTML='';
      card.appendChild(toggle);
      card.appendChild(body);

      toggle.addEventListener('click',function(){
        var open=toggle.getAttribute('aria-expanded')==='true';
        toggle.setAttribute('aria-expanded',open?'false':'true');
        body.hidden=open;
      });
    });
  }

  function openFold(id){
    var card=document.getElementById(id);
    if(!card) return;
    var toggle=card.querySelector('.mobile-fold-toggle');
    var body=card.querySelector('.mobile-fold-body');
    if(toggle&&body){
      toggle.setAttribute('aria-expanded','true');
      body.hidden=false;
    }
    card.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function rebuildBar(){
    var bar=document.querySelector('.mobile-bar');
    var dateBtn=document.getElementById('mobileDateBtn');
    if(!bar||!dateBtn||bar.dataset.compactReady==='1') return;
    bar.dataset.compactReady='1';

    bar.innerHTML='';
    bar.appendChild(dateBtn);

    function make(action){
      var button=document.createElement('button');
      button.type='button';
      button.dataset.mobileAction=action;
      return button;
    }

    var info=make('info');
    var payment=make('payment');
    var whatsapp=make('whatsapp');
    bar.appendChild(info);
    bar.appendChild(payment);
    bar.appendChild(whatsapp);

    info.addEventListener('click',function(){openFold('mobile-info');});
    payment.addEventListener('click',function(){openFold('mobile-payment');});
    whatsapp.addEventListener('click',function(){
      var link=document.getElementById('bookingWhatsApp');
      if(link&&link.href) window.open(link.href,'_blank','noopener');
    });

    function sync(){
      var l=labels();
      info.textContent=l.info;
      payment.textContent=l.payment;
      whatsapp.textContent=l.whatsapp;
    }
    sync();
    new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  }

  function init(){
    if(!mq.matches) return;
    document.body.classList.add('mobile-compact-active');
    foldCards();
    rebuildBar();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();

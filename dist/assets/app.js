(() => {
  const menu=document.querySelector('.menu-toggle'),nav=document.querySelector('#site-nav');
  menu?.addEventListener('click',()=>{const expanded=menu.getAttribute('aria-expanded')==='true';menu.setAttribute('aria-expanded',String(!expanded));nav.classList.toggle('open',!expanded);});
  const motion=document.querySelector('.motion-toggle');
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  let saved=null;try{saved=localStorage.getItem('ft-motion');}catch{}
  const setMotion=paused=>{document.body.classList.toggle('motion-paused',paused);motion.setAttribute('aria-pressed',String(paused));motion.textContent=paused?'开启动画':'暂停动画';};
  setMotion(saved===null?reduced.matches:saved==='paused');
  motion?.addEventListener('click',()=>{const paused=!document.body.classList.contains('motion-paused');setMotion(paused);try{localStorage.setItem('ft-motion',paused?'paused':'running');}catch{}});
  reduced.addEventListener('change',e=>{if(e.matches)setMotion(true);});
  let timer;const toast=text=>{const el=document.querySelector('#toast');el.textContent=text;el.classList.add('visible');clearTimeout(timer);timer=setTimeout(()=>el.classList.remove('visible'),2600);};
  document.querySelectorAll('[data-copy]').forEach(btn=>btn.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(btn.dataset.copy);toast('优惠码已复制，请在结算页确认是否生效');}catch{toast('复制失败，请手动复制旁边的优惠码');}}));
  document.querySelectorAll('[data-filter]').forEach(input=>{const cards=[...document.querySelectorAll(input.dataset.filter)];input.addEventListener('input',()=>{const term=input.value.trim().toLocaleLowerCase();let count=0;cards.forEach(card=>{const match=(card.dataset.search||card.textContent).toLocaleLowerCase().includes(term);card.hidden=!match;if(match)count++;});input.parentElement.querySelector('.filter-status').textContent=count?`显示 ${count} 项`:'没有匹配结果，请换一个关键词';});});
})();

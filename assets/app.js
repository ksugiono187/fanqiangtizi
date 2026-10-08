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
  const canvas=document.querySelector('.tech-canvas');
  if(canvas){
    const ctx=canvas.getContext('2d');
    if(ctx){
      let width=0,height=0,frame=0,last=0,phase=0;
      const particles=Array.from({length:42},(_,i)=>({x:(i*.61803398875)%1,y:(i*.38196601125)%1,r:i%5===0?2:1,speed:.008+(i%7)*.002}));
      const draw=()=>{
        ctx.clearRect(0,0,width,height);
        // Slow luminous currents cross the screen behind the reading surface.
        for(let band=0;band<5;band++){
          const gradient=ctx.createLinearGradient(0,0,width,height);
          gradient.addColorStop(0,'rgba(70,140,255,0)');
          gradient.addColorStop(.35,`rgba(81,151,255,${band===0?.65:.24})`);
          gradient.addColorStop(.72,`rgba(168,100,255,${band===0?.7:.28})`);
          gradient.addColorStop(1,'rgba(117,88,255,0)');
          ctx.beginPath();
          for(let x=-80;x<=width+80;x+=12){
            const y=height*.52+Math.sin(x/width*3.8+phase*.3+band*.12)*height*.2+Math.cos(x/width*6-phase*.45)*height*.05+band*12;
            x===-80?ctx.moveTo(x,y):ctx.lineTo(x,y);
          }
          ctx.strokeStyle=gradient;ctx.lineWidth=band===0?2:1;
          ctx.shadowColor=band%2?'#a875ff':'#518fff';ctx.shadowBlur=band===0?18:8;ctx.stroke();
        }
        ctx.shadowBlur=9;
        for(const p of particles){
          const x=((p.x+phase*p.speed)%1)*width;
          const y=((p.y-phase*p.speed*.35)%1+1)%1*height;
          ctx.fillStyle=p.r===2?'rgba(178,153,255,.75)':'rgba(123,177,255,.55)';
          ctx.beginPath();ctx.arc(x,y,p.r,0,Math.PI*2);ctx.fill();
        }
        ctx.shadowBlur=0;
      };
      const tick=time=>{
        frame=0;
        if(document.hidden||document.body.classList.contains('motion-paused'))return;
        if(time-last>=32){phase+=Math.min((time-last)/1000,.06);last=time;draw();}
        frame=requestAnimationFrame(tick);
      };
      const sync=()=>{
        if(frame)cancelAnimationFrame(frame);frame=0;last=performance.now();
        if(!document.hidden&&!document.body.classList.contains('motion-paused'))frame=requestAnimationFrame(tick);
      };
      const resize=()=>{
        width=innerWidth;height=innerHeight;const ratio=Math.min(devicePixelRatio||1,1.5);
        canvas.width=Math.round(width*ratio);canvas.height=Math.round(height*ratio);
        ctx.setTransform(ratio,0,0,ratio,0,0);draw();
      };
      addEventListener('resize',resize,{passive:true});
      document.addEventListener('visibilitychange',sync);
      new MutationObserver(sync).observe(document.body,{attributes:true,attributeFilter:['class']});
      resize();sync();
    }
  }
  let timer;const toast=text=>{const el=document.querySelector('#toast');el.textContent=text;el.classList.add('visible');clearTimeout(timer);timer=setTimeout(()=>el.classList.remove('visible'),2600);};
  document.querySelectorAll('[data-copy]').forEach(btn=>btn.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(btn.dataset.copy);toast('优惠码已复制，请在结算页确认是否生效');}catch{toast('复制失败，请手动复制旁边的优惠码');}}));
  document.querySelectorAll('[data-filter]').forEach(input=>{const cards=[...document.querySelectorAll(input.dataset.filter)];input.addEventListener('input',()=>{const term=input.value.trim().toLocaleLowerCase();let count=0;cards.forEach(card=>{const match=(card.dataset.search||card.textContent).toLocaleLowerCase().includes(term);card.hidden=!match;if(match)count++;});input.parentElement.querySelector('.filter-status').textContent=count?`显示 ${count} 项`:'没有匹配结果，请换一个关键词';});});
})();

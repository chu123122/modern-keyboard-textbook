'use strict';
(() => {
  const list=JSON.parse(document.getElementById('exercise-data').textContent);
  const examples=new Map(list.map(e=>[e.id,e]));
  let context=null, nodes=[], timer=null, active=null;
  function stop(){for(const node of nodes){try{node.stop()}catch{}}nodes=[];clearTimeout(timer);if(active)active.textContent='已停止';active=null;}
  function tone(frequency,at,duration,level,click=false){
    const oscillator=context.createOscillator(),gain=context.createGain();
    oscillator.type=click?'sine':'triangle';oscillator.frequency.value=frequency;
    gain.gain.setValueAtTime(0,at);gain.gain.linearRampToValueAtTime(level,at+.008);
    gain.gain.exponentialRampToValueAtTime(Math.max(.001,level*.20),at+Math.max(.02,duration));
    gain.gain.exponentialRampToValueAtTime(.0001,at+duration+.22);
    oscillator.connect(gain);gain.connect(context.destination);oscillator.start(at);oscillator.stop(at+duration+.24);nodes.push(oscillator);
  }
  async function play(panel,hand){
    stop();const e=examples.get(panel.dataset.exercise),status=panel.querySelector('output');
    try{
      const AudioContext=window.AudioContext||window.webkitAudioContext;
      if(!AudioContext)throw new Error('音频接口不可用');
      context=context||new AudioContext();await context.resume();
      const speed=Number(panel.querySelector('select').value),unit=60/e.bpm/speed,bar=e.meter[0]*4/e.meter[1];
      const at=context.currentTime+.08,intro=bar*unit,pulses=e.meter[0]===6&&e.meter[1]===8?[0,1.5]:Array.from({length:e.meter[0]},(_,i)=>i);
      for(const p of pulses)tone(p===0?1250:900,at+p*unit,.04,.11,true);
      for(const ev of e.events){
        if((hand==='rh'&&ev.channel!==0)||(hand==='lh'&&ev.channel!==1))continue;
        let duration=ev.duration;
        if(e.pedal){const boundary=(Math.floor(ev.start/bar)+1)*bar-.1;if(ev.start+duration<boundary)duration=boundary-ev.start;}
        tone(440*2**((ev.pitch-69)/12),at+intro+ev.start*unit,duration*unit,(ev.channel===0?.12:.065)*(ev.velocity/78));
      }
      status.textContent=`正在播放${hand==='all'?'双手':hand==='rh'?'右手':e.left_role==='bass-reference'?'贝斯参照':'左手'} · ${Math.round(speed*100)}% 速度 · 先听预备拍`;
      active=status;
      timer=setTimeout(()=>{status.textContent='播放结束；可以再听，也可以离开示范自己弹';nodes=[];active=null},(intro+e.rh.length*bar*unit+.5)*1000);
    }catch(error){status.textContent='播放未启动，请展开“音频与可编辑乐谱”使用音频文件。';console.error(error);}
  }
  for(const panel of document.querySelectorAll('.player')){
    panel.querySelectorAll('[data-hand]').forEach(b=>b.addEventListener('click',()=>play(panel,b.dataset.hand)));
    panel.querySelector('.stop').addEventListener('click',stop);
  }
  document.addEventListener('play',event=>{if(event.target.tagName==='AUDIO'){stop();document.querySelectorAll('audio').forEach(a=>{if(a!==event.target)a.pause()})}},true);
  window.addEventListener('pagehide',stop);
})();

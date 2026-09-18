# -*- coding: utf-8 -*-
"""生成「时代脊梁 · 群星谱」30 位人物页面。每个页面自包含（内联 CSS + JS），无外部资源。"""
import os, json, urllib.parse

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def darken(h, f=0.55):
    r, g, b = hex_to_rgb(h)
    return '#%02X%02X%02X' % (int(r*f), int(g*f), int(b*f))

def rgba(h, a):
    r, g, b = hex_to_rgb(h)
    return 'rgba(%d,%d,%d,%.2f)' % (r, g, b, a)

FIELD_VARIANT = {'科学': 'scientist', '劳模工匠': 'worker', '楷模': 'model', '文人': 'scholar', '医者': 'doctor'}
FEMALE = {'屠呦呦', '张桂梅', '黄文秀', '申纪兰', '林巧稚'}

# —————————————————————————— CSS ——————————————————————————
BASE_CSS = """
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{background-color:var(--paper);background-image:var(--bg-image);background-size:var(--bg-size);color:var(--ink);font-family:var(--sans);line-height:1.85;-webkit-font-smoothing:antialiased;min-height:100vh}
  body::before{content:"";position:fixed;inset:0;z-index:-1;background-image:var(--bgurl);background-size:cover;background-position:center;opacity:.13;filter:saturate(.72) contrast(1.06);pointer-events:none}
  .wrap{max-width:760px;margin:0 auto;padding:0 24px}
  a{color:inherit}

  .topbar{border-bottom:1px solid var(--line);padding:12px 0;position:sticky;top:0;background:rgba(239,233,218,.9);backdrop-filter:blur(6px);z-index:40}
  .topbar .wrap{display:flex;align-items:center;justify-content:space-between;gap:10px}
  .topbar a{text-decoration:none;color:var(--ink-soft);font-family:var(--kai);font-size:13px;letter-spacing:1px}
  .topbar a:hover{color:var(--c-deep)}
  .topbar .hall{font-family:var(--serif);font-size:14px;letter-spacing:3px;color:var(--ink)}
  .m-seal{height:22px;width:22px;object-fit:contain;vertical-align:middle;margin-right:6px;filter:drop-shadow(0 1px 3px rgba(178,58,46,.3))}

  /* hero */
  .hero{padding:46px 0 8px;display:grid;grid-template-columns:auto 1fr;gap:34px;align-items:center}
  .hero .side{display:flex;flex-direction:column;align-items:center;gap:20px}
  .seal{width:96px;height:96px;border-radius:16px;background:var(--cinnabar);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;transform:rotate(-5deg);box-shadow:0 10px 26px rgba(178,58,46,.3);font-family:var(--kai);line-height:1.08;animation:stamp .5s cubic-bezier(.2,1.4,.4,1) .05s both}
  .seal span{font-size:30px;letter-spacing:2px}
  .seal small{font-size:10px;letter-spacing:3px;opacity:.92}
  .vname{writing-mode:vertical-rl;font-family:var(--serif);font-weight:700;font-size:clamp(30px,6vw,46px);letter-spacing:8px;color:var(--ink);line-height:1.15}
  .portrait-wrap{position:relative;width:164px;height:206px;border-radius:12px;background:linear-gradient(135deg,var(--c),var(--c-deep));box-shadow:0 14px 34px var(--c-shadow);overflow:visible}
  .portrait{display:block;width:100%;height:100%;object-fit:cover;border-radius:12px;border:3px solid var(--c);filter:grayscale(.14) contrast(1.08) saturate(.96)}
  .portrait-wrap .seal{position:absolute;right:-14px;bottom:-14px;width:66px;height:66px;font-size:20px}
  .portrait-wrap .seal span{font-size:22px}
  .hero3d{position:absolute;inset:0;border-radius:12px;overflow:hidden;background:linear-gradient(135deg,var(--c),var(--c-deep))}
  .hero3d canvas{display:block}
  @keyframes stamp{from{transform:rotate(-5deg) scale(1.6);opacity:0}to{transform:rotate(-5deg) scale(1);opacity:1}}
  .hero .main .kicker{font-family:var(--kai);font-size:13px;letter-spacing:4px;color:var(--c-deep);margin-bottom:12px}
  .hero .main h1{font-family:var(--serif);font-size:clamp(32px,7vw,54px);letter-spacing:4px;line-height:1.1;margin-bottom:8px}
  .hero .main .identity{font-family:var(--kai);font-size:clamp(16px,2.8vw,19px);color:var(--ink-soft);letter-spacing:1px;margin-bottom:16px}
  .slogan{font-family:var(--kai);font-size:clamp(15px,2.5vw,17px);color:var(--c-deep);line-height:1.9;letter-spacing:1px;border-left:3px solid var(--c);padding-left:14px;margin-bottom:12px}
  .curator{font-family:var(--kai);font-size:12px;color:var(--ink-soft);letter-spacing:2px}
  .ink-divider{display:flex;align-items:center;gap:10px;margin:20px 0 0;color:var(--c)}
  .ink-divider::before,.ink-divider::after{content:"";height:1px;flex:1;background:linear-gradient(90deg,transparent,var(--c))}
  .ink-divider::after{background:linear-gradient(90deg,var(--c),transparent)}

  .voice-btn{margin-top:16px;display:inline-flex;align-items:center;gap:8px;border:2px solid var(--c);background:var(--c);color:#fff;font-family:var(--kai);font-size:15px;letter-spacing:2px;padding:10px 20px;border-radius:10px;cursor:pointer;box-shadow:0 6px 16px var(--c-shadow);transition:transform .2s ease,background .2s ease}
  .voice-btn:hover{transform:translateY(-2px)}
  .voice-btn.speaking{background:var(--cinnabar);border-color:var(--cinnabar);animation:voicepulse 1.1s infinite}
  @keyframes voicepulse{0%,100%{box-shadow:0 0 0 0 rgba(178,58,46,.45)}50%{box-shadow:0 0 0 14px rgba(178,58,46,0)}}
  .portrait-wrap{animation:floaty 6s ease-in-out infinite}
  @keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
  .reveal{opacity:0;transform:translateY(26px);transition:opacity .8s cubic-bezier(.2,.7,.2,1),transform .8s cubic-bezier(.2,.7,.2,1)}
  .reveal.in{opacity:1;transform:none}

  section{margin-top:42px}
  .sec-head{display:flex;align-items:center;gap:14px;margin-bottom:20px}
  .sec-num{width:44px;height:44px;flex:0 0 44px;background:var(--c);color:#fff;display:flex;align-items:center;justify-content:center;font-family:var(--serif);font-size:21px;box-shadow:0 4px 12px var(--c-shadow)}
  .sec-num{clip-path:var(--num-shape)}
  .sec-head h2{font-family:var(--serif);font-size:23px;letter-spacing:4px}
  .sec-head .sub{font-family:var(--kai);font-size:13px;color:var(--ink-soft);margin-left:auto;letter-spacing:1px}

  .panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:24px 26px;box-shadow:0 3px 16px var(--shadow)}
  .identity-line{font-family:var(--kai);font-size:17px;line-height:2;padding-bottom:16px;border-bottom:1px dashed var(--line);margin-bottom:8px}
  .identity-line b{color:var(--c-deep)}
  .timeline{list-style:none;position:relative;padding-left:26px}
  .timeline::before{content:"";position:absolute;left:8px;top:8px;bottom:8px;width:2px;background:linear-gradient(var(--c),var(--c-tint2))}
  .timeline li{position:relative;padding:11px 0}
  .timeline li::before{content:"";position:absolute;left:-24px;top:19px;width:12px;height:12px;background:#fff;border:3px solid var(--c)}
  .timeline li::before{clip-path:var(--num-shape)}
  .timeline .year{font-family:var(--serif);font-weight:700;color:var(--c-deep);font-size:16px;letter-spacing:1px}
  .timeline .txt{font-size:15px;color:var(--ink);margin-top:2px}
  .timeline .src{display:inline-block;font-family:var(--kai);font-size:12px;color:var(--c-deep);background:var(--c-tint);border:1px solid var(--c-line);border-radius:4px;padding:2px 10px;margin-top:6px;letter-spacing:1px}

  .scene{display:grid;grid-template-columns:auto 1fr;gap:20px;align-items:start;padding:22px 24px;margin-bottom:16px}
  .scene:last-child{margin-bottom:0}
  .scene .illu{width:72px;height:72px;border-radius:14px;background:linear-gradient(135deg,var(--c),var(--c-deep));display:flex;align-items:center;justify-content:center;font-size:36px;box-shadow:0 6px 16px var(--c-shadow)}
  .scene h3{font-family:var(--serif);font-size:18px;letter-spacing:2px;color:var(--c-deep);margin-bottom:8px}
  .scene p{font-size:15px;color:var(--ink)}
  .scene p .q{color:var(--c-deep);font-family:var(--kai)}

  .moments{margin-top:18px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px;box-shadow:0 3px 16px var(--shadow)}
  .m-head{font-family:var(--kai);font-size:13px;color:var(--ink-soft);letter-spacing:2px;margin-bottom:13px}
  .post{display:flex;gap:12px}
  .post .avatar{width:44px;height:44px;flex:0 0 44px;border-radius:9px;background:linear-gradient(135deg,var(--c),var(--c-deep));display:flex;align-items:center;justify-content:center;font-size:22px}
  .post .p-body{flex:1;min-width:0}
  .post .p-name{font-family:var(--serif);font-weight:700;color:var(--c-deep);font-size:15px}
  .post .p-text{font-size:14px;margin-top:4px}
  .post .p-pic{margin-top:10px;border-radius:10px;background:linear-gradient(120deg,var(--c),var(--c-deep));padding:16px 12px;text-align:center;font-size:20px;letter-spacing:8px;color:#fff}
  .comments{margin-top:11px;background:var(--c-tint);border-radius:10px;padding:11px 13px}
  .comments .c{display:flex;gap:8px;font-size:13px;color:var(--ink-soft);padding:4px 0}
  .comments .c b{color:var(--c-deep);flex:0 0 auto}

  .codes{display:flex;flex-wrap:wrap;gap:13px}
  .code-tag{cursor:pointer;border:2px solid var(--c);color:var(--c-deep);background:transparent;font-family:var(--kai);font-size:15px;letter-spacing:2px;padding:10px 20px;border-radius:8px;transition:all .2s ease;user-select:none}
  .code-tag:hover{background:var(--c-tint);transform:translateY(-2px)}
  .code-tag.active{background:var(--c);color:#fff;box-shadow:0 6px 16px var(--c-shadow)}
  .code-reveal{margin-top:18px;max-height:0;opacity:0;overflow:hidden;transition:max-height .4s ease,opacity .4s ease;background:var(--c-tint);border-left:4px solid var(--c);border-radius:8px;padding:0 18px}
  .code-reveal.show{max-height:240px;opacity:1;padding:15px 18px}
  .code-reveal .r-label{font-family:var(--kai);font-size:13px;color:var(--c-deep);letter-spacing:2px}
  .code-reveal .r-quote{font-family:var(--kai);font-size:16px;margin-top:6px;line-height:1.9}

  .compare{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-top:18px}
  .compare .side{border-radius:11px;padding:18px 18px}
  .compare .left{background:var(--c-tint);border:1px dashed var(--c-line)}
  .compare .right{background:var(--c-tint2);border:1px dashed var(--c-line)}
  .compare .tag{font-family:var(--kai);font-size:12px;letter-spacing:2px;color:var(--ink-soft);margin-bottom:9px}
  .compare p{font-size:14px;line-height:1.85}
  .compare .left p{font-family:var(--kai);color:var(--c-deep)}

  .sayings .quote-line{font-family:var(--kai);font-size:clamp(16px,2.6vw,19px);line-height:2;padding:10px 0 10px 32px;position:relative}
  .sayings .quote-line::before{content:"“";position:absolute;left:0;top:0;font-size:42px;line-height:1;color:var(--c);font-family:var(--serif)}
  .award{margin-top:20px;text-align:center;background:linear-gradient(160deg,var(--c),var(--c-deep));color:#fff;border-radius:12px;padding:28px 28px 24px;box-shadow:0 12px 30px var(--c-shadow);position:relative}
  .award .a-label{font-family:var(--kai);font-size:12px;letter-spacing:6px;opacity:.94;margin-bottom:10px}
  .award .a-text{font-family:var(--serif);font-size:16px;line-height:2.05;letter-spacing:1px;text-align:justify}

  .curator-note{text-align:center;padding:24px 26px;background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:0 3px 16px var(--shadow)}
  .curator-note p{font-family:var(--kai);font-size:15px;line-height:2.05;letter-spacing:1px}
  .curator-note .sig{margin-top:12px;font-family:var(--kai);color:var(--c-deep);letter-spacing:2px}

  .guest{margin-top:38px;padding:24px 26px;border-radius:12px;background:var(--c-tint);border:1px dashed var(--c-line)}
  .guest .g-head{font-family:var(--serif);font-size:16px;letter-spacing:2px;margin-bottom:12px}
  .guest input{width:100%;border:1px solid var(--line);border-radius:9px;padding:11px 13px;font-size:14px;font-family:var(--sans);color:var(--ink);background:var(--card);outline:none}
  .guest input::placeholder{color:#B3A98F}
  .guest .g-actions{display:flex;align-items:center;justify-content:space-between;margin-top:11px;gap:12px}
  .guest .g-btn{border:none;background:var(--c);color:#fff;font-family:var(--kai);font-size:14px;letter-spacing:2px;padding:8px 18px;border-radius:8px;cursor:pointer;box-shadow:0 4px 12px var(--c-shadow)}
  .guest .g-tip{font-family:var(--kai);font-size:12px;color:var(--ink-soft)}

  footer{margin-top:38px;padding:24px 0 42px;border-top:1px solid var(--line);text-align:center}
  footer a{font-family:var(--kai);font-size:14px;color:var(--c-deep);text-decoration:none;letter-spacing:2px}
  footer p{font-family:var(--kai);font-size:12px;color:var(--ink-soft);margin-top:9px;letter-spacing:2px}

  @media (max-width:640px){
    .hero{grid-template-columns:1fr;gap:18px}
    .hero .side{flex-direction:row;justify-content:center;gap:16px}
    .vname{writing-mode:horizontal-tb;font-size:clamp(30px,9vw,44px);letter-spacing:5px}
    .scene{grid-template-columns:1fr}
    .compare{grid-template-columns:1fr}
  }
  @media (prefers-reduced-motion:reduce){*{transition:none!important}.seal{animation:none}.code-tag:hover{transform:none}.portrait-wrap{animation:none}.voice-btn.speaking{animation:none}.reveal{opacity:1;transform:none}}
"""

# 变体差异：背景纹理 / 板块编号形状
VARIANT_CSS = {
 'scholar': """
  :root{--num-shape:polygon(0 0,100% 0,100% 82%,82% 100%,0 100%);--bg-image:radial-gradient(120% 80% at 50% -10%,rgba(255,255,255,.5),transparent 55%),radial-gradient(60% 40% at 85% 15%,rgba(0,0,0,.05),transparent 70%),radial-gradient(var(--paper-deep) 1px,transparent 1px);--bg-size:100% 100%,100% 100%,28px 28px}
 """,
 'scientist': """
  :root{--num-shape:circle(50% at 50% 50%);--bg-image:radial-gradient(120% 80% at 50% -10%,rgba(255,255,255,.5),transparent 55%),radial-gradient(var(--c-tint2) 1.2px,transparent 1.2px);--bg-size:100% 100%,26px 26px}
 """,
 'worker': """
  :root{--num-shape:polygon(50% 0,100% 50%,50% 100%,0 50%);--bg-image:radial-gradient(120% 80% at 50% -10%,rgba(255,255,255,.5),transparent 55%),repeating-linear-gradient(90deg,var(--c-line) 0 1px,transparent 1px 12px);--bg-size:100% 100%,100% 100%}
 """,
 'model': """
  :root{--num-shape:polygon(0 0,100% 0,100% 100%,0 100%);--bg-image:radial-gradient(120% 80% at 50% -10%,rgba(255,255,255,.5),transparent 55%),repeating-linear-gradient(0deg,rgba(0,0,0,.02) 0 1px,transparent 1px 5px);--bg-size:100% 100%,100% 100%}
 """,
 'doctor': """
  :root{--num-shape:circle(50% at 50% 50%);--bg-image:radial-gradient(120% 80% at 50% -10%,rgba(255,255,255,.55),transparent 55%),radial-gradient(var(--c-tint2) 1px,transparent 1px);--bg-size:100% 100%,22px 22px}
 """,
}

EXTRA_JS = """<script>
(function(){
  var btn=document.getElementById('voice-btn');
  if(!btn) return;
  var narration=btn.getAttribute('data-narration')||'';
  var src=btn.getAttribute('data-audio');
  var audio=src?new Audio(src):null;
  var playing=false;
  function setState(s){playing=s;btn.classList.toggle('speaking',s);btn.innerHTML=s?'⏹ 停止讲解':'🔊 语音讲解';}
  function end(){setState(false);}
  function tts(){
    if(!('speechSynthesis' in window)){btn.textContent='⚠ 无法播放语音';return;}
    var u=new SpeechSynthesisUtterance(narration);u.lang='zh-CN';u.rate=0.95;
    var v=(speechSynthesis.getVoices()||[]).filter(function(x){return /zh|cmn|Chinese/i.test(x.lang);})[0];
    if(v)u.voice=v;
    u.onstart=function(){setState(true);};u.onend=end;u.onerror=end;
    speechSynthesis.cancel();speechSynthesis.speak(u);
  }
  btn.addEventListener('click',function(){
    if(playing){
      if(audio){audio.pause();audio.currentTime=0;}else{speechSynthesis.cancel();}
      setState(false);return;
    }
    if(audio){
      audio.onended=end;
      audio.onerror=function(){tts();};
      audio.play().then(function(){setState(true);}).catch(function(){tts();});
    }else{
      tts();
    }
  });
})();
</script>
<script>
(function(){
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var els=document.querySelectorAll('.reveal');
  if(reduce||!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in');});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}});},{threshold:.1});
  els.forEach(function(e){io.observe(e);});
})();
</script>
<script>
(function(){
  var el=document.getElementById('hero3d');
  if(!el||typeof THREE==='undefined') return;
  var color=el.getAttribute('data-color')||'#8C6A3F';
  var img=el.getAttribute('data-img')||'';
  var name=el.getAttribute('data-name')||'';
  var W=el.clientWidth||164, H=el.clientHeight||206;
  var scene=new THREE.Scene();
  var camera=new THREE.PerspectiveCamera(42,W/H,0.1,50);
  camera.position.set(0,0.2,6);
  var renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setSize(W,H); renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.setClearColor(0x000000,0);
  el.appendChild(renderer.domElement);
  scene.add(new THREE.AmbientLight(0x888888,1.1));
  var key=new THREE.PointLight(color,1.5,30); key.position.set(3,4,6); scene.add(key);
  var rim=new THREE.PointLight(0xffffff,0.7,30); rim.position.set(-4,2,-2); scene.add(rim);
  var wall=new THREE.Mesh(new THREE.PlaneGeometry(12,12),new THREE.MeshStandardMaterial({color:0x2a241d,roughness:0.95}));
  wall.position.z=-4; scene.add(wall);
  var grp=new THREE.Group(); scene.add(grp);
  var portrait=new THREE.Mesh(new THREE.PlaneGeometry(2.5,3.3),new THREE.MeshStandardMaterial({color:color,roughness:0.5}));
  grp.add(portrait);
  if(img){
    new THREE.TextureLoader().load(img,function(t){
      var iw=t.image.width||1, ih=t.image.height||1, a=iw/ih, fa=2.5/3.3;
      var sx=a>fa?1:a/fa, sy=a>fa?fa/a:1;
      portrait.scale.set(sx,sy,1);
      portrait.material=new THREE.MeshStandardMaterial({map:t,roughness:0.55});
    });
  }
  var cv=document.createElement('canvas'); cv.width=512; cv.height=140;
  var cx=cv.getContext('2d'); cx.clearRect(0,0,512,140);
  cx.fillStyle='#E8C77F'; cx.font='bold 58px "Songti SC","STSong",serif'; cx.textAlign='center'; cx.textBaseline='middle';
  cx.fillText(name,256,70);
  var lt=new THREE.CanvasTexture(cv); lt.minFilter=THREE.LinearFilter;
  var label=new THREE.Mesh(new THREE.PlaneGeometry(2.5,0.65),new THREE.MeshBasicMaterial({map:lt,transparent:true}));
  label.position.y=-2.15; grp.add(label);
  var yaw=-0.4, auto=true, down=null;
  el.addEventListener('pointerdown',function(e){down={x:e.clientX,y:e.clientY};auto=false;});
  window.addEventListener('pointermove',function(e){if(down){yaw+=(e.clientX-down.x)*0.01;down.x=e.clientX;}});
  window.addEventListener('pointerup',function(){down=null;setTimeout(function(){auto=true;},1500);});
  function loop(){requestAnimationFrame(loop);if(auto)yaw+=0.004;grp.rotation.y=yaw;renderer.render(scene,camera);}
  loop();
})();
</script>
"""

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} · {title}｜群星脊梁博物馆</title>
<style>
  :root{{
    --paper:#EFE9DA;--paper-deep:#E4DCC6;--ink:#2E2921;--ink-soft:#6C6453;
    --cinnabar:#B23A2E;--c:{color};--c-deep:{deep};--c-tint:{tint1};--c-tint2:{tint2};--c-line:{tint3};--c-shadow:{shadow};--bgurl:{bgurl};
    --line:rgba(46,41,33,.14);--card:#FBF7EC;--shadow:rgba(46,41,33,.07);
    --serif:"Songti SC","STSong","Noto Serif SC",SimSun,serif;
    --kai:"Kaiti SC","KaiTi","FangSong",serif;
    --sans:"PingFang SC","Microsoft YaHei",-apple-system,sans-serif;
  }}
  {variant_css}
  {base_css}
</style>
<script src="js/three.min.js"></script>
</head>
<body>

  <div class="topbar">
    <div class="wrap">
      <a href="index.html"><img class="m-seal" src="images/seal.png" alt="馆印">返回博物馆</a>
      <span class="hall">{title}</span>
    </div>
  </div>

  <header class="hero wrap">
    <div class="side">
      <div class="portrait-wrap">
        <div class="hero3d" id="hero3d" data-color="{color}" data-img="{img_attr}" data-name="{name}"></div>
        <div class="seal"><span>{seal}</span><small>馆 印</small></div>
      </div>
      <div class="vname">{vname}</div>
    </div>
    <div class="main">
      <div class="kicker">{era} · {field} · 时代脊梁</div>
      <h1>{name}</h1>
      <div class="identity">{identity}</div>
      <p class="slogan">{slogan}</p>
      <div class="curator">策展小组：Daniel · Rummy · Bohan · Steven</div>
      <div class="ink-divider"></div>
      <button class="voice-btn" id="voice-btn" data-narration="{narration_attr}" data-audio="{audio_src}">🔊 语音讲解</button>
    </div>
  </header>

  <main class="wrap">

    <section class="reveal">
      <div class="sec-head"><div class="sec-num">一</div><h2>人物档案</h2><span class="sub">一句话身份 · 关键节点</span></div>
      <div class="panel">
        <p class="identity-line">{identity}</p>
        <ul class="timeline">{nodes}</ul>
      </div>
    </section>

    <section class="reveal">
      <div class="sec-head"><div class="sec-num">二</div><h2>高光时刻</h2><span class="sub">原文细节 · 为何是高光</span></div>
      {highlights}
      <div class="moments">
        <div class="m-head">📱 如果他有朋友圈</div>
        <div class="post">
          <div class="avatar">{moments_emoji}</div>
          <div class="p-body">
            <div class="p-name">{name}</div>
            <div class="p-text">{moments_text}</div>
            <div class="p-pic">{moments_pic}</div>
            <div class="comments">{moments_comments}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="reveal">
      <div class="sec-head"><div class="sec-num">三</div><h2>精神密码</h2><span class="sub">点击标签，看原文</span></div>
      <div class="codes">{codes}</div>
      <div class="code-reveal" id="code-reveal"><div class="r-label" id="code-label"></div><div class="r-quote" id="code-quote"></div></div>
      <div class="compare">
        <div class="side left"><div class="tag">📖 课本 / 史实里的他</div><p>“{compare_left}”</p></div>
        <div class="side right"><div class="tag">✍️ 我眼中的他</div><p>{compare_right}</p></div>
      </div>
    </section>

    <section class="reveal">
      <div class="sec-head"><div class="sec-num">四</div><h2>感动箴言</h2><span class="sub">人物原话 · 颁奖词</span></div>
      <div class="sayings panel">
        <p class="quote-line">{quote1}</p>
        <p class="quote-line">{quote2}</p>
      </div>
      <div class="award"><div class="a-label">颁 奖 词</div><div class="a-text">{award}</div></div>
    </section>

    <section class="reveal">
      <div class="sec-head"><div class="sec-num" style="background:var(--cinnabar)">尾</div><h2>策展人的话</h2><span class="sub">我们为什么这样策展</span></div>
      <div class="curator-note"><p>{curator}</p><div class="sig">—— {title}策展小组</div></div>
    </section>

    <section class="reveal guest">
      <div class="g-head">观众留言</div>
      <input type="text" placeholder="写下你想对{name}说的话……" aria-label="观众留言">
      <div class="g-actions"><button class="g-btn" type="button">留 言</button><span class="g-tip">仅装饰展示，无需真实提交</span></div>
    </section>

  </main>

  <footer>
    <a href="index.html">← 返回群星脊梁博物馆</a>
    <p>{name} · {title} · 策展小组：Daniel · Rummy · Bohan · Steven</p>
  </footer>

  <script>
    (function(){{
      var tags=document.querySelectorAll('.code-tag');
      var reveal=document.getElementById('code-reveal');
      var label=document.getElementById('code-label');
      var quote=document.getElementById('code-quote');
      var active=null;
      tags.forEach(function(tag){{
        tag.addEventListener('click',function(){{
          if(active===tag){{tag.classList.remove('active');reveal.classList.remove('show');active=null;return;}}
          tags.forEach(function(t){{t.classList.remove('active');}});
          tag.classList.add('active');
          label.textContent=tag.getAttribute('data-label');
          quote.textContent=tag.getAttribute('data-quote');
          reveal.classList.add('show');
          active=tag;
        }});
      }});
    }})();
  </script>

  {extra_js}

</body>
</html>
"""

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def esc_attr(s):
    return s.replace('&','&amp;').replace('"','&quot;').replace('<','&lt;').replace('>','&gt;')

def render_nodes(nodes):
    out = []
    for y, t, src in nodes:
        out.append('<li><span class="year">%s</span><p class="txt">%s</p><span class="src">出处：%s</span></li>' % (esc(y), esc(t), esc(src)))
    return ''.join(out)

def render_highlights(hl):
    out = []
    for emoji, title, text in hl:
        # text 含内联 <span class='q'>，不转义
        out.append('<div class="scene panel"><div class="illu">%s</div><div><h3>%s</h3><p>%s</p></div></div>' % (emoji, esc(title), text))
    return ''.join(out)

def render_codes(codes):
    out = []
    for label, quote in codes:
        out.append('<button class="code-tag" data-label="%s" data-quote="%s">%s</button>' % (esc(label), esc(quote), esc(label)))
    return ''.join(out)

def render_comments(comments):
    return ''.join('<div class="c"><b>%s</b>：%s</div>' % (esc(w), esc(x)) for w, x in comments)

def build(p, img=None):
    v = FIELD_VARIANT[p['field']]
    color = p['c']
    img = img or {}
    bgurl = "url('%s')" % img['bg'] if img.get('bg') else 'none'
    portrait_html = ('<img class="portrait" src="%s" alt="%s">' % (img['portrait'], p['name'])) if img.get('portrait') else ''
    pronoun = '她' if p['name'] in FEMALE else '他'
    codes_str = '、'.join(c[0] for c in p['codes'])
    def sp(s):
        return s.rstrip('。，、；！？ ')
    narration = '欢迎来到群星脊梁博物馆的%s。本厅致敬%s。%s。%s。%s留给我们的精神密码是：%s。' % (
        p['title'], p['name'], sp(p['identity']), sp(p['slogan']), pronoun, codes_str)
    return PAGE.format(
        name=p['name'], title=p['title'], seal=p['seal'],
        vname=p['name'], bgurl=bgurl, portrait_html=portrait_html,
        audio_src=('audio/' + urllib.parse.quote(p['name']) + '.mp3'),
        img_attr=(img.get('portrait') or ''),
        narration_attr=esc_attr(narration), extra_js=EXTRA_JS,
        era=p['era'], field=p['field'], identity=p['identity'], slogan=p['slogan'],
        color=color, deep=darken(color), tint1=rgba(color,0.10), tint2=rgba(color,0.18),
        tint3=rgba(color,0.34), shadow=rgba(color,0.30),
        variant_css=VARIANT_CSS[v], base_css=BASE_CSS,
        nodes=render_nodes(p['nodes']), highlights=render_highlights(p['highlights']),
        codes=render_codes(p['codes']),
        moments_emoji=p['moments']['emoji'], moments_text=p['moments']['text'],
        moments_pic=p['moments']['pic'], moments_comments=render_comments(p['moments']['comments']),
        compare_left=p['compare']['left'], compare_right=p['compare']['right'],
        quote1=p['quotes'][0], quote2=p['quotes'][1], award=p['award'], curator=p['curator'],
    )

# —————————————————————————— 30 位人物 ——————————————————————————
P = []
def add(**kw): P.append(kw)

# 1 袁隆平
add(name="袁隆平", title="稻浪厅", seal="稻浪", era="当代", field="科学", c="#C89B3C",
    identity="杂交水稻之父，首届国家最高科学技术奖获得者，“共和国勋章”获得者。",
    slogan="他把一生种进稻田，让亿万人的饭碗盛满稻香。",
    nodes=[("1961","在安江农校的稻田里，他发现一株“鹤立鸡群”的天然杂交稻，从此萌生了培育杂交水稻的梦想。","《喜看稻菽千重浪》"),
           ("1973","籼型杂交水稻“三系”配套成功，实现了水稻单产的历史性飞跃。","《喜看稻菽千重浪》"),
           ("2001","荣获首届国家最高科学技术奖，被誉为“杂交水稻之父”。","《喜看稻菽千重浪》"),
           ("2019","被授予“共和国勋章”，成为让中国人把饭碗牢牢端在自己手中的科学家。","《喜看稻菽千重浪》")],
    highlights=[("🌾","一株稻穗，一个世界","烈日下的试验田里，袁隆平挽起裤腿、赤脚下田，一株一株地寻觅。正是那一株<span class='q'>“鹤立鸡群”的天然杂交稻</span>，让他看见了杂交水稻的希望。从此，他的人生与稻田紧紧缠绕——他像一位最普通的农民，也像一位最执着的科学家。"),
                ("🌅","禾下乘凉梦","他做过一个浪漫的梦：<span class='q'>水稻长得像高粱那么高，穗子像扫帚那么长，谷粒像花生米那么大</span>，他和助手坐在稻穗下乘凉。这个梦，成了他毕生追逐的方向，也让千千万万人从此远离饥饿。")],
    codes=[("躬耕田垄","他像一位最普通的农民，挽起裤腿，赤脚下到田里，一株一株地寻觅。"),
           ("禾下乘凉","水稻长得像高粱那么高，穗子像扫帚那么长，谷粒像花生米那么大。"),
           ("一粒种子改变世界","一粒种子，可以改变一个世界；让所有人远离饥饿，是他毕生的追求。"),
           ("敢于追梦","我毕生的追求就是让所有人远离饥饿。")],
    quotes=["我毕生的追求就是让所有人远离饥饿。","人就像一粒种子，要做一粒好种子。"],
    award="他是一位真正的耕耘者。当他还是乡村教师的时候，已经具有颠覆世界权威的胆识；当他名满天下的时候，却仍然只是专注于田畴。淡泊名利，一介农夫，播撒智慧，收获富足。禾下乘凉，稻香千里——他用一粒种子改变了世界，也把中国人的饭碗，牢牢端在了自己手中。",
    curator="我们选袁隆平，因为他离泥土最近，却离天空最高。他把一生种进稻田，用一粒种子回答了“中国人能不能养活自己”这个天问。策展时我们最想让你看见的，是那个挽着裤腿、赤脚下田的背影——那才是脊梁最朴素的样子。",
    moments=dict(emoji="🌾", text="今天在试验田里走了一圈，稻穗沉甸甸的，看着就踏实。🌾", pic="🌾 🌾 🌾",
                 comments=[("学生","袁老师，您的“禾下乘凉梦”，我们记着呢！"),("同事","老袁，明天下田，叫上我。"),("后人","谢谢您，让我们顿顿有米饭。🍚")]),
    compare=dict(left="他像一位最普通的农民，挽起裤腿，赤脚下到田里。", right="原来“最伟大”的样子，是肯为一把稻子弯下腰、踩进泥里。"))

# 2 张秉贵
add(name="张秉贵", title="团火厅", seal="团火", era="当代", field="劳模工匠", c="#D9772E",
    identity="北京百货大楼糖果柜售货员，全国劳动模范，“一团火”精神的化身。",
    slogan="他用一把糖，称出了一个时代的人心。",
    nodes=[("站上柜台","20 世纪 50 年代，他站上北京百货大楼的糖果柜台，把三尺柜台当作为人民服务的舞台。","《心有一团火，温暖众人心》"),
           ("练就绝活","“一把抓”（抓糖一把准）、“一口清”（算账一口清），练成闻名全国的“柜台艺术”。","《心有一团火，温暖众人心》"),
           ("1979","获“全国劳动模范”称号，“一团火”精神传遍全国。","《心有一团火，温暖众人心》"),
           ("时代典范","他用满腔热忱温暖了每一位顾客，成为平凡岗位上为人民服务的时代典范。","《心有一团火，温暖众人心》")],
    highlights=[("🍬","“一把抓”的绝活","顾客要买一两糖，张秉贵伸手一抓，不多不少，正好一两；要二两，他两把并抓，<span class='q'>分毫不差</span>。这手“一把抓”的绝活背后，是数十年如一日的苦练。"),
                ("🔥","心有一团火","面对形形色色的顾客，他始终满面春风、热情似火。他说，售货员递出去的不只是商品，更是一团<span class='q'>温暖众人心</span>的火。")],
    codes=[("心有一团火","售货员递出去的不只是商品，更是一团温暖众人心的火。"),
           ("为人民服务","为人民服务，首先要对人民有感情。"),
           ("平凡岗位做到极致","一把抓、一口清，他把三尺柜台站成了艺术，把平凡做到了极致。"),
           ("温暖众人心","心有一团火，温暖众人心。")],
    quotes=["为人民服务，首先要对人民有感情。","站柜台，就是要站出个样子来。"],
    award="他是一名普通的售货员，却把三尺柜台站成了一座丰碑。一把抓、一口清，他用几十年的苦练，把平凡做到了极致；一团火、一颗心，他用满腔的热忱，温暖了一个时代的人心。他不是在卖糖，他是在称量一颗为人民服务的心。心有一团火，温暖众人心。",
    curator="我们选张秉贵，因为他没有惊天动地的伟业，只有三尺柜台。可正是这方寸之间，他站出了一个时代的精神高度。愿我们每个人，都能在自己的岗位上，燃起一团火。",
    moments=dict(emoji="🍬", text="今天又来了几位老顾客，隔着柜台都认识我，心里暖烘烘的。🍬", pic="🍬 🍭 🍬",
                 comments=[("同事","张师傅，您这“一把抓”，我们学一辈子！"),("顾客","谢谢您，每次买糖都像见老朋友。"),("后人","“一团火”精神，照亮了平凡的岗位。")]),
    compare=dict(left="为人民服务，首先要对人民有感情。", right="原来“服务”二字不是职业，而是一颗心里装得下别人的温度。"))

# 3 钟扬
add(name="钟扬", title="探界厅", seal="探界", era="当代", field="科学", c="#4A6FA5",
    identity="复旦大学生命科学学院教授、援藏 16 年的植物学家，国家种质资源库的建设者。",
    slogan="一粒种子，是他写给高原的情书；四千万颗，是他留给未来的答卷。",
    nodes=[("2001","主动请缨援藏，从此把课堂和实验室，一起搬上了青藏高原。","《“探界者”钟扬》"),
           ("建种子库","16 年间走遍高原，收集了 4000 多万颗植物种子，为未来储存了基因的“诺亚方舟”。","《“探界者”钟扬》"),
           ("珠峰采集","在珠峰北坡海拔 6200 米处，采集到迄今海拔最高的植物种子。","《“探界者”钟扬》"),
           ("2017","在出差途中遭遇车祸，不幸因公殉职，把生命留在了追梦的路上。","《“探界者”钟扬》")],
    highlights=[("🏔️","珠峰北坡的种子","在珠峰北坡海拔 6200 米处，顶着高原反应，钟扬采集到迄今<span class='q'>海拔最高</span>的植物种子。他说，高原的每一颗种子，都可能是未来的希望。"),
                ("🌱","高原上的行走","16 年间，他像一棵扎根高原的种子，走遍西藏的每一个角落。他把论文写在祖国最需要的地方，把种子<span class='q'>留给未来</span>。")],
    codes=[("种子精神","一个基因可以拯救一个国家，一粒种子可以造福万千苍生。"),
           ("高原坚守","16 年援藏，他把论文写在祖国最需要的地方，把课堂搬上青藏高原。"),
           ("追梦不止","不是杰出者才做梦，而是善梦者才杰出。"),
           ("为人师表","他像一棵扎根高原的种子，把知识与希望，一颗一颗埋进未来。")],
    quotes=["一个基因可以拯救一个国家，一粒种子可以造福万千苍生。","不是杰出者才做梦，而是善梦者才杰出。"],
    award="他是复旦的教授，更是高原的种子猎人。16 年援藏，四千万颗种子，他把论文写在祖国最需要的地方，把未来的基因装进一粒粒种子。珠峰北坡六千二百米的寒风里，有他蹒跚却坚定的脚步；雪域高原的课堂里，有他为人师表的温度。一粒种子，为他深爱的祖国，播下了万古长青的春天。",
    curator="我们选钟扬，因为他本可以安稳地待在城市的实验室里，却选择把一生种进海拔数千米的高原。他收集的每一颗种子，都是一句对未来的承诺。愿我们也能成为勇敢的善梦者。",
    moments=dict(emoji="🌱", text="今天又在海拔 5000 多米的地方采到一批种子，高原的阳光真亮。🌱", pic="🌱 🏔️ 🌱",
                 comments=[("学生","钟老师，您教我们的不只是植物，还有怎么追梦。"),("同事","注意身体，高原反应不是闹着玩的。"),("后人","种子已成林，谢谢您为未来存下希望。")]),
    compare=dict(left="一个基因可以拯救一个国家，一粒种子可以造福万千苍生。", right="原来“伟大”不是站在高处，而是把希望一颗一颗埋进未来。"))

# 4 高凤林
add(name="高凤林", title="匠心厅", seal="匠心", era="当代", field="劳模工匠", c="#3E5C76",
    identity="中国航天火箭发动机焊接大师，被誉为“焊接火箭心脏的人”，当代“大国工匠”。",
    slogan="毫厘之间，焊出中国航天的底气。",
    nodes=[("进厂学艺","20 世纪 80 年代，进入中国航天系统，从此与火箭发动机焊接结缘。","《以工匠精神雕琢时代品质》"),
           ("攻克难关","攻克火箭发动机喷管等关键部件的焊接难题，成为“焊接火箭心脏的人”。","《以工匠精神雕琢时代品质》"),
           ("0.08 毫米","练就 0.08 毫米级精度的焊接绝技，毫厘之间，不容一丝瑕疵。","《以工匠精神雕琢时代品质》"),
           ("大国工匠","获评“大国工匠”年度人物、全国劳动模范，一辈子一件事，为国铸剑。","《以工匠精神雕琢时代品质》")],
    highlights=[("🚀","焊接火箭的心脏","火箭发动机喷管焊接，上千摄氏度的高温，0.08 毫米的精度要求。高凤林手持焊枪，一焊就是几十年，<span class='q'>让中国的火箭稳稳腾空</span>。"),
                ("🔥","毫厘之间","焊点成百上千，每一处都必须严丝合缝。他说，<span class='q'>焊缝就是火箭的生命线</span>，容不得一丝瑕疵。")],
    codes=[("毫厘之间见匠心","0.08 毫米的精度，上千摄氏度的高温，毫厘之间，不容一丝瑕疵。"),
           ("一辈子一件事","我这一辈子，就干好焊接这一件事。"),
           ("为国铸剑","每一道焊缝，都连着火箭的成败，也连着国家的安全。"),
           ("追求极致","把一件事做到极致，就是工匠精神。")],
    quotes=["焊缝就是火箭的生命线，容不得一丝瑕疵。","我这一辈子，就干好焊接这一件事。"],
    award="他有一把焊枪，也有一颗为国铸剑的匠心。三十多年，他守在火箭发动机旁，把上千摄氏度的炉火、0.08 毫米的精度，焊进了中国航天的每一次腾空。焊缝即生命线，毫厘见真章。他不是在焊接金属，他是在用一辈子的专注，为大国重器筑牢最精细的根基。",
    curator="我们选高凤林，因为他让我们看见：真正的伟大，藏在一毫米之内的专注里。没有惊天动地的口号，只有几十年如一日的焊枪与炉火。肯把一件事做到极致的人，才是真正的脊梁。",
    moments=dict(emoji="⚙️", text="又一道焊缝通过检测，0.08 毫米，分毫不差。今天可以踏实下班了。⚙️", pic="⚙️ 🚀 🔥",
                 comments=[("工友","高师傅，您这手艺，就是我们的定心丸。"),("徒弟","师父，跟您学了十年，还差得远。"),("后人","致敬大国工匠，火箭腾空的背后有您。")]),
    compare=dict(left="工匠精神，是对精益求精的执着追求，是把品质与极致刻进骨子里的坚守。", right="原来“工匠”不是一种职业，而是把一件事做到极致的人生态度。"))

# 5 钱学森
add(name="钱学森", title="铸剑厅", seal="铸剑", era="近现代", field="科学", c="#2E4A6B",
    identity="中国航天之父，“两弹一星”功勋科学家，被誉为“中国导弹之父”。",
    slogan="他把一生锻造成箭，只为让祖国的尊严，升上星空。",
    nodes=[("1935","远渡重洋赴美求学，成为世界知名的空气动力学家。","人物生平"),
           ("1955","冲破重重阻挠回到祖国，决心用所学为新中国铸就大国重器。","人物生平"),
           ("1960","主持研制的第一枚导弹“东风一号”成功发射。","人物生平"),
           ("1970","参与研制的“东方红一号”卫星成功升空，中国进入航天时代。","人物生平")],
    highlights=[("🚀","五年归国路","他被美方软禁五年，却说<span class='q'>“科学无国界，科学家有祖国”</span>。回国时，他只有一个朴素的心愿：让中国有自己的导弹与卫星。"),
                ("🛰️","东方红，太空唱","1970 年，当《东方红》的旋律从太空传来，钱学森和同事们明白，<span class='q'>中国人也能叩问苍穹</span>了。")],
    codes=[("归国铸剑","科学无国界，科学家有祖国。"),
           ("自力更生","外国人能搞的，中国人为什么不能搞？"),
           ("严谨求实","我这一辈子，就为了一件事：让中国人挺直腰杆。"),
           ("淡泊名利","我姓钱，但我不爱钱。")],
    quotes=["科学无国界，科学家有祖国。","外国人能搞的，中国人为什么不能搞？"],
    award="他是中国航天的奠基人。五年归国路，十年两弹成。当别人追逐繁华，他选择回到一穷二白的祖国；当功成名就，他依旧住在朴素的旧楼里。他用一生证明：真正的脊梁，是把个人的聪明才智，全部献给祖国的尊严与梦想。",
    curator="我们选钱学森，因为他的人生只有一个方向——祖国。他本可以留在最富足的地方，却偏要回到最需要他的土地。他让我们明白，真正的“高级”，是把才华用在国家最需要的地方。",
    moments=dict(emoji="🚀", text="夜深了，图纸还没画完。这颗星，早晚要在中国的天空亮起来。🛰️", pic="🚀 🛰️ ⭐",
                 comments=[("同事","钱老，跟着您，我们心里有底。"),("学生","先生之风，山高水长。"),("后人","致敬，中国航天的领路人。")]),
    compare=dict(left="科学无国界，科学家有祖国。", right="原来“选择”的最高境界，是把才华种进祖国最需要的地方。"))

# 6 邓稼先
add(name="邓稼先", title="元勋厅", seal="元勋", era="近现代", field="科学", c="#B57A3A",
    identity="“两弹元勋”，中国核武器研制工作的开拓者和奠基者。",
    slogan="隐姓埋名二十八载，只为一声惊雷震山河。",
    nodes=[("1950","获物理学博士学位后毅然回国，投身新中国的建设。","人物生平"),
           ("1958","受命研制原子弹，从此隐姓埋名，家人不知其去向。","人物生平"),
           ("1964","中国第一颗原子弹爆炸成功，震惊世界。","人物生平"),
           ("1967","第一颗氢弹爆炸成功，中国核力量挺立东方。","人物生平")],
    highlights=[("💥","一声惊雷","大漠深处，他身先士卒。当原子弹在罗布泊腾起蘑菇云，<span class='q'>二十八年的隐姓埋名</span>，终于化作祖国的一声惊雷。"),
                ("🧪","以身许国","长期受到核辐射侵害，他身患癌症，却仍惦记着工作。他说，<span class='q'>假如能够再活一次，我仍选择中国</span>。")],
    codes=[("隐姓埋名","干惊天动地事，做隐姓埋名人。"),
           ("以身许国","假如能够再活一次，我仍选择中国。"),
           ("自力更生","再难，我们也要造出自己的原子弹。"),
           ("鞠躬尽瘁","一不为名，二不为利，只为国泰民安。")],
    quotes=["假如能够再活一次，我仍选择中国。","一不为名，二不为利，只为国泰民安。"],
    award="他是戈壁滩上的无名英雄。二十八载隐姓埋名，他把青春和健康都留给了大漠，只为让祖国不再受人欺凌。他走得早，却把最硬的底气，留给了身后的中国。邓稼先，一个让山河为之动容的名字。",
    curator="我们选邓稼先，因为他的一生是一场最安静的牺牲。没有鲜花和掌声，只有荒漠和算盘。他让我们懂得：最深沉的爱国，是把自己变成一粒铺路的沙。",
    moments=dict(emoji="💥", text="今天，蘑菇云升起来了。这些年，值了。", pic="💥 🏜️ ⭐",
                 comments=[("妻子","你终于能回来了，我给你留了一碗面。"),("同事","老邓，我们做到了。"),("后人","山河无恙，因你曾负重前行。")]),
    compare=dict(left="干惊天动地事，做隐姓埋名人。", right="原来最深的爱，是把名字都交给祖国。"))

# 7 屠呦呦
add(name="屠呦呦", title="青蒿厅", seal="青蒿", era="当代", field="科学", c="#5E8C5A",
    identity="诺贝尔生理学或医学奖得主，青蒿素的发现者，中国第一位本土诺奖女科学家。",
    slogan="一株青蒿，从古籍里长出了拯救千万生命的力量。",
    nodes=[("1969","临危受命，担任“523”抗疟项目中药组组长，寻找抗疟新药。","人物生平"),
           ("1972","从古籍《肘后备急方》获得灵感，成功提取青蒿素。","人物生平"),
           ("2015","因发现青蒿素荣获诺贝尔生理学或医学奖。","人物生平"),
           ("2019","被授予“共和国勋章”，一生淡泊，专注科研。","人物生平")],
    highlights=[("🌿","一株青蒿济苍生","她翻遍古籍，从<span class='q'>“青蒿一握，以水二升渍，绞取汁”</span>中悟出低温提取之法，终于让青蒿素问世，把数以百万计的生命从疟疾手中夺回。"),
                ("🏅","诺奖台上的中国人","她轻声说：<span class='q'>这不是我一个人的荣誉，是中国科学家集体的荣誉</span>。台下一片掌声。")],
    codes=[("青蒿济世","青蒿一握，以水二升渍，绞取汁。"),
           ("甘坐冷板凳","我不是为了荣誉，是为了救人。"),
           ("守正创新","中医药，是一座值得深挖的宝库。"),
           ("淡泊宁静","我没有什么别的爱好，就是喜欢做实验。")],
    quotes=["这不是我一个人的荣誉，是中国科学家集体的荣誉。","我是一名普通的科学工作者。"],
    award="她是中国科学的骄傲。几十年的寂寞坚守，她从一株不起眼的青蒿里，找到了拯救千万生命的良方。登上世界最高领奖台时，她依旧谦逊如初。她让我们相信：真正的伟大，藏在枯燥的实验室里，也藏在一颗淡泊而执着的心上。",
    curator="我们选屠呦呦，因为她证明了一件事：安静的力量，可以改变世界。她没有惊天动地的宣言，只有日复一日的实验。愿我们也能像她一样，坐得住冷板凳，守得住初心。",
    moments=dict(emoji="🌿", text="第 191 次实验，终于看到希望了。这株小草，了不起。", pic="🌿 🔬 💚",
                 comments=[("同事","屠老师，您是我们的定海神针。"),("学生","跟您做实验，心里踏实。"),("后人","谢谢您，让千万家庭不必再承受疟疾之痛。")]),
    compare=dict(left="青蒿一握，以水二升渍，绞取汁。", right="原来最伟大的发现，藏在一本旧书、一株小草里。"))

# 8 南仁东
add(name="南仁东", title="天眼厅", seal="天眼", era="当代", field="科学", c="#33505A",
    identity="FAST 射电望远镜（“中国天眼”）首席科学家、总工程师。",
    slogan="他把自己熬成一束光，为中国造了一只仰望宇宙的眼睛。",
    nodes=[("1994","提出建设中国自己的大射电望远镜，开启“天眼”之梦。","人物生平"),
           ("2007","“中国天眼”FAST 正式立项，选址贵州大窝凼。","人物生平"),
           ("2016","FAST 落成启用，成为世界最大单口径射电望远镜。","人物生平"),
           ("2017","积劳成疾，因病逝世，把生命留给了深空。","人物生平")],
    highlights=[("🔭","二十二年磨一镜","为给“天眼”找到最完美的家，他走遍贵州上百个洼地，<span class='q'>从壮年走到白发</span>，终于让 FAST 在群山间睁开巨眼。"),
                ("🌌","仰望星空的人","他说：<span class='q'>人类之所以脱颖而出，就是因为对宇宙有好奇</span>。他用一生，替我们仰望星空。")],
    codes=[("天眼问天","人类之所以脱颖而出，就是因为对宇宙有好奇。"),
           ("二十二年一诺","一件事，认准了，就做一辈子。"),
           ("自力更生","关键技术，必须掌握在中国人自己手里。"),
           ("仰望星空","别人能想到的，我们为什么不能做成世界第一？")],
    quotes=["人类之所以脱颖而出，就是因为对宇宙有好奇。","这个望远镜，是给未来的孩子们准备的。"],
    award="他是追星逐月的“天眼之父”。二十二年，他把一个近乎疯狂的构想，变成世界仰望的“中国天眼”。他见过贵州最深的洼地，也见过宇宙最远的光。他让我们知道：一个人若心怀宇宙，便没有到不了的远方。",
    curator="我们选南仁东，因为他的一生是一场向宇宙深处的跋涉。他用二十二年做一件事，把不可能变成可能。愿我们都能像他一样，仰望星空，也脚踏实地。",
    moments=dict(emoji="🔭", text="大窝凼的天，特别适合看星星。我们的“天眼”，快睁开了。", pic="🔭 🌌 ⭐",
                 comments=[("同事","南老师，注意身体，别太拼。"),("学生","跟着您，我们敢想世界第一。"),("后人","天眼已睁，请放心远望。")]),
    compare=dict(left="人类之所以脱颖而出，就是因为对宇宙有好奇。", right="原来“浪漫”是二十二年只做一件事，只为一束来自宇宙的光。"))

# 9 华罗庚
add(name="华罗庚", title="数魂厅", seal="数魂", era="近现代", field="科学", c="#3F6E8E",
    identity="著名数学家，中国解析数论、矩阵几何学的开拓者。",
    slogan="一个初中毕业的数学家，用一生向人民交卷。",
    nodes=[("1925","初中毕业后因家贫辍学，靠自学踏上数学之路。","人物生平"),
           ("1931","被清华破格聘用，从此在数学王国深耕。","人物生平"),
           ("1950","放弃海外优厚条件，回国效力。","人物生平"),
           ("1985","病逝于东京讲台之上，真正“工作到最后一刻”。","人物生平")],
    highlights=[("➗","自学成才的传奇","只读到初中，他却靠<span class='q'>每天 18 个小时的自学</span>，写出了轰动学界的论文。他说：<span class='q'>聪明在于勤奋，天才在于积累</span>。"),
                ("🎓","讲台上的最后一课","78 岁高龄，他在东京的讲台上倒了下去。他把生命，<span class='q'>献给了数学，也献给了讲台</span>。")],
    codes=[("自学成才","聪明在于勤奋，天才在于积累。"),
           ("为学为民","数学，是为了让人民用得上的科学。"),
           ("甘为人梯","我愿做青年人的铺路石。"),
           ("报效祖国","梁园虽好，非久居之乡。")],
    quotes=["聪明在于勤奋，天才在于积累。","梁园虽好，非久居之乡。"],
    award="他是从贫寒中走出来的数学大师。没有文凭，却有超乎常人的勤奋；没有师承，却有照亮后学的胸怀。他把高深的数学，化作了人民用得上的工具。华罗庚，用一生证明：天才不是天赋的恩赐，而是勤奋的果实。",
    curator="我们选华罗庚，因为他告诉我们：起点低不可怕，可怕的是停止攀登。一个只读到初中的人，靠勤奋成了数学大师。愿我们都能相信积累的力量。",
    moments=dict(emoji="➗", text="今天又解出一道难题，比过年还高兴。数学真美。", pic="➗ ✏️ 📐",
                 comments=[("学生","华先生，您是我们的灯塔。"),("同事","您这勤奋劲儿，我们追不上。"),("后人","谢谢您，让中国数学站上了世界舞台。")]),
    compare=dict(left="聪明在于勤奋，天才在于积累。", right="原来所谓“天才”，不过是把勤奋坚持到了极致。"))

# 10 李四光
add(name="李四光", title="寻矿厅", seal="寻矿", era="近现代", field="科学", c="#A98A4B",
    identity="地质学家，中国地质力学的创立者，为祖国找到大油田。",
    slogan="他把论文写在大地上，为祖国找回地下的宝藏。",
    nodes=[("1920","留学归国，任教于北京大学地质系。","人物生平"),
           ("1928","创立地质力学，开创中国地质研究新局面。","人物生平"),
           ("1955","主持全国石油普查，推翻“中国贫油论”。","人物生平"),
           ("1971","病逝于北京，一生献身地质与祖国。","人物生平")],
    highlights=[("⛏️","大地上的寻宝人","当“中国贫油”的论断盛行，李四光凭地质力学预言：<span class='q'>中国的地下有石油</span>。大庆、胜利、大港……一口口油井，验证了他的判断。"),
                ("🗺️","把论文写在祖国大地","他背着地质锤走遍山河，说：<span class='q'>科学要为国家建设服务</span>。")],
    codes=[("地质报国","中国的地下有石油，我们要把它找出来。"),
           ("脚踏实地","科学要为国家建设服务。"),
           ("敢于突破","不迷信权威，只相信事实。"),
           ("鞠躬尽瘁","我这一生，属于地质，属于祖国。")],
    quotes=["中国的地下有石油，我们要把它找出来。","科学要为国家建设服务。"],
    award="他是行走在祖国大地上的寻宝人。当别人说“中国贫油”，他用地质力学给出了不一样的答案。大庆油田的滚滚油流，是他献给祖国最好的答卷。他让我们明白：真正的知识，要落在祖国最需要的地方。",
    curator="我们选李四光，因为他把学问做在了祖国的大地上。他不迷信权威，只相信事实与脚步。愿我们也能像他一样，用知识报国，用双脚丈量。",
    moments=dict(emoji="⛏️", text="又发现一处含油构造。大庆的石油，就在我们脚下。", pic="⛏️ 🗺️ 🛢️",
                 comments=[("同事","李老，跟着您，我们敢说中国有油。"),("学生","先生之志，山高水长。"),("后人","滚滚油流，是对您最好的纪念。")]),
    compare=dict(left="中国的地下有石油，我们要把它找出来。", right="原来“敢于质疑”四个字，能为一个民族找回底气。"))

# 11 茅以升
add(name="茅以升", title="架桥厅", seal="架桥", era="近现代", field="科学", c="#4A6B82",
    identity="桥梁专家，中国现代桥梁事业的奠基人，钱塘江大桥主持者。",
    slogan="天堑变通途，他在江河之上架起中国人的脊梁。",
    nodes=[("1919","留学美国，成为卡内基理工学院第一位工学博士。","人物生平"),
           ("1933","主持建造钱塘江大桥，这是中国人自己设计建造的第一座现代大桥。","人物生平"),
           ("1937","大桥建成，又在抗战中亲手协助炸毁，立誓“不复原桥不丈夫”。","人物生平"),
           ("1955","主持建造武汉长江大桥，天堑从此变通途。","人物生平")],
    highlights=[("🌉","天堑架通途","钱塘江潮凶浪险，外国人断言中国人造不了这座桥。茅以升偏不信，<span class='q'>用中国人的智慧</span>，让第一座现代大桥横跨大江。"),
                ("💔","炸桥与造桥","抗战爆发，为阻断敌军，他忍痛亲手炸掉自己造的桥，含泪立誓：<span class='q'>不复原桥不丈夫</span>。")],
    codes=[("天堑通途","不复原桥不丈夫。"),
           ("自力更生","中国人的桥，要中国人自己造。"),
           ("精益求精","桥，是要用一百年的，容不得半点马虎。"),
           ("为国造桥","造桥，是为了让祖国走得更远。")],
    quotes=["不复原桥不丈夫。","桥，是要用一百年的，容不得半点马虎。"],
    award="他是中国桥梁之父。钱塘江上，他让“不可能”变成“天堑变通途”；武汉长江，他让南北牵手。造桥与炸桥之间，藏着一个工程师对祖国最深沉的爱。茅以升，用桥连通了山河，也连通了一个民族的自强之心。",
    curator="我们选茅以升，因为他用桥梁为祖国铺路。他造桥，也毁桥；毁桥，又复桥。这一造一毁一复之间，是一个知识分子最艰难的抉择，也是最坚定的担当。",
    moments=dict(emoji="🌉", text="武汉长江大桥今天通车，大江南北，终于连成一线。", pic="🌉 🌊 🚂",
                 comments=[("同事","茅老，您圆了中国人的造桥梦。"),("学生","跟着您，我们敢在江上架桥。"),("后人","一桥飞架南北，天堑变通途。")]),
    compare=dict(left="不复原桥不丈夫。", right="原来最硬的脊梁，是把国家的桥，架在自己心上。"))

# 12 于敏
add(name="于敏", title="铸盾厅", seal="铸盾", era="近现代", field="科学", c="#6E5B3A",
    identity="核物理学家，“氢弹之父”，我国氢弹理论的主要奠基人。",
    slogan="一张白纸，他算出了国之重器；一生隐姓，他守住了东方安宁。",
    nodes=[("1961","从原子核理论研究转向氢弹研制，从此隐姓埋名。","人物生平"),
           ("1967","中国第一颗氢弹爆炸成功，速度之快震惊世界。","人物生平"),
           ("1988","姓名解密，人们才第一次知道这位“氢弹之父”。","人物生平"),
           ("2019","被授予“共和国勋章”，一生淡泊，国之重器。","人物生平")],
    highlights=[("📜","从一张白纸算起","国外研制氢弹用了多年，中国却几乎从一张白纸起步。于敏和同事们用<span class='q'>算盘和头脑</span>，算出了氢弹的原理。"),
                ("🛡️","铸盾为和平","他说：<span class='q'>核武器不是用来打仗的，是用来保卫和平的</span>。这把国之盾，守住了东方的安宁。")],
    codes=[("隐姓埋名","核武器不是用来打仗的，是用来保卫和平的。"),
           ("白手起家","中国氢弹，要从一张白纸开始。"),
           ("国之重器","铸就利剑，是为了止戈为武。"),
           ("淡泊名利","国家需要我，我就义无反顾。")],
    quotes=["核武器不是用来打仗的，是用来保卫和平的。","国家需要我，我就义无反顾。"],
    award="他是“氢弹之父”，却长期不为人知。从一张白纸，到一朵蘑菇云，他用头脑和算盘，为中国铸就了最硬的盾。姓名可以隐去，功勋不会磨灭。于敏，用一生诠释了何为“国之重器，不彰自威”。",
    curator="我们选于敏，因为他把一生藏进了祖国最需要的地方。他不求名，不求利，只求国家安宁。愿我们都能懂得：有些脊梁，越是安静，越有力量。",
    moments=dict(emoji="🛡️", text="试验成功了。这些年的账，算得值。", pic="🛡️ 📜 ⭐",
                 comments=[("同事","于老，您是真正的国之栋梁。"),("学生","向隐姓埋名的英雄致敬。"),("后人","谢谢您，为我们铸就了和平之盾。")]),
    compare=dict(left="核武器不是用来打仗的，是用来保卫和平的。", right="原来“强大”的意义，不是攻击，而是守护。"))

# 13 孙家栋
add(name="孙家栋", title="北斗厅", seal="北斗", era="当代", field="科学", c="#4A90A5",
    identity="“两弹一星”功勋、探月工程总设计师、北斗卫星系统总设计师。",
    slogan="让北斗照亮十四亿人的方向，让中国卫星闪耀苍穹。",
    nodes=[("1967","担任中国第一颗人造卫星“东方红一号”的技术总负责人。","人物生平"),
           ("2004","出任北斗导航系统总设计师，开启北斗组网之路。","人物生平"),
           ("2020","北斗三号全球卫星导航系统全面建成。","人物生平"),
           ("功勋","一生主持研制 45 颗卫星，被誉为“卫星之父”。","人物生平")],
    highlights=[("🛰️","北斗指路","从“东方红一号”到北斗组网，他把一生交给卫星。他说：<span class='q'>中国人的导航，必须掌握在中国人手里</span>。"),
                ("🌏","星耀苍穹","如今，北斗已服务全球。这位白发老人说，<span class='q'>只要能做，我就一直做下去</span>。")],
    codes=[("北斗苍穹","中国人的导航，必须掌握在中国人手里。"),
           ("星辰大海","卫星，是给全人类指路的。"),
           ("久久为功","只要能做，我就一直做下去。"),
           ("赤子之心","国家需要，就是我的人生方向。")],
    quotes=["中国人的导航，必须掌握在中国人手里。","只要能做，我就一直做下去。"],
    award="他是中国卫星的缔造者。从“东方红一号”唱响太空，到北斗组网服务全球，他见证并铸就了中国航天的每一次腾飞。白发苍苍，初心不改。孙家栋，用一颗颗卫星，为中国人指明了方向，也为世界点亮了星光。",
    curator="我们选孙家栋，因为他把“仰望星空”做成了“脚踏实地”的毕生事业。他告诉我们，伟大的事业，从来不是一蹴而就，而是一颗一颗卫星，一次一次发射，慢慢攒出来的。",
    moments=dict(emoji="🛰️", text="北斗三号最后一颗卫星入轨。中国人的导航，成了。", pic="🛰️ 🌏 ⭐",
                 comments=[("同事","孙总，辛苦了，我们的北斗圆满了。"),("学生","跟着您，我们敢问苍穹。"),("后人","北斗指路，感恩有您。")]),
    compare=dict(left="中国人的导航，必须掌握在中国人手里。", right="原来“自力更生”，是连导航都不愿受制于人。"))

# 14 王进喜
add(name="王进喜", title="铁人厅", seal="铁人", era="近现代", field="劳模工匠", c="#A8743A",
    identity="大庆“铁人”，中国工人阶级的光辉榜样，全国劳动模范。",
    slogan="宁肯少活二十年，拼命也要拿下大油田。",
    nodes=[("1960","率 1205 钻井队奔赴大庆，参加石油大会战。","人物生平"),
           ("跳泥浆池","井喷危急时刻，他带头跳进泥浆池，用身体搅拌泥浆。","人物生平"),
           ("1964","出席全国人大，被誉为“铁人”。","人物生平"),
           ("1970","积劳成疾，病逝于大庆。","人物生平")],
    highlights=[("🛢️","跳进泥浆池","井喷，就意味着井毁人亡。危急关头，王进喜大喊一声，<span class='q'>纵身跳进泥浆池，用身体搅拌水泥</span>，硬是压住了井喷。"),
                ("🔥","宁肯少活二十年","他说：<span class='q'>宁肯少活二十年，拼命也要拿下大油田</span>。这掷地有声的誓言，成了“铁人精神”的注脚。")],
    codes=[("铁人精神","宁肯少活二十年，拼命也要拿下大油田。"),
           ("艰苦奋斗","有条件要上，没有条件创造条件也要上。"),
           ("为国分忧","国家缺油，就是我们最大的难。"),
           ("顽强拼搏","石油工人，就是要有股子拼命劲。")],
    quotes=["宁肯少活二十年，拼命也要拿下大油田。","有条件要上，没有条件创造条件也要上。"],
    award="他是中国工人阶级的一面旗帜。当国家缺油，他像铁人一样，用血肉之躯搅动泥浆，用拼命精神拿下油田。他让我们看到：脊梁，不只是挺直的腰杆，更是危难时刻豁出去的勇气。",
    curator="我们选王进喜，因为“铁人”二字，是中国工人最硬气的名字。他跳进泥浆池的那一刻，跳出了一个时代的热血与担当。愿我们都能有他这股子拼劲。",
    moments=dict(emoji="🛢️", text="井喷压住了！同志们，这口井，我们拿下了！", pic="🛢️ 🔥 ⛽",
                 comments=[("工友","王队长，您真是条汉子！"),("家属","老铁，注意身体啊。"),("后人","铁人精神，代代相传。")]),
    compare=dict(left="宁肯少活二十年，拼命也要拿下大油田。", right="原来“脊梁”最硬的，是危难时刻敢第一个跳下去的勇气。"))

# 15 时传祥
add(name="时传祥", title="净城厅", seal="净城", era="近现代", field="劳模工匠", c="#5C7A4A",
    identity="北京市环卫掏粪工人，全国劳动模范，被誉为“最美奋斗者”。",
    slogan="宁肯一人脏，换来万家净。",
    nodes=[("1950s","新中国成立后，成为一名光荣的环卫掏粪工人。","人物生平"),
           ("1959","当选全国劳动模范，受到党和国家领导人接见。","人物生平"),
           ("奉献","几十年如一日，用一根扁担，掏净了城市的角角落落。","人物生平"),
           ("精神","“宁愿一人脏，换来万家净”的精神，感动了一个时代。","人物生平")],
    highlights=[("🧹","一根扁担的坚守","他每天推着粪车、挑着扁担，走街串巷。有人嫌这活脏，他却说：<span class='q'>脏了我一个，干净千万家</span>。"),
                ("🏅","与领袖握手","作为劳模，他受到国家领导人接见。一双握过扁担的手，<span class='q'>握住了属于劳动者的尊严</span>。")],
    codes=[("一人脏万家净","宁肯一人脏，换来万家净。"),
           ("劳动光荣","掏粪，也是为人民服务。"),
           ("爱岗敬业","干一行，爱一行，钻一行。"),
           ("无私奉献","脏活累活，总得有人干。")],
    quotes=["宁肯一人脏，换来万家净。","掏粪，也是为人民服务。"],
    award="他是一名掏粪工人，却掏出了一个时代的洁净与尊严。一根扁担、一辆粪车，他走了几十年，把脏和累留给自己，把干净和方便留给千家万户。他让我们懂得：职业没有贵贱，劳动本身就是一种崇高。",
    curator="我们选时传祥，因为他用最平凡的职业，诠释了最不平凡的坚守。他让我们明白，一个人的价值，不取决于干什么，而取决于怎么干。",
    moments=dict(emoji="🧹", text="今天把几条胡同都掏干净了，孩子们上学，踩得舒坦。", pic="🧹 🏘️ 🌿",
                 comments=[("邻居","时师傅，您辛苦了。"),("工友","跟着您，我们不觉得这活低人一等。"),("后人","谢谢您，让城市更干净。")]),
    compare=dict(left="宁肯一人脏，换来万家净。", right="原来“体面”不是职业给的，是认真和担当挣来的。"))

# 16 许振超
add(name="许振超", title="振超厅", seal="振超", era="当代", field="劳模工匠", c="#3E6E8E",
    identity="青岛港码头桥吊司机，全国劳动模范，“振超效率”的创造者。",
    slogan="把中国效率装进集装箱，让世界看见中国速度。",
    nodes=[("1974","进入青岛港，成为一名码头工人。","人物生平"),
           ("自学","只有初中学历，却自学成才，练就桥吊绝活。","人物生平"),
           ("2003","创造每小时吊装集装箱的世界纪录——“振超效率”。","人物生平"),
           ("劳模","成为全国劳动模范、时代楷模。","人物生平")],
    highlights=[("🏗️","振超效率","在 40 米高的桥吊上，他把集装箱吊装速度一次次刷新，创下<span class='q'>“振超效率”</span>，让世界惊叹中国速度。"),
                ("📚","自学成才的码头工","他说：<span class='q'>工人也可以当专家</span>。靠着这股钻劲，他从普通工人，成长为技术权威。")],
    codes=[("振超效率","工人也可以当专家。"),
           ("终身学习","不学习，就会被时代甩下。"),
           ("精益求精","干，就要干出世界一流。"),
           ("实干兴邦","空谈误国，实干兴邦。")],
    quotes=["工人也可以当专家。","干，就要干出世界一流。"],
    award="他是一名码头工人，却把简单重复的吊装，做成了世界纪录。从只有初中学历，到响当当的技术专家，他用“振超效率”告诉世界：中国工人的双手，能创造惊人的速度，也能托起一个港口的骄傲。",
    curator="我们选许振超，因为他证明了“蓝领也能成专家”。他把最普通的岗位，干成了世界一流。愿我们都能相信：无论干什么，做到极致就是本事。",
    moments=dict(emoji="🏗️", text="今天又破纪录了。咱中国速度，不输任何人。", pic="🏗️ 🚢 📦",
                 comments=[("工友","许师傅，您是我们的榜样。"),("徒弟","跟着您，我们也要当专家。"),("后人","振超效率，中国名片。")]),
    compare=dict(left="工人也可以当专家。", right="原来“工匠”不分蓝领白领，只分用不用心。"))

# 17 焦裕禄
add(name="焦裕禄", title="焦桐厅", seal="焦桐", era="近现代", field="楷模", c="#4C7A52",
    identity="兰考县委书记，人民的好公仆，县委书记的榜样。",
    slogan="生也沙丘，死也沙丘，父老生死系。",
    nodes=[("1962","临危受命，赴内涝、风沙、盐碱“三害”严重的兰考任县委书记。","人物生平"),
           ("治三害","带病坚持工作，带领群众治沙、治水、治碱。","人物生平"),
           ("1964","积劳成疾，病逝于郑州，年仅 42 岁。","人物生平"),
           ("精神","“焦裕禄精神”成为全党学习的榜样。","人物生平")],
    highlights=[("🌳","种下一棵泡桐","为治风沙，他带头种泡桐。如今兰考遍地泡桐，人们叫它<span class='q'>“焦桐”</span>——那是他留给这片土地最深的牵挂。"),
                ("📋","最后一口气","肝癌剧痛，他用钢笔顶住肝部，把藤椅都顶破了。他说：<span class='q'>活着，我没治好沙丘，死了，也要看着你们把沙丘治好</span>。")],
    codes=[("鞠躬尽瘁","生也沙丘，死也沙丘，父老生死系。"),
           ("心系人民","当官一任，就要造福一方。"),
           ("艰苦奋斗","越是困难，越要往前冲。"),
           ("无私奉献","活着我没治好沙丘，死了也要看着你们治好。")],
    quotes=["活着我没治好沙丘，死了也要看着你们把沙丘治好。","吃别人嚼过的馍，没味道。"],
    award="他是县委书记的榜样。面对内涝、风沙、盐碱，他带病冲锋，用一根钢笔顶住肝痛，把生命最后一刻，都交给了兰考大地。他倒下了，却留下了一片泡桐，和一串刻进人民心里的名字——焦裕禄。",
    curator="我们选焦裕禄，因为他把“人民”二字，写在了生命的最后一页。他让我们懂得：真正的脊梁，是心里装着群众，唯独没有自己。",
    moments=dict(emoji="🌳", text="沙丘上的泡桐发芽了。等它们长成，风沙就治住了。", pic="🌳 🌾 ☀️",
                 comments=[("群众","焦书记，您就是我们的主心骨。"),("同事","您歇歇吧，我们来。"),("后人","焦桐成林，如您所愿。")]),
    compare=dict(left="活着我没治好沙丘，死了也要看着你们把沙丘治好。", right="原来“公仆”二字，是把人民的苦，扛在自己肩上。"))

# 18 雷锋
add(name="雷锋", title="雷锋精神厅", seal="雷锋", era="近现代", field="楷模", c="#4C6E3A",
    identity="共产主义战士，助人为乐的楷模，“雷锋精神”的代名词。",
    slogan="把有限的生命，投入到无限的为人民服务之中去。",
    nodes=[("1960","参军入伍，成为一名汽车兵。","人物生平"),
           ("日常","在平凡岗位上默默奉献，做了无数好事。","人物生平"),
           ("1962","因公殉职，年仅 22 岁。","人物生平"),
           ("精神","毛泽东题词“向雷锋同志学习”，雷锋精神代代相传。","人物生平")],
    highlights=[("🔩","一颗螺丝钉","他说：<span class='q'>我要像一颗永不生锈的螺丝钉</span>，党把我拧在哪里，我就在哪里闪闪发光。"),
                ("📔","一本日记","他的日记里写着：<span class='q'>人的生命是有限的，可是为人民服务是无限的</span>。这朴素的话，照亮了几代人。")],
    codes=[("螺丝钉精神","我要像一颗永不生锈的螺丝钉。"),
           ("为人民服务","把有限的生命，投入到无限的为人民服务之中去。"),
           ("助人为乐","做好事，不留名。"),
           ("爱岗敬业","对待同志要像春天般温暖。")],
    quotes=["把有限的生命，投入到无限的为人民服务之中去。","对待同志要像春天般温暖。"],
    award="他是一名普通的战士，却用短短 22 年，树起了一座永恒的精神丰碑。一颗螺丝钉、一本日记，他把平凡的善举，做成了不朽的精神。雷锋，一个名字，成了中华民族助人为乐最温暖的注脚。",
    curator="我们选雷锋，因为他的伟大，恰恰来自平凡。他没有惊天动地，却把每一件小事都做到了极致。愿我们都能在平凡的日子里，做一颗温暖的螺丝钉。",
    moments=dict(emoji="🔩", text="今天帮战友修好了车，心里特别踏实。", pic="🔩 📔 ⭐",
                 comments=[("战友","雷锋同志，好样的！"),("群众","谢谢你，不留名的好人。"),("后人","雷锋精神，永远年轻。")]),
    compare=dict(left="把有限的生命，投入到无限的为人民服务之中去。", right="原来“伟大”，是把每一件平凡的小事，都认真做到最好。"))

# 19 张桂梅
add(name="张桂梅", title="燃灯厅", seal="燃灯", era="当代", field="楷模", c="#B54A5E",
    identity="云南华坪女子高级中学校长，“七一勋章”获得者，大山女孩的“燃灯校长”。",
    slogan="我生来就是高山而非溪流，我欲于群峰之巅俯视平庸的沟壑。",
    nodes=[("1996","从大理来到贫困的华坪，投身教育。","人物生平"),
           ("2008","创办全国第一所免费女子高中。","人物生平"),
           ("坚守","拖着病体，走遍大山家访，把 1800 多名女孩送出大山。","人物生平"),
           ("2021","获颁“七一勋章”。","人物生平")],
    highlights=[("🏔️","燃灯者","她把一所免费女高，办成了大山里的希望。她说：<span class='q'>只要我还有一口气，就要站在讲台上</span>。"),
                ("🎓","把女孩送出大山","1800 多名女孩，从华坪女高走进大学、走向更广阔的天地。她们说：<span class='q'>张老师，是改变我们命运的人</span>。")],
    codes=[("燃灯者","只要我还有一口气，就要站在讲台上。"),
           ("我生来就是高山","我生来就是高山而非溪流。"),
           ("为女孩点灯","一个女孩受了教育，能改变三代人。"),
           ("无私奉献","我把这一生，都交给了这些孩子。")],
    quotes=["我生来就是高山而非溪流，我欲于群峰之巅俯视平庸的沟壑。","只要我还有一口气，就要站在讲台上。"],
    award="她是一盏灯，照亮了无数大山女孩的路。拖着病体，她翻山越岭家访；倾尽所有，她创办免费女高。她用生命托举生命，让“知识改变命运”不再是一句空话。张桂梅，一位燃灯者，把光种进了大山深处。",
    curator="我们选张桂梅，因为她让我们看见：一个人的坚守，可以改变一代人的命运。她瘦弱的身体里，藏着最磅礴的力量。愿我们都能成为照亮他人的一束光。",
    moments=dict(emoji="🏔️", text="今天又有一个孩子考上了大学。值了，都值了。", pic="🏔️ 📚 🎓",
                 comments=[("学生","张老师，谢谢您点亮了我的人生。"),("同事","您要注意身体啊。"),("后人","燃灯精神，薪火相传。")]),
    compare=dict(left="我生来就是高山而非溪流。", right="原来“师者”最深的含义，是用生命点亮另一个生命。"))

# 20 黄文秀
add(name="黄文秀", title="青春厅", seal="青春", era="当代", field="楷模", c="#C0603A",
    identity="广西百色乐业县百坭村驻村第一书记，脱贫攻坚的青春楷模。",
    slogan="把青春之花，绽放在祖国最需要的地方。",
    nodes=[("2016","北师大硕士毕业，毅然回到家乡广西。","人物生平"),
           ("2018","主动请缨，担任百坭村驻村第一书记。","人物生平"),
           ("2019","带领村民脱贫，却在扶贫路上遭遇山洪，不幸遇难。","人物生平"),
           ("精神","被追授“时代楷模”“全国优秀共产党员”。","人物生平")],
    highlights=[("🌸","青春之花","研究生毕业，她本可留在大城市，却选择回到大山。她说：<span class='q'>我是从大山里走出来的，应该回到大山里去</span>。"),
                ("🌧️","最后一程","暴雨夜，她惦记着村里的受灾群众，赶回百坭，却把生命永远留在了扶贫路上。<span class='q'>三十岁的青春，永远定格在山洪之中</span>。")],
    codes=[("青春奉献","我是从大山里走出来的，应该回到大山里去。"),
           ("心系群众","群众的事，就是我的事。"),
           ("担当作为","把论文写在祖国的大地上。"),
           ("初心不改","长征路上，我们这一代人接着走。")],
    quotes=["我是从大山里走出来的，应该回到大山里去。","群众的事，就是我的事。"],
    award="她是大山里走出的女儿，又回到大山，把青春献给了扶贫。三十岁的生命，短暂却炽热。她把百坭村的脱贫账本，写到了最后一页。黄文秀，用最年轻的生命，回答了“青春应该怎样度过”。",
    curator="我们选黄文秀，因为她让我们懂得：青春的价值，在于选择祖国最需要的地方。她的生命停在三十岁，却永远活在百坭村的山山水水间。",
    moments=dict(emoji="🌸", text="今天帮乡亲们卖出了最后一批砂糖橘。大家的笑，就是我的动力。", pic="🌸 🍊 🌧️",
                 comments=[("村民","文秀书记，我们想您。"),("同事","你是我们永远的榜样。"),("后人","青春之花，永不凋零。")]),
    compare=dict(left="我是从大山里走出来的，应该回到大山里去。", right="原来“回乡”不是退路，而是最勇敢的选择。"))

# 21 黄大年
add(name="黄大年", title="归国厅", seal="归国", era="当代", field="科学", c="#3A5A8A",
    identity="地球物理学家，战略科学家，让中国深地探测跻身世界前列。",
    slogan="心有大我、至诚报国，把祖国需要当作人生坐标。",
    nodes=[("2009","放弃海外优厚条件，全职回国，出任吉林大学教授。","人物生平"),
           ("攻关","带领团队攻关深地探测技术，填补多项国内空白。","人物生平"),
           ("2017","因积劳成疾，病逝于长春，年仅 58 岁。","人物生平"),
           ("荣誉","被追授“时代楷模”，一生报国。","人物生平")],
    highlights=[("🧭","心有大我","有人问他为什么回国，他说：<span class='q'>振兴中华，乃我辈之责</span>。他把自己交给了祖国，也交给了科研。"),
                ("⚡","与时间赛跑","他常说“我是在和时间赛跑”，<span class='q'>把一天当两天用</span>，只为让中国的深地探测早日走到世界前列。")],
    codes=[("心有大我","振兴中华，乃我辈之责。"),
           ("至诚报国","祖国需要，我就回来。"),
           ("只争朝夕","我是在和时间赛跑。"),
           ("甘为人梯","把机会，留给年轻人。")],
    quotes=["振兴中华，乃我辈之责。","我是在和时间赛跑。"],
    award="他是归国的赤子。放弃海外的荣华，他把毕生所学带回祖国，用生命与时间赛跑，让中国深地探测站上了世界之巅。他走得匆忙，却把一颗报国之心，永远留在了这片土地。",
    curator="我们选黄大年，因为他把“报国”二字，从口号变成了行动。他让我们懂得：真正的赤子之心，是无论身在何方，都朝着祖国的方向。",
    moments=dict(emoji="🧭", text="设备调试成功了。再快一点，我们就能追平世界。", pic="🧭 ⚡ 🌏",
                 comments=[("同事","黄老师，您太拼了，歇歇吧。"),("学生","跟着您，我们不敢懈怠。"),("后人","心有大我，至诚报国。")]),
    compare=dict(left="振兴中华，乃我辈之责。", right="原来“爱国”是无论多优越，都选择回到祖国身边。"))

# 22 申纪兰
add(name="申纪兰", title="纪兰厅", seal="纪兰", era="当代", field="楷模", c="#9E4A3A",
    identity="全国劳动模范，“共和国勋章”获得者，推动“男女同工同酬”写进宪法。",
    slogan="一辈子跟党走，一辈子为人民。",
    nodes=[("1954","当选第一届全国人大代表，把“男女同工同酬”写进宪法。","人物生平"),
           ("1970s","带领西沟村村民艰苦奋斗，改变穷山沟面貌。","人物生平"),
           ("2020","逝世于山西，一生扎根农村、服务人民。","人物生平"),
           ("荣誉","2019 年获颁“共和国勋章”。","人物生平")],
    highlights=[("⚖️","同工同酬","新中国成立初期，她率先提出“男女同工同酬”，并推动这一理念<span class='q'>写入宪法</span>，成为中国妇女解放史上的里程碑。"),
                ("🌄","扎根西沟","从年轻到白发，她一辈子没离开西沟。她说：<span class='q'>我是农民，我就为农民说话</span>。")],
    codes=[("同工同酬","男女同工同酬，是天经地义。"),
           ("扎根基层","我是农民，我就为农民说话。"),
           ("一心向党","一辈子跟党走。"),
           ("艰苦奋斗","穷山沟，也能变成金窝窝。")],
    quotes=["我是农民，我就为农民说话。","男女同工同酬，是天经地义。"],
    award="她是从太行山走出来的劳模。她用一个朴素的诉求——“男女同工同酬”，推动了一个时代的进步。一辈子扎根农村，一辈子为民代言。申纪兰，用一生诠释了“人民代表”四个字的分量。",
    curator="我们选申纪兰，因为她让我们看见：改变历史的力量，有时就来自一个普通农村妇女的坚持。她的一生，平凡而伟大。",
    moments=dict(emoji="⚖️", text="同工同酬，写进宪法了。咱妇女，能挺直腰杆了。", pic="⚖️ 🌄 ⭐",
                 comments=[("村民","纪兰姐，你是咱西沟的骄傲。"),("同事","跟着你，我们信得过。"),("后人","向老劳模致敬。")]),
    compare=dict(left="我是农民，我就为农民说话。", right="原来“发声”本身，就能推动一个时代向前。"))

# 23 王继才
add(name="王继才", title="守岛厅", seal="守岛", era="当代", field="楷模", c="#4A7A8A",
    identity="开山岛民兵哨所所长，守岛卫国 32 年的“时代楷模”。",
    slogan="守岛就是守国，有我在，岛就在。",
    nodes=[("1986","和妻子王仕花一起，登上黄海前哨开山岛。","人物生平"),
           ("32 年","32 年如一日，升国旗、写日志、守海防。","人物生平"),
           ("2018","在执勤中突发疾病，不幸逝世。","人物生平"),
           ("荣誉","被授予“人民楷模”国家荣誉称号。","人物生平")],
    highlights=[("🏝️","守岛就是守国","一座只有两个足球场大的荒岛，他一守就是 32 年。他说：<span class='q'>守岛就是守国，有我在，岛就在</span>。"),
                ("🇨🇳","一面国旗","每天清晨，他都在岛上把国旗高高升起。32 年，<span class='q'>从未间断</span>。那面国旗，就是他对祖国最深的承诺。")],
    codes=[("坚守孤岛","守岛就是守国，有我在，岛就在。"),
           ("忠于职守","升国旗，是我们的仪式。"),
           ("默默奉献","一辈子守一座岛，值。"),
           ("家国情怀","岛虽小，国是大。")],
    quotes=["守岛就是守国，有我在，岛就在。","岛虽小，国是大。"],
    award="他守的是一座孤岛，扛起的却是一个国家的海防。32 年，一万多个日日夜夜，他把青春和生命，都交给了那片海。王继才，用最孤独的坚守，写下了最壮丽的忠诚。",
    curator="我们选王继才，因为他用 32 年的孤独，诠释了“忠诚”二字。岛虽小，国是大。愿我们都能在自己的岗位上，守好属于自己的那座“岛”。",
    moments=dict(emoji="🏝️", text="今天风大，国旗还是要照常升起来。有我在，岛就在。", pic="🏝️ 🇨🇳 🌊",
                 comments=[("妻子","继才，我陪你一起守。"),("战友","你是我们的英雄。"),("后人","向守岛卫士致敬。")]),
    compare=dict(left="守岛就是守国，有我在，岛就在。", right="原来最深的忠诚，是 32 年如一日的一遍升旗。"))

# 24 鲁迅
add(name="鲁迅", title="呐喊厅", seal="呐喊", era="近代", field="文人", c="#4A4438",
    identity="文学家、思想家、革命家，中国现代文学的奠基人。",
    slogan="横眉冷对千夫指，俯首甘为孺子牛。",
    nodes=[("1902","赴日本留学，后弃医从文，决心以笔唤醒国人。","人物生平"),
           ("1918","发表第一篇白话小说《狂人日记》，中国现代文学由此发端。","《狂人日记》"),
           ("1921","发表《阿Q正传》，深刻剖析国民性。","《阿Q正传》"),
           ("1936","病逝于上海，举国哀悼。","人物生平")],
    highlights=[("✒️","弃医从文","在日本，他看到国人的麻木，毅然弃医从文。他说：<span class='q'>学医救不了中国，我要唤醒的是国人的灵魂</span>。"),
                ("🔥","以笔为枪","他一生都在呐喊。他写下的每一个字，<span class='q'>都是投向黑暗的匕首与投枪</span>。")],
    codes=[("民族脊梁","横眉冷对千夫指，俯首甘为孺子牛。"),
           ("以笔为枪","我以我血荐轩辕。"),
           ("批判精神","真的猛士，敢于直面惨淡的人生。"),
           ("唤醒国人","不在沉默中爆发，就在沉默中灭亡。")],
    quotes=["横眉冷对千夫指，俯首甘为孺子牛。","真的猛士，敢于直面惨淡的人生。"],
    award="他是中国现代文学的奠基人，更是民族的良心。他以笔为枪，向腐朽与麻木宣战；他俯首为牛，把满腔热血都献给了这片土地。鲁迅，一个让“脊梁”二字有了骨气的名字。",
    curator="我们选鲁迅，因为他是“民族脊梁”最标准的注脚。他横眉冷对黑暗，俯首甘为人民。愿我们都能像他一样，做一个有骨气、有担当的人。",
    moments=dict(emoji="✒️", text="又写完一篇。愿这些文字，能叫醒几个沉睡的人。", pic="✒️ 📖 🔥",
                 comments=[("读者","先生，您的文字，是黑夜里的灯。"),("同行","这个时代，需要鲁迅。"),("后人","民族魂，永不朽。")]),
    compare=dict(left="横眉冷对千夫指，俯首甘为孺子牛。", right="原来“脊梁”的底色，是傲骨与柔情并存。"))

# 25 闻一多
add(name="闻一多", title="红烛厅", seal="红烛", era="近代", field="文人", c="#8C3A3A",
    identity="诗人、学者、民主战士，为民族尊严与正义献身的斗士。",
    slogan="红烛啊，莫问收获，但问耕耘。",
    nodes=[("1922","赴美留学，写下爱国诗集《红烛》。","《红烛》"),
           ("任教","回国任教，成为著名诗人、学者。","人物生平"),
           ("1946","发表《最后一次讲演》，当天遭暗杀遇难。","《最后一次讲演》"),
           ("精神","为民主与正义，献出了生命。","人物生平")],
    highlights=[("🕯️","红烛精神","他自比红烛：<span class='q'>莫问收获，但问耕耘</span>。他的一生，正是燃烧自己、照亮他人的写照。"),
                ("🎙️","最后一次讲演","面对黑暗势力，他拍案而起，发表了《最后一次讲演》：<span class='q'>正义是杀不完的，因为真理永远存在</span>。当晚，他倒在了血泊之中。")],
    codes=[("红烛精神","红烛啊，莫问收获，但问耕耘。"),
           ("拍案而起","正义是杀不完的，因为真理永远存在。"),
           ("爱国诗人","诗人的天赋，就是爱他的祖国。"),
           ("舍生取义","前脚跨出大门，后脚就不准备再跨进大门。")],
    quotes=["红烛啊，莫问收获，但问耕耘。","正义是杀不完的，因为真理永远存在。"],
    award="他是诗人，更是斗士。一支红烛，燃烧的是对祖国最深的情；最后一次讲演，掷出的是对黑暗最勇的怒。他倒下了，却让“拍案而起”成为民族脊梁最硬的一个动作。",
    curator="我们选闻一多，因为他把诗人的浪漫，与斗士的刚烈，融为了一体。他让我们懂得：脊梁不仅要站得直，还要敢在危难时刻拍案而起。",
    moments=dict(emoji="🕯️", text="灯下写诗。愿这束光，能照进更多人的心里。", pic="🕯️ 📜 🔥",
                 comments=[("学生","先生，您的课，是精神的洗礼。"),("同行","风骨凛然，吾辈楷模。"),("后人","红烛精神，光照千古。")]),
    compare=dict(left="红烛啊，莫问收获，但问耕耘。", right="原来最浪漫的人，往往也最有风骨。"))

# 26 朱自清
add(name="朱自清", title="背影厅", seal="背影", era="近代", field="文人", c="#4C8C6E",
    identity="散文家、诗人、学者，坚守民族气节的现代文人。",
    slogan="宁可饿死，也不领美国的救济粮。",
    nodes=[("1920","北京大学毕业，开始文学创作。","人物生平"),
           ("1925","写下《背影》，感动了一代代中国人。","《背影》"),
           ("1948","贫病交加，拒绝领取“美援”面粉，宁可饿死。","人物生平"),
           ("气节","以生命坚守了文人的民族气节。","人物生平")],
    highlights=[("🚉","父亲的背影","一篇《背影》，写尽了父爱的深沉。那个<span class='q'>蹒跚地爬上月台</span>的背影，成了中国文学史上最动人的画面之一。"),
                ("🍚","宁死不食","1948 年，他贫病交加，却毅然拒绝美国救济粮。他说：<span class='q'>宁可饿死，也不领美国的救济粮</span>。")],
    codes=[("宁死不食","宁可饿死，也不领美国的救济粮。"),
           ("民族气节","文人，要有文人的骨气。"),
           ("真挚深情","我写《背影》，是因为我爱我的父亲。"),
           ("淡泊清廉","清白做人，清白做事。")],
    quotes=["宁可饿死，也不领美国的救济粮。","朱自清的一生，清清白白。"],
    award="他是写《背影》的散文家，更是有骨气的中国人。一篇《背影》，写尽了人间至情；一个拒绝救济粮的决定，守住了文人的民族气节。朱自清，用最温润的文字，写下了最坚硬的骨气。",
    curator="我们选朱自清，因为他让我们看见：文人的风骨，藏在最温柔的笔触里，也藏在最艰难的选择里。宁死不吃嗟来之食，这是中国人的骨气。",
    moments=dict(emoji="🚉", text="又想起父亲的背影。这一别，不知何时再见。", pic="🚉 📖 🌿",
                 comments=[("读者","先生，您的背影，我们读了一辈子。"),("同行","文人气节，令人敬仰。"),("后人","清贫不移，风骨长存。")]),
    compare=dict(left="宁可饿死，也不领美国的救济粮。", right="原来“骨气”是在最难的时候，也守住底线。"))

# 27 老舍
add(name="老舍", title="茶馆厅", seal="茶馆", era="近现代", field="文人", c="#5A5A6E",
    identity="人民艺术家、作家，中国现代文学的一座高峰。",
    slogan="写尽北平的人间烟火，也写透一个民族的心。",
    nodes=[("1924","赴英国讲学，开始文学创作。","人物生平"),
           ("1936","写下《骆驼祥子》，成为现代文学经典。","《骆驼祥子》"),
           ("1957","话剧《茶馆》上演，成为话剧史上的高峰。","《茶馆》"),
           ("人民艺术家","被授予“人民艺术家”称号。","人物生平")],
    highlights=[("🏮","一座茶馆","《茶馆》里，一间小小的茶馆，<span class='q'>装下了半个世纪的沧桑</span>。三教九流、悲欢离合，尽在其中。"),
                ("🖋️","人民艺术家","他说：<span class='q'>我是用我的生命，写我的人民</span>。他的笔，始终对准最普通的中国人。")],
    codes=[("人民艺术家","我是用我的生命，写我的人民。"),
           ("深植民间","北京，是我的乡土。"),
           ("悲悯情怀","写小人物，写大时代。"),
           ("赤子之心","我爱我的国家，爱我的北京。")],
    quotes=["我是用我的生命，写我的人民。","北京的秋天，是最美的。"],
    award="他是“人民艺术家”。从《骆驼祥子》到《茶馆》，他把最普通的中国人，写成了文学史上最鲜活的面孔。他深爱这片土地，也深爱土地上的人民。老舍，用一支笔，留住了北平的烟火，也留住了民族的心跳。",
    curator="我们选老舍，因为他把“人民”二字，刻进了文学的骨血。他让我们懂得：最高级的文学，是为最普通的人立传。",
    moments=dict(emoji="🏮", text="茶馆里又坐满了人。这烟火气，最养人。", pic="🏮 ☕ 🖋️",
                 comments=[("读者","先生，您的文字，就是北平。"),("同行","人民艺术家，当之无愧。"),("后人","经典不朽，烟火长存。")]),
    compare=dict(left="我是用我的生命，写我的人民。", right="原来“伟大作家”的底色，是始终为人民写作。"))

# 28 吴孟超
add(name="吴孟超", title="妙手厅", seal="妙手", era="当代", field="医者", c="#B08C3A",
    identity="“中国肝胆外科之父”，中国科学院院士，拯救了 1.6 万多名患者。",
    slogan="一个好医生，眼里看的是病，心里装的是人。",
    nodes=[("1949","从同济大学医学院毕业，投身外科事业。","人物生平"),
           ("1960","成功完成中国第一例肝脏外科手术。","人物生平"),
           ("1991","当选中国科学院院士。","人物生平"),
           ("一生","主刀 1.6 万例，直到 96 岁仍坚持在手术台旁。","人物生平")],
    highlights=[("🩺","一把刀，救人无数","他创造了多项世界纪录，主刀 1.6 万余例。他说：<span class='q'>一个好医生，眼里看的是病，心里装的是人</span>。"),
                ("❤️","医者仁心","为病人省钱，他坚持用手代替昂贵的器械。96 岁高龄，<span class='q'>他依然站在手术台旁</span>。")],
    codes=[("医者仁心","一个好医生，眼里看的是病，心里装的是人。"),
           ("精益求精","手术刀下，是生死，容不得半点马虎。"),
           ("大医精诚","医生，是救命的，不是赚钱的。"),
           ("奉献一生","只要病人需要，我就一直做下去。")],
    quotes=["一个好医生，眼里看的是病，心里装的是人。","医生，是救命的，不是赚钱的。"],
    award="他是中国肝胆外科的拓荒者。一把手术刀，他用了七十多年，挽救了 1.6 万多个生命。他把“医者仁心”四字，刻进了每一次握刀。吴孟超，用一生证明：最好的医生，心里永远装着病人。",
    curator="我们选吴孟超，因为他让我们看见：一种职业做到极致，就是慈悲。他眼里看的是病，心里装的是人。愿我们都能在自己的岗位上，心怀他人。",
    moments=dict(emoji="🩺", text="今天又做完一台手术，病人醒了，对我笑。值了。", pic="🩺 ❤️ 🌿",
                 comments=[("病人","吴医生，是您给了我第二次生命。"),("学生","跟着您，我们懂得何为仁心。"),("后人","大医精诚，德泽后世。")]),
    compare=dict(left="一个好医生，眼里看的是病，心里装的是人。", right="原来“专业”的尽头，是一颗装着别人的心。"))

# 29 林巧稚
add(name="林巧稚", title="新生厅", seal="新生", era="近代", field="医者", c="#B56A7E",
    identity="妇产科专家，中国现代妇产科学的奠基人，“万婴之母”。",
    slogan="她一生未育，却迎接了五万多个新生命。",
    nodes=[("1921","考入北京协和医学院，成绩优异。","人物生平"),
           ("1929","成为协和医院第一位留院的中国女医生。","人物生平"),
           ("奉献","一生接生 5 万多名婴儿，被誉为“万婴之母”。","人物生平"),
           ("1983","病逝于北京，把一生献给了母婴健康。","人物生平")],
    highlights=[("👶","万婴之母","她一生没有自己的孩子，却亲手迎来了<span class='q'>五万多个新生命</span>。她把每一个婴儿，都当成了自己的孩子。"),
                ("📞","一句嘱托","病危时，她还在梦中喃喃：<span class='q'>产房，快，产房</span>。她把生命最后一刻，都留给了病人。")],
    codes=[("万婴之母","我是一辈子的值班医生。"),
           ("医者仁心","病人，就是我的亲人。"),
           ("无私奉献","我没有儿女，天下的孩子都是我的孩子。"),
           ("精益求精","母婴健康，关乎一个民族的未来。")],
    quotes=["我是一辈子的值班医生。","我没有儿女，天下的孩子都是我的孩子。"],
    award="她是“万婴之母”。一生未婚未育，却把五万多个新生命迎到了人间。她把全部的母爱，都给了病人和孩子。林巧稚，用一双温暖的手，托起了一个民族的希望。",
    curator="我们选林巧稚，因为她让我们懂得：母爱的伟大，不只在生育，更在奉献。她把天下的孩子，都当成了自己的孩子。",
    moments=dict(emoji="👶", text="今天又接生了几个健康的宝宝，听到第一声啼哭，什么累都忘了。", pic="👶 🌸 ❤️",
                 comments=[("产妇","林医生，谢谢您。"),("同事","您就是产妇的守护神。"),("后人","万婴之母，恩泽万千。")]),
    compare=dict(left="我是一辈子的值班医生。", right="原来“母爱”最辽阔的样子，是把全天下的孩子都装进心里。"))

# 30 詹天佑
add(name="詹天佑", title="京张厅", seal="京张", era="近代", field="科学", c="#4C7A6E",
    identity="中国铁路工程之父，京张铁路总工程师。",
    slogan="在悬崖峭壁间，他凿出了中国人的骨气。",
    nodes=[("1872","作为首批幼童赴美留学。","人物生平"),
           ("1881","学成归国，投身铁路建设。","人物生平"),
           ("1905","出任京张铁路总工程师。","人物生平"),
           ("1909","京张铁路全线通车，震惊中外。","人物生平")],
    highlights=[("🚂","人字形铁路","面对八达岭的陡坡，他独创<span class='q'>“人”字形铁路</span>，用“之”字折返的智慧，让火车爬上了险峻山岭。"),
                ("⛰️","中国人的志气","外国人断言中国人修不了京张铁路，詹天佑却说：<span class='q'>中国人能修，而且要修得更好</span>。他做到了。")],
    codes=[("人字铁路","中国人能修，而且要修得更好。"),
           ("自力更生","各出所学，各尽所知，使国家富强。"),
           ("精益求精","造铁路，是为国家图富强。"),
           ("报国之志","不受外侮，靠的是自强。")],
    quotes=["各出所学，各尽所知，使国家富强。","中国人能修，而且要修得更好。"],
    award="他是中国铁路的开拓者。在列强讥讽中，他主持修建了京张铁路，用人字形设计，征服了天险，也赢得了尊严。詹天佑，用一条铁路，让世界看到了中国人的智慧与骨气。",
    curator="我们选詹天佑，因为他让中国人第一次在铁路工程上挺直了腰杆。他用人字形铁路告诉我们：中国人的智慧，足以征服任何天险。",
    moments=dict(emoji="🚂", text="京张铁路，今天全线通车了！我们中国人，自己修的！", pic="🚂 ⛰️ 🛤️",
                 comments=[("同事","詹总，您为中国人争了光！"),("工人","跟着您，我们自豪！"),("后人","人字铁路，中国脊梁。")]),
    compare=dict(left="各出所学，各尽所知，使国家富强。", right="原来“争气”是明知艰难，也要用智慧把它踩在脚下。"))

# —————————————————————————— 生成 ——————————————————————————
OUT = os.path.dirname(os.path.abspath(__file__))
IMG = {}
try:
    with open(os.path.join(OUT, 'images.json'), encoding='utf-8') as f:
        IMG = json.load(f)
except Exception:
    IMG = {}

for p in P:
    html = build(p, IMG.get(p['name']))
    path = os.path.join(OUT, p['name'] + '.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('生成', path)

print('共 %d 位人物' % len(P))

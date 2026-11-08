/* Skupiny sortimentu a ilustrace výrobků J.K.FOOD – sdílí index.html a sortiment.html */
(() => {
  // osm skupin sortimentu; id = kotva v sortiment.html, count = počet výrobků v sortimentu
  const CATS = [
    { id: 'koreni', name: 'Koření jednodruhové', count: 76, color: '#2E211E' },
    { id: 'smesi', name: 'Kořenicí směsi', count: 71, color: '#C8231A' },
    { id: 'zelenina', name: 'Sušená zelenina', count: 72, color: '#6F8435' },
    { id: 'maso', name: 'Směsi pro masný průmysl', count: 181, color: '#7C1A12' },
    { id: 'houby', name: 'Sušené houby a plody', count: 20, color: '#8B6447' },
    { id: 'polevky', name: 'Bujóny, polévky, omáčky', count: 19, color: '#DE9B2A' },
    { id: 'brambory', name: 'Bramborové výrobky', count: 14, color: '#C9A06A' },
    { id: 'testoviny', name: 'Škroby, těstoviny a další', count: 39, color: '#E3B94F' }
  ];

  /* ---------- ilustrace výrobků ----------
     Jednotný styl: plochá barva + tmavší stín vpravo dole + světlý odlesk vlevo nahoře.
     Kreslí se v jednotkách: střed (0,0), kousek se vejde zhruba do kruhu o poloměru 1. */
  const TAU = Math.PI * 2;
  // vyplní tvar se stínem a odleskem; path(c) jen sestaví cestu
  function shaded(c, path, base, dark, light) {
    c.beginPath(); path(c); c.fillStyle = dark; c.fill();
    c.save(); c.beginPath(); path(c); c.clip();
    c.translate(-.1, -.12); c.beginPath(); path(c); c.fillStyle = base; c.fill();
    c.restore();
    if (light) {
      c.save(); c.beginPath(); path(c); c.clip();
      c.fillStyle = light; c.beginPath(); c.ellipse(-.3, -.42, .38, .2, -.5, 0, TAU); c.fill();
      c.restore();
    }
  }
  const circ = (x, y, r) => c => c.arc(x, y, r, 0, TAU);

  const ICONS = {
    // kulička pepře – trojice zrnek
    pepper(c) {
      [[-.44, .3], [.44, .3], [0, -.4]].forEach(([x, y]) => {
        c.save(); c.translate(x, y);
        shaded(c, circ(0, 0, .5), '#3D2C26', '#1F1512', null);
        c.strokeStyle = 'rgba(255,255,255,.14)'; c.lineWidth = .06; c.lineCap = 'round';
        c.beginPath(); c.arc(.05, .05, .3, 3.6, 5.0); c.stroke();
        c.beginPath(); c.arc(-.05, .1, .22, .2, 1.4); c.stroke();
        c.fillStyle = 'rgba(255,255,255,.5)'; c.beginPath(); c.ellipse(-.18, -.2, .12, .08, -.6, 0, TAU); c.fill();
        c.restore();
      });
    },
    // chilli paprička se zelenou stopkou
    chilli(c) {
      const body = c => { c.moveTo(-.62, -.5); c.bezierCurveTo(.05, -.62, .7, -.1, 1.02, .78); c.bezierCurveTo(.45, .3, -.1, .05, -.7, .02); c.bezierCurveTo(-.86, -.12, -.84, -.42, -.62, -.5); };
      shaded(c, body, '#D7281C', '#9C130B', null);
      c.strokeStyle = 'rgba(255,255,255,.55)'; c.lineWidth = .08; c.lineCap = 'round';
      c.beginPath(); c.moveTo(-.4, -.38); c.bezierCurveTo(0, -.42, .38, -.18, .56, .12); c.stroke();
      c.fillStyle = '#4F7D2A';
      c.beginPath(); c.ellipse(-.68, -.24, .14, .3, .2, 0, TAU); c.fill();
      c.strokeStyle = '#4F7D2A'; c.lineWidth = .13;
      c.beginPath(); c.moveTo(-.75, -.3); c.quadraticCurveTo(-.98, -.42, -.94, -.72); c.stroke();
    },
    // badyán – osm lusků se semínky
    anise(c) {
      for (let j = 0; j < 8; j++) {
        c.save(); c.rotate(j * TAU / 8);
        shaded(c, cc => cc.ellipse(.52, 0, .46, .19, 0, 0, TAU), '#94512B', '#5C2D14', null);
        c.fillStyle = '#E2AE6E'; c.beginPath(); c.ellipse(.6, 0, .13, .08, 0, 0, TAU); c.fill();
        c.restore();
      }
      c.fillStyle = '#5C2D14'; c.beginPath(); c.arc(0, 0, .17, 0, TAU); c.fill();
    },
    // bobkový list
    bay(c) {
      const leaf = c => { c.moveTo(-1, .1); c.bezierCurveTo(-.5, -.62, .55, -.6, 1, -.08); c.bezierCurveTo(.5, .5, -.45, .55, -1, .1); };
      shaded(c, leaf, '#8A9A45', '#5E6E2A', null);
      c.strokeStyle = 'rgba(255,255,240,.6)'; c.lineWidth = .06; c.lineCap = 'round';
      c.beginPath(); c.moveTo(-.95, .1); c.quadraticCurveTo(0, -.08, .92, -.08); c.stroke();
      c.lineWidth = .04;
      [-.5, -.1, .3].forEach(x => { c.beginPath(); c.moveTo(x, -.04); c.lineTo(x + .22, -.3); c.moveTo(x, -.02); c.lineTo(x + .2, .22); c.stroke(); });
    },
    // mrkev s natí
    carrot(c) {
      c.fillStyle = '#4F8A2C';
      [[-.28, -1.02, -.35], [0, -1.1, 0], [.28, -1.02, .35]].forEach(([x, y, a]) => { c.save(); c.translate(x * .6, -.55); c.rotate(a); c.beginPath(); c.ellipse(0, -.28, .1, .32, 0, 0, TAU); c.fill(); c.restore(); });
      const body = c => { c.moveTo(-.36, -.55); c.quadraticCurveTo(0, -.68, .36, -.55); c.quadraticCurveTo(.3, .3, .03, 1.02); c.quadraticCurveTo(-.01, 1.06, -.04, 1.02); c.quadraticCurveTo(-.3, .3, -.36, -.55); };
      shaded(c, body, '#F07F2A', '#C2541A', null);
      c.strokeStyle = 'rgba(150,60,10,.55)'; c.lineWidth = .06; c.lineCap = 'round';
      [[-.22, -.2, .02], [.04, .1, .2], [-.14, .42, -.02], [.06, .66, .14]].forEach(([x1, y, x2]) => { c.beginPath(); c.moveTo(x1, y); c.lineTo(x2, y + .03); c.stroke(); });
      c.fillStyle = 'rgba(255,255,255,.4)'; c.beginPath(); c.ellipse(-.16, -.25, .06, .22, .05, 0, TAU); c.fill();
    },
    // hrachový lusk s hrášky
    pea(c) {
      const pod = c => { c.moveTo(-1, .15); c.bezierCurveTo(-.6, -.55, .6, -.6, 1, -.1); c.bezierCurveTo(.6, .45, -.55, .55, -1, .15); };
      shaded(c, pod, '#7DA83A', '#4F7322', null);
      c.fillStyle = '#B6D66A';
      [-.5, 0, .5].forEach(x => { c.beginPath(); c.arc(x, -.02 - (x > 0 ? x * .06 : 0), .22, 0, TAU); c.fill(); });
      c.fillStyle = 'rgba(255,255,255,.55)';
      [-.5, 0, .5].forEach(x => { c.beginPath(); c.arc(x - .07, -.1, .06, 0, TAU); c.fill(); });
      c.strokeStyle = '#4F7322'; c.lineWidth = .1; c.lineCap = 'round';
      c.beginPath(); c.moveTo(-1, .15); c.quadraticCurveTo(-1.1, -.05, -1.02, -.2); c.stroke();
    },
    // klobása s provázky na koncích
    sausage(c) {
      const body = c => { c.moveTo(-.92, .05); c.bezierCurveTo(-.75, -.85, .75, -.85, .92, .05); c.bezierCurveTo(1.0, .42, .7, .55, .6, .3); c.bezierCurveTo(.35, -.12, -.35, -.12, -.6, .3); c.bezierCurveTo(-.7, .55, -1.0, .42, -.92, .05); };
      c.save(); c.translate(0, .15);
      shaded(c, body, '#A3311F', '#6E1A10', null);
      c.strokeStyle = 'rgba(255,255,255,.4)'; c.lineWidth = .07; c.lineCap = 'round';
      c.beginPath(); c.moveTo(-.55, -.42); c.quadraticCurveTo(0, -.72, .55, -.42); c.stroke();
      c.strokeStyle = '#E8D6B5'; c.lineWidth = .07;
      c.beginPath(); c.moveTo(-.88, .38); c.lineTo(-1.02, .6); c.moveTo(.88, .38); c.lineTo(1.02, .6); c.stroke();
      c.restore();
    },
    // kolečko salámu
    salami(c) {
      shaded(c, circ(0, 0, .92), '#7A1A16', '#5A100D', null);
      c.fillStyle = '#C23A3A'; c.beginPath(); c.arc(-.03, -.04, .78, 0, TAU); c.fill();
      c.fillStyle = '#F6DCD2';
      [[-.35, -.3, .1], [.2, -.42, .08], [.42, .05, .11], [-.08, .1, .09], [-.42, .28, .08], [.15, .45, .1], [-.05, -.55, .06], [.55, -.28, .06], [-.6, -.02, .07]]
        .forEach(([x, y, r]) => { c.beginPath(); c.arc(x, y, r, 0, TAU); c.fill(); });
      c.fillStyle = 'rgba(255,255,255,.25)'; c.beginPath(); c.ellipse(-.3, -.45, .25, .1, -.5, 0, TAU); c.fill();
    },
    // hřib
    mushroom(c) {
      const stem = c => { c.moveTo(-.28, -.05); c.quadraticCurveTo(-.48, .55, -.32, .92); c.quadraticCurveTo(0, 1.02, .32, .92); c.quadraticCurveTo(.48, .55, .28, -.05); c.closePath(); };
      shaded(c, stem, '#F1E6CC', '#CDB98F', null);
      const cap = c => { c.moveTo(-.98, .08); c.bezierCurveTo(-.98, -.95, .98, -.95, .98, .08); c.quadraticCurveTo(0, .22, -.98, .08); };
      shaded(c, cap, '#8C5530', '#5E3519', 'rgba(255,255,255,.3)');
      c.fillStyle = '#E6CF8E'; c.beginPath(); c.moveTo(-.9, .1); c.quadraticCurveTo(0, .24, .9, .1); c.quadraticCurveTo(0, .34, -.9, .1); c.fill();
    },
    // talíř polévky s párou (miska v barvě značky)
    soup(c) {
      c.strokeStyle = 'rgba(103,93,91,.55)'; c.lineWidth = .08; c.lineCap = 'round';
      [-.3, .05, .4].forEach((x, j) => { c.beginPath(); c.moveTo(x, -.3); c.bezierCurveTo(x - .18, -.5, x + .18, -.65, x - .02, -.95 + j * .05); c.stroke(); });
      const bowl = c => { c.moveTo(-1, -.12); c.quadraticCurveTo(-.95, .7, 0, .72); c.quadraticCurveTo(.95, .7, 1, -.12); c.closePath(); };
      shaded(c, bowl, '#B8160F', '#7C0B08', null);
      c.fillStyle = '#7C0B08'; c.beginPath(); c.roundRect(-.38, .66, .76, .16, .06); c.fill();
      c.fillStyle = '#F1B23E'; c.beginPath(); c.ellipse(0, -.12, 1, .2, 0, 0, TAU); c.fill();
      c.fillStyle = '#E0922A'; c.beginPath(); c.ellipse(0, -.08, .86, .12, 0, 0, TAU); c.fill();
      c.fillStyle = '#6F8435'; [[-.4, -.12], [.25, -.06], [.55, -.14]].forEach(([x, y]) => { c.beginPath(); c.arc(x, y, .06, 0, TAU); c.fill(); });
      c.strokeStyle = 'rgba(255,255,255,.75)'; c.lineWidth = .07;
      c.beginPath(); c.moveTo(-.75, .2); c.quadraticCurveTo(-.55, .48, -.25, .55); c.stroke();
    },
    // brambora s očky
    potato(c) {
      const blob = c => {
        for (let j = 0; j <= 40; j++) {
          const a = j / 40 * TAU, r = 1 + .07 * Math.sin(3 * a + .5) + .05 * Math.sin(5 * a);
          const x = Math.cos(a) * r * .98, y = Math.sin(a) * r * .7;
          j ? c.lineTo(x, y) : c.moveTo(x, y);
        }
        c.closePath();
      };
      shaded(c, blob, '#D2A464', '#A2753F', 'rgba(255,255,255,.35)');
      c.strokeStyle = '#7A5428'; c.lineWidth = .07; c.lineCap = 'round';
      [[-.45, -.15, .5], [.3, .2, -.4], [.5, -.3, .3]].forEach(([x, y, a]) => { c.beginPath(); c.arc(x, y, .09, a, a + 2.4); c.stroke(); });
      c.fillStyle = 'rgba(122,84,40,.45)';
      [[-.1, .35], [.05, -.35], [-.6, .25], [.7, .1]].forEach(([x, y]) => { c.beginPath(); c.arc(x, y, .04, 0, TAU); c.fill(); });
    },
    // vřetýnko – šroubovice ze šikmých závitů
    fusilli(c) {
      // závity se střídavě natáčejí k divákovi (světlé) a od něj (tmavé), vzadu tenké jádro
      c.fillStyle = '#C9922B'; c.beginPath(); c.roundRect(-.9, -.13, 1.8, .26, .13); c.fill();
      const n = 7;
      for (let j = 0; j < n; j++) {
        const x = -.78 + j * 1.56 / (n - 1), end = j === 0 || j === n - 1;
        c.save(); c.translate(x, 0); c.rotate(.6);
        const h = end ? .3 : .44;
        c.fillStyle = '#B07F22'; c.beginPath(); c.ellipse(.03, .03, .15, h, 0, 0, TAU); c.fill();
        c.fillStyle = j % 2 ? '#E9B84C' : '#F5D27A'; c.beginPath(); c.ellipse(0, 0, .13, h * .95, 0, 0, TAU); c.fill();
        c.restore();
      }
    }
  };

  // druhy výrobků v jednotlivých skupinách (u směsí se střídají)
  const KINDS = [
    ['pepper'],                    // koření jednodruhové
    ['chilli', 'anise', 'bay'],    // kořenicí směsi
    ['carrot', 'pea'],             // sušená zelenina
    ['sausage', 'salami'],         // směsi pro masný průmysl
    ['mushroom'],                  // sušené houby
    ['soup'],                      // bujóny, polévky, omáčky
    ['potato'],                    // bramborové výrobky
    ['fusilli']                    // těstoviny
  ];
  // výrobky, které mají zůstat zhruba nastojato (miska, houba, mrkev)
  const UPRIGHT = { soup: .12, mushroom: .3, carrot: .45 };

  /* nakreslí výrobek skupiny cat; k = poloměr v px, v = index druhu (bere se modulo),
     'mix' = ikonka do legendy složená ze dvou druhů */
  function drawProduct(c, cat, k, v = 0) {
    const kinds = KINDS[cat];
    c.save();
    if (v === 'mix' && kinds.length > 1) {
      c.scale(k, k);
      c.save(); c.translate(-.38, -.3); c.scale(.62, .62); ICONS[kinds[1]](c); c.restore();
      c.save(); c.translate(.22, .25); c.scale(.7, .7); ICONS[kinds[0]](c); c.restore();
    } else {
      c.scale(k, k);
      ICONS[kinds[(v === 'mix' ? 0 : v) % kinds.length]](c);
    }
    c.restore();
  }
  const kindOf = (cat, v) => KINDS[cat][v % KINDS[cat].length];

  // ikonka skupiny do <canvas> (legenda, katalog)
  function productIcon(cat, px) {
    const ic = document.createElement('canvas');
    const d = Math.min(2, devicePixelRatio || 1);
    ic.width = ic.height = Math.round(px * d);
    ic.style.width = ic.style.height = px + 'px';
    ic.setAttribute('aria-hidden', 'true');
    const x = ic.getContext('2d'); x.scale(d, d); x.translate(px / 2, px / 2);
    drawProduct(x, cat, px * .42, 'mix');
    return ic;
  }

  window.JK = { CATS, ICONS, KINDS, UPRIGHT, drawProduct, kindOf, productIcon };
})();

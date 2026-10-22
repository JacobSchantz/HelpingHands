// Every illustration on the page is drawn here as SVG, from one parametric robot.
// Angles are degrees, SVG convention (0 = right, 90 = down).

const rad = d => d * Math.PI / 180;
const pt = (x, y, a, l) => [x + l * Math.cos(rad(a)), y + l * Math.sin(rad(a))];
const f = n => n.toFixed(1);

// Needle-nose pliers jaws at (x, y) pointing along a, opened by `open` degrees.
function pliers(x, y, a, open = 14, len = 46, cls = '') {
  const [px, py] = pt(x, y, a, 14);
  const jaw = s => {
    const ja = a + s * open / 2;
    const [tx, ty] = pt(px, py, ja, len);
    const n = ja + 90;
    const [b1x, b1y] = pt(px, py, n, 5), [b2x, b2y] = pt(px, py, n, -5);
    const [t1x, t1y] = pt(tx, ty, n, 1.4), [t2x, t2y] = pt(tx, ty, n, -1.4);
    return `<path class="jaw" d="M${f(b1x)} ${f(b1y)} L${f(t1x)} ${f(t1y)} L${f(t2x)} ${f(t2y)} L${f(b2x)} ${f(b2y)}Z"/>`;
  };
  return `<g class="pliers ${cls}"><line class="roll" x1="${f(x)}" y1="${f(y)}" x2="${f(px)}" y2="${f(py)}"/>` +
    jaw(-1) + jaw(1) + `<circle class="pivot" cx="${f(px)}" cy="${f(py)}" r="5.5"/></g>`;
}

// One arm from the shoulder: [upper-arm angle, forearm angle, gripper angle, jaw opening].
function arm(sx, sy, [a1, a2, a3, open]) {
  const [ex, ey] = pt(sx, sy, a1, 92), [wx, wy] = pt(ex, ey, a2, 86);
  return `<g class="arm"><path class="limb" d="M${f(sx)} ${f(sy)} L${f(ex)} ${f(ey)} L${f(wx)} ${f(wy)}"/>` +
    `<circle class="joint" cx="${f(ex)}" cy="${f(ey)}" r="11"/>` + pliers(wx, wy, a3, open) +
    `<circle class="joint" cx="${f(wx)}" cy="${f(wy)}" r="8"/></g>`;
}

// The legless two-armed robot. Origin = bottom centre of the weighted base.
function robot({ x = 0, y = 0, s = 1, L = [120, 70, 60, 14], R = [60, 110, 120, 14], head = true,
  left = true, right = true, eyes = true, cls = '' } = {}) {
  let g = `<g class="robot ${cls}" transform="translate(${x} ${y}) scale(${s})">`;
  g += `<ellipse class="shadow" cx="0" cy="2" rx="110" ry="10"/>`;
  g += `<rect class="base" x="-86" y="-38" width="172" height="38" rx="19"/>`;
  g += `<rect class="neck" x="-20" y="-128" width="40" height="96" rx="8"/>`;
  g += `<rect class="torso" x="-72" y="-262" width="144" height="140" rx="44"/>`;
  g += `<path class="seam" d="M-40 -170 H40"/>`;
  if (head) {
    g += `<rect class="neck" x="-12" y="-282" width="24" height="26" rx="6"/>`;
    g += `<rect class="head" x="-58" y="-356" width="116" height="80" rx="32"/>`;
    g += `<rect class="visor" x="-44" y="-340" width="88" height="44" rx="22"/>`;
    if (eyes) g += `<circle class="eye" cx="-18" cy="-318" r="9"/><circle class="eye" cx="18" cy="-318" r="9"/>` +
      `<circle class="glint" cx="-15" cy="-321" r="2.4"/><circle class="glint" cx="21" cy="-321" r="2.4"/>`;
  }
  if (left) g += arm(-70, -232, L) + `<circle class="shoulder" cx="-70" cy="-232" r="16"/>`;
  if (right) g += arm(70, -232, R) + `<circle class="shoulder" cx="70" cy="-232" r="16"/>`;
  return g + '</g>';
}

// A small printer: a frame, a gantry, a print in progress.
function printer(x, y, s = 1, cls = '') {
  return `<g class="printer ${cls}" transform="translate(${x} ${y}) scale(${s})">` +
    `<rect class="frame" x="-40" y="-92" width="80" height="92" rx="8"/>` +
    `<rect class="bed" x="-28" y="-20" width="56" height="6" rx="3"/>` +
    `<rect class="print" x="-12" y="-36" width="24" height="16" rx="3"/>` +
    `<line class="gantry" x1="-34" y1="-62" x2="34" y2="-62"/>` +
    `<rect class="head-p" x="-9" y="-68" width="18" height="16" rx="3"/>` +
    `<path class="nozzle" d="M-3 -52 L0 -44 L3 -52Z"/></g>`;
}

const svg = (vb, body, label) => `<svg viewBox="${vb}" role="img" aria-label="${label}">${body}</svg>`;
const put = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };

// ---- Hero: the robot, breathing.
function hero(t) {
  const w = Math.sin(t / 900), v = Math.sin(t / 1300 + 1);
  const body = robot({ x: 260, y: 470, s: 1.05,
    L: [130 + 6 * w, 60 + 10 * v, 30 + 12 * v, 10 + 8 * (1 + w)],
    R: [55 - 6 * v, 100 - 8 * w, 140 - 10 * w, 6 + 6 * (1 + v)] });
  put('hero-art', svg('0 0 520 500', body, 'A legless two-armed robot with stereo eyes and pliers grippers'));
}

// ---- The rule: a human-held gripper and the robot's gripper are the same part.
function handheld(x, y, s, a = -20) {
  // Handheld version: the same jaws, the same actuator puck, two handles.
  const [hx, hy] = pt(x, y, a + 180, 10);
  const h = sgn => { const [ex, ey] = pt(hx, hy, a + 180 + sgn * 12, 110);
    return `<path class="handle" d="M${f(hx)} ${f(hy)} L${f(ex)} ${f(ey)}"/>`; };
  return `<g transform="translate(0 0)">${h(-1)}${h(1)}${pliers(x, y, a, 16, 60)}` +
    `<circle class="puck" cx="${f(x)}" cy="${f(y)}" r="16"/><circle class="puck-dot" cx="${f(x)}" cy="${f(y)}" r="4"/></g>`;
}
function rule() {
  const left = handheld(150, 170, 1, -24) + `<text class="cap" x="120" y="300">In a person's hand</text>`;
  const right = `<g transform="translate(330 0)">` +
    `<path class="limb" d="M40 290 L80 210 L150 170"/><circle class="joint" cx="80" cy="210" r="11"/>` +
    pliers(150, 170, -24, 16, 60) + `<circle class="puck" cx="150" cy="170" r="16"/><circle class="puck-dot" cx="150" cy="170" r="4"/>` +
    `<text class="cap" x="70" y="300">On the robot's wrist</text></g>`;
  const eq = `<text class="eq" x="300" y="180">=</text>`;
  put('rule-art', svg('0 0 600 320', left + eq + right, 'The same pliers gripper, held by a person and mounted on the robot'));
}

// ---- The gripper, large, with callouts.
function gripper() {
  // The same jaws as everywhere else, drawn 2.4x.
  const x = 90, y = 150, k = 2.4, open = 10, len = 130, px = x + 14 * k;
  let g = `<g class="big" transform="translate(${x} ${y}) scale(${k})">` + pliers(0, 0, 0, open, len) + `</g>` +
    `<circle class="puck" cx="${x}" cy="${y}" r="34"/><circle class="puck-dot" cx="${x}" cy="${y}" r="9"/>`;
  const call = (d, s, label) => { const [cx, cy] = pt(px, y, s * open / 2, d * k), dy = s * 62;
    return `<circle class="dot" cx="${f(cx)}" cy="${f(cy)}" r="5"/>` +
      `<path class="lead" d="M${f(cx)} ${f(cy)} V${f(cy + dy)}"/>` +
      `<text class="callout" x="${f(cx)}" y="${f(cy + dy + (dy < 0 ? -10 : 22))}" text-anchor="middle">${label}</text>`; };
  g += call(126, -1, 'flat + serrated pads') + call(98, 1, 'V-notch for screws') +
    call(62, -1, 'screwdriver-bit pocket') + call(22, 1, 'wire cutter');
  g += `<text class="callout" x="${x}" y="${y + 66}" text-anchor="middle">one motor, one joint</text>`;
  put('gripper-art', svg('0 0 520 300', g, 'Needle-nose pliers gripper with tip features'));
}

// ---- Eyes at eye level: a person and the robot, same height and spacing.
function eyes() {
  const person = `<g class="person"><circle cx="150" cy="110" r="52"/><path d="M64 352 Q64 188 150 188 Q236 188 236 352Z"/></g>` +
    `<rect class="band" x="100" y="92" width="100" height="22" rx="11"/>` +
    `<circle class="eye" cx="132" cy="103" r="7"/><circle class="eye" cx="168" cy="103" r="7"/>`;
  const bot = robot({ x: 450, y: 103 + 318 * 0.78, s: 0.78, L: [100, 95, 90, 10], R: [80, 85, 90, 10] });
  const line = `<path class="level" d="M60 103 H560"/><text class="cap" x="300" y="92" text-anchor="middle">same height, same spacing</text>`;
  put('eyes-art', svg('0 0 600 360', person + bot + line, 'A person wearing stereo cameras beside the robot, eyes at the same height'));
}

// ---- Force from motor current: no force sensor.
function force() {
  let p = 'M30 200', q = '';
  for (let i = 0; i <= 50; i++) {
    const x = 30 + i * 10, k = i < 18 ? 0 : (i - 18);
    const y = 200 - Math.min(140, k * k * 0.6) + Math.sin(i * 1.7) * (i > 18 ? 4 : 1.5);
    p += ` L${x} ${f(y)}`;
  }
  q = `<path class="axis" d="M30 30 V200 H540"/><path class="trace" d="${p}"/>` +
    `<path class="contact" d="M210 30 V200"/><text class="cap" x="216" y="46">contact</text>` +
    `<text class="cap" x="36" y="226">jaws closing</text><text class="cap" x="470" y="226">squeeze</text>` +
    `<text class="cap" x="40" y="44">motor current</text>`;
  put('force-art', svg('0 0 570 240', q, 'Motor current rises when the jaws touch the part'));
}

// ---- The robot building its sibling.
function sibling() {
  const bench = `<rect class="bench" x="20" y="430" width="760" height="18" rx="9"/>`;
  const builder = robot({ x: 250, y: 430, s: 1, L: [100, 80, 75, 6], R: [-6, 22, 28, 6] });
  const child = robot({ x: 590, y: 430, s: 0.72, head: false, left: false, eyes: false,
    R: [80, 95, 90, 14], cls: 'ghost' });
  const parts = `<g class="ghost" transform="translate(730 401) scale(.72)"><rect class="head" x="-58" y="-40" width="116" height="80" rx="32"/>` +
    `<rect class="visor" x="-44" y="-24" width="88" height="44" rx="22"/></g>` +
    `<g class="screws"><rect x="440" y="418" width="6" height="12" rx="2"/><rect x="454" y="418" width="6" height="12" rx="2"/><rect x="468" y="418" width="6" height="12" rx="2"/></g>`;
  const armPart = `<g class="ghost" transform="translate(540 263) scale(.72)">` + arm(0, 0, [100, 95, 90, 14]) + `<circle class="shoulder" cx="0" cy="0" r="16"/></g>`;
  put('sibling-art', svg('0 0 800 470', bench + child + parts + armPart + builder, 'The robot fitting an arm onto a half-built copy of itself'));
}

// ---- Printers that build printers: 1 → 2 → 4 → 8.
function printers() {
  let g = '';
  const cols = [1, 2, 4, 8];
  cols.forEach((n, c) => {
    for (let i = 0; i < n; i++) {
      const x = 70 + c * 170, y = 60 + (i + 0.5) * (440 / n) + 30, s = Math.max(0.32, 1.1 / Math.sqrt(n));
      g += printer(x, y, s, c === 0 ? 'seed' : '');
      if (c < 3) [2 * i, 2 * i + 1].forEach(j => {
        const y2 = 60 + (j + 0.5) * (440 / (n * 2)) + 30 - 40 * Math.max(0.32, 1.1 / Math.sqrt(n * 2));
        g += `<path class="link" d="M${x + 48 * s} ${f(y - 40 * s)} C${x + 90} ${f(y - 40 * s)}, ${x + 80} ${f(y2)}, ${x + 120} ${f(y2)}"/>`;
      });
    }
  });
  put('printer-art', svg('0 0 680 560', g, 'One printer leads to two, four and eight'));
}

// ---- The start line moves down.
const LAYERS = [
  ['Assembly', 'Robots put bought and printed parts together'],
  ['Plastic', 'Shred, pelletise and print from scrap'],
  ['Metal from scrap', 'Melt, cast, machine, draw wire, wind motors'],
  ['Refining', 'Iron and aluminium from ore'],
  ['Mining', 'Robots build the excavators and crushers that dig'],
];
function startLine(stage) {
  const el = document.getElementById('layers');
  if (!el) return;
  el.innerHTML = LAYERS.map((l, i) => `<li class="${i <= stage ? 'made' : 'bought'}"><span class="tag">${i <= stage ? 'robots make' : 'bought'}</span>` +
    `<b>${l[0]}</b><span>${l[1]}</span></li>` + (i === stage ? '<li class="line" aria-hidden="true"><span>start line</span></li>' : '')).join('') +
    `<li class="chips"><span class="tag">always bought</span><b>Chips</b><span>Semiconductors stay out of scope</span></li>`;
  const lab = document.getElementById('stage-label');
  if (lab) lab.textContent = ['C0 · today', 'C1', 'C2', 'C3', 'C4 · full loop'][stage];
}

// ---- Motors with no rare earths.
function motors() {
  let h = `<g transform="translate(150 150)"><circle class="ring" r="112"/><circle class="hole" r="58"/>`;
  for (let i = 0; i < 16; i++) {
    const a = i * 22.5, mag = 2 * a + 90;
    const [mx, my] = pt(0, 0, a, 85);
    h += `<path class="segline" d="M${f(pt(0, 0, a + 11.25, 58)[0])} ${f(pt(0, 0, a + 11.25, 58)[1])} L${f(pt(0, 0, a + 11.25, 112)[0])} ${f(pt(0, 0, a + 11.25, 112)[1])}"/>`;
    const [ax, ay] = pt(mx, my, mag, -11), [bx, by] = pt(mx, my, mag, 11);
    h += `<path class="mag" d="M${f(ax)} ${f(ay)} L${f(bx)} ${f(by)}" marker-end="url(#ah)"/>`;
  }
  h += `</g><text class="cap" x="150" y="300" text-anchor="middle">Ferrite Halbach ring</text>`;
  let r = `<g transform="translate(450 150)"><circle class="ring" r="112"/><circle class="hole" r="74"/>`;
  for (let i = 0; i < 12; i++) {
    const a = i * 30;
    r += `<path class="tooth" transform="rotate(${a})" d="M74 -11 H100 V11 H74Z"/>`;
    r += `<path class="coil" transform="rotate(${a})" d="M78 -15 H92 M78 15 H92"/>`;
  }
  r += `<circle class="rotor" r="56"/>`;
  for (let i = 0; i < 8; i++) r += `<path class="rtooth" transform="rotate(${i * 45 + 8})" d="M44 -10 H62 V10 H44Z"/>`;
  r += `<circle class="hole" r="16"/></g><text class="cap" x="450" y="300" text-anchor="middle">Switched reluctance: no magnets</text>`;
  const defs = `<defs><marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10z" class="ahead"/></marker></defs>`;
  put('motor-art', svg('0 0 600 310', defs + h + r, 'A ferrite Halbach magnet ring and a magnet-free switched reluctance motor'));
}

// ---- Ship a robot and a kit; at home it builds the second.
function ship() {
  const box = (x, y, s, label) => `<g class="box" transform="translate(${x} ${y}) scale(${s})">` +
    `<path class="b-top" d="M0 -100 L70 -130 L140 -100 L70 -70Z"/><path class="b-left" d="M0 -100 L70 -70 V0 L0 -30Z"/>` +
    `<path class="b-right" d="M140 -100 L70 -70 V0 L140 -30Z"/><path class="tape" d="M35 -115 L105 -85"/>` +
    `<text class="boxlabel" x="70" y="18" text-anchor="middle">${label}</text></g>`;
  const a = `<g>${robot({ x: 110, y: 330, s: 0.62, L: [110, 80, 80, 10], R: [70, 100, 100, 10] })}${box(190, 330, 0.85, 'kit')}` +
    `<text class="cap" x="160" y="380" text-anchor="middle">What arrives</text></g>`;
  const arrow = `<path class="flow" d="M380 230 H450" marker-end="url(#fa)"/>`;
  const b = `<g>${robot({ x: 590, y: 330, s: 0.62, L: [20, 10, 0, 8], R: [-15, 15, 25, 16] })}` +
    robot({ x: 740, y: 330, s: 0.5, head: false, right: false, cls: 'ghost', L: [100, 90, 90, 10] }) +
    `<text class="cap" x="660" y="380" text-anchor="middle">At home: it builds the second</text></g>`;
  const defs = `<defs><marker id="fa" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10z" class="ahead"/></marker></defs>`;
  put('ship-art', svg('0 0 840 400', defs + a + arrow + b, 'A robot and a kit box arrive; at home the robot assembles the kit into a second robot'));
}

// ---- Size steps: each generation builds the next, one 2x step at a time.
function sizes() {
  let g = `<rect class="bench" x="10" y="400" width="880" height="14" rx="7"/>`;
  const steps = [1, 0.5, 0.25, 0.125];
  let x = 150;
  steps.forEach((s, i) => {
    g += robot({ x, y: 400, s, L: [110, 85, 80, 10], R: i < 3 ? [10, 25, 30, 12] : [70, 100, 100, 10] });
    g += `<text class="cap" x="${x}" y="440" text-anchor="middle">${['1×', '½×', '¼×', '⅛×'][i]}</text>`;
    if (i < 3) x += 200 * s + 70 * steps[i + 1] + 70;
  });
  put('size-art', svg('0 0 900 460', g, 'Four robots, each half the size of the one before, each building the next'));
}

// ---- Doubling: a penny a day, and robots per generation.
function doubling(weeks) {
  const W = 760, H = 320, n = 33, pad = 40;
  let p = '';
  for (let i = 0; i <= n * 4; i++) {
    const g = i / 4, v = Math.pow(2, g) / Math.pow(2, n);
    p += `${i ? 'L' : 'M'}${f(pad + g / n * (W - 2 * pad))} ${f(H - pad - v * (H - 2 * pad))}`;
  }
  const marks = [[10, '1,024'], [20, '1 million'], [30, '1 billion'], [33, '8.6 billion']].map(([g, l]) => {
    const x = pad + g / n * (W - 2 * pad), y = H - pad - Math.pow(2, g - n) * (H - 2 * pad);
    return `<circle class="dot" cx="${f(x)}" cy="${f(y)}" r="5"/><text class="cap light" x="${f(x - 8)}" y="${f(y - 12)}" text-anchor="end">${l}</text>`;
  }).join('');
  const body = `<path class="axis light" d="M${pad} ${pad / 2} V${H - pad} H${W - pad / 2}"/><path class="curve" d="${p}"/>${marks}` +
    `<text class="cap light" x="${pad}" y="${H - 12}">generation 0</text><text class="cap light" x="${W - pad}" y="${H - 12}" text-anchor="end">33</text>`;
  put('double-art', svg(`0 0 ${W} ${H}`, body, 'Exponential curve: one robot doubling 33 times reaches 8.6 billion'));
  const years = (weeks * 33 / 52);
  const out = document.getElementById('double-out');
  if (out) out.innerHTML = `<b>${years < 10 ? years.toFixed(1) : Math.round(years)} years</b> from one robot to 8.6 billion, if a robot and its kit build the next one every <b>${weeks} weeks</b>.`;
}

// ---- Wire it up.
function init() {
  rule(); gripper(); eyes(); force(); sibling(); printers(); motors(); ship(); sizes();
  const st = document.getElementById('stage');
  if (st) { startLine(+st.value); st.addEventListener('input', () => startLine(+st.value)); }
  const dw = document.getElementById('dweeks');
  if (dw) { doubling(+dw.value); dw.addEventListener('input', () => doubling(+dw.value)); }
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches || location.hash === '#still';
  if (still) hero(0); else { const loop = t => { hero(t); requestAnimationFrame(loop); }; requestAnimationFrame(loop); }
  const io = new IntersectionObserver(es => es.forEach(e => e.isIntersecting && e.target.classList.add('in')), { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => still ? el.classList.add('in') : io.observe(el));
}
document.addEventListener('DOMContentLoaded', init);

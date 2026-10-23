// The live preview's catalog logic, with no DOM or three.js in it so Scripts/test_gallery.py can run it under Node: which
// catalog designs are versions of which part, the versions each part row offers, the assembly a set of picks builds, and the
// picks that do not share an interface (flags) or that follow a change (voice-1a2680b8).
import POSES from './poses.js';

// Part rows, top to bottom, per family (Jake: Gripper, Handle, Base, Mount, Arm). The first part of a mix is always on; the
// rest may be 'none'. The Aero Hand is its own family (AGENTS.md, voice-a87f8d20): it is never a Generalist option.
export const MIX = {id:'generalist-mix', project:'Generalist Gripper', mix:true, parts:['gripper', 'handles', 'base', 'mount', 'arm']};
export const AERO_MIX = {id:'aero-mix', project:'Aero Hand', mix:true, parts:['aero', 'mount', 'arm']};
export const MIXES = [MIX, AERO_MIX];
export const LABELS = {gripper:'Gripper', handles:'Handle', base:'Base', mount:'Mount', arm:'Arm', aero:'Aero Hand'};
export const KEYS = Object.keys(LABELS);
export const mixOf = design => MIXES.find(item => item.id === design?.id);
// The arm dwarfs the gripper, so the Generalist assembly opens hand-held; ?arm=1&mount=1 (or the rows) turn them on.
const OFF_BY_DEFAULT = new Set(['arm', 'mount']);
const FOLLOWERS = new Set(['handles', 'mount']);   // the adapter parts: they move to fit a change, the others are flagged
export function initialPicks(query) {
  return {[MIX.id]:Object.fromEntries(MIX.parts.map(key => [key, query.get(key) || (OFF_BY_DEFAULT.has(key) ? 'none' : null)])),
          [AERO_MIX.id]:Object.fromEntries(AERO_MIX.parts.map(key => [key, query.get(key) || null]))};
}

// A part's kind comes from its name before ' — ': a handle is named like a strap slide or handle, a finger says finger, and
// the rest of a Base design (arms, gears, base, motor) is its base. Arm, Mount and Aero Hand parts ride inside a Base design
// but are published on their own, so a Base option never draws them (CARRIED).
const HANDLE = /strap slide|handle(?!-gear)/i, FINGER = /finger/i, HANDLE_GEAR = /handle-gear/i;
const CARRIED = /^(reBot Arm|SO-101 Arm|Wrist hub|Tool plate|Aero Hand)/;
const TOOL_PLATE = /^Tool plate/, AERO_PLATE = /^Aero Hand tool plate/;   // the Mount's plate for each tool
export const part = model => model.name.split(' — ')[0];
// 'Gripper 16' -> {kind:'gripper', version:'16'}, 'Handle 6' -> handles, 'Base 3' -> base. Each part counts on its own (AGENTS.md).
const KINDS = {gripper:'gripper', handle:'handles', base:'base', arm:'arm', mount:'mount', 'aero hand':'aero'};
export function partVersion(design) {
  const match = (design.name || '').match(/^(gripper|handle|base|arm|mount|aero hand)\s+(\d+[a-z]?)$/i);
  return match ? {kind:KINDS[match[1].toLowerCase()], version:match[2]} : null;
}
const versionOrder = version => parseFloat(version);
// Grippers, then Handles, Bases, Mounts, Arms, each by number: the order the rows list them in.
export function partOrder(design) {
  const found = partVersion(design);
  return found ? KEYS.indexOf(found.kind) * 1000 + versionOrder(found.version) : -1;
}
// Each option is {version, design, models}: the version shown in its row and the parts it adds. Fingers that only exist inside
// a later design come from the catalog's 'fingers' field (Handle 6 and Base 1-3 carry Gripper 21, from VERSIONS.txt).
export function mixOptions(catalog) {
  const family = catalog.designs.filter(design => MIXES.some(item => item.project === design.project) && partVersion(design) && design.models?.length)
    .sort((a, b) => partOrder(a) - partOrder(b) || a.id.localeCompare(b.id));
  const option = (version, design, keep) => ({version, design, models:design.models.filter(keep)});
  const of = kind => family.filter(design => partVersion(design).kind === kind);
  const grippers = of('gripper').map(design => option(partVersion(design).version, design, model => !HANDLE.test(part(model))));
  for (const design of family) {   // a later design's own fingers (Handle 6 -> Gripper 21), once per finger version
    if (design.fingers && !grippers.some(item => item.version === design.fingers)) grippers.push(option(design.fingers, design, model => FINGER.test(part(model))));
  }
  const handles = of('handles').map(design => option(partVersion(design).version, design, model => HANDLE.test(part(model))));
  const bases = of('base').map(design => option(partVersion(design).version, design,
    model => !HANDLE.test(part(model)) && !FINGER.test(part(model)) && !CARRIED.test(part(model))));
  const whole = kind => of(kind).map(design => option(partVersion(design).version, design, () => true));
  const order = (a, b) => versionOrder(a.version) - versionOrder(b.version) || a.version.localeCompare(b.version);
  return {gripper:grippers.filter(item => item.models.length).sort(order), handles:handles.filter(item => item.models.length),
          base:bases.filter(item => item.models.length), arm:whole('arm'), mount:whole('mount'), aero:whole('aero')};
}
// 'Base 12 (from Base 11, on the STS3215 only)': a picked part's own design says what it builds on. Fingers offered from a
// later design (Gripper 21 from Handle 6) are not that design's lineage, so they show bare.
export function optionLabel(label, item) {
  const own = partVersion(item.design)?.version === item.version && item.design.builds_on;
  return label + ' ' + item.version + (own ? ' (from ' + item.design.builds_on + (item.design.gist ? ', ' + item.design.gist : '') + ')' : '');
}
// Pairs of picks that do not share an interface (AGENTS.md: arm flange -> Mount, Mount tool plate -> Base or Aero Hand, Handle
// -> Base, fingers -> the hinges a Handle/Base was built on), from the catalog (fingers, carries, fits), not from names. Each is
// {key, other, text}: the two parts involved, key being the one the text is about when neither was just changed.
export function mixFlags(chosen) {
  const name = key => LABELS[key] + ' ' + chosen[key].version;
  const flags = [], flag = (key, other, text) => flags.push({key, other, text});
  const {gripper, base, arm, mount} = chosen;
  for (const key of ['base', 'handles']) {
    const built = chosen[key]?.design.fingers;
    if (built && gripper && built !== gripper.version) flag(key, 'gripper', name(key) + ' was built on Gripper ' + built + '; ' + name('gripper') + "'s hinges may not line up.");
  }
  if (arm && !mount) for (const key of ['base', 'aero']) if (chosen[key]) flag('mount', 'arm', name(key) + ' needs a Mount to sit on ' + name('arm') + '.');
  // A Mount takes the tool plates of its own number or of the one it names (catalog tool_plate: Mount 2 takes Mount 1's), so a
  // Base or Aero Hand built for Mount 1 fits Mount 2's hub (voice-790aa455).
  const takes = (item, wanted) => !!wanted && (wanted === item.version || wanted === item.design.tool_plate);
  if (mount && base && !takes(mount, base.design.carries?.Mount)) flag('base', 'mount', base.design.carries?.Mount
    ? name('base') + ' was built for Mount ' + base.design.carries.Mount + ', not ' + name('mount') + '.'
    : name('base') + ' has no wrist bracket (hand-held), so it does not fit ' + name('mount') + "'s tool plate.");
  // The Mount sits between the hand and the arm, so the Aero Hand is checked against the Mount it fits, and the Mount against the Arm.
  for (const [key, kind] of [['mount', 'arm'], ['aero', 'mount']]) {
    const other = chosen[kind], wants = chosen[key]?.design.fits?.[LABELS[kind]];
    if (other && wants && !(kind === 'mount' ? takes(other, wants) : wants === other.version)) flag(key, kind, name(key) + ' fits ' + LABELS[kind] + ' ' + wants + ', not ' + name(kind) + '.');
  }
  return flags;
}
// The assembly a mix's picks build: one row per part ({key, label, chosen, options, optional, sitsOut, notes}) and the models
// of every chosen part, each tagged with its row's key. `changed` is the row the user just set: an adapter part (FOLLOWERS: the
// Handle to the fingers, the Mount to the arm) that no longer fits it moves to the newest version that does (Arm 2 brings Mount 2)
// and says so in its notes; anything else that no longer fits, and an adapter with no fitting version, keeps a flag instead. The
// first build (picks still null) settles the adapters around the first row the same way, silently; a refresh never moves a pick.
// Picks never cascade to 'none': a part is only ever flagged off, not switched off.
export function buildMix(catalog, picks, which = MIX, changed = null) {
  const options = mixOptions(catalog), state = picks[which.id], [first] = which.parts;
  if (!options[first].length) return null;
  const chosen = Object.fromEntries(KEYS.map(key => [key, null]));
  for (const key of which.parts) {
    chosen[key] = key !== first && state[key] === 'none' ? null : options[key].find(item => item.version === state[key]) || options[key].at(-1) || null;
  }
  // A Base whose own parts include a handle-gear (Base 8 on: the geared pieces are the handles) carries its handles, so the Handle
  // row sits out while it is chosen and no second handle is drawn (the pick waits for another Base).
  // Miniature bases explicitly declare no_handles when the shared full-size handle interface cannot fit.
  const handlesInBase = !!chosen.base?.design.no_handles || !!chosen.base?.models.some(model => HANDLE_GEAR.test(part(model)));
  if (handlesInBase) chosen.handles = null;
  const follows = [], settle = changed || (which.parts.some(key => state[key] === null) ? first : null);
  if (settle) for (const flag of mixFlags(chosen)) {
    const key = flag.key === settle ? flag.other : flag.other === settle ? flag.key : null;
    if (!key || !FOLLOWERS.has(key) || !which.parts.includes(key) || follows.some(item => item.key === key)) continue;
    if (key === 'handles' && handlesInBase) continue;
    const involves = flags => flags.some(item => item.key === key || item.other === key);
    const fits = [...options[key]].reverse().find(item => !involves(mixFlags({...chosen, [key]:item})));
    if (fits && fits !== chosen[key]) {
      chosen[key] = fits;
      if (changed) follows.push({key, text:LABELS[key] + ' ' + fits.version + ' follows ' + (chosen[changed] ? LABELS[changed] + ' ' + chosen[changed].version : 'no ' + LABELS[changed].toLowerCase()) + '.'});
    }
  }
  for (const key of which.parts) if (!(key === 'handles' && handlesInBase)) state[key] = chosen[key] ? chosen[key].version : 'none';
  // The Aero Hand mix has no Base: the hand moves off the rack onto the Mount's hub (catalog on_mount, from aero_view_x), and the
  // Mount draws the plate of the tool it carries (the Aero Hand's, else the gripper's).
  const shift = model => chosen.aero?.design.on_mount ? {...model, shift:chosen.aero.design.on_mount} : model;
  if (chosen.aero) chosen.aero = {...chosen.aero, models:chosen.aero.models.map(shift)};
  if (chosen.mount) chosen.mount = {...chosen.mount, models:chosen.mount.models
    .filter(model => AERO_PLATE.test(part(model)) ? !!chosen.aero : !(TOOL_PLATE.test(part(model)) && chosen.aero))
    .map(model => AERO_PLATE.test(part(model)) ? shift(model) : model)};
  const flags = mixFlags(chosen), shownOn = flag => flag.key === changed ? flag.other : flag.key;
  const rows = which.parts.map(key => ({key, label:LABELS[key], chosen:chosen[key], options:options[key], optional:key !== first,
    sitsOut:key === 'handles' && handlesInBase ? (chosen.base?.design.no_handles ? 'No handle interface' : 'Handle in Base') : '',
    notes:[...follows.filter(item => item.key === key).map(item => ({text:item.text, follow:true})),
           ...flags.filter(flag => shownOn(flag) === key).map(flag => ({text:flag.text}))]}));
  // Handles, arms and gears ride the gripper's hinges (poses.js, keyed by the gripper's design). A Base whose fingers slide
  // instead (Base 5's racks) moves everything with its own slides.
  const slides = chosen.base && POSES[chosen.base.design.id]?.slides;
  return {...which, rows, pose:slides ? chosen.base.design.id : chosen.gripper?.design.id,
    name:which.parts.filter(key => chosen[key]).map(key => LABELS[key] + ' ' + chosen[key].version).join(' + '),
    models:which.parts.flatMap(key => chosen[key] ? chosen[key].models.map(model => ({...model, part:key})) : [])};
}

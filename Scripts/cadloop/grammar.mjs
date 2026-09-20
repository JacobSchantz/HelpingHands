/**
 * grammar.mjs — the sentences that never need a model.
 *
 * On the web loop the deterministic lane beat the model 900ms to 1.5ms. CAD is
 * a better fit still, because the thing a spoken dimension change names is
 * already a named number in params.scad: "make the jaw two millimetres longer"
 * is `mj_blade_profile` stations times 62/60, and there is nothing in that to
 * reason about.
 *
 * Three rules this file is built on:
 *
 *   1. Return null rather than guess. A wrong edit costs far more than a miss:
 *      he has to notice it, undo it and say it again. Null falls through to the
 *      model, which is a second and a half, and that is the cheaper failure.
 *
 *   2. Refuse a dead parameter out loud. Seven names in params.scad are read by
 *      nothing (see params.mjs). The naming instinct of every one of these
 *      verbs points straight at them — `mj_blade_len` is literally "blade
 *      length" — and editing one renders an identical picture. The loop must
 *      say so, not succeed quietly.
 *
 *   3. Move the position column of a station table, never the section columns.
 *      The blade's length lives in the first column of mj_blade_profile and
 *      mj_face_steps; its cross-section lives in the others. Scaling all of
 *      them is how you make a longer jaw that is also mysteriously fatter, and
 *      it would break params.scad's own tip-alignment assert.
 */

// ── numbers ────────────────────────────────────────────────────────────────

const WORD_NUM = {
  a: 1, an: 1, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7,
  eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12, fifteen: 15, twenty: 20,
  thirty: 30, forty: 40, fifty: 50, sixty: 60, half: 0.5, quarter: 0.25,
}

/** A quantity and what kind of quantity it is, or null when none was said. */
function quantity(text) {
  // "20 percent" / "20%"
  let m = /(-?\d+(?:\.\d+)?)\s*(?:%|percent|per cent)/.exec(text)
  if (m) return { kind: 'percent', value: Number(m[1]) }
  m = new RegExp(`\\b(${Object.keys(WORD_NUM).join('|')})\\s*(?:%|percent)`).exec(text)
  if (m) return { kind: 'percent', value: WORD_NUM[m[1]] }

  // "5 degrees"
  m = /(-?\d+(?:\.\d+)?)\s*(?:deg\b|degs\b|degree|degrees)/.exec(text)
  if (m) return { kind: 'deg', value: Number(m[1]) }

  // "2mm", "2 mm", "2 millimetres", and a bare number, which in this project
  // is always millimetres — every length in params.scad is mm.
  m = /(-?\d+(?:\.\d+)?)\s*(?:mm\b|millimet(?:er|re)s?\b|mil\b)/.exec(text)
  if (m) return { kind: 'mm', value: Number(m[1]) }
  m = /(-?\d+(?:\.\d+)?)\s*(?:cm\b|centimet(?:er|re)s?)/.exec(text)
  if (m) return { kind: 'mm', value: Number(m[1]) * 10 }
  m = /(?:^|\s)(-?\d+(?:\.\d+)?)(?:\s|$)/.exec(text)
  if (m) return { kind: 'mm', value: Number(m[1]) }

  // "two millimetres longer"
  m = new RegExp(`\\b(${Object.keys(WORD_NUM).join('|')})\\s*(?:mm|millimet(?:er|re)s?)\\b`).exec(text)
  if (m) return { kind: 'mm', value: WORD_NUM[m[1]] }
  m = new RegExp(`\\b(${Object.keys(WORD_NUM).join('|')})\\s*(?:deg|degrees?)\\b`).exec(text)
  if (m) return { kind: 'deg', value: WORD_NUM[m[1]] }

  return null
}

/** How hard an unquantified verb pushes. "a bit thicker" is not "way thicker". */
function vagueScale(text) {
  if (/\b(?:a bit|a little|slightly|a touch|a hair|marginally|just a)\b/.test(text)) return 0.04
  if (/\b(?:a lot|much|way|far|considerably|significantly|loads)\b/.test(text)) return 0.25
  if (/\b(?:double|twice)\b/.test(text)) return 1.0
  if (/\b(?:half)\b/.test(text)) return -0.5
  return 0.10
}

// ── what was said about it ─────────────────────────────────────────────────

const DIMS = [
  [/\b(?:longer|lengthen|extend|extended)\b/, 'length', +1],
  [/\b(?:shorter|shorten)\b/, 'length', -1],
  [/\b(?:thicker|fatter|beefier|chunkier|stronger|sturdier)\b/, 'thickness', +1],
  [/\b(?:thinner|slimmer|skinnier)\b/, 'thickness', -1],
  [/\b(?:wider|widen|broader)\b/, 'width', +1],
  [/\b(?:narrower|narrow|slimmer)\b/, 'width', -1],
  [/\b(?:taller|deeper)\b/, 'width', +1],
  [/\b(?:rounder|more round(?:ed)?|smoother|more fillet)\b/, 'fillet', +1],
  [/\b(?:sharper|less round(?:ed)?|crisper)\b/, 'fillet', -1],
  [/\b(?:bigger|larger|grow|scale up)\b/, 'scale', +1],
  [/\b(?:smaller|shrink|scale down|tinier)\b/, 'scale', -1],
  [/\b(?:open|opened|opening|further apart|apart)\b/, 'opening', +1],
  [/\b(?:close|closed|shut|together)\b/, 'opening', -1],
  [/\b(?:double|twice)\b/, 'scale', +1],
  [/\b(?:halve)\b/, 'scale', -1],
  [/\b(?:steeper|more angle|more taper)\b/, 'angle', +1],
  [/\b(?:shallower|less angle|less taper)\b/, 'angle', -1],
]

/** Subjects, longest phrase first so "fixed jaw" beats "jaw". */
const SUBJECTS = [
  [/\b(?:fixed jaw|static jaw|gripper body|wrist roll follower|follower|the body)\b/, 'fj'],
  [/\b(?:moving jaw|movable jaw|moving finger)\b/, 'mj'],
  [/\b(?:jaw opening|opening|the gap|grip gap)\b/, 'opening'],
  [/\b(?:fingertips?|the tips?)\b/, 'tip'],
  [/\b(?:screw holes?|clearance holes?|screws?|bolts?|fasteners?)\b/, 'screw'],
  [/\b(?:servo horn|the horn|horn recess)\b/, 'horn'],
  [/\b(?:cable bore|cable hole|cable channel|cable)\b/, 'cable'],
  [/\b(?:corners?|edges?|fille?ts?)\b/, 'corner'],
  [/\b(?:both jaws|the jaws|the fingers|the gripper)\b/, 'both'],
  // The crow beak is the same mechanism under different words: a gape is an
  // opening and a mandible is a jaw. Without these, "open the beak" misses the
  // grammar entirely and pays the model's second and a half for a sentence
  // that is one number. See plans/crow_gripper.md §8.
  [/\b(?:gape|commissure)\b/, 'opening'],
  [/\b(?:beak|bill|mandibles)\b/, 'both'],
  [/\b(?:jaw|finger|blade|mandible)\b/, 'mj'],
]

/**
 * The phrases a person says for a parameter that has an identifier nobody
 * speaks aloud. Two of these deliberately resolve to dead names — "blade
 * length" and "tip thickness" are the two most natural things to ask for and
 * the two most likely to do nothing — so that they reach the refusal instead
 * of falling through to a model that would happily set them.
 */
const PHRASES = [
  [/\bjaw opening\b|\bthe opening\b/, 'jaw_opening'],
  // Qualified radii first. "make the flange corner radius 10" contains the
  // words "corner radius", and the unqualified rule below happily took it and
  // rounded the jaw instead of the flange — a confident edit to the wrong part
  // of the gripper, which is the failure this lane is supposed to not have.
  [/\bflange (?:corner )?radius\b/, 'fj_flange_r'],
  [/\b(?:fixed jaw|body) (?:corner |tip )?radius\b/, 'fj_tip_r'],
  [/\bcorner radius\b|\bcorner round(?:ing)?\b/, 'mj_corner_r'],
  [/\btip radius\b|\bfingertip radius\b/, 'fj_tip_r'],
  [/\b(?:blade|jaw|finger) length\b/, 'mj_blade_len'],
  [/\btip thickness\b|\bfingertip thickness\b/, 'mj_tip_thickness'],
  [/\bcable bore\b|\bcable hole\b/, 'fj_cable_bore_d'],
  [/\bhorn recess\b/, 'horn_recess_d'],
  [/\bscrew (?:hole )?diameter\b|\bclearance hole\b/, 'm3_clear_d'],
]

function namedByPhrase(text) {
  for (const [re, name] of PHRASES) {
    const m = re.exec(text)
    if (m) return { name, at: m.index + m[0].length }
  }
  return null
}

function subjectOf(text) {
  for (const [re, name] of SUBJECTS) if (re.test(text)) return name
  return null
}

function dimOf(text) {
  for (const [re, name, sign] of DIMS) if (re.test(text)) return { dim: name, sign }
  return null
}

// ── the dead names, and what to say instead ────────────────────────────────
//
// Each of these is a number in params.scad that no geometry file reads. They
// are listed by name because the refusal has to be specific enough to be
// useful: "that parameter does nothing" is not actionable, "blade length is
// documentation, the stations drive it" is.

export const DEAD_TRAPS = {
  mj_blade_len: 'the blade is drawn by the mj_blade_profile stations, not by mj_blade_len',
  mj_tip_thickness: 'tip thickness is derived from the face and back planes',
  fj_tip_thickness: 'tip thickness is derived from the face and back planes',
  horn_bolt_circle_d: 'the horn pattern is driven by horn_bolt_square',
  horn_spigot_h: 'nothing reads it',
  fj_back_half_y: 'nothing reads it',
  fj_tip_step_rise: 'nothing reads it',
}

// ── levers ─────────────────────────────────────────────────────────────────
//
// One entry per (subject, dimension) that can be answered without a model.
// Each returns ops plus a sentence describing exactly what it did, because the
// loop reports that back and it is how a wrong guess gets caught in one turn.

function num(model, name) {
  const p = model.params.get(name)
  return p && p.scalar !== null ? p.scalar : null
}

/** The opening parameter, whichever model this params file belongs to. */
const OPENING_NAMES = ['jaw_opening', 'crow_opening']

/** Last value in column 0 of a station table — the tip's coordinate. */
function tableEnd(model, name) {
  const p = model.params.get(name)
  if (!p) return null
  const rows = [...p.raw.matchAll(/\[\s*(-?\d+(?:\.\d+)?)/g)].map(m => Number(m[1]))
  return rows.length ? rows[rows.length - 1] : null
}

const LEVERS = {
  // ---- moving jaw ---------------------------------------------------------
  'mj/length': (model, q) => {
    const root = num(model, 'mj_neck_y_start')          // -22, where the blade starts
    const tip = tableEnd(model, 'mj_blade_profile')     // -82, the fingertip
    if (root === null || tip === null) return null
    const len = Math.abs(tip - root)
    const scale = q.kind === 'percent' ? 1 + q.value / 100 : (len + q.value) / len
    if (!(scale > 0.2 && scale < 5)) return null
    const newLen = Math.round(len * scale * 100) / 100
    return {
      ops: [
        { kind: 'stretch', param: 'mj_blade_profile', root, scale, column: 0 },
        { kind: 'stretch', param: 'mj_face_steps', root, scale, column: 0 },
      ],
      // mj_blade_len is dead, but it is the file's stated blade length and
      // leaving it at 82 while the stations say 84 is a lie in the source.
      also: [{ kind: 'scalar', param: 'mj_blade_len', value: Math.abs(root) + newLen }],
      what: `moving jaw blade ${len}mm -> ${newLen}mm (stations stretched about y=${root})`,
    }
  },
  'mj/thickness': (model, q) => {
    // Front-to-back thickness is the gap between the gripping face (fixed, it
    // has to stay aligned with the other jaw) and the back plane. So the back
    // moves and the face does not.
    const cur = num(model, 'mj_back_x_at_pivot')
    if (cur === null) return null
    const by = q.kind === 'percent' ? cur * (q.value / 100) : q.value
    return {
      ops: [{ kind: 'scalar', param: 'mj_back_x_at_pivot', value: cur + by }],
      what: `moving jaw back face ${cur} -> ${Math.round((cur + by) * 100) / 100} (${by > 0 ? 'thicker' : 'thinner'})`,
    }
  },
  'mj/width': (model, q) => {
    const scale = q.kind === 'percent' ? 1 + q.value / 100 : null
    if (scale === null) {
      // A millimetre change to a tapering profile is ambiguous — which station?
      // Convert it at the root, where the blade is widest and he is looking.
      const p = model.params.get('mj_blade_profile')
      const m = /\[\s*-?\d+(?:\.\d+)?\s*,\s*(-?\d+(?:\.\d+)?)/.exec(p?.raw || '')
      if (!m) return null
      const half = Number(m[1])
      const k = (half + q.value / 2) / half
      return {
        ops: [{ kind: 'scaleCol', param: 'mj_blade_profile', scale: k, column: 1 }],
        what: `moving jaw blade ${q.value > 0 ? 'wider' : 'narrower'} by ${Math.abs(q.value)}mm across the pivot axis`,
      }
    }
    return {
      ops: [{ kind: 'scaleCol', param: 'mj_blade_profile', scale, column: 1 }],
      what: `moving jaw blade profile scaled ${Math.round(scale * 100)}% across the pivot axis`,
    }
  },
  'mj/fillet': (model, q) => scalarLever(model, q, 'mj_corner_r', 'moving jaw corner radius'),
  'mj/scale': (model, q) => LEVERS['mj/length'](model, q),

  // ---- fixed jaw ----------------------------------------------------------
  'fj/length': (model, q) => {
    const root = num(model, 'fj_body_top_z')            // 38, blade leaves the body
    const tip = num(model, 'fj_top_z')                  // 105.375, fingertip
    if (root === null || tip === null) return null
    const len = tip - root
    const scale = q.kind === 'percent' ? 1 + q.value / 100 : (len + q.value) / len
    if (!(scale > 0.2 && scale < 5)) return null
    const newTip = root + len * scale
    return {
      ops: [
        { kind: 'stretch', param: 'fj_face_steps', root, scale, column: 0 },
        { kind: 'scalar', param: 'fj_top_z', value: newTip },
        { kind: 'stretch-scalar', param: 'fj_back_z_start', root, scale },
      ],
      what: `fixed jaw blade ${Math.round(len * 100) / 100}mm -> ${Math.round(len * scale * 100) / 100}mm (tip z ${tip} -> ${Math.round(newTip * 100) / 100})`,
    }
  },
  'fj/width': (model, q) => {
    const scale = q.kind === 'percent' ? 1 + q.value / 100 : null
    if (scale === null) return null
    return {
      ops: [{ kind: 'scaleCol', param: 'fj_face_steps', scale, column: 2 }],
      what: `fixed jaw blade half-width scaled ${Math.round(scale * 100)}%`,
    }
  },
  'fj/fillet': (model, q) => scalarLever(model, q, 'fj_tip_r', 'fixed jaw tip radius'),
  'fj/scale': (model, q) => LEVERS['fj/length'](model, q),

  // ---- the opening --------------------------------------------------------
  'opening/opening': (model, q) => {
    // Two models share this lever and spell the same number differently:
    // `jaw_opening` on the stock gripper, `crow_opening` on the beak. Whichever
    // params file the loop was pointed at declares exactly one of them.
    const name = OPENING_NAMES.find(n => num(model, n) !== null)
    if (!name) return null
    const cur = num(model, name)
    const max = num(model, `${name}_max`) ?? 55
    let next = q.mode === 'abs' ? q.value
      // A proportional change to a closed jaw is a proportion of nothing, and
      // "open it a bit" from 0mm would silently stay shut. Measure the
      // proportion against the travel instead, which is what he means.
      : q.kind === 'percent' ? (cur === 0 ? (q.value / 100) * max : cur * (1 + q.value / 100))
        : cur + q.value
    next = Math.max(0, Math.min(max, next))
    if (next === cur) return null
    return {
      ops: [{ kind: 'scalar', param: name, value: next }],
      what: `${name.replace('_', ' ')} ${cur}mm -> ${Math.round(next * 100) / 100}mm at the fingertip`,
    }
  },

  // ---- everything else ----------------------------------------------------
  'screw/scale': (m, q) => scalarLever(m, q, 'm3_clear_d', 'screw clearance holes'),
  'screw/width': (m, q) => scalarLever(m, q, 'm3_clear_d', 'screw clearance holes'),
  'screw/thickness': (m, q) => scalarLever(m, q, 'm3_clear_d', 'screw clearance holes'),
  'cable/scale': (m, q) => scalarLever(m, q, 'fj_cable_bore_d', 'cable bore'),
  'cable/width': (m, q) => scalarLever(m, q, 'fj_cable_bore_d', 'cable bore'),
  'horn/scale': (m, q) => scalarLever(m, q, 'horn_recess_d', 'servo horn recess'),
  'horn/width': (m, q) => scalarLever(m, q, 'horn_recess_d', 'servo horn recess'),
  'horn/length': (m, q) => scalarLever(m, q, 'horn_recess_depth', 'servo horn recess depth'),
  'corner/fillet': (m, q) => scalarLever(m, q, 'mj_corner_r', 'moving jaw corner radius'),
  'corner/scale': (m, q) => scalarLever(m, q, 'mj_corner_r', 'moving jaw corner radius'),
  'tip/fillet': (m, q) => scalarLever(m, q, 'fj_tip_r', 'fixed jaw tip radius'),

  // Tip thickness is the one dimension a person naturally asks for that this
  // model genuinely does not own: it falls out of the face and back planes, and
  // both `mj_tip_thickness` and `fj_tip_thickness` are notes about the result.
  // Saying so is more useful than moving a number nothing reads.
  'tip/thickness': () => ({ refuse: 'mj_tip_thickness', why: DEAD_TRAPS.mj_tip_thickness }),
  'tip/scale': () => ({ refuse: 'mj_tip_thickness', why: DEAD_TRAPS.mj_tip_thickness }),
}

// Whatever part of the gripper he names, "open it" means one number: the
// fingertip gap. Route every subject's opening verb to the same lever.
const openingLever = LEVERS['opening/opening']
for (const k of ['mj/opening', 'fj/opening', 'both/opening', 'tip/opening',
  'opening/scale', 'opening/width', 'opening/length']) {
  LEVERS[k] = openingLever
}

function scalarLever(model, q, name, label) {
  const p = model.params.get(name)
  if (!p || p.scalar === null) return null
  const cur = p.scalar
  const next = q.mode === 'abs' ? q.value
    : q.kind === 'percent' ? cur * (1 + q.value / 100)
      : cur + q.value
  if (next <= 0) return null
  return {
    ops: [{ kind: 'scalar', param: name, value: next }],
    what: `${label} ${cur} -> ${Math.round(next * 1000) / 1000}`,
  }
}

// ── the one entry point ────────────────────────────────────────────────────

/**
 * @returns null            — say nothing, hand it to the model
 *          {refuse, why}   — say this out loud; the model must not try either
 *          {ops, what}     — apply these
 */
export function fastEdit(model, instruction) {
  // Strip sentence punctuation, but NOT a decimal point between two digits.
  // The naive version of this line turned "1.5mm thicker" into "1 5mm thicker",
  // which parsed as five millimetres and moved the back face 3.5mm too far —
  // a plausible-looking wrong answer, which is the only kind worth fearing.
  const text = ' ' + instruction.toLowerCase()
    .replace(/(?<!\d)[.,](?!\d)/g, ' ')
    .replace(/[!?;:]/g, ' ')
    .replace(/\s+/g, ' ') + ' '

  // A parameter named outright, either as its identifier ("set mj_corner_r to
  // 2") or by the phrase a person actually says for it. Both are exact, so
  // they bypass the lever table — but a dead name is still refused.
  const named = /\b([a-z]{2,3}_[a-z0-9_]+|jaw_opening|jaw_pivot_[xz]|m3_[a-z_]+|horn_[a-z_]+|fast_preview)\b/.exec(text)
  const alias = namedByPhrase(text)
  const name = named?.[1] ?? alias?.name
  if (name) {
    // "set X to N", "make X N", "X of N mm" — the number said about that name.
    // The third form looks just after the phrase itself, so "make the corner
    // radius 3" lands without needing the word "to".
    const abs = /\bto\s*(-?\d+(?:\.\d+)?)/.exec(text)
      || /\b(?:of|at|=)\s*(-?\d+(?:\.\d+)?)/.exec(text)
      || (alias ? /^\s*(-?\d+(?:\.\d+)?)\s*(?:mm|millimet(?:er|re)s?|degrees?)?\s*$/.exec(text.slice(alias.at)) : null)
    if (abs) {
      if (DEAD_TRAPS[name]) return { refuse: name, why: DEAD_TRAPS[name] }
      const p = model.params.get(name)
      if (p && p.scalar !== null && Number(abs[1]) !== p.scalar) {
        return {
          ops: [{ kind: 'scalar', param: name, value: Number(abs[1]) }],
          what: `${name} ${p.scalar} -> ${Number(abs[1])}`,
        }
      }
    }
  }

  const subject = subjectOf(text)
  const d = dimOf(text)
  if (!subject || !d) return null

  // "the jaws" means both, and both is two edits, which is the one case where
  // the grammar does two things at once. Opening is the exception: one number
  // already describes both jaws, so splitting it would edit it twice.
  if (subject === 'both' && d.dim !== 'opening') {
    const a = runLever('mj', d, model, text)
    const b = runLever('fj', d, model, text)
    if (!a || !b || a.refuse || b.refuse) return a?.refuse ? a : (b?.refuse ? b : null)
    return { ops: [...a.ops, ...b.ops], also: [...(a.also || []), ...(b.also || [])], what: `${a.what}; ${b.what}` }
  }

  return runLever(subject, d, model, text)
}

function runLever(subject, d, model, text) {
  const lever = LEVERS[`${subject}/${d.dim}`]
  if (!lever) return null

  let q = quantity(text)
  if (q) {
    // "set the opening to 25" is an absolute; "open it 10mm" is a change. An
    // absolute is only ever accepted for a dimension a single scalar owns —
    // the fingertip gap — because "make the jaw 90mm long" is genuinely
    // ambiguous between the 82mm pivot-to-tip figure and the 60mm blade, and
    // guessing between them is exactly what this lane must not do.
    const isAbs = d.dim === 'opening' && /\b(?:set|to)\b/.test(text)
    q = isAbs
      ? { ...q, value: Math.abs(q.value), mode: 'abs' }
      // "2mm shorter" is a negative change said with a positive number.
      : { ...q, value: Math.abs(q.value) * d.sign, mode: 'rel' }
  } else {
    q = { kind: 'percent', value: vagueScale(text) * 100 * d.sign, mode: 'rel' }
  }
  return lever(model, q)
}

export const _internals = { quantity, subjectOf, dimOf, vagueScale }

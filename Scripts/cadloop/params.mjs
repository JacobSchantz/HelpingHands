/**
 * params.mjs — reading, analysing and rewriting cad/openscad/params.scad.
 *
 * The one thing this file exists to prevent: a silent no-op.
 *
 * params.scad declares 80 top-level variables. Seven of them are read by
 * nothing — `mj_blade_len`, `mj_tip_thickness`, `fj_tip_thickness` and four
 * more are documentation of numbers that the geometry derives some other way.
 * They are also, unhappily, the ones with the most inviting names: a spoken
 * "make the jaw 2 mm longer" lands on `mj_blade_len` by every naming instinct
 * there is, rewrites 82.0 to 84.0, re-renders an identical picture and reports
 * success. That is the worst failure this loop can have, because it is the one
 * he cannot see.
 *
 * So liveness is computed, not assumed: a name is live only if it appears in a
 * geometry file. The grammar refuses the dead ones by name and says why.
 */

import fs from 'node:fs'
import path from 'node:path'

const GEOM = ['moving_jaw.scad', 'fixed_jaw.scad', 'gripper.scad', 'common.scad']

/**
 * Every top-level `name = value;` in the target's params file, with where its
 * number lives.
 *
 * `opts` names the target when it is not the stock gripper: `{ params, geom }`.
 * The crow beak (cad/openscad/crow) is a second model on the same mount, with
 * its own params file and its own geometry files, and liveness has to be
 * computed against *those* — a crow parameter read only by crow_lower.scad is
 * live, and reads of the stock params.scad it includes are not this loop's to
 * offer. That last part is the point: the beak's params file declares none of
 * the mount dimensions, so pointing the loop at it makes the arm interface
 * unreachable by construction rather than by care. See plans/crow_gripper.md D1.
 */
export function readParams(scadDir, opts = {}) {
  const file = path.join(scadDir, opts.params || 'params.scad')
  const src = fs.readFileSync(file, 'utf8')
  const lines = src.split('\n')
  const params = new Map()

  lines.forEach((line, i) => {
    // Top-level only: an assignment that starts at column 0. Anything indented
    // is inside a module or a list and is not a parameter.
    const m = /^([a-zA-Z_]\w*)\s*=\s*(.*)$/.exec(line)
    if (!m) return
    const [, name, rest] = m

    // The station tables — mj_blade_profile, mj_face_steps, fj_face_steps — are
    // the most important parameters in the file and every one of them spans a
    // dozen lines with a provenance comment per row. A single-line match misses
    // exactly those, and misses them silently: the lever that stretches the
    // blade simply reports that it cannot find the blade. So the value is read
    // forward to its terminating semicolon, with comments stripped first so a
    // `;` inside a `// [STEP] ...` note cannot end it early.
    let end = i
    let body = ''
    while (end < lines.length) {
      const text = (end === i ? rest : lines[end]).replace(/\/\/.*$/, '')
      const semi = text.indexOf(';')
      body += (end === i ? '' : ' ') + (semi >= 0 ? text.slice(0, semi) : text)
      if (semi >= 0) break
      end++
    }
    if (end >= lines.length) return

    const rawValue = body.trim()
    const num = /^(-?\d+(?:\.\d+)?)$/.exec(rawValue)
    params.set(name, {
      name,
      line: i,                                  // 0-based, the declaration line
      endLine: end,                             // 0-based, the line holding the ;
      raw: rawValue,
      scalar: num ? Number(num[1]) : null,      // null => a list, or an expression
      isList: rawValue.startsWith('['),
    })
  })

  const geom = (opts.geom || GEOM).map(f => {
    try { return fs.readFileSync(path.join(scadDir, f), 'utf8') } catch { return '' }
  }).join('\n')

  // A parameter is also live when the geometry reaches it through one of the
  // params file's OWN functions. On the stock gripper every station table is
  // named directly by moving_jaw.scad, so this never came up. On the crow beak
  // it is the normal case and the omission was fatal: crow_tomium, crow_culmen
  // and crow_gonys — the three lists that ARE the beak's shape — are read only
  // by crow_tomium_x() and friends inside crow_params.scad, and a name-in-
  // geometry test scores them `indirect`, which the loop never offers the edit
  // engine. The loop would have rendered the beak and refused to reshape it.
  const reached = reachedFunctions(src, geom)

  for (const p of params.values()) {
    const re = new RegExp(`\\b${p.name}\\b`)
    if (re.test(geom) || reached.some(body => re.test(body))) { p.liveness = 'live'; continue }
    // Not read by the geometry — but it may feed another parameter that is.
    const uses = src.match(new RegExp(`\\b${p.name}\\b`, 'g'))?.length ?? 0
    p.liveness = uses > 1 ? 'indirect' : 'dead'
  }

  return { file, src, lines, params }
}

/**
 * The bodies of the params file's own `function` definitions that the geometry
 * can actually reach — directly, or through another reached function.
 *
 * Deliberately functions only, not modules: a module in a params file emits
 * geometry, and there are none in either model. Comments are stripped first so
 * a parameter named only in a `// [STEP] ...` note is not mistaken for a read.
 */
function reachedFunctions(src, geom) {
  const bare = src.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/\/\/.*$/gm, ' ')
  const fns = new Map()
  // `function name(args) = <expression>;` — the body runs to the first `;`,
  // which is unambiguous because OpenSCAD function bodies are single expressions.
  for (const m of bare.matchAll(/\bfunction\s+([a-zA-Z_]\w*)\s*\(/g)) {
    const semi = bare.indexOf(';', m.index)
    if (semi > 0) fns.set(m[1], bare.slice(m.index, semi))
  }
  const live = new Set()
  for (;;) {
    const before = live.size
    for (const [name, body] of fns) {
      if (live.has(name)) continue
      const re = new RegExp(`\\b${name}\\s*\\(`)
      const inLive = [...live].some(n => re.test(fns.get(n)))
      if (re.test(geom) || inLive) live.add(name)
    }
    if (live.size === before) break
  }
  return [...live].map(n => fns.get(n))
}

/** Rewrite one scalar in place, touching only the number. Comments survive. */
export function setScalar(src, param, value) {
  const lines = src.split('\n')
  const line = lines[param.line]
  const rounded = Math.round(value * 1000) / 1000
  // Replace only the number between `=` and `;`, so the alignment and the
  // trailing `// [STEP] ...` provenance comment are left exactly as they were.
  const next = line.replace(/^(\s*[a-zA-Z_]\w*\s*=\s*)(-?\d+(?:\.\d+)?)(\s*;)/,
    (_, head, __, tail) => head + String(rounded) + tail)
  if (next === line) return null
  lines[param.line] = next
  return lines.join('\n')
}

/**
 * A station table is a list of rows whose first column is a coordinate along
 * the part's length. Stretching the part means moving those coordinates, and
 * nothing else: the half-heights and face offsets in the other columns are
 * cross-section, not length, and must not scale with it.
 *
 * The table may span many lines and carries one provenance comment per row, so
 * this rewrites numbers in place rather than regenerating the list.
 */
export function stretchTable(src, param, { root, scale, column = 0 }) {
  const lines = src.split('\n')
  const end = param.endLine

  let touched = 0
  for (let i = param.line; i <= end; i++) {
    lines[i] = lines[i].replace(/\[([^\]]*)\]/g, (whole, inner) => {
      // Skip the outer bracket of the list itself, which contains other rows.
      if (inner.includes('[')) return whole
      const cells = inner.split(',')
      if (column >= cells.length) return whole
      const cell = cells[column]
      const m = /^(\s*)(-?\d+(?:\.\d+)?)(\s*)$/.exec(cell)
      if (!m) return whole
      const moved = root + (Number(m[2]) - root) * scale
      cells[column] = m[1] + String(Math.round(moved * 1000) / 1000) + m[3]
      touched++
      return '[' + cells.join(',') + ']'
    })
  }
  return touched ? { src: lines.join('\n'), rows: touched } : null
}

/** Scale every value in one column of a station table (a cross-section change). */
export function scaleColumn(src, param, { scale, column }) {
  const lines = src.split('\n')
  const end = param.endLine
  let touched = 0
  for (let i = param.line; i <= end; i++) {
    lines[i] = lines[i].replace(/\[([^\]]*)\]/g, (whole, inner) => {
      if (inner.includes('[')) return whole
      const cells = inner.split(',')
      if (column >= cells.length) return whole
      const m = /^(\s*)(-?\d+(?:\.\d+)?)(\s*)$/.exec(cells[column])
      if (!m) return whole
      cells[column] = m[1] + String(Math.round(Number(m[2]) * scale * 1000) / 1000) + m[3]
      touched++
      return '[' + cells.join(',') + ']'
    })
  }
  return touched ? { src: lines.join('\n'), rows: touched } : null
}

/** Shift every value in one column by a fixed offset. */
export function shiftColumn(src, param, { by, column }) {
  return scaleColumnBy(src, param, column, v => v + by)
}

function scaleColumnBy(src, param, column, fn) {
  const lines = src.split('\n')
  const end = param.endLine
  let touched = 0
  for (let i = param.line; i <= end; i++) {
    lines[i] = lines[i].replace(/\[([^\]]*)\]/g, (whole, inner) => {
      if (inner.includes('[')) return whole
      const cells = inner.split(',')
      if (column >= cells.length) return whole
      const m = /^(\s*)(-?\d+(?:\.\d+)?)(\s*)$/.exec(cells[column])
      if (!m) return whole
      cells[column] = m[1] + String(Math.round(fn(Number(m[2])) * 1000) / 1000) + m[3]
      touched++
      return '[' + cells.join(',') + ']'
    })
  }
  return touched ? { src: lines.join('\n'), rows: touched } : null
}

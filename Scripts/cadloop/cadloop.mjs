#!/usr/bin/env node
/**
 * cadloop — a spoken sentence to a changed gripper, on the real CAD source.
 *
 * The loop, end to end:
 *
 *   Pebbles.app writes a note  ->  this process is already tailing that file
 *   ->  the grammar rewrites a number in params.scad for free, else a warm
 *       model names the parameter  ->  OpenSCAD re-renders  ->  the open tab
 *       swaps the image
 *
 * WHY OPENSCAD. Measured on this machine, on this part: a full CGAL render of
 * the whole assembly to PNG is 330ms. The same part in build123d costs 2.6s to
 * import OCCT and then 4.3s per jaw to rebuild, resident — 9s for the assembly
 * before anything is drawn, which is not a loop. Blender is a mesh modeller and
 * its own notes say nothing printable should originate there.
 *
 * WHAT THE STOPWATCH SAID, and what this file is shaped by:
 *
 *   - Deciding the edit is the whole budget, exactly as on the web loop. The
 *     grammar answers a dimension change in about a millisecond; the model
 *     lane costs ~1.5s, and almost all of that is the model.
 *   - Rendering is not the problem. 330ms of a ~1.9s model-lane turn, and
 *     ~0.33s of an otherwise ~0.34s grammar turn. Attacking it would be
 *     attacking the only cheap stage.
 *   - MAX_THINKING_TOKENS=0 is the single biggest per-turn lever, and CAD needs
 *     the reasoning even less than the web did: the answer is a parameter name
 *     and a number, both of which are in the prompt.
 *
 * WHAT IT REFUSES TO DO. params.scad declares seven numbers that no geometry
 * file reads — including `mj_blade_len`, which is the literal words "blade
 * length". Editing one re-renders a pixel-identical image. The loop computes
 * liveness at startup, refuses those by name, and independently hashes every
 * render so that a no-op is reported as a no-op rather than as success.
 *
 *   CADLOOP_REPO    the checkout (default ~/HelpingHands)
 *   CADLOOP_PART    assembly | fixed_jaw | moving_jaw | open   (default assembly)
 *   CADLOOP_PORT    preview server port (default 7333)
 *   CADLOOP_TRIGGER the word that claims a note (default "design")
 *   CADLOOP_MODEL   the fallback edit engine (default haiku)
 *   CADLOOP_NOTES   a scratch notes file, for exercising the loop by hand
 *   CADLOOP_NO_BROWSER / CADLOOP_NO_VOICE
 */

import { spawn, execFile } from 'node:child_process'
import { createServer } from 'node:http'
import crypto from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'
import os from 'node:os'

import { readParams, setScalar, stretchTable, scaleColumn } from './params.mjs'
import { fastEdit, DEAD_TRAPS } from './grammar.mjs'

const HOME = os.homedir()
const REPO = process.env.CADLOOP_REPO || path.join(HOME, 'HelpingHands')
const SCAD = path.join(REPO, 'cad', 'openscad')
const PARAMS = path.join(SCAD, 'params.scad')
const PART = process.env.CADLOOP_PART || 'assembly'
const PORT = Number(process.env.CADLOOP_PORT || 7333)
const TRIGGER = (process.env.CADLOOP_TRIGGER || 'design').toLowerCase()
const MODEL = process.env.CADLOOP_MODEL || 'haiku'
const OPENSCAD = process.env.OPENSCAD || '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

const PEB = path.join(HOME, '.pebbles')
const STATE = path.join(PEB, 'cadloop')
const BACKUPS = path.join(STATE, 'backups')
const TIMING = path.join(STATE, 'timing.log')
const CLAIM = path.join(PEB, 'cadloop.json')
fs.mkdirSync(BACKUPS, { recursive: true })

const log = (...a) => console.log(new Date().toISOString().slice(11, 23), ...a)
const stamp = (r) => { try { fs.appendFileSync(TIMING, JSON.stringify({ at: new Date().toISOString(), ...r }) + '\n') } catch {} }
const say = (l) => { if (!process.env.CADLOOP_NO_VOICE) { try { fs.appendFileSync(path.join(PEB, 'say.log'), l + '\n') } catch {} } }

if (!fs.existsSync(PARAMS)) { console.error(`cadloop: no params.scad at ${PARAMS}`); process.exit(2) }
if (!fs.existsSync(OPENSCAD)) { console.error(`cadloop: no OpenSCAD at ${OPENSCAD}`); process.exit(2) }

// ── the model of the source ────────────────────────────────────────────────
//
// Re-read before every instruction. The numbers move under us on every edit,
// and a lever that computes "82 + 2" off a stale 82 walks backwards.

let model = readParams(SCAD)
const liveNames = [...model.params.values()].filter(p => p.liveness === 'live').map(p => p.name)
const deadNames = [...model.params.values()].filter(p => p.liveness === 'dead').map(p => p.name)

// ── rendering ──────────────────────────────────────────────────────────────
//
// Two cameras, spawned together. On this machine the second view is very
// nearly free — the two processes overlap on separate cores — and one view of
// a gripper hides exactly the thing a jaw edit changes.

const VIEWS = {
  iso: ['--camera=-4,0,52,62,0,28,330', '--imgsize=900,990'],
  side: ['--camera=-4,0,52,90,0,0,300', '--imgsize=720,990'],
}
const shots = {}          // view -> { buf, hash }
let revision = 0

/**
 * Coarse curves for the loop, fine curves for anything exported.
 *
 * params.scad already carries a `fast_preview` switch that trades $fa 2 -> 12
 * and $fs 0.35 -> 1.2. Overriding it on the command line changes nothing on
 * disk, so the committed source stays at full fidelity and only the picture is
 * cheap. Measured on the assembly with the jaw open, one view:
 *
 *     CGAL --render, fine            840, 893, 527 ms
 *     CGAL --render, fast_preview    344, 381, 488 ms
 *     OpenCSG preview, fine          999, 1034, 495 ms
 *     OpenCSG preview, fast_preview  648, 723, 789 ms
 *
 * Note the second half of that table, which is why it was worth measuring
 * rather than assuming: OpenCSG "preview" mode — the thing named for being the
 * fast one — is consistently SLOWER than a full CGAL render here, because
 * standing up an offscreen GL context costs more than the booleans do on a
 * part this size. The win is entirely in the facet count. Every hole in this
 * model is a cylinder, and at $fa=2 a Ø1.5 vent is 180 segments.
 */
const FAST = process.env.CADLOOP_FINE ? [] : ['-D', 'fast_preview=true']

function renderOne(view, part) {
  return new Promise((res) => {
    const out = path.join(STATE, `${view}.png`)
    const args = ['--render', '-D', `part="${part}"`, ...FAST, ...VIEWS[view],
      '--colorscheme=Tomorrow', '-o', out, 'gripper.scad']
    execFile(OPENSCAD, args, { cwd: SCAD, timeout: 30000 }, (err, _so, se) => {
      if (err) return res({ view, ok: false, err: String(se || err).slice(0, 400) })
      // OpenSCAD reports a failed assert on stderr and still exits 0 in some
      // builds, so the text is checked as well as the code.
      if (/ERROR:|Assertion.*failed/i.test(String(se))) {
        return res({ view, ok: false, err: String(se).split('\n').filter(l => /ERROR|Assert/i.test(l)).join(' ').slice(0, 400) })
      }
      let buf; try { buf = fs.readFileSync(out) } catch { return res({ view, ok: false, err: 'no output' }) }
      res({ view, ok: true, buf, hash: crypto.createHash('sha1').update(buf).digest('hex') })
    })
  })
}

/**
 * @returns { ok, ms, changed }  — `changed` false means the render is
 *          byte-identical to the last one, i.e. the edit did nothing visible.
 *          OpenSCAD is deterministic here (verified: repeated renders of an
 *          untouched source produce identical bytes), so this is a real signal
 *          and not a heuristic.
 */
async function render(part = PART) {
  const t = Date.now()
  const results = await Promise.all(Object.keys(VIEWS).map(v => renderOne(v, part)))
  const ms = Date.now() - t
  const bad = results.find(r => !r.ok)
  if (bad) return { ok: false, ms, err: bad.err }
  let changed = false
  for (const r of results) {
    if (shots[r.view]?.hash !== r.hash) changed = true
    shots[r.view] = { buf: r.buf, hash: r.hash }
  }
  if (changed) { revision++; push() }
  return { ok: true, ms, changed }
}

// ── the preview he is looking at ───────────────────────────────────────────
//
// A page held open in Chrome, told over SSE that a new revision exists. The
// image is fetched and decoded before it is swapped in, so the view never
// blanks between edits — the same reason the web loop leaned on HMR instead of
// reloading the tab. Nothing about the page is reloaded per iteration.

const clients = new Set()
function push() {
  for (const c of clients) { try { c.write(`data: ${revision}\n\n`) } catch {} }
}

const PAGE = `<!doctype html><html><head><meta charset="utf-8">
<title>SO-101 gripper</title>
<style>
  :root { color-scheme: dark; --bg:#14161a; --fg:#e8eaed; --dim:#8b929d; --line:#262a31; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--fg); height:100vh; display:flex; flex-direction:column;
         font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; }
  header { padding:10px 16px; border-bottom:1px solid var(--line); display:flex; gap:16px; align-items:baseline; flex:0 0 auto; }
  b { font-weight:600; letter-spacing:.02em; }
  #what { color:var(--dim); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #rev { color:var(--dim); font-variant-numeric:tabular-nums; }
  main { flex:1; display:flex; gap:8px; padding:8px; min-height:0; }
  figure { margin:0; flex:1; display:flex; align-items:center; justify-content:center; min-width:0;
           background:#0e1013; border:1px solid var(--line); border-radius:6px; }
  img { max-width:100%; max-height:100%; object-fit:contain; display:block; }
  .flash { animation:f .5s ease-out; }
  @keyframes f { from { box-shadow:inset 0 0 0 2px #4a9eff; } to { box-shadow:inset 0 0 0 2px transparent; } }
</style></head><body>
<header><b>SO-101 gripper</b><span id="what">say: pebbles, ${TRIGGER}, make the jaw 2mm longer</span><span id="rev">r0</span></header>
<main><figure><img id="iso"></figure><figure><img id="side"></figure></main>
<script>
const imgs = { iso: document.getElementById('iso'), side: document.getElementById('side') }
async function load(rev) {
  // Decode both before either is shown, so the pair never disagrees and the
  // panel never goes blank mid-edit.
  const next = await Promise.all(Object.keys(imgs).map(async v => {
    const im = new Image(); im.src = '/view/' + v + '.png?r=' + rev
    await im.decode().catch(() => {}); return [v, im.src]
  }))
  for (const [v, src] of next) imgs[v].src = src
  document.getElementById('rev').textContent = 'r' + rev
  document.querySelectorAll('figure').forEach(f => { f.classList.remove('flash'); void f.offsetWidth; f.classList.add('flash') })
}
const es = new EventSource('/events')
es.onmessage = e => load(e.data)
es.addEventListener('what', e => { document.getElementById('what').textContent = e.data })
load(0)
</script></body></html>`

createServer((req, res) => {
  const url = new URL(req.url, 'http://x')
  if (url.pathname === '/') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); return res.end(PAGE)
  }
  if (url.pathname.startsWith('/view/')) {
    const v = url.pathname.slice(6).replace('.png', '')
    const shot = shots[v]
    if (!shot) { res.writeHead(404); return res.end() }
    res.writeHead(200, { 'content-type': 'image/png', 'cache-control': 'no-store' })
    return res.end(shot.buf)
  }
  if (url.pathname === '/events') {
    res.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-cache', connection: 'keep-alive' })
    res.write(`data: ${revision}\n\n`)
    clients.add(res)
    req.on('close', () => clients.delete(res))
    return
  }
  res.writeHead(404); res.end()
}).listen(PORT, () => log(`preview on http://localhost:${PORT}`))

function tell(line) { for (const c of clients) { try { c.write(`event: what\ndata: ${line}\n\n`) } catch {} } }

// ── the warm edit engine ───────────────────────────────────────────────────
//
// Only for the sentences the grammar declines. Tools off, no MCP, no project
// context, thinking off: it is an edit engine, not an agent. The protocol is a
// single line because CAD gives us something the web loop never had — the
// thing being changed already has a name, so the model does not have to
// describe a location, only pick a name and a number.

const SYS = `You are an edit engine for a live voice-driven CAD loop on an OpenSCAD model of the
SO-101 robot gripper. Every dimension is a named variable in params.scad.

You get the current parameter values, then short spoken instructions.
Reply with ONE line and nothing else. No prose, no backticks, no explanation.

  SET <param> <number>        set a parameter to an absolute value
  SKIP                        the instruction is not a change to this model

Only these parameter names exist. Using any other name is an error:
${liveNames.join(' ')}

These names appear in the file but are read by NO geometry. Never SET them; reply SKIP:
${deadNames.join(' ')}

All lengths are millimetres, angles degrees. jaw_opening is the fingertip gap.
Reply SKIP if the instruction names nothing in that list.`

const ENGINE_CWD = path.join(os.tmpdir(), 'cadloop-engine')
fs.mkdirSync(ENGINE_CWD, { recursive: true })
let engine = null, pending = null, engineReady = false

function startEngine() {
  engine = spawn('claude', [
    '-p', '--input-format', 'stream-json', '--output-format', 'stream-json', '--verbose',
    '--model', MODEL, '--permission-mode', 'bypassPermissions',
    '--disallowed-tools', 'Bash,Read,Edit,Write,Glob,Grep,Task,WebFetch,WebSearch,NotebookEdit,TodoWrite',
    '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
    '--append-system-prompt', SYS,
  ], {
    cwd: ENGINE_CWD, stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, MAX_THINKING_TOKENS: '0', DISABLE_NON_ESSENTIAL_MODEL_CALLS: '1', DISABLE_TELEMETRY: '1' },
  })
  let buf = ''
  engine.stdout.on('data', (c) => {
    buf += c
    let i
    while ((i = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, i); buf = buf.slice(i + 1)
      if (!line.trim()) continue
      let j; try { j = JSON.parse(line) } catch { continue }
      if (j.type === 'system' && j.subtype === 'init') { engineReady = true; log('engine warm') }
      if (j.type === 'result' && pending) { const p = pending; pending = null; p(j.result || '') }
    }
  })
  engine.stderr.on('data', () => {})
  engine.on('exit', () => { engineReady = false; log('engine died, restarting'); setTimeout(startEngine, 500) })
}

function askEngine(text, timeoutMs = 20000) {
  return new Promise((res) => {
    if (!engine || engine.killed) return res('')
    const to = setTimeout(() => { if (pending) { pending = null; res('') } }, timeoutMs)
    pending = (r) => { clearTimeout(to); res(r) }
    engine.stdin.write(JSON.stringify({ type: 'user', message: { role: 'user', content: [{ type: 'text', text }] } }) + '\n')
  })
}

/** The parameters, as the engine is shown them: name, value, one line each. */
function paramSheet() {
  return [...model.params.values()]
    .filter(p => p.liveness === 'live' && p.scalar !== null)
    .map(p => `${p.name}=${p.scalar}`).join(' ')
}

// ── applying ops ───────────────────────────────────────────────────────────

function applyOps(src, ops) {
  let out = src
  const done = []
  for (const op of ops) {
    const p = model.params.get(op.param)
    if (!p) return { error: `no parameter ${op.param}` }
    if (DEAD_TRAPS[op.param] && op.kind !== 'scalar') return { error: `${op.param} is not read by any geometry` }
    let next = null
    if (op.kind === 'scalar') {
      next = setScalar(out, p, op.value)
    } else if (op.kind === 'stretch-scalar') {
      if (p.scalar === null) return { error: `${op.param} is not a number` }
      next = setScalar(out, p, op.root + (p.scalar - op.root) * op.scale)
    } else if (op.kind === 'stretch') {
      const r = stretchTable(out, p, op); next = r?.src
    } else if (op.kind === 'scaleCol') {
      const r = scaleColumn(out, p, op); next = r?.src
    }
    if (!next) return { error: `${op.param} did not change` }
    out = next
    done.push(op.param)
  }
  return { src: out, done }
}

// ── one instruction ────────────────────────────────────────────────────────

let busy = false

async function onNote(rawText, heardAt) {
  const instruction = claimNote(rawText)
  if (!instruction) return
  if (busy) { log('busy, dropped:', instruction.slice(0, 60)); return }
  busy = true
  const t0 = Date.now()
  try {
    model = readParams(SCAD)
    const src = model.src
    const backup = path.join(BACKUPS, `${Date.now()}-params.scad`)
    fs.writeFileSync(backup, src)

    // Fast lane.
    let lane = 'grammar'
    let plan = fastEdit(model, instruction)
    if (plan?.refuse) {
      const line = `${plan.refuse} is in the file but no geometry reads it — ${plan.why}. Nothing changed.`
      log(`REFUSED ${Date.now() - t0}ms — ${line}`)
      stamp({ lane: 'grammar', decide_ms: Date.now() - t0, applied: false, reason: 'dead-param', instruction })
      tell(line); say(line)
      return
    }

    // Model lane.
    if (!plan) {
      lane = 'model'
      const reply = await askEngine(`PARAMS: ${paramSheet()}\n\nINSTRUCTION: ${instruction}`)
      const m = /^\s*SET\s+([a-zA-Z_]\w*)\s+(-?\d+(?:\.\d+)?)\s*$/m.exec(reply || '')
      if (!m) {
        const why = /SKIP/i.test(reply || '') ? 'nothing in the model matches that' : 'I could not turn that into a parameter change'
        log(`MODEL ${Date.now() - t0}ms — ${why} (${JSON.stringify(reply || '').slice(0, 80)})`)
        stamp({ lane, decide_ms: Date.now() - t0, applied: false, reason: 'skip', instruction })
        tell(why); say(why + '.')
        return
      }
      if (DEAD_TRAPS[m[1]]) {
        const line = `${m[1]} is read by no geometry — ${DEAD_TRAPS[m[1]]}. Nothing changed.`
        log(`MODEL ${Date.now() - t0}ms — refused dead param`)
        stamp({ lane, decide_ms: Date.now() - t0, applied: false, reason: 'dead-param', instruction })
        tell(line); say(line)
        return
      }
      const p = model.params.get(m[1])
      plan = { ops: [{ kind: 'scalar', param: m[1], value: Number(m[2]) }], what: `${m[1]} ${p?.scalar} -> ${Number(m[2])}` }
    }

    const decide_ms = Date.now() - t0

    const applied = applyOps(src, [...plan.ops, ...(plan.also || [])])
    if (applied.error) {
      log(`${lane.toUpperCase()} ${decide_ms}ms — ${applied.error}`)
      stamp({ lane, decide_ms, applied: false, reason: applied.error, instruction })
      tell(applied.error); say(`That one did not land — ${applied.error}.`)
      return
    }

    const tw = Date.now()
    fs.writeFileSync(PARAMS, applied.src)
    const write_ms = Date.now() - tw

    // The render is the parse check. OpenSCAD compiles params.scad and runs its
    // own asserts — the jaw-alignment and wall-thickness ones at the bottom of
    // the file — so a dimension that cannot be built fails here rather than
    // being discovered later in a print. A failure is rolled back immediately,
    // because the next instruction is spoken against what he can see.
    const r = await render()
    if (!r.ok) {
      fs.writeFileSync(PARAMS, src)
      await render()
      const line = `${plan.what} would not build: ${r.err.slice(0, 160)}. Put it back.`
      log(`${lane.toUpperCase()} ${decide_ms}ms — rejected — ${r.err.slice(0, 120)}`)
      stamp({ lane, decide_ms, render_ms: r.ms, applied: false, reason: 'render-failed', instruction, err: r.err.slice(0, 200) })
      tell(line); say(line)
      return
    }

    const total = Date.now() - heardAt
    if (!r.changed) {
      const line = `${plan.what} — but the render is pixel-identical, so that changed nothing you can see.`
      log(`${lane.toUpperCase()} ${decide_ms}ms decide ${r.ms}ms render — NO VISIBLE CHANGE — "${instruction}"`)
      stamp({ lane, decide_ms, write_ms, render_ms: r.ms, total_ms: total, applied: true, visible: false, instruction, what: plan.what })
      tell(line); say(line)
      return
    }

    log(`${lane.toUpperCase()} decide ${decide_ms}ms · write ${write_ms}ms · render ${r.ms}ms · total ${total}ms — ${plan.what}`)
    stamp({ lane, decide_ms, write_ms, render_ms: r.ms, total_ms: total, applied: true, visible: true, instruction, what: plan.what, params: applied.done })
    tell(plan.what)
  } catch (e) {
    log('error', String(e).slice(0, 300))
  } finally {
    busy = false
  }
}

// ── the spoken line ────────────────────────────────────────────────────────
//
// Same bridge as the web loop, and the same known failure: session.json moves
// when a session restarts, and a loop pinned to a dead notes file is silently
// useless. So the path is re-resolved whenever session.json changes.
//
// The trigger word is the arbitration with the voice session, and it has to be
// a word in the sentence, because both readers see the line at the same instant
// and anything this process could write afterwards arrives too late.

const WAKE = /^\s*(?:hey\s+)?(?:pebbles|jarvis|peebles|pebble)\b[\s,]*/i

function claimNote(text) {
  const t = text.replace(WAKE, '').trim()
  const re = new RegExp(`^${TRIGGER}\\b[\\s,:-]*`, 'i')
  if (!re.test(t)) return null
  return t.replace(re, '').trim() || null
}

let tailProc = null, notesPath = null

function resolveNotes() {
  if (process.env.CADLOOP_NOTES) return process.env.CADLOOP_NOTES
  try { return JSON.parse(fs.readFileSync(path.join(PEB, 'session.json'), 'utf8')).notes || null } catch { return null }
}

function attachTail() {
  const next = resolveNotes()
  if (!next || next === notesPath) return
  if (tailProc) tailProc.kill()
  notesPath = next
  log('listening on', notesPath)
  writeClaim()
  tailProc = spawn('tail', ['-n', '0', '-F', notesPath])
  let buf = ''
  tailProc.stdout.on('data', (c) => {
    buf += c
    let i
    while ((i = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, i); buf = buf.slice(i + 1)
      if (!line.trim()) continue
      let note; try { note = JSON.parse(line) } catch { continue }
      if (note.text) onNote(note.text, Date.now())
    }
  })
  tailProc.stderr.on('data', () => {})
}

function writeClaim() {
  try {
    fs.writeFileSync(CLAIM, JSON.stringify({
      pid: process.pid, repo: REPO, source: path.relative(REPO, PARAMS),
      trigger: TRIGGER, url: `http://localhost:${PORT}/`, notes: notesPath,
      startedAt: new Date().toISOString(),
    }, null, 2) + '\n')
  } catch {}
}
function dropClaim() {
  try { if (JSON.parse(fs.readFileSync(CLAIM, 'utf8')).pid === process.pid) fs.rmSync(CLAIM, { force: true }) } catch {}
}

function openPage() {
  if (process.env.CADLOOP_NO_BROWSER) return
  const url = `http://localhost:${PORT}/`
  const script = `tell application "Google Chrome"
      activate
      set found to false
      repeat with w in windows
        repeat with t in tabs of w
          if URL of t starts with "${url}" then
            set active tab index of w to (index of t)
            set index of w to 1
            set found to true
          end if
        end repeat
      end repeat
      if not found then
        if (count of windows) = 0 then make new window
        tell window 1 to make new tab with properties {URL:"${url}"}
      end if
    end tell`
  execFile('osascript', ['-e', script], { timeout: 8000, killSignal: 'SIGKILL' }, (e) => {
    if (e) execFile('open', ['-a', 'Google Chrome', url], () => {})
  })
}

// ── go ─────────────────────────────────────────────────────────────────────

log('cadloop starting')
log(`source ${path.relative(REPO, PARAMS)}  part "${PART}"  trigger "${TRIGGER}"  model ${MODEL}`)
log(`${liveNames.length} live parameters, ${deadNames.length} dead (refused): ${deadNames.join(' ')}`)

startEngine()
try { fs.watch(PEB, (_, f) => { if (f === 'session.json') setTimeout(attachTail, 150) }) } catch {}
attachTail()
setInterval(attachTail, 10000).unref?.()

const first = await render()
log(first.ok ? `first render ${first.ms}ms` : `first render FAILED: ${first.err}`)
openPage()
askEngine('Reply exactly: SKIP').then(() => log('engine first turn done'))
log(`ready — say: "pebbles, ${TRIGGER}, make the jaw 2mm longer"`)

const bye = () => { dropClaim(); tailProc?.kill(); engine?.kill(); process.exit(0) }
process.on('SIGTERM', bye); process.on('SIGINT', bye); process.on('exit', dropClaim)

#!/usr/bin/env python3
"""2.4 live preview (2.5, 2.6: unchanged; 3.1: ten parts, adding the arms, gears, base and motor; 3.2: eight, the drivers, base and motor; 3.3: nine, the side gears, pinion, base and motor; Base 4 and 7: seven, each handle in its gear): render the viewer parts (assembled pose, as viewer_parts.json) for a set of parameter overrides,
fast enough to follow a slider. Scripts/serve_designs.py runs this for the gallery's Tune panel.

    python3 live_render.py --values '{"plate": 10, "beak_stretch": 1.9}' --out /tmp/tuned

Writes <out>/<part>.stl and <out>/result.json {ok, pivot, seconds, retraced, error}. Outline params re-run
trace_photo.py (cached by value in --cache); solid params only re-run OpenSCAD (Manifold backend, ~0.1 s a part).
Nothing in this folder is written: params.scad and trace_px.scad go to a scratch copy."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, re, shutil, subprocess, sys, tempfile, time
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import params
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PARTS=('right','left','right_gear','left_gear','pinion','base','top_plate','bracket','tool_plate','hub','aero_plate','motor')   # Base 10: + the top plate and the four wrist-mount parts (Base 4: seven, the handles part of the gears; 3.3: nine)


def outline(vals,overrides,cache):
    """A trace_px.scad for these values: the committed one, a cached one, or a fresh trace."""
    if not params.outline_changed(overrides):return HERE/'trace_px.scad',False
    stage={p['name']:p['stage'] for p in params.specs()}
    key=hashlib.sha256(json.dumps({k:v for k,v in vals.items() if stage[k]!='solid'},sort_keys=True).encode()).hexdigest()[:20]
    path=Path(cache or tempfile.gettempdir())/f'trace-{key}.scad';path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        import trace_photo   # numpy/scipy/matplotlib: only imported when the outline moves
        trace_photo.configure(vals);tmp=path.with_suffix('.part.scad');trace_photo.main(out=tmp,quiet=True);tmp.replace(path)
    return path,True


def render(overrides,out,cache=None):
    t0=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    try:
        vals=params.values(overrides);trace,retraced=outline(vals,overrides,cache)
    except Exception as e:   # a bad name/value, or an outline the tracer cannot build
        return dict(ok=False,error=f'{type(e).__name__}: {e}',seconds=round(time.time()-t0,2))
    with tempfile.TemporaryDirectory(prefix='gripper25_') as work:
        work=Path(work);shutil.copy(HERE/'gripper.scad',work);shutil.copy(trace,work/'trace_px.scad')
        params.write_scad(work/'params.scad',vals)
        def one(k):
            dst=out/f'{k}.stl';tmp=out/f'.{k}.building.stl'
            p=subprocess.run([SCAD,'--backend','manifold','--export-format','binstl','-D',f'part="viewer_{k}"','-o',str(tmp),str(work/'gripper.scad')],
                             capture_output=True,text=True,timeout=60)
            log=p.stdout+p.stderr
            if p.returncode or not tmp.exists() or 'ERROR' in log:
                tmp.unlink(missing_ok=True)
                msg=next((m.group(1) for m in re.finditer(r'Assertion .*? failed: "(.*?)"',log)),None)   # gripper.scad's own words
                return k,msg or (log.strip().splitlines() or ['OpenSCAD failed'])[-1],None
            tmp.replace(dst);m=re.search(r'ECHO: pivot = ([-\d.e]+)',log)
            return k,None,float(m.group(1)) if m else None
        with concurrent.futures.ThreadPoolExecutor(len(PARTS)) as ex:results=list(ex.map(one,PARTS))
    errors=list(dict.fromkeys(e for _,e,_ in results if e))   # one message, not one per part
    pivot=next((v for *_,v in results if v is not None),None)
    return dict(ok=not errors,error='; '.join(errors) or None,pivot=pivot,retraced=retraced,seconds=round(time.time()-t0,2),
                values={k:vals[k] for k in overrides})


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--values',default='{}');ap.add_argument('--out',required=True);ap.add_argument('--cache')
    a=ap.parse_args();r=render(json.loads(a.values),a.out,a.cache)
    (Path(a.out)/'result.json').write_text(json.dumps(r)+'\n');print(json.dumps(r));sys.exit(0 if r['ok'] else 1)

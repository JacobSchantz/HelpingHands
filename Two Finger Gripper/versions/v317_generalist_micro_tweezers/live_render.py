"""Render a scratch copy for the gallery's Tune protocol; never edits this version."""
from pathlib import Path
import argparse,json,shutil,subprocess,tempfile,time
from concurrent.futures import ThreadPoolExecutor
import params,export_models,genus
from geometry import envelope
HERE=Path(__file__).resolve().parent
def render(overrides,out,cache=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);started=time.time()
    try:
        values=params.values(overrides)
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);shutil.copy(HERE/'gripper.scad',folder)
            params.write_scad(folder/'params.scad',values)
            def one(part):
                target=out/(part[0]+'.stl')
                subprocess.run([export_models.SCAD,'--export-format','binstl','-D',f'part="{part[0]}"',
                    '-o',str(target),str(folder/'gripper.scad')],capture_output=True,check=True,timeout=60)
            with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(one,export_models.PARTS))
        swept=envelope(out,values)
        if not swept['passed']:raise ValueError('Moving envelope exceeds the 24.8 mm servo width; reduce jaw length, stroke or gear size.')
        return dict(envelope=swept,ok=True,pivot=values['gear_m']*values['gear_teeth'],retraced=False,seconds=round(time.time()-started,2),values=overrides)
    except Exception as error:return dict(ok=False,error=str(error))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--values',default='{}');p.add_argument('--out',required=True);p.add_argument('--cache')
    a=p.parse_args();r=render(json.loads(a.values),a.out,a.cache)
    (Path(a.out)/'result.json').write_text(json.dumps(r)+'\n');print(json.dumps(r));raise SystemExit(0 if r['ok'] else 1)

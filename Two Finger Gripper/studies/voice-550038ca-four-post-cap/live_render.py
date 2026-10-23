"""Tune compact clearance in an isolated directory, keeping bought parts actual size."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,shutil,subprocess,tempfile,time
import params
from export_models import PARTS,SCAD
HERE=Path(__file__).resolve().parent
def render(overrides,out,cache=None):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);started=time.monotonic()
 try:
  v=params.values(overrides)
  with tempfile.TemporaryDirectory(prefix='compact-overhead-') as tmp:
   work=Path(tmp)
   for file in HERE.glob('*.scad'):shutil.copy2(file,work/file.name)
   shutil.copytree(HERE/'reference',work/'reference')
   params.write_scad(work/'params.scad',v)
   def one(k):
    result=subprocess.run([SCAD,'--backend','manifold','--export-format','binstl','-D',f'part="viewer_{k}"','-o',str(out.resolve()/f'{k}.stl'),str(work/'gripper.scad')],capture_output=True,text=True)
    if result.returncode or 'WARNING' in result.stderr:raise RuntimeError(result.stderr)
   with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(one,PARTS+['motor','stock_plate']))
  return dict(ok=True,pivot=v['pivot_spacing']/2*v['scale_factor'],seconds=time.monotonic()-started,retraced=False,values=overrides)
 except Exception as e:return dict(ok=False,error=str(e))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--values',default='{}');p.add_argument('--out',required=True);p.add_argument('--cache');a=p.parse_args()
 result=render(json.loads(a.values),a.out,a.cache);(Path(a.out)/'result.json').write_text(json.dumps(result)+'\n');print(json.dumps(result));raise SystemExit(0 if result['ok'] else 1)

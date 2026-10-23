"""Gallery Tune: resize original fingers/drive while retaining real mounting interfaces."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,shutil,subprocess,tempfile,time
import params
from export_models import PARTS,SCAD
HERE=Path(__file__).resolve().parent

def render(overrides,out,cache=None):
 started=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
 try:
  v=params.values(overrides)
  from hardware_fit import hardware_fit
  fit=hardware_fit(v)
  if not fit['passed']:raise ValueError('Pinion screw rim too thin for full-size horn hardware.')
  with tempfile.TemporaryDirectory() as folder:
   folder=Path(folder)
   for n in ['gripper.scad','large_source.scad','trace_px.scad']:shutil.copy(HERE/n,folder/n)
   params.write_scad(folder/'params.scad',v)
   def one(k):
    p=subprocess.run([SCAD,'--backend','manifold','--export-format','binstl','-D',f'part="viewer_{k}"','-o',str(out/(k+'.stl')),str(folder/'gripper.scad')],capture_output=True,text=True,timeout=60)
    if p.returncode or 'WARNING' in p.stderr:raise ValueError(p.stderr)
   with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(one,PARTS+['motor']))
  return dict(ok=True,pivot=v['pivot_spacing']/2*v['scale_factor'],seconds=time.time()-started,retraced=False,values=overrides,fit=fit)
 except Exception as e:return dict(ok=False,error=str(e))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--values',default='{}');ap.add_argument('--out',required=True);ap.add_argument('--cache');a=ap.parse_args()
 result=render(json.loads(a.values),a.out,a.cache);(Path(a.out)/'result.json').write_text(json.dumps(result)+'\n');print(json.dumps(result));raise SystemExit(0 if result['ok'] else 1)

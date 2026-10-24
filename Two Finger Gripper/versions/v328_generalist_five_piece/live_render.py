"""Tune compact clearance in an isolated directory, keeping bought parts actual size."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,shutil,subprocess,tempfile,time,sys,os,importlib.util
import params
from export_models import PARTS,REFS,SCAD,normalize_jaw
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
    result=subprocess.run([SCAD,'--backend',('CGAL' if k in ('left','right','base') else 'manifold'),'--export-format','binstl','-D',f'part="viewer_{k}"','-o',str(out.resolve()/f'{k}.stl'),str(work/'gripper.scad')],capture_output=True,text=True)
    if result.returncode or 'WARNING' in result.stderr:raise RuntimeError(result.stderr)
    if k in ('left','right'):normalize_jaw(out.resolve()/f'{k}.stl')
   with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(one,PARTS+['motor','stock_plate']+[k for k in REFS if not k.endswith('_tools') and k!='cable']))
  return dict(ok=True,pivot=v['pivot_spacing']/2*v['scale_factor'],seconds=time.monotonic()-started,retraced=False,values=overrides)
 except Exception as e:return dict(ok=False,error=str(e))
if __name__=='__main__':
 # Gallery server uses system Python; STL normalization owns this explicit CAD runtime.
 if importlib.util.find_spec('trimesh') is None:
  runtime=HERE.parents[2]/'cad/blender/.venv/bin/python'
  os.execv(str(runtime),[str(runtime),__file__,*sys.argv[1:]])
 p=argparse.ArgumentParser();p.add_argument('--values',default='{}');p.add_argument('--out',required=True);p.add_argument('--cache');a=p.parse_args()
 result=render(json.loads(a.values),a.out,a.cache);(Path(a.out)/'result.json').write_text(json.dumps(result)+'\n');print(json.dumps(result));raise SystemExit(0 if result['ok'] else 1)

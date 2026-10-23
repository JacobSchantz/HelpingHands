"""Serve the verified fixed-size Base 18 export through the gallery Tune contract."""
from pathlib import Path
import argparse,json,shutil
import params
from export_models import PARTS
HERE=Path(__file__).resolve().parent
def render(overrides,out,cache=None):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 try:
  v=params.values(overrides)
  # The only inherited slider is locked at 50%; purchased reference hardware stays immutable.
  for k in PARTS+['motor','stock_plate']:shutil.copy2(HERE/f'exports/parts/{k}.stl',out/f'{k}.stl')
  return dict(ok=True,pivot=v['pivot_spacing']/2*v['scale_factor'],seconds=0,retraced=False,values=overrides)
 except Exception as e:return dict(ok=False,error=str(e))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--values',default='{}');p.add_argument('--out',required=True);p.add_argument('--cache');a=p.parse_args()
 result=render(json.loads(a.values),a.out,a.cache);(Path(a.out)/'result.json').write_text(json.dumps(result)+'\n');print(json.dumps(result));raise SystemExit(0 if result['ok'] else 1)

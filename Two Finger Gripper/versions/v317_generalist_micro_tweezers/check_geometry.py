"""Check actual solids over the entire commanded stroke."""
from pathlib import Path
import tempfile,json
from concurrent.futures import ThreadPoolExecutor
import params,export_models,genus
from geometry import envelope
HERE=Path(__file__).resolve().parent
def main():
    p=params.values();half=p['servo_w']/2
    with tempfile.TemporaryDirectory() as tmp:
        def check(a):
            result={'angle':a}
            for part in ('left','right','coupler','collision_jaws','collision_frame','collision_hardware'):
                out=Path(tmp)/(part+str(a)+'.stl')
                export_models.export(part,a,out)
                if part.startswith('collision'):
                    volume=genus.inspect(out)['volume_mm3'] if out.exists() else 0
                    assert volume<.0001,(a,part,volume)
                    result[part]=volume
                else:
                    bounds=genus.inspect(out)['bounds']
                    assert bounds[0][0]>=-half-.001 and bounds[1][0]<=half+.001,(a,part,bounds)
                    result[part+'_x']=[bounds[0][0],bounds[1][0]]
            return result
        with ThreadPoolExecutor(max_workers=3) as pool:
            swept=list(pool.map(check,[i*.5 for i in range(int(p['max_angle']*2)+1)]))
    for part in ('base','cap','motor','horn_heads','case_heads','cap_heads','cable'):
        b=genus.inspect(HERE/'exports/parts'/f'{part}.stl')['bounds']
        assert b[0][0]>=-half-.001 and b[1][0]<=half+.001,(part,b)
    continuous=envelope(HERE/'exports/parts',p)
    assert continuous['passed'],continuous
    assert not envelope(HERE/'exports/parts',dict(p,max_angle=40))['passed'], 'Over-opening regression must fail'
    report={'continuous_envelope':continuous,'servo_width_mm':p['servo_w'],'sweep':swept,'passed':True,
            'limitations':'CAD clearance only; no strength, print-tolerance or hardware fit validation.'}
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: fixed parts and',len(swept),'poses fit within servo width; no moving interference.')
if __name__=='__main__':main()

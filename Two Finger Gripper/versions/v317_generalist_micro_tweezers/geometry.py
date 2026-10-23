"""Exact continuous X envelope of binary-STL vertices rotating around Y."""
import math,struct
from pathlib import Path

def vertices(path):
    b=Path(path).read_bytes();n=struct.unpack_from('<I',b,80)[0]
    return [struct.unpack_from('<3f',b,84+i*50+j) for i in range(n) for j in (12,24,36)]

def swept_x(points,pivot,lo,hi):
    low,high=math.inf,-math.inf
    lo,hi=sorted((math.radians(lo),math.radians(hi)))
    for x,_,z in points:
        dx=x-pivot;ts=[lo,hi];t=math.atan2(z,dx)
        for k in range(-2,3):
            a=t+k*math.pi
            if lo<=a<=hi:ts.append(a)
        xs=[pivot+dx*math.cos(a)+z*math.sin(a) for a in ts]
        low=min(low,*xs);high=max(high,*xs)
    return [low,high]

def envelope(folder,vals):
    limits={};spacing=vals['gear_m']*vals['gear_teeth']
    for path in sorted(Path(folder).glob('*.stl')):
        k=path.stem;points=vertices(path)
        if k in ('left','coupler','horn_heads'):
            limits[k]=swept_x(points,0,-vals['max_angle'],0)
        elif k=='right':limits[k]=swept_x(points,spacing,0,vals['max_angle'])
        else:limits[k]=[min(p[0] for p in points),max(p[0] for p in points)]
    passed=all(lo>=-vals['servo_w']/2-1e-5 and hi<=vals['servo_w']/2+1e-5 for lo,hi in limits.values())
    return dict(passed=passed,method='Analytic extrema of every STL vertex over continuous rotation; includes modeled screw heads and cable keep-out.',stroke_deg=[0,vals['max_angle']],per_part_x_mm=limits,width_mm=max(x[1] for x in limits.values())-min(x[0] for x in limits.values()))

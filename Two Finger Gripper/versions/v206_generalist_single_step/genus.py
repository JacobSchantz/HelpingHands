#!/usr/bin/env python3
"""Count the through-holes of a watertight STL from its Euler characteristic (genus = holes).
The right finger should have exactly the designed holes: honeycomb + dot + slots (2.5: no pocket, so BREACHED 0; 2.3-2.4: plus one per honeycomb hole the
handle pocket opens into the side of (BREACHED: a hole cut into from the side gains a second loop). The strap slide has its two strap slots. A ridge breaking into a slot, or a pinhole, shows up as an
extra hole."""
import re, struct, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BREACHED=0   # 2.5: no pocket (2.4 opened 4 honeycomb holes from the side)
def genus(stl):
    raw=Path(stl).read_bytes();n=struct.unpack_from('<I',raw,80)[0];V={};E=set()
    for i in range(n):
        q=struct.unpack_from('<12f',raw,84+i*50);ix=[V.setdefault(tuple(q[j:j+3]),len(V)) for j in (3,6,9)]
        for a,b in ((0,1),(1,2),(2,0)):E.add(tuple(sorted((ix[a],ix[b]))))
    return (2-(len(V)-len(E)+n))//2
if __name__=='__main__':
    t=(HERE/'trace_px.scad').read_text()
    count=lambda name:len(re.findall(r'\[[-\d. ]+,[-\d., ]+\]',re.search(name+r'=\[(.*?)\];',t,re.S).group(1)))
    want=count('holes_px')+1+count('slots_px')+BREACHED;got=genus(HERE/'exports/print/right.stl')
    print(f'{"PASS" if got==want else "FAIL"}: right finger has {got} through-holes, designed {want} ({BREACHED} opened by the pocket)')
    slide=genus(HERE/'exports/print/right_slide.stl')
    print(f'{"PASS" if slide==2 else "FAIL"}: right handle has {slide} through-holes, designed 2')
    sys.exit(got!=want or slide!=2)

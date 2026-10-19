#!/usr/bin/env python3
"""Count the through-holes of a watertight STL from its Euler characteristic (genus = holes).
The right finger should have exactly the designed holes: honeycomb + dot + slots. A ridge
breaking into a slot, or a pinhole, shows up as an extra hole."""
import re, struct, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def genus(stl):
    raw=Path(stl).read_bytes();n=struct.unpack_from('<I',raw,80)[0];V={};E=set()
    for i in range(n):
        q=struct.unpack_from('<12f',raw,84+i*50);ix=[V.setdefault(tuple(q[j:j+3]),len(V)) for j in (3,6,9)]
        for a,b in ((0,1),(1,2),(2,0)):E.add(tuple(sorted((ix[a],ix[b]))))
    return (2-(len(V)-len(E)+n))//2
if __name__=='__main__':
    with tempfile.TemporaryDirectory() as tmp:   # Gen 12 drops the slots the tine is too slender for, so ask the .scad
        w=Path(tmp)/'w.scad';o=Path(tmp)/'o.echo';w.write_text(f'include <{HERE/"gripper.scad"}>\necho(want=len(holes_px)+1+len(slots_kept));\n')
        subprocess.run(['/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD','-D','part="none"','-o',str(o),str(w)],capture_output=True)
        want=int(re.search(r'want = (\d+)',o.read_text()).group(1))
    got=genus(HERE/'exports/print/right.stl')
    print(f'{"PASS" if got==want else "FAIL"}: right finger has {got} through-holes, designed {want}');sys.exit(got!=want)

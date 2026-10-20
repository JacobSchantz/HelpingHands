#!/usr/bin/env python3
"""Count the through-holes of a watertight STL from its Euler characteristic (genus = holes).
The right finger should have exactly the designed holes: honeycomb + dot + slots (2.5: no pocket, so BREACHED 0; 2.3-2.4: plus one per honeycomb hole the
handle pocket opens into the side of (BREACHED: a hole cut into from the side gains a second loop). The handle has its strap tunnel (3.3; 2.5-3.2: two strap slots). A ridge breaking into a slot, or a pinhole, shows up as an
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
    # Base 8: each handle-gear: its strap_slots strap-loop slots + the bore for its post. Base 7: each side gear is one print with its handle: 2 holes, the strap tunnel and the bore for its post (the finger's
    # pocket sits over the web). Pinion: its 3 motor-flange bolt holes. Base: the motor boss hole, 3 motor screws, 2 dowels
    # (Base 4's 2 bushings are posts now). The motor model has only blind holes.
    bad=False
    slots=int(re.search(r'^strap_slots=(\d+);',(HERE/'params.scad').read_text(),re.M).group(1))
    # Base 9: base + 3 pillar screws (9); top plate: the pinion access hole (its 3 pillar pilots are blind)
    # Base 10: bracket: 4 foot pilots + 4 leg holes + 2 tie slots; tool plate: centre hole + 4 tool screws + 3 radial; the Aero plate the
    # same (its cable channel is a groove in the hand face, not a hole); hub: bore + 6 J6 screws + 3 reliefs + 3 radial pilots (into the reliefs)
    # Base 11, STS3215 (motor_sts 1): pinion 4 horn screws (the centre screw's recess is blind); base 4 M2 + 3 pillar screws, its horn hole
    # runs into the hump's window, which runs out of the base's edge (a notch, not a hole); no mount parts. The servo model: its horn's
    # 4 screw holes go through the horn (air under it); the case holes are blind
    sts=re.search(r'^motor_sts=(\d+);',(HERE/'params.scad').read_text(),re.M).group(1)=='1'
    want_parts=(('right_gear',slots+1),('left_gear',slots+1),('pinion',4),('base',7),('top_plate',1),('motor',4)) if sts else \
               (('right_gear',slots+1),('left_gear',slots+1),('pinion',3),('base',9),('top_plate',1),('bracket',10),('tool_plate',8),('aero_plate',8),('hub',13),('motor',0))
    for part,n in want_parts:
        g=genus(HERE/f'exports/print/{part}.stl');bad|=g!=n
        print(f'{"PASS" if g==n else "FAIL"}: {part} has {g} through-holes, designed {n}')
    sys.exit(got!=want or bad)

"""Export Base 26 and Gripper 30, plus actual-size hardware probes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess
import params
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PARTS=['left_blade','right_blade','left_gear','right_gear','right_upper','pinion','base','ear_spacers','capture_ring']
PRINTS=['left_blade','right_blade','left_gear','right_gear','right_upper','pinion','base','ear_spacers','capture_ring']
REFS=['plate_washers','spacer_tools','spacer_screws','plate_screws','case_screws','pivot_screws','pivot_washers','pivot_nuts','center_screw','cable','plate_tools','case_tools','pivot_tools','nut_tools','center_tools','case_straight_tools']
def scad(out,part):
 out.parent.mkdir(parents=True,exist_ok=True)
 p=subprocess.run([SCAD,'--backend','manifold','--export-format','binstl','-D',f'part="{part}"','-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
 if p.returncode or 'WARNING' in p.stderr:raise RuntimeError(p.stderr)
def main():
 params.write_scad()
 jobs=[(HERE/f'exports/parts/{k}.stl',f'viewer_{k}') for k in PARTS]+[(HERE/f'exports/print/{k}.stl',f'print_{k}') for k in PRINTS]+[(HERE/f'exports/parts/{k}.stl',f'viewer_{k}') for k in PRINTS if k not in PARTS]
 jobs += [(HERE/f'exports/parts/{k}.stl',f'viewer_{k}') for k in ['left','right']]
 jobs += [(HERE/f'exports/reference/{k}.stl',f'viewer_{k}') for k in REFS]
 jobs += [(HERE/'exports/assembly.stl','assembly')]+[(HERE/f'exports/parts/{k}.stl',f'viewer_{k}') for k in ['motor','stock_plate']]
 with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda j:scad(*j),jobs))
 entries=[]
 names={'left':'Left assembled jaw','right':'Right assembled jaw','left_blade':'Left finger solid blade','right_blade':'Right finger solid blade','left_gear':'Left lower gear','right_gear':'Right lower gear','right_upper':'Right upper gear','ear_spacers':'Motor spacers (4)','spacer_screws':'Spacer screws (4)','capture_ring':'Center screw capture ring','plate_washers':'Plate screws washers (2)','pinion':'Pinion','base':'Base','motor':'Motor HLS3606M','stock_plate':'Stock aluminum spline plate','plate_screws':'Plate screws (2)','case_screws':'Case screws (4)','pivot_screws':'Pivot screws (2)','pivot_washers':'Pivot washers (2)','pivot_nuts':'Pivot nuts (2)','center_screw':'Center screw'}
 for i,k in enumerate(PRINTS+['motor','stock_plate','plate_washers','spacer_screws','plate_screws','case_screws','pivot_screws','pivot_washers','pivot_nuts','center_screw']):
  hardware=k in REFS
  entries.append(dict(path=f'exports/{"reference" if hardware else "parts"}/{k}.stl',name=names[k]+' — Base 26, Gripper 30',color='#efb83b' if k in ['left','right'] else '#718096' if hardware or k in ['motor','stock_plate'] else '#26272b',explode=[-20 if k=='left' else 20 if k=='right' else 0, -35 if k in ['pivot_screws','pivot_washers'] else 35 if k in ['base','pivot_nuts'] else 65 if k=='motor' else 15, -25 if k in ['pinion','stock_plate','center_screw','plate_screws'] else 0]))
 original=dict(no_handles=True,parts=entries,finger_lineage=dict(builds_on='Gripper 29',gist='Solid original-outline blades with keyed separate flat gear layers for support-free FDM'),preview='previews/comparison.png')
 (HERE/'viewer_parts.json').write_text(json.dumps(original,indent=2)+'\n')
 print('Exported twelve prints: two blades, three gears, pinion, base and four spacers.')
if __name__=='__main__':main()

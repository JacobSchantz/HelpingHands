from pathlib import Path
import json,subprocess,sys
import numpy as np,trimesh
folder=Path(__file__).resolve().parent;root=folder.parents[2];out=folder/'slicing';out.mkdir(exist_ok=True)
ini='''# Explicit generic FDM screening profile; saved Bambu profile is X1 Carbon / 0.4 / eSUN PLA+.
# PrusaSlicer produces portable toolpath evidence; not a ready-to-run Bambu machine job.
layer_height = 0.1
first_layer_height = 0.2
nozzle_diameter = 0.4
filament_diameter = 1.75
filament_type = PLA
bed_shape = 0x0,256x0,256x256,0x256
max_print_height = 256
printer_technology = FFF
gcode_flavor = marlin
use_relative_e_distances = 1
layer_gcode = G92 E0
temperature = 210
first_layer_temperature = 210
bed_temperature = 60
first_layer_bed_temperature = 60
perimeters = 4
top_solid_layers = 5
bottom_solid_layers = 5
fill_density = 100%
fill_pattern = rectilinear
perimeter_generator = arachne
extrusion_width = 0.45
first_layer_extrusion_width = 0.45
bridge_flow_ratio = 0.9
support_material = 0
support_material_auto = 0
support_material_enforce_layers = 0
raft_layers = 0
brim_width = 0
skirts = 0
fan_always_on = 1
min_fan_speed = 100
max_fan_speed = 100
bridge_fan_speed = 100
disable_fan_first_layers = 1
perimeter_speed = 30
external_perimeter_speed = 20
infill_speed = 40
solid_infill_speed = 30
bridge_speed = 20
first_layer_speed = 20
start_gcode = G28\\nG92 E0
end_gcode = M104 S0\\nM140 S0
'''
(out/'fdm_screen.ini').write_text(ini)
parts=[]
for f in sorted((folder/'exports/print').glob('*.stl')):
 m=trimesh.load_mesh(f)
 for i,c in enumerate(m.split()):parts.append((f.stem+(str(i+1) if f.stem=='ear_spacers' else ''),c))
# Stable explicit arrangement: eleven independent objects, no auto orientation.
placed=[];x=y=12;rowh=0
for name,m in parts:
 sx,sy,sz=m.extents
 if x+sx>235:x=12;y+=rowh+8;rowh=0
 m.apply_translation([x-m.bounds[0,0],y-m.bounds[0,1],-m.bounds[0,2]])
 placed.append(m);x+=sx+8;rowh=max(rowh,sy)
trimesh.util.concatenate(placed).export(folder/'exports/print_plate.stl')
(folder/'print_orientations.json').write_text(json.dumps([dict(part=n,plate_bounds_mm=m.bounds.tolist(),orientation='Supplied print STL on its flat Z=0 face; do not auto-orient') for (n,_),m in zip(parts,placed)],indent=2)+'\n')
cli='/Applications/Original Prusa Drivers/PrusaSlicer.app/Contents/MacOS/PrusaSlicer'
# individual parts prove each actual export slices; combined spacer file contains four independent upright objects
for f in sorted((folder/'exports/print').glob('*.stl')):
 cmd=[cli,'--load',str(out/'fdm_screen.ini'),'--export-gcode','--output',str(out/(f.stem+'.gcode')),str(f)]
 r=subprocess.run(cmd,capture_output=True,text=True);(out/(f.stem+'.log')).write_text(r.stdout+r.stderr)
 print(f.stem,r.returncode,flush=True)
 if r.returncode or not (out/(f.stem+'.gcode')).exists():print(r.stdout,r.stderr);sys.exit(r.returncode or 1)
r=subprocess.run([cli,'--load',str(out/'fdm_screen.ini'),'--export-3mf','--dont-arrange','--output',str(folder/'exports/print_plate.3mf'),str(folder/'exports/print_plate.stl')],capture_output=True,text=True)
(out/'plate.log').write_text(r.stdout+r.stderr);print('3mf',r.returncode,r.stderr)

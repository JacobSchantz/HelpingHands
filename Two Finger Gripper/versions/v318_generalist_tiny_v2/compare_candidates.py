"""Bounded design search; allowances are explicit, no globally-smallest claim."""
from pathlib import Path
import json
import params
from hardware_fit import hardware_fit
HERE=Path(__file__).resolve().parent
SOURCE_PLAN_WEB=.8094511785704572
SOURCE_SWEPT_HALF=70.0323020725481

def candidate(scale,side,pinion,v=None):
 v=dict(v or params.values(),scale_factor=scale,gear_teeth=side,pinion_teeth=pinion)
 fit=hardware_fit(v);web=SOURCE_PLAN_WEB*scale
 pivot=v['pivot_spacing']/2*scale;rp=pivot*pinion/side
 base_r=fit['gear_module_mm']*(pinion/2+1)+v['min_base_rim']
 lo=min(-SOURCE_SWEPT_HALF*scale,-v['cap_pillar_x']-v['pillar_d']/2-.5,pivot-base_r,pivot-(v['sts_len']-v['sts_near']))
 hi=max(SOURCE_SWEPT_HALF*scale,v['cap_pillar_x']+v['pillar_d']/2+.5,pivot+base_r,pivot+v['sts_near'])
 return dict(scale=scale,side_teeth=side,pinion_teeth=pinion,passed=fit['passed'] and web>=v['min_lattice_web'],minimum_web_mm=web,gear_module_mm=fit['gear_module_mm'],pinion_rim_mm=fit['rim_mm'],pinion_pitch_radius_mm=rp,estimated_continuous_width_mm=hi-lo,failures=(["stock horn countersink rim"] if fit['rim_mm']<v['min_screw_rim'] else [])+(["gear module"] if fit['gear_module_mm']<v['min_gear_module'] else [])+(["unchanged lattice ligament"] if web<v['min_lattice_web'] else []))

def search(v=None):
 v=v or params.values();passing=[]
 for percent in range(20,101):
  for side in range(18,41):
   for pinion in range(18,41):
    c=candidate(percent/100,side,pinion,v)
    if c['passed']:passing.append(c)
 return min(passing,key=lambda c:(c['scale'],c['estimated_continuous_width_mm'],c['pinion_pitch_radius_mm']))
if __name__=='__main__':
 report=dict(scope='Scale 20–100% in 1% increments; integer 18–40 teeth per gear; original lattice/outline retained. Rank by scale, estimated width, then pinion radius. Analytical screening; only chosen CAD receives full mesh/motion validation.',selected=search(),alternatives=[candidate(.9,34,16),candidate(.5,34,16),candidate(.6,30,24),candidate(.5,30,24),candidate(.49,28,24),candidate(.4,22,24)],allowances=dict(min_lattice_web_mm=.4,min_gear_module_mm=1,min_pinion_screw_rim_mm=1),limitations='Fine resin prototype allowance, not FDM or strength-qualified. No claim of global optimum across other finger reinforcements, lattice edits, manufacturing processes, horns or architectures.')
 (HERE/'candidate_comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

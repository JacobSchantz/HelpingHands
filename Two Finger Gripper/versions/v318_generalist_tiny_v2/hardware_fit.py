"""Explicit design allowances, not a claim of globally minimum or strength-qualified size."""
def hardware_fit(v):
 s=v['scale_factor'];module=v['pivot_spacing']*s/v['gear_teeth'];root=module*(v['pinion_teeth']/2-1.25)
 rim=root-v['sts_horn_pcd']/2-v['gear_bolt_head_d']/2
 return dict(passed=rim>=v['min_screw_rim'] and module>=v['min_gear_module'],scale=s,gear_module_mm=module,pinion_root_radius_mm=root,rim_mm=rim,required_rim_mm=v['min_screw_rim'],ratio=v['gear_teeth']/v['pinion_teeth'])

"""Miniature interface and complete width regressions (voice-dd73161d)."""
import importlib.util,json,math,subprocess,unittest
from pathlib import Path
import publish_designs
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'Two Finger Gripper/versions/v317_generalist_micro_tweezers'
spec=importlib.util.spec_from_file_location('micro_geometry',FOLDER/'geometry.py')
geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)

class MicroTweezerTests(unittest.TestCase):
    def test_analytic_envelope_checks_interior_extrema(self):
        lo,hi=geometry.swept_x([(1,0,1)],0,0,90)
        self.assertAlmostEqual(lo,1)
        self.assertAlmostEqual(hi,math.sqrt(2))

    def test_complete_stroke_and_excessive_opening(self):
        vals={q['name']:q['value'] for g in json.loads((FOLDER/'params.json').read_text())['groups'] for q in g['params']}
        self.assertTrue(geometry.envelope(FOLDER/'exports/parts',vals)['passed'])
        self.assertFalse(geometry.envelope(FOLDER/'exports/parts',dict(vals,max_angle=40))['passed'])

    def test_catalog_excludes_full_size_handles_and_flags_old_grippers(self):
        rows=publish_designs.discover(ROOT)
        micro=next(r for r in rows if r['id']=='two-finger-gripper-v317-generalist-micro-tweezers')
        self.assertEqual(micro['name'],'Base 16');self.assertEqual(micro['fingers'],'23')
        self.assertEqual(micro['builds_on'],'Base 15');self.assertTrue(publish_designs.public_fields(micro)['no_handles'])
        catalog={'designs':[dict(publish_designs.public_fields(r),models=r['existing']) for r in rows if r['existing']]}
        script='''import {MIX,buildMix,initialPicks} from %s;
const picks=initialPicks(new URLSearchParams('gripper=23&base=16&handles=7&arm=none&mount=none'));
let mix=buildMix(JSON.parse(process.argv[1]),picks,MIX);
const handle=mix.rows.find(r=>r.key==='handles');
if(handle.chosen || handle.sitsOut!=='No handle interface')throw Error('full-size handles drawn');
picks[MIX.id].gripper='22';mix=buildMix(JSON.parse(process.argv[1]),picks,MIX,'gripper');
if(!mix.rows.some(r=>r.notes.some(n=>n.text.includes('built on Gripper 23'))))throw Error('incompatible fingers not flagged');
''' % json.dumps((ROOT/'cad/mobile_gallery/model.js').as_uri())
        subprocess.run(['node','--input-type=module','-e',script,json.dumps(catalog,default=str)],check=True,capture_output=True,text=True)

if __name__=='__main__':unittest.main()

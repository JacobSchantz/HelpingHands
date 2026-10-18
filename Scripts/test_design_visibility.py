import json
from pathlib import Path
import tempfile
import unittest

import design_visibility as visibility

CATALOG = [
    {'id': 'demo-gripper-gen-00', 'project': 'Generalist Gripper', 'name': 'Gen 1'},
    {'id': 'demo-gripper-gen-01', 'project': 'Generalist Gripper', 'name': 'Gen 2'},
    {'id': 'two-finger-gripper-v006-dorsal-drive', 'project': 'Generalist Gripper', 'name': 'Gen 6'},
    {'id': 'glove-hand-gen-01', 'project': 'Glove Hand', 'name': 'Glove Hand gen 01 · fit-test surround'},
    {'id': 'orca-cc-by-prototype-v002-clean-index', 'project': 'Orca Hand', 'name': 'v002 clean index'},
]


class ResolveTests(unittest.TestCase):
    def ids(self, query):
        return [d['id'] for d in visibility.resolve(query, CATALOG)]

    def test_spoken_generations(self):
        self.assertEqual(self.ids('gripper gen 1 and 2'), ['demo-gripper-gen-00', 'demo-gripper-gen-01'])
        self.assertEqual(self.ids('gripper generation two'), ['demo-gripper-gen-01'])
        self.assertEqual(self.ids('gripper gen1'), ['demo-gripper-gen-00'])
        self.assertEqual(self.ids('glove hand gen 1'), ['glove-hand-gen-01'])
        self.assertEqual(self.ids('orca v2'), ['orca-cc-by-prototype-v002-clean-index'])

    def test_ambiguous_or_missing_is_refused(self):
        for query in ('gripper', 'gen 1', 'gripper gen 9'):
            with self.assertRaises(LookupError):
                visibility.resolve(query, CATALOG)

    def test_hide_then_show_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            gallery = Path(tmp)
            (gallery / 'catalog.json').write_text(json.dumps({'designs': CATALOG}))
            visibility.main(['hide', 'gripper', 'gen', '1', '2', '--gallery', tmp])
            self.assertEqual(visibility.load(gallery)[1], ['demo-gripper-gen-00', 'demo-gripper-gen-01'])
            visibility.main(['show', 'gripper gen 1', '--gallery', tmp])
            self.assertEqual(visibility.load(gallery)[1], ['demo-gripper-gen-01'])


if __name__ == '__main__':
    unittest.main()

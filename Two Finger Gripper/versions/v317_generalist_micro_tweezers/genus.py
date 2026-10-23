"""Closed manifold, volume and bounds checks on exported binary STL."""
from pathlib import Path
import struct,json
HERE=Path(__file__).resolve().parent
def mesh(path):
    raw=Path(path).read_bytes();n=struct.unpack_from('<I',raw,80)[0];faces=[]
    for i in range(n):
        v=struct.unpack_from('<12f',raw,84+50*i)
        faces.append([tuple(round(c,5) for c in v[j:j+3]) for j in (3,6,9)])
    return faces
def inspect(path):
    faces=mesh(path);edges={};volume=0
    for a,b,c in faces:
        for u,v in ((a,b),(b,c),(c,a)):
            e=tuple(sorted((u,v)));edges[e]=edges.get(e,0)+1
        volume+=sum(a[i]*(b[(i+1)%3]*c[(i+2)%3]-b[(i+2)%3]*c[(i+1)%3]) for i in range(3))/6
    vs=[v for face in faces for v in face]
    return dict(triangles=len(faces),watertight=all(n==2 for n in edges.values()),volume_mm3=round(abs(volume),4),
        bounds=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]])
if __name__=='__main__':
    report={p.stem:inspect(p) for p in (HERE/'exports/parts').glob('*.stl')}
    (HERE/'mesh_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    assert all(r['watertight'] and r['volume_mm3']>0 for r in report.values()),report
    for path in (HERE/'exports/print').glob('*.stl'):
        r=inspect(path)
        assert r['watertight'] and r['volume_mm3']>0 and abs(r['bounds'][0][2])<.001,(path,r)
    print('All',len(report),'parts: closed manifold, positive volume')

"""Ray tests against CAD, not real camera calibration or hand-fit validation."""
import tempfile, subprocess
from validate import *
def hits(t,origin,target):
 d=target-origin; length=np.linalg.norm(d);d/=length
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0]
 h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h)
 valid=abs(det)>1e-8;inv=np.zeros(len(t));inv[valid]=1/det[valid]
 s=origin-t[:,0];u=inv*np.einsum('ij,ij->i',s,h)
 q=np.cross(s,e1);v=inv*np.einsum('j,ij->i',d,q);dist=inv*np.einsum('ij,ij->i',e2,q)
 mask=valid&(u>=0)&(v>=0)&(u+v<=1)&(dist>0.1)&(dist<length-0.2)
 return dist[mask]
def main():
 origin=np.array([0.,65.,20.]); aim=np.array([0.,0.,60.])-origin;aim/=np.linalg.norm(aim)
 count=0;maximum=0
 for variant in ['A','B']:
  for angle in [0,14,29.5]:
   for mode in ['pair','in_hand','on_arm']:
    with tempfile.TemporaryDirectory() as tmp:
     out=Path(tmp)/'scene.stl'
     subprocess.run([SCAD,'--export-format','binstl','-o',str(out),'-D',f'part="{mode}"','-D',f'angle={angle}','-D',f'variant="{variant}"',str(SOURCE)],capture_output=True,check=True)
     t=triangles(out.read_bytes())
    for side in [-1,1]:
     a=np.radians(angle);tip=71.5 if variant=='A' else 83.5
     x=12+(0.4-12)*np.cos(a)+tip*np.sin(a)
     z=-(0.4-12)*np.sin(a)+tip*np.cos(a)
     target=np.array([side*x,0,z]); ray=target-origin
     off=np.degrees(np.arccos(np.dot(ray/np.linalg.norm(ray),aim)))
     assert not len(hits(t,origin,target)), (variant,angle,mode,side,'tip hidden')
     assert off<35, (variant,angle,mode,side,'outside assumed 70-degree field')
     count+=1; maximum=max(maximum,off)
 print(f'{count} tip rays clear (bare, schematic hand/straps, and arm); maximum off-axis {maximum:.2f} degrees. Lens field is an assumption.')

if __name__=='__main__': main()

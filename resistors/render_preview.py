"""Side-view (XZ) flat preview: parts painted body->leads->bands."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import gen_resistors as g
def draw(ax,m,e,short,title):
    a=g.build(m,e,short)
    order=sorted(a.children,key=lambda c:(0 if 'lead' in c.name else 1 if c.name=='body' else 2))
    for ch in order:
        sh=ch.obj.val().moved(ch.loc); v,t=sh.tessellate(0.02)
        ax.add_collection(PolyCollection([[(v[i].x,v[i].z) for i in tri] for tri in t],facecolor=ch.color.toTuple()[:3],edgecolor='none'))
    ax.axhline(0,color='g',lw=0.8); ax.plot(0,0,'r+',ms=10)
    ax.set_xlim(-6,6);ax.set_ylim(-2.5,3);ax.set_aspect('equal');ax.set_title(title+"  (green = board top, + = origin)")
for fn,items in [("10K_std_vs_short.png",[(10,3,False,"10K std"),(10,3,True,"10K Short")]),
                 ("1R_vs_10M.png",[(10,-1,False,"1R std"),(10,6,False,"10M std")])]:
    f,axs=plt.subplots(2,1,figsize=(8,7))
    for ax,it in zip(axs,items): draw(ax,*it)
    f.savefig("previews/"+fn,dpi=110,bbox_inches='tight')

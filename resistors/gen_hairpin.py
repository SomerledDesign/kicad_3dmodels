#!/usr/bin/env python3
"""Hairpin (vertical) axial resistors, built from gen_resistors body/bands.
(c) Kevin Murphy / Somerled.Design - CERN-OHL-S-2.0
Pin 1 at origin under the body, pin 2 at +X pitch; top lead is a true semicircle."""
import sys, os, cadquery as cq
from multiprocessing import Pool
import gen_resistors as g
GAP=0.5  # body bottom above board
def build(m,e,pitch):
    b,h,c=g.body(False)
    rot=lambda w: w.rotate((0,0,0),(0,1,0),-90).translate((0,0,GAP+h))
    a=cq.Assembly(name="resistor")
    a.add(rot(b),name="body",color=cq.Color(*g.BODY_C))
    asm=g.build(m,e,False)
    for ch in asm.children:
        if ch.name.startswith("band"):
            a.add(rot(ch.obj.translate((0,0,-g.AXIS_Z))),name=ch.name,color=ch.color)
    top=GAP+2*h; zt=top+0.8; rr=pitch/2
    p1=cq.Workplane("XZ").moveTo(0,-g.DROP).lineTo(0,zt).threePointArc((rr,zt+rr),(pitch,zt)).lineTo(pitch,-g.DROP)
    lead=cq.Workplane("XY").workplane(offset=-g.DROP).circle(g.LEAD_D/2).sweep(p1,transition="round")
    a.add(lead,name="lead",color=cq.Color(*g.LEAD_C))
    return a
def job(arg):
    m,e,p,out=arg
    fn=os.path.join(out,f"Res Axial Hairpin P{int(round(p*100))} 0_25W-{g.name(m,e)}.step")
    build(m,e,p).save(fn,"STEP"); g.fixhdr(fn); return fn
if __name__=="__main__":
    out=sys.argv[1] if len(sys.argv)>1 else "hairpin"; os.makedirs(out,exist_ok=True)
    jobs=[(m,e,p,out) for (m,e) in g.values() for p in (2.54,5.08)]
    with Pool() as pl: print(len(pl.map(job,jobs)),"files")

#!/usr/bin/env python3
"""Parametric axial THT resistor generator (original work, CadQuery).
(c) Kevin Murphy / Somerled.Design - CERN-OHL-S-2.0
Usage: python gen_resistors.py [outdir]
"""
import sys, os, re, math
import cadquery as cq
from multiprocessing import Pool

PITCH   = 10.16   # lead pitch (mm), pins at x = +/-PITCH/2, origin mid-way
LEAD_D  = 0.60    # lead diameter
AXIS_Z  = 1.213   # body axis height above board (body sits 0.013 above board)
DROP    = 2.00    # lead length below board plane (z = -DROP)
BEND_R  = 0.60    # lead bend centre-line radius
BODY_D  = 2.40    # end-cap diameter
MID_D   = 1.90    # waist diameter between end caps
CAP_L   = {False: 2.0, True: 1.7}   # end-cap length
BODY_L  = {False: 8.3, True: 6.6}   # std / Short overall body length
BAND_W  = 0.45
COL = {0:(0,0,0),1:(0.45,0.25,0.08),2:(0.85,0.0,0.0),3:(1.0,0.45,0.0),4:(1.0,0.85,0.0),
       5:(0.0,0.6,0.0),6:(0.0,0.2,0.9),7:(0.55,0.0,0.75),8:(0.5,0.5,0.5),9:(1,1,1),
       -1:(0.83,0.69,0.22)}  # -1 = gold
BODY_C = (0.85,0.74,0.55); LEAD_C=(0.78,0.79,0.80)
E24=[10,11,12,13,15,16,18,20,22,24,27,30,33,36,39,43,47,51,56,62,68,75,82,91]

def values():
    v=[(m,e) for e in range(-1,6) for m in E24]   # value = m*10^e ohm, 1R..9M1
    return v+[(10,6),(0,0)]  # + 0R jumper
def name(m,e):
    if m==0: return "0R"
    ohm=m*10**e/1.0 if e>=0 else m/10
    for div,s in ((1e6,'M'),(1e3,'K'),(1,'R')):
        if ohm>=div:
            x=ohm/div; i=int(x+1e-9); f=round((x-i)*10)
            return f"{i}{s}{f}" if f else f"{i}{s}"
def bands(m,e):   # digit1, digit2, multiplier exponent (-1 -> gold), tolerance gold
    return [m//10, m%10, e, -1]

def body(short):
    L=BODY_L[short]; c=CAP_L[short]; R=BODY_D/2; r=MID_D/2; h=L/2
    # half profile: flat ends, cap, short taper to waist; then generous fillets everywhere
    pts=[(-h,0),(-h,R),(-h+c-0.45,R),(-h+c,r),(h-c,r),(h-c+0.45,R),(h,R),(h,0)]
    w=cq.Workplane("XZ").polyline(pts).close().revolve(360,(0,0,0),(1,0,0))
    for rad in (0.40,0.30,0.20):
        try: return w.edges().fillet(rad), h, c
        except Exception: pass
    return w, h, c
def ring(x0,w,rad):
    return cq.Workplane("YZ").workplane(offset=x0).circle(rad).extrude(w)
def lead(sign, x0=1.5):
    # each lead built on its own (no mirror), starting inside the body away from centre
    xe=PITCH/2
    path=(cq.Workplane("XZ").moveTo(x0,AXIS_Z).lineTo(xe-BEND_R,AXIS_Z)
          .radiusArc((xe,AXIS_Z-BEND_R),BEND_R).lineTo(xe,-DROP))
    s=cq.Workplane("YZ").workplane(offset=x0).center(0,AXIS_Z).circle(LEAD_D/2).sweep(path)
    if sign<0: s=s.rotate((0,0,0),(0,0,1),180)
    return s
def build(m,e,short):
    b,h,c=body(short); b=b.translate((0,0,AXIS_Z))
    R=BODY_D/2+0.03; r=MID_D/2+0.03
    bd=bands(m,e)
    gap=0.25 if short else 0.30; gg=0.45 if short else 0.60
    tot=4*BAND_W+2*gap+gg; x=-tot/2; xs=[]
    for i in range(4):
        xs.append((x,r)); x+=BAND_W+(gap if i<2 else gg)
    a=cq.Assembly(name="resistor")
    a.add(b,name="body",color=cq.Color(*BODY_C))
    if m==0:  # 0R jumper: single black band at centre
        a.add(ring(-BAND_W/2,BAND_W,r).translate((0,0,AXIS_Z)),name="band1",color=cq.Color(*COL[0]))
        xs=[]
    for i,(x,rad) in enumerate(xs):
        a.add(ring(x,BAND_W,rad).translate((0,0,AXIS_Z)),name=f"band{i+1}",color=cq.Color(*COL[bd[i]]))
    for s in (1,-1): a.add(lead(s),name=f"lead{'2' if s>0 else '1'}",color=cq.Color(*LEAD_C))
    return a
def fixhdr(fn):
    t=open(fn).read()
    t=re.sub(r"FILE_NAME\s*\((.*?)\);", lambda mm: "FILE_NAME('%s','%s',('Kevin Murphy'),('Somerled.Design'),'CadQuery','gen_resistors.py','');"%(os.path.basename(fn),"2026-10-29T00:00:00"),t,count=1,flags=re.S)
    open(fn,'w').write(t)
def job(arg):
    m,e,short,out=arg
    fn=os.path.join(out,f"Res40-Axial {'Short ' if short else ''}0_25W-{name(m,e)}.step")
    build(m,e,short).save(fn,"STEP"); fixhdr(fn); return fn
if __name__=="__main__":
    out=sys.argv[1] if len(sys.argv)>1 else "."
    os.makedirs(out,exist_ok=True)
    jobs=[(m,e,s,out) for (m,e) in values() for s in (False,True)]
    with Pool() as p: n=len(p.map(job,jobs))
    print(n,"files")

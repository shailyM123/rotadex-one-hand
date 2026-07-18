"""
Rotadex One-Handed Pill Organizer — Precision STL Generator v2
Generates highly detailed STL models + standalone embedded 3D viewer.
"""
import math, os, json

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(OUTPUT_DIR, "stl_models")
os.makedirs(STL_DIR, exist_ok=True)

# ============================================================
# STL Writer
# ============================================================
class STL:
    def __init__(self):
        self.facets = []

    def tri(self, v1, v2, v3):
        u = (v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2])
        w = (v3[0]-v1[0], v3[1]-v1[1], v3[2]-v1[2])
        nx = u[1]*w[2] - u[2]*w[1]
        ny = u[2]*w[0] - u[0]*w[2]
        nz = u[0]*w[1] - u[1]*w[0]
        ln = math.sqrt(nx*nx + ny*ny + nz*nz)
        if ln > 1e-12: nx/=ln; ny/=ln; nz/=ln
        self.facets.append(((nx,ny,nz), v1, v2, v3))

    def quad(self, v1, v2, v3, v4):
        self.tri(v1, v2, v3)
        self.tri(v1, v3, v4)

    def merge(self, other):
        self.facets.extend(other.facets)

    def translate(self, dx, dy, dz):
        s = STL()
        for (n, v1, v2, v3) in self.facets:
            s.facets.append((n,
                (v1[0]+dx, v1[1]+dy, v1[2]+dz),
                (v2[0]+dx, v2[1]+dy, v2[2]+dz),
                (v3[0]+dx, v3[1]+dy, v3[2]+dz)))
        return s

    def rotate_z(self, angle):
        s = STL()
        ca, sa = math.cos(angle), math.sin(angle)
        for (n, v1, v2, v3) in self.facets:
            def rz(v): return (v[0]*ca - v[1]*sa, v[0]*sa + v[1]*ca, v[2])
            def rn(nn): return (nn[0]*ca - nn[1]*sa, nn[0]*sa + nn[1]*ca, nn[2])
            s.facets.append((rn(n), rz(v1), rz(v2), rz(v3)))
        return s

    def write(self, path, name="solid"):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"solid {name}\n")
            for (n, v1, v2, v3) in self.facets:
                f.write(f"  facet normal {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n")
                f.write(f"    outer loop\n")
                for v in (v1, v2, v3):
                    f.write(f"      vertex {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
                f.write(f"    endloop\n  endfacet\n")
            f.write(f"endsolid {name}\n")
        print(f"  [{len(self.facets):>5} tris] {os.path.basename(path)}")


# ============================================================
# Primitives
# ============================================================
def cylinder(r, h, n=48, z0=0):
    s = STL()
    for i in range(n):
        a0 = 2*math.pi*i/n; a1 = 2*math.pi*(i+1)/n
        x0,y0 = r*math.cos(a0), r*math.sin(a0)
        x1,y1 = r*math.cos(a1), r*math.sin(a1)
        s.quad((x0,y0,z0),(x1,y1,z0),(x1,y1,z0+h),(x0,y0,z0+h))
        s.tri((0,0,z0+h),(x0,y0,z0+h),(x1,y1,z0+h))
        s.tri((0,0,z0),(x1,y1,z0),(x0,y0,z0))
    return s

def tube(ro, ri, h, n=48, z0=0):
    s = STL()
    for i in range(n):
        a0 = 2*math.pi*i/n; a1 = 2*math.pi*(i+1)/n
        c0,s0 = math.cos(a0), math.sin(a0)
        c1,s1 = math.cos(a1), math.sin(a1)
        ox0,oy0 = ro*c0, ro*s0; ox1,oy1 = ro*c1, ro*s1
        ix0,iy0 = ri*c0, ri*s0; ix1,iy1 = ri*c1, ri*s1
        z1 = z0+h
        s.quad((ox0,oy0,z0),(ox1,oy1,z0),(ox1,oy1,z1),(ox0,oy0,z1))
        s.quad((ix1,iy1,z0),(ix0,iy0,z0),(ix0,iy0,z1),(ix1,iy1,z1))
        s.quad((ix0,iy0,z1),(ix1,iy1,z1),(ox1,oy1,z1),(ox0,oy0,z1))
        s.quad((ix1,iy1,z0),(ix0,iy0,z0),(ox0,oy0,z0),(ox1,oy1,z0))
    return s

def box(sx, sy, sz, cx=0, cy=0, cz=0):
    s = STL()
    x0,x1 = cx-sx/2, cx+sx/2
    y0,y1 = cy-sy/2, cy+sy/2
    z0,z1 = cz-sz/2, cz+sz/2
    s.quad((x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1))
    s.quad((x1,y1,z0),(x0,y1,z0),(x0,y1,z1),(x1,y1,z1))
    s.quad((x0,y1,z0),(x0,y0,z0),(x0,y0,z1),(x0,y1,z1))
    s.quad((x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1))
    s.quad((x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))
    s.quad((x1,y0,z0),(x0,y0,z0),(x0,y1,z0),(x1,y1,z0))
    return s

def hemisphere(r, seg=40, rings=20):
    s = STL()
    for i in range(rings):
        p0 = math.pi/2*i/rings; p1 = math.pi/2*(i+1)/rings
        for j in range(seg):
            t0 = 2*math.pi*j/seg; t1 = 2*math.pi*(j+1)/seg
            def sp(p,t): return (r*math.cos(p)*math.cos(t), r*math.cos(p)*math.sin(t), r*math.sin(p))
            v00,v10,v11,v01 = sp(p0,t0), sp(p1,t0), sp(p1,t1), sp(p0,t1)
            if i == 0: s.tri(v00, v10, v11)
            elif i == rings-1: s.tri(v00, v10, v01)
            else: s.quad(v00, v10, v11, v01)
    for j in range(seg):
        t0 = 2*math.pi*j/seg; t1 = 2*math.pi*(j+1)/seg
        s.tri((0,0,0),(r*math.cos(t1),r*math.sin(t1),0),(r*math.cos(t0),r*math.sin(t0),0))
    return s

def sphere(r, seg=24, rings=12):
    s = STL()
    for i in range(rings):
        p0 = -math.pi/2 + math.pi*i/rings
        p1 = -math.pi/2 + math.pi*(i+1)/rings
        for j in range(seg):
            t0 = 2*math.pi*j/seg; t1 = 2*math.pi*(j+1)/seg
            def sp(p,t): return (r*math.cos(p)*math.cos(t), r*math.cos(p)*math.sin(t), r*math.sin(p))
            v00,v10,v11,v01 = sp(p0,t0), sp(p1,t0), sp(p1,t1), sp(p0,t1)
            if i == 0: s.tri(v00, v10, v11)
            elif i == rings-1: s.tri(v00, v10, v01)
            else: s.quad(v00, v10, v11, v01)
    return s


# ============================================================
# Component Builders
# ============================================================
NUM_DAYS = 7
DAY_ANGLE = 2*math.pi/NUM_DAYS

# Dimensions (mm)
BASE_R = 65; BASE_H = 10
HOUSING_RO = 63; HOUSING_RI = 59; HOUSING_H = 80
CAROUSEL_RO = 55; CAROUSEL_RI = 12; CAROUSEL_H = 28
RATCHET_R = 16; RATCHET_H = 5
AXLE_R = 5; AXLE_H = 70
BUTTON_R = 28; PLUNGER_R = 6; PLUNGER_H = 20
CUP_R = 22
SPRING_R = 8; SPRING_WIRE = 1.5; SPRING_COILS = 5; SPRING_H = 18

def build_base():
    print("  Base Plate + Feet...")
    s = cylinder(BASE_R, BASE_H, 64)
    # 4 rubber feet
    for i in range(4):
        a = math.pi/4 + i*math.pi/2
        foot = cylinder(8, 4, 24)
        foot = foot.translate(BASE_R*0.72*math.cos(a), BASE_R*0.72*math.sin(a), -4)
        s.merge(foot)
    return s

def build_housing():
    print("  Housing Shell...")
    s = tube(HOUSING_RO, HOUSING_RI, HOUSING_H, 64, z0=BASE_H)
    return s

def build_carousel():
    print("  Carousel Wheel + Dividers...")
    # Bottom disc
    s = tube(CAROUSEL_RO, CAROUSEL_RI, 2, 64, z0=0)
    # 7 divider walls
    for i in range(NUM_DAYS):
        a = i * DAY_ANGLE
        wall_len = CAROUSEL_RO - CAROUSEL_RI - 1
        wall = box(wall_len, 2, CAROUSEL_H, cx=CAROUSEL_RI + wall_len/2 + 0.5, cy=0, cz=CAROUSEL_H/2)
        s.merge(wall.rotate_z(a))
    # Outer ring wall
    s.merge(tube(CAROUSEL_RO, CAROUSEL_RO - 2, CAROUSEL_H, 64))
    return s

def build_ratchet():
    print("  Ratchet Wheel (7-tooth)...")
    s = cylinder(RATCHET_R, RATCHET_H, 7)
    # Sawtooth profile teeth
    for i in range(NUM_DAYS):
        a = i * DAY_ANGLE
        # Each tooth: wedge shape
        tooth = STL()
        t_len = 5; t_w = 3; t_h = RATCHET_H
        # Triangular prism (sawtooth)
        p1 = (0, -t_w/2, 0); p2 = (0, t_w/2, 0)
        p3 = (t_len, 0, 0); p4 = (0, -t_w/2, t_h)
        p5 = (0, t_w/2, t_h); p6 = (t_len, 0, t_h)
        tooth.tri(p1,p2,p3); tooth.tri(p4,p6,p5)  # bottom, top
        tooth.quad(p1,p3,p6,p4); tooth.quad(p2,p5,p6,p3)  # sides
        tooth.quad(p1,p4,p5,p2)  # back
        tooth = tooth.translate(RATCHET_R - 1, 0, 0)
        s.merge(tooth.rotate_z(a))
    return s

def build_pawl():
    print("  Pawl Arm...")
    s = box(15, 3, RATCHET_H, cx=0, cy=0, cz=RATCHET_H/2)
    # Triangular tip
    tip = STL()
    p1 = (0,-1.5,0); p2 = (0,1.5,0); p3 = (5,0,0)
    p4 = (0,-1.5,RATCHET_H); p5 = (0,1.5,RATCHET_H); p6 = (5,0,RATCHET_H)
    tip.tri(p1,p2,p3); tip.tri(p4,p6,p5)
    tip.quad(p1,p3,p6,p4); tip.quad(p2,p5,p6,p3)
    tip.quad(p1,p4,p5,p2)
    s.merge(tip.translate(7.5, 0, 0))
    return s

def build_plunger():
    print("  Plunger Shaft...")
    return cylinder(PLUNGER_R, PLUNGER_H, 32)

def build_spring():
    print("  Return Spring...")
    s = STL()
    pts_per_coil = 24
    total = SPRING_COILS * pts_per_coil
    tube_seg = 8
    for i in range(total):
        t0 = 2*math.pi*i/pts_per_coil; t1 = 2*math.pi*(i+1)/pts_per_coil
        z0 = SPRING_H*i/total; z1 = SPRING_H*(i+1)/total
        cx0 = SPRING_R*math.cos(t0); cy0 = SPRING_R*math.sin(t0)
        cx1 = SPRING_R*math.cos(t1); cy1 = SPRING_R*math.sin(t1)
        for j in range(tube_seg):
            p0 = 2*math.pi*j/tube_seg; p1 = 2*math.pi*(j+1)/tube_seg
            def wp(cx,cy,cz,tm,ph):
                nx = math.cos(tm); ny = math.sin(tm)
                px = cx + SPRING_WIRE*(nx*math.cos(ph))
                py = cy + SPRING_WIRE*(ny*math.cos(ph))
                pz = cz + SPRING_WIRE*math.sin(ph)
                return (px,py,pz)
            v00 = wp(cx0,cy0,z0,t0,p0); v01 = wp(cx0,cy0,z0,t0,p1)
            v10 = wp(cx1,cy1,z1,t1,p0); v11 = wp(cx1,cy1,z1,t1,p1)
            s.quad(v00, v10, v11, v01)
    return s

def build_button():
    print("  Palm Button (Dome)...")
    s = hemisphere(BUTTON_R, 48, 24)
    s.merge(cylinder(BUTTON_R - 2, 8, 48))  # Short cylindrical skirt
    return s

def build_cup():
    print("  Dispenser Cup...")
    # Bowl shape: hemisphere flipped
    bowl = hemisphere(CUP_R, 32, 16)
    flipped = STL()
    for (n, v1, v2, v3) in bowl.facets:
        def fl(v): return (v[0], v[1], -v[2])
        def fn(nn): return (nn[0], nn[1], -nn[2])
        flipped.facets.append((fn(n), fl(v1), fl(v3), fl(v2)))
    # Add a small ramp leading into the cup
    ramp = box(15, CUP_R*1.5, 2, cx=-10, cy=0, cz=-1)
    flipped.merge(ramp)
    return flipped

def build_axle():
    print("  Central Axle...")
    return cylinder(AXLE_R, AXLE_H, 32)

def build_pills():
    """Small pill-shaped spheres for visualization."""
    print("  Pills (for active compartment)...")
    s = STL()
    # 4 pills in the active compartment (pointing at angle 0)
    mid_r = (CAROUSEL_RO + CAROUSEL_RI) / 2
    half_angle = DAY_ANGLE / 2
    positions = [
        (mid_r * 0.7, 0, 8),
        (mid_r * 0.9, 3, 6),
        (mid_r * 0.8, -3, 10),
        (mid_r * 1.05, 1, 7),
    ]
    for (px, py, pz) in positions:
        pill = sphere(3.5, 12, 8)
        s.merge(pill.translate(px, py, pz))
    return s


# ============================================================
# Build All
# ============================================================
PARTS = [
    ("01_base_plate",     build_base,    (0, 0, 0)),
    ("02_housing_shell",  build_housing, (0, 0, 0)),
    ("03_carousel_wheel", build_carousel,(0, 0, BASE_H + 5)),
    ("04_ratchet_wheel",  build_ratchet, (0, 0, BASE_H + 5 + CAROUSEL_H + 2)),
    ("05_pawl_arm",       build_pawl,    (-(RATCHET_R + 12), 0, BASE_H + 5 + CAROUSEL_H + 2)),
    ("06_plunger_shaft",  build_plunger, (0, 0, BASE_H + HOUSING_H - PLUNGER_H - 5)),
    ("07_return_spring",  build_spring,  (0, 0, BASE_H + 5 + CAROUSEL_H + RATCHET_H + 4)),
    ("08_palm_button",    build_button,  (0, 0, BASE_H + HOUSING_H + 2)),
    ("09_dispenser_cup",  build_cup,     (HOUSING_RO + CUP_R * 0.6, 0, BASE_H + 8)),
    ("10_central_axle",   build_axle,    (0, 0, BASE_H)),
    ("11_pills",          build_pills,   (0, 0, BASE_H + 5)),
]

print("=" * 60)
print("Rotadex v2 — Precision STL Generator")
print("=" * 60)

assembly = STL()
stl_data = {}

for (name, builder, offset) in PARTS:
    part = builder()
    part.write(os.path.join(STL_DIR, f"{name}.stl"), name)
    positioned = part.translate(*offset)
    assembly.merge(positioned)
    # Read back for embedding
    with open(os.path.join(STL_DIR, f"{name}.stl"), 'r', encoding='utf-8') as f:
        stl_data[f"{name}.stl"] = f.read()

# Full assembly
assembly.write(os.path.join(STL_DIR, "rotadex_full_assembly.stl"), "rotadex")
# Y-up version
yup = STL()
for (n, v1, v2, v3) in assembly.facets:
    def ry(v): return (v[0], -v[2], v[1])
    def ryn(nn): return (nn[0], -nn[2], nn[1])
    yup.facets.append((ryn(n), ry(v1), ry(v2), ry(v3)))
yup.write(os.path.join(STL_DIR, "rotadex_full_assembly_y_up.stl"), "rotadex")

print(f"\n  Total assembly: {len(assembly.facets)} triangles")

# ============================================================
# Generate Standalone Embedded HTML Viewer
# ============================================================
print("\nGenerating standalone interactive viewer...")

viewer_html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Rotadex One-Hand — Interactive 3D CAD Viewer</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet"/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Outfit',sans-serif;background:#0a0f1a;color:#f1f5f9;overflow:hidden;height:100vh}
#hud-top{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;
  justify-content:space-between;padding:16px 28px;
  background:linear-gradient(180deg,rgba(10,15,26,0.95) 60%,rgba(10,15,26,0) 100%);pointer-events:none}
#hud-top>*{pointer-events:all}
.logo{display:flex;align-items:center;gap:12px}
.logo-icon{width:42px;height:42px;background:linear-gradient(135deg,#14b8a6,#0ea5e9);border-radius:11px;
  display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:800;color:#0a0f1a}
.logo h1{font-size:17px;font-weight:700;background:linear-gradient(90deg,#2dd4bf,#38bdf8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.logo p{font-size:11px;color:#64748b;font-weight:400}
.day-display{background:rgba(20,184,166,0.12);border:1px solid rgba(45,212,191,0.3);border-radius:12px;
  padding:10px 22px;text-align:center}
.day-display .day{font-size:28px;font-weight:700;color:#2dd4bf;line-height:1}
.day-display .label{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:2px}

#sidebar{position:fixed;right:20px;top:50%;transform:translateY(-50%);z-index:100;width:240px;
  background:rgba(15,23,42,0.85);backdrop-filter:blur(20px);border:1px solid rgba(148,163,184,0.12);
  border-radius:16px;padding:20px;box-shadow:0 12px 40px rgba(0,0,0,0.5)}
#sidebar h3{font-size:14px;color:#2dd4bf;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.part-row{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid rgba(148,163,184,0.08);
  font-size:12px;color:#94a3b8;cursor:pointer;transition:all .15s}
.part-row:hover{color:#f1f5f9;padding-left:4px}
.part-row:last-child{border-bottom:none}
.pdot{width:10px;height:10px;border-radius:50%;flex-shrink:0;box-shadow:0 0 6px rgba(0,0,0,0.3)}

#controls{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:100;
  display:flex;gap:8px;padding:8px 16px;background:rgba(15,23,42,0.85);backdrop-filter:blur(20px);
  border:1px solid rgba(148,163,184,0.12);border-radius:14px;box-shadow:0 8px 32px rgba(0,0,0,0.4)}
.cb{padding:10px 16px;border:1px solid rgba(148,163,184,0.15);background:transparent;color:#94a3b8;
  font-family:'Outfit',sans-serif;font-size:12px;font-weight:500;border-radius:10px;cursor:pointer;
  transition:all .2s;display:flex;align-items:center;gap:6px;white-space:nowrap}
.cb:hover{background:rgba(45,212,191,0.12);border-color:#2dd4bf;color:#2dd4bf}
.cb.active{background:rgba(45,212,191,0.18);border-color:#2dd4bf;color:#2dd4bf;
  box-shadow:0 0 12px rgba(45,212,191,0.15)}
.cb.primary{background:linear-gradient(135deg,rgba(20,184,166,0.25),rgba(14,165,233,0.25));
  border-color:#14b8a6;color:#2dd4bf}

#tip{position:fixed;bottom:80px;left:50%;transform:translateX(-50%);z-index:100;
  font-size:12px;color:#475569;text-align:center;pointer-events:none}

#overlay{position:fixed;inset:0;z-index:1000;background:#0a0f1a;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:16px;transition:opacity .6s}
#overlay.hide{opacity:0;pointer-events:none}
.spin{width:48px;height:48px;border:3px solid #1e293b;border-top-color:#14b8a6;border-radius:50%;
  animation:sp 1s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
@media(max-width:768px){#sidebar{display:none}.cb{padding:8px 10px;font-size:11px}}
</style>
</head>
<body>
<div id="overlay"><div class="spin"></div><p style="font-size:12px;color:#64748b;letter-spacing:3px">LOADING 3D MODEL</p></div>

<div id="hud-top">
  <div class="logo">
    <div class="logo-icon">R</div>
    <div><h1>Rotadex One-Hand</h1><p>Interactive CAD Assembly Viewer</p></div>
  </div>
  <div class="day-display"><div class="label">Active Day</div><div class="day" id="activeDayLabel">MON</div></div>
</div>

<div id="sidebar">
  <h3>🔩 Assembly Parts</h3>
  <div id="partsList"></div>
</div>

<div id="controls">
  <button class="cb primary" id="btnDispense">▶ Dispense Pill</button>
  <button class="cb" id="btnExplode">💥 Explode</button>
  <button class="cb" id="btnWire">🔲 Wireframe</button>
  <button class="cb" id="btnSpin">🔄 Auto-Rotate</button>
  <button class="cb" id="btnReset">🏠 Reset</button>
</div>

<div id="tip">🖱 Left-drag to rotate · Scroll to zoom · Right-drag to pan</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
/* ============ EMBEDDED STL DATA ============ */
const STL_DATA = __STL_DATA_PLACEHOLDER__;

/* ============ CONFIG ============ */
const DAYS = ['MON','TUE','WED','THU','FRI','SAT','SUN'];
const DAY_ANGLE = (2*Math.PI)/7;
const PARTS_CFG = [
  {key:'01_base_plate.stl',     name:'Base Plate & Feet',  color:0x475569, eColor:0x1e293b, explode:[0,-25,0]},
  {key:'02_housing_shell.stl',  name:'Housing Shell',      color:0x90a4ae, eColor:0x455a64, explode:[0,0,0],  transparent:true},
  {key:'03_carousel_wheel.stl', name:'Carousel (7-Day)',   color:0xcfd8dc, eColor:0x78909c, explode:[0,12,0]},
  {key:'04_ratchet_wheel.stl',  name:'Ratchet Wheel',      color:0xfbbf24, eColor:0x92400e, explode:[0,35,0]},
  {key:'05_pawl_arm.stl',       name:'Indexing Pawl',      color:0xf59e0b, eColor:0x78350f, explode:[-45,35,0]},
  {key:'06_plunger_shaft.stl',  name:'Plunger Shaft',      color:0x7dd3fc, eColor:0x0c4a6e, explode:[0,50,0]},
  {key:'07_return_spring.stl',  name:'Return Spring',      color:0xf87171, eColor:0x991b1b, explode:[30,50,0]},
  {key:'08_palm_button.stl',    name:'Palm Button (Dome)', color:0x38bdf8, eColor:0x075985, explode:[0,72,0]},
  {key:'09_dispenser_cup.stl',  name:'Dispenser Cup',      color:0x2dd4bf, eColor:0x134e4a, explode:[70,-12,0]},
  {key:'10_central_axle.stl',   name:'Central Axle',       color:0x64748b, eColor:0x1e293b, explode:[0,0,0]},
  {key:'11_pills.stl',          name:'Pills (Active Day)', color:0xfbbf24, eColor:0xb45309, explode:[0,12,0]},
];

/* ============ SCENE ============ */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0f1a);
scene.fog = new THREE.FogExp2(0x0a0f1a, 0.003);

const camera = new THREE.PerspectiveCamera(38, innerWidth/innerHeight, 0.1, 2000);
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
document.body.appendChild(renderer.domElement);

/* Lights */
scene.add(new THREE.AmbientLight(0x94a3b8, 0.45));
const keyL = new THREE.DirectionalLight(0xffffff, 0.85);
keyL.position.set(80,180,120); keyL.castShadow=true;
keyL.shadow.mapSize.set(1024,1024); scene.add(keyL);
scene.add(Object.assign(new THREE.DirectionalLight(0x2dd4bf,0.25),{position:new THREE.Vector3(-80,40,-80)}));
scene.add(Object.assign(new THREE.DirectionalLight(0x38bdf8,0.2),{position:new THREE.Vector3(0,-30,-100)}));
scene.add(Object.assign(new THREE.PointLight(0x14b8a6,0.3,300),{position:new THREE.Vector3(0,100,0)}));

/* Ground */
const gnd = new THREE.Mesh(new THREE.PlaneGeometry(500,500),
  new THREE.MeshStandardMaterial({color:0x0a0f1a,roughness:0.95}));
gnd.rotation.x=-Math.PI/2; gnd.position.y=-8; gnd.receiveShadow=true; scene.add(gnd);
const grid = new THREE.GridHelper(300,30,0x151d2e,0x151d2e);
grid.position.y=-7; scene.add(grid);

/* ============ STL PARSER ============ */
function parseSTL(text){
  const verts=[], norms=[];
  let cn=null, tv=[];
  for(const line of text.split('\n')){
    const t=line.trim();
    if(t.startsWith('facet normal')){const p=t.split(/\s+/);cn=[+p[2],+p[3],+p[4]]}
    else if(t.startsWith('vertex')){const p=t.split(/\s+/);tv.push(+p[1],+p[2],+p[3]);
      if(tv.length===9){verts.push(...tv);norms.push(...cn,...cn,...cn);tv=[]}}
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));
  g.setAttribute('normal',new THREE.Float32BufferAttribute(norms,3));
  return g;
}

/* ============ LOAD PARTS ============ */
const meshes=[], origPos=[];

const listEl=document.getElementById('partsList');
PARTS_CFG.forEach((cfg,i)=>{
  const d=document.createElement('div'); d.className='part-row';
  d.innerHTML=`<span class="pdot" style="background:#${cfg.color.toString(16).padStart(6,'0')}"></span>${cfg.name}`;
  d.onmouseenter=()=>{if(meshes[i])meshes[i].material.emissiveIntensity=0.5};
  d.onmouseleave=()=>{if(meshes[i])meshes[i].material.emissiveIntensity=0.06};
  listEl.appendChild(d);

  const text=STL_DATA[cfg.key];
  if(!text){meshes[i]=null;origPos[i]=new THREE.Vector3();return}
  const geo=parseSTL(text);
  const mat=new THREE.MeshPhysicalMaterial({
    color:cfg.color, emissive:cfg.eColor, emissiveIntensity:0.06,
    roughness:0.3, metalness:0.12, clearcoat:0.35, clearcoatRoughness:0.3,
    transparent:!!cfg.transparent, opacity:cfg.transparent?0.28:1, side:THREE.DoubleSide
  });
  const mesh=new THREE.Mesh(geo,mat);
  mesh.castShadow=true; mesh.receiveShadow=true;
  scene.add(mesh); meshes[i]=mesh; origPos[i]=mesh.position.clone();
});

/* ============ DAY LABELS (3D Sprites) ============ */
const daySprites=[];
DAYS.forEach((day,i)=>{
  const canvas=document.createElement('canvas');
  canvas.width=128; canvas.height=64;
  const ctx=canvas.getContext('2d');
  ctx.fillStyle='transparent'; ctx.fillRect(0,0,128,64);
  ctx.font='bold 32px Outfit, sans-serif';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillStyle='#2dd4bf'; ctx.fillText(day,64,32);
  const tex=new THREE.CanvasTexture(canvas);
  const mat=new THREE.SpriteMaterial({map:tex,transparent:true,depthTest:false});
  const sprite=new THREE.Sprite(mat);
  const angle=i*DAY_ANGLE + DAY_ANGLE/2;
  const r=72;
  sprite.position.set(r*Math.cos(angle), 30, r*Math.sin(angle));
  sprite.scale.set(20,10,1);
  scene.add(sprite);
  daySprites.push(sprite);
});

document.getElementById('overlay').classList.add('hide');

/* ============ ORBIT CONTROLS ============ */
let drag=false,rDrag=false,prev={x:0,y:0};
let orb={t:Math.PI/4,p:Math.PI/7},rad=240,pan={x:0,y:35,z:0};
let spinning=true;

function camUpdate(){
  camera.position.x=pan.x+rad*Math.cos(orb.p)*Math.cos(orb.t);
  camera.position.y=pan.y+rad*Math.sin(orb.p);
  camera.position.z=pan.z+rad*Math.cos(orb.p)*Math.sin(orb.t);
  camera.lookAt(pan.x,pan.y,pan.z);
}
camUpdate();

const cv=renderer.domElement;
cv.addEventListener('mousedown',e=>{if(e.button===2)rDrag=true;else drag=true;prev={x:e.clientX,y:e.clientY}});
cv.addEventListener('mousemove',e=>{
  const dx=e.clientX-prev.x, dy=e.clientY-prev.y;
  if(drag){orb.t-=dx*0.005;orb.p=Math.max(-1,Math.min(1.3,orb.p+dy*0.005));camUpdate()}
  if(rDrag){pan.x-=dx*0.25;pan.y+=dy*0.25;camUpdate()}
  prev={x:e.clientX,y:e.clientY};
});
cv.addEventListener('mouseup',()=>{drag=false;rDrag=false});
cv.addEventListener('mouseleave',()=>{drag=false;rDrag=false});
cv.addEventListener('wheel',e=>{rad=Math.max(80,Math.min(500,rad+e.deltaY*0.25));camUpdate()});
cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('touchstart',e=>{if(e.touches.length===1){drag=true;prev={x:e.touches[0].clientX,y:e.touches[0].clientY}}});
cv.addEventListener('touchmove',e=>{if(!drag||e.touches.length!==1)return;
  const dx=e.touches[0].clientX-prev.x,dy=e.touches[0].clientY-prev.y;
  orb.t-=dx*0.005;orb.p=Math.max(-1,Math.min(1.3,orb.p+dy*0.005));
  prev={x:e.touches[0].clientX,y:e.touches[0].clientY};camUpdate()});
cv.addEventListener('touchend',()=>drag=false);

/* ============ STATE ============ */
let exploded=false, wireOn=false, explodeT=0;
let currentDay=0, animating=false;

/* ============ DISPENSE ANIMATION ============ */
document.getElementById('btnDispense').onclick=()=>{
  if(animating)return; animating=true;
  const carousel=meshes[2], button=meshes[7], pills=meshes[10];
  const origBtnY=origPos[7]?origPos[7].y:0;
  const pushDist=6;
  let phase=0, t=0;
  const rotTarget=DAY_ANGLE;

  function step(){
    t+=0.025;
    if(phase===0){
      // Button press down
      if(button) button.position.y=origBtnY - Math.sin(Math.min(t,1)*Math.PI)*pushDist;
      if(t>=1){phase=1;t=0}
    } else if(phase===1){
      // Carousel rotates one click
      if(carousel) carousel.rotation.y+=rotTarget*0.03;
      if(pills) pills.rotation.y+=rotTarget*0.03;
      if(t>=1){
        phase=2;t=0;
        currentDay=(currentDay+1)%7;
        document.getElementById('activeDayLabel').textContent=DAYS[currentDay];
      }
    } else if(phase===2){
      // Button spring back
      if(button) button.position.y=origBtnY - Math.sin(Math.max(0,(1-t))*Math.PI)*pushDist*0.3;
      if(t>=0.5){animating=false;if(button)button.position.y=origBtnY;return}
    }
    requestAnimationFrame(step);
  }
  step();
};

/* ============ BUTTONS ============ */
document.getElementById('btnExplode').onclick=()=>{
  exploded=!exploded;
  document.getElementById('btnExplode').classList.toggle('active',exploded);
};
document.getElementById('btnWire').onclick=()=>{
  wireOn=!wireOn;
  meshes.forEach(m=>{if(m)m.material.wireframe=wireOn});
  document.getElementById('btnWire').classList.toggle('active',wireOn);
};
document.getElementById('btnSpin').onclick=()=>{
  spinning=!spinning;
  document.getElementById('btnSpin').classList.toggle('active',spinning);
};
document.getElementById('btnReset').onclick=()=>{
  orb={t:Math.PI/4,p:Math.PI/7};rad=240;pan={x:0,y:35,z:0};
  exploded=false;wireOn=false;spinning=true;explodeT=0;currentDay=0;
  document.getElementById('activeDayLabel').textContent=DAYS[0];
  meshes.forEach(m=>{if(m){m.material.wireframe=false;if(m.rotation)m.rotation.y=0}});
  document.querySelectorAll('.cb').forEach(b=>b.classList.remove('active'));
  camUpdate();
};

/* ============ RENDER LOOP ============ */
function animate(){
  requestAnimationFrame(animate);
  if(spinning&&!drag){orb.t+=0.002;camUpdate()}
  // Smooth explode
  const eTarget=exploded?1:0;
  explodeT+=(eTarget-explodeT)*0.05;
  meshes.forEach((m,i)=>{
    if(!m||!origPos[i])return;
    const ex=PARTS_CFG[i].explode;
    m.position.x=origPos[i].x+ex[0]*explodeT;
    m.position.y=origPos[i].y+ex[1]*explodeT;
    m.position.z=origPos[i].z+ex[2]*explodeT;
  });
  renderer.render(scene,camera);
}
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)});
animate();
</script>
</body>
</html>"""

# Inject the STL data
viewer_html = viewer_html.replace('__STL_DATA_PLACEHOLDER__', json.dumps(stl_data))

viewer_path = os.path.join(os.path.dirname(OUTPUT_DIR), "view_stl_model.html")
with open(viewer_path, 'w', encoding='utf-8') as f:
    f.write(viewer_html)
print(f"  Standalone viewer: {viewer_path}")

print(f"\n{'='*60}")
print("ALL DONE! Double-click view_stl_model.html to open.")
print(f"{'='*60}")

"""
Rotadex One-Handed Pill Organizer — STL CAD Model Generator
Generates proper ASCII STL files for each component and the full assembly.
No external dependencies required — uses pure Python + math.
"""
import math
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# STL Writer
# ============================================================
class STLWriter:
    def __init__(self):
        self.facets = []

    def add_triangle(self, v1, v2, v3):
        # Compute normal via cross product
        u = (v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2])
        w = (v3[0]-v1[0], v3[1]-v1[1], v3[2]-v1[2])
        nx = u[1]*w[2] - u[2]*w[1]
        ny = u[2]*w[0] - u[0]*w[2]
        nz = u[0]*w[1] - u[1]*w[0]
        ln = math.sqrt(nx*nx + ny*ny + nz*nz)
        if ln > 1e-12:
            nx /= ln; ny /= ln; nz /= ln
        self.facets.append(((nx, ny, nz), v1, v2, v3))

    def add_quad(self, v1, v2, v3, v4):
        self.add_triangle(v1, v2, v3)
        self.add_triangle(v1, v3, v4)

    def write(self, filepath, name="solid"):
        with open(filepath, 'w') as f:
            f.write(f"solid {name}\n")
            for (n, v1, v2, v3) in self.facets:
                f.write(f"  facet normal {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n")
                f.write(f"    outer loop\n")
                f.write(f"      vertex {v1[0]:.6f} {v1[1]:.6f} {v1[2]:.6f}\n")
                f.write(f"      vertex {v2[0]:.6f} {v2[1]:.6f} {v2[2]:.6f}\n")
                f.write(f"      vertex {v3[0]:.6f} {v3[1]:.6f} {v3[2]:.6f}\n")
                f.write(f"    endloop\n")
                f.write(f"  endfacet\n")
            f.write(f"endsolid {name}\n")
        print(f"  -> Written: {filepath} ({len(self.facets)} triangles)")

    def merge(self, other):
        self.facets.extend(other.facets)

    def translate(self, dx, dy, dz):
        new = STLWriter()
        for (n, v1, v2, v3) in self.facets:
            new.facets.append((n,
                (v1[0]+dx, v1[1]+dy, v1[2]+dz),
                (v2[0]+dx, v2[1]+dy, v2[2]+dz),
                (v3[0]+dx, v3[1]+dy, v3[2]+dz)))
        return new


# ============================================================
# Primitive Generators
# ============================================================
def make_cylinder(r, h, segments=48, center_z=False):
    """Solid cylinder along Z axis."""
    stl = STLWriter()
    z0 = -h/2 if center_z else 0
    z1 = h/2 if center_z else h
    for i in range(segments):
        a0 = 2*math.pi*i/segments
        a1 = 2*math.pi*(i+1)/segments
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)
        x0, y0 = r*c0, r*s0
        x1, y1 = r*c1, r*s1
        # Side face
        stl.add_quad((x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1))
        # Top face
        stl.add_triangle((0,0,z1),(x0,y0,z1),(x1,y1,z1))
        # Bottom face
        stl.add_triangle((0,0,z0),(x1,y1,z0),(x0,y0,z0))
    return stl

def make_hollow_cylinder(ro, ri, h, segments=48):
    """Hollow cylinder (tube) along Z axis."""
    stl = STLWriter()
    for i in range(segments):
        a0 = 2*math.pi*i/segments
        a1 = 2*math.pi*(i+1)/segments
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)
        # Outer wall
        ox0, oy0 = ro*c0, ro*s0
        ox1, oy1 = ro*c1, ro*s1
        stl.add_quad((ox0,oy0,0),(ox1,oy1,0),(ox1,oy1,h),(ox0,oy0,h))
        # Inner wall
        ix0, iy0 = ri*c0, ri*s0
        ix1, iy1 = ri*c1, ri*s1
        stl.add_quad((ix1,iy1,0),(ix0,iy0,0),(ix0,iy0,h),(ix1,iy1,h))
        # Top ring
        stl.add_quad((ix0,iy0,h),(ix1,iy1,h),(ox1,oy1,h),(ox0,oy0,h))
        # Bottom ring
        stl.add_quad((ix1,iy1,0),(ix0,iy0,0),(ox0,oy0,0),(ox1,oy1,0))
    return stl

def make_box(sx, sy, sz, cx=0, cy=0, cz=0):
    """Axis-aligned box centered at (cx, cy, cz)."""
    stl = STLWriter()
    x0, x1 = cx-sx/2, cx+sx/2
    y0, y1 = cy-sy/2, cy+sy/2
    z0, z1 = cz-sz/2, cz+sz/2
    # Front
    stl.add_quad((x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1))
    # Back
    stl.add_quad((x1,y1,z0),(x0,y1,z0),(x0,y1,z1),(x1,y1,z1))
    # Left
    stl.add_quad((x0,y1,z0),(x0,y0,z0),(x0,y0,z1),(x0,y1,z1))
    # Right
    stl.add_quad((x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1))
    # Top
    stl.add_quad((x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))
    # Bottom
    stl.add_quad((x1,y0,z0),(x0,y0,z0),(x0,y1,z0),(x1,y1,z0))
    return stl

def make_hemisphere(r, segments=32, rings=16):
    """Upper hemisphere (z >= 0)."""
    stl = STLWriter()
    for i in range(rings):
        phi0 = math.pi/2 * i / rings
        phi1 = math.pi/2 * (i+1) / rings
        for j in range(segments):
            theta0 = 2*math.pi*j/segments
            theta1 = 2*math.pi*(j+1)/segments
            def sph(p, t):
                return (r*math.cos(p)*math.cos(t),
                        r*math.cos(p)*math.sin(t),
                        r*math.sin(p))
            v00 = sph(phi0, theta0)
            v10 = sph(phi1, theta0)
            v11 = sph(phi1, theta1)
            v01 = sph(phi0, theta1)
            if i == 0:
                stl.add_triangle(v00, v10, v11)
            elif i == rings - 1:
                stl.add_triangle(v00, v10, v01)
            else:
                stl.add_quad(v00, v10, v11, v01)
    # Bottom cap (circle at z=0)
    for j in range(segments):
        theta0 = 2*math.pi*j/segments
        theta1 = 2*math.pi*(j+1)/segments
        stl.add_triangle((0,0,0),
                         (r*math.cos(theta1), r*math.sin(theta1), 0),
                         (r*math.cos(theta0), r*math.sin(theta0), 0))
    return stl

def make_cone(r, h, segments=24):
    """Cone with base at z=0, tip at z=h."""
    stl = STLWriter()
    for i in range(segments):
        a0 = 2*math.pi*i/segments
        a1 = 2*math.pi*(i+1)/segments
        x0, y0 = r*math.cos(a0), r*math.sin(a0)
        x1, y1 = r*math.cos(a1), r*math.sin(a1)
        # Side
        stl.add_triangle((x0,y0,0),(x1,y1,0),(0,0,h))
        # Base
        stl.add_triangle((0,0,0),(x1,y1,0),(x0,y0,0))
    return stl

def make_torus_segment(R, r, segments=24, tube_segments=12, angle=2*math.pi):
    """Torus segment (for spring coils)."""
    stl = STLWriter()
    for i in range(segments):
        t0 = angle * i / segments
        t1 = angle * (i+1) / segments
        for j in range(tube_segments):
            p0 = 2*math.pi*j/tube_segments
            p1 = 2*math.pi*(j+1)/tube_segments
            def torus_pt(t, p):
                x = (R + r*math.cos(p))*math.cos(t)
                y = (R + r*math.cos(p))*math.sin(t)
                z = r*math.sin(p)
                return (x, y, z)
            v00 = torus_pt(t0, p0)
            v10 = torus_pt(t1, p0)
            v11 = torus_pt(t1, p1)
            v01 = torus_pt(t0, p1)
            stl.add_quad(v00, v10, v11, v01)
    return stl


# ============================================================
# Component Builders (dimensions in mm)
# ============================================================
def build_base_plate():
    """Heavy weighted base plate with feet recesses."""
    print("Building: Base Plate...")
    stl = make_cylinder(62, 8, 64)
    return stl

def build_silicone_feet():
    """4 non-slip silicone feet."""
    print("Building: Silicone Feet...")
    stl = STLWriter()
    for i in range(4):
        angle = math.pi/4 + i * math.pi/2
        foot = make_cylinder(8, 3, 24)
        foot = foot.translate(62*0.75*math.cos(angle), 62*0.75*math.sin(angle), -3)
        stl.merge(foot)
    return stl

def build_housing_shell():
    """Outer cylindrical housing (hollow tube)."""
    print("Building: Housing Shell...")
    stl = make_hollow_cylinder(62, 59, 85, 64)
    return stl

def build_carousel_wheel():
    """7-compartment internal carousel with divider walls."""
    print("Building: Carousel Wheel...")
    # Main disc with center hole
    outer = make_cylinder(55, 30, 64)
    # We'll keep it solid and add divider walls on top
    stl = outer
    # 7 radial divider walls
    for i in range(7):
        angle = i * 2*math.pi/7
        # Each divider is a thin box from Ri to Ro
        wall_length = 55 - 15  # Ro - Ri = 40mm
        wall = make_box(wall_length, 2, 30,
                        cx=15 + wall_length/2, cy=0, cz=15)
        # Rotate by angle (manual rotation around Z)
        rotated = STLWriter()
        ca, sa = math.cos(angle), math.sin(angle)
        for (n, v1, v2, v3) in wall.facets:
            def rot(v):
                return (v[0]*ca - v[1]*sa, v[0]*sa + v[1]*ca, v[2])
            def rot_n(nn):
                return (nn[0]*ca - nn[1]*sa, nn[0]*sa + nn[1]*ca, nn[2])
            rotated.facets.append((rot_n(n), rot(v1), rot(v2), rot(v3)))
        stl.merge(rotated)
    return stl

def build_ratchet_wheel():
    """7-tooth ratchet wheel."""
    print("Building: Ratchet Wheel...")
    stl = make_cylinder(18, 6, 7)  # 7-sided for visual effect
    # Add 7 teeth (small cones)
    for i in range(7):
        angle = i * 2*math.pi/7
        tooth = make_cone(3, 5, 4)
        # Rotate tooth to point outward
        rotated = STLWriter()
        ca, sa = math.cos(angle), math.sin(angle)
        for (n, v1, v2, v3) in tooth.facets:
            def transform(v):
                # Rotate around Y by 90deg to lay flat, then position
                x = v[2]  # was z, now points radially out
                y = v[1]
                z = v[0]  # was x
                # Rotate in XY plane by angle
                rx = (18 + x)*ca - y*sa
                ry = (18 + x)*sa + y*ca
                return (rx, ry, z + 3)  # center vertically in ratchet
            def transform_n(nn):
                x = nn[2]; y = nn[1]; z = nn[0]
                rx = x*ca - y*sa
                ry = x*sa + y*ca
                ln = math.sqrt(rx*rx+ry*ry+z*z)
                if ln > 0: rx/=ln; ry/=ln; z/=ln
                return (rx, ry, z)
            rotated.facets.append((transform_n(n), transform(v1), transform(v2), transform(v3)))
        stl.merge(rotated)
    return stl

def build_pawl_arm():
    """Spring-loaded indexing pawl lever."""
    print("Building: Pawl Arm...")
    arm = make_box(12, 3, 6, cx=0, cy=0, cz=3)
    tip = make_cone(2, 5, 4)
    # Position tip at end of arm
    tip = tip.translate(8, 0, 0)
    stl = arm
    stl.merge(tip)
    return stl

def build_plunger_shaft():
    """Vertical plunger that connects button to ratchet."""
    print("Building: Plunger Shaft...")
    stl = make_cylinder(7, 25, 32)
    return stl

def build_return_spring():
    """Compression spring around the plunger."""
    print("Building: Return Spring...")
    stl = STLWriter()
    # Create a helix of small torus segments
    num_coils = 5
    coil_r = 1.2  # wire radius
    helix_R = 9   # spring outer radius
    pitch = 4     # mm per coil
    points_per_coil = 16
    total_points = num_coils * points_per_coil
    
    for i in range(total_points):
        t0 = 2*math.pi * i / points_per_coil
        t1 = 2*math.pi * (i+1) / points_per_coil
        z0 = pitch * i / points_per_coil
        z1 = pitch * (i+1) / points_per_coil
        cx0, cy0 = helix_R*math.cos(t0), helix_R*math.sin(t0)
        cx1, cy1 = helix_R*math.cos(t1), helix_R*math.sin(t1)
        
        # Small circle cross-section at each point
        tube_segs = 6
        for j in range(tube_segs):
            p0 = 2*math.pi*j/tube_segs
            p1 = 2*math.pi*(j+1)/tube_segs
            
            def wire_pt(cx, cy, cz, theta_main, phi):
                # Direction along helix
                dx = -math.sin(theta_main)
                dy = math.cos(theta_main)
                # Normal directions
                nx = math.cos(theta_main)
                ny = math.sin(theta_main)
                nz = 0
                bx = 0; by = 0; bz = 1
                
                px = cx + coil_r*(nx*math.cos(phi) + bx*math.sin(phi))
                py = cy + coil_r*(ny*math.cos(phi) + by*math.sin(phi))
                pz = cz + coil_r*(nz*math.cos(phi) + bz*math.sin(phi))
                return (px, py, pz)
            
            v00 = wire_pt(cx0, cy0, z0, t0, p0)
            v01 = wire_pt(cx0, cy0, z0, t0, p1)
            v10 = wire_pt(cx1, cy1, z1, t1, p0)
            v11 = wire_pt(cx1, cy1, z1, t1, p1)
            stl.add_quad(v00, v10, v11, v01)
    
    return stl

def build_palm_button():
    """Large dome button for palm/fist/elbow actuation."""
    print("Building: Palm Button (Dome)...")
    dome = make_hemisphere(25, 48, 24)
    # Add a short cylindrical stem below
    stem = make_cylinder(23, 5, 48)
    stem = stem.translate(0, 0, -5)
    stl = dome
    stl.merge(stem)
    return stl

def build_dispenser_cup():
    """Open-faced scoop cup for pill collection."""
    print("Building: Dispenser Cup...")
    # Half-sphere bowl
    bowl = make_hemisphere(20, 32, 16)
    # Flip upside down (negate Z)
    flipped = STLWriter()
    for (n, v1, v2, v3) in bowl.facets:
        def flip(v): return (v[0], v[1], -v[2])
        def flip_n(nn): return (nn[0], nn[1], -nn[2])
        # Reverse winding when flipping
        flipped.facets.append((flip_n(n), flip(v1), flip(v3), flip(v2)))
    return flipped

def build_central_axle():
    """Central rotation axle."""
    print("Building: Central Axle...")
    stl = make_cylinder(5, 77, 32)
    return stl


# ============================================================
# Assembly Positions (offsets in mm, Z-up)
# ============================================================
ASSEMBLY = [
    ("01_base_plate",      build_base_plate,      (0, 0, 0)),
    ("02_silicone_feet",   build_silicone_feet,    (0, 0, 0)),
    ("03_housing_shell",   build_housing_shell,    (0, 0, 8)),
    ("04_carousel_wheel",  build_carousel_wheel,   (0, 0, 18)),
    ("05_ratchet_wheel",   build_ratchet_wheel,    (0, 0, 50)),
    ("06_pawl_arm",        build_pawl_arm,         (-32, 0, 50)),
    ("07_plunger_shaft",   build_plunger_shaft,    (0, 0, 58)),
    ("08_return_spring",   build_return_spring,    (0, 0, 58)),
    ("09_palm_button",     build_palm_button,      (0, 0, 90)),
    ("10_dispenser_cup",   build_dispenser_cup,    (70, 0, 15)),
    ("11_central_axle",    build_central_axle,     (0, 0, 8)),
]


def main():
    print("=" * 60)
    print("Rotadex One-Hand — STL CAD Model Generator")
    print("=" * 60)
    
    stl_dir = os.path.join(OUTPUT_DIR, "stl_models")
    os.makedirs(stl_dir, exist_ok=True)
    
    full_assembly = STLWriter()
    
    for (name, builder, offset) in ASSEMBLY:
        part = builder()
        # Save individual part
        part.write(os.path.join(stl_dir, f"{name}.stl"), name)
        # Add to assembly with offset
        positioned = part.translate(*offset)
        full_assembly.merge(positioned)
    
    # Save full assembly (Z-up)
    print("\nBuilding: Full Assembly (Z-up)...")
    full_assembly.write(os.path.join(stl_dir, "rotadex_full_assembly.stl"), "rotadex_assembly")
    
    # Save full assembly rotated for Y-up viewers (like viewstl.com)
    print("\nBuilding: Full Assembly (Y-up rotated)...")
    y_up_assembly = STLWriter()
    for (n, v1, v2, v3) in full_assembly.facets:
        # Rotate 90 degrees around X-axis: (x, y, z) -> (x, -z, y)
        def rot_x90(v): return (v[0], -v[2], v[1])
        def rot_x90_n(nn): return (nn[0], -nn[2], nn[1])
        y_up_assembly.facets.append((rot_x90_n(n), rot_x90(v1), rot_x90(v2), rot_x90(v3)))
    y_up_assembly.write(os.path.join(stl_dir, "rotadex_full_assembly_y_up.stl"), "rotadex_assembly")
    
    total = len(full_assembly.facets)
    print(f"\n{'=' * 60}")
    print(f"DONE! Generated 13 STL files in: {stl_dir}")
    print(f"Full assembly: {total} triangles")
    print(f"{'=' * 60}")
    print(f"\nOpen any .stl file in:")
    print(f"  - Windows 3D Viewer (built-in)")
    print(f"  - FreeCAD (free)")
    print(f"  - Fusion 360 / SolidWorks / CATIA")
    print(f"  - Any 3D printing slicer (Cura, PrusaSlicer)")


if __name__ == "__main__":
    main()

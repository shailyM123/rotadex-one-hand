// ============================================================
// Rotadex One-Handed Pill Organizer — Parametric OpenSCAD Model
// ============================================================
// Author: End-Semester Design Project
// Description: A 7-day mechanical rotary pill organizer with
//   palm-button ratchet indexing and gravity dispensing.
// Units: millimeters (mm)
// ============================================================

// ---- GLOBAL PARAMETERS ----
$fn = 80; // Facet resolution

// Carousel parameters
num_days        = 7;
carousel_Ro     = 55;    // outer radius of carousel
carousel_Ri     = 15;    // inner radius (axle hole)
carousel_H      = 30;    // height of carousel compartments
wall_thick      = 2;     // divider wall thickness

// Housing parameters
housing_Ro      = 62;    // outer radius of housing shell
housing_H       = 85;    // total height of housing
housing_wall    = 3;     // wall thickness
base_H          = 8;     // base plate height
base_weight_R   = 50;    // radius of weight ring in base

// Button parameters
button_R        = 25;    // button dome radius
button_H        = 15;    // button protrusion height
plunger_R       = 7;     // plunger shaft radius
plunger_L       = 25;    // plunger shaft length

// Ratchet parameters
ratchet_R       = 18;    // ratchet wheel radius
ratchet_H       = 6;     // ratchet wheel thickness
tooth_depth     = 3;     // depth of each tooth
pawl_L          = 12;    // pawl arm length
pawl_W          = 3;     // pawl width

// Chute & Cup parameters
chute_W         = 25;    // chute opening width
cup_R           = 20;    // cup inner radius
cup_depth       = 15;    // cup depth

// Axle parameters
axle_R          = 5;     // central axle radius
axle_H          = housing_H - base_H; // axle height

// Foot parameters
foot_R          = 8;
foot_H          = 3;
num_feet        = 4;

// Day angle
day_angle = 360 / num_days;


// ============================================================
// MODULE: Base Plate with Weighted Ring & Feet
// ============================================================
module base_plate() {
    color("#475569") {
        difference() {
            cylinder(r=housing_Ro, h=base_H);
            // Weight channel (hollow ring to fill with steel shot)
            translate([0, 0, 2])
                difference() {
                    cylinder(r=base_weight_R, h=base_H - 3);
                    cylinder(r=base_weight_R - 8, h=base_H - 3 + 1);
                }
        }
    }
    // Silicone feet
    color("#1e293b")
    for (i = [0:num_feet-1]) {
        angle = i * (360 / num_feet) + 45;
        translate([housing_Ro * 0.75 * cos(angle), housing_Ro * 0.75 * sin(angle), -foot_H])
            cylinder(r=foot_R, h=foot_H);
    }
}


// ============================================================
// MODULE: Outer Housing Shell (Cylinder with viewing window)
// ============================================================
module housing_shell() {
    color("#e2e8f0", 0.4) {
        difference() {
            cylinder(r=housing_Ro, h=housing_H);
            // Hollow inside
            translate([0, 0, base_H])
                cylinder(r=housing_Ro - housing_wall, h=housing_H - base_H + 1);
            // Viewing window (front)
            translate([housing_Ro - housing_wall - 1, -12, housing_H * 0.55])
                cube([housing_wall + 4, 24, 20]);
            // Dispensing chute opening (bottom front)
            translate([housing_Ro - housing_wall - 1, -chute_W/2, base_H])
                cube([housing_wall + 4, chute_W, carousel_H + 5]);
        }
    }
}


// ============================================================
// MODULE: 7-Compartment Carousel Wheel
// ============================================================
module carousel_wheel() {
    color("#f1f5f9") {
        difference() {
            cylinder(r=carousel_Ro, h=carousel_H);
            // Axle hole
            translate([0, 0, -1])
                cylinder(r=carousel_Ri, h=carousel_H + 2);
        }
    }
    // Divider walls
    color("#94a3b8")
    for (i = [0:num_days-1]) {
        rotate([0, 0, i * day_angle])
            translate([-wall_thick/2, carousel_Ri, 0])
                cube([wall_thick, carousel_Ro - carousel_Ri, carousel_H]);
    }
}


// ============================================================
// MODULE: Ratchet Wheel (7-tooth)
// ============================================================
module ratchet_wheel() {
    color("#fbbf24") {
        difference() {
            cylinder(r=ratchet_R, h=ratchet_H);
            translate([0, 0, -1])
                cylinder(r=axle_R + 0.5, h=ratchet_H + 2);
        }
        // Teeth
        for (i = [0:num_days-1]) {
            rotate([0, 0, i * day_angle])
                translate([ratchet_R - 1, -2, 0])
                    linear_extrude(height=ratchet_H)
                        polygon([
                            [0, 0],
                            [tooth_depth, 2],
                            [0, 4]
                        ]);
        }
    }
}


// ============================================================
// MODULE: Pawl (Spring-loaded indexing lever)
// ============================================================
module pawl() {
    color("#d97706") {
        translate([0, 0, 0]) {
            // Arm
            cube([pawl_L, pawl_W, ratchet_H]);
            // Tip (triangular tooth engagement)
            translate([pawl_L, 0, 0])
                linear_extrude(height=ratchet_H)
                    polygon([
                        [0, 0],
                        [4, pawl_W/2],
                        [0, pawl_W]
                    ]);
        }
    }
}


// ============================================================
// MODULE: Plunger Shaft
// ============================================================
module plunger() {
    color("#93c5fd") {
        cylinder(r=plunger_R, h=plunger_L);
    }
}


// ============================================================
// MODULE: Top Button (Dome)
// ============================================================
module top_button() {
    color("#3b82f6") {
        // Dome shape (hemisphere)
        translate([0, 0, 0])
            scale([1, 1, 0.5])
                sphere(r=button_R);
        // Cylindrical base of button
        translate([0, 0, -5])
            cylinder(r=button_R - 2, h=5);
    }
}


// ============================================================
// MODULE: Central Axle
// ============================================================
module central_axle() {
    color("#64748b") {
        cylinder(r=axle_R, h=axle_H);
    }
}


// ============================================================
// MODULE: Dispenser Cup (Scoop tray)
// ============================================================
module dispenser_cup() {
    color("#dbeafe") {
        difference() {
            translate([0, 0, 0])
                scale([1.3, 1, 0.5])
                    sphere(r=cup_R);
            // Cut top half to make a bowl
            translate([-cup_R*2, -cup_R*2, 0])
                cube([cup_R*4, cup_R*4, cup_R*2]);
            // Cut back half to make it open-faced
            translate([-cup_R*2, -cup_R*2, -cup_R*2])
                cube([cup_R*4, cup_R*4 / 2 - 2, cup_R*4]);
        }
    }
}


// ============================================================
// MODULE: Spring (Decorative helix)
// ============================================================
module spring_coil(turns=3, r=5, h=15) {
    color("#ef4444") {
        for (i = [0:turns*36-1]) {
            t  = i / (turns * 36);
            t2 = (i+1) / (turns * 36);
            hull() {
                translate([r * cos(i * 10), r * sin(i * 10), t * h])
                    sphere(r=0.6);
                translate([r * cos((i+1) * 10), r * sin((i+1) * 10), t2 * h])
                    sphere(r=0.6);
            }
        }
    }
}


// ============================================================
// MODULE: Day Label (Text on housing, for visualization)
// ============================================================
module day_label(day_text, angle_pos) {
    color("#1e293b")
    rotate([0, 0, angle_pos])
        translate([housing_Ro + 1, 0, housing_H * 0.7])
            rotate([90, 0, 90])
                linear_extrude(height=1)
                    text(day_text, size=6, halign="center", valign="center",
                         font="Liberation Sans:style=Bold");
}


// ============================================================
// ASSEMBLY: Full Rotadex Model
// ============================================================
module rotadex_assembly() {
    // 1. Base Plate
    base_plate();
    
    // 2. Central Axle
    translate([0, 0, base_H])
        central_axle();
    
    // 3. Outer Housing Shell
    housing_shell();
    
    // 4. Carousel Wheel (positioned inside housing)
    translate([0, 0, base_H + 10])
        carousel_wheel();
    
    // 5. Ratchet Wheel (on top of carousel)
    translate([0, 0, base_H + 10 + carousel_H + 2])
        ratchet_wheel();
    
    // 6. Pawl
    translate([-(ratchet_R + pawl_L + 2), -pawl_W/2, base_H + 10 + carousel_H + 2])
        pawl();
    
    // 7. Plunger Shaft
    translate([0, 0, housing_H - plunger_L - button_H + 5])
        plunger();
    
    // 8. Spring around plunger
    translate([0, 0, housing_H - plunger_L - button_H + 5])
        spring_coil(turns=3, r=plunger_R + 2, h=plunger_L - 5);
    
    // 9. Top Button
    translate([0, 0, housing_H + 2])
        top_button();
    
    // 10. Dispenser Cup
    translate([housing_Ro + cup_R * 0.5, 0, base_H + 3])
        dispenser_cup();
    
    // 11. Day Labels (external markings)
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
    for (i = [0:6]) {
        day_label(days[i], i * day_angle);
    }
}


// ============================================================
// RENDER
// ============================================================
rotadex_assembly();

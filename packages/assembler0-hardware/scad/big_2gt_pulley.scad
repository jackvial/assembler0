include <BOSL2/std.scad>

// 2GT Timing Belt Pulley - Large (200 teeth for 10:1 ratio with 20-tooth small pulley)

// ===== Pulley Dimensions =====
// Basic parameters
teeth = 200;                    // Number of teeth (10:1 ratio with 20-tooth pulley)
pitch = 2;                      // 2GT standard pitch in mm
belt_width = 6;                 // Belt width in mm
flange_height = 1;              // Flange height on each side in mm
bore_diameter = 5;              // Center bore diameter in mm

// Calculated dimensions
pitch_circumference = teeth * pitch;                    // 400mm
pitch_radius = pitch_circumference / (2 * PI);          // ~63.66mm
pitch_diameter = pitch_radius * 2;                      // ~127.32mm

// 2GT tooth profile dimensions (standard for 2GT belts)
tooth_depth = 0.75;             // Tooth height above pitch circle
tooth_width_top = 0.75;         // Tooth width at the top
tooth_width_base = 1.2;         // Tooth width at base
tooth_radius = 0.15;            // Radius for rounding tooth corners

// Pulley body dimensions
tooth_base_radius = pitch_radius - tooth_depth;         // Base of teeth (root)
tooth_tip_radius = pitch_radius + tooth_depth;          // Top of teeth
flange_radius = tooth_tip_radius + 0.5;                 // Flange extends beyond teeth
total_height = belt_width + (2 * flange_height);        // Total pulley height = 8mm

// Resolution
$fn = 100;

// ===== Modules =====

// Single 2GT tooth profile (2D)
module tooth_2d() {
    // 2GT teeth have a rounded trapezoid profile
    // The tooth is centered at the origin and extends radially outward
    
    tooth_angle = 360 / teeth;  // Angle per tooth
    half_tooth_angle_base = (tooth_width_base / pitch_radius) * (180 / PI) / 2;
    half_tooth_angle_top = (tooth_width_top / tooth_tip_radius) * (180 / PI) / 2;
    
    hull() {
        // Bottom of tooth (at root radius)
        rotate([0, 0, -half_tooth_angle_base])
            translate([tooth_base_radius, 0, 0])
                circle(r=tooth_radius, $fn=16);
        
        rotate([0, 0, half_tooth_angle_base])
            translate([tooth_base_radius, 0, 0])
                circle(r=tooth_radius, $fn=16);
        
        // Top of tooth (at tip radius)
        rotate([0, 0, -half_tooth_angle_top])
            translate([tooth_tip_radius, 0, 0])
                circle(r=tooth_radius, $fn=16);
        
        rotate([0, 0, half_tooth_angle_top])
            translate([tooth_tip_radius, 0, 0])
                circle(r=tooth_radius, $fn=16);
    }
}

// Complete pulley with teeth
module pulley_with_teeth() {
    linear_extrude(height=belt_width, center=true) {
        union() {
            // Base cylinder at root radius
            circle(r=tooth_base_radius);
            
            // Add all teeth around the circumference
            zrot_copies(n=teeth) {
                tooth_2d();
            }
        }
    }
}

// Flanges on both sides
module flanges() {
    // Bottom flange
    translate([0, 0, -belt_width/2 - flange_height/2])
        cyl(h=flange_height, r=flange_radius, anchor=CENTER);
    
    // Top flange
    translate([0, 0, belt_width/2 + flange_height/2])
        cyl(h=flange_height, r=flange_radius, anchor=CENTER);
}

// Main assembly
module big_2gt_pulley() {
    difference() {
        union() {
            // Pulley body with teeth
            pulley_with_teeth();
            
            // Belt guide flanges
            flanges();
        }
        
        // Center bore hole
        cylinder(h=total_height + 2, r=bore_diameter/2, center=true, $fn=50);
    }
}

// Render the pulley
big_2gt_pulley();



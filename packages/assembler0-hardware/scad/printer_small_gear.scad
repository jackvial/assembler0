include <BOSL2/std.scad>
include <BOSL2/gears.scad>

// Gear
circ_pitch = 5.44;
teeth = 9;
gear_height = 12;
shaft_diam = 6.2;
pressure_angle = 30;
clearance = 0.1;
backlash = 0;

// Base cylinder
base_cylinder_radius = 9.5;
base_cylinder_height = 6;

// Shaft hole
shaft_hole_radius = shaft_diam/2;
shaft_hole_height = 10;

// Side hole
side_hole_radius = 1;
side_hole_height = 10;

fn = 64;
eps = 0.1;

module printer_small_gear() {
    spur_gear(
        circ_pitch=circ_pitch,
        teeth=teeth,
        thickness=gear_height,
        shaft_diam=shaft_diam,
        pressure_angle=pressure_angle,
        clearance=clearance,
        backlash=backlash
    );
    translate([0, 0, -(gear_height)]) {
        difference() {
            cylinder(r=base_cylinder_radius, h=base_cylinder_height, $fn=fn);
            translate([0, 0, -eps]) {
                cylinder(r=shaft_hole_radius, h=base_cylinder_height + (2 * eps), $fn=fn);
            }

            // rotate([0, 90, 0]) {
            //     translate([-3, 0, 0]) {
            //         cylinder(r=side_hole_radius, h=side_hole_height, $fn=fn);
            //     }
            // }
        }
    }
    
    // shaft D fill
    translate([0, 0, -12]) {
        difference() {
            cylinder(r=shaft_diam/2, h=base_cylinder_height, $fn=fn);
            
            // slice part off
            translate([0, -0.75, 0]) {
                cube([shaft_diam, shaft_diam, 20], center=true);
                
            }
        }
    }
    
}

printer_small_gear();

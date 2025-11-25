include <BOSL2/std.scad>

// ========================= Parameters =========================
// Wrist roll dimensions
wrist_width = 46;
wrist_depth = 33;
wrist_origin_x = -wrist_width/2;  // Calculated to center assembly around x=0
wrist_origin_y = -15;

// Extruder mounting dimensions
extruder_unit_offset_from_front = 10;
extruder_screw_spacing = 9.5; // distance from center
extruder_front_row_offset = 8;
extruder_back_row_offset = 18;
extruder_center_hole_radius = 3;
extruder_cradle_thickness = 10;
extruder_cradle_height = 60;
extruder_screw_spacing = 9.5; // distance from center
extruder_mount_screw_hole_radius = 1.6;
screw_holes_height = 12;

// Hotend mounting dimensions
hotend_cradle_width = 46;
hotend_hole_radius = 6.5;
hotend_hex_radius = 10;
hotend_cradle_thickness = 8;
screw_access_hole_radius = 2.8;

// Boolean difference offset
boolean_offset = -0.1;

$fn = 64; // global smoothness for all circular geometry
$render_vitamines = false;
$extruder_width = 38;

module manipulator() {

  // Extruder cradle
  translate([-wrist_width/2, wrist_origin_y, extruder_cradle_height]) {
    difference() {
        cuboid([wrist_width, wrist_depth, extruder_cradle_thickness], anchor=FRONT+LEFT+BOTTOM, rounding=2, except=[TOP, FRONT]);
        
        // Extruder to hotend hole for filament
        translate([wrist_width/2, wrist_depth - (5 + extruder_unit_offset_from_front), boolean_offset]) {
            cylinder(h=11, r=extruder_center_hole_radius);
        }
        
        

        // can add these back for additional extruder support but might not be needed and simplifies design and assembly not having them
        // Front row of screw holes
        translate([(wrist_width/2) - extruder_screw_spacing, wrist_depth - (extruder_front_row_offset + extruder_unit_offset_from_front), boolean_offset]) {
            cylinder(h=screw_holes_height, r=extruder_mount_screw_hole_radius);
        }

        translate([(wrist_width/2) + extruder_screw_spacing, wrist_depth - (extruder_front_row_offset + extruder_unit_offset_from_front), boolean_offset]) {
            cylinder(h=screw_holes_height, r=extruder_mount_screw_hole_radius);
        }

        // Back row of screw holes
        translate([(wrist_width/2) - extruder_screw_spacing, wrist_depth - (extruder_back_row_offset + extruder_unit_offset_from_front), boolean_offset]) {
            cylinder(h=screw_holes_height, r=extruder_mount_screw_hole_radius);
        }

        translate([(wrist_width/2) + extruder_screw_spacing, wrist_depth - (extruder_back_row_offset + extruder_unit_offset_from_front), boolean_offset]) {
            cylinder(h=screw_holes_height, r=extruder_mount_screw_hole_radius);
        }
    }
  }


  // Hotend cradle
  translate([-hotend_cradle_width/2, wrist_origin_y, 82]) {
    hole_height = 12;
    difference() {
        union() {
            cuboid([hotend_cradle_width, wrist_depth, hotend_cradle_thickness], anchor=FRONT+LEFT+BOTTOM, rounding=2, except=[BOTTOM, FRONT]);
            
            // Side wall 1
            translate([0, 0, -12]) {
                cuboid([10.5, wrist_depth, 12], anchor=FRONT+LEFT+BOTTOM, rounding=2, except=[TOP, BOTTOM, FRONT, BACK+RIGHT]);
            }
            
            // Side wall 2
            translate([hotend_cradle_width - 10.5, 0, -12]) {   
                cuboid([10.5, wrist_depth, 12], anchor=FRONT+LEFT+BOTTOM, rounding=2, except=[TOP, BOTTOM, FRONT, BACK+LEFT]);
            }
        }

        translate([hotend_cradle_width/2, wrist_depth - (5 + extruder_unit_offset_from_front), boolean_offset]) {

            // Hotend attachment hole
            cylinder(h=hole_height, r=hotend_hole_radius);

            // Hex nut hole
            cylinder(h=2, r=hotend_hex_radius, $fn=6);
        }


        // Cut holes through the hotend cradle for access to the extruder mount screw holes
        // Both the extruder and hotend are centered at global x=0
        // The extruder screw holes are at ±extruder_screw_spacing from this center
        // In hotend cradle local coordinates, x=0 is at hotend_cradle_width/2
        
        center_x = hotend_cradle_width/2;  // This is where global x=0 is in hotend cradle coords
        
        // Front row access holes
        translate([center_x - extruder_screw_spacing, wrist_depth - (extruder_front_row_offset + extruder_unit_offset_from_front), boolean_offset]) {
            cylinder(h=hotend_cradle_thickness + 1, r=screw_access_hole_radius);
        }
        
        translate([center_x + extruder_screw_spacing, wrist_depth - (extruder_front_row_offset + extruder_unit_offset_from_front), boolean_offset]) {
            cylinder(h=hotend_cradle_thickness + 1, r=screw_access_hole_radius);
        }
        
        // Back row access holes
        translate([center_x - extruder_screw_spacing, wrist_depth - (extruder_back_row_offset + extruder_unit_offset_from_front), boolean_offset]) {
            cylinder(h=hotend_cradle_thickness + 1, r=screw_access_hole_radius);
        }
        
        translate([center_x + extruder_screw_spacing, wrist_depth - (extruder_back_row_offset + extruder_unit_offset_from_front), boolean_offset]) {
            cylinder(h=hotend_cradle_thickness + 1, r=screw_access_hole_radius);
        }
    }
  }
}

module mount() {
    difference() {
        cuboid([wrist_width, 24, 10], anchor=FRONT+LEFT+BOTTOM, rounding=2, except=[TOP, BACK, FRONT]);
        
        // Three screw holes
        spacing = 15;
        
        // center hole
        translate([wrist_width/2, 5, -0.1]) {
            cylinder(h=11, r=2);
            
            // hex nut hole
            cylinder(h=4, r=4, $fn=6);
        }
        
        // left hole
        translate([wrist_width/2 - spacing, 5, -0.1]) {
            cylinder(h=11, r=2);
            
            // hex nut hole
            cylinder(h=4, r=4, $fn=6);
        }
        
        // right hole
        translate([wrist_width/2 + spacing, 5, -0.1]) {
            cylinder(h=11, r=2);
            
            // hex nut hole
            cylinder(h=4, r=4, $fn=6);
        }
    }
}

module extruder_placeholder() {
    rotate([90, 90, 0]) {
        translate([-60, -$extruder_width/2, -(20 - extruder_unit_offset_from_front) ]) {
            cuboid([$extruder_width, $extruder_width, 24], anchor=FRONT+LEFT+BOTTOM);
            translate([38/2, 38/2, 24]) {
                cylinder(h=19, r=18);
            }
        }
    }
}

module hotend_placeholder() {
    translate([0, extruder_unit_offset_from_front - 6, 79]) {
        cylinder(h=11, r=hotend_hole_radius);
        translate([0, 0, 11]) {
            cylinder(h=24, r=10);
        }
        translate([0, 0, 35]) {
            cylinder(h=3, r=1.5);
        }
        translate([0, 0, 38]) {
            cylinder(h=12, r=8);
        }
        translate([0, 0, 50]) {
            cylinder(h=5, r=hotend_hole_radius);
        }
        translate([0, 0, 55]) {
            cylinder(h=3, r=2, r2=0);
        }
    }
}

module main() {
  translate([-wrist_width/2, wrist_origin_y-24, 60]) {
    mount();
    // difference() {
    //     import("../stl/ftobler_arm/files/gripperBase.stl");
    //     translate([-50, -15, -5]) {
    //       cuboid([100, 50, 20], anchor=FRONT+LEFT+BOTTOM);
    //     }
        
    //     // Hex nut hole 1
    //     translate([-15, -19, -0.1]) {
    //         cylinder(h=3, r=4, $fn=6);
    //     }
        
    //     // Hex nut hole 2
    //     translate([15, -19, -0.1]) {
    //         cylinder(h=3, r=4, $fn=6);
    //     }
        
    //     // Hex nut hole center
    //     translate([0, -19, -0.1]) {
    //         cylinder(h=3, r=4, $fn=6);
    //     }
    // }
  }
  
  manipulator();

  if ($render_vitamines) {
    extruder_placeholder();
  }
  if ($render_vitamines) {
    hotend_placeholder();
  }
}

main();
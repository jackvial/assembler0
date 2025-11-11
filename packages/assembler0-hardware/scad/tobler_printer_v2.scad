
// ========================= Parameters =========================
// Wrist roll dimensions
wrist_width = 46;
wrist_depth = 38;
wrist_origin_x = -wrist_width/2;  // Calculated to center assembly around x=0
wrist_origin_y = -15;

// Extruder mounting dimensions
extruder_offset_from_front = 5;
extruder_center_hole_radius = 3;
extruder_cradle_thickness = 10;
extruder_cradle_height = 60;

// Hotend mounting dimensions
hotend_cradle_width = 25;
hotend_hole_radius = 6.5;
hotend_hex_radius = 10;
hotend_cradle_thickness = 8;
screw_access_hole_radius = 2.4;

// Boolean difference offset
boolean_offset = -0.1;

$fn = 64; // global smoothness for all circular geometry
$render_vitamines = true;
$extruder_width = 38;

module wrist_roll() {

  // Extruder cradle
  translate([-wrist_width/2, wrist_origin_y, extruder_cradle_height]) {
    difference() {
        cube([wrist_width, wrist_depth, extruder_cradle_thickness]);
        
        // Extruder to hotend hole for filament
        translate([wrist_width/2, wrist_depth - (5 + extruder_offset_from_front), boolean_offset]) {
            cylinder(h=11, r=extruder_center_hole_radius);
        }

        // can add these back for additional extruder support but might not be needed and simplifies design and assembly not having them
        // Front row of screw holes
        // translate([(wrist_width/2) - extruder_screw_spacing, wrist_depth - (extruder_front_row_offset + extruder_offset_from_front), boolean_offset]) {
        //     cylinder(h=4, r=screw_hole_radius);
        // }

        // translate([(wrist_width/2) + extruder_screw_spacing, wrist_depth - (extruder_front_row_offset + extruder_offset_from_front), boolean_offset]) {
        //     cylinder(h=4, r=screw_hole_radius);
        // }

        // // Back row of screw holes
        // translate([(wrist_width/2) - extruder_screw_spacing, wrist_depth - (extruder_back_row_offset + extruder_offset_from_front), boolean_offset]) {
        //     cylinder(h=4, r=screw_hole_radius);
        // }

        // translate([(wrist_width/2) + extruder_screw_spacing, wrist_depth - (extruder_back_row_offset + extruder_offset_from_front), boolean_offset]) {
        //     cylinder(h=4, r=screw_hole_radius);
        // }
    }
  }


  // Hotend cradle
  translate([-hotend_cradle_width/2, wrist_origin_y, 82]) {
    hole_height = 12;
    difference() {
        cube([hotend_cradle_width, wrist_depth, hotend_cradle_thickness]);

        // Cut away for screwdriver access
        // translate([wrist_width/2, 0, boolean_offset]) {
        //     cylinder(h=hotend_cradle_thickness + 1, r=mount_screw_access_cutaway);
        // }

        translate([hotend_cradle_width/2, wrist_depth - (5 + extruder_offset_from_front), boolean_offset]) {

            // Hotend attachment hole
            cylinder(h=hole_height, r=hotend_hole_radius);

            // Hex nut hole
            cylinder(h=2, r=hotend_hex_radius, $fn=6);
        }

        // can add these back for additional extruder support but might not be needed and simplifies design and assembly not having them
        // Access holes for the extruder cradle attachment
        // Front row of screw holes
        // translate([(wrist_width/2) - extruder_screw_spacing, wrist_depth - (extruder_front_row_offset + extruder_offset_from_front), boolean_offset]) {
        //     cylinder(h=hole_height, r=screw_access_hole_radius);
        // }

        // translate([(wrist_width/2) + extruder_screw_spacing, wrist_depth - (extruder_front_row_offset + extruder_offset_from_front), boolean_offset]) {
        //     cylinder(h=hole_height, r=screw_access_hole_radius);
        // }

        // // Back row of screw holes
        // translate([(wrist_width/2) - extruder_screw_spacing, wrist_depth - (extruder_back_row_offset + extruder_offset_from_front), boolean_offset]) {
        //     cylinder(h=hole_height, r=screw_access_hole_radius);
        // }

        // translate([(wrist_width/2) + extruder_screw_spacing, wrist_depth - (extruder_back_row_offset + extruder_offset_from_front), boolean_offset]) {
        //     cylinder(h=hole_height, r=screw_access_hole_radius);
        // }
    }
  }
}

module extruder_placeholder() {
    rotate([90, 90, 0]) {
        translate([-60, -$extruder_width/2, -23]) {
            cube([$extruder_width, $extruder_width, 24]);
            translate([38/2, 38/2, 24]) {
                cylinder(h=19, r=18);
            }
        }
    }
}

module hotend_placeholder() {
    translate([0, 12.5, 79]) {
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

// TODO 
// - Create screw holes in extruder cradle
// - Connect extruder cradle to hotend cradle
// - Add better clearance for arm connection bolts and probably balance the manipulator better
module main() {
  // stl/sos101_screwdriver_wrist_roll.stl
  
  // import packages/assembler0-hardware/stl/ftobler_arm/files/gripperBase.stl
  translate([0, 0, 60]) {
    difference() {
        import("../stl/ftobler_arm/files/gripperBase.stl");
        translate([-50, -15, -5]) {
          cube([100, 50, 20]);
        }
    }
  }
  
  wrist_roll();

  if ($render_vitamines) {
    extruder_placeholder();
  }
  if ($render_vitamines) {
    hotend_placeholder();
  }
}

main();
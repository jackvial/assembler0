
// ========================= Parameters =========================
// Wrist roll dimensions
wrist_width = 51;
wrist_depth = 38;
wrist_origin_x = -wrist_width/2;  // Calculated to center assembly around x=0
wrist_origin_y = -15;

// Plate and structure dimensions
plate_thickness = 2; // thickness of all small plates
side_plate_thickness = 6;
top_plate_height = 6;
side_plate_height = 65;
large_counter_sink_depth = 5;
side_plate_height_from_top = 10;

// Screw hole dimensions
screw_hole_radius = 1.8;
top_plate_screw_radius = 1.8;
counter_sink_radius = 3;
top_plate_center_hole_radius = 3;
top_plate_screw_offset = 6.9;

// Extruder mounting dimensions
extruder_offset_from_front = 5;
extruder_screw_spacing = 9.5; // distance from center
extruder_front_row_offset = 8;
extruder_back_row_offset = 18;
extruder_center_hole_radius = 3;
extruder_cradle_thickness = 3;
mount_screw_access_cutaway = 10;
extruder_cradle_height = 60;

// Hotend mounting dimensions
hotend_hole_radius = 6.5;
hotend_hex_radius = 10;
hotend_cradle_thickness = 8;
screw_access_hole_radius = 2.4;

// Boolean difference offset
boolean_offset = -0.1;

$fn = 64; // global smoothness for all circular geometry
$render_vitamines = false;
$extruder_width = 38;

// ========================= Assemblies =========================
// ========================= Top-level Model =========================

module wrist_roll() {
  translate([-wrist_width/2, wrist_origin_y, 4]) {

    // Top plate
    difference() {
        // Jut out to clear wrist roll holder
        union() {
            translate([wrist_width/2, wrist_depth/2, -5]) {
                cylinder(h=5, r=12);
            }
            cube([wrist_width, wrist_depth,top_plate_height]);
        }

        // hole for filament
        // Filament will need to bend a bit forward to clear the wrist roll holder
        // todo(jack): Need to round this hole to reduce friction with the filament
        translate([wrist_width/2, 34, -6]) {
            cylinder(h=16, r=extruder_center_hole_radius);
        }

        // Large counter sink
        translate([wrist_width/2, wrist_depth/2, 3]) {
                cylinder(h=large_counter_sink_depth, r=10);
         }

        // hole at center
        translate([wrist_width/2, wrist_depth/2, - (large_counter_sink_depth + 0.2)]) {
            cylinder(h=3, r=top_plate_center_hole_radius);
        }

        // Four holes in a circular pattern around center
        for (angle = [45, 45 + 90, 45 + 180, 45 + 270]) {
            translate([wrist_width/2, wrist_depth/2, -5]) {
                rotate([0, 0, angle]) {
                    translate([top_plate_screw_offset, 0, boolean_offset]) {
                        cylinder(h=top_plate_height + 0.2, r=top_plate_screw_radius);
                        translate([0, 0, 4]) {
                            cylinder(h=6.2, r=counter_sink_radius);
                        }
                    }
                }
            }
        }
    }
  }

  // Side 1
  // todo(jack): Add cutout for the gear wheel
  translate([wrist_width/2 - side_plate_thickness, wrist_origin_y, side_plate_height_from_top]) {
    difference() {
        union() {
            cube([side_plate_thickness, wrist_depth, side_plate_height]);

            // translate([-2, 0, extruder_cradle_height - 46]) {
            //     cube([2, 19, 36]);
            // }
        }

        // Extruder side mount screw holes
         translate([-0.1, wrist_depth - (extruder_back_row_offset + extruder_offset_from_front), extruder_cradle_height - side_plate_height_from_top - extruder_screw_spacing]) {
            rotate([0, 90, 0]) {
                cylinder(h=10, r=screw_hole_radius);
            }
        }

        translate([-0.1, wrist_depth - (extruder_back_row_offset + extruder_offset_from_front), extruder_cradle_height - side_plate_height_from_top - (extruder_screw_spacing * 3)]) {
            rotate([0, 90, 0]) {
                cylinder(h=10, r=screw_hole_radius);
            }
        }
    }
  }

  // Side 2
  // todo(jack): Add cutout for the gear wheel
  translate([wrist_origin_x, wrist_origin_y, side_plate_height_from_top]) {

    difference() {
        union() {
            cube([side_plate_thickness, wrist_depth, side_plate_height]);

            // translate([side_plate_thickness, 0, extruder_cradle_height - 26]) {
            //     cube([2, 19, 16]);
            // }
        }

         // Extruder side mount screw hole
         translate([-0.1, wrist_depth - (extruder_back_row_offset + extruder_offset_from_front), extruder_cradle_height - side_plate_height_from_top - extruder_screw_spacing]) {
            rotate([0, 90, 0]) {
                cylinder(h=10, r=screw_hole_radius);
            }
        }

        translate([3, -0.1, extruder_cradle_height - (26 + 24)]) {
            cube([7, 19, 18]);
        }
    }


  }

  // Extruder cradle
  translate([-wrist_width/2, wrist_origin_y, extruder_cradle_height]) {
    difference() {
        cube([wrist_width, wrist_depth, extruder_cradle_thickness]);

        // Cut away for screwdriver access
        translate([wrist_width/2, 0, boolean_offset]) {
            cylinder(h=extruder_cradle_thickness + 1, r=mount_screw_access_cutaway);
        }

        // Extruder to hotend hole for filament
        translate([wrist_width/2, wrist_depth - (5 + extruder_offset_from_front), boolean_offset]) {
            cylinder(h=4, r=extruder_center_hole_radius);
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
  translate([-wrist_width/2, wrist_origin_y, 75]) {
    hole_height = 9;
    difference() {
        cube([wrist_width, wrist_depth, hotend_cradle_thickness]);

        // Cut away for screwdriver access
        translate([wrist_width/2, 0, boolean_offset]) {
            cylinder(h=hotend_cradle_thickness + 1, r=mount_screw_access_cutaway);
        }

        translate([wrist_width/2, wrist_depth - (5 + extruder_offset_from_front), boolean_offset]) {

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
    translate([0, 10, 72]) {
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
  // stl/sos101_screwdriver_wrist_roll.stl
  wrist_roll();

  if ($render_vitamines) {
    extruder_placeholder();
  }
  if ($render_vitamines) {
    hotend_placeholder();
  }
}

main();